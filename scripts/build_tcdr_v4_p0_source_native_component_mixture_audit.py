from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

ROUTE = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
PILOT = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_component_mixture_audit_summary_v0_1.json"


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


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _primary_component(family: str) -> str:
    if family == "K_BARRED_M2":
        return "bar"
    if family == "K_RING_RESONANCE":
        return "ring"
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        return "spiral_or_disk"
    if family == "K_DIFFUSE_LATE_DISK":
        return "diffuse_hi_disk"
    if family == "K_COMPACT_EARLY_DISK":
        return "compact_early_disk"
    return "unfreezable_or_unknown"


def _component_status(primary: str, has_bar: bool, has_ring: bool, has_spiral: bool) -> str:
    n_components = int(has_bar) + int(has_ring) + int(has_spiral)
    primary_covered = (
        (primary == "bar" and has_bar)
        or (primary == "ring" and has_ring)
        or (primary == "spiral_or_disk" and has_spiral)
    )
    if n_components == 0:
        return "no_source_native_bar_ring_spiral_component"
    if n_components >= 2:
        return "mixed_source_native_multicomponent"
    if primary_covered:
        return "single_source_native_primary_component"
    return "single_source_native_secondary_component_only"


def _active_components(has_bar: bool, has_ring: bool, has_spiral: bool) -> str:
    components = []
    if has_bar:
        components.append("bar")
    if has_ring:
        components.append("ring")
    if has_spiral:
        components.append("spiral")
    return ";".join(components) if components else "none"


def build_mixture_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    route = pd.read_csv(ROUTE)
    freeze = pd.read_csv(FREEZE)
    pilot = pd.read_csv(PILOT)[["galaxy", "pilot_role"]]
    detail = route.merge(
        freeze[
            [
                "galaxy",
                "kernel_coordinate_status",
                "bar_radius_kpc_source",
                "ring_radius_kpc_source",
                "spiral_pitch_median_abs_deg_source",
            ]
        ],
        on="galaxy",
        how="left",
    ).merge(pilot, on="galaxy", how="left")

    rows: list[dict[str, object]] = []
    for _, row in detail.iterrows():
        family = str(row["source_family_candidate"])
        primary = _primary_component(family)
        has_bar = _float(row.get("bar_radius_kpc_source")) is not None
        has_ring = _float(row.get("ring_radius_kpc_source")) is not None
        has_spiral = _float(row.get("spiral_pitch_median_abs_deg_source")) is not None
        status = _component_status(primary, has_bar, has_ring, has_spiral)
        n_components = int(has_bar) + int(has_ring) + int(has_spiral)
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row.get("pilot_role", ""),
                "source_family_candidate": family,
                "primary_component_from_family": primary,
                "source_native_bar_present": _yes_no(has_bar),
                "source_native_ring_present": _yes_no(has_ring),
                "source_native_spiral_pitch_present": _yes_no(has_spiral),
                "source_native_component_count": n_components,
                "active_source_native_components": _active_components(has_bar, has_ring, has_spiral),
                "component_mixture_status": status,
                "feature_types_present": row.get("feature_types_present", ""),
                "kernel_coordinate_status": row.get("kernel_coordinate_status", ""),
                "bar_radius_kpc_source": row.get("bar_radius_kpc_source", ""),
                "ring_radius_kpc_source": row.get("ring_radius_kpc_source", ""),
                "spiral_pitch_median_abs_deg_source": row.get("spiral_pitch_median_abs_deg_source", ""),
                "wrong_family_control_interpretation": (
                    "mixed_components_can_legitimately_activate_multiple_family_kernels"
                    if status == "mixed_source_native_multicomponent"
                    else "single_or_uncovered_source_native_component"
                ),
                "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_component_mixture_audit",
                "claim_boundary": "source_native_component_mixture_audit_not_endpoint_validation",
            }
        )

    audit = pd.DataFrame(rows).fillna("")
    audit = audit.sort_values(["component_mixture_status", "source_family_candidate", "pilot_role", "galaxy"]).reset_index(drop=True)
    holdout = audit[audit["pilot_role"] == "PILOT_HOLDOUT"].copy()
    summary = {
        "n_rows": int(len(audit)),
        "component_mixture_status_counts": {
            str(key): int(value)
            for key, value in audit["component_mixture_status"].value_counts().sort_index().items()
        },
        "holdout_component_mixture_status_counts": {
            str(key): int(value)
            for key, value in holdout["component_mixture_status"].value_counts().sort_index().items()
        },
        "n_mixed_source_native_multicomponent": int((audit["component_mixture_status"] == "mixed_source_native_multicomponent").sum()),
        "n_holdout_mixed_source_native_multicomponent": int((holdout["component_mixture_status"] == "mixed_source_native_multicomponent").sum()),
        "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_component_mixture_audit",
        "verdict": (
            "Several P0 galaxies have multiple source-native structural components. "
            "Wrong-family controls can therefore be physically meaningful component controls rather than pure false labels; "
            "future scoring should test mixed-component kernels source-side."
        ),
    }
    return audit, summary


def main() -> None:
    detail, summary = build_mixture_audit()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
