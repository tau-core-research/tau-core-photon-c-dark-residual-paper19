from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data" / "source_manifests" / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv"
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
    "incl",
    "pa",
    "logr25",
]


def _normalize_name(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


def _name_variants(name: str) -> set[str]:
    raw = _normalize_name(name)
    variants = {raw}
    for prefix in ("NGC", "UGC", "IC"):
        if raw.startswith(prefix):
            suffix = raw[len(prefix) :]
            if suffix.isdigit():
                variants.add(prefix + suffix.lstrip("0"))
                variants.add(prefix + suffix.zfill(4))
                variants.add(prefix + suffix.zfill(5))
    if raw.startswith("ESO"):
        variants.add(raw.replace("G", ""))
    return {v for v in variants if v}


def _download_s4g_subset() -> pd.DataFrame:
    query = f"SELECT {','.join(S4G_COLUMNS)} FROM s4gcat"
    url = (
        "https://irsa.ipac.caltech.edu/TAP/sync?"
        + urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": query})
    )
    request = urllib.request.Request(url, headers={"User-Agent": "tau-core-paper19-s4g-lookup/0.1"})
    text = urllib.request.urlopen(request, timeout=90).read().decode("utf-8", "replace")
    return pd.read_csv(io.StringIO(text))


def build_lookup(queue_path: Path = QUEUE) -> tuple[pd.DataFrame, dict[str, int]]:
    queue = pd.read_csv(queue_path)
    p0 = queue[queue["source_review_priority"] == "P0_SOURCE_REVIEW"].copy()
    s4g = _download_s4g_subset()
    s4g["_norm"] = s4g["object"].map(_normalize_name)
    by_norm = {row["_norm"]: row for _, row in s4g.iterrows()}

    rows = []
    for _, src in p0.iterrows():
        variants = _name_variants(src["galaxy"])
        match = None
        matched_variant = ""
        for variant in sorted(variants):
            if variant in by_norm:
                match = by_norm[variant]
                matched_variant = variant
                break
        if match is None:
            rows.append(
                {
                    "galaxy": src["galaxy"],
                    "s4g_lookup_status": "not_found_by_name",
                    "matched_s4g_object": "",
                    "matched_name_variant": "",
                    "s4g_type": "",
                    "s4g_bar": "",
                    "s4g_ring": "",
                    "s4g_t": "",
                    "s4g_ra_deg": "",
                    "s4g_dec_deg": "",
                    "s4g_pa1_25p5_deg": "",
                    "s4g_ellip1_25p5": "",
                    "s4g_pa1_26p5_deg": "",
                    "s4g_ellip1_26p5": "",
                    "s4g_sma1_25p5_arcsec": "",
                    "s4g_sma1_26p5_arcsec": "",
                    "s4g_c31_1": "",
                    "s4g_c42_1": "",
                    "s4g_mstar_log10_msun": "",
                    "s4g_incl_deg": "",
                    "s4g_optical_pa_deg": "",
                    "s4g_logr25": "",
                    "source_freeze_policy": "lookup_needed_before_endpoint_scoring",
                }
            )
            continue
        rows.append(
            {
                "galaxy": src["galaxy"],
                "s4g_lookup_status": "matched_by_name",
                "matched_s4g_object": match["object"],
                "matched_name_variant": matched_variant,
                "s4g_type": match.get("type", ""),
                "s4g_bar": match.get("bar", ""),
                "s4g_ring": match.get("ring", ""),
                "s4g_t": match.get("t", ""),
                "s4g_ra_deg": match.get("ra", ""),
                "s4g_dec_deg": match.get("dec", ""),
                "s4g_pa1_25p5_deg": match.get("pa1_25p5", ""),
                "s4g_ellip1_25p5": match.get("ellip1_25p5", ""),
                "s4g_pa1_26p5_deg": match.get("pa1_26p5", ""),
                "s4g_ellip1_26p5": match.get("ellip1_26p5", ""),
                "s4g_sma1_25p5_arcsec": match.get("sma1_25p5", ""),
                "s4g_sma1_26p5_arcsec": match.get("sma1_26p5", ""),
                "s4g_c31_1": match.get("c31_1", ""),
                "s4g_c42_1": match.get("c42_1", ""),
                "s4g_mstar_log10_msun": match.get("mstar", ""),
                "s4g_incl_deg": match.get("incl", ""),
                "s4g_optical_pa_deg": match.get("pa", ""),
                "s4g_logr25": match.get("logr25", ""),
                "source_freeze_policy": "source_side_morphology_available_before_endpoint_scoring",
            }
        )

    detail = pd.DataFrame(rows)
    summary = {
        "n_p0_candidates": len(detail),
        "n_s4g_matched_by_name": int((detail["s4g_lookup_status"] == "matched_by_name").sum()),
        "n_s4g_not_found_by_name": int((detail["s4g_lookup_status"] == "not_found_by_name").sum()),
    }
    return detail, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Lookup P0 SPARC candidates in the S4G source-side morphology catalog. "
            "This script does not read rotation residuals and does not score endpoints."
        )
    )
    parser.add_argument("--queue", type=Path, default=QUEUE)
    args = parser.parse_args()

    detail, summary = build_lookup(args.queue)
    detail_out = OUT_DIR / "tcdr_v4_p0_s4g_lookup_v0_1.csv"
    summary_out = OUT_DIR / "tcdr_v4_p0_s4g_lookup_summary_v0_1.json"
    detail.to_csv(detail_out, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {detail_out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
