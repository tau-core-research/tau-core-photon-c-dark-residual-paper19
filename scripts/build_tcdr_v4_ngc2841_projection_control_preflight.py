from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

LEDGER_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_surviving_route_ledger_summary_v0_1.json"
GEOMETRY_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json"
)
PROJECTION_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_projection_sign_load_derivation_summary_v0_1.json"
PROFILE_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_projection_control_preflight_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_projection_control_preflight_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_projection_control_preflight_not_endpoint_scoring"
ROUTE_ID = "tilted_ring_projection_control"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;positive_load_backsolve"
)
ENDPOINT_POLICY = "source_side_projection_control_preflight_only"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_preflight() -> tuple[pd.DataFrame, dict[str, object]]:
    ledger = _load_json(LEDGER_SUMMARY)
    geometry = _load_json(GEOMETRY_SUMMARY)
    projection = _load_json(PROJECTION_SUMMARY)
    profile = _load_json(PROFILE_SUMMARY)

    if ledger.get("preferred_next_route") != ROUTE_ID:
        raise ValueError("Surviving-route ledger does not select the tilted-ring projection control.")
    if ledger.get("positive_load_ready_route_count") != 0:
        raise ValueError("Projection-control preflight requires no positive-load-ready route.")
    if ledger.get("endpoint_ready_route_count") != 0:
        raise ValueError("Projection-control preflight cannot coexist with endpoint-ready routes.")
    if geometry.get("formula_freeze_review_ready") is not True:
        raise ValueError("Geometry kernel shape is not formula-freeze-review ready.")
    if geometry.get("formula_ready") is not False:
        raise ValueError("Geometry kernel must remain non-formula-ready.")
    if projection.get("derived_projection_sign") != "negative_multiplicative_attenuation":
        raise ValueError("Projection sign derivation did not yield the strict attenuation branch.")
    if projection.get("added_capacity_sign_status") != "not_derived_from_PA_i_alone":
        raise ValueError("Positive added-capacity branch was unexpectedly derived from PA/i alone.")
    if profile.get("profile_status") != "accepted_caveated_source_side_digitized_radial_pa_inclination_profile":
        raise ValueError("Accepted PA/inclination source profile is missing or not accepted.")

    rows = [
        {
            "galaxy": "NGC2841",
            "route_id": ROUTE_ID,
            "preflight_item": "route_selection",
            "status": "accepted_diagnostic_control_route",
            "source_basis": "surviving_route_ledger_preferred_next_route",
            "allowed_use": "projection_control_diagnostic_preflight_only",
            "blocked_use": "positive_dark_residual_endpoint_or_kernel_promotion",
            "value": str(ledger["preferred_next_route"]),
        },
        {
            "galaxy": "NGC2841",
            "route_id": ROUTE_ID,
            "preflight_item": "source_profile",
            "status": "accepted_caveated_pa_inclination_profile",
            "source_basis": "Bosma_Figure7_panels_a_b_reviewer_digitization",
            "allowed_use": "radial_projection_geometry_shape",
            "blocked_use": "velocity_squared_load_or_endpoint_label_rescue",
            "value": (
                f"R_range_kpc={profile['radius_range_kpc']};"
                f"i_range_deg={profile['inclination_range_deg']};"
                f"PA_range_deg={profile['position_angle_range_deg']}"
            ),
        },
        {
            "galaxy": "NGC2841",
            "route_id": ROUTE_ID,
            "preflight_item": "geometry_kernel_shape",
            "status": "source_side_shape_available_not_formula_ready",
            "source_basis": str(geometry["kernel_id"]),
            "allowed_use": "dimensionless_projection_control_shape",
            "blocked_use": "amplitude_sign_or_carrier_inference_from_endpoint",
            "value": (
                f"kernel_outer={geometry['kernel_outer_value']:.6f};"
                f"kernel_monotonic={geometry['kernel_monotonic_increasing']}"
            ),
        },
        {
            "galaxy": "NGC2841",
            "route_id": ROUTE_ID,
            "preflight_item": "projection_sign_and_cap",
            "status": "negative_multiplicative_projection_only",
            "source_basis": "v_los_equals_v_c_sin_i_identity_plus_source_i_profile",
            "allowed_use": "projection_deprojection_control_factor",
            "blocked_use": "positive_additive_dark_residual_load",
            "value": (
                f"outer_projection_factor={projection['outer_projection_factor']:.6f};"
                f"outer_gamma_i={projection['outer_gamma_i']:.6f};"
                f"gamma_i_max={projection['gamma_i_max']:.6f}"
            ),
        },
        {
            "galaxy": "NGC2841",
            "route_id": ROUTE_ID,
            "preflight_item": "endpoint_boundary",
            "status": "diagnostic_only_separate_authorization_required_for_any_replay",
            "source_basis": "all_upstream_artifacts_keep_endpoint_permissions_closed",
            "allowed_use": "write_preflight_and_optional_future_projection_control_replay_request",
            "blocked_use": "endpoint_scoring_or_claim_of_improved_rotation_fit_from_this_preflight",
            "value": "endpoint_replay_permission=no;diagnostic_replay_permission=separate_authorization_required",
        },
    ]

    frame = pd.DataFrame(rows)
    frame["projection_control_preflight_ready"] = "yes"
    frame["diagnostic_only"] = "yes"
    frame["positive_load_ready"] = "no"
    frame["endpoint_ready"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["diagnostic_replay_permission"] = "separate_authorization_required"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["uses_vobs_or_residual"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "route_id": ROUTE_ID,
        "preferred_next_route": ledger["preferred_next_route"],
        "projection_control_preflight_ready": True,
        "diagnostic_only": True,
        "positive_load_ready": False,
        "endpoint_ready": False,
        "endpoint_replay_allowed": False,
        "diagnostic_replay_permission": "separate_authorization_required",
        "kernel_promotion_allowed": False,
        "new_route_scoring_allowed": False,
        "uses_vobs_or_residual_counts": (
            frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
        ),
        "endpoint_replay_permission_counts": (
            frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "new_route_scoring_permission_counts": (
            frame["new_route_scoring_permission"].value_counts().sort_index().to_dict()
        ),
        "outer_projection_factor": projection["outer_projection_factor"],
        "outer_gamma_i": projection["outer_gamma_i"],
        "gamma_i_max": projection["gamma_i_max"],
        "geometry_kernel_id": geometry["kernel_id"],
        "source_profile_status": profile["profile_status"],
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC2841 has one clean near-term route: a tilted-ring projection-control "
            "preflight. The route is source-side and leakage-clean, and the strict "
            "projection identity fixes a negative multiplicative attenuation. It is "
            "not a positive dark-residual load, not endpoint scoring, and not kernel "
            "promotion."
        ),
        "next_allowed_action": (
            "If the user requests a replay, build a separate diagnostic-only projection "
            "control replay that reads this frozen preflight unchanged. Do not use that "
            "replay to promote a positive outer-capacity branch."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_preflight()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "preflight_item",
                "status",
                "allowed_use",
                "blocked_use",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
