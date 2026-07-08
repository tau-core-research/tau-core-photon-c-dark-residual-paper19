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

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_outer_capacity_requirement_audit_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_outer_capacity_requirement_audit_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_outer_capacity_requirement_audit_not_kernel_repair"
AUDIT_POLICY = (
    "post_scoring_capacity_requirement_diagnostic_no_formula_change_"
    "no_endpoint_fit_no_kernel_promotion"
)

ZONES = {
    "inner_lt_10kpc": lambda r: r < 10.0,
    "mid_10_30kpc": lambda r: (r >= 10.0) & (r < 30.0),
    "outer_ge_30kpc": lambda r: r >= 30.0,
}


def _spiral_window_and_path(group: pd.DataFrame, formula_row: pd.Series) -> tuple[pd.Series, pd.Series]:
    radius = group["radius_kpc"].astype(float)
    r_in = float(formula_row["r_in_kpc"])
    r_out = float(formula_row["r_out_kpc"])
    r_path = float(formula_row["r_path_kpc"])
    sigma_edge = float(formula_row["sigma_edge_kpc"])
    sigma_path = float(formula_row["sigma_path_kpc"])

    spiral_window = 0.5 * (
        np.tanh((radius - r_in) / sigma_edge) - np.tanh((radius - r_out) / sigma_edge)
    )
    path_gate = 1.0 / (1.0 + np.exp(-(radius - r_path) / sigma_path))
    return (
        pd.Series(np.clip(spiral_window, 0.0, 1.0), index=group.index),
        pd.Series(np.clip(path_gate, 0.0, 1.0), index=group.index),
    )


def _verdict(required_epsilon: float, epsilon_cap: float, zone: str) -> str:
    if required_epsilon > 10.0 * epsilon_cap and zone.startswith("outer"):
        return "outer_capacity_requires_new_independent_dark_residual_or_path_source"
    if required_epsilon > 3.0 * epsilon_cap:
        return "capacity_requirement_exceeds_source_frozen_path_cap"
    return "capacity_requirement_within_caveated_path_cap"


def _pool_rows(pool_name: str, config: dict[str, object], formula_row: pd.Series) -> list[dict[str, object]]:
    galaxy = str(formula_row["galaxy"])
    data = top_component._load_pool_data(pool_name, config)
    test = data[data["galaxy"].eq(galaxy)].copy().sort_values("radius_kpc")
    train = data[~data["galaxy"].eq(galaxy)].copy()

    spiral_window, path_gate = _spiral_window_and_path(test, formula_row)
    amp = top_component._fit_amplitude(train, top_component._component_kernel("spiral", train))
    epsilon_cap = float(formula_row["epsilon_path"])
    current_kernel = np.clip(spiral_window + epsilon_cap * path_gate, 0.0, 1.0)

    vbar2 = test["vbar2_fixed_mlr"].astype(float)
    vobs2 = test["vobs_kms"].astype(float) ** 2
    current_vpred2 = (vbar2 + amp * current_kernel).clip(lower=0)
    missing_v2 = (vobs2 - current_vpred2).clip(lower=0)

    # Required epsilon is diagnostic only: it asks how much path weight would be
    # necessary to close the observed v^2 gap if the current source-frozen
    # carrier/amplitude were left unchanged. It is never fed back into a kernel.
    denominator = amp * path_gate.replace(0.0, np.nan)
    required_epsilon_point = ((vobs2 - vbar2 - amp * spiral_window) / denominator).replace(
        [np.inf, -np.inf],
        np.nan,
    )
    required_epsilon_positive = required_epsilon_point.clip(lower=0)

    rows: list[dict[str, object]] = []
    radius = test["radius_kpc"].astype(float)
    for zone, selector in ZONES.items():
        mask = selector(radius)
        if not bool(mask.any()):
            continue
        zone_required = required_epsilon_positive[mask].dropna()
        if zone_required.empty:
            median_required = float("nan")
            q75_required = float("nan")
        else:
            median_required = float(np.median(zone_required))
            q75_required = float(np.quantile(zone_required, 0.75))
        cap_ratio = median_required / epsilon_cap if epsilon_cap > 0 and np.isfinite(median_required) else float("nan")
        rows.append(
            {
                "support_safe_pool": pool_name,
                "galaxy": galaxy,
                "zone": zone,
                "n_points": int(mask.sum()),
                "r_min_kpc": float(radius[mask].min()),
                "r_max_kpc": float(radius[mask].max()),
                "epsilon_path_cap": epsilon_cap,
                "median_required_epsilon_path_to_close_v2_gap": median_required,
                "q75_required_epsilon_path_to_close_v2_gap": q75_required,
                "median_required_to_cap_ratio": cap_ratio,
                "median_missing_v2_kms2": float(np.median(missing_v2[mask])),
                "median_path_gate": float(np.median(path_gate[mask])),
                "spiral_control_train_amplitude_v2": float(amp),
                "capacity_verdict": _verdict(median_required, epsilon_cap, zone),
                "audit_policy": AUDIT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def run_audit() -> tuple[pd.DataFrame, dict[str, object]]:
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
        "capacity_verdict_counts": detail["capacity_verdict"].value_counts().to_dict(),
        "median_required_epsilon_by_zone": detail.groupby("zone")[
            "median_required_epsilon_path_to_close_v2_gap"
        ].median().to_dict(),
        "median_required_to_cap_ratio_by_zone": detail.groupby("zone")[
            "median_required_to_cap_ratio"
        ].median().to_dict(),
        "epsilon_path_cap": float(detail["epsilon_path_cap"].median()),
        "audit_policy": AUDIT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Closing the NGC2841 outer v^2 gap with the present spiral/path shell would require "
            "a path weight far above the source-frozen epsilon cap. The result rejects endpoint "
            "amplitude rescue and points to a separate independent outer path or dark-residual "
            "capacity source requirement."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = run_audit()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(detail.to_string(index=False))


if __name__ == "__main__":
    main()
