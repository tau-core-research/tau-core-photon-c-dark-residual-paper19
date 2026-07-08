from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_tilted_ring_geometry_source_review_not_formula_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
NED_BOSMA_URL = "https://ned.ipac.caltech.edu/level5/March05/Bosma/Bosma4_6.html"


ROWS = [
    {
        "galaxy": "NGC2841",
        "geometry_item": "outer_hi_orientation_change",
        "source_status": "accepted_qualitative_geometry_source",
        "source_statement": (
            "The outer HI structure has a sky orientation different from the main "
            "body, and the kinematical major axis changes position angle in the "
            "outer parts."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": NED_BOSMA_URL,
        "source_location": "NED/Bosma section 3b-3c, lines describing HI orientation and velocity-field PA change",
        "formula_implication": "geometry_bearing_outer_hi_route_supported",
        "formula_freeze_status": "support_only_numeric_profile_still_blocked",
    },
    {
        "galaxy": "NGC2841",
        "geometry_item": "channel_map_bend_radius",
        "source_status": "accepted_qualitative_geometry_source",
        "source_statement": (
            "Extreme-velocity channel maps show a bend beyond about 6 arcmin from "
            "the centre, instead of remaining on the optical major-axis line."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": NED_BOSMA_URL,
        "source_location": "NED/Bosma section 3b, channel-map discussion",
        "formula_implication": "outer_geometry_onset_crosscheck_only",
        "formula_freeze_status": "support_only_numeric_profile_still_blocked",
    },
    {
        "galaxy": "NGC2841",
        "geometry_item": "annular_tilted_ring_model",
        "source_status": "accepted_model_geometry_source",
        "source_statement": (
            "Bosma constructs a descriptive warp model by dividing the galaxy into "
            "concentric annuli, each allowed to have its own sky orientation."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": NED_BOSMA_URL,
        "source_location": "NED/Bosma section 4a, warp model",
        "formula_implication": "tilted_ring_profile_exists_in_source_model",
        "formula_freeze_status": "numeric_profile_requires_digitization_or_table",
    },
    {
        "galaxy": "NGC2841",
        "geometry_item": "outer_inclination_adjustment",
        "source_status": "accepted_caveated_geometry_source",
        "source_statement": (
            "At high inclination the minimum-dispersion fit is not satisfactory; "
            "increasing the inclination of the outer annuli improves resemblance "
            "to the observed HI distribution and velocity field."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": NED_BOSMA_URL,
        "source_location": "NED/Bosma section 4a, high-inclination discussion",
        "formula_implication": "outer_inclination_profile_is_caveated_not_simple_scalar",
        "formula_freeze_status": "numeric_profile_requires_digitization_or_table",
    },
    {
        "galaxy": "NGC2841",
        "geometry_item": "figure7_profile_availability",
        "source_status": "figure_only_profile_available",
        "source_statement": (
            "Figure 7 contains radial distributions of position angle, inclination, "
            "rotation velocity, and surface densities. The NED HTML page exposes "
            "the profile as an image, not as a machine-readable table."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": NED_BOSMA_URL,
        "source_location": "NED/Bosma Figure 7 caption",
        "formula_implication": "exact_profile_blocked_until_residual_blind_digitization",
        "formula_freeze_status": "blocked_needs_source_side_digitization_or_native_table",
    },
    {
        "galaxy": "NGC2841",
        "geometry_item": "asymmetry_not_explained_by_tilted_ring",
        "source_status": "accepted_geometry_caveat",
        "source_statement": (
            "The tilted-ring model gives good agreement with observations but does "
            "not explain the north-south asymmetry of the HI distribution."
        ),
        "source_reference": "Bosma1981NGC2841HI",
        "source_url": NED_BOSMA_URL,
        "source_location": "NED/Bosma section 4a, model agreement caveat",
        "formula_implication": "tilted_ring_route_not_complete_morphology",
        "formula_freeze_status": "caveat_only_no_profile_freeze",
    },
]


def build_review() -> tuple[pd.DataFrame, dict[str, object]]:
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
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "source_status_counts": frame["source_status"].value_counts().to_dict(),
        "formula_freeze_status_counts": frame["formula_freeze_status"].value_counts().to_dict(),
        "geometry_route_supported": True,
        "exact_tilted_ring_numeric_profile_frozen": False,
        "digitization_or_native_table_required": True,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().to_dict(),
        "forbidden_endpoint_inputs_used_counts": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Bosma/NED source text strongly supports a geometry-bearing warped-HI "
            "tilted-ring route for NGC2841, including an outer PA/orientation change "
            "and an annular tilted-ring model. It does not yet freeze an exact numeric "
            "PA/inclination profile because the available source profile is figure-only "
            "in the HTML representation. Formula freeze and endpoint replay remain closed."
        ),
        "next_allowed_action": (
            "perform residual-blind digitization of Bosma Figure 7 or locate a "
            "source-native PA/inclination table; otherwise build only a scalar "
            "outer-capacity support shell with the geometry subchannel disabled"
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "geometry_item",
                "source_status",
                "formula_freeze_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
