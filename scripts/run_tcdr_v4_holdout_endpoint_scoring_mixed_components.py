from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring as base
from run_tcdr_v4_holdout_endpoint_scoring_source_native_coordinates import _source_native_kernel


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

KERNEL_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
MIXED_KERNEL_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_v0_1.csv"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_mixed_components_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_mixed_components_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_mixed_components_summary_local.json"

MIXED_MODEL = "K_SOURCE_NATIVE_MIXED_COMPONENT"
KERNEL_SHAPE_POLICY = (
    "source_native_mixed_component_kernel_freeze_v0_1_primary_0p5_secondary_equal_"
    "when_multicomponent_proxy_fallback_no_holdout_shape_tuning"
)
AMPLITUDE_POLICY = (
    "single_mixed_component_amplitude_fit_on_pilot_train_pool_only_"
    "nonnegative_weighted_no_holdout_tuning"
)
SCORING_POLICY = (
    "holdout_only_mixed_component_vs_pure_family_controls_no_validation"
)


def _load_source_meta() -> pd.DataFrame:
    freeze = pd.read_csv(KERNEL_FREEZE)
    mixed_freeze = pd.read_csv(MIXED_KERNEL_FREEZE)
    keep_freeze = [
        "galaxy",
        "bar_radius_kpc_source",
        "ring_radius_kpc_source",
        "spiral_pitch_median_abs_deg_source",
        "kernel_coordinate_status",
    ]
    keep_mixed = [
        "galaxy",
        "component_mixture_status",
        "active_source_native_components",
        "mixed_kernel_status",
        "bar_component_weight",
        "ring_component_weight",
        "spiral_component_weight",
        "fallback_family_proxy_weight",
    ]
    return freeze[keep_freeze].merge(mixed_freeze[keep_mixed], on="galaxy", how="left")


def _component_kernel(component: str, group: pd.DataFrame) -> pd.Series:
    if component == "bar":
        return _source_native_kernel("K_BARRED_M2", group)
    if component == "ring":
        return _source_native_kernel("K_RING_RESONANCE", group)
    if component == "spiral":
        return _source_native_kernel("K_EXPONENTIAL_SPIRAL_DISK", group)
    return _source_native_kernel(str(group["source_family_candidate"].iloc[0]), group)


def _mixed_kernel_for_group(group: pd.DataFrame) -> pd.Series:
    family = str(group["source_family_candidate"].iloc[0])
    fallback_weight = float(group["fallback_family_proxy_weight"].iloc[0] or 0.0)
    component_weights = {
        "bar": float(group["bar_component_weight"].iloc[0] or 0.0),
        "ring": float(group["ring_component_weight"].iloc[0] or 0.0),
        "spiral": float(group["spiral_component_weight"].iloc[0] or 0.0),
    }
    if fallback_weight >= 1.0:
        return _source_native_kernel(family, group)

    result = pd.Series(0.0, index=group.index)
    for component, weight in component_weights.items():
        if weight > 0:
            result = result + weight * _component_kernel(component, group)
    if float(result.sum()) == 0.0:
        return _source_native_kernel(family, group)
    return result.clip(lower=0)


def _mixed_kernel(data: pd.DataFrame) -> pd.Series:
    pieces = []
    for _, group in data.groupby("galaxy", sort=False):
        pieces.append(_mixed_kernel_for_group(group))
    if not pieces:
        return pd.Series(dtype=float)
    return pd.concat(pieces).sort_index()


def _fit_mixed_amplitude(train: pd.DataFrame) -> float:
    k = _mixed_kernel(train).to_numpy()
    y = train["y_residual_v2"].to_numpy()
    w = 1.0 / (train["sigma_v2"].to_numpy() ** 2)
    denom = float(np.sum(w * k * k))
    if denom <= 0:
        return 0.0
    amp = float(np.sum(w * k * y) / denom)
    return max(0.0, amp)


def _rmse_with_kernel(group: pd.DataFrame, kernel: pd.Series, amp: float) -> tuple[float, float]:
    vpred2 = (group["vbar2_fixed_mlr"] + amp * kernel).clip(lower=0)
    vpred = np.sqrt(vpred2)
    residual = group["vobs_kms"] - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(np.sqrt(np.average(residual**2, weights=1.0 / group["e_vobs_kms"].clip(lower=1.0) ** 2)))
    return rmse, wrmse


def _pure_rmse(group: pd.DataFrame, family: str, amp: float) -> tuple[float, float]:
    return _rmse_with_kernel(group, _source_native_kernel(family, group), amp)


def _fit_pure_amplitudes(train: pd.DataFrame) -> dict[str, dict[str, object]]:
    calibration: dict[str, dict[str, object]] = {}
    for family in base.FAMILIES:
        subset = train[train["source_family_candidate"] == family].copy()
        n_galaxies = int(subset["galaxy"].nunique())
        n_points = int(len(subset))
        if n_galaxies < base.MIN_TRAIN_GALAXIES_PER_FAMILY:
            calibration[family] = {
                "family_amplitude_v2": 0.0,
                "n_train_galaxies": n_galaxies,
                "n_train_points": n_points,
                "calibration_status": "calibration_blocked_underpowered_train_family",
            }
            continue
        k = _source_native_kernel(family, subset).to_numpy()
        y = subset["y_residual_v2"].to_numpy()
        w = 1.0 / (subset["sigma_v2"].to_numpy() ** 2)
        denom = float(np.sum(w * k * k))
        amp = 0.0 if denom <= 0 else max(0.0, float(np.sum(w * k * y) / denom))
        calibration[family] = {
            "family_amplitude_v2": amp,
            "n_train_galaxies": n_galaxies,
            "n_train_points": n_points,
            "calibration_status": "calibrated_min2_train_galaxies",
        }
    return calibration


def _load_data() -> pd.DataFrame:
    pilot = pd.read_csv(base.PILOT)
    pilot = pilot[pilot["pilot_role"].isin(["PILOT_HOLDOUT", "PILOT_TRAIN_POOL"])].copy()
    galaxies = set(str(g) for g in pilot["galaxy"])
    sample = base._sample_rows(galaxies)
    curves = base._mass_model_rows(galaxies)
    if curves.empty:
        raise RuntimeError("No local SPARC endpoint rows found. Run/download SPARC preflight first.")

    meta_rows = []
    for _, row in pilot.iterrows():
        galaxy = str(row["galaxy"])
        sample_meta = sample.get(galaxy)
        if sample_meta is None:
            continue
        meta_rows.append(
            {
                "galaxy": galaxy,
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "projection_caveat": row["projection_caveat"],
                **sample_meta,
            }
        )
    meta = pd.DataFrame(meta_rows).merge(_load_source_meta(), on="galaxy", how="left")
    return curves.merge(meta, on="galaxy", how="inner")


def run_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    data = _load_data()
    train = data[data["pilot_role"] == "PILOT_TRAIN_POOL"].copy()
    holdout = data[data["pilot_role"] == "PILOT_HOLDOUT"].copy()

    pure_calibration = _fit_pure_amplitudes(train)
    pure_amplitudes = {
        family: float(values["family_amplitude_v2"]) for family, values in pure_calibration.items()
    }
    calibrated_families = {
        family
        for family, values in pure_calibration.items()
        if values["calibration_status"] == "calibrated_min2_train_galaxies"
    }
    mixed_amp = _fit_mixed_amplitude(train)

    detail_rows = []
    summary_rows = []
    for galaxy, group in holdout.groupby("galaxy", sort=True):
        matched_family = str(group["source_family_candidate"].iloc[0])
        component_status = str(group["component_mixture_status"].iloc[0])
        active_components = str(group["active_source_native_components"].iloc[0])
        baseline_rmse, baseline_wrmse = _pure_rmse(group, matched_family, 0.0)
        mixed_rmse, mixed_wrmse = _rmse_with_kernel(group, _mixed_kernel_for_group(group), mixed_amp)
        family_scores = {}
        for family in base.FAMILIES:
            rmse, wrmse = _pure_rmse(group, family, pure_amplitudes[family])
            family_scores[family] = {"rmse": rmse, "wrmse": wrmse}
            detail_rows.append(
                {
                    "galaxy": galaxy,
                    "matched_source_family": matched_family,
                    "component_mixture_status": component_status,
                    "active_source_native_components": active_components,
                    "scored_model": family,
                    "model_type": "pure_family",
                    "n_points": int(len(group)),
                    "rmse_kms": rmse,
                    "weighted_rmse_kms": wrmse,
                    "amplitude_v2": pure_amplitudes[family],
                    "calibration_status": pure_calibration[family]["calibration_status"],
                    "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                    "carrier_policy": base.CARRIER_POLICY,
                    "amplitude_policy": AMPLITUDE_POLICY,
                    "scoring_policy": SCORING_POLICY,
                }
            )
        detail_rows.append(
            {
                "galaxy": galaxy,
                "matched_source_family": matched_family,
                "component_mixture_status": component_status,
                "active_source_native_components": active_components,
                "scored_model": MIXED_MODEL,
                "model_type": "mixed_component",
                "n_points": int(len(group)),
                "rmse_kms": mixed_rmse,
                "weighted_rmse_kms": mixed_wrmse,
                "amplitude_v2": mixed_amp,
                "calibration_status": "calibrated_single_mixed_train_pool_amplitude",
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "carrier_policy": base.CARRIER_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
            }
        )

        wrong = [
            value["wrmse"]
            for fam, value in family_scores.items()
            if fam != matched_family and fam in calibrated_families
        ]
        scoreable = matched_family in calibrated_families and len(wrong) > 0
        matched_wrmse = float(family_scores[matched_family]["wrmse"]) if matched_family in family_scores else float("nan")
        if scoreable:
            wrong_mean = float(np.mean(wrong))
            wrong_best = float(np.min(wrong))
        else:
            wrong_mean = float("nan")
            wrong_best = float("nan")
        summary_rows.append(
            {
                "galaxy": galaxy,
                "matched_source_family": matched_family,
                "component_mixture_status": component_status,
                "active_source_native_components": active_components,
                "n_points": int(len(group)),
                "baseline_carrier_weighted_rmse_kms": baseline_wrmse,
                "pure_matched_weighted_rmse_kms": matched_wrmse,
                "mixed_component_weighted_rmse_kms": mixed_wrmse,
                "wrong_family_mean_weighted_rmse_kms": wrong_mean,
                "best_wrong_family_weighted_rmse_kms": wrong_best,
                "mixed_minus_pure_matched_weighted_rmse_kms": mixed_wrmse - matched_wrmse if scoreable else float("nan"),
                "mixed_minus_baryonic_carrier_weighted_rmse_kms": mixed_wrmse - baseline_wrmse if scoreable else float("nan"),
                "wrong_mean_minus_mixed_weighted_rmse_kms": wrong_mean - mixed_wrmse if scoreable else float("nan"),
                "best_wrong_minus_mixed_weighted_rmse_kms": wrong_best - mixed_wrmse if scoreable else float("nan"),
                "mixed_beats_pure_matched": "yes" if scoreable and mixed_wrmse < matched_wrmse else "no",
                "mixed_beats_baryonic_carrier": "yes" if scoreable and mixed_wrmse < baseline_wrmse else "no",
                "mixed_beats_wrong_mean": "yes" if scoreable and mixed_wrmse < wrong_mean else "no",
                "mixed_beats_best_wrong": "yes" if scoreable and mixed_wrmse < wrong_best else "no",
                "endpoint_scoring_status": "scoreable" if scoreable else "calibration_blocked",
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "carrier_policy": base.CARRIER_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
            }
        )

    detail = pd.DataFrame(detail_rows).sort_values(["galaxy", "model_type", "scored_model"])
    summary = pd.DataFrame(summary_rows).sort_values(["component_mixture_status", "galaxy"])
    scoreable_summary = summary[summary["endpoint_scoring_status"] == "scoreable"].copy()
    mixed_scoreable = scoreable_summary[
        scoreable_summary["component_mixture_status"] == "mixed_source_native_multicomponent"
    ].copy()
    aggregate = {
        "n_train_pool_galaxies": int(train["galaxy"].nunique()),
        "n_holdout_galaxies": int(holdout["galaxy"].nunique()),
        "n_scoreable_holdout_galaxies": int(len(scoreable_summary)),
        "n_mixed_scoreable_holdout_galaxies": int(len(mixed_scoreable)),
        "n_train_points": int(len(train)),
        "n_holdout_points": int(len(holdout)),
        "mixed_component_amplitude_v2": mixed_amp,
        "pure_family_amplitudes_v2": pure_amplitudes,
        "mixed_beats_pure_matched": int((scoreable_summary["mixed_beats_pure_matched"] == "yes").sum()),
        "mixed_beats_baryonic_carrier": int((scoreable_summary["mixed_beats_baryonic_carrier"] == "yes").sum()),
        "mixed_beats_wrong_mean": int((scoreable_summary["mixed_beats_wrong_mean"] == "yes").sum()),
        "mixed_beats_best_wrong": int((scoreable_summary["mixed_beats_best_wrong"] == "yes").sum()),
        "mixed_objects_mixed_beats_pure_matched": int((mixed_scoreable["mixed_beats_pure_matched"] == "yes").sum()),
        "mixed_objects_mixed_beats_wrong_mean": int((mixed_scoreable["mixed_beats_wrong_mean"] == "yes").sum()),
        "median_mixed_minus_pure_matched_weighted_rmse_kms": float(
            scoreable_summary["mixed_minus_pure_matched_weighted_rmse_kms"].median()
        )
        if not scoreable_summary.empty
        else None,
        "median_wrong_mean_minus_mixed_weighted_rmse_kms": float(
            scoreable_summary["wrong_mean_minus_mixed_weighted_rmse_kms"].median()
        )
        if not scoreable_summary.empty
        else None,
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "carrier_policy": base.CARRIER_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
        "scoring_policy": SCORING_POLICY,
        "claim_boundary": "local_preflight_mixed_component_diagnostic_not_population_validation",
    }
    return detail, summary, aggregate


def main() -> None:
    detail, summary, aggregate = run_scoring()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    summary.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(aggregate, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
