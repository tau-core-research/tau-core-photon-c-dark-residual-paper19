from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring_mixed_components as mixed


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

READINESS = SOURCE_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
RADIAL_GEOMETRY_FREEZE = (
    SOURCE_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"
)

OUT_DETAIL = (
    EXTERNAL_DIR
    / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_component_ablation_detail_local.csv"
)
OUT_SUMMARY = (
    EXTERNAL_DIR
    / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_component_ablation_summary_local.csv"
)
OUT_JSON = (
    EXTERNAL_DIR
    / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_component_ablation_summary_local.json"
)

READY_STATUS = "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
VARIANTS = [
    "full_source_mix",
    "bar_only",
    "ring_only",
    "spiral_only",
    "leaveout_bar",
    "leaveout_ring",
    "leaveout_spiral",
]
COMPONENTS = ("bar", "ring", "spiral")
KERNEL_SHAPE_POLICY = (
    "formula_compiler_ready_v0_4_component_ablation_using_radial_geometry_mixed_freeze_v0_3_"
    "no_family_fallback_for_ablation_no_holdout_shape_tuning"
)
AMPLITUDE_POLICY = (
    "single_variant_amplitude_fit_on_formula_ready_train_pool_only_"
    "nonnegative_weighted_no_holdout_tuning"
)
SCORING_POLICY = (
    "formula_ready_holdout_only_component_ablation_diagnostic_not_endpoint_validation"
)


def _ready_rows(data: pd.DataFrame) -> pd.DataFrame:
    readiness = pd.read_csv(READINESS)[
        [
            "galaxy",
            "compiler_readiness_status",
            "compiled_formula_family_candidate",
            "available_formula_components",
            "missing_source_observables",
            "source_load_rule_status",
            "support_window_status",
            "dimension_check_status",
            "composition_rule_status",
        ]
    ]
    data = data.merge(readiness, on="galaxy", how="left")
    return data[data["compiler_readiness_status"] == READY_STATUS].copy()


def _component_weights(group: pd.DataFrame) -> dict[str, float]:
    return {
        "bar": float(group["bar_component_weight"].iloc[0] or 0.0),
        "ring": float(group["ring_component_weight"].iloc[0] or 0.0),
        "spiral": float(group["spiral_component_weight"].iloc[0] or 0.0),
    }


def _variant_weights(group: pd.DataFrame, variant: str) -> dict[str, float]:
    source = _component_weights(group)
    if variant == "full_source_mix":
        return source
    if variant.endswith("_only"):
        target = variant.removesuffix("_only")
        return {
            component: (1.0 if component == target and source.get(component, 0.0) > 0.0 else 0.0)
            for component in COMPONENTS
        }
    if variant.startswith("leaveout_"):
        target = variant.removeprefix("leaveout_")
        kept = {
            component: weight
            for component, weight in source.items()
            if component != target and weight > 0.0
        }
        total = float(sum(kept.values()))
        if total <= 0.0:
            return {component: 0.0 for component in COMPONENTS}
        return {component: kept.get(component, 0.0) / total for component in COMPONENTS}
    raise ValueError(f"Unknown ablation variant: {variant}")


def _variant_kernel_for_group(group: pd.DataFrame, variant: str) -> pd.Series:
    weights = _variant_weights(group, variant)
    result = pd.Series(0.0, index=group.index)
    for component, weight in weights.items():
        if weight > 0.0:
            result = result + weight * mixed._component_kernel(component, group)
    return result.clip(lower=0)


def _variant_kernel(data: pd.DataFrame, variant: str) -> pd.Series:
    pieces = [
        _variant_kernel_for_group(group, variant)
        for _, group in data.groupby("galaxy", sort=False)
    ]
    if not pieces:
        return pd.Series(dtype=float)
    return pd.concat(pieces).sort_index()


def _fit_variant_amplitude(train: pd.DataFrame, variant: str) -> float:
    k = _variant_kernel(train, variant).to_numpy()
    y = train["y_residual_v2"].to_numpy()
    w = 1.0 / (train["sigma_v2"].to_numpy() ** 2)
    denom = float(np.sum(w * k * k))
    if denom <= 0.0:
        return 0.0
    return max(0.0, float(np.sum(w * k * y) / denom))


def _rmse(group: pd.DataFrame, kernel: pd.Series, amp: float) -> tuple[float, float]:
    vpred2 = (group["vbar2_fixed_mlr"] + amp * kernel).clip(lower=0)
    vpred = np.sqrt(vpred2)
    residual = group["vobs_kms"] - vpred
    weights = 1.0 / (group["e_vobs_kms"].clip(lower=1.0) ** 2)
    return (
        float(np.sqrt(np.mean(residual**2))),
        float(np.sqrt(np.average(residual**2, weights=weights))),
    )


def _load_ready_data() -> pd.DataFrame:
    mixed.MIXED_KERNEL_FREEZE = RADIAL_GEOMETRY_FREEZE
    mixed.KERNEL_SHAPE_POLICY = KERNEL_SHAPE_POLICY
    return _ready_rows(mixed._load_data())


def run_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    data = _load_ready_data()
    train = data[data["pilot_role"] == "PILOT_TRAIN_POOL"].copy()
    holdout = data[data["pilot_role"] == "PILOT_HOLDOUT"].copy()
    amplitudes = {variant: _fit_variant_amplitude(train, variant) for variant in VARIANTS}

    detail_rows = []
    for galaxy, group in holdout.groupby("galaxy", sort=True):
        full_wrmse = None
        variant_scores: dict[str, float] = {}
        for variant in VARIANTS:
            kernel = _variant_kernel_for_group(group, variant)
            rmse, wrmse = _rmse(group, kernel, amplitudes[variant])
            if variant == "full_source_mix":
                full_wrmse = wrmse
            variant_scores[variant] = wrmse
            weights = _variant_weights(group, variant)
            detail_rows.append(
                {
                    "galaxy": galaxy,
                    "variant": variant,
                    "matched_source_family": str(group["source_family_candidate"].iloc[0]),
                    "component_mixture_status": str(group["component_mixture_status"].iloc[0]),
                    "active_source_native_components": str(group["active_source_native_components"].iloc[0]),
                    "compiled_formula_family_candidate": str(
                        group["compiled_formula_family_candidate"].iloc[0]
                    ),
                    "available_formula_components": str(group["available_formula_components"].iloc[0]),
                    "n_points": int(len(group)),
                    "rmse_kms": rmse,
                    "weighted_rmse_kms": wrmse,
                    "amplitude_v2": amplitudes[variant],
                    "variant_bar_weight": weights["bar"],
                    "variant_ring_weight": weights["ring"],
                    "variant_spiral_weight": weights["spiral"],
                    "source_bar_weight": float(group["bar_component_weight"].iloc[0] or 0.0),
                    "source_ring_weight": float(group["ring_component_weight"].iloc[0] or 0.0),
                    "source_spiral_weight": float(group["spiral_component_weight"].iloc[0] or 0.0),
                    "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                    "carrier_policy": mixed.base.CARRIER_POLICY,
                    "amplitude_policy": AMPLITUDE_POLICY,
                    "scoring_policy": SCORING_POLICY,
                }
            )
        best_variant = min(variant_scores, key=variant_scores.get)
        for row in detail_rows:
            if row["galaxy"] == galaxy:
                row["full_source_mix_weighted_rmse_kms"] = full_wrmse
                row["delta_vs_full_source_mix_weighted_rmse_kms"] = (
                    row["weighted_rmse_kms"] - full_wrmse
                    if full_wrmse is not None
                    else float("nan")
                )
                row["best_ablation_variant_for_galaxy"] = best_variant

    detail = pd.DataFrame(detail_rows)
    summary_rows = []
    for variant, group in detail.groupby("variant", sort=False):
        summary_rows.append(
            {
                "variant": variant,
                "n_holdout_galaxies": int(group["galaxy"].nunique()),
                "median_weighted_rmse_kms": float(group["weighted_rmse_kms"].median()),
                "mean_weighted_rmse_kms": float(group["weighted_rmse_kms"].mean()),
                "median_delta_vs_full_source_mix_weighted_rmse_kms": float(
                    group["delta_vs_full_source_mix_weighted_rmse_kms"].median()
                ),
                "mean_delta_vs_full_source_mix_weighted_rmse_kms": float(
                    group["delta_vs_full_source_mix_weighted_rmse_kms"].mean()
                ),
                "amplitude_v2": amplitudes[variant],
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values("median_weighted_rmse_kms")

    full_median = float(
        summary.loc[summary["variant"] == "full_source_mix", "median_weighted_rmse_kms"].iloc[0]
    )
    best_variant = str(summary.iloc[0]["variant"])
    best_median = float(summary.iloc[0]["median_weighted_rmse_kms"])
    best_counts = detail.groupby("galaxy")["best_ablation_variant_for_galaxy"].first().value_counts()
    aggregate = {
        "n_train_pool_galaxies": int(train["galaxy"].nunique()),
        "n_holdout_galaxies": int(holdout["galaxy"].nunique()),
        "n_train_points": int(len(train)),
        "n_holdout_points": int(len(holdout)),
        "formula_compiler_ready_status": READY_STATUS,
        "formula_ready_holdout_galaxies": sorted(holdout["galaxy"].unique().tolist()),
        "variant_amplitudes_v2": amplitudes,
        "full_source_mix_median_weighted_rmse_kms": full_median,
        "best_ablation_variant_by_median_weighted_rmse": best_variant,
        "best_ablation_variant_median_weighted_rmse_kms": best_median,
        "full_source_mix_beats_all_component_ablation_medians": bool(
            best_variant == "full_source_mix"
        ),
        "best_variant_counts_by_galaxy": {
            str(key): int(value) for key, value in best_counts.items()
        },
        "component_ablation_interpretation": (
            "If a single-component or leave-one-out variant matches or beats the full mix, "
            "the present source-frozen composition is not yet uniquely selected by the "
            "available source observables."
        ),
        "readiness_manifest": str(READINESS.relative_to(ROOT)),
        "radial_geometry_freeze_manifest": str(RADIAL_GEOMETRY_FREEZE.relative_to(ROOT)),
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "carrier_policy": mixed.base.CARRIER_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
        "scoring_policy": SCORING_POLICY,
        "claim_boundary": (
            "formula_compiler_ready_component_ablation_preflight_not_population_validation"
        ),
    }
    return detail.sort_values(["galaxy", "variant"]), summary, aggregate


def main() -> None:
    detail, summary, aggregate = run_scoring()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    summary.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(aggregate, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
