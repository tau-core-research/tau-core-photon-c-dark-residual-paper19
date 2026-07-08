from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

REVIEW_ACCEPTANCE_SUMMARY = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json"
)
GEOMETRY_KERNEL_CSV = (
    SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_v0_1.csv"
)
GEOMETRY_KERNEL_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_v0_1.csv"
OUT_JSON = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_beta_closure_k_beta_profile_freeze_review_not_scoring"
K_BETA_ID = "K_BETA_NGC2841_PA_I_SOURCE_SHAPE_V0_1"
K_BETA_EXPRESSION = (
    "K_beta_shape(R)=minmax_0_1(K_geom_raw(R)); "
    "K_geom_raw=sqrt(((PA(R)-<PA>_R<=10)/DeltaPA_max)^2 + "
    "((i(R)-<i>_R<=10)/Deltai_max)^2)"
)
ENDPOINT_POLICY = "source_side_only_no_rotation_curve_residual_endpoint_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;panel_c_rotation_velocity;panel_d_surface_density"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _require_columns(frame: pd.DataFrame, columns: set[str], source: Path) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {source}: {sorted(missing)}")


def build_k_beta_profile_freeze_review() -> tuple[pd.DataFrame, dict[str, object]]:
    review = _load_json(REVIEW_ACCEPTANCE_SUMMARY)
    geometry_summary = _load_json(GEOMETRY_KERNEL_SUMMARY)

    if review.get("review_response_accepted") is not True:
        raise ValueError("Beta/closure reviewer response has not been accepted.")
    if review.get("K_beta_status") != "blocked_requires_source_native_radial_profile":
        raise ValueError("Unexpected K_beta status; this builder resolves only the radial-profile blocker.")
    if review.get("endpoint_ready") is not False or review.get("formula_freeze_ready") is not False:
        raise ValueError("Input review unexpectedly authorizes endpoint or formula freeze.")
    if geometry_summary.get("formula_freeze_review_ready") is not True:
        raise ValueError("Tilted-ring geometry profile is not ready for formula-freeze review.")
    if geometry_summary.get("endpoint_replay_allowed") is not False:
        raise ValueError("Geometry profile unexpectedly authorizes endpoint replay.")

    frame = pd.read_csv(GEOMETRY_KERNEL_CSV)
    _require_columns(
        frame,
        {
            "galaxy",
            "radius_kpc",
            "position_angle_deg",
            "inclination_deg",
            "source_reference",
            "source_panels_used",
            "source_panels_forbidden",
            "uses_vobs_or_residual",
            "endpoint_replay_permission",
            "kernel_promotion_permission",
            "new_route_scoring_permission",
            "k_tilted_ring_geometry_raw",
            "k_tilted_ring_geometry_0_1",
            "delta_pa_deg_from_inner_mean",
            "delta_inclination_deg_from_inner_mean",
        },
        GEOMETRY_KERNEL_CSV,
    )
    if set(frame["galaxy"].astype(str)) != {"NGC2841"}:
        raise ValueError("This builder is only valid for NGC2841.")
    for column in [
        "uses_vobs_or_residual",
        "endpoint_replay_permission",
        "kernel_promotion_permission",
        "new_route_scoring_permission",
    ]:
        if not (frame[column].astype(str) == "no").all():
            raise ValueError(f"Forbidden or scoring permission opened in {column}.")

    frame = frame.copy().sort_values("radius_kpc").reset_index(drop=True)
    for column in [
        "radius_kpc",
        "position_angle_deg",
        "inclination_deg",
        "delta_pa_deg_from_inner_mean",
        "delta_inclination_deg_from_inner_mean",
        "k_tilted_ring_geometry_raw",
    ]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    raw = frame["k_tilted_ring_geometry_raw"]
    raw_min = float(raw.min())
    raw_max = float(raw.max())
    if raw_max <= raw_min:
        raise ValueError("Cannot min-max normalize a degenerate K_beta raw shape.")

    frame["k_beta_shape_0_1"] = (raw - raw_min) / (raw_max - raw_min)
    frame["k_beta_shape_role"] = (
        "caveated_dimensionless_radial_shape_only_no_amplitude_no_sign_no_carrier"
    )
    frame["k_beta_id"] = K_BETA_ID
    frame["k_beta_expression"] = K_BETA_EXPRESSION
    frame["k_beta_source_basis"] = (
        "accepted_Bosma_Fig7a_PA_and_Fig7b_inclination_digitization_via_tilted_ring_geometry"
    )
    frame["k_beta_normalization_rule"] = (
        "minmax_0_1_over_reviewed_radius_grid_after_inner_orientation_contrast"
    )
    frame["k_beta_profile_status"] = "k_beta_shape_ready_for_formula_freeze_review_no_scoring"
    frame["source_profile_leakage_free"] = "yes"
    frame["resolved_blocker_id"] = "BETA_K_REQUIRES_SOURCE_NATIVE_RADIAL_PROFILE"
    frame["remaining_blockers"] = (
        "BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE;BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE"
    )
    frame["formula_freeze_ready"] = "no"
    frame["endpoint_ready"] = "no"
    frame["kernel_promotion_ready"] = "no"
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
        "galaxies": sorted(frame["galaxy"].astype(str).unique().tolist()),
        "k_beta_id": K_BETA_ID,
        "k_beta_expression": K_BETA_EXPRESSION,
        "k_beta_source_basis": (
            "accepted caveated Bosma Fig.7a PA and Fig.7b inclination digitization"
        ),
        "dimension_check": "pass_dimensionless_profile_from_normalized_pa_inclination_shape",
        "raw_shape_min": raw_min,
        "raw_shape_max": raw_max,
        "k_beta_min": float(frame["k_beta_shape_0_1"].min()),
        "k_beta_max": float(frame["k_beta_shape_0_1"].max()),
        "k_beta_outer_value": float(frame.iloc[-1]["k_beta_shape_0_1"]),
        "k_beta_monotonic_increasing": bool(frame["k_beta_shape_0_1"].is_monotonic_increasing),
        "K_beta_profile_ready_for_formula_freeze_review": True,
        "K_beta_kernel_promoted": False,
        "source_profile_leakage_free": True,
        "resolved_blocker_id": "BETA_K_REQUIRES_SOURCE_NATIVE_RADIAL_PROFILE",
        "resolved_blocker_status": "resolved_as_caveated_digitized_pa_inclination_profile_shape",
        "remaining_blockers": [
            "BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE",
            "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE",
        ],
        "full_formula_freeze_ready": False,
        "formula_freeze_ready": False,
        "endpoint_ready": False,
        "kernel_promotion_ready": False,
        "endpoint_replay_allowed": False,
        "new_route_scoring_allowed": False,
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
            "The accepted PA/inclination source profile closes only the K_beta radial-shape "
            "blocker for a later formula-freeze review. It does not freeze beta amplitude, "
            "spin normalization, sign, carrier, or any endpoint replay."
        ),
        "next_allowed_action": (
            "Resolve the carrier and spin-normalization blockers with residual-blind "
            "source-side artifacts before any beta/closure endpoint scoring."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_k_beta_profile_freeze_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "radius_kpc",
                "position_angle_deg",
                "inclination_deg",
                "k_beta_shape_0_1",
                "k_beta_profile_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
