from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_support_safe_pool_loocv_scoring as top_component


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

FORMULA_FREEZE = SOURCE_DIR / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_v0_1.csv"
READINESS_SCORING = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_readiness_filtered_scoring_local.csv"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring_summary_local.json"

CLAIM_BOUNDARY = "allowed_failure_spiral_path_diagnostic_scoring_not_validation"
SCORING_POLICY = (
    "allowed_failure_spiral_path_formula_shell_diagnostic_replay_"
    "train_only_spiral_control_amplitude_no_target_tuning_no_validation"
)
AMPLITUDE_POLICY = (
    "spiral_control_amplitude_fit_on_other_support_safe_pool_galaxies_only_"
    "target_galaxy_formula_shape_source_frozen_no_target_amplitude_tuning"
)
KERNEL_SHAPE_POLICY = (
    "ngc2841_caveated_spiral_path_window_from_frozen_source_observables_"
    "kendall2011_zhang2018_no_rotation_curve_shape_tuning"
)


def _load_formula_rows() -> pd.DataFrame:
    if not FORMULA_FREEZE.exists():
        raise FileNotFoundError(f"Missing formula freeze artifact: {FORMULA_FREEZE}")
    formula = pd.read_csv(FORMULA_FREEZE)
    formula = formula[
        formula["formula_freeze_status"].eq("frozen_caveated_source_formula_no_scoring")
        & formula["formula_freeze_permission"].eq("yes_source_formula_frozen_no_scoring")
    ].copy()
    if formula.empty:
        raise RuntimeError("No source-frozen spiral/path formula row is available for diagnostic scoring.")
    return formula


def _spiral_path_kernel(group: pd.DataFrame, formula_row: pd.Series) -> pd.Series:
    radius = group["radius_kpc"].astype(float)
    r_in = float(formula_row["r_in_kpc"])
    r_out = float(formula_row["r_out_kpc"])
    r_path = float(formula_row["r_path_kpc"])
    sigma_edge = float(formula_row["sigma_edge_kpc"])
    sigma_path = float(formula_row["sigma_path_kpc"])
    epsilon_path = float(formula_row["epsilon_path"])

    spiral_window = 0.5 * (
        np.tanh((radius - r_in) / sigma_edge) - np.tanh((radius - r_out) / sigma_edge)
    )
    path_gate = 1.0 / (1.0 + np.exp(-(radius - r_path) / sigma_path))
    kernel = spiral_window + epsilon_path * path_gate
    return pd.Series(np.clip(kernel, 0.0, 1.0), index=group.index)


def _pool_row(
    pool_name: str,
    config: dict[str, object],
    formula_row: pd.Series,
    readiness: pd.DataFrame,
) -> dict[str, object]:
    galaxy = str(formula_row["galaxy"])
    data = top_component._load_pool_data(pool_name, config)
    if galaxy not in set(data["galaxy"]):
        raise RuntimeError(f"{galaxy} is not present in {pool_name}.")

    test = data[data["galaxy"].eq(galaxy)].copy()
    train = data[~data["galaxy"].eq(galaxy)].copy()

    formula_kernel_test = _spiral_path_kernel(test, formula_row)
    spiral_kernel_train = top_component._component_kernel("spiral", train)
    spiral_control_amp = top_component._fit_amplitude(train, spiral_kernel_train)
    formula_rmse, formula_wrmse = top_component._weighted_rmse(
        test,
        formula_kernel_test,
        spiral_control_amp,
    )

    baryonic_rmse, baryonic_wrmse = top_component._weighted_rmse(
        test,
        pd.Series(0.0, index=test.index),
        0.0,
    )
    current = readiness[
        readiness["support_safe_pool"].eq(pool_name) & readiness["galaxy"].eq(galaxy)
    ]
    if current.empty:
        current_row: dict[str, object] = {}
    else:
        current_row = current.iloc[0].to_dict()

    current_candidate = float(current_row.get("candidate_weighted_rmse_kms", np.nan))
    current_matched_control = float(
        current_row.get("matched_component_control_weighted_rmse_kms", np.nan)
    )
    current_best_wrong = float(current_row.get("best_wrong_component_weighted_rmse_kms", np.nan))
    current_wrong_mean = float(current_row.get("wrong_component_mean_weighted_rmse_kms", np.nan))

    radii = test["radius_kpc"].astype(float)
    r_in = float(formula_row["r_in_kpc"])
    r_out = float(formula_row["r_out_kpc"])
    r_path = float(formula_row["r_path_kpc"])

    return {
        "support_safe_pool": pool_name,
        "galaxy": galaxy,
        "formula_id": str(formula_row["formula_id"]),
        "n_train_galaxies": int(train["galaxy"].nunique()),
        "n_test_points": int(len(test)),
        "r_min_kpc": float(radii.min()),
        "r_max_kpc": float(radii.max()),
        "spiral_window_points": int(((radii >= r_in) & (radii <= r_out)).sum()),
        "path_gate_points": int((radii >= r_path).sum()),
        "formula_kernel_mean": float(formula_kernel_test.mean()),
        "formula_kernel_max": float(formula_kernel_test.max()),
        "spiral_control_train_amplitude_v2": spiral_control_amp,
        "baryonic_carrier_weighted_rmse_kms": baryonic_wrmse,
        "current_formula_weighted_rmse_kms": current_candidate,
        "current_matched_component_control_weighted_rmse_kms": current_matched_control,
        "current_wrong_component_mean_weighted_rmse_kms": current_wrong_mean,
        "current_best_wrong_component_weighted_rmse_kms": current_best_wrong,
        "spiral_path_formula_weighted_rmse_kms": formula_wrmse,
        "spiral_path_formula_rmse_kms": formula_rmse,
        "spiral_path_minus_current_formula_weighted_rmse_kms": formula_wrmse - current_candidate,
        "spiral_path_minus_best_wrong_weighted_rmse_kms": formula_wrmse - current_best_wrong,
        "spiral_path_minus_baryonic_weighted_rmse_kms": formula_wrmse - baryonic_wrmse,
        "spiral_path_beats_current_formula": "yes" if formula_wrmse < current_candidate else "no",
        "spiral_path_beats_best_wrong": "yes" if formula_wrmse < current_best_wrong else "no",
        "spiral_path_beats_baryonic": "yes" if formula_wrmse < baryonic_wrmse else "no",
        "diagnostic_scoring_status": "diagnostic_replay_completed_no_validation",
        "endpoint_validation_claimed": "no",
        "kernel_promotion_permission": "no",
        "new_route_scoring_permission": "diagnostic_only_no_promotion",
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
        "scoring_policy": SCORING_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_scoring() -> tuple[pd.DataFrame, dict[str, object]]:
    formula = _load_formula_rows()
    if READINESS_SCORING.exists():
        readiness = pd.read_csv(READINESS_SCORING)
    else:
        readiness = pd.DataFrame()

    rows = []
    for _, formula_row in formula.iterrows():
        for pool_name, config in top_component.POOL_CONFIGS.items():
            rows.append(_pool_row(pool_name, config, formula_row, readiness))

    detail = pd.DataFrame(rows).sort_values(["galaxy", "support_safe_pool"])
    summary = {
        "n_rows": int(len(detail)),
        "galaxies": sorted(detail["galaxy"].unique().tolist()),
        "formula_ids": sorted(detail["formula_id"].unique().tolist()),
        "diagnostic_status_counts": detail["diagnostic_scoring_status"].value_counts().to_dict(),
        "endpoint_validation_claimed_counts": detail["endpoint_validation_claimed"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": detail["kernel_promotion_permission"].value_counts().to_dict(),
        "spiral_path_beats_current_formula_counts": detail[
            "spiral_path_beats_current_formula"
        ].value_counts().to_dict(),
        "spiral_path_beats_best_wrong_counts": detail[
            "spiral_path_beats_best_wrong"
        ].value_counts().to_dict(),
        "spiral_path_beats_baryonic_counts": detail["spiral_path_beats_baryonic"].value_counts().to_dict(),
        "median_spiral_path_minus_current_formula_weighted_rmse_kms": float(
            detail["spiral_path_minus_current_formula_weighted_rmse_kms"].median()
        ),
        "median_spiral_path_minus_best_wrong_weighted_rmse_kms": float(
            detail["spiral_path_minus_best_wrong_weighted_rmse_kms"].median()
        ),
        "median_spiral_path_minus_baryonic_weighted_rmse_kms": float(
            detail["spiral_path_minus_baryonic_weighted_rmse_kms"].median()
        ),
        "scoring_policy": SCORING_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return detail, summary


def main() -> None:
    detail, summary = run_scoring()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    detail.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(detail.to_string(index=False))


if __name__ == "__main__":
    main()
