from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_radial_pa_inclination_table_search_audit_not_formula_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


ROWS = [
    {
        "search_target": "source_native_numeric_radial_pa_inclination_table",
        "source_checked": "Bosma1981NGC2841HI_NED",
        "source_url": "https://ned.ipac.caltech.edu/level5/March05/Bosma/Bosma4_6.html",
        "source_status": "radial_profile_figure_available_no_numeric_table_in_html",
        "evidence": (
            "NED/Bosma exposes Figure 7 with radial distributions of position angle "
            "and inclination, but the local representation is an image rather than a "
            "machine-readable numeric PA/i table."
        ),
        "usable_now": "review_digitization_candidate_only",
        "formula_freeze_impact": "radial_kernel_still_blocked",
    },
    {
        "search_target": "source_native_numeric_radial_pa_inclination_table",
        "source_checked": "deBlok2008THINGS_Table1_Table2",
        "source_url": "https://arxiv.org/abs/0810.2100",
        "source_status": "scalar_pa_inclination_support_found_no_radial_table",
        "evidence": (
            "Table 1 gives indicative global H I/optical inclinations; Table 2 gives "
            "average tilted-ring PA and inclination for NGC2841. The arXiv source "
            "contains figures but no extracted radial PA/i numeric table."
        ),
        "usable_now": "scalar_geometry_support_only",
        "formula_freeze_impact": "supports_geometry_scale_does_not_freeze_radial_kernel",
    },
    {
        "search_target": "source_native_numeric_radial_pa_inclination_table",
        "source_checked": "Samurovic2015NGC2841",
        "source_url": "https://doi.org/10.1093/mnras/stv1226",
        "source_status": "median_pa_inclination_support_found_radial_profile_figure_level",
        "evidence": (
            "The article states that PA and inclination radial profiles are shown in "
            "Figure 4 panels c and d, and gives/uses median PA/i values. No source-native "
            "numeric radial PA/i table was located in this bounded pass."
        ),
        "usable_now": "scalar_geometry_crosscheck_only",
        "formula_freeze_impact": "supports_deblok_scale_does_not_freeze_radial_kernel",
    },
    {
        "search_target": "source_native_numeric_radial_pa_inclination_table",
        "source_checked": "general_web_primary_source_pass",
        "source_url": "search_queries_recorded_in_script",
        "source_status": "no_primary_machine_readable_radial_pa_i_table_found",
        "evidence": (
            "Targeted searches for NGC2841 tilted-ring PA/inclination table, THINGS "
            "ROTCUR PA/i, and radial PA/i table returned figure-level profiles, scalar "
            "summaries, or unrelated material, not a primary numeric radial PA/i table."
        ),
        "usable_now": "negative_source_search_result",
        "formula_freeze_impact": "keep_endpoint_and_kernel_promotion_closed",
    },
]

SEARCH_QUERIES = [
    "NGC 2841 tilted ring position angle inclination table",
    "NGC2841 PA inclination tilted ring table",
    "NGC 2841 THINGS tilted ring model inclination position angle",
    "NGC2841 rotcur PA incl table",
    "\"NGC 2841\" \"position angle\" \"inclination\" \"radial\" \"table\"",
    "\"NGC 2841\" \"PA\" \"inclination\" \"Table\" \"rotcur\"",
]


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    frame = pd.DataFrame(ROWS)
    frame["forbidden_inputs"] = (
        "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;required_epsilon_fit"
    )
    frame["uses_vobs_or_residual"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "search_queries": SEARCH_QUERIES,
        "source_status_counts": frame["source_status"].value_counts().to_dict(),
        "usable_now_counts": frame["usable_now"].value_counts().to_dict(),
        "has_source_native_numeric_radial_pa_inclination_table": False,
        "has_source_native_numeric_scalar_pa_inclination_support": True,
        "has_figure_level_radial_pa_inclination_profile": True,
        "radial_kernel_formula_ready": False,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().to_dict(),
        "forbidden_endpoint_inputs_used_counts": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "A bounded primary-source pass did not locate a source-native numeric "
            "radial PA/inclination table for NGC2841. It did locate scalar/summary "
            "PA/inclination support from THINGS/de Blok and Samurovic, and figure-level "
            "radial PA/i profiles from Bosma and Samurovic. Therefore the route is "
            "better supported, but the radial tilted-ring kernel remains blocked."
        ),
        "next_allowed_action": (
            "Either obtain author/archive machine-readable tilted-ring PA/i values or "
            "run an independent reviewer digitization of the Bosma/Samurovic PA/i panels. "
            "Do not score or promote the kernel before that source-side step."
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
                "source_checked",
                "source_status",
                "usable_now",
                "formula_freeze_impact",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
