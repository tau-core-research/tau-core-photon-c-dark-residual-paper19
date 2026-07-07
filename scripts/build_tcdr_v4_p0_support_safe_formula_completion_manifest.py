from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

OPPORTUNITY = OUT_DIR / "tcdr_v4_p0_support_safe_expansion_opportunity_ledger_v0_8.csv"
SUPPORT_AUDIT = OUT_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"
READINESS = OUT_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
COORDINATES = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_summary_v0_9.json"

TIER0 = "TIER0_REPLAY_ELIGIBLE_NOW"
TIER1 = "TIER1_FORMULA_COMPLETION_SAFE_SELECTOR"
ENDPOINT_DATA_POLICY = (
    "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
)
CLAIM_BOUNDARY = "support_safe_formula_completion_manifest_not_endpoint_scoring"


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


def _positive(value: object) -> bool:
    number = _float(value)
    return number is not None and number > 0.0


def _component_formula(row: pd.Series) -> tuple[str, str, str, str]:
    component = str(row["top_component"])
    if component == "bar":
        required = ["rdisk_kpc_source", "bar_radius_kpc_source"]
        if all(_positive(row.get(field)) for field in required):
            return (
                "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_READY",
                "F_SUPPORT_SAFE_BAR_COMPONENT_SOURCE_FROZEN",
                ";".join(required),
                "bar_radius_and_disk_scale_positive",
            )
        return (
            "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_BLOCKED",
            "none",
            ";".join(required),
            "missing_positive_bar_radius_or_disk_scale",
        )
    if component == "ring":
        required = ["rdisk_kpc_source", "ring_radius_kpc_source"]
        if all(_positive(row.get(field)) for field in required):
            return (
                "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_READY",
                "F_SUPPORT_SAFE_RING_COMPONENT_SOURCE_FROZEN",
                ";".join(required),
                "ring_radius_and_disk_scale_positive",
            )
        return (
            "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_BLOCKED",
            "none",
            ";".join(required),
            "missing_positive_ring_radius_or_disk_scale",
        )
    if component == "spiral":
        required = [
            "rdisk_kpc_source",
            "spiral_inner_kpc_source",
            "spiral_outer_kpc_source",
        ]
        inner = _float(row.get("spiral_inner_kpc_source"))
        outer = _float(row.get("spiral_outer_kpc_source"))
        if (
            _positive(row.get("rdisk_kpc_source"))
            and inner is not None
            and outer is not None
            and outer > inner
            and inner > 0.0
        ):
            return (
                "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_READY",
                "F_SUPPORT_SAFE_SPIRAL_COMPONENT_SOURCE_FROZEN",
                ";".join(required),
                "spiral_support_window_and_disk_scale_positive",
            )
        return (
            "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_BLOCKED",
            "none",
            ";".join(required),
            "missing_positive_spiral_support_window_or_disk_scale",
        )
    return (
        "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_BLOCKED",
        "none",
        "top_component",
        "unsupported_or_missing_top_component",
    )


def _pool_role(row: pd.Series, completion_status: str) -> tuple[str, str]:
    tier = str(row["expansion_opportunity_tier"])
    if tier == TIER0:
        return (
            "SUPPORT_SAFE_10_POOL_READY_CARRIED_FROM_V0_7",
            "already_formula_ready_and_support_safe",
        )
    if tier == TIER1 and completion_status == "SUPPORT_SAFE_COMPONENT_ROUTE_FORMULA_READY":
        return (
            "SUPPORT_SAFE_10_POOL_READY_BY_COMPONENT_ROUTE_COMPLETION",
            "partial_family_formula_completed_by_support_safe_component_route",
        )
    if tier == TIER1:
        return (
            "SUPPORT_SAFE_10_POOL_BLOCKED_COMPONENT_ROUTE_INCOMPLETE",
            "support_safe_but_component_route_formula_incomplete",
        )
    return (
        "NOT_IN_SUPPORT_SAFE_10_POOL",
        "not_tier0_or_tier1_component_route_ready",
    )


def build_manifest() -> tuple[pd.DataFrame, dict[str, object]]:
    opportunity = pd.read_csv(OPPORTUNITY)
    support = pd.read_csv(
        SUPPORT_AUDIT,
        usecols=[
            "galaxy",
            "spiral_inner_kpc_source",
            "spiral_outer_kpc_source",
            "top_component_weight",
            "dominance_margin",
        ],
    )
    readiness = pd.read_csv(
        READINESS,
        usecols=[
            "galaxy",
            "compiled_formula_family_candidate",
            "available_formula_components",
            "missing_source_observables",
        ],
    )
    coordinates = pd.read_csv(
        COORDINATES,
        usecols=[
            "galaxy",
            "rdisk_kpc_source",
            "bar_radius_kpc_source",
            "ring_radius_kpc_source",
            "bar_strength_proxy",
            "ring_strength_proxy",
            "spiral_pitch_median_abs_deg_source",
        ],
    )
    data = (
        opportunity.merge(support, on="galaxy", how="left")
        .merge(readiness, on="galaxy", how="left")
        .merge(coordinates, on="galaxy", how="left")
    )

    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        completion_status, formula, required, reason = _component_formula(row)
        pool_role, pool_reason = _pool_role(row, completion_status)
        if row["expansion_opportunity_tier"] == TIER0:
            formula = str(row["compiled_formula_family_candidate"])
            required = "carried_from_v0_4_formula_readiness"
            reason = "carried_from_v0_7_support_safe_pool"
            completion_status = "SUPPORT_SAFE_COMPONENT_ROUTE_CARRIED_READY"
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "compiler_readiness_status_v0_4": row["compiler_readiness_status"],
                "expansion_opportunity_tier_v0_8": row["expansion_opportunity_tier"],
                "support_aware_selector_status": row["support_aware_selector_status"],
                "top_component": row["top_component"],
                "positive_components": row["positive_components"],
                "top_component_weight": row["top_component_weight"],
                "dominance_margin": row["dominance_margin"],
                "support_safe_formula_completion_status": completion_status,
                "support_safe_compiled_formula": formula,
                "support_safe_formula_required_observables": required,
                "support_safe_formula_completion_reason": reason,
                "support_safe_10_pool_role": pool_role,
                "support_safe_10_pool_reason": pool_reason,
                "rdisk_kpc_source": row["rdisk_kpc_source"],
                "bar_radius_kpc_source": row["bar_radius_kpc_source"],
                "ring_radius_kpc_source": row["ring_radius_kpc_source"],
                "spiral_inner_kpc_source": row["spiral_inner_kpc_source"],
                "spiral_outer_kpc_source": row["spiral_outer_kpc_source"],
                "spiral_pitch_median_abs_deg_source": row[
                    "spiral_pitch_median_abs_deg_source"
                ],
                "bar_strength_proxy": row["bar_strength_proxy"],
                "ring_strength_proxy": row["ring_strength_proxy"],
                "endpoint_data_policy": ENDPOINT_DATA_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    detail = pd.DataFrame(rows).sort_values(
        ["support_safe_10_pool_role", "pilot_role", "galaxy"]
    )
    pool = detail[
        detail["support_safe_10_pool_role"].isin(
            {
                "SUPPORT_SAFE_10_POOL_READY_CARRIED_FROM_V0_7",
                "SUPPORT_SAFE_10_POOL_READY_BY_COMPONENT_ROUTE_COMPLETION",
            }
        )
    ]
    completed = detail[
        detail["support_safe_10_pool_role"]
        == "SUPPORT_SAFE_10_POOL_READY_BY_COMPONENT_ROUTE_COMPLETION"
    ]
    summary = {
        "n_rows": int(len(detail)),
        "support_safe_10_pool_role_counts": detail[
            "support_safe_10_pool_role"
        ].value_counts().sort_index().to_dict(),
        "support_safe_10_pool_size": int(len(pool)),
        "support_safe_10_pool_galaxies": sorted(pool["galaxy"].tolist()),
        "component_route_completed_galaxies": sorted(completed["galaxy"].tolist()),
        "support_safe_10_pool_by_formula": pool[
            "support_safe_compiled_formula"
        ].value_counts().sort_index().to_dict(),
        "support_safe_10_pool_by_top_component": pool[
            "top_component"
        ].value_counts().sort_index().to_dict(),
        "endpoint_data_policy": ENDPOINT_DATA_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The three Tier-1 objects can enter a support-safe 10-object pool "
            "by using their source-dominant support-safe component route rather "
            "than forcing the broad family label. This is source-side formula "
            "completion only, not endpoint scoring."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_manifest()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
