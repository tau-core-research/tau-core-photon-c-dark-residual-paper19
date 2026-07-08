from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

OUT_CSV = OUT_DIR / "tcdr_v4_ngc2841_outer_capacity_source_search_v0_1.csv"
OUT_JSON = OUT_DIR / "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_outer_capacity_source_search_not_formula_not_scoring"


SOURCE_ROWS = [
    {
        "galaxy": "NGC2841",
        "source_id": "dragonfly_extended_stellar_hi_uv_disk",
        "source_status": "STRONG_OUTER_CAPACITY_SOURCE_CANDIDATE",
        "source_route": "outer_stellar_hi_uv_capacity",
        "source_observables": (
            "stellar_disk_traced_to_about_70_kpc;"
            "outer_disk_traces_HI_and_extended_UV;"
            "stellar_to_gas_surface_density_ratio_about_3_to_1_beyond_about_20_kpc;"
            "low_surface_brightness_stellar_disk_begins_to_warp_beyond_about_30_kpc"
        ),
        "source_reference": "Zhang2018NGC2841Dragonfly",
        "source_url": "https://doi.org/10.3847/1538-4357/aaac81",
        "numeric_formula_freeze_use": "candidate_after_source_review",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "notes": (
            "Strong residual-blind evidence that the missing NGC2841 capacity is not "
            "captured by a short spiral/path shell alone; the outer disk has stellar, "
            "gas, UV, and warp structure at the relevant radii."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "bosma_extended_hi_warp_tilted_ring",
        "source_status": "STRONG_OUTER_PATH_HALO_SOURCE_CANDIDATE",
        "source_route": "outer_hi_warp_halo_capacity",
        "source_observables": (
            "HI_extent_about_2p5_Holmberg_diameters;"
            "outer_HI_disk_not_coplanar_with_optical_disk;"
            "tilted_ring_warp_model;"
            "flat_rotation_about_280_km_s_to_about_36_kpc;"
            "outer_mass_to_light_ratio_increases"
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": "https://ned.ipac.caltech.edu/level5/March05/Bosma/Bosma4_6.html",
        "numeric_formula_freeze_use": "candidate_after_source_review",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "notes": (
            "Strong source-side route for an outer path/halo-capacity shell. The tilted-ring "
            "geometry and extended HI are independent of this paper's endpoint residual."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "galex_xuv_hi_outer_star_formation",
        "source_status": "STRONG_XUV_HI_OUTER_CAPACITY_SOURCE_CANDIDATE",
        "source_route": "outer_xuv_hi_starforming_capacity",
        "source_observables": (
            "nearly_continuous_outer_spiral_arms_outside_inner_disk;"
            "XUV_complexes_to_at_least_4D25_along_major_axis;"
            "ongoing_star_formation_throughout_HI_distribution;"
            "ringlike_outer_HI_or_XUV_structure_just_outside_optical_disk"
        ),
        "source_reference": "Thilker2007XUVDisks",
        "source_url": "https://arxiv.org/abs/0712.3555",
        "numeric_formula_freeze_use": "candidate_after_source_review",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "notes": (
            "Strong source-side evidence for outer-disk capacity tied to the HI/XUV body, "
            "not to the inner optical spiral description alone."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "cosmic_infall_outer_lon_twist",
        "source_status": "CAVEATED_OUTER_HALO_SHAPE_SOURCE_CANDIDATE",
        "source_route": "outer_halo_shape_or_infall_path_context",
        "source_observables": (
            "weak_signs_of_outer_line_of_nodes_spirality_twist;"
            "outer_HI_morphology_may_trace_outer_halo_shape_or_profile"
        ),
        "source_reference": "ShenSellwood2006WarpInfall",
        "source_url": "https://arxiv.org/abs/astro-ph/0604529",
        "numeric_formula_freeze_use": "review_context_only",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "notes": (
            "Useful but caveated path-context evidence. It should not by itself close the "
            "formula-freeze route."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "radio_continuum_hourglass_and_hi_warp",
        "source_status": "CAVEATED_VERTICAL_PATH_SOURCE_CANDIDATE",
        "source_route": "vertical_path_or_outflow_context",
        "source_observables": (
            "diffuse_hourglass_radio_structure;"
            "possible_minor_axis_bipolar_outflow;"
            "HI_extends_beyond_stellar_disk_with_different_position_angle"
        ),
        "source_reference": "Braun2007WesterborkSINGS",
        "source_url": "https://arxiv.org/abs/astro-ph/0610114",
        "numeric_formula_freeze_use": "review_context_only",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "notes": (
            "Caveated vertical/path context. It can help decide whether the future route "
            "needs vertical-path terms, but not endpoint scoring permission."
        ),
    },
    {
        "galaxy": "NGC2841",
        "source_id": "chandra_hot_gas_halo",
        "source_status": "CAVEATED_HOT_GAS_PATH_CONTEXT",
        "source_route": "hot_gas_halo_path_context",
        "source_observables": (
            "multimillion_degree_gas_rising_above_disk;"
            "hot_gas_shells_or_bubbles_contribute_to_gaseous_halo_context"
        ),
        "source_reference": "Chandra2006NGC2841",
        "source_url": "https://chandra.harvard.edu/photo/2006/n2841/",
        "numeric_formula_freeze_use": "review_context_only",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "notes": (
            "Context for a path-environment layer only. It is not a source-native rotation "
            "kernel and does not repair the NGC2841 curve."
        ),
    },
]


def build_source_search() -> tuple[pd.DataFrame, dict[str, object]]:
    rows = []
    for row in SOURCE_ROWS:
        rows.append(
            {
                **row,
                "forbidden_endpoint_inputs_used": "no",
                "uses_vobs_or_residual": "no",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    frame = pd.DataFrame(rows)
    strong = frame[frame["source_status"].str.startswith("STRONG")]
    summary = {
        "n_rows": int(len(frame)),
        "n_strong_source_candidates": int(len(strong)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "source_status_counts": frame["source_status"].value_counts().to_dict(),
        "source_route_counts": frame["source_route"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "forbidden_endpoint_inputs_used_counts": frame["forbidden_endpoint_inputs_used"].value_counts().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Independent source-side literature does identify plausible outer-capacity "
            "routes for NGC2841. The strongest route is composite: extended stellar/HI/UV "
            "outer disk plus warped HI tilted-ring geometry plus XUV/HI outer star "
            "formation. This closes a source-search blocker only; it does not authorize "
            "endpoint replay or kernel promotion."
        ),
        "next_allowed_action": (
            "build a residual-blind outer-capacity formula-freeze worklist using only "
            "source-native fields such as outer onset radius, outer extent, HI extent, "
            "XUV extent, warp/tilted-ring geometry, and caveated vertical/path flags"
        ),
    }
    return frame, summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_source_search()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "source_id",
                "source_status",
                "source_route",
                "endpoint_replay_permission",
                "kernel_promotion_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
