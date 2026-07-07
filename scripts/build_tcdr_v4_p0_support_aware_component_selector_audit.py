from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

UNIQUENESS = OUT_DIR / "tcdr_v4_p0_source_composition_uniqueness_audit_v0_5.csv"
COORDINATES = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
ROUTE = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_summary_v0_6.json"

COMPONENTS = ("bar", "ring", "spiral")
ENDPOINT_POLICY = "do_not_use_rotation_residuals_or_endpoint_scores_for_support_aware_selector"
CLAIM_BOUNDARY = "support_aware_component_selector_audit_not_endpoint_validation"
ADJACENT_SUPPORT_FRACTION = 0.25


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


def _arcsec_to_kpc(arcsec: float | None, distance_mpc: float | None) -> float | None:
    if arcsec is None or distance_mpc is None:
        return None
    return arcsec * distance_mpc * 1000.0 / 206265.0


def _positive_components(row: pd.Series) -> list[str]:
    text = row.get("positive_components")
    if text is None or pd.isna(text) or str(text) == "none":
        return []
    return [item for item in str(text).split(";") if item in COMPONENTS]


def _radius_in_span(radius: float | None, inner: float | None, outer: float | None) -> bool:
    if radius is None or inner is None or outer is None:
        return False
    lo = min(inner, outer)
    hi = max(inner, outer)
    return lo <= radius <= hi


def _radius_adjacent_to_span(
    radius: float | None,
    inner: float | None,
    outer: float | None,
    fraction: float = ADJACENT_SUPPORT_FRACTION,
) -> bool:
    if radius is None or inner is None or outer is None:
        return False
    lo = min(inner, outer)
    hi = max(inner, outer)
    span = max(hi - lo, hi, lo, 1.0)
    distance = min(abs(radius - lo), abs(radius - hi))
    return distance / span <= fraction


def _support_flags(row: pd.Series) -> dict[str, object]:
    distance = _float(row.get("distance_mpc_source"))
    spiral_inner = _arcsec_to_kpc(_float(row.get("spiral_inner_radius_min_arcsec")), distance)
    spiral_outer = _arcsec_to_kpc(_float(row.get("spiral_outer_radius_max_arcsec")), distance)
    bar_radius = _float(row.get("bar_radius_kpc_source"))
    ring_radius = _float(row.get("ring_radius_kpc_source"))
    positive = set(_positive_components(row))

    ring_spiral_overlap = (
        "ring" in positive
        and "spiral" in positive
        and _radius_in_span(ring_radius, spiral_inner, spiral_outer)
    )
    ring_spiral_adjacent = (
        "ring" in positive
        and "spiral" in positive
        and not ring_spiral_overlap
        and _radius_adjacent_to_span(ring_radius, spiral_inner, spiral_outer)
    )
    bar_spiral_overlap = (
        "bar" in positive
        and "spiral" in positive
        and _radius_in_span(bar_radius, spiral_inner, spiral_outer)
    )
    bar_spiral_adjacent = (
        "bar" in positive
        and "spiral" in positive
        and not bar_spiral_overlap
        and _radius_adjacent_to_span(bar_radius, spiral_inner, spiral_outer)
    )
    bar_ring_close = False
    if "bar" in positive and "ring" in positive and bar_radius is not None and ring_radius is not None:
        scale = max(abs(bar_radius), abs(ring_radius), 1.0)
        bar_ring_close = abs(bar_radius - ring_radius) / scale < 0.35

    overlap_reasons = []
    if ring_spiral_overlap:
        overlap_reasons.append("ring_radius_inside_spiral_radial_span")
    if ring_spiral_adjacent:
        overlap_reasons.append("ring_radius_adjacent_to_spiral_radial_span")
    if bar_spiral_overlap:
        overlap_reasons.append("bar_radius_inside_spiral_radial_span")
    if bar_spiral_adjacent:
        overlap_reasons.append("bar_radius_adjacent_to_spiral_radial_span")
    if bar_ring_close:
        overlap_reasons.append("bar_ring_radii_close")

    missing_support = []
    if "spiral" in positive and (spiral_inner is None or spiral_outer is None):
        missing_support.append("spiral_support_span_missing")
    if "ring" in positive and ring_radius is None:
        missing_support.append("ring_radius_missing")
    if "bar" in positive and bar_radius is None:
        missing_support.append("bar_radius_missing")

    return {
        "spiral_inner_kpc_source": spiral_inner,
        "spiral_outer_kpc_source": spiral_outer,
        "ring_spiral_support_overlap": "yes" if ring_spiral_overlap else "no",
        "ring_spiral_support_adjacent": "yes" if ring_spiral_adjacent else "no",
        "bar_spiral_support_overlap": "yes" if bar_spiral_overlap else "no",
        "bar_spiral_support_adjacent": "yes" if bar_spiral_adjacent else "no",
        "bar_ring_support_close": "yes" if bar_ring_close else "no",
        "support_overlap_reasons": ";".join(overlap_reasons) if overlap_reasons else "none",
        "missing_support_reasons": ";".join(missing_support) if missing_support else "none",
        "has_support_overlap": bool(overlap_reasons),
        "has_missing_support": bool(missing_support),
    }


def _selector_status(row: pd.Series, flags: dict[str, object]) -> tuple[str, str]:
    uniqueness = str(row["source_composition_uniqueness_status"])
    positive = _positive_components(row)
    if not positive:
        return "SUPPORT_AWARE_SELECTOR_UNCOVERED", "no_source_native_components"
    if flags["has_missing_support"]:
        return "SUPPORT_AWARE_SELECTOR_UNRESOLVED_MISSING_SUPPORT", str(
            flags["missing_support_reasons"]
        )
    if flags["has_support_overlap"]:
        return "SUPPORT_AWARE_SELECTOR_UNRESOLVED_OVERLAPPING_SUPPORT", str(
            flags["support_overlap_reasons"]
        )
    if uniqueness == "SOURCE_COMPOSITION_UNIQUE_CANDIDATE":
        if len(positive) == 1:
            return "SUPPORT_AWARE_SELECTOR_SAFE_SINGLE_COMPONENT", "single_component_no_overlap"
        return "SUPPORT_AWARE_SELECTOR_SAFE_DOMINANT_DISJOINT", "dominant_component_disjoint_support"
    if uniqueness == "SOURCE_COMPOSITION_WEAKLY_UNIQUE_CANDIDATE":
        return "SUPPORT_AWARE_SELECTOR_WEAK_CANDIDATE", "weak_weight_dominance_disjoint_support"
    if uniqueness == "SOURCE_COMPOSITION_AMBIGUOUS":
        return "SUPPORT_AWARE_SELECTOR_UNRESOLVED_AMBIGUOUS_WEIGHTS", "component_weights_too_close"
    return "SUPPORT_AWARE_SELECTOR_UNRESOLVED", "unclassified_source_state"


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    uniqueness = pd.read_csv(UNIQUENESS)
    coords = pd.read_csv(COORDINATES)
    route = pd.read_csv(ROUTE)
    data = (
        uniqueness.merge(
            coords[
                [
                    "galaxy",
                    "distance_mpc_source",
                    "bar_radius_kpc_source",
                    "ring_radius_kpc_source",
                ]
            ],
            on="galaxy",
            how="left",
        )
        .merge(
            route[
                [
                    "galaxy",
                    "spiral_inner_radius_min_arcsec",
                    "spiral_outer_radius_max_arcsec",
                    "spiral_segment_count",
                    "feature_types_present",
                ]
            ],
            on="galaxy",
            how="left",
        )
    )

    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        flags = _support_flags(row)
        selector_status, selector_reason = _selector_status(row, flags)
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "compiler_readiness_status": row["compiler_readiness_status"],
                "source_composition_uniqueness_status": row[
                    "source_composition_uniqueness_status"
                ],
                "support_aware_selector_status": selector_status,
                "support_aware_selector_reason": selector_reason,
                "top_component": row["top_component"],
                "top_component_weight": row["top_component_weight"],
                "dominance_margin": row["dominance_margin"],
                "positive_components": row["positive_components"],
                "bar_component_weight": row["bar_component_weight"],
                "ring_component_weight": row["ring_component_weight"],
                "spiral_component_weight": row["spiral_component_weight"],
                "bar_radius_kpc_source": row.get("bar_radius_kpc_source"),
                "ring_radius_kpc_source": row.get("ring_radius_kpc_source"),
                "spiral_inner_kpc_source": flags["spiral_inner_kpc_source"],
                "spiral_outer_kpc_source": flags["spiral_outer_kpc_source"],
                "spiral_segment_count": row.get("spiral_segment_count"),
                "feature_types_present": row.get("feature_types_present"),
                "ring_spiral_support_overlap": flags["ring_spiral_support_overlap"],
                "ring_spiral_support_adjacent": flags["ring_spiral_support_adjacent"],
                "bar_spiral_support_overlap": flags["bar_spiral_support_overlap"],
                "bar_spiral_support_adjacent": flags["bar_spiral_support_adjacent"],
                "bar_ring_support_close": flags["bar_ring_support_close"],
                "support_overlap_reasons": flags["support_overlap_reasons"],
                "missing_support_reasons": flags["missing_support_reasons"],
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    detail = pd.DataFrame(rows).sort_values(["pilot_role", "support_aware_selector_status", "galaxy"])
    ready_holdout = detail[
        (detail["pilot_role"] == "PILOT_HOLDOUT")
        & (detail["compiler_readiness_status"] == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE")
    ]
    ready_all = detail[
        detail["compiler_readiness_status"] == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
    ]
    safe_statuses = {
        "SUPPORT_AWARE_SELECTOR_SAFE_SINGLE_COMPONENT",
        "SUPPORT_AWARE_SELECTOR_SAFE_DOMINANT_DISJOINT",
    }
    summary = {
        "n_rows": int(len(detail)),
        "support_aware_selector_status_counts": detail[
            "support_aware_selector_status"
        ].value_counts().sort_index().to_dict(),
        "ready_formula_support_aware_selector_status_counts": ready_all[
            "support_aware_selector_status"
        ].value_counts().sort_index().to_dict(),
        "ready_holdout_support_aware_selector_status_counts": ready_holdout[
            "support_aware_selector_status"
        ].value_counts().sort_index().to_dict(),
        "n_ready_formula_selector_safe": int(
            ready_all["support_aware_selector_status"].isin(safe_statuses).sum()
        ),
        "n_ready_holdout_selector_safe": int(
            ready_holdout["support_aware_selector_status"].isin(safe_statuses).sum()
        ),
        "ready_holdout_selector_status": {
            str(row["galaxy"]): {
                "status": str(row["support_aware_selector_status"]),
                "reason": str(row["support_aware_selector_reason"]),
                "top_component": str(row["top_component"]),
                "positive_components": str(row["positive_components"]),
            }
            for _, row in ready_holdout.sort_values("galaxy").iterrows()
        },
        "endpoint_data_policy": ENDPOINT_POLICY,
        "adjacent_support_fraction": ADJACENT_SUPPORT_FRACTION,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "This endpoint-blind support-aware audit demotes weight-dominant "
            "component selections when their radial source supports overlap or "
            "when support data are missing. It distinguishes formula readiness "
            "from selector safety."
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
