from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

GEOM_KERNEL = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_v0_1.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_projection_sign_load_derivation_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_projection_sign_load_derivation_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_projection_sign_load_derivation_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;panel_c_rotation_velocity;panel_d_surface_density"
)


def _sin2_factor(i_ref_deg: float, i_deg: float) -> float:
    return (math.sin(math.radians(i_ref_deg)) / math.sin(math.radians(i_deg))) ** 2


def build_derivation() -> tuple[pd.DataFrame, dict[str, object]]:
    kernel = pd.read_csv(GEOM_KERNEL).sort_values("radius_kpc").reset_index(drop=True)
    if set(kernel["uses_vobs_or_residual"].astype(str)) != {"no"}:
        raise ValueError("Geometry kernel reports forbidden endpoint input use.")
    if set(kernel["formula_ready"].astype(str)) != {"no"}:
        raise ValueError("Geometry kernel should not already be formula-ready.")

    for column in ["radius_kpc", "inclination_deg", "position_angle_deg"]:
        kernel[column] = pd.to_numeric(kernel[column], errors="raise")

    inner = kernel[kernel["radius_kpc"] <= 10.0]
    i_ref = float(inner["inclination_deg"].mean())
    pa_ref = float(inner["position_angle_deg"].mean())

    kernel["projection_factor_sin2_i_ref_over_i"] = kernel["inclination_deg"].map(
        lambda i: _sin2_factor(i_ref, float(i))
    )
    kernel["projection_attenuation_gamma_i"] = (
        1.0 - kernel["projection_factor_sin2_i_ref_over_i"]
    )
    gamma_max = float(kernel["projection_attenuation_gamma_i"].max())
    gamma_min = float(kernel["projection_attenuation_gamma_i"].min())
    if gamma_max <= 0:
        raise ValueError("Projection attenuation is not positive for this inclination profile.")
    kernel["k_inclination_projection_0_1"] = kernel["projection_attenuation_gamma_i"] / gamma_max

    rows = [
        {
            "galaxy": "NGC2841",
            "derived_item": "projection_deprojection_identity",
            "status": "derived_from_tilted_ring_inclination_geometry",
            "formula": (
                "v_los(R)=v_c(R) sin i(R); if the carrier is referenced to "
                "i_ref=<i>_{R<=10}, then v_proj^2(R)=v_carrier^2(R)"
                "*(sin(i_ref)/sin(i(R)))^2"
            ),
            "source_value": f"i_ref_deg={i_ref:.6f}",
            "dimension_check": "pass_dimensionless_sine_ratio_multiplies_velocity_squared",
            "sign_result": "negative_multiplicative_projection_attenuation",
            "load_result": "source_fixed_gamma_i_of_R_no_free_velocity_scale",
            "formula_use_permission": "yes_projection_branch_shape_and_sign_only_no_endpoint",
        },
        {
            "galaxy": "NGC2841",
            "derived_item": "projection_gamma_cap",
            "status": "computed_from_source_side_inclination_profile",
            "formula": "gamma_i(R)=1-(sin(i_ref)/sin(i(R)))^2; gamma_i_max=max_R gamma_i(R)",
            "source_value": f"gamma_i_max={gamma_max:.6f}",
            "dimension_check": "pass_dimensionless",
            "sign_result": "attenuation_cap_not_additive_boost",
            "load_result": "no_train_or_endpoint_amplitude",
            "formula_use_permission": "yes_projection_branch_gamma_cap_no_endpoint",
        },
        {
            "galaxy": "NGC2841",
            "derived_item": "position_angle_role",
            "status": "context_shape_only",
            "formula": "PA(R)-<PA>_{R<=10} marks ring-orientation change but does not set a 1D velocity amplitude",
            "source_value": f"pa_ref_deg={pa_ref:.6f}",
            "dimension_check": "pass_angle_context_only",
            "sign_result": "no_unique_sign_from_PA_alone",
            "load_result": "no_velocity_squared_load_from_PA_alone",
            "formula_use_permission": "context_only_no_endpoint",
        },
        {
            "galaxy": "NGC2841",
            "derived_item": "positive_outer_capacity_branch",
            "status": "not_derived_from_PA_i_profile_alone",
            "formula": "v_readout^2(R)=v_carrier^2(R)+lambda K_geom(R) requires lambda with velocity^2 units",
            "source_value": "lambda_pending_source_native_load_or_external_frozen_train_rule",
            "dimension_check": "blocked_missing_velocity_squared_load",
            "sign_result": "positive_additive_sign_not_forced_by_PA_i",
            "load_result": "blocked",
            "formula_use_permission": "no_added_capacity_not_frozen",
        },
    ]
    out = pd.DataFrame(rows)
    out["endpoint_replay_permission"] = "no"
    out["kernel_promotion_permission"] = "no"
    out["new_route_scoring_permission"] = "no"
    out["forbidden_inputs"] = FORBIDDEN_INPUTS
    out["endpoint_data_policy"] = ENDPOINT_POLICY
    out["claim_boundary"] = CLAIM_BOUNDARY

    profile_columns = [
        "radius_kpc",
        "inclination_deg",
        "projection_factor_sin2_i_ref_over_i",
        "projection_attenuation_gamma_i",
        "k_inclination_projection_0_1",
    ]
    profile = kernel[profile_columns].copy()
    profile["galaxy"] = "NGC2841"
    profile["derived_item"] = "projection_profile_row"
    profile["status"] = "source_side_projection_profile_no_endpoint"
    profile["formula"] = "v_proj^2/v_carrier^2=(sin(i_ref)/sin(i(R)))^2"
    profile["source_value"] = profile.apply(
        lambda row: (
            f"R_kpc={row['radius_kpc']:.3f};i_deg={row['inclination_deg']:.3f};"
            f"P_i={row['projection_factor_sin2_i_ref_over_i']:.6f};"
            f"gamma_i={row['projection_attenuation_gamma_i']:.6f}"
        ),
        axis=1,
    )
    profile["dimension_check"] = "pass_dimensionless"
    profile["sign_result"] = "negative_multiplicative_projection_attenuation"
    profile["load_result"] = "source_fixed_projection_factor_no_free_amplitude"
    profile["formula_use_permission"] = "projection_profile_support_no_endpoint"
    profile["endpoint_replay_permission"] = "no"
    profile["kernel_promotion_permission"] = "no"
    profile["new_route_scoring_permission"] = "no"
    profile["forbidden_inputs"] = FORBIDDEN_INPUTS
    profile["endpoint_data_policy"] = ENDPOINT_POLICY
    profile["claim_boundary"] = CLAIM_BOUNDARY

    combined = pd.concat([out, profile[out.columns]], ignore_index=True)
    summary = {
        "n_rows": int(len(combined)),
        "n_derivation_rows": int(len(out)),
        "n_projection_profile_rows": int(len(profile)),
        "galaxies": ["NGC2841"],
        "i_ref_deg": i_ref,
        "pa_ref_deg": pa_ref,
        "projection_factor_min": float(kernel["projection_factor_sin2_i_ref_over_i"].min()),
        "projection_factor_max": float(kernel["projection_factor_sin2_i_ref_over_i"].max()),
        "gamma_i_min": gamma_min,
        "gamma_i_max": gamma_max,
        "outer_projection_factor": float(kernel.iloc[-1]["projection_factor_sin2_i_ref_over_i"]),
        "outer_gamma_i": float(kernel.iloc[-1]["projection_attenuation_gamma_i"]),
        "derived_projection_sign": "negative_multiplicative_attenuation",
        "added_capacity_sign_status": "not_derived_from_PA_i_alone",
        "amplitude_load_status": "projection_factor_source_fixed;added_capacity_load_blocked",
        "endpoint_replay_permission_counts": (
            combined["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            combined["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "new_route_scoring_permission_counts": (
            combined["new_route_scoring_permission"].value_counts().sort_index().to_dict()
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The PA/inclination profile does derive a strict projection/deprojection "
            "branch: increasing inclination relative to the inner reference produces a "
            "negative multiplicative attenuation with no fitted amplitude. It does not "
            "derive the positive added outer-capacity branch, because that would require "
            "a velocity-squared load not contained in the PA/i profile."
        ),
        "caveat": (
            "Because the inner reference is an average over R<=10 kpc, a few inner rows "
            "can have a projection factor slightly above unity. This is retained as a "
            "digitization/reference caveat rather than clipped."
        ),
        "next_allowed_action": (
            "Either freeze the projection-only attenuation branch as a non-endpoint "
            "control, or source-review an independent outer-capacity load for the "
            "positive added branch before scoring."
        ),
    }
    return combined, summary


def main() -> None:
    frame, summary = build_derivation()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(frame[["derived_item", "status", "sign_result", "load_result"]].to_string(index=False))


if __name__ == "__main__":
    main()
