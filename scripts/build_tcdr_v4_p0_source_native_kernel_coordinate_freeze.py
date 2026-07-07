from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

ROUTE = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
QUEUE = OUT_DIR / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv"
PILOT = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_summary_v0_1.json"


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


def _first_float(*values: object) -> float | None:
    for value in values:
        result = _float(value)
        if result is not None and result > 0:
            return result
    return None


def _arcsec_to_kpc(arcsec: float | None, distance_mpc: float | None) -> float | None:
    if arcsec is None or distance_mpc is None or distance_mpc <= 0:
        return None
    return arcsec * distance_mpc * 1000.0 / 206265.0


def _strength_from_axis_ratio_or_ellipticity(axis_ratio: object, ellipticity: object) -> float | None:
    ell = _float(ellipticity)
    if ell is not None:
        return max(0.0, min(1.0, ell))
    q = _float(axis_ratio)
    if q is not None:
        return max(0.0, min(1.0, 1.0 - q))
    return None


def _source_coordinate_for_row(row: pd.Series) -> dict[str, object]:
    family = str(row["source_family_candidate"])
    distance = _float(row["distance_mpc"])
    rdisk = _float(row["rdisk_kpc"])
    rhi = _float(row["rhi_kpc"])

    bar_arcsec = _first_float(
        row.get("feature_bar_deprojected_sma_arcsec"),
        row.get("feature_bar_sma_arcsec"),
        row.get("p4_bar_radius_arcsec"),
    )
    ring_arcsec = _first_float(
        row.get("feature_ring_deprojected_sma_arcsec"),
        row.get("feature_ring_sma_arcsec"),
    )
    bar_kpc = _arcsec_to_kpc(bar_arcsec, distance)
    ring_kpc = _arcsec_to_kpc(ring_arcsec, distance)
    pitch = _float(row.get("spiral_pitch_median_abs_deg"))

    bar_strength = _strength_from_axis_ratio_or_ellipticity(
        row.get("p4_bar_axis_ratio"), row.get("feature_bar_deprojected_ellipticity") or row.get("feature_bar_ellipticity")
    )
    ring_strength = _strength_from_axis_ratio_or_ellipticity(
        None, row.get("feature_ring_deprojected_ellipticity") or row.get("feature_ring_ellipticity")
    )

    kernel_center_kpc: float | None = None
    kernel_width_kpc: float | None = None
    coordinate_status = "source_proxy_kernel_fallback"
    coordinate_rule = "family_proxy_only"

    if family == "K_BARRED_M2" and bar_kpc is not None:
        kernel_center_kpc = bar_kpc
        kernel_width_kpc = max(0.35 * bar_kpc, 0.20 * rdisk) if rdisk is not None else 0.35 * bar_kpc
        coordinate_status = "source_native_bar_radius_frozen"
        coordinate_rule = "bar_kernel_center_equals_s4g_bar_radius_width_max_0p35_bar_0p20_rdisk"
    elif family == "K_RING_RESONANCE" and ring_kpc is not None:
        kernel_center_kpc = ring_kpc
        kernel_width_kpc = max(0.18 * ring_kpc, 0.20 * rdisk) if rdisk is not None else 0.18 * ring_kpc
        coordinate_status = "source_native_ring_radius_frozen"
        coordinate_rule = "ring_kernel_center_equals_s4g_ring_radius_width_max_0p18_ring_0p20_rdisk"
    elif family == "K_EXPONENTIAL_SPIRAL_DISK" and pitch is not None:
        # Pitch is dimensionless angular morphology. The center remains the
        # disk-scale bump used by the frozen proxy kernel; pitch is retained for
        # later source-native spiral-arm refinements rather than endpoint tuning.
        kernel_center_kpc = 1.4 * rdisk if rdisk is not None else None
        kernel_width_kpc = 0.55 * rdisk if rdisk is not None else None
        coordinate_status = "source_native_spiral_pitch_recorded_disk_proxy_center"
        coordinate_rule = "spiral_pitch_recorded_but_disk_kernel_center_remains_1p4_rdisk"

    return {
        "bar_radius_arcsec_source": "" if bar_arcsec is None else bar_arcsec,
        "bar_radius_kpc_source": "" if bar_kpc is None else bar_kpc,
        "bar_strength_proxy": "" if bar_strength is None else bar_strength,
        "ring_radius_arcsec_source": "" if ring_arcsec is None else ring_arcsec,
        "ring_radius_kpc_source": "" if ring_kpc is None else ring_kpc,
        "ring_strength_proxy": "" if ring_strength is None else ring_strength,
        "spiral_pitch_median_abs_deg_source": "" if pitch is None else pitch,
        "kernel_center_kpc_source": "" if kernel_center_kpc is None else kernel_center_kpc,
        "kernel_width_kpc_source": "" if kernel_width_kpc is None else kernel_width_kpc,
        "kernel_coordinate_status": coordinate_status,
        "kernel_coordinate_rule": coordinate_rule,
    }


def build_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    route = pd.read_csv(ROUTE)
    queue = pd.read_csv(QUEUE)[["galaxy", "distance_mpc", "rdisk_kpc", "rhi_kpc"]]
    pilot = pd.read_csv(PILOT)[["galaxy", "pilot_role"]]
    detail = route.merge(queue, on="galaxy", how="left").merge(pilot, on="galaxy", how="left")

    rows: list[dict[str, object]] = []
    for _, row in detail.iterrows():
        coordinates = _source_coordinate_for_row(row)
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row.get("pilot_role", ""),
                "source_family_candidate": row["source_family_candidate"],
                "source_tier": row["source_tier"],
                "bar_ring_decomposition_route_status": row["bar_ring_decomposition_route_status"],
                "distance_mpc_source": row.get("distance_mpc", ""),
                "rdisk_kpc_source": row.get("rdisk_kpc", ""),
                "rhi_kpc_source": row.get("rhi_kpc", ""),
                **coordinates,
                "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_coordinate_freeze",
                "claim_boundary": "source_native_coordinate_freeze_not_kernel_validation",
            }
        )

    frozen = pd.DataFrame(rows).fillna("")
    frozen = frozen.sort_values(["source_family_candidate", "kernel_coordinate_status", "pilot_role", "galaxy"]).reset_index(drop=True)
    summary = {
        "n_rows": int(len(frozen)),
        "kernel_coordinate_status_counts": {
            str(key): int(value)
            for key, value in frozen["kernel_coordinate_status"].value_counts().sort_index().items()
        },
        "pilot_role_counts": {
            str(key): int(value)
            for key, value in frozen["pilot_role"].value_counts().sort_index().items()
        },
        "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_coordinate_freeze",
        "verdict": (
            "Source-native bar/ring coordinates can be frozen for the covered subset before endpoint scoring. "
            "Uncovered objects remain source-proxy fallback cases; no endpoint validation follows."
        ),
    }
    return frozen, summary


def main() -> None:
    detail, summary = build_freeze()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
