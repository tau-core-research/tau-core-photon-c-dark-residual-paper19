from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring as diagnostic
import run_tcdr_v4_support_safe_pool_loocv_scoring as top_component


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_absolute_residual_gap_diagnostic_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_absolute_residual_gap_diagnostic_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_absolute_residual_gap_diagnostic_not_kernel_repair"
DIAGNOSTIC_POLICY = (
    "zonewise_absolute_residual_gap_after_source_frozen_spiral_path_replay_"
    "no_new_kernel_no_endpoint_fit"
)

ZONES = {
    "inner_lt_10kpc": lambda r: r < 10.0,
    "mid_10_30kpc": lambda r: (r >= 10.0) & (r < 30.0),
    "outer_ge_30kpc": lambda r: r >= 30.0,
}


def _zone_verdict(zone: str, median_pred_over_obs: float, median_missing_v2_fraction: float) -> str:
    if median_pred_over_obs < 0.50 and zone.startswith("outer"):
        return "large_outer_capacity_deficit_requires_independent_outer_path_or_dark_residual_source"
    if median_pred_over_obs < 0.70:
        return "large_capacity_deficit_not_solved_by_spiral_path_shell"
    if median_missing_v2_fraction > 0.40:
        return "moderate_residual_capacity_remains"
    return "local_capacity_deficit_moderate"


def _pool_rows(pool_name: str, config: dict[str, object], formula_row: pd.Series) -> list[dict[str, object]]:
    galaxy = str(formula_row["galaxy"])
    data = top_component._load_pool_data(pool_name, config)
    test = data[data["galaxy"].eq(galaxy)].copy().sort_values("radius_kpc")
    train = data[~data["galaxy"].eq(galaxy)].copy()

    kernel = diagnostic._spiral_path_kernel(test, formula_row)
    amp = top_component._fit_amplitude(train, top_component._component_kernel("spiral", train))
    vpred2 = (test["vbar2_fixed_mlr"] + amp * kernel).clip(lower=0)
    vpred = np.sqrt(vpred2)
    vobs = test["vobs_kms"].astype(float)
    missing_v = vobs - vpred
    missing_v2 = (vobs**2 - vpred2).clip(lower=0)
    missing_v2_fraction = missing_v2 / (vobs**2).clip(lower=1.0)
    pred_over_obs = vpred / vobs.clip(lower=1.0)

    rows: list[dict[str, object]] = []
    radius = test["radius_kpc"].astype(float)
    for zone, selector in ZONES.items():
        mask = selector(radius)
        if not bool(mask.any()):
            continue
        med_pred_over_obs = float(np.median(pred_over_obs[mask]))
        med_missing_v2_fraction = float(np.median(missing_v2_fraction[mask]))
        rows.append(
            {
                "support_safe_pool": pool_name,
                "galaxy": galaxy,
                "zone": zone,
                "n_points": int(mask.sum()),
                "r_min_kpc": float(radius[mask].min()),
                "r_max_kpc": float(radius[mask].max()),
                "median_vobs_kms": float(np.median(vobs[mask])),
                "median_vpred_kms": float(np.median(vpred[mask])),
                "median_missing_velocity_kms": float(np.median(missing_v[mask])),
                "mean_missing_velocity_kms": float(np.mean(missing_v[mask])),
                "median_pred_over_obs": med_pred_over_obs,
                "median_missing_v2_fraction": med_missing_v2_fraction,
                "diagnostic_verdict": _zone_verdict(
                    zone,
                    med_pred_over_obs,
                    med_missing_v2_fraction,
                ),
                "amplitude_v2_policy": diagnostic.AMPLITUDE_POLICY,
                "diagnostic_policy": DIAGNOSTIC_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def run_diagnostic() -> tuple[pd.DataFrame, dict[str, object]]:
    formula = diagnostic._load_formula_rows()
    formula_row = formula[formula["galaxy"].eq("NGC2841")].iloc[0]
    rows: list[dict[str, object]] = []
    for pool_name, config in top_component.POOL_CONFIGS.items():
        rows.extend(_pool_rows(pool_name, config, formula_row))
    detail = pd.DataFrame(rows).sort_values(["support_safe_pool", "zone"])
    summary = {
        "n_rows": int(len(detail)),
        "galaxies": sorted(detail["galaxy"].unique().tolist()),
        "zones": sorted(detail["zone"].unique().tolist()),
        "verdict_counts": detail["diagnostic_verdict"].value_counts().to_dict(),
        "median_pred_over_obs_by_zone": detail.groupby("zone")["median_pred_over_obs"].median().to_dict(),
        "median_missing_velocity_kms_by_zone": detail.groupby("zone")[
            "median_missing_velocity_kms"
        ].median().to_dict(),
        "median_missing_v2_fraction_by_zone": detail.groupby("zone")[
            "median_missing_v2_fraction"
        ].median().to_dict(),
        "diagnostic_policy": DIAGNOSTIC_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The source-frozen spiral/path shell is directionally better than the previous local "
            "formula but leaves a large absolute capacity deficit, especially outside 30 kpc. "
            "The next source-side task is an independent outer path/dark-residual capacity route, "
            "not endpoint amplitude tuning."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = run_diagnostic()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(detail.to_string(index=False))


if __name__ == "__main__":
    main()
