from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

SUPPORT_AUDIT = OUT_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"
EXPANSION = OUT_DIR / "tcdr_v4_p0_support_safe_expansion_manifest_v0_7.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_support_safe_expansion_opportunity_ledger_v0_8.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_support_safe_expansion_opportunity_ledger_summary_v0_8.json"

READY = "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
PARTIAL = "PARTIAL_FORMULA_COMPILER_CANDIDATE"
UNCOVERED = "SUPPORT_AWARE_SELECTOR_UNCOVERED"
OVERLAP = "SUPPORT_AWARE_SELECTOR_UNRESOLVED_OVERLAPPING_SUPPORT"
SAFE_STATUSES = {
    "SUPPORT_AWARE_SELECTOR_SAFE_SINGLE_COMPONENT",
    "SUPPORT_AWARE_SELECTOR_SAFE_DOMINANT_DISJOINT",
}
TIER0_ROLES = {
    "EXISTING_SUPPORT_SAFE_HOLDOUT",
    "SUPPORT_SAFE_HOLDOUT_EXPANSION_CANDIDATE",
}
ENDPOINT_DATA_POLICY = (
    "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
)
CLAIM_BOUNDARY = "support_safe_expansion_opportunity_ledger_not_endpoint_scoring"


def _tier(row: pd.Series) -> tuple[str, str, str]:
    if row["selector_expansion_role"] in TIER0_ROLES:
        return (
            "TIER0_REPLAY_ELIGIBLE_NOW",
            "already_formula_ready_and_support_safe",
            "may_enter_support_safe_replay_pool_without_endpoint_label_rescue",
        )
    if (
        row["compiler_readiness_status"] == PARTIAL
        and row["support_aware_selector_status"] in SAFE_STATUSES
    ):
        return (
            "TIER1_FORMULA_COMPLETION_SAFE_SELECTOR",
            "selector_is_support_safe_but_formula_compiler_is_partial",
            "complete_source_frozen_formula_terms_before_replay_pool_admission",
        )
    if (
        row["compiler_readiness_status"] == READY
        and row["support_aware_selector_status"] == OVERLAP
    ):
        return (
            "TIER2_SUPPORT_OVERLAP_REVIEW_READY_FORMULA",
            "formula_ready_but_bar_ring_spiral_supports_overlap_or_are_adjacent",
            "obtain_or_freeze_independent_support_windows_or_keep_blocked",
        )
    if (
        row["compiler_readiness_status"] == READY
        and row["support_aware_selector_status"] == UNCOVERED
    ):
        return (
            "TIER3_COMPONENT_SOURCE_ACQUISITION_READY_FORMULA",
            "formula_ready_but_no_bar_ring_spiral_source_native_component",
            "add_a_residual_blind_disk_or_other_component_support_rule_before_replay_pool_admission",
        )
    return (
        "TIER4_NOT_NEAR_TERM_EXPANSION_READY",
        "neither_formula_ready_support_safe_nor_a_bounded_near_term_rescue_case",
        "do_not_expand_without_new_source_data_or_new_formula_compiler_work",
    )


def build_ledger() -> tuple[pd.DataFrame, dict[str, object]]:
    support = pd.read_csv(SUPPORT_AUDIT)
    expansion = pd.read_csv(
        EXPANSION,
        usecols=[
            "galaxy",
            "selector_expansion_role",
            "selector_expansion_reason",
        ],
    )
    data = support.merge(expansion, on="galaxy", how="left")
    data["selector_expansion_role"] = data["selector_expansion_role"].fillna(
        "NOT_IN_V0_7_EXPANSION_MANIFEST"
    )
    data["selector_expansion_reason"] = data["selector_expansion_reason"].fillna(
        "not_classified_by_v0_7"
    )
    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        tier, reason, required_action = _tier(row)
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "compiler_readiness_status": row["compiler_readiness_status"],
                "support_aware_selector_status": row["support_aware_selector_status"],
                "support_aware_selector_reason": row["support_aware_selector_reason"],
                "selector_expansion_role_v0_7": row["selector_expansion_role"],
                "expansion_opportunity_tier": tier,
                "expansion_opportunity_reason": reason,
                "required_source_side_action": required_action,
                "top_component": row["top_component"],
                "positive_components": row["positive_components"],
                "source_composition_uniqueness_status": row[
                    "source_composition_uniqueness_status"
                ],
                "support_overlap_reasons": row["support_overlap_reasons"],
                "missing_support_reasons": row["missing_support_reasons"],
                "endpoint_data_policy": ENDPOINT_DATA_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    detail = pd.DataFrame(rows).sort_values(
        ["expansion_opportunity_tier", "pilot_role", "galaxy"]
    )

    tier_counts = detail["expansion_opportunity_tier"].value_counts().sort_index()
    tier_galaxies = {
        tier: sorted(group["galaxy"].tolist())
        for tier, group in detail.groupby("expansion_opportunity_tier")
    }
    summary = {
        "n_rows": int(len(detail)),
        "expansion_opportunity_tier_counts": tier_counts.to_dict(),
        "tier_galaxies": tier_galaxies,
        "near_term_expandable_count_if_tier1_formula_completed": int(
            tier_counts.get("TIER0_REPLAY_ELIGIBLE_NOW", 0)
            + tier_counts.get("TIER1_FORMULA_COMPLETION_SAFE_SELECTOR", 0)
        ),
        "near_term_review_queue_count_tier2_tier3": int(
            tier_counts.get("TIER2_SUPPORT_OVERLAP_REVIEW_READY_FORMULA", 0)
            + tier_counts.get("TIER3_COMPONENT_SOURCE_ACQUISITION_READY_FORMULA", 0)
        ),
        "endpoint_data_policy": ENDPOINT_DATA_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The current support-safe replay pool can be expanded immediately "
            "only to the 7 Tier-0 objects. A bounded next expansion to 10 is "
            "possible if the 3 Tier-1 support-safe partial-formula objects get "
            "source-frozen formula completion. Tier-2 and Tier-3 objects need "
            "independent source-support review or a disk/component source rule "
            "before replay admission."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_ledger()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
