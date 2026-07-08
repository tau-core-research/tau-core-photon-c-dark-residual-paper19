from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

RELATED_PROXY_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_summary_v0_1.json"
)

OUT_CSV = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_v0_1.csv"
)
OUT_JSON = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_summary_v0_1.json"
)

CLAIM_BOUNDARY = "multiplicative_beta_closure_reformulation_preflight_not_endpoint"
FORMULA_SHELL = "v_beta^2(R)=v_carrier^2(R)*[1+(beta_cl-1)*K_beta(R)]"
PERTURBATION_SHELL = "Delta_v_beta^2(R)=(beta_cl-1)*K_beta(R)*v_carrier^2(R)"
FORBIDDEN_ENDPOINT_FIELDS = (
    "Vobs;rotation_curve;residual;RMSE;endpoint_score;baseline_score;"
    "required_A_tau;required_lambda;observed_velocity_gap"
)


def _load_related_summary() -> dict[str, object]:
    if not RELATED_PROXY_SUMMARY.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {RELATED_PROXY_SUMMARY}")
    return json.loads(RELATED_PROXY_SUMMARY.read_text(encoding="utf-8"))


def _permission_row(
    gate_id: str,
    status: str,
    finding: str,
    allowed_next_action: str,
    blocker: str,
) -> dict[str, str]:
    return {
        "galaxy": "NGC2841",
        "gate_id": gate_id,
        "status": status,
        "finding": finding,
        "formula_shell": FORMULA_SHELL,
        "perturbation_shell": PERTURBATION_SHELL,
        "dimension_status": (
            "valid_if_beta_cl_and_K_beta_are_dimensionless_and_v_carrier_squared_has_velocity_squared_units"
        ),
        "allowed_next_action": allowed_next_action,
        "blocker": blocker,
        "uses_vobs_or_residual": "no",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "formula_freeze_permission": "no",
        "reformulation_label_promotion_permission": "no",
        "claim_boundary": CLAIM_BOUNDARY,
        "forbidden_endpoint_fields": FORBIDDEN_ENDPOINT_FIELDS,
    }


def build_preflight() -> tuple[list[dict[str, str]], dict[str, object]]:
    related = _load_related_summary()
    lambda_spin = float(related["paper9_bullock_ngc2841_lambda_spin"])
    beta_cl = float(related["paper9_bullock_ngc2841_beta_if_used"])

    rows = [
        _permission_row(
            "BETA_1_PROXY_AVAILABLE",
            "PASS_CAVEATED",
            (
                "Paper 9 provides a residual-blind dimensionless Bullock-disk spin proxy "
                f"for NGC2841: lambda_spin={lambda_spin:.12g}, beta_cl={beta_cl:.12g}."
            ),
            "use_only_as_dimensionless_context_for_a_beta_closure_reformulation_review",
            "none_for_preflight_proxy_availability",
        ),
        _permission_row(
            "BETA_2_FAMILY_REFORMULATION_LABEL",
            "BLOCKED_SOURCE_LABEL_REVIEW_REQUIRED",
            (
                "The current Paper 19 route is additive outer-capacity stress/load. "
                "A beta/closure route would be a reformulation, not a continuation of "
                "the additive A_tau route."
            ),
            "build_source_side_reformulation_label_review_before_any_formula_freeze",
            "no_independent_source_side_decision_that_NGC2841_belongs_to_beta_closure_family",
        ),
        _permission_row(
            "BETA_3_FORMULA_SHELL",
            "FORMULA_CONDITIONAL_READY",
            (
                "A multiplicative closure shell is dimensionally coherent because beta_cl "
                "and K_beta are dimensionless while v_carrier^2 supplies velocity-squared units."
            ),
            "derive_source_frozen_carrier_and_K_beta_before_scoring",
            "formula_shell_ready_only_conditionally",
        ),
        _permission_row(
            "BETA_4_CARRIER",
            "BLOCKED_CARRIER_FREEZE_REQUIRED",
            (
                "The beta shell requires a source-frozen carrier velocity-squared field. "
                "A SPARC/baryonic or TPG carrier may be used only after an explicit "
                "carrier freeze policy, not by endpoint performance."
            ),
            "freeze_carrier_policy_source_side",
            "no_NGC2841_beta_route_carrier_freeze",
        ),
        _permission_row(
            "BETA_5_K_BETA_KERNEL",
            "BLOCKED_KERNEL_FREEZE_REQUIRED",
            (
                "The beta shell requires a source-frozen dimensionless K_beta(R). "
                "The existing K_outer stress kernel cannot be silently reused as K_beta "
                "without source-side family and kernel review."
            ),
            "derive_or_freeze_K_beta_from_residual_blind_source_data",
            "no_NGC2841_source_frozen_K_beta_profile",
        ),
        _permission_row(
            "BETA_6_ENDPOINT_LEAKAGE",
            "READY_AS_AUDIT_CONSTRAINT",
            (
                "The reformulation preflight reads only prior source/proxy artifacts and "
                "does not read observed rotation residuals, endpoint scores, or required gaps."
            ),
            "keep_scoring_separate_until_BETA_2_BETA_4_BETA_5_pass",
            "none_for_leakage_audit_constraint",
        ),
        _permission_row(
            "BETA_7_ADDITIVE_ROUTE_SEPARATION",
            "READY_AS_AUDIT_CONSTRAINT",
            (
                "The beta closure shell does not rescue the additive A_tau blocker. "
                "It opens a different candidate family with its own source-label, carrier, "
                "and kernel freeze requirements."
            ),
            "preserve_additive_route_blocked_status",
            "none_for_route_separation_constraint",
        ),
    ]

    blocked_ids = [
        row["gate_id"]
        for row in rows
        if row["status"].startswith("BLOCKED")
    ]
    permission_fields = [
        "uses_vobs_or_residual",
        "endpoint_replay_permission",
        "kernel_promotion_permission",
        "formula_freeze_permission",
        "reformulation_label_promotion_permission",
    ]
    permission_counts = {
        field: {
            "yes": sum(1 for row in rows if row[field] == "yes"),
            "no": sum(1 for row in rows if row[field] == "no"),
        }
        for field in permission_fields
    }
    summary = {
        "artifact": OUT_CSV.name,
        "claim_boundary": CLAIM_BOUNDARY,
        "n_rows": len(rows),
        "reformulation_open": True,
        "beta_proxy_available": True,
        "lambda_spin": lambda_spin,
        "beta_cl_if_used": beta_cl,
        "formula_shell": FORMULA_SHELL,
        "perturbation_shell": PERTURBATION_SHELL,
        "dimension_status": (
            "valid_if_carrier_velocity_squared_and_K_beta_dimensionless"
        ),
        "endpoint_ready": False,
        "formula_freeze_ready": False,
        "source_label_promotion_ready": False,
        "blocked_requirement_ids": blocked_ids,
        "permission_counts": permission_counts,
        "verdict": (
            "Paper 9 opens a legitimate multiplicative beta/closure preflight direction "
            "for NGC2841, but it does not authorize replay. Source-side family "
            "reformulation, carrier freeze, and K_beta freeze remain required."
        ),
        "next_allowed_action": (
            "build_source_side_label_reformulation_review_for_NGC2841_beta_closure_candidate"
        ),
    }
    return rows, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    rows, summary = build_preflight()

    fieldnames = list(rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
