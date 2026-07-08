from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

ACCEPTED_PROFILE = (
    SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance_v0_1.csv"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_tilted_ring_geometry_kernel_freeze_review_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
KERNEL_ID = "K_NGC2841_TILTED_RING_PA_I_SOURCE_REVIEW_V0_1"
KERNEL_EXPRESSION = (
    "K_geom(R)=normalize_0_1(sqrt(((PA(R)-<PA>_R<=10)/DeltaPA_max)^2 + "
    "((i(R)-<i>_R<=10)/Deltai_max)^2)); source-review geometry shape only"
)
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;panel_c_rotation_velocity;panel_d_surface_density"
)


def _require_columns(frame: pd.DataFrame, columns: set[str]) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in accepted profile: {sorted(missing)}")


def build_kernel_freeze_review() -> tuple[pd.DataFrame, dict[str, object]]:
    accepted = pd.read_csv(ACCEPTED_PROFILE)
    _require_columns(
        accepted,
        {
            "galaxy",
            "radius_kpc",
            "position_angle_deg",
            "inclination_deg",
            "profile_status",
            "uses_vobs_or_residual",
            "endpoint_replay_permission",
            "kernel_promotion_permission",
            "new_route_scoring_permission",
        },
    )

    if set(accepted["galaxy"].astype(str)) != {"NGC2841"}:
        raise ValueError("This builder is only valid for the accepted NGC2841 profile.")
    if not accepted["profile_status"].astype(str).str.startswith("accepted_caveated_source_side").all():
        raise ValueError("Profile is not accepted as caveated source-side input.")
    if not (accepted["uses_vobs_or_residual"].astype(str) == "no").all():
        raise ValueError("Accepted profile reports forbidden Vobs/residual use.")
    if not (accepted["endpoint_replay_permission"].astype(str) == "no").all():
        raise ValueError("Accepted profile unexpectedly authorizes endpoint replay.")
    if not (accepted["kernel_promotion_permission"].astype(str) == "no").all():
        raise ValueError("Accepted profile unexpectedly authorizes kernel promotion.")
    if not (accepted["new_route_scoring_permission"].astype(str) == "no").all():
        raise ValueError("Accepted profile unexpectedly authorizes new-route scoring.")

    frame = accepted.copy()
    for column in ["radius_kpc", "position_angle_deg", "inclination_deg"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame = frame.sort_values("radius_kpc").reset_index(drop=True)

    inner = frame[frame["radius_kpc"] <= 10.0]
    if inner.empty:
        raise ValueError("Need at least one inner R<=10 kpc row for source-side baseline.")

    pa0 = float(inner["position_angle_deg"].mean())
    inc0 = float(inner["inclination_deg"].mean())
    frame["delta_pa_deg_from_inner_mean"] = frame["position_angle_deg"] - pa0
    frame["delta_inclination_deg_from_inner_mean"] = frame["inclination_deg"] - inc0

    pa_norm = float(frame["delta_pa_deg_from_inner_mean"].abs().max())
    inc_norm = float(frame["delta_inclination_deg_from_inner_mean"].abs().max())
    if pa_norm <= 0 or inc_norm <= 0:
        raise ValueError("Cannot normalize a zero-span PA/inclination profile.")

    raw = (
        (frame["delta_pa_deg_from_inner_mean"] / pa_norm) ** 2
        + (frame["delta_inclination_deg_from_inner_mean"] / inc_norm) ** 2
    ).pow(0.5)
    raw_max = float(raw.max())
    if raw_max <= 0:
        raise ValueError("Cannot normalize zero raw geometry kernel.")

    frame["k_tilted_ring_geometry_raw"] = raw
    frame["k_tilted_ring_geometry_0_1"] = raw / raw_max
    frame["geometry_kernel_role"] = "source_side_shape_only_no_amplitude_no_sign_no_carrier"
    frame["kernel_id"] = KERNEL_ID
    frame["kernel_expression"] = KERNEL_EXPRESSION
    frame["baseline_rule"] = "inner_orientation_mean_over_R_le_10_kpc"
    frame["normalization_rule"] = "dimensionless_profile_normalized_to_unit_max_over_reviewed_radius_grid"
    frame["formula_freeze_review_status"] = "geometry_kernel_shape_review_ready_no_scoring"
    frame["formula_ready"] = "no"
    frame["formula_blockers"] = (
        "sign_rule_not_frozen;carrier_rule_not_frozen;amplitude_rule_not_frozen;"
        "endpoint_replay_authorization_missing"
    )
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    monotonic_kernel = bool(frame["k_tilted_ring_geometry_0_1"].is_monotonic_increasing)
    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].astype(str).unique().tolist()),
        "kernel_id": KERNEL_ID,
        "kernel_expression": KERNEL_EXPRESSION,
        "baseline_rule": "inner_orientation_mean_over_R_le_10_kpc",
        "inner_mean_position_angle_deg": pa0,
        "inner_mean_inclination_deg": inc0,
        "position_angle_normalization_delta_deg": pa_norm,
        "inclination_normalization_delta_deg": inc_norm,
        "kernel_min": float(frame["k_tilted_ring_geometry_0_1"].min()),
        "kernel_max": float(frame["k_tilted_ring_geometry_0_1"].max()),
        "kernel_outer_value": float(frame.iloc[-1]["k_tilted_ring_geometry_0_1"]),
        "kernel_monotonic_increasing": monotonic_kernel,
        "formula_freeze_review_status_counts": (
            frame["formula_freeze_review_status"].value_counts().sort_index().to_dict()
        ),
        "formula_ready_counts": frame["formula_ready"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": (
            frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "new_route_scoring_permission_counts": (
            frame["new_route_scoring_permission"].value_counts().sort_index().to_dict()
        ),
        "uses_vobs_or_residual_counts": (
            frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
        ),
        "dimension_check": "pass_dimensionless_kernel_from_degrees_normalized_by_degree_spans",
        "formula_ready": False,
        "formula_freeze_review_ready": True,
        "endpoint_replay_allowed": False,
        "kernel_promotion_allowed": False,
        "new_route_scoring_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The accepted NGC2841 reviewer PA/inclination profile now supports a "
            "caveated source-side tilted-ring geometry kernel shape. This freezes only "
            "the dimensionless radial shape for formula-freeze review. It does not "
            "freeze sign, amplitude, or carrier, and it does not authorize endpoint "
            "replay or kernel promotion."
        ),
        "next_allowed_action": (
            "source-review sign, carrier, and amplitude rules before any scoring script "
            "may read rotation data"
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_kernel_freeze_review()
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
                "k_tilted_ring_geometry_0_1",
                "formula_freeze_review_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
