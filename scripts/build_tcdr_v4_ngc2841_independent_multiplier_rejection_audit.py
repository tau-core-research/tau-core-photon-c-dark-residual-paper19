from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_independent_multiplier_rejection_audit_not_endpoint"
ENDPOINT_POLICY = (
    "source_side_multiplier_audit_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
)
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


ROWS = [
    {
        "galaxy": "NGC2841",
        "multiplier_route": "physical_hi_plus_helium_gas_control",
        "route_kind": "baryonic_bookkeeping_control",
        "source_basis": "THINGS/NED MOM0 HI profile plus standard helium bookkeeping factor",
        "source_reference": "Leroy2008SFE;Walter2008THINGS",
        "source_url": "https://arxiv.org/abs/0810.2556",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_summary_v0_1.json"
        ),
        "source_status": "SOURCE_FROZEN_PHYSICAL_GAS_CONTROL",
        "multiplier_status": "CONTROL_READY_NOT_EXTRA_DARK_RESIDUAL_MULTIPLIER",
        "candidate_multiplier_value": "1.36_standard_HI_plus_helium_bookkeeping",
        "allowed_use": "physical_gas_control_only",
        "blocked_use": "extra_halo_capacity_or_positive_dark_residual_multiplier",
        "next_action": "none_for_extra_multiplier_keep_as_control",
    },
    {
        "galaxy": "NGC2841",
        "multiplier_route": "bosma_hi_scaling_outer_disk",
        "route_kind": "empirical_hi_scaling_context_candidate",
        "source_basis": "extended HI support and Bosma-style mass-discrepancy motivation",
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": "https://ui.adsabs.harvard.edu/abs/1981AJ.....86.1825B/abstract",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_summary_v0_1.json"
        ),
        "source_status": "MOTIVATED_CONTEXT_ONLY",
        "multiplier_status": "REJECTED_NO_SOURCE_FROZEN_SCALE",
        "candidate_multiplier_value": "not_frozen",
        "allowed_use": "motivation_context_only",
        "blocked_use": "using_a_Bosma_scale_as_lambda_without_independent_freeze",
        "next_action": "find_independent_Bosma_scale_rule_or_keep_blocked",
    },
    {
        "galaxy": "NGC2841",
        "multiplier_route": "xuv_hi_outer_starforming_capacity",
        "route_kind": "outer_disk_activity_context_candidate",
        "source_basis": "GALEX/XUV and HI outer-disk support beyond the optical disk",
        "source_reference": "Thilker2007XUVDisks",
        "source_url": "https://ui.adsabs.harvard.edu/abs/2007ApJS..173..538T/abstract",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_summary_v0_1.json"
        ),
        "source_status": "SOURCE_SUPPORTED_CONTEXT",
        "multiplier_status": "MULTIPLIER_MISSING",
        "candidate_multiplier_value": "not_available",
        "allowed_use": "outer_activity_context_only",
        "blocked_use": "velocity_squared_extra_load_without_radial_load_conversion",
        "next_action": "acquire_source_native_radial_xuv_hi_load_or_drop_route",
    },
    {
        "galaxy": "NGC2841",
        "multiplier_route": "diffuse_outer_envelope_capacity",
        "route_kind": "diffuse_component_context_candidate",
        "source_basis": "Dragonfly diffuse outer stellar/envelope support and outer mass-profile context",
        "source_reference": "Zhang2018NGC2841Dragonfly",
        "source_url": "https://arxiv.org/abs/1802.02583",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
        ),
        "source_status": "SOURCE_SUPPORTED_SHAPE_CONTEXT",
        "multiplier_status": "MULTIPLIER_MISSING_COMPONENT_NORMALIZATION_MISSING",
        "candidate_multiplier_value": "not_available",
        "allowed_use": "diffuse_shape_context_only",
        "blocked_use": "extra_load_without_component_normalization_or_source_native_table",
        "next_action": "find_independent_component_normalization_or_keep_shape_only",
    },
    {
        "galaxy": "NGC2841",
        "multiplier_route": "history_environment_outer_capacity",
        "route_kind": "history_environment_context_candidate",
        "source_basis": "warp, line-of-nodes twist, infall, halo-shape, hot-gas, and vertical/path context",
        "source_reference": "ShenSellwood2006WarpInfall;Braun2007WesterborkSINGS;Chandra2006NGC2841",
        "source_url": "https://ui.adsabs.harvard.edu/abs/2006MNRAS.370....2S/abstract",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_summary_v0_1.json"
        ),
        "source_status": "CAVEATED_CONTEXT_ONLY",
        "multiplier_status": "MULTIPLIER_MISSING_OBSERVABLE_MISSING",
        "candidate_multiplier_value": "not_available",
        "allowed_use": "history_environment_context_only",
        "blocked_use": "amplitude_or_kernel_weight_without_residual_blind_observable",
        "next_action": "define_residual_blind_environment_history_observable_or_keep_blocked",
    },
    {
        "galaxy": "NGC2841",
        "multiplier_route": "tau_side_outer_capacity_load_theorem",
        "route_kind": "theory_route",
        "source_basis": "Tau-side theorem mapping outer-capacity support to velocity-squared load",
        "source_reference": "internal_tau_core_theory_route",
        "source_url": "not_applicable",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json"
        ),
        "source_status": "THEORY_ROUTE_OPEN",
        "multiplier_status": "THEOREM_MISSING",
        "candidate_multiplier_value": "not_derived",
        "allowed_use": "theory_worklist_only",
        "blocked_use": "promoting_required_gap_yardstick_to_source_multiplier",
        "next_action": "derive_tau_side_load_theorem_or_do_not_score_positive_load_kernel",
    },
    {
        "galaxy": "NGC2841",
        "multiplier_route": "nfw_iso_halo_fit_parameters",
        "route_kind": "endpoint_fit_rejected_route",
        "source_basis": "published halo parameters fit to rotation-curve endpoints",
        "source_reference": "halo_fit_literature",
        "source_url": "not_used",
        "local_artifact": (
            "data/source_manifests/"
            "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_summary_v0_1.json"
        ),
        "source_status": "ENDPOINT_FIT_ROUTE",
        "multiplier_status": "REJECTED_ENDPOINT_FIT",
        "candidate_multiplier_value": "forbidden",
        "allowed_use": "negative_control_for_source_freeze_policy",
        "blocked_use": "source_freeze_or_kernel_amplitude_or_multiplier",
        "next_action": "none_reject_for_tau_source_freeze",
    },
]


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    rows = []
    for row in ROWS:
        uses_endpoint = row["multiplier_status"] == "REJECTED_ENDPOINT_FIT"
        rows.append(
            {
                **row,
                "independent_multiplier_ready": "no",
                "positive_load_freeze_permission": "no",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "uses_vobs_or_residual": (
                    "yes_endpoint_fit_route_rejected" if uses_endpoint else "no"
                ),
                "forbidden_endpoint_inputs": FORBIDDEN_INPUTS,
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    frame = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "control_ready_routes": ["physical_hi_plus_helium_gas_control"],
        "context_supported_multiplier_missing_routes": sorted(
            frame[
                frame["multiplier_status"].isin(
                    [
                        "MULTIPLIER_MISSING",
                        "MULTIPLIER_MISSING_COMPONENT_NORMALIZATION_MISSING",
                        "MULTIPLIER_MISSING_OBSERVABLE_MISSING",
                        "REJECTED_NO_SOURCE_FROZEN_SCALE",
                    ]
                )
            ]["multiplier_route"].tolist()
        ),
        "theory_route_open": ["tau_side_outer_capacity_load_theorem"],
        "rejected_endpoint_fit_routes": ["nfw_iso_halo_fit_parameters"],
        "independent_multiplier_ready": False,
        "positive_dark_residual_load_ready": False,
        "endpoint_ready": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "source_status_counts": frame["source_status"].value_counts().sort_index().to_dict(),
        "multiplier_status_counts": frame["multiplier_status"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": (
            frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "positive_load_freeze_permission_counts": (
            frame["positive_load_freeze_permission"].value_counts().sort_index().to_dict()
        ),
        "independent_multiplier_ready_counts": (
            frame["independent_multiplier_ready"].value_counts().sort_index().to_dict()
        ),
        "uses_vobs_or_residual_counts": (
            frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
        ),
        "verdict": (
            "The audit finds one source-frozen physical gas bookkeeping control "
            "(HI plus the standard helium factor) but no independent extra-capacity "
            "or positive dark-residual multiplier. XUV, diffuse-envelope, Bosma-style, "
            "and history/environment routes remain source/context supported but "
            "multiplier-blocked. NFW/ISO halo-fit parameters are rejected because they "
            "are endpoint fits. NGC2841 therefore remains endpoint-blocked."
        ),
        "next_allowed_action": (
            "Either find an independent source-native extra-capacity multiplier, or derive "
            "a Tau-side outer-capacity load theorem. Do not replay the positive-load "
            "kernel from required residual scale."
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_audit()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "multiplier_route",
                "source_status",
                "multiplier_status",
                "allowed_use",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
