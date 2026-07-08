from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
RESPONSE_ROOT = ROOT / "data" / "reviewer_responses"
RESPONSE_ID = "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_response_v0_1"
RESPONSE_DIR = RESPONSE_ROOT / RESPONSE_ID
LOCAL_RESPONSE_ZIP = RESPONSE_ROOT / f"{RESPONSE_ID}.zip"
DOWNLOAD_RESPONSE_ZIP = (
    Path.home() / "Downloads" / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_response_v0_1(1).zip"
)

RESPONSE_CSV = RESPONSE_DIR / "review_response_completed.csv"
DECISION_CSV = RESPONSE_DIR / "endpoint_authorization_review_decision.csv"
DECISION_JSON = RESPONSE_DIR / "review_decision_summary.json"
OUT_CSV = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance_v0_1.csv"
)
OUT_JSON = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance_summary_v0_1.json"
)

CLAIM_BOUNDARY = (
    "ngc2841_beta_closure_endpoint_authorization_review_acceptance_preliminary_control_only"
)
EXPECTED_DECISIONS = {
    "Q1_formula_integrity": "authorize_unchanged_formula_replay",
    "Q2_beta_context_boundary": "accept_caveated_beta_context",
    "Q3_endpoint_scope": "single_object_preliminary_control_replay_only",
    "Q4_final_authorization": "authorize_endpoint_replay_preliminary_control",
}
STRICT_NO_FIELDS = ["formula_retuning_allowed", "morphology_relabel_allowed"]
STRICT_FALSE_FIELDS = [
    "uses_rotation_curve_or_velocity",
    "uses_endpoint_rotation_residual",
    "uses_tau_core_score_or_required_load",
]


def _ensure_response_files() -> None:
    if RESPONSE_CSV.exists() and DECISION_CSV.exists() and DECISION_JSON.exists():
        return
    if not LOCAL_RESPONSE_ZIP.exists():
        if not DOWNLOAD_RESPONSE_ZIP.exists():
            raise FileNotFoundError(
                "Missing filled reviewer response. Expected either "
                f"{LOCAL_RESPONSE_ZIP} or {DOWNLOAD_RESPONSE_ZIP}."
            )
        RESPONSE_ROOT.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DOWNLOAD_RESPONSE_ZIP, LOCAL_RESPONSE_ZIP)
    with zipfile.ZipFile(LOCAL_RESPONSE_ZIP) as zf:
        zf.extractall(RESPONSE_ROOT)
    if not RESPONSE_CSV.exists() or not DECISION_CSV.exists() or not DECISION_JSON.exists():
        raise FileNotFoundError("The filled reviewer response zip did not contain the expected files.")


def _load_decision_summary() -> dict[str, object]:
    return json.loads(DECISION_JSON.read_text(encoding="utf-8"))


def _norm(value: object) -> str:
    return str(value).strip().lower()


def _is_no(value: object) -> bool:
    return _norm(value) in {"no", "false", "0"}


def _is_yes(value: object) -> bool:
    return _norm(value) in {"yes", "true", "1"}


def build_acceptance() -> tuple[pd.DataFrame, dict[str, object]]:
    _ensure_response_files()
    response_summary = _load_decision_summary()
    response = pd.read_csv(RESPONSE_CSV, keep_default_na=False)
    decision = pd.read_csv(DECISION_CSV, keep_default_na=False)

    expected_qids = set(EXPECTED_DECISIONS)
    if set(response["question_id"]) != expected_qids:
        raise ValueError("Reviewer response question set does not match the endpoint authorization template.")
    if set(decision["question_id"]) != expected_qids:
        raise ValueError("Reviewer decision question set does not match the endpoint authorization template.")

    decision_by_qid = {str(row["question_id"]): row for _, row in decision.iterrows()}
    rows = []
    for _, item in response.iterrows():
        qid = str(item["question_id"])
        expected = EXPECTED_DECISIONS[qid]
        answer = str(item["reviewer_answer"])
        decision_row = decision_by_qid[qid]
        decision_answer = str(decision_row["reviewer_answer"])
        decision_matches = answer == expected and decision_answer == expected
        permission_ok = (
            _is_yes(item["endpoint_replay_permission"])
            and _is_yes(decision_row["endpoint_replay_permission"])
        )
        strict_no_ok = all(_is_no(item[field]) for field in STRICT_NO_FIELDS)
        strict_false_ok = all(_is_no(item[field]) for field in STRICT_FALSE_FIELDS)
        decision_no_retune_ok = _is_no(decision_row["formula_retuning_allowed"])
        decision_no_relabel_ok = _is_no(decision_row["morphology_relabel_allowed"])
        decision_no_endpoint_inputs_ok = _is_no(decision_row["uses_vobs_or_residual"])
        accepted = all(
            [
                decision_matches,
                permission_ok,
                strict_no_ok,
                strict_false_ok,
                decision_no_retune_ok,
                decision_no_relabel_ok,
                decision_no_endpoint_inputs_ok,
            ]
        )
        rows.append(
            {
                "galaxy": item["galaxy"],
                "question_id": qid,
                "reviewer_answer": answer,
                "expected_acceptance_answer": expected,
                "decision_matches_expected": "yes" if decision_matches else "no",
                "confidence": item["confidence"],
                "acceptance_status": "ACCEPT_ENDPOINT_AUTHORIZATION" if accepted else "REJECT_OR_REVIEW_RESPONSE",
                "route_effect": _route_effect(qid, answer),
                "endpoint_replay_permission": "yes" if accepted else "no",
                "authorized_scope": "single_object_preliminary_control_replay_only",
                "kernel_promotion_permission": "no",
                "formula_retuning_allowed": "no",
                "morphology_relabel_allowed": "no",
                "validation_claim_allowed": "no",
                "scoring_script_may_read_vobs_after_authorization": "yes" if accepted else "no",
                "formula_must_be_read_unchanged": "yes",
                "uses_vobs_or_residual_in_review": "no",
                "evidence_note": item["evidence_quote_or_note"],
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    out = pd.DataFrame(rows)
    accepted = bool((out["acceptance_status"] == "ACCEPT_ENDPOINT_AUTHORIZATION").all())
    high_confidence = bool((out["confidence"] == "high").all())
    summary = {
        "artifact": OUT_CSV.name,
        "galaxy": "NGC2841",
        "n_rows": int(len(out)),
        "claim_boundary": CLAIM_BOUNDARY,
        "review_response_claim_boundary": response_summary["claim_boundary"],
        "overall_verdict": response_summary["overall_verdict"],
        "review_response_accepted": accepted,
        "all_decisions_high_confidence": high_confidence,
        "endpoint_replay_authorized": accepted,
        "endpoint_scope": "single_object_preliminary_endpoint_control_replay_only",
        "endpoint_ready": accepted,
        "kernel_promotion_ready": False,
        "validation_claim_allowed": False,
        "formula_retuning_allowed": False,
        "morphology_relabel_allowed": False,
        "scoring_script_may_read_vobs_after_authorization": accepted,
        "formula_must_be_read_unchanged": True,
        "authorized_formula": response_summary["authorized_formula"],
        "beta_context": response_summary["beta_context"],
        "beta_context_boundary": response_summary["beta_context_boundary"],
        "k_beta_status": response_summary["k_beta_status"],
        "carrier_status": response_summary["carrier_status"],
        "source_side_evidence": response_summary["source_side_evidence"],
        "not_authorized": response_summary["not_authorized"],
        "conditions_for_valid_replay": response_summary["conditions_for_valid_replay"],
        "permission_counts": {
            "endpoint_replay_permission": out["endpoint_replay_permission"].value_counts().to_dict(),
            "kernel_promotion_permission": out["kernel_promotion_permission"].value_counts().to_dict(),
            "formula_retuning_allowed": out["formula_retuning_allowed"].value_counts().to_dict(),
            "morphology_relabel_allowed": out["morphology_relabel_allowed"].value_counts().to_dict(),
            "validation_claim_allowed": out["validation_claim_allowed"].value_counts().to_dict(),
            "uses_vobs_or_residual_in_review": out["uses_vobs_or_residual_in_review"].value_counts().to_dict(),
        },
        "legacy_blocked_review_artifact_present": (RESPONSE_DIR / "review_response_acceptance_summary.json").exists(),
        "legacy_blocked_review_disposition": (
            "superseded_for_endpoint_authorization_by_later_k_beta_carrier_and_formula_freeze_reviews"
        ),
        "verdict": (
            "The filled endpoint authorization response is accepted. It authorizes only a "
            "separate NGC2841 single-object preliminary endpoint/control replay using the "
            "frozen beta-context formula unchanged. It does not authorize retuning, "
            "morphology/readout relabeling, kernel promotion, validation claims, or "
            "population claims."
        ),
        "next_allowed_action": (
            "write_and_run_separate_endpoint_replay_script_that_reads_the_frozen_formula_unchanged"
        ),
    }
    return out, summary


def _route_effect(question_id: str, answer: str) -> str:
    if question_id == "Q1_formula_integrity" and answer == "authorize_unchanged_formula_replay":
        return "frozen_formula_integrity_authorized_for_replay"
    if question_id == "Q2_beta_context_boundary" and answer == "accept_caveated_beta_context":
        return "beta_context_accepted_only_as_caveated_context_coefficient"
    if question_id == "Q3_endpoint_scope" and answer == "single_object_preliminary_control_replay_only":
        return "endpoint_scope_limited_to_single_object_preliminary_control"
    if question_id == "Q4_final_authorization" and answer == "authorize_endpoint_replay_preliminary_control":
        return "separate_endpoint_replay_authorized_preliminary_control_only"
    return "unexpected_response"


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_acceptance()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
