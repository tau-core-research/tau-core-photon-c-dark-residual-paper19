from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

RELATED_PROXY_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_summary_v0_1.json"
)
REVIEW_ACCEPTANCE_SUMMARY = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json"
)
K_BETA_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_v0_1.csv"
K_BETA_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_summary_v0_1.json"
)
CARRIER_CSV = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_v0_1.csv"
)
CARRIER_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_v0_1.csv"
OUT_JSON = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_beta_closure_context_formula_freeze_review_not_endpoint"
FORMULA_ID = "F_NGC2841_BETA_CONTEXT_CLOSURE_REVIEW_V0_1"
FORMULA_EXPRESSION = (
    "v_beta_context^2(R)=v_carrier^2(R)*[1+(beta_context-1)*K_beta_shape(R)]"
)
PERTURBATION_EXPRESSION = (
    "Delta_v_beta_context^2(R)=(beta_context-1)*K_beta_shape(R)*v_carrier^2(R)"
)
ENDPOINT_POLICY = "formula_freeze_review_only_no_vobs_errv_endpoint_scores_or_residuals"
FORBIDDEN_INPUTS = (
    "Vobs;errV;rotation_curve;rotation_residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def build_context_formula_freeze_review() -> tuple[pd.DataFrame, dict[str, object]]:
    related = _load_json(RELATED_PROXY_SUMMARY)
    review = _load_json(REVIEW_ACCEPTANCE_SUMMARY)
    k_summary = _load_json(K_BETA_SUMMARY)
    carrier_summary = _load_json(CARRIER_SUMMARY)

    if related.get("paper9_bullock_ngc2841_available") is not True:
        raise ValueError("Paper 9 Bullock-like beta context is not available.")
    if review.get("spin_route_status") != "context_only_not_spin_freeze":
        raise ValueError("This builder expects spin route to remain context-only.")
    if k_summary.get("K_beta_profile_ready_for_formula_freeze_review") is not True:
        raise ValueError("K_beta shape is not formula-freeze-review ready.")
    if carrier_summary.get("carrier_ready_for_beta_formula_freeze_review") is not True:
        raise ValueError("Carrier is not formula-freeze-review ready.")

    beta_context = float(related["paper9_bullock_ngc2841_beta_if_used"])
    lambda_context = float(related["paper9_bullock_ngc2841_lambda_spin"])
    if beta_context <= 0:
        raise ValueError("Beta context coefficient must be positive.")

    k_frame = pd.read_csv(K_BETA_CSV).sort_values("radius_kpc").reset_index(drop=True)
    carrier = pd.read_csv(CARRIER_CSV).sort_values("radius_kpc").reset_index(drop=True)

    k_radius = pd.to_numeric(k_frame["radius_kpc"], errors="raise").to_numpy(dtype=float)
    k_value = pd.to_numeric(k_frame["k_beta_shape_0_1"], errors="raise").to_numpy(dtype=float)
    carrier_radius = pd.to_numeric(carrier["radius_kpc"], errors="raise").to_numpy(dtype=float)
    carrier_v2 = pd.to_numeric(carrier["v_carrier2_fixed_ml_km2s2"], errors="raise")

    k_interp = np.interp(carrier_radius, k_radius, k_value, left=k_value[0], right=k_value[-1])
    delta_v2 = (beta_context - 1.0) * k_interp * carrier_v2
    v_beta2 = carrier_v2 + delta_v2

    frame = carrier[
        [
            "galaxy",
            "radius_kpc",
            "v_carrier2_fixed_ml_km2s2",
            "v_carrier_fixed_ml_kms",
            "carrier_id",
            "carrier_policy",
        ]
    ].copy()
    frame["k_beta_shape_interp_0_1"] = k_interp
    frame["beta_context"] = beta_context
    frame["lambda_spin_context"] = lambda_context
    frame["delta_v_beta_context2_km2s2"] = delta_v2
    frame["v_beta_context2_km2s2"] = v_beta2
    frame["v_beta_context_kms"] = np.sqrt(np.maximum(v_beta2, 0.0))
    frame["formula_id"] = FORMULA_ID
    frame["formula_expression"] = FORMULA_EXPRESSION
    frame["perturbation_expression"] = PERTURBATION_EXPRESSION
    frame["beta_context_role"] = (
        "caveated_context_coefficient_not_direct_source_native_spin_measurement"
    )
    frame["spin_blocker_disposition"] = (
        "retired_for_formula_review_by_recasting_as_beta_context_not_spin_freeze"
    )
    frame["formula_freeze_review_status"] = (
        "all_terms_frozen_for_formula_review_endpoint_still_forbidden"
    )
    frame["formula_freeze_review_ready"] = "yes"
    frame["physical_spin_claim"] = "no"
    frame["endpoint_ready"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["formula_freeze_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["uses_vobs_or_residual"] = "no"
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "formula_id": FORMULA_ID,
        "formula_expression": FORMULA_EXPRESSION,
        "perturbation_expression": PERTURBATION_EXPRESSION,
        "beta_context": beta_context,
        "lambda_spin_context": lambda_context,
        "beta_context_source": "paper9_bullock_ngc2841_dimensionless_proxy_context",
        "beta_context_role": "caveated_context_coefficient_not_direct_spin_measurement",
        "dimension_check": (
            "pass_beta_context_and_K_beta_dimensionless_carrier_supplies_velocity_squared"
        ),
        "k_beta_profile_ready": True,
        "carrier_ready": True,
        "spin_blocker_disposition": (
            "retired_for_formula_review_by_recasting_as_beta_context_not_spin_freeze"
        ),
        "physical_spin_claim": False,
        "all_formula_terms_frozen_for_review": True,
        "formula_freeze_review_ready": True,
        "endpoint_ready": False,
        "endpoint_replay_allowed": False,
        "kernel_promotion_ready": False,
        "new_route_scoring_allowed": False,
        "v_beta_context_min_kms": float(frame["v_beta_context_kms"].min()),
        "v_beta_context_max_kms": float(frame["v_beta_context_kms"].max()),
        "delta_v_beta_context2_min_km2s2": float(frame["delta_v_beta_context2_km2s2"].min()),
        "delta_v_beta_context2_max_km2s2": float(frame["delta_v_beta_context2_km2s2"].max()),
        "permission_counts": {
            "endpoint_replay_permission": (
                frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
            ),
            "formula_freeze_permission": (
                frame["formula_freeze_permission"].value_counts().sort_index().to_dict()
            ),
            "kernel_promotion_permission": (
                frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
            ),
            "new_route_scoring_permission": (
                frame["new_route_scoring_permission"].value_counts().sort_index().to_dict()
            ),
            "uses_vobs_or_residual": (
                frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
            ),
        },
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The NGC2841 beta/closure route is now formula-freeze-review ready as a "
            "caveated beta-context formula, not as a physical spin-normalization claim. "
            "The profile still grants no endpoint replay, no kernel promotion, and no "
            "validation claim."
        ),
        "next_allowed_action": (
            "Prepare a separate endpoint authorization review if scoring is desired; "
            "the scoring script must read this frozen formula unchanged."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_context_formula_freeze_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "radius_kpc",
                "k_beta_shape_interp_0_1",
                "v_carrier2_fixed_ml_km2s2",
                "delta_v_beta_context2_km2s2",
                "v_beta_context_kms",
            ]
        ].head(14).to_string(index=False)
    )


if __name__ == "__main__":
    main()
