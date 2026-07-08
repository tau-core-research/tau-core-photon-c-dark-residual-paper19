from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

SOURCE_SEARCH = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_source_search_v0_1.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_outer_capacity_formula_freeze_worklist_not_formula_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


WORKLIST_ROWS = [
    {
        "galaxy": "NGC2841",
        "requested_field": "outer_capacity_onset_kpc",
        "field_role": "outer_capacity_ramp_start",
        "source_status": "candidate_numeric_source_available",
        "source_value": "20",
        "source_value_type": "approximate_lower_onset_kpc",
        "source_reference": "Zhang2018NGC2841Dragonfly",
        "why_needed": (
            "Dragonfly reports the outer stellar/gas surface-density ratio as stable "
            "beyond about 20 kpc; this is a plausible start for an outer-capacity route."
        ),
        "formula_freeze_status": "not_frozen_needs_onset_priority_rule",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "outer_warp_onset_kpc",
        "field_role": "outer_warp_path_tail_start",
        "source_status": "candidate_numeric_source_available",
        "source_value": "30",
        "source_value_type": "approximate_warp_onset_kpc",
        "source_reference": "Zhang2018NGC2841Dragonfly",
        "why_needed": (
            "The low-surface-brightness outer stellar disk begins to warp beyond about "
            "30 kpc; this is a plausible start for a path/warp tail."
        ),
        "formula_freeze_status": "not_frozen_needs_onset_priority_rule",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "outer_capacity_extent_kpc",
        "field_role": "outer_capacity_support_extent",
        "source_status": "candidate_numeric_source_available",
        "source_value": "70",
        "source_value_type": "approximate_outer_extent_kpc",
        "source_reference": "Zhang2018NGC2841Dragonfly",
        "why_needed": "Sets the outer support scale for a future extended outer-disk capacity kernel.",
        "formula_freeze_status": "candidate_freezable_after_review",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "hi_extent_factor_holmberg",
        "field_role": "outer_hi_support_extent_proxy",
        "source_status": "candidate_numeric_source_available",
        "source_value": "2.5",
        "source_value_type": "approximate_hi_extent_in_holmberg_diameters",
        "source_reference": "Bosma1981NGC2841HI",
        "why_needed": "Provides an independent HI support proxy for the same outer-capacity route.",
        "formula_freeze_status": "candidate_freezable_after_review",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "xuv_extent_factor_d25",
        "field_role": "outer_xuv_support_extent_proxy",
        "source_status": "lower_bound_source_available",
        "source_value": ">=4",
        "source_value_type": "lower_bound_xuv_extent_in_D25",
        "source_reference": "Thilker2007XUVDisks",
        "why_needed": (
            "Records that the outer-disk route is also UV/HI active outside the optical "
            "disk; lower-bound values must not be treated as exact fit radii."
        ),
        "formula_freeze_status": "not_frozen_lower_bound_requires_policy",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "tilted_ring_geometry_profile",
        "field_role": "outer_hi_warp_shape",
        "source_status": "qualitative_or_tabulated_source_required",
        "source_value": "pending",
        "source_value_type": "tilted_ring_PA_inclination_or_warp_profile",
        "source_reference": "Bosma1981NGC2841HI",
        "why_needed": (
            "A geometry-bearing kernel should use source-native outer-ring orientation "
            "rather than a residual-driven radial shape."
        ),
        "formula_freeze_status": "blocked_needs_source_native_geometry_extraction",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "outer_component_weight_rule",
        "field_role": "stellar_hi_uv_vs_hi_warp_vs_xuv_weighting",
        "source_status": "not_yet_defined",
        "source_value": "pending",
        "source_value_type": "residual_blind_weight_rule",
        "source_reference": "Zhang2018NGC2841Dragonfly;Bosma1981NGC2841HI;Thilker2007XUVDisks",
        "why_needed": (
            "The three strong source routes must not be combined by endpoint residual. "
            "A source-side weighting rule is required before formula freeze."
        ),
        "formula_freeze_status": "blocked_needs_residual_blind_component_weight_rule",
    },
    {
        "galaxy": "NGC2841",
        "requested_field": "vertical_or_hot_gas_path_flags",
        "field_role": "caveated_path_context_only",
        "source_status": "caveated_context_available",
        "source_value": "radio_hourglass;hot_gas_halo",
        "source_value_type": "non_primary_context_flags",
        "source_reference": "Braun2007WesterborkSINGS;Chandra2006NGC2841",
        "why_needed": (
            "Keeps vertical/path context visible while preventing it from being silently "
            "used as an amplitude-rescue parameter."
        ),
        "formula_freeze_status": "context_only_not_formula_freeze_field",
    },
]


def build_worklist() -> tuple[pd.DataFrame, dict[str, object]]:
    source_search = pd.read_csv(SOURCE_SEARCH)
    strong_routes = sorted(
        source_search[source_search["source_status"].str.startswith("STRONG")]["source_route"].tolist()
    )
    rows = []
    for row in WORKLIST_ROWS:
        rows.append(
            {
                **row,
                "candidate_formula_family": (
                    "F_NGC2841_OUTER_CAPACITY_COMPOSITE_SOURCE_SIDE_WORKLIST"
                ),
                "formula_shell_sketch": (
                    "K_outer(R)=w_ext*K_ext(R;20,70)+w_warp*K_warp(R;30,70)+"
                    "w_xuv*K_xuv(R;>=4D25), with weights and exact geometry still source-blocked"
                ),
                "forbidden_inputs": "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;required_epsilon_fit",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    frame = pd.DataFrame(rows)
    status_counts = frame["formula_freeze_status"].value_counts().to_dict()
    formula_ready = all(
        not status.startswith("blocked") and not status.startswith("not_frozen")
        for status in frame["formula_freeze_status"]
    )
    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "strong_source_routes_inherited": strong_routes,
        "formula_freeze_status_counts": status_counts,
        "candidate_numeric_or_lower_bound_fields": int(
            frame["source_status"].isin(
                ["candidate_numeric_source_available", "lower_bound_source_available"]
            ).sum()
        ),
        "blocked_formula_fields": int(frame["formula_freeze_status"].str.startswith("blocked").sum()),
        "not_frozen_formula_fields": int(frame["formula_freeze_status"].str.startswith("not_frozen").sum()),
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().to_dict(),
        "formula_ready": bool(formula_ready),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The NGC2841 outer-capacity route is source-supported but not formula-frozen. "
            "Several source-native scales are available, but the route is blocked by the "
            "outer onset priority rule, source-native tilted-ring geometry extraction, "
            "and a residual-blind component-weight rule. Endpoint replay remains closed."
        ),
        "next_allowed_action": (
            "derive a source-side onset/weight policy and extract tilted-ring geometry "
            "before any outer-capacity kernel scoring"
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_worklist()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "requested_field",
                "source_status",
                "source_value",
                "formula_freeze_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
