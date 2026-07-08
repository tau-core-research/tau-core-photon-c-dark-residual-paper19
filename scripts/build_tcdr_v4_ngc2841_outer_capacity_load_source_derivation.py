from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

SOURCE_SEARCH = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_source_search_v0_1.csv"
POLICY_FREEZE = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_policy_freeze_v0_1.csv"
PROJECTION_DERIVATION = SOURCE_DIR / "tcdr_v4_ngc2841_projection_sign_load_derivation_v0_1.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_derivation_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_derivation_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_outer_capacity_load_source_derivation_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _load_frame(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    frame = pd.read_csv(path)
    forbidden_cols = {"Vobs", "vobs", "rotation_residual", "delta_v2", "rmse", "score"}
    overlap = forbidden_cols.intersection(frame.columns)
    if overlap:
        raise ValueError(f"{label} contains forbidden endpoint columns: {sorted(overlap)}")
    return frame


def build_load_source_derivation() -> tuple[pd.DataFrame, dict[str, object]]:
    source_search = _load_frame(SOURCE_SEARCH, "outer-capacity source search")
    policy_freeze = _load_frame(POLICY_FREEZE, "outer-capacity policy freeze")
    projection = _load_frame(PROJECTION_DERIVATION, "projection sign/load derivation")

    strong_routes = sorted(
        source_search[source_search["source_status"].astype(str).str.startswith("STRONG")][
            "source_route"
        ].tolist()
    )
    policy_ids = sorted(policy_freeze["policy_id"].astype(str).tolist())
    positive_branch = projection[
        projection["derived_item"].astype(str) == "positive_outer_capacity_branch"
    ]
    if positive_branch.empty:
        raise ValueError("Projection derivation is missing the positive branch blocker row.")
    if (
        "uses_vobs_or_residual" in projection
        and set(projection["uses_vobs_or_residual"].astype(str)) != {"no"}
    ):
        raise ValueError("Projection derivation reports forbidden endpoint input use.")

    rows = [
        {
            "galaxy": "NGC2841",
            "load_channel": "strict_projection_control",
            "source_basis": "accepted_radial_PA_inclination_geometry",
            "source_status": "derived_source_side_projection_factor",
            "formula_shell": (
                "v_proj^2(R)=v_carrier^2(R)*(sin(i_ref)/sin(i(R)))^2"
            ),
            "sign_status": "negative_multiplicative_attenuation_derived",
            "load_status": "source_fixed_dimensionless_projection_factor_no_lambda",
            "velocity_squared_load_available": "no_free_load_needed_for_projection_control",
            "formula_readiness": "projection_control_ready_not_added_capacity",
            "formula_use_permission": "projection_control_only_no_endpoint",
            "source_references": "Bosma1981NGC2841HI;deBlok2008THINGS;Samurovic2015NGC2841",
            "derivation_note": (
                "Inclination geometry supplies a dimensionless deprojection factor. "
                "It attenuates or rescales a carrier but does not create an additive "
                "outer dark-residual load."
            ),
        },
        {
            "galaxy": "NGC2841",
            "load_channel": "extended_stellar_hi_uv_capacity",
            "source_basis": "Dragonfly outer stellar disk plus HI/UV support",
            "source_status": "route_presence_and_support_extent_source_supported",
            "formula_shell": "v_readout^2(R)=v_carrier^2(R)+lambda_ext*K_ext(R)",
            "sign_status": "positive_additive_sign_not_source_forced",
            "load_status": "blocked_missing_velocity_squared_conversion",
            "velocity_squared_load_available": "no",
            "formula_readiness": "blocked_load_missing",
            "formula_use_permission": "no_added_capacity_not_frozen",
            "source_references": "Zhang2018NGC2841Dragonfly",
            "derivation_note": (
                "The source supports an outer capacity route and approximate radial "
                "support, but the manifest does not contain a residual-blind mapping "
                "from stellar/HI/UV surface-density evidence to a velocity-squared "
                "load lambda_ext."
            ),
        },
        {
            "galaxy": "NGC2841",
            "load_channel": "warped_hi_tilted_ring_capacity",
            "source_basis": "extended HI warp and tilted-ring geometry",
            "source_status": "geometry_shape_partly_ready_load_missing",
            "formula_shell": "v_readout^2(R)=v_carrier^2(R)+lambda_warp*K_geom(R)",
            "sign_status": "positive_additive_sign_not_source_forced",
            "load_status": "blocked_geometry_is_not_load",
            "velocity_squared_load_available": "no",
            "formula_readiness": "blocked_load_missing",
            "formula_use_permission": "no_added_capacity_not_frozen",
            "source_references": "Bosma1981NGC2841HI;deBlok2008THINGS;Samurovic2015NGC2841",
            "derivation_note": (
                "The PA/inclination route can determine a geometry kernel and a "
                "projection-control sign. It cannot by itself determine the positive "
                "velocity-squared amplitude lambda_warp."
            ),
        },
        {
            "galaxy": "NGC2841",
            "load_channel": "xuv_hi_outer_starforming_capacity",
            "source_basis": "GALEX/XUV outer disk and HI star-forming support",
            "source_status": "route_presence_source_supported_shape_and_load_missing",
            "formula_shell": "v_readout^2(R)=v_carrier^2(R)+lambda_xuv*K_xuv(R)",
            "sign_status": "positive_additive_sign_not_source_forced",
            "load_status": "blocked_missing_shape_and_velocity_squared_conversion",
            "velocity_squared_load_available": "no",
            "formula_readiness": "blocked_shape_and_load_missing",
            "formula_use_permission": "no_added_capacity_not_frozen",
            "source_references": "Thilker2007XUVDisks",
            "derivation_note": (
                "The lower-bound XUV extent supports the route but cannot be used as "
                "an exact kernel shape or as a velocity-squared load."
            ),
        },
        {
            "galaxy": "NGC2841",
            "load_channel": "composite_positive_outer_capacity",
            "source_basis": ";".join(strong_routes),
            "source_status": "support_routes_and_weights_present_load_missing",
            "formula_shell": (
                "v_readout^2(R)=v_carrier^2(R)+lambda_outer*"
                "[w_ext*K_ext+w_warp*K_geom+w_xuv*K_xuv]"
            ),
            "sign_status": "positive_additive_sign_requires_independent_load_rule",
            "load_status": "blocked_missing_independent_velocity_squared_load",
            "velocity_squared_load_available": "no",
            "formula_readiness": "not_formula_ready",
            "formula_use_permission": "no_endpoint_no_kernel_promotion",
            "source_references": ";".join(policy_ids),
            "derivation_note": (
                "The source-search and policy-freeze artifacts close route presence, "
                "onset priority, and equal strong-route weights. They do not close "
                "the load problem: lambda_outer still needs a source-native "
                "velocity-squared conversion, a predeclared train-only amplitude rule, "
                "or a theory-side load theorem."
            ),
        },
    ]

    frame = pd.DataFrame(rows)
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["uses_vobs_or_residual"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "strong_source_routes_inherited": strong_routes,
        "policy_ids_inherited": policy_ids,
        "projection_control_ready": True,
        "positive_added_capacity_load_ready": False,
        "positive_added_capacity_formula_ready": False,
        "load_blocker": "missing_independent_velocity_squared_load",
        "formula_readiness_counts": frame["formula_readiness"].value_counts().sort_index().to_dict(),
        "load_status_counts": frame["load_status"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC2841 now has a source-side projection-control derivation and a "
            "source-supported composite outer-capacity route, but the positive "
            "added dark-residual branch remains blocked. Geometry, route support, "
            "radial support, and component weights do not by themselves supply the "
            "velocity-squared load required by lambda K(R)."
        ),
        "next_allowed_action": (
            "freeze one independent load route before scoring: either a source-native "
            "stellar/HI/XUV mass or surface-density conversion to velocity-squared "
            "units, a residual-blind train-only amplitude rule, or a Tau-side "
            "outer-capacity load theorem. Until then, only the projection-control "
            "branch may be used as a non-endpoint diagnostic/control."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_load_source_derivation()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "load_channel",
                "source_status",
                "load_status",
                "formula_readiness",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
