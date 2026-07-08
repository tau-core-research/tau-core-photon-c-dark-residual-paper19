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

AUTH_SUMMARY = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance_summary_v0_1.json"
)
FROZEN_FORMULA = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_v0_1.csv"
)

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_beta_closure_endpoint_control_replay_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc2841_beta_closure_endpoint_control_replay_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_beta_closure_endpoint_control_replay_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_beta_closure_endpoint_control_replay_preliminary_not_validation"
REPLAY_POLICY = (
    "authorized_single_object_preliminary_control_replay_reads_frozen_beta_context_formula_"
    "unchanged_no_retuning_no_relabeling_no_kernel_promotion"
)
CARRIER_POLICY = "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_amplitude_fit"


def _load_authorization() -> dict[str, object]:
    summary = json.loads(AUTH_SUMMARY.read_text(encoding="utf-8"))
    required = {
        "review_response_accepted": True,
        "endpoint_replay_authorized": True,
        "formula_retuning_allowed": False,
        "morphology_relabel_allowed": False,
        "validation_claim_allowed": False,
        "formula_must_be_read_unchanged": True,
    }
    for key, expected in required.items():
        if summary.get(key) is not expected:
            raise ValueError(f"Endpoint authorization guardrail failed for {key}: {summary.get(key)!r}")
    if summary.get("endpoint_scope") != "single_object_preliminary_endpoint_control_replay_only":
        raise ValueError("Endpoint authorization is not limited to the expected preliminary-control scope.")
    return summary


def _load_frozen_formula() -> pd.DataFrame:
    formula = pd.read_csv(FROZEN_FORMULA)
    if formula.empty:
        raise RuntimeError("Missing frozen beta-context formula rows.")
    if set(formula["formula_freeze_review_ready"].astype(str)) != {"yes"}:
        raise ValueError("Frozen beta-context formula is not formula-review ready.")
    if set(formula["physical_spin_claim"].astype(str)) != {"no"}:
        raise ValueError("Beta-context formula must not claim direct physical spin measurement.")
    if set(formula["uses_vobs_or_residual"].astype(str)) != {"no"}:
        raise ValueError("Frozen beta-context formula used endpoint/residual data.")
    required_cols = {
        "galaxy",
        "radius_kpc",
        "v_carrier2_fixed_ml_km2s2",
        "v_carrier_fixed_ml_kms",
        "k_beta_shape_interp_0_1",
        "beta_context",
        "delta_v_beta_context2_km2s2",
        "v_beta_context2_km2s2",
        "v_beta_context_kms",
    }
    missing = required_cols.difference(formula.columns)
    if missing:
        raise ValueError(f"Frozen beta-context formula is missing columns: {sorted(missing)}")
    return formula.sort_values("radius_kpc").reset_index(drop=True)


def _weighted_rmse(vobs: pd.Series, evobs: pd.Series, vpred: pd.Series) -> tuple[float, float]:
    residual = vobs - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(np.sqrt(np.average(residual**2, weights=1.0 / evobs.clip(lower=1.0) ** 2)))
    return rmse, wrmse


def run_replay() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    authorization = _load_authorization()
    formula = _load_frozen_formula()
    curves = base._mass_model_rows({"NGC2841"}).sort_values("radius_kpc").reset_index(drop=True)
    if curves.empty:
        raise RuntimeError("Missing local SPARC mass-model rows for NGC2841.")

    merged = pd.merge(
        curves,
        formula,
        on=["galaxy", "radius_kpc"],
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != len(formula) or len(merged) != len(curves):
        raise RuntimeError("Frozen formula rows and endpoint rows do not align one-to-one.")

    merged["vobs_minus_baryonic_kms"] = merged["vobs_kms"] - merged["vbar_fixed_mlr_kms"]
    merged["vobs_minus_beta_context_kms"] = merged["vobs_kms"] - merged["v_beta_context_kms"]
    merged["beta_context_minus_baryonic_kms"] = (
        merged["v_beta_context_kms"] - merged["vbar_fixed_mlr_kms"]
    )
    merged["zone"] = np.select(
        [merged["radius_kpc"] < 10.0, merged["radius_kpc"] < 30.0],
        ["inner_lt_10kpc", "mid_10_30kpc"],
        default="outer_ge_30kpc",
    )

    bary_rmse, bary_wrmse = _weighted_rmse(
        merged["vobs_kms"], merged["e_vobs_kms"], merged["vbar_fixed_mlr_kms"]
    )
    beta_rmse, beta_wrmse = _weighted_rmse(
        merged["vobs_kms"], merged["e_vobs_kms"], merged["v_beta_context_kms"]
    )

    zone_rows = []
    for zone, group in merged.groupby("zone", sort=False):
        z_bary_rmse, z_bary_wrmse = _weighted_rmse(
            group["vobs_kms"], group["e_vobs_kms"], group["vbar_fixed_mlr_kms"]
        )
        z_beta_rmse, z_beta_wrmse = _weighted_rmse(
            group["vobs_kms"], group["e_vobs_kms"], group["v_beta_context_kms"]
        )
        zone_rows.append(
            {
                "galaxy": "NGC2841",
                "zone": zone,
                "n_points": int(len(group)),
                "radius_min_kpc": float(group["radius_kpc"].min()),
                "radius_max_kpc": float(group["radius_kpc"].max()),
                "k_beta_shape_median": float(group["k_beta_shape_interp_0_1"].median()),
                "delta_v_beta_context2_median_km2s2": float(
                    group["delta_v_beta_context2_km2s2"].median()
                ),
                "baryonic_rmse_kms": z_bary_rmse,
                "baryonic_weighted_rmse_kms": z_bary_wrmse,
                "beta_context_rmse_kms": z_beta_rmse,
                "beta_context_weighted_rmse_kms": z_beta_wrmse,
                "beta_minus_baryonic_weighted_rmse_kms": z_beta_wrmse - z_bary_wrmse,
                "median_missing_velocity_after_beta_kms": float(
                    group["vobs_minus_beta_context_kms"].median()
                ),
            }
        )

    detail = merged[
        [
            "galaxy",
            "radius_kpc",
            "vobs_kms",
            "e_vobs_kms",
            "vbar_fixed_mlr_kms",
            "v_beta_context_kms",
            "k_beta_shape_interp_0_1",
            "beta_context",
            "delta_v_beta_context2_km2s2",
            "vobs_minus_baryonic_kms",
            "vobs_minus_beta_context_kms",
            "beta_context_minus_baryonic_kms",
            "zone",
        ]
    ].copy()
    detail["endpoint_control_status"] = "preliminary_control_replay_completed_no_validation"
    detail["formula_retuned_after_authorization"] = "no"
    detail["morphology_relabel_after_authorization"] = "no"
    detail["kernel_promotion_permission"] = "no"
    detail["validation_claimed"] = "no"
    detail["authorization_claim_boundary"] = str(authorization["claim_boundary"])
    detail["replay_policy"] = REPLAY_POLICY
    detail["carrier_policy"] = CARRIER_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    zone_summary = pd.DataFrame(zone_rows)
    zone_summary["endpoint_control_status"] = "preliminary_control_replay_completed_no_validation"
    zone_summary["formula_retuned_after_authorization"] = "no"
    zone_summary["morphology_relabel_after_authorization"] = "no"
    zone_summary["kernel_promotion_permission"] = "no"
    zone_summary["validation_claimed"] = "no"
    zone_summary["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_points": int(len(detail)),
        "galaxies": ["NGC2841"],
        "beta_context": float(detail["beta_context"].iloc[0]),
        "baryonic_rmse_kms": bary_rmse,
        "baryonic_weighted_rmse_kms": bary_wrmse,
        "beta_context_rmse_kms": beta_rmse,
        "beta_context_weighted_rmse_kms": beta_wrmse,
        "beta_minus_baryonic_weighted_rmse_kms": beta_wrmse - bary_wrmse,
        "beta_context_improves_baryonic": bool(beta_wrmse < bary_wrmse),
        "median_delta_v_beta_context2_km2s2": float(
            detail["delta_v_beta_context2_km2s2"].median()
        ),
        "max_delta_v_beta_context2_km2s2": float(detail["delta_v_beta_context2_km2s2"].max()),
        "median_missing_velocity_after_beta_kms": float(
            detail["vobs_minus_beta_context_kms"].median()
        ),
        "outer_zone_median_missing_velocity_after_beta_kms": float(
            detail.loc[detail["zone"].eq("outer_ge_30kpc"), "vobs_minus_beta_context_kms"].median()
        ),
        "endpoint_control_status_counts": (
            detail["endpoint_control_status"].value_counts().sort_index().to_dict()
        ),
        "formula_retuned_after_authorization_counts": (
            detail["formula_retuned_after_authorization"].value_counts().sort_index().to_dict()
        ),
        "morphology_relabel_after_authorization_counts": (
            detail["morphology_relabel_after_authorization"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            detail["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "validation_claimed_counts": (
            detail["validation_claimed"].value_counts().sort_index().to_dict()
        ),
        "authorization_claim_boundary": authorization["claim_boundary"],
        "replay_policy": REPLAY_POLICY,
        "carrier_policy": CARRIER_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The authorized beta-context replay is a single-object preliminary control. "
            "It reads the frozen formula unchanged and does not retune, relabel, promote "
            "the kernel, or claim validation."
        ),
    }
    return detail, zone_summary, summary


def main() -> None:
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    detail, zone_summary, summary = run_replay()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    zone_summary.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(zone_summary.to_string(index=False))


if __name__ == "__main__":
    main()
