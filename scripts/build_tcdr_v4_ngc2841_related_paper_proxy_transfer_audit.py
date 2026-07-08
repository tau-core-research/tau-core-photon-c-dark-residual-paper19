from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT.parent
SOURCE_DIR = ROOT / "data" / "source_manifests"

PAPER9_BULLOCK = (
    PROJECTS
    / "tau-core-projection-readout-paper9"
    / "data"
    / "derived"
    / "ugc12506_beta_closure_bullock_spin_conversion_proxy_values.csv"
)
PAPER9_PREFREEZE_REPORT = (
    PROJECTS
    / "tau-core-projection-readout-paper9"
    / "reports"
    / "ugc12506_beta_closure_spin_route_prefreeze_gate.md"
)
PAPER9_TAXONOMY_REPORT = (
    PROJECTS
    / "tau-core-projection-readout-paper9"
    / "reports"
    / "projection_channel_taxonomy.md"
)
PAPER8_EULER_REPORT = (
    PROJECTS
    / "tau-core-morphology-forward-readout-paper8"
    / "reports"
    / "s4g75_ngc4088_minimal_euler_ansatz_gate.md"
)
PAPER8_NGC7331_Q_AUDIT = (
    PROJECTS
    / "tau-core-morphology-forward-readout-paper8"
    / "data"
    / "derived"
    / "ngc7331_b2_q_placement_ablation_summary.csv"
)
PAPER19_MULTIPLIER = (
    SOURCE_DIR / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_summary_v0_1.json"
)
PAPER19_THEOREM = (
    SOURCE_DIR / "tcdr_v4_ngc2841_tau_side_load_theorem_readiness_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_related_paper_proxy_transfer_audit_not_endpoint"
ENDPOINT_POLICY = (
    "cross_paper_proxy_audit_only_do_not_use_rotation_residuals_endpoint_scores_or_required_gap_as_source"
)
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_ngc2841_bullock() -> dict[str, object]:
    if not PAPER9_BULLOCK.exists():
        return {
            "paper9_bullock_available": False,
            "lambda_spin": None,
            "beta_if_used": None,
            "artifact": str(PAPER9_BULLOCK),
        }
    frame = pd.read_csv(PAPER9_BULLOCK)
    row = frame[frame["galaxy"] == "NGC2841"]
    if row.empty:
        return {
            "paper9_bullock_available": False,
            "lambda_spin": None,
            "beta_if_used": None,
            "artifact": str(PAPER9_BULLOCK),
        }
    item = row.iloc[0]
    return {
        "paper9_bullock_available": True,
        "lambda_spin": float(item["lambda_bullock_disk_proxy"]),
        "beta_if_used": float(item["beta_if_bullock_disk_proxy_used"]),
        "artifact": str(PAPER9_BULLOCK.relative_to(PROJECTS)),
    }


def build_proxy_transfer_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    multiplier = _load_json(PAPER19_MULTIPLIER)
    theorem = _load_json(PAPER19_THEOREM)
    bullock = _read_ngc2841_bullock()

    rows = [
        {
            "galaxy": "NGC2841",
            "proxy_route": "paper9_bullock_disk_spin_proxy",
            "origin_paper": "paper9_projection_readout",
            "proxy_type": "dimensionless_spin_beta_transfer_proxy",
            "source_artifact": bullock["artifact"],
            "source_value": (
                f"lambda_bullock_disk_proxy={bullock['lambda_spin']:.12g};"
                f"beta_if_used={bullock['beta_if_used']:.12g}"
                if bullock["paper9_bullock_available"]
                else "not_available"
            ),
            "transfer_status": "TRANSFERABLE_AS_DIMENSIONLESS_CONTEXT_NOT_A_TAU",
            "why_not_a_tau": (
                "Paper 9 Bullock conversion supplies a dimensionless spin/beta proxy. "
                "It can inform a multiplicative carrier or beta-closure route after "
                "separate label promotion, but it does not supply an additive "
                "velocity-squared A_tau for Delta_v^2=A_tau*K_outer."
            ),
            "allowed_use": "dimensionless_context_for_future_beta_or_closure_route",
            "blocked_use": "direct_additive_A_tau_for_ngc2841_outer_capacity",
            "source_safety": "residual_blind_in_source_artifact",
        },
        {
            "galaxy": "NGC2841",
            "proxy_route": "paper9_distributed_vertical_halo_beta_formula",
            "origin_paper": "paper9_projection_readout",
            "proxy_type": "multiplicative_carrier_formula_family",
            "source_artifact": str(
                (
                    PROJECTS
                    / "tau-core-projection-readout-paper9"
                    / "reports"
                    / "beta_transfer_distributed_vertical_halo_formula_freeze.md"
                ).relative_to(PROJECTS)
            ),
            "source_value": "v_lock^2=v_carrier^2*[1+(beta_cl-1)*K_DVH]",
            "transfer_status": "FAMILY_MISMATCH_FOR_CURRENT_ADDITIVE_OUTER_CAPACITY_ROUTE",
            "why_not_a_tau": (
                "This is a multiplicative beta-transfer/vertical-halo formula, not an "
                "additive positive-load theorem. NGC2841 would need a source-side "
                "replacement-label route before this family could be relevant."
            ),
            "allowed_use": "taxonomy_comparison_only",
            "blocked_use": "using_beta_formula_as_additive_A_tau",
            "source_safety": "formula_was_source_frozen_for_other_galaxies_not_for_ngc2841",
        },
        {
            "galaxy": "NGC2841",
            "proxy_route": "paper8_ngc4088_minimal_euler_warp_amplitude",
            "origin_paper": "paper8_morphology_forward_readout",
            "proxy_type": "conditional_additive_velocity_squared_ansatz",
            "source_artifact": str(PAPER8_EULER_REPORT.relative_to(PROJECTS)),
            "source_value": "lambda_w=sigma_warp*q_warp*x_w*Vflat^2",
            "transfer_status": "FORMULA_CONDITIONAL_NOT_DIRECTLY_TRANSFERABLE",
            "why_not_a_tau": (
                "The algebra is dimensionally useful but Paper 8 records the target "
                "functional as not Tau-side derived. Transferring it to NGC2841 would "
                "require source-native q_warp, x_w, sign, and an accepted carrier-scale "
                "rule; Vflat^2 cannot be used here as a curve-saving required-load proxy."
            ),
            "allowed_use": "candidate_shape_of_future_source_factored_load_theorem",
            "blocked_use": "direct_NGC2841_A_tau_without_new_source_freeze",
            "source_safety": "origin_artifact_is_endpoint_blind_but_not_theorem_complete",
        },
        {
            "galaxy": "NGC2841",
            "proxy_route": "paper8_ngc7331_split_b2_unit_load_and_q_audit",
            "origin_paper": "paper8_morphology_forward_readout",
            "proxy_type": "warp_history_unit_load_transfer_caution",
            "source_artifact": str(PAPER8_NGC7331_Q_AUDIT.relative_to(PROJECTS)),
            "source_value": "q-placement and Vflat^2 transfer can suppress or mis-scale corrections",
            "transfer_status": "TRANSFER_CAUTION_NOT_A_TAU",
            "why_not_a_tau": (
                "The NGC7331 audit warns that reusing a transferred warp-load protocol "
                "can misplace q_warp and alter scaling. This argues against transplanting "
                "a Paper 8 amplitude form into NGC2841 without a fresh source-side theorem."
            ),
            "allowed_use": "negative_transfer_caution",
            "blocked_use": "blind_formula_transplant",
            "source_safety": "diagnostic_caution_from_related_paper",
        },
        {
            "galaxy": "NGC2841",
            "proxy_route": "paper9_projection_channel_taxonomy_mass_envelope_closure",
            "origin_paper": "paper9_projection_readout",
            "proxy_type": "channel_taxonomy",
            "source_artifact": str(PAPER9_TAXONOMY_REPORT.relative_to(PROJECTS)),
            "source_value": "mass/envelope/closure channel requires source-native carrier/amplitude freeze",
            "transfer_status": "ARCHITECTURE_SUPPORTS_ROUTE_BUT_REQUIRES_NEW_SOURCE_FREEZE",
            "why_not_a_tau": (
                "The taxonomy supports the idea that an envelope/closure channel may be "
                "distinct from local baryonic density, but it explicitly requires "
                "source-native carrier/amplitude freeze. It supplies no NGC2841 numeric A_tau."
            ),
            "allowed_use": "architecture_alignment",
            "blocked_use": "numeric_A_tau_claim",
            "source_safety": "taxonomy_only",
        },
        {
            "galaxy": "NGC2841",
            "proxy_route": "paper19_physical_hi_plus_helium_control",
            "origin_paper": "paper19_current",
            "proxy_type": "physical_gas_velocity_squared_control",
            "source_artifact": (
                "data/source_manifests/"
                "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_summary_v0_1.json"
            ),
            "source_value": "HI+He control accepted; extra multiplier absent",
            "transfer_status": "CONTROL_READY_NOT_EXTRA_A_TAU",
            "why_not_a_tau": (
                "The physical gas control has velocity-squared units, but it is already "
                "baryonic bookkeeping. It cannot be promoted to dark-residual A_tau "
                "without an independent extra-capacity multiplier."
            ),
            "allowed_use": "physical_gas_control",
            "blocked_use": "extra_dark_residual_multiplier",
            "source_safety": "current_paper_source_frozen_control",
        },
    ]

    frame = pd.DataFrame(rows)
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["positive_load_freeze_permission"] = "no"
    frame["A_tau_freeze_permission"] = "no"
    frame["uses_vobs_or_residual"] = "no"
    frame["forbidden_endpoint_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "related_papers_checked": [
            "paper8_morphology_forward_readout",
            "paper9_projection_readout",
            "paper19_current",
        ],
        "paper9_bullock_ngc2841_available": bullock["paper9_bullock_available"],
        "paper9_bullock_ngc2841_lambda_spin": bullock["lambda_spin"],
        "paper9_bullock_ngc2841_beta_if_used": bullock["beta_if_used"],
        "direct_A_tau_proxy_found": False,
        "dimensionless_context_proxy_found": bool(bullock["paper9_bullock_available"]),
        "transferable_as_additive_outer_capacity": False,
        "theorem_ready_from_previous_audit": theorem["theorem_ready"],
        "independent_multiplier_ready_from_previous_audit": multiplier[
            "independent_multiplier_ready"
        ],
        "status_counts": frame["transfer_status"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": (
            frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "positive_load_freeze_permission_counts": (
            frame["positive_load_freeze_permission"].value_counts().sort_index().to_dict()
        ),
        "A_tau_freeze_permission_counts": (
            frame["A_tau_freeze_permission"].value_counts().sort_index().to_dict()
        ),
        "uses_vobs_or_residual_counts": (
            frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Related Paper 8/9 material helps classify the blocker but does not close it. "
            "Paper 9 provides a residual-blind dimensionless Bullock spin proxy for NGC2841, "
            "which is relevant to multiplicative beta/closure routes but not a velocity-squared "
            "additive A_tau. Paper 8 provides a useful source-factored amplitude form, but it "
            "remains formula-conditional and cannot be transplanted into NGC2841 without fresh "
            "source-side q/x/sign/carrier freeze. No direct A_tau proxy is found."
        ),
        "next_allowed_action": (
            "Either reformulate NGC2841 as a source-supported multiplicative beta/closure "
            "candidate using the Paper 9 dimensionless proxy, or continue the additive route "
            "only by deriving/procuring a velocity-squared A_tau source. Do not score from "
            "these transferred proxies."
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_proxy_transfer_audit()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "proxy_route",
                "origin_paper",
                "transfer_status",
                "allowed_use",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
