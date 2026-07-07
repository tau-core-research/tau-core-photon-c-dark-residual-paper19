from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

QUEUE = OUT_DIR / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv"
FAMILY_FREEZE = OUT_DIR / "tcdr_v4_p0_source_family_freeze_v0_1.csv"
PILOT = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_audit_v0_1.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_audit_summary_v0_1.json"


def _clean(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _float(value: object) -> float | None:
    text = _clean(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _needs_for_family(family: str) -> tuple[str, str, str]:
    if family == "K_BARRED_M2":
        return (
            "bar_length;bar_strength;bar_phase_or_orientation;bar_radial_support",
            "binary_bar_flag_or_barred_type",
            "source_proxy_only_needs_bar_decomposition",
        )
    if family == "K_RING_RESONANCE":
        return (
            "ring_radius;ring_width;resonance_onset_class;inner_outer_pseudoring_class",
            "binary_ring_flag_or_ring_type",
            "source_proxy_only_needs_ring_decomposition",
        )
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        return (
            "disk_scale;bulge_disk_split;outer_hi_transition;smooth_tail_guard",
            "rdisk_kpc;rhi_kpc;t_value;bulge_presence_later_endpoint_only",
            "partial_source_proxy_disk_hi_coordinates_available",
        )
    if family == "K_DIFFUSE_LATE_DISK":
        return (
            "hi_extent;low_surface_brightness_support;outer_gas_transition;diffuse_disk_quality",
            "rhi_kpc;rdisk_kpc;t_value",
            "underpowered_family_needs_more_train_support",
        )
    if family == "K_COMPACT_EARLY_DISK":
        return (
            "compact_support_radius;bulge_dominance;early_disk_scale",
            "t_value;morphology_type",
            "not_in_first_homogeneous_s4g_pilot",
        )
    return (
        "source_identity_resolution;morphology_type",
        "identity_or_catalogue_name_only",
        "not_kernel_freeze_ready",
    )


def build_coordinate_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    queue = pd.read_csv(QUEUE)
    freeze = pd.read_csv(FAMILY_FREEZE)
    pilot = pd.read_csv(PILOT)[["galaxy", "pilot_role"]]
    queue_by_galaxy = {row["galaxy"]: row for _, row in queue.iterrows()}
    pilot_by_galaxy = {row["galaxy"]: row["pilot_role"] for _, row in pilot.iterrows()}

    rows = []
    for _, row in freeze.iterrows():
        galaxy = str(row["galaxy"])
        family = str(row["source_family_candidate"])
        queue_row = queue_by_galaxy.get(galaxy)
        rdisk = _float(queue_row["rdisk_kpc"]) if queue_row is not None else None
        rhi = _float(queue_row["rhi_kpc"]) if queue_row is not None else None
        morphology_type = _clean(row["morphology_type"])
        bar_flag = _clean(row["bar_flag"])
        ring_flag = _clean(row["ring_flag"])
        t_value = _float(row["t_value"])
        ellipticity = _float(row["ellipticity_for_projection_flag"])
        inclination = _float(row["inclination_deg_for_projection_flag"])
        required, available_proxy, status = _needs_for_family(family)

        has_binary_bar = bool(bar_flag) or morphology_type.upper().startswith(("SB", "SAB"))
        has_binary_ring = bool(ring_flag) or "R" in morphology_type.upper()
        has_disk_hi = rdisk is not None and rhi is not None and rdisk > 0 and rhi > 0
        hi_to_disk_ratio = (rhi / rdisk) if has_disk_hi else None

        rows.append(
            {
                "galaxy": galaxy,
                "pilot_role": pilot_by_galaxy.get(galaxy, "not_in_pilot_manifest"),
                "source_tier": row["source_tier"],
                "source_family_candidate": family,
                "morphology_type": morphology_type,
                "bar_flag": bar_flag,
                "ring_flag": ring_flag,
                "t_value": "" if t_value is None else t_value,
                "rdisk_kpc_source_proxy": "" if rdisk is None else rdisk,
                "rhi_kpc_source_proxy": "" if rhi is None else rhi,
                "hi_to_disk_ratio_source_proxy": "" if hi_to_disk_ratio is None else hi_to_disk_ratio,
                "ellipticity_source_proxy": "" if ellipticity is None else ellipticity,
                "inclination_deg_source_proxy": "" if inclination is None else inclination,
                "has_binary_bar_or_type_proxy": _yes_no(has_binary_bar),
                "has_binary_ring_or_type_proxy": _yes_no(has_binary_ring),
                "has_disk_hi_scale_proxy": _yes_no(has_disk_hi),
                "required_source_native_coordinates": required,
                "currently_available_proxy_coordinates": available_proxy,
                "kernel_coordinate_status": status,
                "endpoint_data_policy": "do_not_use_rotation_residuals_for_kernel_coordinate_audit",
                "claim_boundary": "source_proxy_coordinate_audit_not_endpoint_scoring",
            }
        )

    detail = pd.DataFrame(rows).sort_values(["source_family_candidate", "pilot_role", "galaxy"]).reset_index(drop=True)
    summary = {
        "n_rows": int(len(detail)),
        "kernel_coordinate_status_counts": {
            str(k): int(v)
            for k, v in detail["kernel_coordinate_status"].value_counts().sort_index().items()
        },
        "family_counts": {
            str(k): int(v)
            for k, v in detail["source_family_candidate"].value_counts().sort_index().items()
        },
        "pilot_role_counts": {
            str(k): int(v) for k, v in detail["pilot_role"].value_counts().sort_index().items()
        },
        "n_has_binary_bar_or_type_proxy": int((detail["has_binary_bar_or_type_proxy"] == "yes").sum()),
        "n_has_binary_ring_or_type_proxy": int((detail["has_binary_ring_or_type_proxy"] == "yes").sum()),
        "n_has_disk_hi_scale_proxy": int((detail["has_disk_hi_scale_proxy"] == "yes").sum()),
        "verdict": (
            "The current family labels are endpoint-blind source proxies. "
            "Barred and ring/resonance kernels require source-native structural "
            "decomposition before endpoint-level family separation can be claimed."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_coordinate_audit()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
