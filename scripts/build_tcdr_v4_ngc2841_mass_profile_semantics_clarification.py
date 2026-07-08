from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

NORMALIZATION_AUDIT = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_normalization_audit_v0_1.csv"
NORMALIZATION_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_normalization_audit_summary_v0_1.json"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_clarification_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_clarification_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_semantics_clarification_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def build_clarification() -> tuple[pd.DataFrame, dict[str, object]]:
    if not NORMALIZATION_AUDIT.exists() or not NORMALIZATION_SUMMARY.exists():
        raise FileNotFoundError("Run mass-profile normalization audit first.")
    audit = pd.read_csv(NORMALIZATION_AUDIT)
    summary_in = json.loads(NORMALIZATION_SUMMARY.read_text(encoding="utf-8"))
    if summary_in.get("normalization_blocked") is not True:
        raise ValueError("Semantics clarification is only needed for blocked normalization.")

    ratios = {
        str(row["profile_variant"]): float(row["naive_to_reference_ratio"])
        for _, row in audit.iterrows()
    }
    min_ratio = min(ratios.values())

    rows = [
        {
            "galaxy": "NGC2841",
            "clarification_item": "hard_conflict_observed",
            "status": "confirmed_source_side_blocker",
            "evidence": (
                "The filled response is leakage-free, but naive annular integration of "
                "the digitized outer profile is tens of times larger than the quoted "
                "Zhang et al. outer-disk stellar mass."
            ),
            "quantitative_check": (
                f"measured_color_ratio={ratios.get('measured_color', float('nan')):.3f};"
                f"constant_outer_color_ratio={ratios.get('constant_outer_color', float('nan')):.3f}"
            ),
            "allowed_resolution": "none_without_source_semantics_review",
            "endpoint_relevance": "blocks_load_promotion",
        },
        {
            "galaxy": "NGC2841",
            "clarification_item": "component_semantics_hypothesis",
            "status": "plausible_not_resolved",
            "evidence": (
                "The quoted outer stellar mass may refer to an isolated outer-disk "
                "component or model residual, while the digitized curve may trace a "
                "displayed total/profile-level surface-density curve."
            ),
            "quantitative_check": "would_explain_large_integral_if_curve_is_not_isolated_outer_component",
            "allowed_resolution": "source_author_table_or_reviewer_component_semantics_note",
            "endpoint_relevance": "profile_shape_only_until_resolved",
        },
        {
            "galaxy": "NGC2841",
            "clarification_item": "area_geometry_hypothesis",
            "status": "insufficient_by_itself",
            "evidence": (
                "Inclination, elliptical annulus, or projection-area conventions can "
                "change the integral by order-unity factors, but not by the observed "
                "tens-of-times discrepancy."
            ),
            "quantitative_check": f"minimum_observed_ratio_to_quote={min_ratio:.3f}",
            "allowed_resolution": "do_not_fix_by_area_factor_alone",
            "endpoint_relevance": "cannot_supply_lambda",
        },
        {
            "galaxy": "NGC2841",
            "clarification_item": "digitization_axis_or_curve_identity_hypothesis",
            "status": "possible_requires_reviewer_followup",
            "evidence": (
                "The figure has multiple blue/profile variants, shaded constant-colour "
                "regions, error bars, and a red ratio axis. A curve-identity or axis "
                "misread can only be resolved by a focused reviewer response."
            ),
            "quantitative_check": "current_response_kept_as_caveated",
            "allowed_resolution": "request_reviewer_to_confirm_curve_identity_and_axis_mapping",
            "endpoint_relevance": "shape_candidate_not_load",
        },
        {
            "galaxy": "NGC2841",
            "clarification_item": "claim_safe_verdict",
            "status": "load_formula_blocked",
            "evidence": (
                "The source-side response is useful as a morphology/load-shape clue, but "
                "not as a normalized velocity-squared load."
            ),
            "quantitative_check": "formula_ready=false;endpoint_replay_permission=no",
            "allowed_resolution": (
                "Either obtain a source-native table/component model from the source, "
                "or freeze a separate train-only amplitude rule before scoring."
            ),
            "endpoint_relevance": "no_endpoint_replay",
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

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "normalization_blocked": True,
        "minimum_naive_to_reference_ratio": min_ratio,
        "clarification_status_counts": frame["status"].value_counts().sort_index().to_dict(),
        "formula_ready": False,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The mismatch is now localized: the issue is not endpoint leakage, but "
            "source-profile semantics. The digitized mass profile should be treated as "
            "a shape candidate only until its component identity and normalization are "
            "resolved against the quoted outer-disk stellar mass."
        ),
        "next_allowed_action": (
            "Ask for a reviewer follow-up on curve identity/axis mapping, or locate a "
            "source-native table/model for the isolated outer-disk component."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_clarification()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
