from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path

import astropy.units as u
import pandas as pd
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad


ROOT = Path(__file__).resolve().parents[1]
NAME_LOOKUP = ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_lookup_v0_1.csv"
OUT_DIR = ROOT / "data" / "source_manifests"
OUT_DIR.mkdir(parents=True, exist_ok=True)

S4G_COLUMNS = [
    "object",
    "ra",
    "dec",
    "type",
    "bar",
    "ring",
    "t",
    "pa1_25p5",
    "ellip1_25p5",
    "pa1_26p5",
    "ellip1_26p5",
    "sma1_25p5",
    "sma1_26p5",
    "c31_1",
    "c42_1",
    "mstar",
]


def _download_s4g_subset() -> pd.DataFrame:
    query = f"SELECT {','.join(S4G_COLUMNS)} FROM s4gcat"
    url = (
        "https://irsa.ipac.caltech.edu/TAP/sync?"
        + urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": query})
    )
    request = urllib.request.Request(url, headers={"User-Agent": "tau-core-paper19-s4g-coordinate-lookup/0.1"})
    text = urllib.request.urlopen(request, timeout=90).read().decode("utf-8", "replace")
    return pd.read_csv(io.StringIO(text))


def _resolve_simbad(name: str) -> tuple[str, float | None, float | None, str]:
    try:
        result = Simbad.query_object(name)
    except Exception as exc:  # pragma: no cover - source-network guard
        return "resolver_error", None, None, str(exc)
    if result is None or len(result) == 0:
        return "not_resolved", None, None, ""
    try:
        return "resolved", float(result["ra"][0]), float(result["dec"][0]), str(result["main_id"][0])
    except Exception as exc:  # pragma: no cover - defensive table parsing
        return "resolver_parse_error", None, None, str(exc)


def build_coordinate_lookup(name_lookup_path: Path = NAME_LOOKUP, match_radius_arcmin: float = 1.0) -> tuple[pd.DataFrame, dict[str, float]]:
    name_lookup = pd.read_csv(name_lookup_path)
    unresolved = name_lookup[name_lookup["s4g_lookup_status"] == "not_found_by_name"].copy()
    s4g = _download_s4g_subset()
    s4g_coords = SkyCoord(s4g["ra"].astype(float).to_numpy() * u.deg, s4g["dec"].astype(float).to_numpy() * u.deg)

    rows = []
    for _, src in unresolved.iterrows():
        galaxy = src["galaxy"]
        resolver_status, ra, dec, resolver_note = _resolve_simbad(galaxy)
        if resolver_status != "resolved" or ra is None or dec is None:
            rows.append(
                {
                    "galaxy": galaxy,
                    "resolver_status": resolver_status,
                    "resolver_main_id_or_note": resolver_note,
                    "resolved_ra_deg": "",
                    "resolved_dec_deg": "",
                    "coordinate_lookup_status": "not_resolved",
                    "nearest_s4g_object": "",
                    "nearest_sep_arcmin": "",
                    "s4g_type": "",
                    "s4g_bar": "",
                    "s4g_ring": "",
                    "s4g_t": "",
                    "s4g_pa1_25p5_deg": "",
                    "s4g_ellip1_25p5": "",
                    "s4g_pa1_26p5_deg": "",
                    "s4g_ellip1_26p5": "",
                    "s4g_sma1_25p5_arcsec": "",
                    "s4g_sma1_26p5_arcsec": "",
                    "s4g_c31_1": "",
                    "s4g_c42_1": "",
                    "s4g_mstar_log10_msun": "",
                    "source_freeze_policy": "coordinate_lookup_needed_before_endpoint_scoring",
                }
            )
            continue

        coord = SkyCoord([ra] * u.deg, [dec] * u.deg)
        idx, sep2d, _ = coord.match_to_catalog_sky(s4g_coords)
        nearest = s4g.iloc[int(idx[0])]
        sep_arcmin = float(sep2d.arcmin[0])
        is_match = sep_arcmin <= match_radius_arcmin
        rows.append(
            {
                "galaxy": galaxy,
                "resolver_status": resolver_status,
                "resolver_main_id_or_note": resolver_note,
                "resolved_ra_deg": ra,
                "resolved_dec_deg": dec,
                "coordinate_lookup_status": "matched_by_coordinate" if is_match else "not_in_s4g_within_radius",
                "nearest_s4g_object": nearest["object"],
                "nearest_sep_arcmin": sep_arcmin,
                "s4g_type": nearest.get("type", "") if is_match else "",
                "s4g_bar": nearest.get("bar", "") if is_match else "",
                "s4g_ring": nearest.get("ring", "") if is_match else "",
                "s4g_t": nearest.get("t", "") if is_match else "",
                "s4g_pa1_25p5_deg": nearest.get("pa1_25p5", "") if is_match else "",
                "s4g_ellip1_25p5": nearest.get("ellip1_25p5", "") if is_match else "",
                "s4g_pa1_26p5_deg": nearest.get("pa1_26p5", "") if is_match else "",
                "s4g_ellip1_26p5": nearest.get("ellip1_26p5", "") if is_match else "",
                "s4g_sma1_25p5_arcsec": nearest.get("sma1_25p5", "") if is_match else "",
                "s4g_sma1_26p5_arcsec": nearest.get("sma1_26p5", "") if is_match else "",
                "s4g_c31_1": nearest.get("c31_1", "") if is_match else "",
                "s4g_c42_1": nearest.get("c42_1", "") if is_match else "",
                "s4g_mstar_log10_msun": nearest.get("mstar", "") if is_match else "",
                "source_freeze_policy": (
                    "source_side_morphology_available_by_coordinate_before_endpoint_scoring"
                    if is_match
                    else "outside_coordinate_match_radius_before_endpoint_scoring"
                ),
            }
        )

    detail = pd.DataFrame(rows)
    matched = int((detail["coordinate_lookup_status"] == "matched_by_coordinate").sum())
    summary = {
        "n_name_unresolved_p0_checked": int(len(detail)),
        "n_simbad_resolved": int((detail["resolver_status"] == "resolved").sum()),
        "n_s4g_coordinate_matched": matched,
        "n_remaining_without_s4g_match": int(len(detail) - matched),
        "match_radius_arcmin": float(match_radius_arcmin),
    }
    return detail, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve P0 name-unmatched SPARC candidates through SIMBAD and cross-match "
            "to S4G coordinates. This is source-side lookup only; it does not score endpoints."
        )
    )
    parser.add_argument("--name-lookup", type=Path, default=NAME_LOOKUP)
    parser.add_argument("--match-radius-arcmin", type=float, default=1.0)
    args = parser.parse_args()

    detail, summary = build_coordinate_lookup(args.name_lookup, args.match_radius_arcmin)
    detail_out = OUT_DIR / "tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv"
    summary_out = OUT_DIR / "tcdr_v4_p0_s4g_coordinate_lookup_summary_v0_1.json"
    detail.to_csv(detail_out, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {detail_out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
