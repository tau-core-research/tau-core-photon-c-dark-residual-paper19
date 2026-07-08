from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_source_native_pa_inclination_table_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_source_native_pa_inclination_table_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_source_native_pa_inclination_table_not_radial_formula_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"

DEBLOK_ARXIV = "https://arxiv.org/abs/0810.2100"
DEBLOK_DOI = "https://doi.org/10.1088/0004-6256/136/6/2648"
SAMUROVIC_DOI = "https://doi.org/10.1093/mnras/stv1226"
BOSMA_NED = "https://ned.ipac.caltech.edu/level5/March05/Bosma/Bosma4_6.html"


ROWS = [
    {
        "galaxy": "NGC2841",
        "source_id": "DEBLOK2008_THINGS_TABLE1_GLOBAL_INCLINATION",
        "source_type": "published_source_native_global_inclination_table",
        "quantity_scope": "global_indicative_hi_and_optical_inclination",
        "radius_scope": "global",
        "position_angle_deg": "",
        "inclination_deg": 69.0,
        "inclination_leda_deg": 61.0,
        "distance_mpc": "",
        "ring_sampling_arcsec": "",
        "systemic_velocity_kms": "",
        "source_method": (
            "THINGS indicative H I inclination from ellipse fits to outer H I maps; "
            "LEDA optical inclination listed as comparison."
        ),
        "source_reference": "deBlok2008THINGS",
        "source_url": DEBLOK_ARXIV,
        "source_location": "Table 1, indicative global inclinations; NGC 2841 row",
        "profile_level": "scalar_global_not_radial_profile",
        "formula_use_permission": "support_context_only_no_formula_freeze",
        "caveat": "indicative global inclination; no PA and no radial tilted-ring profile in this row",
    },
    {
        "galaxy": "NGC2841",
        "source_id": "DEBLOK2008_THINGS_TABLE2_TILTED_RING_MEAN_PA_INCLINATION",
        "source_type": "published_source_native_tilted_ring_parameter_table",
        "quantity_scope": "average_tilted_ring_model_pa_inclination",
        "radius_scope": "radially_averaged_model_summary",
        "position_angle_deg": 152.6,
        "inclination_deg": 73.7,
        "inclination_leda_deg": "",
        "distance_mpc": 14.1,
        "ring_sampling_arcsec": 5.0,
        "systemic_velocity_kms": 633.7,
        "source_method": (
            "THINGS GIPSY ROTCUR tilted-ring analysis; Table 2 reports average "
            "inclination and receding-side PA for the adopted tilted-ring model."
        ),
        "source_reference": "deBlok2008THINGS",
        "source_url": DEBLOK_DOI,
        "source_location": "Table 2, tilted-ring model parameters; NGC 2841 row",
        "profile_level": "source_native_scalar_tilted_ring_summary_not_radial_profile",
        "formula_use_permission": "scalar_geometry_support_only_no_radial_kernel_freeze",
        "caveat": (
            "PA/inclination are averaged tilted-ring model parameters derived from "
            "H I velocity-field fitting; useful as source-native geometry support, "
            "but insufficient for an outer radial PA/i kernel."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "SAMUROVIC2015_MEDIAN_ROTCUR_PA_INCLINATION",
        "source_type": "published_source_native_median_pa_inclination_statement",
        "quantity_scope": "median_radial_pa_inclination_from_rotcur_free_pa_i_run",
        "radius_scope": "median_of_radial_profile",
        "position_angle_deg": 150.7,
        "inclination_deg": 73.5,
        "inclination_leda_deg": "",
        "distance_mpc": "",
        "ring_sampling_arcsec": 5.0,
        "systemic_velocity_kms": 633.8,
        "source_method": (
            "GIPSY ROTCUR applied to THINGS naturally weighted velocity map; "
            "PA and inclination radial distributions were smoothed and summarized "
            "by median values for gas-surface-density extraction."
        ),
        "source_reference": "Samurovic2015NGC2841",
        "source_url": SAMUROVIC_DOI,
        "source_location": "Section 2.3 and 2.4, radio observations and gas component",
        "profile_level": "source_native_median_summary_not_radial_profile",
        "formula_use_permission": "scalar_geometry_crosscheck_only_no_radial_kernel_freeze",
        "caveat": (
            "Median PA/i confirms the de Blok mean geometry scale, but the actual "
            "radial PA/i profile remains figure-level in the article and is not "
            "used here as a numeric formula input."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "BOSMA1981_FIGURE7_PA_INCLINATION_PROFILE",
        "source_type": "published_figure_radial_profile_not_machine_readable_table",
        "quantity_scope": "radial_pa_inclination_profile_from_figure",
        "radius_scope": "radial_figure_profile",
        "position_angle_deg": "",
        "inclination_deg": "",
        "inclination_leda_deg": "",
        "distance_mpc": "",
        "ring_sampling_arcsec": "",
        "systemic_velocity_kms": "",
        "source_method": (
            "Bosma warp model uses concentric annuli; the PA and inclination profile "
            "is exposed as Figure 7 panels a and b in the NED-hosted representation."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": BOSMA_NED,
        "source_location": "Figure 7 panels a and b; section 4a warp model",
        "profile_level": "radial_profile_available_as_figure_only",
        "formula_use_permission": "review_candidate_only_requires_digitization_or_native_table",
        "caveat": (
            "This is the only route that exposes radial PA/i shape in the current "
            "source set, but it is not a source-native numeric table. The companion "
            "digitized-profile artifact remains review-only."
        ),
    },
]


def build_table() -> tuple[pd.DataFrame, dict[str, object]]:
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

    numeric_pa = pd.to_numeric(frame["position_angle_deg"], errors="coerce").dropna()
    numeric_i = pd.to_numeric(frame["inclination_deg"], errors="coerce").dropna()

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "source_ids": frame["source_id"].tolist(),
        "source_type_counts": frame["source_type"].value_counts().to_dict(),
        "profile_level_counts": frame["profile_level"].value_counts().to_dict(),
        "formula_use_permission_counts": frame["formula_use_permission"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().to_dict(),
        "forbidden_endpoint_inputs_used_counts": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "has_source_native_numeric_pa_inclination_scalar": True,
        "has_source_native_numeric_radial_pa_inclination_table": False,
        "has_published_figure_radial_pa_inclination_profile": True,
        "mean_source_native_pa_deg": float(numeric_pa.mean()),
        "mean_source_native_inclination_deg": float(numeric_i.mean()),
        "position_angle_deg_values": numeric_pa.astype(float).tolist(),
        "inclination_deg_values": numeric_i.astype(float).tolist(),
        "formula_ready": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The primary-source pass found source-native numeric PA/inclination "
            "summaries for NGC2841: de Blok et al. THINGS Table 2 gives "
            "<PA>=152.6 deg and <i>=73.7 deg, and Samurovic et al. give median "
            "PA=150.7 deg and i=73.5 deg. These values validate the scalar geometry "
            "scale of the tilted-ring route. They do not close the radial-profile "
            "blocker: the available radial PA/i shape remains Bosma figure-only or "
            "article-figure-level, not a source-native numeric radial table."
        ),
        "next_allowed_action": (
            "Use the scalar PA/i rows only as source-native geometry support and "
            "crosscheck; keep endpoint scoring closed until an independently reviewed "
            "digitized radial profile or a source-native radial PA/i table is available."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_table()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "source_id",
                "position_angle_deg",
                "inclination_deg",
                "profile_level",
                "formula_use_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
