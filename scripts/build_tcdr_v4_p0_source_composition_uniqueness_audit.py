from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

READINESS = OUT_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
RADIAL_GEOMETRY_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_composition_uniqueness_audit_v0_5.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_composition_uniqueness_audit_summary_v0_5.json"

COMPONENTS = ("bar", "ring", "spiral")
ENDPOINT_POLICY = "do_not_use_rotation_residuals_or_endpoint_scores_for_source_composition_uniqueness"
CLAIM_BOUNDARY = "source_composition_uniqueness_audit_not_endpoint_validation"

STRONG_TOP_WEIGHT = 0.60
STRONG_MARGIN = 0.20
WEAK_TOP_WEIGHT = 0.50
WEAK_MARGIN = 0.10


def _float(value: object) -> float:
    if value is None or pd.isna(value):
        return 0.0
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(result):
        return 0.0
    return result


def _component_weights(row: pd.Series) -> dict[str, float]:
    return {
        component: _float(row.get(f"{component}_component_weight"))
        for component in COMPONENTS
    }


def _entropy(weights: list[float]) -> float:
    positives = [weight for weight in weights if weight > 0.0]
    if not positives:
        return 0.0
    return -sum(weight * math.log(weight) for weight in positives)


def _active_components(weights: dict[str, float]) -> list[str]:
    return [component for component, weight in weights.items() if weight > 0.0]


def _uniqueness_status(weights: dict[str, float], fallback_weight: float) -> tuple[str, str]:
    active = _active_components(weights)
    if not active:
        if fallback_weight > 0.0:
            return "NO_SOURCE_NATIVE_COMPONENTS", "family_proxy_fallback_only"
        return "NO_ACTIVE_COMPONENT_WEIGHT", "zero_component_weight"
    if len(active) == 1:
        return "SOURCE_COMPOSITION_UNIQUE_CANDIDATE", "single_positive_component"

    ordered = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    top_component, top_weight = ordered[0]
    runner_up = ordered[1][1]
    margin = top_weight - runner_up
    if top_weight >= STRONG_TOP_WEIGHT and margin >= STRONG_MARGIN:
        return "SOURCE_COMPOSITION_UNIQUE_CANDIDATE", (
            f"{top_component}_dominates_top_weight_ge_{STRONG_TOP_WEIGHT}_"
            f"margin_ge_{STRONG_MARGIN}"
        )
    if top_weight >= WEAK_TOP_WEIGHT and margin >= WEAK_MARGIN:
        return "SOURCE_COMPOSITION_WEAKLY_UNIQUE_CANDIDATE", (
            f"{top_component}_weakly_dominates_top_weight_ge_{WEAK_TOP_WEIGHT}_"
            f"margin_ge_{WEAK_MARGIN}"
        )
    return "SOURCE_COMPOSITION_AMBIGUOUS", "component_weights_too_close"


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    readiness = pd.read_csv(READINESS)
    radial = pd.read_csv(RADIAL_GEOMETRY_FREEZE)
    keep_readiness = [
        "galaxy",
        "pilot_role",
        "source_family_candidate",
        "compiler_readiness_status",
        "compiled_formula_family_candidate",
        "available_formula_components",
        "source_load_rule_status",
        "support_window_status",
        "dimension_check_status",
        "composition_rule_status",
    ]
    keep_radial = [
        "galaxy",
        "component_mixture_status",
        "active_source_native_components",
        "mixed_kernel_status",
        "bar_component_weight",
        "ring_component_weight",
        "spiral_component_weight",
        "fallback_family_proxy_weight",
        "bar_raw_component_score",
        "ring_raw_component_score",
        "spiral_raw_component_score",
        "weight_policy",
    ]
    data = readiness[keep_readiness].merge(radial[keep_radial], on="galaxy", how="left")

    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        weights = _component_weights(row)
        fallback_weight = _float(row.get("fallback_family_proxy_weight"))
        ordered = sorted(weights.items(), key=lambda item: item[1], reverse=True)
        top_component, top_weight = ordered[0]
        runner_up_component, runner_up_weight = ordered[1]
        status, reason = _uniqueness_status(weights, fallback_weight)
        active = _active_components(weights)
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "compiler_readiness_status": row["compiler_readiness_status"],
                "compiled_formula_family_candidate": row["compiled_formula_family_candidate"],
                "available_formula_components": row["available_formula_components"],
                "component_mixture_status": row["component_mixture_status"],
                "active_source_native_components": row["active_source_native_components"],
                "mixed_kernel_status": row["mixed_kernel_status"],
                "source_composition_uniqueness_status": status,
                "source_composition_uniqueness_reason": reason,
                "top_component": top_component if top_weight > 0.0 else "none",
                "top_component_weight": top_weight,
                "runner_up_component": runner_up_component if runner_up_weight > 0.0 else "none",
                "runner_up_component_weight": runner_up_weight,
                "dominance_margin": top_weight - runner_up_weight,
                "component_entropy": _entropy([weights[component] for component in COMPONENTS]),
                "n_positive_components": len(active),
                "positive_components": ";".join(active) if active else "none",
                "bar_component_weight": weights["bar"],
                "ring_component_weight": weights["ring"],
                "spiral_component_weight": weights["spiral"],
                "fallback_family_proxy_weight": fallback_weight,
                "bar_raw_component_score": _float(row.get("bar_raw_component_score")),
                "ring_raw_component_score": _float(row.get("ring_raw_component_score")),
                "spiral_raw_component_score": _float(row.get("spiral_raw_component_score")),
                "threshold_policy": (
                    f"strong_top_ge_{STRONG_TOP_WEIGHT}_margin_ge_{STRONG_MARGIN};"
                    f"weak_top_ge_{WEAK_TOP_WEIGHT}_margin_ge_{WEAK_MARGIN}"
                ),
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    detail = pd.DataFrame(rows).sort_values(
        ["pilot_role", "source_composition_uniqueness_status", "galaxy"]
    )
    ready_holdout = detail[
        (detail["pilot_role"] == "PILOT_HOLDOUT")
        & (detail["compiler_readiness_status"] == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE")
    ]
    ready_all = detail[
        detail["compiler_readiness_status"] == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
    ]
    summary = {
        "n_rows": int(len(detail)),
        "uniqueness_status_counts": detail[
            "source_composition_uniqueness_status"
        ].value_counts().sort_index().to_dict(),
        "ready_formula_uniqueness_status_counts": ready_all[
            "source_composition_uniqueness_status"
        ].value_counts().sort_index().to_dict(),
        "ready_holdout_uniqueness_status_counts": ready_holdout[
            "source_composition_uniqueness_status"
        ].value_counts().sort_index().to_dict(),
        "ready_holdout_galaxy_status": {
            str(row["galaxy"]): {
                "status": str(row["source_composition_uniqueness_status"]),
                "top_component": str(row["top_component"]),
                "top_component_weight": float(row["top_component_weight"]),
                "dominance_margin": float(row["dominance_margin"]),
                "positive_components": str(row["positive_components"]),
            }
            for _, row in ready_holdout.sort_values("galaxy").iterrows()
        },
        "threshold_policy": {
            "strong_top_weight": STRONG_TOP_WEIGHT,
            "strong_margin": STRONG_MARGIN,
            "weak_top_weight": WEAK_TOP_WEIGHT,
            "weak_margin": WEAK_MARGIN,
        },
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "This source-side audit identifies whether the frozen component composition "
            "is uniquely selected before endpoint scoring. Ambiguous ready-holdout "
            "objects explain why shuffled and ablation controls can remain competitive."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_audit()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
