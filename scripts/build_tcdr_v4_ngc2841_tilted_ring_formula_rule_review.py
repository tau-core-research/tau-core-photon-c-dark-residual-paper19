from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

GEOM_KERNEL = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_v0_1.csv"
GEOM_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_formula_rule_review_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_formula_rule_review_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_tilted_ring_formula_rule_review_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;panel_c_rotation_velocity;panel_d_surface_density"
)


def build_rule_review() -> tuple[pd.DataFrame, dict[str, object]]:
    kernel = pd.read_csv(GEOM_KERNEL)
    summary = json.loads(GEOM_SUMMARY.read_text(encoding="utf-8"))
    if summary["claim_boundary"] != "ngc2841_tilted_ring_geometry_kernel_freeze_review_not_scoring":
        raise ValueError("Unexpected geometry-kernel claim boundary.")
    if summary["formula_ready"] is not False:
        raise ValueError("Geometry kernel should not already be formula-ready.")
    if set(kernel["uses_vobs_or_residual"].astype(str)) != {"no"}:
        raise ValueError("Geometry kernel reports forbidden endpoint input use.")

    rows = [
        {
            "galaxy": "NGC2841",
            "rule_item": "geometry_kernel_shape",
            "rule_status": "frozen_for_formula_review_shape_only",
            "candidate_value": summary["kernel_id"],
            "rule_expression": summary["kernel_expression"],
            "source_basis": (
                "Accepted reviewer digitization of Bosma Figure 7 panels a/b only; "
                "dimensionless PA/inclination displacement from inner orientation mean."
            ),
            "why_not_final_formula": (
                "Shape has no velocity units and carries no sign, carrier, or amplitude."
            ),
            "allowed_formula_use": "yes_shape_only_formula_review_no_scoring",
        },
        {
            "galaxy": "NGC2841",
            "rule_item": "sign_rule",
            "rule_status": "blocked_two_branch_source_interpretation",
            "candidate_value": "projection_attenuation_or_outer_capacity_addition",
            "rule_expression": (
                "Branch A: v_readout^2=v_carrier^2*(1-gamma*K_geom); "
                "Branch B: v_readout^2=v_carrier^2+lambda*K_geom"
            ),
            "source_basis": (
                "The source shows a tilted-ring orientation change, but the PA/i profile "
                "alone does not determine whether the 4D readout should be treated as a "
                "projection/deprojection correction or as an added outer-capacity lane."
            ),
            "why_not_final_formula": (
                "Choosing the sign from the observed rotation residual would be leakage. "
                "A source-side or theory-side sign rule is still required."
            ),
            "allowed_formula_use": "no_sign_not_frozen",
        },
        {
            "galaxy": "NGC2841",
            "rule_item": "carrier_rule",
            "rule_status": "candidate_inherit_fixed_baryonic_carrier_policy",
            "candidate_value": "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_target_fit",
            "rule_expression": "v_carrier^2=v_baryonic_fixed_mlr^2",
            "source_basis": (
                "This is the existing TCDR-v4 preflight carrier convention used for "
                "baseline bookkeeping; it is not selected by NGC2841 residual quality."
            ),
            "why_not_final_formula": (
                "Carrier inheritance can be reviewable, but final replay still requires "
                "a sign rule and amplitude/load rule."
            ),
            "allowed_formula_use": "candidate_carrier_review_no_scoring",
        },
        {
            "galaxy": "NGC2841",
            "rule_item": "amplitude_or_load_rule",
            "rule_status": "blocked_no_source_native_load_rule",
            "candidate_value": "pending",
            "rule_expression": (
                "Need gamma or lambda from source-side geometry/load proxy, frozen "
                "external train rule, or explicit reviewer-authorized stress carrier."
            ),
            "source_basis": (
                "The accepted PA/i profile supplies radial shape only. It does not supply "
                "a physical load scale or velocity-squared amplitude."
            ),
            "why_not_final_formula": (
                "Fitting the amplitude on NGC2841 or choosing it to close the v^2 gap "
                "would be endpoint rescue."
            ),
            "allowed_formula_use": "no_amplitude_not_frozen",
        },
        {
            "galaxy": "NGC2841",
            "rule_item": "endpoint_authorization",
            "rule_status": "blocked_until_formula_rules_frozen",
            "candidate_value": "no",
            "rule_expression": "endpoint scoring script may read Vobs only after frozen sign/carrier/amplitude manifest",
            "source_basis": "Formula rule review, not scoring authorization.",
            "why_not_final_formula": "A shape kernel plus unresolved sign/load is not an endpoint formula.",
            "allowed_formula_use": "no_endpoint_replay",
        },
    ]
    frame = pd.DataFrame(rows)
    frame["kernel_id"] = summary["kernel_id"]
    frame["formula_ready"] = "no"
    frame["formula_freeze_review_ready"] = frame["rule_status"].isin(
        {
            "frozen_for_formula_review_shape_only",
            "candidate_inherit_fixed_baryonic_carrier_policy",
        }
    ).map({True: "yes_caveated", False: "no_blocked"})
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    blocked = int(frame["rule_status"].str.startswith("blocked").sum())
    complete_formula_ready = blocked == 0
    out_summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "kernel_id": summary["kernel_id"],
        "rule_status_counts": frame["rule_status"].value_counts().sort_index().to_dict(),
        "allowed_formula_use_counts": frame["allowed_formula_use"].value_counts().sort_index().to_dict(),
        "formula_ready_counts": frame["formula_ready"].value_counts().sort_index().to_dict(),
        "formula_freeze_review_ready_counts": (
            frame["formula_freeze_review_ready"].value_counts().sort_index().to_dict()
        ),
        "blocked_rule_items": sorted(
            frame[frame["rule_status"].str.startswith("blocked")]["rule_item"].tolist()
        ),
        "candidate_review_rule_items": sorted(
            frame[frame["rule_status"].str.startswith("candidate")]["rule_item"].tolist()
        ),
        "frozen_review_rule_items": sorted(
            frame[frame["rule_status"].str.startswith("frozen")]["rule_item"].tolist()
        ),
        "formula_ready": bool(complete_formula_ready),
        "endpoint_replay_allowed": False,
        "kernel_promotion_allowed": False,
        "new_route_scoring_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The accepted NGC2841 geometry kernel supplies a source-side shape and a "
            "reviewable fixed-baryonic carrier candidate. It does not yet supply a "
            "single sign rule or an amplitude/load rule. Endpoint replay remains "
            "blocked; the next finite task is a source/theory-side sign-and-load "
            "review, not scoring."
        ),
        "next_allowed_action": (
            "build a reviewer authorization package for the sign rule and load rule, "
            "or derive them from a declared Tau Core outer-capacity principle"
        ),
    }
    return frame, out_summary


def main() -> None:
    frame, summary = build_rule_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(frame[["rule_item", "rule_status", "allowed_formula_use"]].to_string(index=False))


if __name__ == "__main__":
    main()
