from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

WORKLIST = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_v0_1.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_policy_freeze_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_policy_freeze_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_outer_capacity_policy_freeze_not_formula_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


def _source_value(worklist: pd.DataFrame, field: str) -> str:
    row = worklist[worklist["requested_field"] == field]
    if row.empty:
        raise ValueError(f"Missing worklist field: {field}")
    return str(row.iloc[0]["source_value"])


def build_policy() -> tuple[pd.DataFrame, dict[str, object]]:
    worklist = pd.read_csv(WORKLIST)
    r_capacity_onset = _source_value(worklist, "outer_capacity_onset_kpc")
    r_warp_onset = _source_value(worklist, "outer_warp_onset_kpc")
    r_extent = _source_value(worklist, "outer_capacity_extent_kpc")
    hi_extent = _source_value(worklist, "hi_extent_factor_holmberg")
    xuv_extent = _source_value(worklist, "xuv_extent_factor_d25")

    rows = [
        {
            "galaxy": "NGC2841",
            "policy_id": "P_NGC2841_NESTED_OUTER_ONSET_V0_1",
            "policy_type": "onset_priority_rule",
            "policy_status": "frozen_source_side_policy",
            "policy_statement": (
                "Use the 20 kpc Dragonfly outer stellar/gas stability scale as the "
                "general outer-capacity ramp onset, and use the 30 kpc Dragonfly warp "
                "scale only as the nested warp/path subchannel onset."
            ),
            "frozen_policy_values": (
                f"R_capacity_on_kpc={r_capacity_onset};R_warp_on_kpc={r_warp_onset};"
                f"R_outer_extent_kpc={r_extent}"
            ),
            "source_references": "Zhang2018NGC2841Dragonfly",
            "residual_blind_reason": (
                "The two onsets are assigned to different source roles instead of being "
                "chosen by curve residuals."
            ),
            "formula_use_permission": "yes_policy_only_no_scoring",
        },
        {
            "galaxy": "NGC2841",
            "policy_id": "P_NGC2841_MAX_ENTROPY_STRONG_ROUTE_WEIGHTS_V0_1",
            "policy_type": "component_weight_rule",
            "policy_status": "frozen_source_side_policy",
            "policy_statement": (
                "If several strong residual-blind source routes are present and no "
                "source-native evidence ranks them, assign equal prior weights to the "
                "strong routes and zero primary weight to caveated context rows."
            ),
            "frozen_policy_values": (
                "w_stellar_hi_uv=1/3;w_hi_warp=1/3;w_xuv_hi=1/3;"
                "w_caveated_vertical_or_hot_gas=0_primary_context_only"
            ),
            "source_references": (
                "Zhang2018NGC2841Dragonfly;Bosma1981NGC2841HI;Thilker2007XUVDisks"
            ),
            "residual_blind_reason": (
                "This is a maximum-ignorance/source-symmetry prior over equally strong "
                "source-supported routes, not an endpoint amplitude fit."
            ),
            "formula_use_permission": "yes_policy_only_no_scoring",
        },
        {
            "galaxy": "NGC2841",
            "policy_id": "P_NGC2841_XUV_LOWER_BOUND_USE_V0_1",
            "policy_type": "lower_bound_use_rule",
            "policy_status": "frozen_source_side_policy_with_shape_blocker",
            "policy_statement": (
                "Use the XUV >=4D25 source as evidence that the XUV/HI outer route is "
                "active; do not use the lower bound as an exact radial cutoff or decay "
                "scale until a source-native XUV profile is extracted."
            ),
            "frozen_policy_values": f"xuv_support_lower_bound={xuv_extent};exact_xuv_shape=pending",
            "source_references": "Thilker2007XUVDisks",
            "residual_blind_reason": (
                "Lower bounds can establish source support but cannot be silently "
                "converted into tuned radial shape parameters."
            ),
            "formula_use_permission": "support_flag_only_shape_blocked",
        },
        {
            "galaxy": "NGC2841",
            "policy_id": "P_NGC2841_HI_EXTENT_CONTEXT_V0_1",
            "policy_type": "hi_extent_use_rule",
            "policy_status": "frozen_source_side_policy_with_geometry_blocker",
            "policy_statement": (
                "Use the 2.5-Holmberg HI extent as independent outer-support evidence; "
                "do not replace the tilted-ring geometry profile with this scalar."
            ),
            "frozen_policy_values": f"HI_extent_factor_Holmberg={hi_extent};tilted_ring_profile=pending",
            "source_references": "Bosma1981NGC2841HI",
            "residual_blind_reason": (
                "The scalar HI extent constrains support but does not determine the "
                "orientation profile needed for a geometry-bearing path kernel."
            ),
            "formula_use_permission": "support_flag_only_geometry_blocked",
        },
    ]

    frame = pd.DataFrame(rows)
    frame["forbidden_inputs"] = (
        "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;required_epsilon_fit"
    )
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "policy_status_counts": frame["policy_status"].value_counts().to_dict(),
        "onset_priority_blocker_closed": True,
        "component_weight_blocker_closed": True,
        "xuv_exact_shape_blocker_closed": False,
        "tilted_ring_geometry_blocker_closed": False,
        "formula_ready": False,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The NGC2841 outer-capacity branch now has a residual-blind onset policy "
            "and a residual-blind equal-strong-route component-weight policy. It remains "
            "not formula-ready because the exact XUV radial shape and the source-native "
            "tilted-ring geometry profile are still blocked."
        ),
        "next_allowed_action": (
            "extract or source-review a tilted-ring geometry profile and, separately, an "
            "XUV/HI radial-shape policy before any endpoint replay"
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_policy()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(frame[["policy_id", "policy_status", "formula_use_permission"]].to_string(index=False))


if __name__ == "__main__":
    main()
