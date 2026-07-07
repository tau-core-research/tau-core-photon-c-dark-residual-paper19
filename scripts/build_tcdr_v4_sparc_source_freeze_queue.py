from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPARC_TABLE = ROOT / "data" / "external" / "sparc_preflight" / "SPARC_Lelli2016c.mrt"
OUT_DIR = ROOT / "data" / "source_manifests"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HUBBLE_TYPES = {
    0: "S0",
    1: "Sa",
    2: "Sab",
    3: "Sb",
    4: "Sbc",
    5: "Sc",
    6: "Scd",
    7: "Sd",
    8: "Sdm",
    9: "Sm",
    10: "Im",
    11: "BCD",
}


def _parse_sparc_table(path: Path) -> list[dict[str, str | float | int]]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) < 18:
            continue
        if parts[0] in {"Title:", "Authors:", "Table:", "Bytes", "Note"}:
            continue
        try:
            row = {
                "galaxy": parts[0],
                "hubble_t": int(parts[1]),
                "distance_mpc": float(parts[2]),
                "distance_error_mpc": float(parts[3]),
                "distance_method_code": int(parts[4]),
                "inclination_deg": float(parts[5]),
                "inclination_error_deg": float(parts[6]),
                "lum_36_1e9_lsun": float(parts[7]),
                "reff_kpc": float(parts[9]),
                "rdisk_kpc": float(parts[11]),
                "mhi_1e9_msun": float(parts[13]),
                "rhi_kpc": float(parts[14]),
                "quality_flag": int(parts[17]),
                "hi_ha_reference": parts[18] if len(parts) > 18 else "",
            }
        except ValueError:
            continue
        rows.append(row)
    return rows


def _name_family(galaxy: str) -> str:
    for prefix in ("NGC", "UGC", "IC", "DDO", "ESO", "UGCA", "F", "CamB"):
        if galaxy.upper().startswith(prefix):
            return prefix
    return "OTHER"


def _source_priority(row: dict[str, str | float | int]) -> tuple[str, list[str]]:
    q = int(row["quality_flag"])
    inc = float(row["inclination_deg"])
    rhi = float(row["rhi_kpc"])
    family = _name_family(str(row["galaxy"]))
    reasons = []

    if q == 1:
        reasons.append("high_quality_rotation_curve")
    elif q == 2:
        reasons.append("medium_quality_rotation_curve")
    else:
        reasons.append("low_quality_rotation_curve")

    if 35.0 <= inc <= 82.0:
        reasons.append("inclination_not_extreme")
    elif inc > 82.0:
        reasons.append("edge_on_projection_caveat")
    else:
        reasons.append("face_on_projection_caveat")

    if rhi > 0:
        reasons.append("hi_extent_available")
    else:
        reasons.append("hi_extent_missing_or_zero")

    if family in {"NGC", "UGC", "IC", "ESO"}:
        reasons.append("catalog_name_queryable")
    else:
        reasons.append("catalog_name_needs_alias_review")

    if q == 1 and 35.0 <= inc <= 82.0 and rhi > 0 and family in {"NGC", "UGC", "IC", "ESO"}:
        return "P0_SOURCE_REVIEW", reasons
    if q <= 2 and 25.0 <= inc <= 88.0 and family in {"NGC", "UGC", "IC", "ESO", "DDO", "UGCA"}:
        return "P1_SOURCE_REVIEW", reasons
    return "P2_SOURCE_REVIEW", reasons


def build_queue(sparc_table: Path = DEFAULT_SPARC_TABLE) -> tuple[list[dict[str, str | float | int]], dict[str, int]]:
    rows = _parse_sparc_table(sparc_table)
    out_rows: list[dict[str, str | float | int]] = []
    for row in rows:
        priority, reasons = _source_priority(row)
        hubble_t = int(row["hubble_t"])
        out_rows.append(
            {
                "galaxy": row["galaxy"],
                "name_family": _name_family(str(row["galaxy"])),
                "hubble_t": hubble_t,
                "hubble_type_label": HUBBLE_TYPES.get(hubble_t, "unknown"),
                "quality_flag": row["quality_flag"],
                "distance_mpc": row["distance_mpc"],
                "distance_error_mpc": row["distance_error_mpc"],
                "inclination_deg": row["inclination_deg"],
                "inclination_error_deg": row["inclination_error_deg"],
                "reff_kpc": row["reff_kpc"],
                "rdisk_kpc": row["rdisk_kpc"],
                "mhi_1e9_msun": row["mhi_1e9_msun"],
                "rhi_kpc": row["rhi_kpc"],
                "source_review_priority": priority,
                "source_review_reasons": ";".join(reasons),
                "s4g_lookup_status": "not_queried",
                "galaxy_zoo_lookup_status": "not_queried",
                "endpoint_data_policy": "do_not_use_rotation_residuals_for_source_label",
                "allowed_for_endpoint_scoring": "after_source_freeze_only",
            }
        )
    summary = {
        "n_sparc_rows": len(out_rows),
        "n_p0_source_review": sum(row["source_review_priority"] == "P0_SOURCE_REVIEW" for row in out_rows),
        "n_p1_source_review": sum(row["source_review_priority"] == "P1_SOURCE_REVIEW" for row in out_rows),
        "n_p2_source_review": sum(row["source_review_priority"] == "P2_SOURCE_REVIEW" for row in out_rows),
        "n_quality_1": sum(row["quality_flag"] == 1 for row in out_rows),
        "n_quality_2": sum(row["quality_flag"] == 2 for row in out_rows),
        "n_quality_3": sum(row["quality_flag"] == 3 for row in out_rows),
    }
    return out_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a SPARC-based TCDR-v4 source-freeze queue. This script uses SPARC "
            "sample metadata only and intentionally excludes Vflat/rotation endpoint values."
        )
    )
    parser.add_argument("--sparc-table", type=Path, default=DEFAULT_SPARC_TABLE)
    args = parser.parse_args()

    rows, summary = build_queue(args.sparc_table)
    out = OUT_DIR / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    summary_out = OUT_DIR / "tcdr_v4_sparc_source_freeze_queue_summary_v0_1.json"
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
