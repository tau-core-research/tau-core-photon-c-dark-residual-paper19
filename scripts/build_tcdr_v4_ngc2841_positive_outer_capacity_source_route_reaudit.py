from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
PREFLIGHT_DIR = ROOT / "data" / "external" / "sparc_preflight"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_positive_outer_capacity_source_route_reaudit_not_scoring"
ENDPOINT_POLICY = (
    "source_side_route_reaudit_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
)
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required source-route artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _permission_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    return frame[column].value_counts().sort_index().to_dict()


def build_reaudit() -> tuple[pd.DataFrame, dict[str, object]]:
    projection = _load_json(
        PREFLIGHT_DIR / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.json"
    )
    ceiling = _load_json(
        PREFLIGHT_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.json"
    )
    gap = _load_json(PREFLIGHT_DIR / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.json")
    scale = _load_json(
        PREFLIGHT_DIR / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json"
    )
    mass_semantics = _load_json(
        SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
    )
    hi_gas_proxy = _load_json(
        SOURCE_DIR / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json"
    )

    rows = [
        {
            "galaxy": "NGC2841",
            "route_id": "tilted_ring_projection_control",
            "route_class": "observer_projection_geometry_control",
            "source_basis": "Bosma/NED tilted-ring PA-inclination geometry plus projection-control replay",
            "source_status": "source_frozen_diagnostic_control",
            "load_status": "negative_multiplicative_control_wrong_sign_for_positive_load",
            "priority": "closed_control",
            "allowed_use": "diagnostic_projection_control_only",
            "blocked_use": "positive_outer_capacity_readout;endpoint_kernel_promotion",
            "next_source_action": "none_for_positive_load_route_keep_as_control",
            "source_route_basis_artifacts": (
                "tcdr_v4_ngc2841_projection_control_preflight_summary_v0_1.json;"
                "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.json"
            ),
            "diagnostic_result": (
                f"projection_improves_baryonic={projection['projection_improves_baryonic']};"
                f"projection_minus_baryonic_weighted_rmse_kms="
                f"{projection['projection_minus_baryonic_weighted_rmse_kms']:.6f}"
            ),
        },
        {
            "galaxy": "NGC2841",
            "route_id": "known_integrated_outer_baryonic_ceiling",
            "route_class": "baryonic_ceiling_control",
            "source_basis": "Dragonfly integrated outer stellar mass and 3:1 stellar/gas source-side ratio",
            "source_status": "source_frozen_baryonic_ceiling_control",
            "load_status": "velocity_squared_units_but_too_small",
            "priority": "closed_control",
            "allowed_use": "non_endpoint_baryonic_ceiling_control",
            "blocked_use": "positive_dark_residual_load;endpoint_kernel_promotion",
            "next_source_action": "none_for_positive_load_route_keep_as_baryonic_ceiling_control",
            "source_route_basis_artifacts": (
                "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_summary_v0_1.json;"
                "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.json"
            ),
            "diagnostic_result": (
                f"max_delta_v2_outer_baryonic_ceiling={ceiling['max_delta_v2_outer_baryonic_ceiling']:.6f};"
                f"ceiling_fraction_of_outer_gap={gap['ceiling_fraction_of_outer_baryonic_gap']:.9f}"
            ),
        },
        {
            "galaxy": "NGC2841",
            "route_id": "dragonfly_mass_profile_shape",
            "route_class": "mass_profile_shape_context",
            "source_basis": "Dragonfly mass-profile figure and reviewer-accepted semantics clarification",
            "source_status": "accepted_shape_context_only",
            "load_status": "shape_only_load_formula_blocked",
            "priority": "closed_shape_context",
            "allowed_use": "shape_context_only_no_velocity_squared_load",
            "blocked_use": "load_formula;endpoint_kernel_promotion",
            "next_source_action": "only_reopen_if_source_native_component_normalization_table_is_found",
            "source_route_basis_artifacts": (
                "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
            ),
            "diagnostic_result": str(mass_semantics["final_status"]),
        },
        {
            "galaxy": "NGC2841",
            "route_id": "outer_hi_warp_halo_capacity",
            "route_class": "positive_outer_capacity_candidate",
            "source_basis": "Bosma extended HI, tilted-ring warp, flat outer rotation field, outer M/L context",
            "source_status": "strong_source_side_candidate",
            "load_status": "lower_bound_gas_proxy_frozen_halo_capacity_load_still_missing",
            "priority": "high_primary_positive_load_candidate",
            "allowed_use": "source_acquisition_worklist_for_positive_outer_capacity",
            "blocked_use": "endpoint_scoring_until_halo_capacity_or_extended_hi_load_conversion_is_source_frozen",
            "next_source_action": (
                "use_frozen_sparc_hi_gas_proxy_as_lower_bound_and_acquire_halo_capacity_or_extended_hi_conversion"
            ),
            "source_route_basis_artifacts": (
                "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json;"
                "tcdr_v4_ngc2841_surviving_route_ledger_summary_v0_1.json;"
                "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json"
            ),
            "diagnostic_result": (
                "frozen_sparc_hi_gas_proxy_outer_median_fraction_of_required_gap="
                f"{hi_gas_proxy['outer_median_gas_proxy_fraction_of_required_gap']:.6f};"
                "lower_bound_proxy_not_positive_dark_residual"
            ),
        },
        {
            "galaxy": "NGC2841",
            "route_id": "outer_xuv_hi_starforming_capacity",
            "route_class": "positive_outer_capacity_candidate",
            "source_basis": "GALEX/XUV and HI outer-disk structure around and beyond the optical disk",
            "source_status": "strong_source_side_candidate",
            "load_status": "candidate_needs_radial_xuv_hi_shape_and_load_conversion",
            "priority": "medium_secondary_positive_load_candidate",
            "allowed_use": "source_acquisition_worklist_for_outer_capacity_context",
            "blocked_use": "endpoint_scoring_until_radial_load_rule_is_source_frozen",
            "next_source_action": "acquire_radial_xuv_hi_support_profile_or_component_load_conversion",
            "source_route_basis_artifacts": "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json",
            "diagnostic_result": "context_candidate_not_yet_velocity_squared_load",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "diffuse_outer_envelope_capacity",
            "route_class": "positive_outer_capacity_context_candidate",
            "source_basis": "Dragonfly diffuse extended disk/envelope and outer stellar-gas context",
            "source_status": "source_side_context_candidate",
            "load_status": "candidate_needs_component_normalization_or_independent_table",
            "priority": "medium_secondary_positive_load_candidate",
            "allowed_use": "source_acquisition_worklist_for_diffuse_outer_component",
            "blocked_use": "load_formula_without_component_normalization",
            "next_source_action": "find_independent_outer_envelope_component_normalization_or_radial_table",
            "source_route_basis_artifacts": (
                "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json;"
                "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
            ),
            "diagnostic_result": "diffuse_shape_context_only_until_normalized",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "history_environment_outer_load",
            "route_class": "history_environment_context_candidate",
            "source_basis": "outer warp, line-of-nodes twist, infall/halo-shape context, vertical/path context",
            "source_status": "caveated_context_candidate",
            "load_status": "candidate_needs_residual_blind_environment_history_observable",
            "priority": "low_context_candidate",
            "allowed_use": "context_only_until_observable_is_source_native",
            "blocked_use": "endpoint_scoring_or_amplitude_rule",
            "next_source_action": "define_or_acquire_residual_blind_environment_history_observable",
            "source_route_basis_artifacts": "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json",
            "diagnostic_result": "context_only_not_load",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "tau_side_outer_capacity_load_theorem",
            "route_class": "theory_route",
            "source_basis": "Tau-side outer-capacity source theorem or velocity-squared readout derivation",
            "source_status": "theory_missing",
            "load_status": "candidate_needs_tau_side_derivation_to_velocity_squared_units",
            "priority": "medium_theory_candidate",
            "allowed_use": "theory_worklist_only",
            "blocked_use": "empirical_endpoint_kernel_without_source_derivation",
            "next_source_action": "derive_tau_side_outer_capacity_to_velocity_squared_units_or_keep_blocked",
            "source_route_basis_artifacts": "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json",
            "diagnostic_result": "required_scale_yardstick_only_not_source_label_or_kernel",
        },
    ]

    frame = pd.DataFrame(rows)
    frame["uses_endpoint_diagnostic_as_yardstick"] = "no"
    frame.loc[
        frame["route_id"] == "tau_side_outer_capacity_load_theorem",
        "uses_endpoint_diagnostic_as_yardstick",
    ] = "yes_not_for_label_or_kernel"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["uses_vobs_or_residual"] = "no"
    frame["forbidden_endpoint_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "primary_positive_load_candidates": ["outer_hi_warp_halo_capacity"],
        "secondary_positive_load_candidates": [
            "outer_xuv_hi_starforming_capacity",
            "diffuse_outer_envelope_capacity",
            "history_environment_outer_load",
            "tau_side_outer_capacity_load_theorem",
        ],
        "closed_control_routes": [
            "tilted_ring_projection_control",
            "known_integrated_outer_baryonic_ceiling",
            "dragonfly_mass_profile_shape",
        ],
        "endpoint_ready": False,
        "positive_load_ready": False,
        "projection_dominated_interpretation_supported": False,
        "outer_capacity_dominated_interpretation_supported": True,
        "sourced_hi_gas_proxy_frozen": True,
        "sourced_hi_gas_proxy_fraction_of_required_gap_median": (
            hi_gas_proxy["outer_median_gas_proxy_fraction_of_required_gap"]
        ),
        "sourced_hi_gas_proxy_fraction_of_required_gap_max": (
            hi_gas_proxy["outer_max_gas_proxy_fraction_of_required_gap"]
        ),
        "halo_capacity_or_extended_hi_load_still_missing": True,
        "required_equivalent_load_scale_msun_yardstick": (
            scale["outer_zone_median_required_equivalent_load_mass_after_ceiling_msun"]
        ),
        "required_scale_is_physical_mass_claim": False,
        "outer_zone_median_positive_v2_gap_after_ceiling_control": (
            scale["outer_zone_median_positive_v2_gap_after_ceiling_control"]
        ),
        "known_outer_baryon_ceiling_fraction_of_required": (
            scale["outer_zone_median_known_outer_baryon_ceiling_fraction_of_required"]
        ),
        "endpoint_replay_permission_counts": _permission_counts(frame, "endpoint_replay_permission"),
        "kernel_promotion_permission_counts": _permission_counts(frame, "kernel_promotion_permission"),
        "new_route_scoring_permission_counts": _permission_counts(frame, "new_route_scoring_permission"),
        "uses_vobs_or_residual_counts": _permission_counts(frame, "uses_vobs_or_residual"),
        "uses_endpoint_diagnostic_as_yardstick_counts": _permission_counts(
            frame, "uses_endpoint_diagnostic_as_yardstick"
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC2841 should be treated as positive outer-capacity dominated rather than "
            "projection-dominated. The projection route and the known integrated outer "
            "baryonic ceiling are valid controls, and the Dragonfly mass profile remains "
            "shape-only. A SPARC/THINGS gas proxy is now frozen as a lower-bound HI/gas "
            "shape component, but it supplies only a small fraction of the required outer "
            "positive-load scale. The primary source-side next route remains HI warp/halo "
            "capacity, now specifically requiring a halo-capacity or extended-HI load "
            "conversion before any scoring or kernel promotion."
        ),
        "next_allowed_action": (
            "Use the frozen SPARC/THINGS gas proxy as the lower-bound HI/gas component, "
            "then acquire or derive a source-native halo-capacity or extended-HI load "
            "conversion for NGC2841. Do not run endpoint scoring until that rule is frozen."
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_reaudit()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(frame[["route_id", "priority", "load_status", "allowed_use"]].to_string(index=False))


if __name__ == "__main__":
    main()
