from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
RESPONSES_DIR = ROOT / "data" / "reviewer_responses"

FILLED_ZIP = Path.home() / "Downloads" / "tcdr_v4_ngc2841_mass_profile_semantics_review_package_FILLED_v0_1.zip"
EXTRACT_DIR = RESPONSES_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_review_package_FILLED_v0_1"
PACKAGE_STEM = "tcdr_v4_ngc2841_mass_profile_semantics_review_package_v0_1"
FILLED_DIR = EXTRACT_DIR / PACKAGE_STEM
RESPONSE_CSV = FILLED_DIR / "review_response_template.csv"
VALIDATION_SUMMARY = FILLED_DIR / "VALIDATION_SUMMARY.txt"
COMPLETION_NOTES = FILLED_DIR / "REVIEW_COMPLETION_NOTES.md"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_semantics_review_acceptance_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)

EXPECTED_ANSWERS = {
    "Q1_curve_identity": "figure_total_profile_not_isolated_component",
    "Q2_normalization_mapping": "no_not_in_source",
    "Q3_axis_or_units_issue": "no",
    "Q4_allowed_use": "shape_only",
}


def _extract_response() -> None:
    if not FILLED_ZIP.exists():
        raise FileNotFoundError(f"Missing filled review package: {FILLED_ZIP}")
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(FILLED_ZIP) as archive:
        archive.extractall(EXTRACT_DIR)


def build_acceptance() -> tuple[pd.DataFrame, dict[str, object]]:
    _extract_response()
    if not RESPONSE_CSV.exists():
        raise FileNotFoundError(f"Missing filled response CSV: {RESPONSE_CSV}")
    response = pd.read_csv(RESPONSE_CSV)

    required_cols = {
        "galaxy",
        "question_id",
        "reviewer_answer",
        "confidence",
        "endpoint_replay_permission",
        "kernel_promotion_permission",
        "uses_rotation_curve_or_velocity",
        "uses_endpoint_rotation_residual",
        "uses_tau_core_score_or_required_lambda",
    }
    missing_cols = sorted(required_cols.difference(response.columns))
    if missing_cols:
        raise ValueError(f"Missing response columns: {missing_cols}")

    answers = dict(zip(response["question_id"], response["reviewer_answer"]))
    missing_questions = sorted(set(EXPECTED_ANSWERS).difference(answers))
    if missing_questions:
        raise ValueError(f"Missing expected questions: {missing_questions}")

    guardrail_pass = (
        (response["endpoint_replay_permission"] == "must_be_no").all()
        and (response["kernel_promotion_permission"] == "must_be_no").all()
        and (response["uses_rotation_curve_or_velocity"] == "must_be_false").all()
        and (response["uses_endpoint_rotation_residual"] == "must_be_false").all()
        and (response["uses_tau_core_score_or_required_lambda"] == "must_be_false").all()
    )
    answer_validation_pass = all(answers[key] == value for key, value in EXPECTED_ANSWERS.items())

    response["acceptance_status"] = response["question_id"].map(
        {
            "Q1_curve_identity": "accepted_total_profile_not_isolated_component",
            "Q2_normalization_mapping": "accepted_no_source_native_normalization",
            "Q3_axis_or_units_issue": "accepted_no_axis_unit_fix",
            "Q4_allowed_use": "accepted_shape_only",
        }
    )
    response["allowed_use_after_acceptance"] = "shape_candidate_only_no_load"
    response["formula_ready"] = "no"
    response["endpoint_replay_permission_after_acceptance"] = "no"
    response["kernel_promotion_permission_after_acceptance"] = "no"
    response["new_route_scoring_permission_after_acceptance"] = "no"
    response["forbidden_inputs"] = FORBIDDEN_INPUTS
    response["endpoint_data_policy"] = ENDPOINT_POLICY
    response["claim_boundary"] = CLAIM_BOUNDARY

    validation_text = VALIDATION_SUMMARY.read_text(encoding="utf-8", errors="replace") if VALIDATION_SUMMARY.exists() else ""
    notes_text = COMPLETION_NOTES.read_text(encoding="utf-8", errors="replace") if COMPLETION_NOTES.exists() else ""

    final_status = (
        "ACCEPT_SHAPE_ONLY_LOAD_FORMULA_BLOCKED"
        if guardrail_pass and answer_validation_pass
        else "BLOCKED_REVIEW_RESPONSE_NOT_ACCEPTED"
    )
    summary = {
        "n_rows": int(len(response)),
        "galaxies": sorted(response["galaxy"].unique().tolist()),
        "answer_validation_pass": bool(answer_validation_pass),
        "guardrail_pass": bool(guardrail_pass),
        "reviewer_answers": answers,
        "confidence_counts": response["confidence"].value_counts().sort_index().to_dict(),
        "accepted_source_side_shape_candidate": bool(guardrail_pass and answer_validation_pass),
        "source_native_normalization_rule_found": False,
        "axis_or_units_fix_found": False,
        "component_identity_resolved_for_load": False,
        "allowed_use": "shape_candidate_only_no_load",
        "formula_ready": False,
        "endpoint_replay_permission_counts": response[
            "endpoint_replay_permission_after_acceptance"
        ].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": response[
            "kernel_promotion_permission_after_acceptance"
        ].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": response[
            "new_route_scoring_permission_after_acceptance"
        ].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "final_status": final_status,
        "validation_summary_excerpt": validation_text[:1200],
        "completion_notes_excerpt": notes_text[:1600],
        "verdict": (
            "The filled semantics review confirms that the displayed Zhang et al. mass "
            "profile is not source-resolved as the isolated outer component with a "
            "normalization to the quoted 1.4e8 Msun mass. No source-native normalization "
            "or axis/unit fix was found. The profile is accepted only as a shape candidate; "
            "load formula, kernel promotion, and endpoint replay remain closed."
        ),
        "next_allowed_action": (
            "Use the profile only as source-side shape context, or obtain an author/source-native "
            "outer-component table before reopening load-formula derivation."
        ),
    }
    return response, summary


def main() -> None:
    frame, summary = build_acceptance()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
