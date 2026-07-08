from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_surviving_route_ledger_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_surviving_route_ledger_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_surviving_route_ledger_not_scoring"
ENDPOINT_POLICY = "source_side_route_triage_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _load_summary(name: str) -> dict[str, object]:
    path = SOURCE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required NGC2841 summary: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_ledger() -> tuple[pd.DataFrame, dict[str, object]]:
    mass_accept = _load_summary(
        "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
    )
    projection = _load_summary("tcdr_v4_ngc2841_projection_sign_load_derivation_summary_v0_1.json")
    geom_kernel = _load_summary(
        "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json"
    )
    formula_rule = _load_summary("tcdr_v4_ngc2841_tilted_ring_formula_rule_review_summary_v0_1.json")
    outer_search = _load_summary("tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json")
    load_derivation = _load_summary(
        "tcdr_v4_ngc2841_outer_capacity_load_source_derivation_summary_v0_1.json"
    )
    policy = _load_summary("tcdr_v4_ngc2841_outer_capacity_policy_freeze_summary_v0_1.json")
    load_search = _load_summary("tcdr_v4_ngc2841_outer_capacity_load_source_search_summary_v0_1.json")

    rows = [
        {
            "galaxy": "NGC2841",
            "route_id": "dragonfly_mass_profile_load",
            "route_family": "stellar_gas_mass_profile",
            "source_basis": "Zhang2018 Dragonfly mass-profile figure and integrated outer stellar mass",
            "shape_status": "accepted_shape_candidate",
            "load_status": "blocked_no_source_native_normalization",
            "formula_status": "not_formula_ready",
            "endpoint_status": "closed",
            "allowed_use": "shape_context_only",
            "evidence_artifacts": (
                "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
            ),
            "route_verdict": mass_accept["final_status"],
            "next_allowed_action": mass_accept["next_allowed_action"],
            "survival_class": "closed_as_load_route_preserve_shape",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "tilted_ring_projection_control",
            "route_family": "observer_projection_geometry",
            "source_basis": "Bosma PA/inclination digitization plus source-side projection derivation",
            "shape_status": "geometry_shape_frozen_for_formula_review",
            "load_status": "projection_attenuation_only_no_positive_load",
            "formula_status": "projection_control_derivable_not_added_load",
            "endpoint_status": "closed_but_diagnostic_control_candidate",
            "allowed_use": "non_endpoint_projection_control_or_diagnostic_preflight",
            "evidence_artifacts": (
                "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json;"
                "tcdr_v4_ngc2841_projection_sign_load_derivation_summary_v0_1.json"
            ),
            "route_verdict": projection["verdict"],
            "next_allowed_action": projection["next_allowed_action"],
            "survival_class": "survives_as_projection_control_not_positive_dark_residual",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "tilted_ring_positive_outer_capacity",
            "route_family": "warped_hi_tilted_ring_outer_capacity",
            "source_basis": "Bosma/NED tilted-ring support and accepted PA/inclination shape",
            "shape_status": "accepted_geometry_shape",
            "load_status": "blocked_missing_velocity_squared_load",
            "formula_status": "not_formula_ready_sign_and_load_blocked",
            "endpoint_status": "closed",
            "allowed_use": "source_side_geometry_shape_only",
            "evidence_artifacts": (
                "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json;"
                "tcdr_v4_ngc2841_tilted_ring_formula_rule_review_summary_v0_1.json"
            ),
            "route_verdict": formula_rule["verdict"],
            "next_allowed_action": formula_rule["next_allowed_action"],
            "survival_class": "survives_as_shape_route_load_blocked",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "composite_outer_morphology",
            "route_family": "extended_stellar_hi_uv_warp_xuv_composite",
            "source_basis": "Dragonfly extended disk, warped HI tilted-ring structure, XUV/HI outer disk",
            "shape_status": "source_supported_composite_shape",
            "load_status": "blocked_missing_independent_positive_load",
            "formula_status": "not_formula_ready",
            "endpoint_status": "closed",
            "allowed_use": "source_side_route_context_and_worklist_only",
            "evidence_artifacts": (
                "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json;"
                "tcdr_v4_ngc2841_outer_capacity_policy_freeze_summary_v0_1.json;"
                "tcdr_v4_ngc2841_outer_capacity_load_source_derivation_summary_v0_1.json"
            ),
            "route_verdict": load_derivation["verdict"],
            "next_allowed_action": load_derivation["next_allowed_action"],
            "survival_class": "survives_as_composite_source_route_load_blocked",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "dragonfly_integrated_outer_baryonic_ceiling",
            "route_family": "baryonic_ceiling_control",
            "source_basis": "Zhang2018 integrated outer stellar mass and 3:1 stellar/gas ratio",
            "shape_status": "not_radial_shape",
            "load_status": "usable_only_as_small_baryonic_ceiling_control",
            "formula_status": "control_only_not_dark_residual_formula",
            "endpoint_status": "closed",
            "allowed_use": "non_endpoint_baryonic_ceiling_control",
            "evidence_artifacts": "tcdr_v4_ngc2841_outer_capacity_load_source_search_summary_v0_1.json",
            "route_verdict": load_search["verdict"],
            "next_allowed_action": load_search["next_allowed_action"],
            "survival_class": "survives_as_negative_capacity_control",
        },
        {
            "galaxy": "NGC2841",
            "route_id": "xuv_hi_outer_disk_shape",
            "route_family": "xuv_hi_outer_star_formation_context",
            "source_basis": "outer UV/HI structure and route support from source-search ledger",
            "shape_status": "source_supported_context_only",
            "load_status": "blocked_no_radial_shape_or_load_rule",
            "formula_status": "not_formula_ready",
            "endpoint_status": "closed",
            "allowed_use": "source_side_context_only",
            "evidence_artifacts": "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json",
            "route_verdict": outer_search["verdict"],
            "next_allowed_action": policy["next_allowed_action"],
            "survival_class": "survives_as_context_needs_radial_shape_and_load",
        },
    ]

    frame = pd.DataFrame(rows)
    frame["uses_vobs_or_residual"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    shape_ready = frame["shape_status"].str.contains("accepted|frozen|supported", regex=True)
    load_ready = frame["load_status"].str.contains("ready|usable", regex=True) & ~frame[
        "load_status"
    ].str.contains("blocked|control|only", regex=True)
    endpoint_ready = frame["endpoint_status"].eq("open")

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "survival_class_counts": frame["survival_class"].value_counts().sort_index().to_dict(),
        "shape_ready_route_count": int(shape_ready.sum()),
        "positive_load_ready_route_count": int(load_ready.sum()),
        "endpoint_ready_route_count": int(endpoint_ready.sum()),
        "closed_route_count": int((frame["endpoint_status"] == "closed").sum()),
        "diagnostic_control_candidate_routes": frame.loc[
            frame["endpoint_status"].str.contains("diagnostic", regex=False), "route_id"
        ].tolist(),
        "preferred_next_route": "tilted_ring_projection_control",
        "preferred_next_action": (
            "If a replay is needed, run only a projection-control diagnostic/preflight. "
            "Do not reopen positive outer-capacity scoring until an independent "
            "velocity-squared load source is frozen."
        ),
        "formula_ready": False,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC2841 has several surviving source-side shape routes, but no positive "
            "outer-capacity load route is formula-ready. The Dragonfly mass profile is "
            "closed as a load route and preserved as shape-only. The only clean near-term "
            "replay direction is a projection-control diagnostic; a positive dark-residual "
            "endpoint remains blocked by missing independent velocity-squared load evidence."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_ledger()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(frame[["route_id", "survival_class", "allowed_use"]].to_string(index=False))


if __name__ == "__main__":
    main()
