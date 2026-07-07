from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

QUEUE = OUT_DIR / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv"
SOURCE_TIER = OUT_DIR / "tcdr_v4_p0_source_tier_manifest_v0_1.csv"
S4G_NAME = OUT_DIR / "tcdr_v4_p0_s4g_lookup_v0_1.csv"
S4G_COORD = OUT_DIR / "tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv"


def _clean(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _float(value: object) -> float | None:
    if pd.isna(value) or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _has_bar(morphology: str, bar_flag: str) -> bool:
    m = morphology.upper()
    b = bar_flag.upper()
    return b == "B" or m.startswith("SB") or m.startswith("SAB") or "IAB" in m


def _has_ring(morphology: str, ring_flag: str) -> bool:
    m = morphology.upper()
    r = ring_flag.upper()
    return r == "R" or "(R" in m or "R)" in m or "R:" in m or "RING" in m


def _is_late_diffuse(morphology: str, t_value: float | None) -> bool:
    m = morphology.upper()
    if t_value is not None and t_value >= 8.0:
        return True
    return any(token in m for token in ("SM", "SBM", "IM", "IRR", "BCD", "DIA", "LSB"))


def _is_early_compact(morphology: str, t_value: float | None) -> bool:
    m = morphology.upper()
    if t_value is not None and t_value <= 1.0:
        return True
    return m.startswith("S0") or m in {"E", "SA", "S0-A"} or "S0" in m


def _is_projection_dominated(ellipticity: float | None, inclination: float | None) -> bool:
    return (ellipticity is not None and ellipticity >= 0.65) or (inclination is not None and inclination >= 78.0)


def _family_from_source(
    morphology: str,
    bar_flag: str,
    ring_flag: str,
    t_value: float | None,
) -> tuple[str, str]:
    if not morphology:
        return "K_UNFREEZABLE_IDENTITY_ONLY", "no_source_side_morphology_type"
    if _has_ring(morphology, ring_flag):
        return "K_RING_RESONANCE", "ring_flag_or_ring_morphology"
    if _has_bar(morphology, bar_flag):
        return "K_BARRED_M2", "bar_flag_or_barred_morphology"
    if _is_late_diffuse(morphology, t_value):
        return "K_DIFFUSE_LATE_DISK", "late_or_irregular_morphology"
    if _is_early_compact(morphology, t_value):
        return "K_COMPACT_EARLY_DISK", "early_or_compact_morphology"
    return "K_EXPONENTIAL_SPIRAL_DISK", "ordinary_spiral_default"


def build_family_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    queue = pd.read_csv(QUEUE)
    queue_by_galaxy = {row["galaxy"]: row for _, row in queue.iterrows()}
    tier = pd.read_csv(SOURCE_TIER)
    name = pd.read_csv(S4G_NAME)
    coord = pd.read_csv(S4G_COORD)
    name_by_galaxy = {row["galaxy"]: row for _, row in name.iterrows()}
    coord_by_galaxy = {row["galaxy"]: row for _, row in coord.iterrows()}

    rows = []
    for _, row in tier.iterrows():
        galaxy = row["galaxy"]
        source_tier = row["source_tier"]
        queue_row = queue_by_galaxy.get(galaxy)
        inclination = _float(queue_row["inclination_deg"]) if queue_row is not None else None
        morphology = _clean(row["morphology_type"])
        bar_flag = ""
        ring_flag = ""
        t_value = None
        ellipticity = None
        if source_tier == "S4G_STRONG" and galaxy in name_by_galaxy:
            src = name_by_galaxy[galaxy]
            bar_flag = _clean(src.get("s4g_bar", ""))
            ring_flag = _clean(src.get("s4g_ring", ""))
            t_value = _float(src.get("s4g_t", ""))
            ellipticity = _float(src.get("s4g_ellip1_25p5", ""))
        elif source_tier == "S4G_COORD_RESCUE" and galaxy in coord_by_galaxy:
            src = coord_by_galaxy[galaxy]
            bar_flag = _clean(src.get("s4g_bar", ""))
            ring_flag = _clean(src.get("s4g_ring", ""))
            t_value = _float(src.get("s4g_t", ""))
            ellipticity = _float(src.get("s4g_ellip1_25p5", ""))

        family, family_rule = _family_from_source(morphology, bar_flag, ring_flag, t_value)
        projection_flag = "yes" if _is_projection_dominated(ellipticity, inclination) else "no"
        if source_tier in {"S4G_STRONG", "S4G_COORD_RESCUE"}:
            freeze_strength = "freeze_ready_homogeneous_s4g"
        elif source_tier == "SIMBAD_FALLBACK" and family != "K_UNFREEZABLE_IDENTITY_ONLY":
            freeze_strength = "freeze_candidate_catalogue_fallback"
        else:
            freeze_strength = "not_freeze_ready_identity_only"

        rows.append(
            {
                "galaxy": galaxy,
                "source_tier": source_tier,
                "source_family_candidate": family,
                "family_selection_rule": family_rule,
                "freeze_strength": freeze_strength,
                "morphology_type": morphology,
                "bar_flag": bar_flag,
                "ring_flag": ring_flag,
                "t_value": "" if t_value is None else t_value,
                "ellipticity_for_projection_flag": "" if ellipticity is None else ellipticity,
                "inclination_deg_for_projection_flag": "" if inclination is None else inclination,
                "projection_caveat": projection_flag,
                "source_family_policy": "freeze_before_endpoint_scoring",
                "endpoint_data_policy": "do_not_use_rotation_residuals_for_family_selection",
            }
        )

    detail = pd.DataFrame(rows).sort_values(["source_tier", "source_family_candidate", "galaxy"]).reset_index(drop=True)
    family_counts = detail["source_family_candidate"].value_counts().sort_index().to_dict()
    strength_counts = detail["freeze_strength"].value_counts().sort_index().to_dict()
    summary = {
        "n_p0_objects": int(len(detail)),
        "family_counts": {key: int(value) for key, value in family_counts.items()},
        "freeze_strength_counts": {key: int(value) for key, value in strength_counts.items()},
        "n_projection_caveat": int((detail["projection_caveat"] == "yes").sum()),
        "n_freeze_ready_homogeneous_s4g": int((detail["freeze_strength"] == "freeze_ready_homogeneous_s4g").sum()),
        "n_freeze_candidate_catalogue_fallback": int((detail["freeze_strength"] == "freeze_candidate_catalogue_fallback").sum()),
        "n_not_freeze_ready_identity_only": int((detail["freeze_strength"] == "not_freeze_ready_identity_only").sum()),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_family_freeze()
    detail_out = OUT_DIR / "tcdr_v4_p0_source_family_freeze_v0_1.csv"
    summary_out = OUT_DIR / "tcdr_v4_p0_source_family_freeze_summary_v0_1.json"
    detail.to_csv(detail_out, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {detail_out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
