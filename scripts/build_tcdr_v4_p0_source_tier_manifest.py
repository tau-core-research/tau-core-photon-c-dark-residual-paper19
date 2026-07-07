from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

NAME_LOOKUP = OUT_DIR / "tcdr_v4_p0_s4g_lookup_v0_1.csv"
COORD_LOOKUP = OUT_DIR / "tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv"
SIMBAD_FALLBACK = OUT_DIR / "tcdr_v4_p0_simbad_fallback_lookup_v0_1.csv"


def _blank_to_empty(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def build_source_tier_manifest() -> tuple[pd.DataFrame, dict[str, int]]:
    name_lookup = pd.read_csv(NAME_LOOKUP)
    coord_lookup = pd.read_csv(COORD_LOOKUP)
    simbad = pd.read_csv(SIMBAD_FALLBACK)
    coord_by_galaxy = {row["galaxy"]: row for _, row in coord_lookup.iterrows()}
    simbad_by_galaxy = {row["galaxy"]: row for _, row in simbad.iterrows()}

    rows = []
    for _, row in name_lookup.iterrows():
        galaxy = row["galaxy"]
        if row["s4g_lookup_status"] == "matched_by_name":
            source_tier = "S4G_STRONG"
            source_tier_rank = 1
            source_catalog = "S4G_IRSA_s4gcat"
            source_match_method = "catalogue_name"
            morphology_type = _blank_to_empty(row["s4g_type"])
            source_object = _blank_to_empty(row["matched_s4g_object"])
            source_bibcode = ""
            homogeneous_structural_morphology = "yes"
            source_tier_caveat = "strongest_current_tier_homogeneous_s4g_catalogue_match"
        elif galaxy in coord_by_galaxy and coord_by_galaxy[galaxy]["coordinate_lookup_status"] == "matched_by_coordinate":
            coord = coord_by_galaxy[galaxy]
            source_tier = "S4G_COORD_RESCUE"
            source_tier_rank = 2
            source_catalog = "S4G_IRSA_s4gcat_plus_SIMBAD_coordinates"
            source_match_method = "simbad_coordinate_crossmatch_1_arcmin"
            morphology_type = _blank_to_empty(coord["s4g_type"])
            source_object = _blank_to_empty(coord["nearest_s4g_object"])
            source_bibcode = ""
            homogeneous_structural_morphology = "yes"
            source_tier_caveat = "s4g_structural_fields_available_but_identity_requires_coordinate_alias_rescue"
        elif galaxy in simbad_by_galaxy and simbad_by_galaxy[galaxy]["simbad_lookup_status"] == "resolved_with_morphology":
            fallback = simbad_by_galaxy[galaxy]
            source_tier = "SIMBAD_FALLBACK"
            source_tier_rank = 3
            source_catalog = "SIMBAD_basic_morphtype"
            source_match_method = "simbad_name_resolution"
            morphology_type = _blank_to_empty(fallback["simbad_morph_type"])
            source_object = _blank_to_empty(fallback["simbad_main_id"])
            source_bibcode = _blank_to_empty(fallback["simbad_morph_bibcode"])
            homogeneous_structural_morphology = "no"
            source_tier_caveat = "catalogue_type_fallback_not_homogeneous_s4g_structural_morphology"
        elif galaxy in simbad_by_galaxy and simbad_by_galaxy[galaxy]["simbad_lookup_status"] == "resolved_without_morphology":
            fallback = simbad_by_galaxy[galaxy]
            source_tier = "SIMBAD_IDENTITY_ONLY"
            source_tier_rank = 4
            source_catalog = "SIMBAD_basic_identity"
            source_match_method = "simbad_name_resolution"
            morphology_type = ""
            source_object = _blank_to_empty(fallback["simbad_main_id"])
            source_bibcode = ""
            homogeneous_structural_morphology = "no"
            source_tier_caveat = "identity_resolved_but_no_source_side_morphology_type_available"
        else:
            source_tier = "SOURCE_UNRESOLVED"
            source_tier_rank = 9
            source_catalog = ""
            source_match_method = ""
            morphology_type = ""
            source_object = ""
            source_bibcode = ""
            homogeneous_structural_morphology = "no"
            source_tier_caveat = "no_allowed_source_side_morphology_route_currently_available"

        rows.append(
            {
                "galaxy": galaxy,
                "source_tier": source_tier,
                "source_tier_rank": source_tier_rank,
                "source_catalog": source_catalog,
                "source_match_method": source_match_method,
                "source_object": source_object,
                "morphology_type": morphology_type,
                "source_bibcode": source_bibcode,
                "homogeneous_structural_morphology": homogeneous_structural_morphology,
                "source_tier_caveat": source_tier_caveat,
                "source_freeze_policy": "source_tier_may_be_frozen_before_endpoint_scoring",
                "endpoint_data_policy": "do_not_use_rotation_residuals_for_source_tier",
            }
        )

    detail = pd.DataFrame(rows).sort_values(["source_tier_rank", "galaxy"]).reset_index(drop=True)
    counts = detail["source_tier"].value_counts().to_dict()
    summary = {
        "n_p0_objects": int(len(detail)),
        "n_s4g_strong": int(counts.get("S4G_STRONG", 0)),
        "n_s4g_coord_rescue": int(counts.get("S4G_COORD_RESCUE", 0)),
        "n_simbad_fallback": int(counts.get("SIMBAD_FALLBACK", 0)),
        "n_simbad_identity_only": int(counts.get("SIMBAD_IDENTITY_ONLY", 0)),
        "n_source_unresolved": int(counts.get("SOURCE_UNRESOLVED", 0)),
        "n_homogeneous_s4g_structural": int((detail["homogeneous_structural_morphology"] == "yes").sum()),
        "n_any_source_side_morphology_type": int((detail["morphology_type"] != "").sum()),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_source_tier_manifest()
    detail_out = OUT_DIR / "tcdr_v4_p0_source_tier_manifest_v0_1.csv"
    summary_out = OUT_DIR / "tcdr_v4_p0_source_tier_manifest_summary_v0_1.json"
    detail.to_csv(detail_out, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {detail_out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
