from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

MIXTURE_AUDIT = OUT_DIR / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"
COORDINATE_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
SOURCE_ROUTE = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_v0_2.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_summary_v0_2.json"

WEIGHT_POLICY = (
    "source_native_strength_weighted_mixed_component_freeze_v0_2_"
    "bar_ring_strength_proxy_spiral_pitch_segment_span_no_endpoint_inputs"
)


def _float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def _active_components(text: object) -> list[str]:
    if text is None or pd.isna(text):
        return []
    return [item for item in str(text).split(";") if item in {"bar", "ring", "spiral"}]


def _spiral_score(row: pd.Series) -> float:
    pitch = _float(row.get("spiral_pitch_median_abs_deg_source"))
    if pitch is None:
        return 0.0
    segment_count = _float(row.get("spiral_segment_count")) or 1.0
    inner = _float(row.get("spiral_inner_radius_min_arcsec"))
    outer = _float(row.get("spiral_outer_radius_max_arcsec"))
    segment_score = min(max(segment_count, 1.0), 6.0) / 6.0
    pitch_score = min(max(abs(pitch), 5.0), 30.0) / 30.0
    if inner is None or outer is None or outer <= 0 or outer <= inner:
        span_score = 0.5
    else:
        span_score = min(max((outer - inner) / outer, 0.0), 1.0)
    return max(0.05, 0.4 * segment_score + 0.3 * pitch_score + 0.3 * span_score)


def _raw_scores(row: pd.Series, active: list[str]) -> dict[str, float]:
    scores = {"bar": 0.0, "ring": 0.0, "spiral": 0.0}
    if "bar" in active:
        scores["bar"] = max(0.05, _float(row.get("bar_strength_proxy")) or 0.05)
    if "ring" in active:
        scores["ring"] = max(0.05, _float(row.get("ring_strength_proxy")) or 0.05)
    if "spiral" in active:
        scores["spiral"] = _spiral_score(row)
    return scores


def _weights(row: pd.Series, active: list[str]) -> tuple[dict[str, float], dict[str, float]]:
    if not active:
        return (
            {"bar": 0.0, "ring": 0.0, "spiral": 0.0},
            {"bar": 0.0, "ring": 0.0, "spiral": 0.0, "fallback_family_proxy": 1.0},
        )
    scores = _raw_scores(row, active)
    total = sum(scores[component] for component in active)
    if total <= 0:
        equal = 1.0 / len(active)
        weights = {component: (equal if component in active else 0.0) for component in ["bar", "ring", "spiral"]}
    else:
        weights = {component: (scores[component] / total if component in active else 0.0) for component in ["bar", "ring", "spiral"]}
    weights["fallback_family_proxy"] = 0.0
    return scores, weights


def _kernel_status(active: list[str]) -> str:
    if not active:
        return "fallback_family_proxy_kernel"
    if len(active) == 1:
        return "single_strength_weighted_source_native_component_kernel"
    return "mixed_strength_weighted_source_native_component_kernel"


def build_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    audit = pd.read_csv(MIXTURE_AUDIT)
    coords = pd.read_csv(COORDINATE_FREEZE)
    route = pd.read_csv(SOURCE_ROUTE)
    detail = audit.merge(
        coords[["galaxy", "bar_strength_proxy", "ring_strength_proxy"]],
        on="galaxy",
        how="left",
    ).merge(
        route[
            [
                "galaxy",
                "spiral_segment_count",
                "spiral_inner_radius_min_arcsec",
                "spiral_outer_radius_max_arcsec",
            ]
        ],
        on="galaxy",
        how="left",
    )
    rows: list[dict[str, object]] = []
    for _, row in detail.iterrows():
        active = _active_components(row["active_source_native_components"])
        scores, weights = _weights(row, active)
        total_weight = sum(weights.values())
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "component_mixture_status": row["component_mixture_status"],
                "active_source_native_components": row["active_source_native_components"],
                "mixed_kernel_status": _kernel_status(active),
                "bar_source_evidence_score": scores["bar"],
                "ring_source_evidence_score": scores["ring"],
                "spiral_source_evidence_score": scores["spiral"],
                "bar_component_weight": weights["bar"],
                "ring_component_weight": weights["ring"],
                "spiral_component_weight": weights["spiral"],
                "fallback_family_proxy_weight": weights["fallback_family_proxy"],
                "total_kernel_weight": total_weight,
                "weight_policy": WEIGHT_POLICY,
                "endpoint_data_policy": (
                    "do_not_use_rotation_residuals_or_endpoint_scores_for_strength_weighted_mixed_component_kernel_freeze"
                ),
                "claim_boundary": "source_native_strength_weighted_mixed_component_kernel_freeze_not_endpoint_validation",
            }
        )

    result = pd.DataFrame(rows).sort_values(["mixed_kernel_status", "source_family_candidate", "pilot_role", "galaxy"]).reset_index(drop=True)
    holdout = result[result["pilot_role"] == "PILOT_HOLDOUT"].copy()
    summary = {
        "n_rows": int(len(result)),
        "mixed_kernel_status_counts": {
            str(key): int(value)
            for key, value in result["mixed_kernel_status"].value_counts().sort_index().items()
        },
        "holdout_mixed_kernel_status_counts": {
            str(key): int(value)
            for key, value in holdout["mixed_kernel_status"].value_counts().sort_index().items()
        },
        "weight_policy": WEIGHT_POLICY,
        "endpoint_data_policy": (
            "do_not_use_rotation_residuals_or_endpoint_scores_for_strength_weighted_mixed_component_kernel_freeze"
        ),
        "verdict": (
            "The v0.2 mixed-component weights are frozen from source-side component evidence. "
            "They refine v0.1 without using endpoint curves, residuals, or scores."
        ),
    }
    return result, summary


def main() -> None:
    detail, summary = build_freeze()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
