from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
RESPONSE_DIR = (
    ROOT
    / "data"
    / "reviewer_responses"
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_response_v0_1"
)

RESPONSE_CSV = RESPONSE_DIR / "review_response_completed.csv"
RESPONSE_JSON = RESPONSE_DIR / "review_decision_summary.json"
OUT_CSV = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_v0_1.csv"
)
OUT_JSON = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_beta_closure_reformulation_review_acceptance_not_endpoint"
EXPECTED_DECISIONS = {
    "Q1_spin_route": "retain_as_context_only",
    "Q2_carrier_policy": "require_new_source_frozen_carrier",
    "Q3_k_beta_kernel": "require_new_source_native_radial_profile",
    "Q4_route_status": "review_open_not_promoted",
}
STRICT_NO_FIELDS = [
    "endpoint_replay_permission",
    "kernel_promotion_permission",
    "formula_freeze_permission",
]
STRICT_FALSE_FIELDS = [
    "uses_rotation_curve_or_velocity",
    "uses_endpoint_rotation_residual",
    "uses_tau_core_score_or_required_load",
]


def _load_response_summary() -> dict[str, object]:
    if not RESPONSE_JSON.exists():
        raise FileNotFoundError(f"Missing reviewer summary: {RESPONSE_JSON}")
    return json.loads(RESPONSE_JSON.read_text(encoding="utf-8"))


def build_acceptance() -> tuple[pd.DataFrame, dict[str, object]]:
    if not RESPONSE_CSV.exists():
        raise FileNotFoundError(f"Missing reviewer response: {RESPONSE_CSV}")
    response_summary = _load_response_summary()
    frame = pd.read_csv(RESPONSE_CSV, keep_default_na=False)
    if set(EXPECTED_DECISIONS) != set(frame["question_id"]):
        raise ValueError("Reviewer response question set does not match the expected template.")

    rows = []
    for _, item in frame.iterrows():
        qid = str(item["question_id"])
        expected = EXPECTED_DECISIONS[qid]
        answer = str(item["reviewer_answer"])
        decision_matches = answer == expected
        strict_no_ok = all(str(item[field]) == "must_be_no" for field in STRICT_NO_FIELDS)
        strict_false_ok = all(str(item[field]) == "must_be_false" for field in STRICT_FALSE_FIELDS)
        rows.append(
            {
                "galaxy": item["galaxy"],
                "question_id": qid,
                "reviewer_answer": answer,
                "expected_acceptance_answer": expected,
                "decision_matches_expected": "yes" if decision_matches else "no",
                "confidence": item["confidence"],
                "acceptance_status": (
                    "ACCEPT_REVIEW_DECISION" if decision_matches and strict_no_ok and strict_false_ok else "REJECT_OR_REVIEW_RESPONSE"
                ),
                "route_effect": _route_effect(qid, answer),
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "formula_freeze_permission": "no",
                "uses_vobs_or_residual": "no",
                "evidence_note": item["evidence_quote_or_note"],
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    out = pd.DataFrame(rows)
    accepted = bool((out["acceptance_status"] == "ACCEPT_REVIEW_DECISION").all())
    strict_high_confidence = bool((out["confidence"] == "high").all())
    summary = {
        "artifact": OUT_CSV.name,
        "galaxy": "NGC2841",
        "n_rows": int(len(out)),
        "claim_boundary": CLAIM_BOUNDARY,
        "review_response_claim_boundary": response_summary["claim_boundary"],
        "overall_verdict": response_summary["overall_verdict"],
        "review_response_accepted": accepted,
        "all_decisions_high_confidence": strict_high_confidence,
        "spin_route_status": "context_only_not_spin_freeze",
        "carrier_status": "blocked_requires_new_source_frozen_carrier",
        "K_beta_status": "blocked_requires_source_native_radial_profile",
        "beta_closure_route_status": "review_open_not_promoted",
        "endpoint_ready": False,
        "formula_freeze_ready": False,
        "kernel_promotion_ready": False,
        "blocked_requirement_ids": [
            "BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE",
            "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE",
            "BETA_K_REQUIRES_SOURCE_NATIVE_RADIAL_PROFILE",
        ],
        "permission_counts": {
            "endpoint_replay_permission": out["endpoint_replay_permission"].value_counts().to_dict(),
            "kernel_promotion_permission": out["kernel_promotion_permission"].value_counts().to_dict(),
            "formula_freeze_permission": out["formula_freeze_permission"].value_counts().to_dict(),
            "uses_vobs_or_residual": out["uses_vobs_or_residual"].value_counts().to_dict(),
        },
        "allowed_next_actions": response_summary["allowed_next_actions"],
        "blocked_actions": response_summary["blocked_actions"],
        "verdict": (
            "The filled reviewer response is accepted as source-side review evidence. "
            "It keeps NGC2841 beta/closure open only as a review route: the Bullock "
            "spin proxy is context-only, the carrier must be newly source-frozen, "
            "and K_beta requires a residual-blind radial PA/i profile or native table. "
            "No endpoint replay, kernel promotion, or formula freeze is authorized."
        ),
        "next_allowed_action": (
            "obtain_source_native_radial_profile_or_build_spin_carrier_review_package_before_formula_freeze"
        ),
    }
    return out, summary


def _route_effect(question_id: str, answer: str) -> str:
    if question_id == "Q1_spin_route" and answer == "retain_as_context_only":
        return "spin_proxy_context_only_not_freeze"
    if question_id == "Q2_carrier_policy" and answer == "require_new_source_frozen_carrier":
        return "carrier_freeze_still_blocked"
    if question_id == "Q3_k_beta_kernel" and answer == "require_new_source_native_radial_profile":
        return "K_beta_freeze_still_blocked_until_radial_profile"
    if question_id == "Q4_route_status" and answer == "review_open_not_promoted":
        return "route_open_no_promotion"
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
