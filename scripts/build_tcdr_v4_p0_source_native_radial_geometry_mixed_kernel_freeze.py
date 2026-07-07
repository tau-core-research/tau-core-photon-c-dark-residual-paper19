from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

MIXTURE_AUDIT = OUT_DIR / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"
COORDINATE_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
SOURCE_ROUTE = OUT_DIR / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
PILOT = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"
STRENGTH_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_v0_2.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_summary_v0_3.json"

WEIGHT_POLICY = (
    "source_native_radial_geometry_mixed_component_freeze_v0_3_"
    "strength_times_radial_zone_times_hierarchy_times_projection_reliability_no_endpoint_inputs"
)

COMPONENTS = ["bar", "ring", "spiral"]
PRIMARY_COMPONENT = {
    "K_BARRED_M2": "bar",
    "K_RING_RESONANCE": "ring",
    "K_EXPONENTIAL_SPIRAL_DISK": "spiral",
    "K_SCALE_TAIL_SPIRAL": "spiral",
}


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


def _active_components(text: object) -> list[str]:
    if text is None or pd.isna(text):
        return []
    return [item for item in str(text).split(";") if item in set(COMPONENTS)]


def _log_gaussian_window(x: float | None, centers: list[float], sigma: float, floor: float) -> float:
    if x is None or x <= 0:
        return 0.75
    best = max(math.exp(-0.5 * (math.log(x / center) / sigma) ** 2) for center in centers)
    return max(floor, min(1.0, floor + (1.0 - floor) * best))


def _arcsec_to_kpc(arcsec: float | None, distance_mpc: float | None) -> float | None:
    if arcsec is None or distance_mpc is None:
        return None
    return arcsec * distance_mpc * 1000.0 / 206265.0


def _radial_factor(component: str, row: pd.Series) -> float:
    rdisk = _float(row.get("rdisk_kpc_source"))
    rhi = _float(row.get("rhi_kpc_source"))
    distance = _float(row.get("distance_mpc_source"))
    if component == "bar":
        radius = _float(row.get("bar_radius_kpc_source"))
        ratio = None if rdisk is None or rdisk <= 0 or radius is None else radius / rdisk
        return _log_gaussian_window(ratio, centers=[1.0], sigma=math.log(2.2), floor=0.55)
    if component == "ring":
        radius = _float(row.get("ring_radius_kpc_source"))
        ratio = None if rdisk is None or rdisk <= 0 or radius is None else radius / rdisk
        disk_factor = _log_gaussian_window(ratio, centers=[0.6, 2.4], sigma=math.log(2.0), floor=0.60)
        if radius is None or rhi is None or rhi <= 0:
            return disk_factor
        hi_factor = 1.0 if radius <= rhi else 0.75
        return disk_factor * hi_factor
    if component == "spiral":
        inner_arcsec = _float(row.get("spiral_inner_radius_min_arcsec"))
        outer_arcsec = _float(row.get("spiral_outer_radius_max_arcsec"))
        outer_kpc = _arcsec_to_kpc(outer_arcsec, distance)
        inner_kpc = _arcsec_to_kpc(inner_arcsec, distance)
        if outer_kpc is None or outer_kpc <= 0:
            return 0.75
        if inner_kpc is None or inner_kpc < 0:
            span_factor = 0.75
        else:
            span_factor = min(1.0, max(0.55, (outer_kpc - inner_kpc) / outer_kpc))
        if rhi is not None and rhi > 0:
            reach_factor = min(1.0, max(0.55, outer_kpc / rhi))
        elif rdisk is not None and rdisk > 0:
            reach_factor = _log_gaussian_window(outer_kpc / rdisk, centers=[4.0], sigma=math.log(2.0), floor=0.55)
        else:
            reach_factor = 0.75
        return 0.5 * span_factor + 0.5 * reach_factor
    return 1.0


def _hierarchy_factor(component: str, row: pd.Series) -> float:
    primary = PRIMARY_COMPONENT.get(str(row.get("source_family_candidate")))
    if primary is None:
        return 1.0
    return 1.10 if component == primary else 0.95


def _projection_factor(component: str, row: pd.Series) -> float:
    inclination = _float(row.get("inclination_deg_for_projection_flag"))
    if inclination is None:
        return 1.0
    if component == "ring":
        return 0.95 if inclination >= 82.0 else 1.0
    if inclination >= 82.0:
        return 0.80
    if inclination >= 72.0:
        return 0.90
    return 1.0


def _component_score(component: str, row: pd.Series) -> tuple[float, float, float, float, float]:
    evidence = _float(row.get(f"{component}_source_evidence_score")) or 0.0
    radial = _radial_factor(component, row)
    hierarchy = _hierarchy_factor(component, row)
    projection = _projection_factor(component, row)
    return evidence * radial * hierarchy * projection, radial, hierarchy, projection, evidence


def _kernel_status(active: list[str]) -> str:
    if not active:
        return "fallback_family_proxy_kernel"
    if len(active) == 1:
        return "single_radial_geometry_source_native_component_kernel"
    return "mixed_radial_geometry_source_native_component_kernel"


def build_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    audit = pd.read_csv(MIXTURE_AUDIT)
    coords = pd.read_csv(COORDINATE_FREEZE)
    route = pd.read_csv(SOURCE_ROUTE)
    pilot = pd.read_csv(PILOT)
    strength = pd.read_csv(STRENGTH_FREEZE)

    detail = (
        audit.merge(
            coords[
                [
                    "galaxy",
                    "distance_mpc_source",
                    "rdisk_kpc_source",
                    "rhi_kpc_source",
                    "bar_radius_kpc_source",
                    "ring_radius_kpc_source",
                ]
            ],
            on="galaxy",
            how="left",
        )
        .merge(
            route[
                [
                    "galaxy",
                    "spiral_inner_radius_min_arcsec",
                    "spiral_outer_radius_max_arcsec",
                ]
            ],
            on="galaxy",
            how="left",
        )
        .merge(
            pilot[["galaxy", "inclination_deg_for_projection_flag", "projection_caveat"]],
            on="galaxy",
            how="left",
        )
        .merge(
            strength[
                [
                    "galaxy",
                    "bar_source_evidence_score",
                    "ring_source_evidence_score",
                    "spiral_source_evidence_score",
                ]
            ],
            on="galaxy",
            how="left",
        )
    )

    train_component_counts = (
        detail[detail["pilot_role"] == "PILOT_TRAIN_POOL"]["active_source_native_components"]
        .fillna("none")
        .apply(_active_components)
        .explode()
        .dropna()
        .value_counts()
        .to_dict()
    )

    rows: list[dict[str, object]] = []
    for _, row in detail.iterrows():
        active = _active_components(row["active_source_native_components"])
        raw_scores = {component: 0.0 for component in COMPONENTS}
        radial_factors = {component: 0.0 for component in COMPONENTS}
        hierarchy_factors = {component: 0.0 for component in COMPONENTS}
        projection_factors = {component: 0.0 for component in COMPONENTS}
        evidence_scores = {component: 0.0 for component in COMPONENTS}
        for component in active:
            score, radial, hierarchy, projection, evidence = _component_score(component, row)
            raw_scores[component] = score
            radial_factors[component] = radial
            hierarchy_factors[component] = hierarchy
            projection_factors[component] = projection
            evidence_scores[component] = evidence

        total_score = sum(raw_scores[component] for component in active)
        if not active:
            weights = {component: 0.0 for component in COMPONENTS}
            fallback = 1.0
        elif total_score <= 0:
            equal = 1.0 / len(active)
            weights = {component: (equal if component in active else 0.0) for component in COMPONENTS}
            fallback = 0.0
        else:
            weights = {component: (raw_scores[component] / total_score if component in active else 0.0) for component in COMPONENTS}
            fallback = 0.0

        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "component_mixture_status": row["component_mixture_status"],
                "active_source_native_components": row["active_source_native_components"],
                "mixed_kernel_status": _kernel_status(active),
                "bar_source_evidence_score": evidence_scores["bar"],
                "ring_source_evidence_score": evidence_scores["ring"],
                "spiral_source_evidence_score": evidence_scores["spiral"],
                "bar_radial_factor": radial_factors["bar"],
                "ring_radial_factor": radial_factors["ring"],
                "spiral_radial_factor": radial_factors["spiral"],
                "bar_hierarchy_factor": hierarchy_factors["bar"],
                "ring_hierarchy_factor": hierarchy_factors["ring"],
                "spiral_hierarchy_factor": hierarchy_factors["spiral"],
                "bar_projection_factor": projection_factors["bar"],
                "ring_projection_factor": projection_factors["ring"],
                "spiral_projection_factor": projection_factors["spiral"],
                "bar_raw_component_score": raw_scores["bar"],
                "ring_raw_component_score": raw_scores["ring"],
                "spiral_raw_component_score": raw_scores["spiral"],
                "bar_component_weight": weights["bar"],
                "ring_component_weight": weights["ring"],
                "spiral_component_weight": weights["spiral"],
                "fallback_family_proxy_weight": fallback,
                "total_kernel_weight": sum(weights.values()) + fallback,
                "projection_caveat": row.get("projection_caveat"),
                "train_support_bar_count": int(train_component_counts.get("bar", 0)),
                "train_support_ring_count": int(train_component_counts.get("ring", 0)),
                "train_support_spiral_count": int(train_component_counts.get("spiral", 0)),
                "weight_policy": WEIGHT_POLICY,
                "endpoint_data_policy": (
                    "do_not_use_rotation_residuals_or_endpoint_scores_for_radial_geometry_mixed_component_kernel_freeze"
                ),
                "claim_boundary": "source_native_radial_geometry_mixed_component_kernel_freeze_not_endpoint_validation",
            }
        )

    result = pd.DataFrame(rows).sort_values(["mixed_kernel_status", "source_family_candidate", "pilot_role", "galaxy"]).reset_index(drop=True)
    holdout = result[result["pilot_role"] == "PILOT_HOLDOUT"].copy()
    mixed_holdout = holdout[holdout["mixed_kernel_status"] == "mixed_radial_geometry_source_native_component_kernel"].copy()
    summary = {
        "n_rows": int(len(result)),
        "mixed_kernel_status_counts": {
            str(key): int(value)
            for key, value in result["mixed_kernel_status"].value_counts().sort_index().items()
        },
        "holdout_mixed_kernel_status_counts": {
            str(key): int(value)
            for key, value in holdout["mixed_kernel_status"].value_counts().sort_index().items()
        },
        "holdout_mixed_component_weights": mixed_holdout[
            [
                "galaxy",
                "bar_component_weight",
                "ring_component_weight",
                "spiral_component_weight",
            ]
        ].to_dict(orient="records"),
        "train_component_support_counts": {str(key): int(value) for key, value in train_component_counts.items()},
        "weight_policy": WEIGHT_POLICY,
        "endpoint_data_policy": (
            "do_not_use_rotation_residuals_or_endpoint_scores_for_radial_geometry_mixed_component_kernel_freeze"
        ),
        "verdict": (
            "The v0.3 mixed-component weights are frozen from source-side component evidence, "
            "source-native radial location, primary-family hierarchy, and conservative projection "
            "reliability factors. No rotation curve residuals or endpoint scores are used."
        ),
    }
    return result, summary


def main() -> None:
    detail, summary = build_freeze()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
