from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

OVERLAY = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_failure_overlay_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_readiness_ledger_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_readiness_ledger_summary_local.json"

CLAIM_BOUNDARY = (
    "paper8_paper9_scoring_readiness_local_diagnostic_not_endpoint_validation"
)


def _readiness(row: pd.Series) -> dict[str, str]:
    permission = str(row["route_permission"])
    overlay_class = str(row["paper8_paper9_overlay_class"])

    if permission == "no_repair_needed_for_this_control":
        return {
            "scoring_readiness_class": "READY_CURRENT_FORMULA_STRICT_SURVIVAL",
            "next_scoring_action": "include_current_formula_in_confirmatory_or_error_weighted_replay",
            "new_kernel_allowed_now": "no",
            "endpoint_replay_allowed_now": "yes_current_formula_only",
            "source_work_required_before_replay": "no",
            "reason": "Candidate already beats best wrong component under the frozen formula-aware replay.",
        }
    if permission == "no_kernel_change_allowed_from_tie":
        return {
            "scoring_readiness_class": "READY_CURRENT_FORMULA_NEAR_TIE_ROBUSTNESS_ONLY",
            "next_scoring_action": "rerun_same_formula_with_error_weighting_or_stability_checks",
            "new_kernel_allowed_now": "no",
            "endpoint_replay_allowed_now": "yes_current_formula_robustness_only",
            "source_work_required_before_replay": "no",
            "reason": "Best-wrong margin is too small to justify a morphology repair.",
        }
    if permission == "provisional_mixed_route_allowed_after_nonoverlap_and_shuffle_controls":
        return {
            "scoring_readiness_class": "NOT_READY_MIXED_ROUTE_REQUIRES_NONOVERLAP",
            "next_scoring_action": "freeze_secondary_component_support_then_run_nonoverlap_and_shuffle_controls",
            "new_kernel_allowed_now": "no",
            "endpoint_replay_allowed_now": "no",
            "source_work_required_before_replay": "yes_nonoverlap_and_shuffle_controls",
            "reason": "A source-visible secondary component exists, but Paper9 forbids replay until non-overlap and shuffle controls are frozen.",
        }
    if permission == "candidate_kreadout_relabel_review_allowed_source_side_only":
        return {
            "scoring_readiness_class": "NOT_READY_KOBS_KREADOUT_REVIEW_REQUIRED",
            "next_scoring_action": "perform_source_side_kobs_kreadout_review_before_any_relabel_replay",
            "new_kernel_allowed_now": "no",
            "endpoint_replay_allowed_now": "no",
            "source_work_required_before_replay": "yes_kobs_kreadout_review",
            "reason": "The overlay permits source-side review only; endpoint score cannot promote a relabel.",
        }
    if permission == "blocked_until_independent_spiral_projection_history_source_exists":
        return {
            "scoring_readiness_class": "BLOCKED_SOURCE_GAP",
            "next_scoring_action": "seek_independent_spiral_projection_history_source_or_keep_as_false_component_control",
            "new_kernel_allowed_now": "no",
            "endpoint_replay_allowed_now": "no",
            "source_work_required_before_replay": "yes_independent_projection_or_history_source",
            "reason": "The best wrong component lacks current independent source support.",
        }

    return {
        "scoring_readiness_class": "BLOCKED_UNCLASSIFIED_STRICT_CONTROL",
        "next_scoring_action": "retain_as_strict_control_blocker_until_new_source_evidence_exists",
        "new_kernel_allowed_now": "no",
        "endpoint_replay_allowed_now": "no",
        "source_work_required_before_replay": "yes_independent_source_evidence",
        "reason": f"No scoring permission defined for overlay class {overlay_class}.",
    }


def build_readiness() -> tuple[pd.DataFrame, dict[str, object]]:
    overlay = pd.read_csv(OVERLAY)
    readiness = overlay.apply(_readiness, axis=1, result_type="expand")
    ledger = pd.concat([overlay, readiness], axis=1)
    ledger["claim_boundary"] = CLAIM_BOUNDARY

    score_ready = ledger[
        ledger["endpoint_replay_allowed_now"].isin(
            {
                "yes_current_formula_only",
                "yes_current_formula_robustness_only",
            }
        )
    ]
    blocked = ledger[ledger["endpoint_replay_allowed_now"] == "no"]

    summary = {
        "n_rows": int(len(ledger)),
        "scoring_readiness_class_counts": ledger[
            "scoring_readiness_class"
        ].value_counts().to_dict(),
        "endpoint_replay_allowed_now_counts": ledger[
            "endpoint_replay_allowed_now"
        ].value_counts().to_dict(),
        "source_work_required_before_replay_counts": ledger[
            "source_work_required_before_replay"
        ].value_counts().to_dict(),
        "current_formula_replay_rows": int(len(score_ready)),
        "blocked_or_review_rows": int(len(blocked)),
        "current_formula_replay_galaxies": sorted(score_ready["galaxy"].unique().tolist()),
        "blocked_or_review_galaxies": sorted(blocked["galaxy"].unique().tolist()),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The next scoring step is current-formula robustness replay for strict "
            "survivals and near ties only. Mixed, K_obs/K_readout, and projection/history "
            "routes are not endpoint-replay-ready until their source-side conditions close."
        ),
    }
    return ledger.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    ledger, summary = build_readiness()
    ledger.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "paper8_paper9_overlay_class",
        "scoring_readiness_class",
        "endpoint_replay_allowed_now",
        "next_scoring_action",
    ]
    print(ledger[cols].to_string(index=False))


if __name__ == "__main__":
    main()
