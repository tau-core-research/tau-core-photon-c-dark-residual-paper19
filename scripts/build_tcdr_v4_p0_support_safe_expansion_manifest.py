from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

SUPPORT_AUDIT = OUT_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_support_safe_expansion_manifest_v0_7.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_support_safe_expansion_manifest_summary_v0_7.json"

READY = "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
SAFE_STATUSES = {
    "SUPPORT_AWARE_SELECTOR_SAFE_SINGLE_COMPONENT",
    "SUPPORT_AWARE_SELECTOR_SAFE_DOMINANT_DISJOINT",
}
ENDPOINT_DATA_POLICY = (
    "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
)
CLAIM_BOUNDARY = "support_safe_expansion_manifest_not_endpoint_scoring"


def _selector_expansion_role(row: pd.Series) -> tuple[str, str]:
    is_ready = row["compiler_readiness_status"] == READY
    is_safe = row["support_aware_selector_status"] in SAFE_STATUSES
    if is_ready and is_safe and row["pilot_role"] == "PILOT_HOLDOUT":
        return (
            "EXISTING_SUPPORT_SAFE_HOLDOUT",
            "already_in_pilot_holdout_and_support_safe",
        )
    if is_ready and is_safe and row["pilot_role"] == "PILOT_TRAIN_POOL":
        return (
            "SUPPORT_SAFE_HOLDOUT_EXPANSION_CANDIDATE",
            "formula_ready_train_pool_object_with_support_safe_selector",
        )
    if not is_ready:
        return (
            "NOT_EXPANSION_READY_FORMULA_COMPILER_NOT_READY",
            str(row["compiler_readiness_status"]),
        )
    if not is_safe:
        return (
            "NOT_EXPANSION_READY_SELECTOR_NOT_SUPPORT_SAFE",
            str(row["support_aware_selector_status"]),
        )
    return (
        "NOT_EXPANSION_READY_UNCLASSIFIED",
        "unexpected_role_or_status_combination",
    )


def build_manifest() -> tuple[pd.DataFrame, dict[str, object]]:
    data = pd.read_csv(SUPPORT_AUDIT)
    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        expansion_role, expansion_reason = _selector_expansion_role(row)
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "compiler_readiness_status": row["compiler_readiness_status"],
                "support_aware_selector_status": row["support_aware_selector_status"],
                "support_aware_selector_reason": row["support_aware_selector_reason"],
                "selector_expansion_role": expansion_role,
                "selector_expansion_reason": expansion_reason,
                "top_component": row["top_component"],
                "positive_components": row["positive_components"],
                "top_component_weight": row["top_component_weight"],
                "dominance_margin": row["dominance_margin"],
                "bar_component_weight": row["bar_component_weight"],
                "ring_component_weight": row["ring_component_weight"],
                "spiral_component_weight": row["spiral_component_weight"],
                "bar_radius_kpc_source": row["bar_radius_kpc_source"],
                "ring_radius_kpc_source": row["ring_radius_kpc_source"],
                "spiral_inner_kpc_source": row["spiral_inner_kpc_source"],
                "spiral_outer_kpc_source": row["spiral_outer_kpc_source"],
                "support_overlap_reasons": row["support_overlap_reasons"],
                "missing_support_reasons": row["missing_support_reasons"],
                "endpoint_data_policy": ENDPOINT_DATA_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    detail = pd.DataFrame(rows).sort_values(
        ["selector_expansion_role", "pilot_role", "galaxy"]
    )

    candidates = detail[
        detail["selector_expansion_role"].isin(
            {
                "EXISTING_SUPPORT_SAFE_HOLDOUT",
                "SUPPORT_SAFE_HOLDOUT_EXPANSION_CANDIDATE",
            }
        )
    ]
    expansion_candidates = detail[
        detail["selector_expansion_role"]
        == "SUPPORT_SAFE_HOLDOUT_EXPANSION_CANDIDATE"
    ]
    summary = {
        "n_rows": int(len(detail)),
        "selector_expansion_role_counts": detail[
            "selector_expansion_role"
        ].value_counts().sort_index().to_dict(),
        "support_safe_replay_pool_size": int(len(candidates)),
        "support_safe_expansion_candidate_count": int(len(expansion_candidates)),
        "support_safe_replay_pool_galaxies": sorted(candidates["galaxy"].tolist()),
        "support_safe_expansion_candidate_galaxies": sorted(
            expansion_candidates["galaxy"].tolist()
        ),
        "support_safe_replay_pool_by_family": candidates[
            "source_family_candidate"
        ].value_counts().sort_index().to_dict(),
        "support_safe_replay_pool_by_top_component": candidates[
            "top_component"
        ].value_counts().sort_index().to_dict(),
        "endpoint_data_policy": ENDPOINT_DATA_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "This source-side manifest expands the future replay pool only to "
            "formula-ready objects whose component selector is support-safe. "
            "It is not an endpoint score and does not use rotation residuals."
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
