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

FREEZE_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_summary_v0_1.json"
)

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_integrated_outer_baryonic_ceiling_control_diagnostic_not_validation"
REPLAY_POLICY = (
    "diagnostic_only_integrated_outer_baryonic_ceiling_control_"
    "reads_frozen_control_unchanged_no_dark_residual_promotion"
)
CARRIER_POLICY = "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_amplitude_fit"
G_KPC_KMS2_PER_MSUN = 4.30091e-6


def _load_freeze() -> dict[str, object]:
    summary = json.loads(FREEZE_SUMMARY.read_text(encoding="utf-8"))
    if summary.get("control_freeze_ready") is not True:
        raise ValueError("Integrated outer baryonic ceiling control is not freeze-ready.")
    if summary.get("positive_dark_residual_load_ready") is not False:
        raise ValueError("This diagnostic requires the dark-residual load to remain blocked.")
    if summary.get("endpoint_ready") is not False:
        raise ValueError("This diagnostic cannot run as an endpoint-ready artifact.")
    return summary


def _weighted_rmse(vobs: pd.Series, evobs: pd.Series, vpred: pd.Series) -> tuple[float, float]:
    residual = vobs - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(
        np.sqrt(
            np.average(
                residual**2,
                weights=1.0 / evobs.clip(lower=1.0) ** 2,
            )
        )
    )
    return rmse, wrmse


def run_diagnostic() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    freeze = _load_freeze()
    m_outer = float(freeze["outer_baryonic_mass_from_3to1_msun"])
    curves = base._mass_model_rows({"NGC2841"}).sort_values("radius_kpc").reset_index(drop=True)
    if curves.empty:
        raise RuntimeError("Missing local SPARC mass-model rows for NGC2841.")

    active = curves["radius_kpc"] >= 30.0
    curves["delta_v2_outer_baryonic_ceiling"] = 0.0
    curves.loc[active, "delta_v2_outer_baryonic_ceiling"] = (
        G_KPC_KMS2_PER_MSUN * m_outer / curves.loc[active, "radius_kpc"]
    )
    curves["v_outer_baryonic_ceiling_control2"] = (
        curves["vbar2_fixed_mlr"] + curves["delta_v2_outer_baryonic_ceiling"]
    )
    curves["v_outer_baryonic_ceiling_control_kms"] = np.sqrt(
        curves["v_outer_baryonic_ceiling_control2"].clip(lower=0.0)
    )
    curves["vobs_minus_baryonic_kms"] = curves["vobs_kms"] - curves["vbar_fixed_mlr_kms"]
    curves["vobs_minus_ceiling_control_kms"] = (
        curves["vobs_kms"] - curves["v_outer_baryonic_ceiling_control_kms"]
    )
    curves["zone"] = np.select(
        [
            curves["radius_kpc"] < 10.0,
            curves["radius_kpc"] < 30.0,
        ],
        ["inner_lt_10kpc", "mid_10_30kpc"],
        default="outer_ge_30kpc",
    )

    bary_rmse, bary_wrmse = _weighted_rmse(
        curves["vobs_kms"],
        curves["e_vobs_kms"],
        curves["vbar_fixed_mlr_kms"],
    )
    ctrl_rmse, ctrl_wrmse = _weighted_rmse(
        curves["vobs_kms"],
        curves["e_vobs_kms"],
        curves["v_outer_baryonic_ceiling_control_kms"],
    )

    zone_rows = []
    for zone, group in curves.groupby("zone", sort=False):
        z_bary_rmse, z_bary_wrmse = _weighted_rmse(
            group["vobs_kms"],
            group["e_vobs_kms"],
            group["vbar_fixed_mlr_kms"],
        )
        z_ctrl_rmse, z_ctrl_wrmse = _weighted_rmse(
            group["vobs_kms"],
            group["e_vobs_kms"],
            group["v_outer_baryonic_ceiling_control_kms"],
        )
        zone_rows.append(
            {
                "galaxy": "NGC2841",
                "zone": zone,
                "n_points": int(len(group)),
                "radius_min_kpc": float(group["radius_kpc"].min()),
                "radius_max_kpc": float(group["radius_kpc"].max()),
                "median_delta_v2_outer_baryonic_ceiling": float(
                    group["delta_v2_outer_baryonic_ceiling"].median()
                ),
                "max_delta_v2_outer_baryonic_ceiling": float(
                    group["delta_v2_outer_baryonic_ceiling"].max()
                ),
                "baryonic_weighted_rmse_kms": z_bary_wrmse,
                "ceiling_control_weighted_rmse_kms": z_ctrl_wrmse,
                "ceiling_minus_baryonic_weighted_rmse_kms": z_ctrl_wrmse - z_bary_wrmse,
                "median_missing_velocity_after_ceiling_kms": float(
                    group["vobs_minus_ceiling_control_kms"].median()
                ),
            }
        )

    detail = curves[
        [
            "galaxy",
            "radius_kpc",
            "vobs_kms",
            "e_vobs_kms",
            "vbar_fixed_mlr_kms",
            "delta_v2_outer_baryonic_ceiling",
            "v_outer_baryonic_ceiling_control_kms",
            "vobs_minus_baryonic_kms",
            "vobs_minus_ceiling_control_kms",
            "zone",
        ]
    ].copy()
    detail["diagnostic_replay_status"] = "diagnostic_control_completed_no_validation"
    detail["endpoint_validation_claimed"] = "no"
    detail["kernel_promotion_permission"] = "no"
    detail["positive_dark_residual_load_promotion_permission"] = "no"
    detail["freeze_claim_boundary"] = str(freeze["claim_boundary"])
    detail["replay_policy"] = REPLAY_POLICY
    detail["carrier_policy"] = CARRIER_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    zone_summary = pd.DataFrame(zone_rows)
    zone_summary["diagnostic_replay_status"] = "diagnostic_control_completed_no_validation"
    zone_summary["endpoint_validation_claimed"] = "no"
    zone_summary["kernel_promotion_permission"] = "no"
    zone_summary["positive_dark_residual_load_promotion_permission"] = "no"
    zone_summary["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_points": int(len(detail)),
        "galaxies": ["NGC2841"],
        "outer_baryonic_mass_from_3to1_msun": m_outer,
        "baryonic_rmse_kms": bary_rmse,
        "baryonic_weighted_rmse_kms": bary_wrmse,
        "ceiling_control_rmse_kms": ctrl_rmse,
        "ceiling_control_weighted_rmse_kms": ctrl_wrmse,
        "ceiling_minus_baryonic_weighted_rmse_kms": ctrl_wrmse - bary_wrmse,
        "ceiling_control_improves_baryonic": bool(ctrl_wrmse < bary_wrmse),
        "max_delta_v2_outer_baryonic_ceiling": float(
            detail["delta_v2_outer_baryonic_ceiling"].max()
        ),
        "outer_zone_median_delta_v2_outer_baryonic_ceiling": float(
            detail.loc[detail["zone"].eq("outer_ge_30kpc"), "delta_v2_outer_baryonic_ceiling"].median()
        ),
        "diagnostic_replay_status_counts": (
            detail["diagnostic_replay_status"].value_counts().sort_index().to_dict()
        ),
        "endpoint_validation_claimed_counts": (
            detail["endpoint_validation_claimed"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            detail["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "positive_dark_residual_load_promotion_permission_counts": (
            detail["positive_dark_residual_load_promotion_permission"]
            .value_counts()
            .sort_index()
            .to_dict()
        ),
        "freeze_claim_boundary": freeze["claim_boundary"],
        "replay_policy": REPLAY_POLICY,
        "carrier_policy": CARRIER_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The integrated Dragonfly outer baryonic mass ceiling has the correct "
            "velocity-squared units and can be replayed as a diagnostic control, but "
            "its amplitude is tiny relative to the NGC2841 capacity gap. It is a "
            "baryonic ceiling/control, not a positive dark-residual load."
        ),
    }
    return detail, zone_summary, summary


def main() -> None:
    detail, zone_summary, summary = run_diagnostic()
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
