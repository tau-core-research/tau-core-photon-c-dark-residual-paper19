from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import pandas as pd
from astroquery.vizier import Vizier


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

FAMILY_FREEZE = OUT_DIR / "tcdr_v4_p0_source_family_freeze_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_summary_v0_1.json"

P4_CATALOG = "J/ApJS/219/4"
FEATURE_CATALOG = "J/A+A/582/A86"


def _norm_name(name: object) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


def _name_variants(name: object) -> set[str]:
    raw = _norm_name(name)
    variants = {raw}
    for prefix in ("NGC", "UGC", "IC"):
        if raw.startswith(prefix):
            suffix = raw[len(prefix) :]
            if suffix.isdigit():
                variants.add(prefix + suffix.lstrip("0"))
                variants.add(prefix + suffix.zfill(4))
                variants.add(prefix + suffix.zfill(5))
    return {variant for variant in variants if variant}


def _float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def _text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _load_vizier_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    vizier = Vizier(columns=["**"])
    vizier.ROW_LIMIT = -1
    p4_tables = vizier.get_catalogs(P4_CATALOG)
    feature_tables = vizier.get_catalogs(FEATURE_CATALOG)

    p4_table7 = p4_tables[1].to_pandas()
    feature_table2 = feature_tables[0].to_pandas()
    spiral_table3 = feature_tables[1].to_pandas()

    for table in (p4_table7, feature_table2, spiral_table3):
        table["_norm"] = table["Name"].map(_norm_name)
    return p4_table7, feature_table2, spiral_table3


def _rows_for_name(table: pd.DataFrame, galaxy: str) -> pd.DataFrame:
    variants = _name_variants(galaxy)
    return table[table["_norm"].isin(variants)].copy()


def _best_p4_bar(rows: pd.DataFrame) -> dict[str, object]:
    if rows.empty or "Rbar" not in rows:
        return {}
    candidates = rows[rows["Rbar"].map(_float).notna()].copy()
    if candidates.empty:
        return {}
    candidates["_Rbar"] = candidates["Rbar"].map(_float)
    candidates["_Q"] = candidates["Q"].map(_float).fillna(-1)
    candidates = candidates.sort_values(["_Q", "_Rbar"], ascending=[False, False])
    row = candidates.iloc[0]
    return {
        "p4_model": _text(row.get("Mod")),
        "p4_quality": _text(row.get("Q")),
        "p4_bar_radius_arcsec": _text(row.get("Rbar")),
        "p4_bar_flux_fraction": _text(row.get("f4")),
        "p4_bar_axis_ratio": _text(row.get("q4")),
        "p4_bar_pa_deg": _text(row.get("PA4")),
    }


def _best_feature(rows: pd.DataFrame, mode: str) -> dict[str, object]:
    if rows.empty:
        return {}
    feature_rows = rows.copy()
    types = feature_rows["Type"].map(_text)
    if mode == "bar":
        candidates = feature_rows[types.str.lower() == "bar"].copy()
    elif mode == "ring":
        candidates = feature_rows[
            types.map(lambda item: item.lower() != "bar" and any(token in item.lower() for token in ("r", "l", "nr", "rs")))
        ].copy()
    else:
        candidates = pd.DataFrame()
    if candidates.empty:
        return {}
    candidates["_radius"] = candidates.apply(
        lambda row: _float(row.get("dsma")) or _float(row.get("sma")) or -1.0,
        axis=1,
    )
    candidates = candidates.sort_values("_radius", ascending=False)
    row = candidates.iloc[0]
    prefix = "feature_bar" if mode == "bar" else "feature_ring"
    return {
        f"{prefix}_type": _text(row.get("Type")),
        f"{prefix}_quality": _text(row.get("Qual")),
        f"{prefix}_sma_arcsec": _text(row.get("sma")),
        f"{prefix}_deprojected_sma_arcsec": _text(row.get("dsma")),
        f"{prefix}_pa_deg": _text(row.get("PA")),
        f"{prefix}_deprojected_pa_deg": _text(row.get("dPA")),
        f"{prefix}_ellipticity": _text(row.get("Ell")),
        f"{prefix}_deprojected_ellipticity": _text(row.get("dEll")),
    }


def _spiral_summary(rows: pd.DataFrame) -> dict[str, object]:
    if rows.empty:
        return {}
    pitches = [_float(value) for value in rows["Pitchang"].tolist()]
    pitches = [value for value in pitches if value is not None]
    if not pitches:
        return {"spiral_segment_count": int(len(rows))}
    return {
        "spiral_segment_count": int(len(rows)),
        "spiral_pitch_median_abs_deg": float(pd.Series([abs(value) for value in pitches]).median()),
        "spiral_inner_radius_min_arcsec": float(pd.Series([_float(value) for value in rows["ri"].tolist() if _float(value) is not None]).min()),
        "spiral_outer_radius_max_arcsec": float(pd.Series([_float(value) for value in rows["ro"].tolist() if _float(value) is not None]).max()),
    }


def _route_status(family: str, p4_bar: dict[str, object], feature_bar: dict[str, object], feature_ring: dict[str, object], spiral: dict[str, object]) -> str:
    if family == "K_BARRED_M2":
        if feature_bar:
            return "source_native_feature_bar_available"
        if p4_bar:
            return "source_native_p4_bar_available"
        return "source_proxy_only_bar_decomposition_missing"
    if family == "K_RING_RESONANCE":
        if feature_ring:
            return "source_native_feature_ring_available"
        return "source_proxy_only_ring_decomposition_missing"
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        if spiral:
            return "source_native_spiral_pitch_available"
        return "disk_scale_proxy_available_no_spiral_feature"
    if family == "K_DIFFUSE_LATE_DISK":
        return "diffuse_family_needs_additional_lsb_hi_support"
    if family == "K_COMPACT_EARLY_DISK":
        return "compact_family_not_primary_bar_ring_route"
    return "not_kernel_route_ready"


def build_source_route() -> tuple[pd.DataFrame, dict[str, object]]:
    freeze = pd.read_csv(FAMILY_FREEZE)
    p4_table7, feature_table2, spiral_table3 = _load_vizier_tables()

    rows: list[dict[str, object]] = []
    for _, source in freeze.iterrows():
        galaxy = str(source["galaxy"])
        family = str(source["source_family_candidate"])
        p4_rows = _rows_for_name(p4_table7, galaxy)
        feature_rows = _rows_for_name(feature_table2, galaxy)
        spiral_rows = _rows_for_name(spiral_table3, galaxy)

        p4_bar = _best_p4_bar(p4_rows)
        feature_bar = _best_feature(feature_rows, "bar")
        feature_ring = _best_feature(feature_rows, "ring")
        spiral = _spiral_summary(spiral_rows)
        route_status = _route_status(family, p4_bar, feature_bar, feature_ring, spiral)

        row: dict[str, object] = {
            "galaxy": galaxy,
            "source_family_candidate": family,
            "source_tier": source["source_tier"],
            "morphology_type": source["morphology_type"],
            "p4_row_count": int(len(p4_rows)),
            "feature_row_count": int(len(feature_rows)),
            "spiral_row_count": int(len(spiral_rows)),
            "feature_types_present": ";".join(sorted({item for item in feature_rows["Type"].map(_text).tolist() if item})),
            "bar_ring_decomposition_route_status": route_status,
            "vizier_catalogs_used": f"{P4_CATALOG};{FEATURE_CATALOG}",
            "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_source_route",
            "claim_boundary": "source_native_coordinate_route_not_kernel_validation",
        }
        row.update(p4_bar)
        row.update(feature_bar)
        row.update(feature_ring)
        row.update(spiral)
        rows.append(row)

    detail = pd.DataFrame(rows).fillna("")
    detail = detail.sort_values(["source_family_candidate", "bar_ring_decomposition_route_status", "galaxy"]).reset_index(drop=True)
    summary = {
        "n_rows": int(len(detail)),
        "route_status_counts": {
            str(key): int(value)
            for key, value in detail["bar_ring_decomposition_route_status"].value_counts().sort_index().items()
        },
        "family_counts": {
            str(key): int(value)
            for key, value in detail["source_family_candidate"].value_counts().sort_index().items()
        },
        "n_with_pipeline4_rows": int((detail["p4_row_count"] > 0).sum()),
        "n_with_feature_rows": int((detail["feature_row_count"] > 0).sum()),
        "n_with_spiral_rows": int((detail["spiral_row_count"] > 0).sum()),
        "vizier_catalogs_used": [P4_CATALOG, FEATURE_CATALOG],
        "verdict": (
            "A machine-readable S4G route exists for a nontrivial subset of P0 galaxies. "
            "Bar/ring endpoint promotion still requires a frozen coordinate rule and coverage review; "
            "this artifact is source-route evidence, not endpoint validation."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_source_route()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
