from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

FAILURE_LEDGER = EXTERNAL_DIR / "tcdr_v4_support_safe_pool_loocv_failure_ledger_local.csv"
FORMULA_AWARE = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_summary_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_failure_overlay_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_failure_overlay_summary_local.json"

NEAR_TIE_KMS = 0.10


def _components(value: object) -> set[str]:
    if pd.isna(value):
        return set()
    return {
        part.strip()
        for part in str(value).split(";")
        if part.strip() and part.strip() != "none"
    }


def _classify(row: pd.Series) -> dict[str, str]:
    margin = float(row["formula_aware_best_wrong_minus_candidate_weighted_rmse_kms"])
    original = str(row["failure_class"])
    best_wrong = str(row["best_wrong_component"])
    matched = str(row["matched_component"])
    family = str(row["source_family_candidate"])
    positives = _components(row["positive_components"])

    if margin > 0:
        return {
            "paper8_paper9_overlay_class": "STRICT_CONTROL_SURVIVED",
            "route_permission": "no_repair_needed_for_this_control",
            "required_next_step": "retain_as_positive_strict_control_survival_row",
            "reason": "Formula-aware candidate beats the best wrong component.",
        }
    if abs(margin) <= NEAR_TIE_KMS:
        return {
            "paper8_paper9_overlay_class": "NEAR_TIE_NOT_MATERIAL_FAILURE",
            "route_permission": "no_kernel_change_allowed_from_tie",
            "required_next_step": "report_as_numerically_near_tie_and_retest_with_error_weighting",
            "reason": f"Best-wrong margin is within {NEAR_TIE_KMS} km/s.",
        }
    if best_wrong in positives:
        return {
            "paper8_paper9_overlay_class": "PAPER8_SOURCE_VISIBLE_SECONDARY_COMPONENT",
            "route_permission": "provisional_mixed_route_allowed_after_nonoverlap_and_shuffle_controls",
            "required_next_step": (
                "apply Paper8 mixed-readout rule: freeze secondary support, "
                "check non-overlap, then rerun shuffled-component controls"
            ),
            "reason": "The best wrong component is present in the residual-blind source component ledger.",
        }
    if best_wrong == "spiral" and "EXPONENTIAL" in family:
        return {
            "paper8_paper9_overlay_class": "PAPER8_KOBS_KREADOUT_BROAD_DISK_MISMATCH",
            "route_permission": "candidate_kreadout_relabel_review_allowed_source_side_only",
            "required_next_step": (
                "review K_obs versus K_readout using source morphology; "
                "do not use endpoint score to promote spiral"
            ),
            "reason": "The broad source family is disk/spiral even though the selected top component is different.",
        }
    if best_wrong == "ring" and "RING" in family:
        return {
            "paper8_paper9_overlay_class": "PAPER8_KOBS_KREADOUT_RING_MISMATCH",
            "route_permission": "candidate_kreadout_relabel_review_allowed_source_side_only",
            "required_next_step": (
                "review ring route from source support; do not use endpoint score "
                "as the selector"
            ),
            "reason": "The broad source family is ring/resonance while the selected top component is different.",
        }
    if best_wrong == "spiral" and matched == "bar":
        return {
            "paper8_paper9_overlay_class": "PAPER9_PROJECTION_OR_DISK_SUPPORT_SOURCE_GAP",
            "route_permission": "blocked_until_independent_spiral_projection_history_source_exists",
            "required_next_step": (
                "seek residual-blind spiral/disk/projection/history source tokens; "
                "if none exist, retain as competitive false-component control"
            ),
            "reason": "Spiral wins against a bar-selected candidate without current source-visible spiral support.",
        }

    return {
        "paper8_paper9_overlay_class": "TRUE_COMPETITIVE_FALSE_COMPONENT_CANDIDATE",
        "route_permission": "blocked_no_repair_without_new_source_evidence",
        "required_next_step": "retain as strict-control blocker unless independent source support is acquired",
        "reason": f"Best wrong component {best_wrong} is neither source-visible nor explained by broad-family mismatch.",
    }


def build_overlay() -> tuple[pd.DataFrame, dict[str, object]]:
    failure = pd.read_csv(FAILURE_LEDGER)
    formula = pd.read_csv(FORMULA_AWARE)[
        [
            "support_safe_pool",
            "galaxy",
            "candidate_weighted_rmse_kms",
            "best_wrong_component",
            "best_wrong_component_weighted_rmse_kms",
            "best_wrong_minus_candidate_weighted_rmse_kms",
            "wrong_mean_minus_candidate_weighted_rmse_kms",
            "candidate_beats_baryonic",
            "candidate_beats_wrong_component_mean",
            "candidate_beats_best_wrong_component",
        ]
    ].rename(
        columns={
            "candidate_weighted_rmse_kms": "formula_aware_candidate_weighted_rmse_kms",
            "best_wrong_component": "formula_aware_best_wrong_component",
            "best_wrong_component_weighted_rmse_kms": "formula_aware_best_wrong_component_weighted_rmse_kms",
            "best_wrong_minus_candidate_weighted_rmse_kms": "formula_aware_best_wrong_minus_candidate_weighted_rmse_kms",
            "wrong_mean_minus_candidate_weighted_rmse_kms": "formula_aware_wrong_mean_minus_candidate_weighted_rmse_kms",
            "candidate_beats_baryonic": "formula_aware_candidate_beats_baryonic",
            "candidate_beats_wrong_component_mean": "formula_aware_candidate_beats_wrong_component_mean",
            "candidate_beats_best_wrong_component": "formula_aware_candidate_beats_best_wrong_component",
        }
    )
    overlay = failure.merge(formula, on=["support_safe_pool", "galaxy"], how="left")

    # Prefer formula-aware best-wrong identity for the overlay. If it differs
    # from the earlier top-component failure ledger, record that explicitly.
    overlay["top_component_best_wrong_component"] = overlay["best_wrong_component"]
    overlay["best_wrong_component"] = overlay["formula_aware_best_wrong_component"]
    overlay["best_wrong_component_changed_under_formula_awareness"] = (
        overlay["top_component_best_wrong_component"] != overlay["formula_aware_best_wrong_component"]
    ).map({True: "yes", False: "no"})

    classified = overlay.apply(_classify, axis=1, result_type="expand")
    overlay = pd.concat([overlay, classified], axis=1)
    overlay["paper8_import"] = "K_obs_not_equal_K_readout_and_wrong_family_can_be_secondary_or_review_signal"
    overlay["paper9_import"] = "projection_or_time_channel_requires_residual_blind_nonoverlap_source_token"
    overlay["claim_boundary"] = "paper8_paper9_overlay_local_interpretive_diagnostic_not_kernel_selector"

    summary = {
        "n_rows": int(len(overlay)),
        "overlay_class_counts": overlay["paper8_paper9_overlay_class"].value_counts().to_dict(),
        "route_permission_counts": overlay["route_permission"].value_counts().to_dict(),
        "best_wrong_changed_under_formula_awareness": overlay[
            "best_wrong_component_changed_under_formula_awareness"
        ].value_counts().to_dict(),
        "near_tie_kms": NEAR_TIE_KMS,
        "paper8_import": "K_obs may differ from K_readout; wrong-family can be a source-visible secondary component or a subfamily-review signal.",
        "paper9_import": "Projection/history/time routes require residual-blind source-token non-overlap before endpoint use.",
        "claim_boundary": "paper8_paper9_overlay_local_interpretive_diagnostic_not_kernel_selector",
    }
    return overlay.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    overlay, summary = build_overlay()
    overlay.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "matched_component",
        "positive_components",
        "source_family_candidate",
        "support_safe_compiled_formula",
        "best_wrong_component",
        "formula_aware_best_wrong_minus_candidate_weighted_rmse_kms",
        "paper8_paper9_overlay_class",
        "route_permission",
    ]
    print(overlay[cols].to_string(index=False))


if __name__ == "__main__":
    main()
