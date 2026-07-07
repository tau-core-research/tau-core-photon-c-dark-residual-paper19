from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

PILOT = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"
COORDINATE_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
ROUTE = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
MIXTURE_AUDIT = OUT_DIR / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"
RADIAL_GEOMETRY_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_summary_v0_4.json"

ENDPOINT_POLICY = "do_not_use_rotation_residuals_or_endpoint_scores_for_formula_compiler_readiness"
CLAIM_BOUNDARY = "source_frozen_formula_compiler_readiness_not_endpoint_validation"

COMPONENTS = ("bar", "ring", "spiral")


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


def _yes(value: object) -> bool:
    return str(value).strip().lower() == "yes"


def _active_components(value: object) -> list[str]:
    if value is None or pd.isna(value):
        return []
    return [item for item in str(value).split(";") if item in COMPONENTS]


def _available_observables(row: pd.Series) -> set[str]:
    available: set[str] = set()
    if _float(row.get("rdisk_kpc_source")) is not None:
        available.add("rdisk_kpc_source")
    if _float(row.get("rhi_kpc_source")) is not None:
        available.add("rhi_kpc_source")
    if _float(row.get("bar_radius_kpc_source")) is not None:
        available.add("bar_radius_kpc_source")
    if _float(row.get("ring_radius_kpc_source")) is not None:
        available.add("ring_radius_kpc_source")
    if _float(row.get("spiral_pitch_median_abs_deg_source")) is not None:
        available.add("spiral_pitch_median_abs_deg_source")
    if _float(row.get("bar_strength_proxy")) is not None:
        available.add("bar_strength_proxy")
    if _float(row.get("ring_strength_proxy")) is not None:
        available.add("ring_strength_proxy")
    return available


def _required_observables(family: str) -> tuple[list[str], list[str]]:
    if family == "K_BARRED_M2":
        return ["rdisk_kpc_source", "bar_radius_kpc_source"], ["bar_strength_proxy"]
    if family == "K_RING_RESONANCE":
        return ["rdisk_kpc_source", "ring_radius_kpc_source"], ["ring_strength_proxy"]
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        return ["rdisk_kpc_source"], ["spiral_pitch_median_abs_deg_source", "rhi_kpc_source"]
    if family == "K_DIFFUSE_LATE_DISK":
        return ["rdisk_kpc_source", "rhi_kpc_source", "diffuse_lsb_or_hi_dominance_source"], []
    if family == "K_COMPACT_EARLY_DISK":
        return ["rdisk_kpc_source", "compact_support_or_turnover_radius_source"], []
    return ["freezeable_source_family"], []


def _available_formula_components(row: pd.Series) -> list[str]:
    components: list[str] = []
    if _float(row.get("bar_radius_kpc_source")) is not None:
        components.append("bar")
    if _float(row.get("ring_radius_kpc_source")) is not None:
        components.append("ring")
    if _float(row.get("spiral_pitch_median_abs_deg_source")) is not None:
        components.append("spiral")
    if _float(row.get("rdisk_kpc_source")) is not None:
        components.append("exponential_disk")
    return components


def _formula_name(family: str, primary_ready: bool, available_components: list[str]) -> str:
    non_disk_components = [item for item in available_components if item != "exponential_disk"]
    if family == "K_BARRED_M2":
        if primary_ready and len(non_disk_components) > 1:
            return "F_MIXED_BAR_SOURCE_NATIVE_COMPONENTS"
        if primary_ready:
            return "F_BAR_M2_SOURCE_FROZEN"
        if non_disk_components:
            return "F_SECONDARY_COMPONENT_DIAGNOSTIC_ONLY"
        return "F_BAR_M2_TEMPLATE_FALLBACK_ONLY"
    if family == "K_RING_RESONANCE":
        if primary_ready and len(non_disk_components) > 1:
            return "F_MIXED_RING_SOURCE_NATIVE_COMPONENTS"
        if primary_ready:
            return "F_RING_RESONANCE_SOURCE_FROZEN"
        if non_disk_components:
            return "F_SECONDARY_COMPONENT_DIAGNOSTIC_ONLY"
        return "F_RING_TEMPLATE_FALLBACK_ONLY"
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        if "spiral" in available_components:
            return "F_EXPONENTIAL_DISK_WITH_SPIRAL_PITCH_SOURCE_FROZEN"
        if "exponential_disk" in available_components:
            return "F_EXPONENTIAL_DISK_SCALE_TAIL_SOURCE_FROZEN"
        return "F_EXPONENTIAL_DISK_TEMPLATE_FALLBACK_ONLY"
    if family == "K_DIFFUSE_LATE_DISK":
        return "F_DIFFUSE_LSB_HI_SOURCE_PARTIAL"
    if family == "K_COMPACT_EARLY_DISK":
        return "F_COMPACT_FINITE_SOURCE_PARTIAL"
    return "F_UNFREEZABLE_IDENTITY_ONLY"


def _readiness_status(family: str, missing_required: list[str], primary_ready: bool, components: list[str]) -> str:
    if family == "K_UNFREEZABLE_IDENTITY_ONLY":
        return "BLOCKED_UNFREEZABLE_SOURCE_FAMILY"
    if family in {"K_DIFFUSE_LATE_DISK", "K_COMPACT_EARLY_DISK"}:
        if missing_required:
            return "PARTIAL_FORMULA_COMPILER_CANDIDATE"
        return "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
    if not missing_required and primary_ready:
        return "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
    if components and components != ["exponential_disk"]:
        return "PARTIAL_FORMULA_COMPILER_CANDIDATE"
    return "FALLBACK_TEMPLATE_ONLY_NOT_FORMULA_READY"


def _primary_ready(family: str, available: set[str]) -> bool:
    if family == "K_BARRED_M2":
        return "bar_radius_kpc_source" in available
    if family == "K_RING_RESONANCE":
        return "ring_radius_kpc_source" in available
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        return "rdisk_kpc_source" in available
    if family == "K_DIFFUSE_LATE_DISK":
        return {"rdisk_kpc_source", "rhi_kpc_source", "diffuse_lsb_or_hi_dominance_source"}.issubset(available)
    if family == "K_COMPACT_EARLY_DISK":
        return {"rdisk_kpc_source", "compact_support_or_turnover_radius_source"}.issubset(available)
    return False


def _positive_radius_status(row: pd.Series, fields: list[str]) -> str:
    checked = [field for field in fields if field.endswith("_kpc_source")]
    if not checked:
        return "DIMENSION_CHECK_NOT_APPLICABLE"
    for field in checked:
        value = _float(row.get(field))
        if value is None or value <= 0.0:
            return "DIMENSION_CHECK_BLOCKED_MISSING_POSITIVE_RADIUS"
    return "DIMENSION_CHECK_PASS_POSITIVE_KPC_RADII"


def build_readiness() -> tuple[pd.DataFrame, dict[str, object]]:
    pilot = pd.read_csv(PILOT)
    coords = pd.read_csv(COORDINATE_FREEZE)
    route = pd.read_csv(ROUTE)
    mixture = pd.read_csv(MIXTURE_AUDIT)
    radial = pd.read_csv(RADIAL_GEOMETRY_FREEZE)

    data = (
        pilot[
            [
                "galaxy",
                "pilot_role",
                "source_family_candidate",
                "source_tier",
                "freeze_strength",
                "projection_caveat",
            ]
        ]
        .merge(
            coords[
                [
                    "galaxy",
                    "rdisk_kpc_source",
                    "rhi_kpc_source",
                    "bar_radius_kpc_source",
                    "ring_radius_kpc_source",
                    "bar_strength_proxy",
                    "ring_strength_proxy",
                    "spiral_pitch_median_abs_deg_source",
                    "kernel_center_kpc_source",
                    "kernel_width_kpc_source",
                    "kernel_coordinate_status",
                ]
            ],
            on="galaxy",
            how="left",
        )
        .merge(
            route[
                [
                    "galaxy",
                    "bar_ring_decomposition_route_status",
                    "feature_types_present",
                    "vizier_catalogs_used",
                ]
            ],
            on="galaxy",
            how="left",
        )
        .merge(
            mixture[
                [
                    "galaxy",
                    "component_mixture_status",
                    "active_source_native_components",
                    "source_native_component_count",
                ]
            ],
            on="galaxy",
            how="left",
        )
        .merge(
            radial[
                [
                    "galaxy",
                    "mixed_kernel_status",
                    "bar_component_weight",
                    "ring_component_weight",
                    "spiral_component_weight",
                    "fallback_family_proxy_weight",
                    "total_kernel_weight",
                ]
            ],
            on="galaxy",
            how="left",
        )
    )

    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        family = str(row["source_family_candidate"])
        required, optional = _required_observables(family)
        available = _available_observables(row)
        missing_required = [item for item in required if item not in available]
        missing_optional = [item for item in optional if item not in available]
        components = _available_formula_components(row)
        active = _active_components(row.get("active_source_native_components"))
        primary_ready = _primary_ready(family, available)
        status = _readiness_status(family, missing_required, primary_ready, components)
        formula = _formula_name(family, primary_ready, components)

        if status == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE":
            load_status = "SOURCE_GEOMETRY_READY_LOAD_REQUIRES_FROZEN_CARRIER_FOR_ENDPOINT_REPLAY"
            support_status = "SUPPORT_WINDOW_READY_FROM_SOURCE_COORDINATES_OR_DISK_SCALE"
            zero_status = "ZERO_SOURCE_LIMIT_DEFINED_FOR_ACTIVE_FORMULA"
        elif status == "PARTIAL_FORMULA_COMPILER_CANDIDATE":
            load_status = "SOURCE_LOAD_PARTIAL_REQUIRES_MISSING_OBSERVABLES_BEFORE_ENDPOINT_REPLAY"
            support_status = "SUPPORT_WINDOW_PARTIAL_OR_PROXY_ONLY"
            zero_status = "ZERO_SOURCE_LIMIT_DIAGNOSTIC_ONLY"
        else:
            load_status = "SOURCE_LOAD_BLOCKED_TEMPLATE_ONLY"
            support_status = "SUPPORT_WINDOW_NOT_FORMULA_READY"
            zero_status = "ZERO_SOURCE_LIMIT_NOT_AVAILABLE_FOR_TEMPLATE_FALLBACK"

        composition_status = (
            "SOURCE_NATIVE_COMPOSITION_READY"
            if len(active) > 1 and status == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
            else "SOURCE_NATIVE_COMPOSITION_PARTIAL"
            if len(active) > 1
            else "SINGLE_OR_NO_SOURCE_NATIVE_COMPOSITION"
        )

        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": family,
                "source_tier": row["source_tier"],
                "freeze_strength": row["freeze_strength"],
                "projection_caveat": row["projection_caveat"],
                "bar_ring_decomposition_route_status": row["bar_ring_decomposition_route_status"],
                "component_mixture_status": row["component_mixture_status"],
                "active_source_native_components": row["active_source_native_components"],
                "available_formula_components": ";".join(components) if components else "none",
                "compiler_readiness_status": status,
                "compiled_formula_family_candidate": formula,
                "required_source_observables": ";".join(required) if required else "none",
                "optional_source_observables": ";".join(optional) if optional else "none",
                "available_source_observables": ";".join(sorted(available)) if available else "none",
                "missing_source_observables": ";".join(missing_required) if missing_required else "none",
                "missing_optional_source_observables": ";".join(missing_optional) if missing_optional else "none",
                "source_load_rule_status": load_status,
                "support_window_status": support_status,
                "dimension_check_status": _positive_radius_status(row, required),
                "zero_source_limit_status": zero_status,
                "composition_rule_status": composition_status,
                "kernel_coordinate_status": row["kernel_coordinate_status"],
                "mixed_kernel_status": row["mixed_kernel_status"],
                "bar_component_weight": row["bar_component_weight"],
                "ring_component_weight": row["ring_component_weight"],
                "spiral_component_weight": row["spiral_component_weight"],
                "fallback_family_proxy_weight": row["fallback_family_proxy_weight"],
                "total_kernel_weight": row["total_kernel_weight"],
                "vizier_catalogs_used": row["vizier_catalogs_used"],
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    detail = pd.DataFrame(rows).sort_values(["compiler_readiness_status", "pilot_role", "source_family_candidate", "galaxy"]).reset_index(drop=True)
    holdout = detail[detail["pilot_role"] == "PILOT_HOLDOUT"].copy()
    summary = {
        "n_rows": int(len(detail)),
        "readiness_status_counts": {
            str(key): int(value)
            for key, value in detail["compiler_readiness_status"].value_counts().sort_index().items()
        },
        "holdout_readiness_status_counts": {
            str(key): int(value)
            for key, value in holdout["compiler_readiness_status"].value_counts().sort_index().items()
        },
        "ready_holdout_galaxies": sorted(
            holdout.loc[
                holdout["compiler_readiness_status"] == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE",
                "galaxy",
            ].tolist()
        ),
        "partial_holdout_galaxies": sorted(
            holdout.loc[
                holdout["compiler_readiness_status"] == "PARTIAL_FORMULA_COMPILER_CANDIDATE",
                "galaxy",
            ].tolist()
        ),
        "fallback_holdout_galaxies": sorted(
            holdout.loc[
                holdout["compiler_readiness_status"] == "FALLBACK_TEMPLATE_ONLY_NOT_FORMULA_READY",
                "galaxy",
            ].tolist()
        ),
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "This is a pre-scoring formula-compiler readiness manifest. It identifies which P0 "
            "galaxies have enough residual-blind source observables for source-frozen formula replay. "
            "It is not endpoint scoring and does not use rotation residuals, RMSE values, or endpoint scores."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_readiness()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
