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

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_projection_control_diagnostic_replay_not_endpoint_validation"
REPLAY_POLICY = (
    "diagnostic_only_projection_control_replay_reads_frozen_preflight_unchanged_"
    "no_kernel_promotion_no_positive_load_no_route_rescue"
)
CARRIER_POLICY = "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_amplitude_fit"
PROJECTION_POLICY = (
    "source_side_interpolated_P_i_R_equals_sin2_i_ref_over_sin2_i_R_"
    "from_accepted_PA_inclination_profile"
)


def _load_preflight() -> dict[str, object]:
    summary = json.loads(PREFLIGHT_SUMMARY.read_text(encoding="utf-8"))
    required = {
        "projection_control_preflight_ready": True,
        "diagnostic_only": True,
        "positive_load_ready": False,
        "endpoint_ready": False,
        "endpoint_replay_allowed": False,
        "kernel_promotion_allowed": False,
        "new_route_scoring_allowed": False,
    }
    for key, expected in required.items():
        if summary.get(key) is not expected:
            raise ValueError(f"Preflight guardrail failed for {key}: {summary.get(key)!r}")
    if summary.get("diagnostic_replay_permission") != "separate_authorization_required":
        raise ValueError("Projection-control replay requires explicit separate authorization.")
    return summary


def _load_projection_profile() -> pd.DataFrame:
    profile = pd.read_csv(PROJECTION_PROFILE)
    profile = profile[profile["derived_item"].eq("projection_profile_row")].copy()
    if profile.empty:
        raise RuntimeError("Missing projection profile rows.")
    if set(profile["endpoint_replay_permission"].astype(str)) != {"no"}:
        raise ValueError("Projection profile unexpectedly grants endpoint replay.")
    profile[["radius_kpc", "projection_factor"]] = profile["source_value"].str.extract(
        r"R_kpc=([0-9.]+);.*P_i=([-0-9.]+);"
    )
    profile["radius_kpc"] = pd.to_numeric(profile["radius_kpc"], errors="raise")
    profile["projection_factor"] = pd.to_numeric(profile["projection_factor"], errors="raise")
    return profile.sort_values("radius_kpc")


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


def run_replay() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    preflight = _load_preflight()
    profile = _load_projection_profile()
    curves = base._mass_model_rows({"NGC2841"}).sort_values("radius_kpc").reset_index(drop=True)
    if curves.empty:
        raise RuntimeError("Missing local SPARC mass-model rows for NGC2841.")

    curves["projection_factor"] = np.interp(
        curves["radius_kpc"].astype(float),
        profile["radius_kpc"].astype(float),
        profile["projection_factor"].astype(float),
        left=float(profile["projection_factor"].iloc[0]),
        right=float(profile["projection_factor"].iloc[-1]),
    )
    curves["projection_factor"] = curves["projection_factor"].clip(lower=0.0)
    curves["v_projection_control2"] = curves["vbar2_fixed_mlr"] * curves["projection_factor"]
    curves["v_projection_control_kms"] = np.sqrt(curves["v_projection_control2"].clip(lower=0.0))
    curves["delta_v2_projection_control"] = curves["v_projection_control2"] - curves["vbar2_fixed_mlr"]
    curves["vobs_minus_baryonic_kms"] = curves["vobs_kms"] - curves["vbar_fixed_mlr_kms"]
    curves["vobs_minus_projection_control_kms"] = (
        curves["vobs_kms"] - curves["v_projection_control_kms"]
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
    proj_rmse, proj_wrmse = _weighted_rmse(
        curves["vobs_kms"],
        curves["e_vobs_kms"],
        curves["v_projection_control_kms"],
    )

    zone_rows = []
    for zone, group in curves.groupby("zone", sort=False):
        z_bary_rmse, z_bary_wrmse = _weighted_rmse(
            group["vobs_kms"],
            group["e_vobs_kms"],
            group["vbar_fixed_mlr_kms"],
        )
        z_proj_rmse, z_proj_wrmse = _weighted_rmse(
            group["vobs_kms"],
            group["e_vobs_kms"],
            group["v_projection_control_kms"],
        )
        zone_rows.append(
            {
                "galaxy": "NGC2841",
                "zone": zone,
                "n_points": int(len(group)),
                "radius_min_kpc": float(group["radius_kpc"].min()),
                "radius_max_kpc": float(group["radius_kpc"].max()),
                "projection_factor_median": float(group["projection_factor"].median()),
                "projection_factor_min": float(group["projection_factor"].min()),
                "projection_factor_max": float(group["projection_factor"].max()),
                "baryonic_rmse_kms": z_bary_rmse,
                "baryonic_weighted_rmse_kms": z_bary_wrmse,
                "projection_control_rmse_kms": z_proj_rmse,
                "projection_control_weighted_rmse_kms": z_proj_wrmse,
                "projection_minus_baryonic_weighted_rmse_kms": z_proj_wrmse - z_bary_wrmse,
                "median_delta_v2_projection_control": float(
                    group["delta_v2_projection_control"].median()
                ),
                "median_missing_velocity_after_projection_kms": float(
                    group["vobs_minus_projection_control_kms"].median()
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
            "projection_factor",
            "v_projection_control_kms",
            "delta_v2_projection_control",
            "vobs_minus_baryonic_kms",
            "vobs_minus_projection_control_kms",
            "zone",
        ]
    ].copy()
    detail["diagnostic_replay_status"] = "diagnostic_replay_completed_no_validation"
    detail["endpoint_validation_claimed"] = "no"
    detail["kernel_promotion_permission"] = "no"
    detail["positive_load_promotion_permission"] = "no"
    detail["preflight_claim_boundary"] = str(preflight["claim_boundary"])
    detail["replay_policy"] = REPLAY_POLICY
    detail["carrier_policy"] = CARRIER_POLICY
    detail["projection_policy"] = PROJECTION_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    zone_summary = pd.DataFrame(zone_rows)
    zone_summary["diagnostic_replay_status"] = "diagnostic_replay_completed_no_validation"
    zone_summary["endpoint_validation_claimed"] = "no"
    zone_summary["kernel_promotion_permission"] = "no"
    zone_summary["positive_load_promotion_permission"] = "no"
    zone_summary["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_points": int(len(detail)),
        "galaxies": ["NGC2841"],
        "zones": zone_summary["zone"].tolist(),
        "baryonic_rmse_kms": bary_rmse,
        "baryonic_weighted_rmse_kms": bary_wrmse,
        "projection_control_rmse_kms": proj_rmse,
        "projection_control_weighted_rmse_kms": proj_wrmse,
        "projection_minus_baryonic_weighted_rmse_kms": proj_wrmse - bary_wrmse,
        "projection_improves_baryonic": bool(proj_wrmse < bary_wrmse),
        "projection_factor_min": float(detail["projection_factor"].min()),
        "projection_factor_max": float(detail["projection_factor"].max()),
        "projection_factor_outermost": float(detail.iloc[-1]["projection_factor"]),
        "diagnostic_replay_status_counts": (
            detail["diagnostic_replay_status"].value_counts().sort_index().to_dict()
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
        "preflight_claim_boundary": preflight["claim_boundary"],
        "replay_policy": REPLAY_POLICY,
        "carrier_policy": CARRIER_POLICY,
        "projection_policy": PROJECTION_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The source-frozen tilted-ring projection control is a valid diagnostic "
            "replay, but it is not a positive dark-residual load. Because the outer "
            "projection factor is below unity, it attenuates the fixed baryonic carrier "
            "and therefore cannot close NGC2841's known positive capacity deficit."
        ),
    }
    return detail, zone_summary, summary


def main() -> None:
    detail, zone_summary, summary = run_replay()
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
