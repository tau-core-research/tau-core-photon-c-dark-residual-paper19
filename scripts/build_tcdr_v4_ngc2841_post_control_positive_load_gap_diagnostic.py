from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

PREFLIGHT_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_projection_control_preflight_summary_v0_1.json"
PROJECTION_PROFILE = SOURCE_DIR / "tcdr_v4_ngc2841_projection_sign_load_derivation_v0_1.csv"
CEILING_FREEZE = (
    SOURCE_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_summary_v0_1.json"
)

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_post_control_positive_load_gap_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_post_control_positive_load_gap_diagnostic_not_kernel_fit"
AUDIT_POLICY = (
    "post_control_positive_v2_gap_diagnostic_after_frozen_projection_and_baryonic_ceiling_"
    "no_parameter_fit_no_kernel_promotion_no_endpoint_validation"
)
G_KPC_KMS2_PER_MSUN = 4.30091e-6


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _projection_profile() -> pd.DataFrame:
    profile = pd.read_csv(PROJECTION_PROFILE)
    profile = profile[profile["derived_item"].eq("projection_profile_row")].copy()
    if profile.empty:
        raise RuntimeError("Missing projection profile rows.")
    profile[["radius_kpc", "projection_factor"]] = profile["source_value"].str.extract(
        r"R_kpc=([0-9.]+);.*P_i=([-0-9.]+);"
    )
    profile["radius_kpc"] = pd.to_numeric(profile["radius_kpc"], errors="raise")
    profile["projection_factor"] = pd.to_numeric(profile["projection_factor"], errors="raise")
    return profile.sort_values("radius_kpc")


def _zone(radius: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [radius < 10.0, radius < 30.0],
            ["inner_lt_10kpc", "mid_10_30kpc"],
            default="outer_ge_30kpc",
        ),
        index=radius.index,
    )


def build_gap_diagnostic() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    preflight = _load_json(PREFLIGHT_SUMMARY)
    ceiling = _load_json(CEILING_FREEZE)
    if preflight.get("projection_control_preflight_ready") is not True:
        raise ValueError("Projection preflight is not ready.")
    if ceiling.get("control_freeze_ready") is not True:
        raise ValueError("Integrated outer baryonic ceiling control is not frozen.")
    if ceiling.get("positive_dark_residual_load_ready") is not False:
        raise ValueError("This diagnostic requires the positive dark-residual load to remain blocked.")

    profile = _projection_profile()
    curves = base._mass_model_rows({"NGC2841"}).sort_values("radius_kpc").reset_index(drop=True)
    if curves.empty:
        raise RuntimeError("Missing local SPARC mass-model rows for NGC2841.")

    m_outer = float(ceiling["outer_baryonic_mass_from_3to1_msun"])
    curves["projection_factor"] = np.interp(
        curves["radius_kpc"].astype(float),
        profile["radius_kpc"].astype(float),
        profile["projection_factor"].astype(float),
        left=float(profile["projection_factor"].iloc[0]),
        right=float(profile["projection_factor"].iloc[-1]),
    ).clip(min=0.0)
    active = curves["radius_kpc"] >= 30.0
    curves["delta_v2_outer_baryonic_ceiling"] = 0.0
    curves.loc[active, "delta_v2_outer_baryonic_ceiling"] = (
        G_KPC_KMS2_PER_MSUN * m_outer / curves.loc[active, "radius_kpc"]
    )

    curves["v2_baryonic"] = curves["vbar2_fixed_mlr"]
    curves["v2_projection_control"] = curves["vbar2_fixed_mlr"] * curves["projection_factor"]
    curves["v2_ceiling_control"] = (
        curves["vbar2_fixed_mlr"] + curves["delta_v2_outer_baryonic_ceiling"]
    )
    curves["v2_projection_plus_ceiling_control"] = (
        curves["v2_projection_control"] + curves["delta_v2_outer_baryonic_ceiling"]
    )
    curves["vobs2"] = curves["vobs_kms"] ** 2
    for model in [
        "baryonic",
        "projection_control",
        "ceiling_control",
        "projection_plus_ceiling_control",
    ]:
        curves[f"positive_v2_gap_after_{model}"] = (
            curves["vobs2"] - curves[f"v2_{model}"]
        ).clip(lower=0.0)
        curves[f"positive_v_gap_after_{model}_kms"] = (
            curves["vobs_kms"] - np.sqrt(curves[f"v2_{model}"].clip(lower=0.0))
        ).clip(lower=0.0)

    curves["zone"] = _zone(curves["radius_kpc"])

    detail = curves[
        [
            "galaxy",
            "radius_kpc",
            "vobs_kms",
            "vbar_fixed_mlr_kms",
            "projection_factor",
            "delta_v2_outer_baryonic_ceiling",
            "zone",
            "positive_v2_gap_after_baryonic",
            "positive_v2_gap_after_projection_control",
            "positive_v2_gap_after_ceiling_control",
            "positive_v2_gap_after_projection_plus_ceiling_control",
            "positive_v_gap_after_baryonic_kms",
            "positive_v_gap_after_projection_control_kms",
            "positive_v_gap_after_ceiling_control_kms",
            "positive_v_gap_after_projection_plus_ceiling_control_kms",
        ]
    ].copy()
    detail["diagnostic_status"] = "post_control_gap_diagnostic_no_fit"
    detail["endpoint_validation_claimed"] = "no"
    detail["kernel_promotion_permission"] = "no"
    detail["positive_load_promotion_permission"] = "no"
    detail["audit_policy"] = AUDIT_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    zone_rows = []
    for zone, group in detail.groupby("zone", sort=False):
        row: dict[str, object] = {
            "galaxy": "NGC2841",
            "zone": zone,
            "n_points": int(len(group)),
            "radius_min_kpc": float(group["radius_kpc"].min()),
            "radius_max_kpc": float(group["radius_kpc"].max()),
            "projection_factor_median": float(group["projection_factor"].median()),
            "outer_baryonic_ceiling_delta_v2_median": float(
                group["delta_v2_outer_baryonic_ceiling"].median()
            ),
        }
        for model in [
            "baryonic",
            "projection_control",
            "ceiling_control",
            "projection_plus_ceiling_control",
        ]:
            row[f"median_positive_v2_gap_after_{model}"] = float(
                group[f"positive_v2_gap_after_{model}"].median()
            )
            row[f"median_positive_v_gap_after_{model}_kms"] = float(
                group[f"positive_v_gap_after_{model}_kms"].median()
            )
        zone_rows.append(row)

    zone_summary = pd.DataFrame(zone_rows)
    zone_summary["diagnostic_status"] = "post_control_gap_diagnostic_no_fit"
    zone_summary["endpoint_validation_claimed"] = "no"
    zone_summary["kernel_promotion_permission"] = "no"
    zone_summary["positive_load_promotion_permission"] = "no"
    zone_summary["audit_policy"] = AUDIT_POLICY
    zone_summary["claim_boundary"] = CLAIM_BOUNDARY

    outer = zone_summary[zone_summary["zone"].eq("outer_ge_30kpc")].iloc[0]
    summary = {
        "n_points": int(len(detail)),
        "galaxies": ["NGC2841"],
        "zones": zone_summary["zone"].tolist(),
        "outer_zone_median_positive_v2_gap_after_baryonic": float(
            outer["median_positive_v2_gap_after_baryonic"]
        ),
        "outer_zone_median_positive_v2_gap_after_projection_control": float(
            outer["median_positive_v2_gap_after_projection_control"]
        ),
        "outer_zone_median_positive_v2_gap_after_ceiling_control": float(
            outer["median_positive_v2_gap_after_ceiling_control"]
        ),
        "outer_zone_median_positive_v2_gap_after_projection_plus_ceiling_control": float(
            outer["median_positive_v2_gap_after_projection_plus_ceiling_control"]
        ),
        "outer_zone_median_positive_v_gap_after_ceiling_control_kms": float(
            outer["median_positive_v_gap_after_ceiling_control_kms"]
        ),
        "outer_zone_median_ceiling_delta_v2": float(
            outer["outer_baryonic_ceiling_delta_v2_median"]
        ),
        "ceiling_fraction_of_outer_baryonic_gap": float(
            outer["outer_baryonic_ceiling_delta_v2_median"]
            / outer["median_positive_v2_gap_after_baryonic"]
        )
        if outer["median_positive_v2_gap_after_baryonic"] > 0
        else 0.0,
        "diagnostic_status_counts": (
            detail["diagnostic_status"].value_counts().sort_index().to_dict()
        ),
        "endpoint_validation_claimed_counts": (
            detail["endpoint_validation_claimed"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            detail["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "positive_load_promotion_permission_counts": (
            detail["positive_load_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "audit_policy": AUDIT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "After the frozen projection control and integrated outer baryonic ceiling "
            "are accounted for, NGC2841 still has a large positive outer velocity-squared "
            "gap. The known outer baryonic ceiling contributes only a tiny fraction of "
            "the median outer gap, while the projection control has the wrong sign for "
            "closing it."
        ),
    }
    return detail, zone_summary, summary


def main() -> None:
    detail, zone_summary, summary = build_gap_diagnostic()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    zone_summary.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(zone_summary.to_string(index=False))


if __name__ == "__main__":
    main()
