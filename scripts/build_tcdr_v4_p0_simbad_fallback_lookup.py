from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd
from astroquery.simbad import Simbad


ROOT = Path(__file__).resolve().parents[1]
COORD_LOOKUP = ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv"
OUT_DIR = ROOT / "data" / "source_manifests"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _safe_cell(row, key: str) -> str:
    try:
        value = row[key]
    except Exception:
        return ""
    if value is None:
        return ""
    return str(value)


def _configure_simbad() -> Simbad:
    simbad = Simbad()
    simbad.add_votable_fields("otype", "otypes", "ids", "morphtype")
    return simbad


def build_simbad_fallback(coord_lookup_path: Path = COORD_LOOKUP) -> tuple[pd.DataFrame, dict[str, int]]:
    coord_lookup = pd.read_csv(coord_lookup_path)
    unresolved = coord_lookup[coord_lookup["coordinate_lookup_status"] != "matched_by_coordinate"].copy()
    simbad = _configure_simbad()

    rows = []
    for _, src in unresolved.iterrows():
        galaxy = src["galaxy"]
        try:
            result = simbad.query_object(galaxy)
        except Exception as exc:  # pragma: no cover - source-network guard
            result = None
            error = str(exc)
        else:
            error = ""

        if result is None or len(result) == 0:
            rows.append(
                {
                    "galaxy": galaxy,
                    "simbad_lookup_status": "not_resolved",
                    "simbad_main_id": "",
                    "simbad_ra_deg": "",
                    "simbad_dec_deg": "",
                    "simbad_object_type": "",
                    "simbad_object_type_text": "",
                    "simbad_morph_type": "",
                    "simbad_morph_qual": "",
                    "simbad_morph_bibcode": "",
                    "simbad_ids": "",
                    "source_freeze_policy": "manual_source_review_needed_before_endpoint_scoring",
                    "lookup_note": error,
                }
            )
            continue

        row = result[0]
        morph_type = _safe_cell(row, "morph_type")
        rows.append(
            {
                "galaxy": galaxy,
                "simbad_lookup_status": "resolved_with_morphology" if morph_type else "resolved_without_morphology",
                "simbad_main_id": _safe_cell(row, "main_id"),
                "simbad_ra_deg": _safe_cell(row, "ra"),
                "simbad_dec_deg": _safe_cell(row, "dec"),
                "simbad_object_type": _safe_cell(row, "otype"),
                "simbad_object_type_text": _safe_cell(row, "otypes.otype_txt"),
                "simbad_morph_type": morph_type,
                "simbad_morph_qual": _safe_cell(row, "morph_qual"),
                "simbad_morph_bibcode": _safe_cell(row, "morph_bibcode"),
                "simbad_ids": _safe_cell(row, "ids"),
                "source_freeze_policy": (
                    "simbad_source_side_morphology_available_before_endpoint_scoring"
                    if morph_type
                    else "simbad_identity_available_morphology_missing_before_endpoint_scoring"
                ),
                "lookup_note": "",
            }
        )

    detail = pd.DataFrame(rows)
    summary = {
        "n_non_s4g_p0_checked": int(len(detail)),
        "n_simbad_resolved": int((detail["simbad_lookup_status"] != "not_resolved").sum()),
        "n_simbad_resolved_with_morphology": int((detail["simbad_lookup_status"] == "resolved_with_morphology").sum()),
        "n_simbad_resolved_without_morphology": int((detail["simbad_lookup_status"] == "resolved_without_morphology").sum()),
        "n_not_resolved": int((detail["simbad_lookup_status"] == "not_resolved").sum()),
    }
    return detail, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a SIMBAD source-side fallback manifest for P0 galaxies not covered by S4G. "
            "This does not read rotation residuals and does not run endpoint scoring."
        )
    )
    parser.add_argument("--coordinate-lookup", type=Path, default=COORD_LOOKUP)
    args = parser.parse_args()

    detail, summary = build_simbad_fallback(args.coordinate_lookup)
    detail_out = OUT_DIR / "tcdr_v4_p0_simbad_fallback_lookup_v0_1.csv"
    summary_out = OUT_DIR / "tcdr_v4_p0_simbad_fallback_lookup_summary_v0_1.json"
    detail.to_csv(detail_out, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {detail_out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
