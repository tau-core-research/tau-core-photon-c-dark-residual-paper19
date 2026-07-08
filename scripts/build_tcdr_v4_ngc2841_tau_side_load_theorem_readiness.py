from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

MULTIPLIER_AUDIT = (
    SOURCE_DIR / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_tau_side_load_theorem_readiness_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_tau_side_load_theorem_readiness_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_tau_side_load_theorem_readiness_not_theorem_not_endpoint"
ENDPOINT_POLICY = (
    "theory_readiness_only_do_not_use_rotation_residuals_endpoint_scores_or_required_gap_as_source"
)
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


THEOREM_ROWS = [
    {
        "requirement_id": "TLOAD_1_SUPPORT_FIELD",
        "requirement_role": "dimensionless_outer_capacity_support",
        "minimal_statement": "K_outer(R) must be source-frozen, nonnegative, dimensionless, and zero outside the declared outer-capacity support.",
        "current_status": "PARTIALLY_READY",
        "current_evidence": (
            "Dragonfly outer support, THINGS/NED MOM0 support, SPARC/THINGS gas proxy, "
            "and PA/inclination geometry provide source-side support/context."
        ),
        "blocking_gap": "composite K_outer is still not promoted to a single theorem-grade source field.",
        "allowed_use": "support_context_and_theory_worklist",
    },
    {
        "requirement_id": "TLOAD_2_UNIT_MAP",
        "requirement_role": "velocity_squared_codomain",
        "minimal_statement": (
            "A Tau-side readout map R_load must send the outer-capacity class to "
            "velocity-squared units without borrowing the endpoint residual scale."
        ),
        "current_status": "BLOCKED",
        "current_evidence": (
            "Physical HI and HI+He controls already have velocity-squared units, but they "
            "are baryonic gas controls rather than extra-capacity readouts."
        ),
        "blocking_gap": "no source-independent Tau map R_load([K_outer]) -> km^2/s^2 is derived.",
        "allowed_use": "theory_derivation_target_only",
    },
    {
        "requirement_id": "TLOAD_3_AMPLITUDE_SOURCE",
        "requirement_role": "residual_blind_positive_scale",
        "minimal_statement": (
            "The amplitude A_tau must come from a protected Tau-side source class or "
            "independent observable, not from the NGC2841 velocity gap."
        ),
        "current_status": "BLOCKED",
        "current_evidence": "Independent multiplier rejection audit finds no extra-capacity multiplier.",
        "blocking_gap": "A_tau is missing; required-gap yardsticks are explicitly forbidden as source multipliers.",
        "allowed_use": "blocker_record_only",
    },
    {
        "requirement_id": "TLOAD_4_SIGN_RULE",
        "requirement_role": "positive_outer_added_load_sign",
        "minimal_statement": (
            "If the theorem is an added-load theorem, it must derive why the relevant "
            "outer-capacity class contributes +A_tau K_outer rather than an attenuation."
        ),
        "current_status": "PARTIALLY_READY",
        "current_evidence": (
            "Projection route is independently closed as attenuation/control; remaining "
            "outer-capacity lane is anatomically positive-load dominated."
        ),
        "blocking_gap": "positive sign is motivated by route separation, not yet forced by a Tau-side theorem.",
        "allowed_use": "conditional_sign_scaffold_only",
    },
    {
        "requirement_id": "TLOAD_5_LIMITS_AND_GAUGE",
        "requirement_role": "known_limits_and_no_double_counting",
        "minimal_statement": (
            "The theorem must recover the carrier when K_outer=0 or A_tau=0, and must "
            "not double-count physical HI, HI+He, or baryonic ceiling controls."
        ),
        "current_status": "READY_AS_AUDIT_CONSTRAINT",
        "current_evidence": (
            "Existing gas, HI+He, projection, and outer-baryonic ceiling controls define "
            "what the added-load theorem is not allowed to absorb."
        ),
        "blocking_gap": "constraint is ready, but it is a boundary condition rather than a load theorem.",
        "allowed_use": "theorem_boundary_condition",
    },
    {
        "requirement_id": "TLOAD_6_ENDPOINT_LEAKAGE",
        "requirement_role": "source_freeze_safety",
        "minimal_statement": (
            "The theorem inputs must be frozen before scoring; no endpoint-fit halo "
            "parameters, required residual scale, or baseline scores may select A_tau, K_outer, or sign."
        ),
        "current_status": "READY_AS_AUDIT_CONSTRAINT",
        "current_evidence": (
            "Independent multiplier audit rejects NFW/ISO fit parameters and keeps all "
            "permissions closed."
        ),
        "blocking_gap": "none for leakage boundary; theorem content still missing.",
        "allowed_use": "theorem_boundary_condition",
    },
]


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_readiness() -> tuple[pd.DataFrame, dict[str, object]]:
    multiplier = _load_json(MULTIPLIER_AUDIT)
    rows = []
    for row in THEOREM_ROWS:
        rows.append(
            {
                **row,
                "candidate_theorem_shell": (
                    "If K_outer is source-frozen and A_tau is supplied by a protected "
                    "Tau-side source class, then Delta_v_tau^2(R)=A_tau*K_outer(R) "
                    "is an admissible added outer-capacity readout; otherwise it is blocked."
                ),
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "positive_load_freeze_permission": "no",
                "theorem_promotion_permission": "no",
                "uses_vobs_or_residual": "no",
                "forbidden_endpoint_inputs": FORBIDDEN_INPUTS,
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    frame = pd.DataFrame(rows)
    blocked = frame[frame["current_status"].astype(str).str.startswith("BLOCKED")]
    summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "candidate_theorem_name": "NGC2841_TAU_SIDE_OUTER_CAPACITY_LOAD_THEOREM_SHELL_V0_1",
        "candidate_formula_shell": "Delta_v_tau^2(R)=A_tau*K_outer(R)",
        "formula_shell_dimension_status": "dimensionally_valid_if_A_tau_has_velocity_squared_units",
        "theorem_ready": False,
        "positive_load_freeze_ready": False,
        "endpoint_ready": False,
        "blocked_requirement_ids": blocked["requirement_id"].tolist(),
        "blocked_requirement_roles": blocked["requirement_role"].tolist(),
        "ready_as_audit_constraint_ids": frame[
            frame["current_status"] == "READY_AS_AUDIT_CONSTRAINT"
        ]["requirement_id"].tolist(),
        "partial_requirement_ids": frame[
            frame["current_status"] == "PARTIALLY_READY"
        ]["requirement_id"].tolist(),
        "status_counts": frame["current_status"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": (
            frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "positive_load_freeze_permission_counts": (
            frame["positive_load_freeze_permission"].value_counts().sort_index().to_dict()
        ),
        "theorem_promotion_permission_counts": (
            frame["theorem_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "uses_vobs_or_residual_counts": (
            frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
        ),
        "independent_multiplier_ready_from_previous_audit": multiplier[
            "independent_multiplier_ready"
        ],
        "previous_audit_endpoint_ready": multiplier["endpoint_ready"],
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The minimal Tau-side load theorem shell is now explicit, but not proved. "
            "The zero-support/no-double-counting and leakage boundaries are ready as "
            "audit constraints, and the outer support/sign anatomy is partially ready. "
            "The decisive missing pieces are a Tau-side unit map into velocity-squared "
            "load and a protected residual-blind amplitude source A_tau. Therefore "
            "NGC2841 remains endpoint-blocked."
        ),
        "next_allowed_action": (
            "Attack only the two blocked theorem pieces: derive R_load([K_outer]) in "
            "velocity-squared units, or find a protected Tau/source-native A_tau. "
            "Do not introduce additional gates or replay from the required residual scale."
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_readiness()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "requirement_id",
                "requirement_role",
                "current_status",
                "blocking_gap",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
