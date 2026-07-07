from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

KERNEL_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_source_native_coordinates_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_source_native_coordinates_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_source_native_coordinates_summary_local.json"

KERNEL_SHAPE_POLICY = (
    "source_native_bar_ring_coordinate_replay_v0_1_"
    "s4g_radius_when_available_proxy_fallback_no_holdout_shape_tuning"
)
SCORING_POLICY = (
    "holdout_only_matched_vs_calibrated_wrong_family_source_native_coordinate_"
    "replay_no_validation"
)


def _load_coordinate_freeze() -> pd.DataFrame:
    freeze = pd.read_csv(KERNEL_FREEZE)
    keep = [
        "galaxy",
        "bar_radius_kpc_source",
        "ring_radius_kpc_source",
        "spiral_pitch_median_abs_deg_source",
        "kernel_coordinate_status",
        "kernel_coordinate_rule",
    ]
    return freeze[keep].copy()


def _source_native_kernel(family: str, group: pd.DataFrame) -> pd.Series:
    fallback = base._kernel(family, group["radius_kpc"], group["rdisk_kpc"], group["rhi_kpc"]).copy()
    radius = group["radius_kpc"].astype(float)
    rdisk = group["rdisk_kpc"].replace(0, np.nan).astype(float)

    if family == "K_BARRED_M2":
        center = pd.to_numeric(group.get("bar_radius_kpc_source"), errors="coerce")
        width = np.maximum(0.35 * center, 0.20 * rdisk)
        mask = center.notna() & width.notna() & (center > 0) & (width > 0)
        if mask.any():
            fallback.loc[mask] = np.exp(-0.5 * ((radius.loc[mask] - center.loc[mask]) / width.loc[mask]) ** 2)
    elif family == "K_RING_RESONANCE":
        center = pd.to_numeric(group.get("ring_radius_kpc_source"), errors="coerce")
        width = np.maximum(0.18 * center, 0.20 * rdisk)
        mask = center.notna() & width.notna() & (center > 0) & (width > 0)
        if mask.any():
            fallback.loc[mask] = np.exp(-0.5 * ((radius.loc[mask] - center.loc[mask]) / width.loc[mask]) ** 2)
    return fallback.clip(lower=0)


def _fit_amplitude(train: pd.DataFrame, family: str) -> float:
    subset = train[train["source_family_candidate"] == family].copy()
    if subset.empty:
        return 0.0
    k = _source_native_kernel(family, subset).to_numpy()
    y = subset["y_residual_v2"].to_numpy()
    w = 1.0 / (subset["sigma_v2"].to_numpy() ** 2)
    denom = float(np.sum(w * k * k))
    if denom <= 0:
        return 0.0
    amp = float(np.sum(w * k * y) / denom)
    return max(0.0, amp)


def _family_calibration(train: pd.DataFrame) -> dict[str, dict[str, object]]:
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
        else:
            calibration[family] = {
                "family_amplitude_v2": _fit_amplitude(train, family),
                "n_train_galaxies": n_galaxies,
                "n_train_points": n_points,
                "calibration_status": "calibrated_min2_train_galaxies",
            }
    return calibration


def _rmse(group: pd.DataFrame, family: str, amp: float) -> tuple[float, float]:
    k = _source_native_kernel(family, group)
    vpred2 = (group["vbar2_fixed_mlr"] + amp * k).clip(lower=0)
    vpred = np.sqrt(vpred2)
    residual = group["vobs_kms"] - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(np.sqrt(np.average(residual**2, weights=1.0 / group["e_vobs_kms"].clip(lower=1.0) ** 2)))
    return rmse, wrmse


def run_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
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
    meta = pd.DataFrame(meta_rows)
    coordinate_freeze = _load_coordinate_freeze()
    meta = meta.merge(coordinate_freeze, on="galaxy", how="left")
    data = curves.merge(meta, on="galaxy", how="inner")
    train = data[data["pilot_role"] == "PILOT_TRAIN_POOL"].copy()
    holdout = data[data["pilot_role"] == "PILOT_HOLDOUT"].copy()

    calibration = _family_calibration(train)
    amplitudes = {
        family: float(values["family_amplitude_v2"]) for family, values in calibration.items()
    }
    calibrated_families = {
        family
        for family, values in calibration.items()
        if values["calibration_status"] == "calibrated_min2_train_galaxies"
    }

    detail_rows = []
    summary_rows = []
    for galaxy, group in holdout.groupby("galaxy", sort=True):
        matched_family = str(group["source_family_candidate"].iloc[0])
        baseline_rmse, baseline_wrmse = _rmse(group, matched_family, 0.0)
        coordinate_status = str(group["kernel_coordinate_status"].iloc[0])
        family_scores = {}
        for family in base.FAMILIES:
            rmse, wrmse = _rmse(group, family, amplitudes[family])
            family_scores[family] = {"rmse": rmse, "wrmse": wrmse}
            calibration_row = calibration[family]
            detail_rows.append(
                {
                    "galaxy": galaxy,
                    "matched_source_family": matched_family,
                    "matched_kernel_coordinate_status": coordinate_status,
                    "scored_family": family,
                    "is_matched_family": "yes" if family == matched_family else "no",
                    "is_calibrated_family": "yes" if family in calibrated_families else "no",
                    "n_points": int(len(group)),
                    "rmse_kms": rmse,
                    "weighted_rmse_kms": wrmse,
                    "baseline_carrier_rmse_kms": baseline_rmse,
                    "baseline_carrier_weighted_rmse_kms": baseline_wrmse,
                    "family_amplitude_v2": amplitudes[family],
                    "family_train_galaxy_count": calibration_row["n_train_galaxies"],
                    "family_train_point_count": calibration_row["n_train_points"],
                    "family_calibration_status": calibration_row["calibration_status"],
                    "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                    "carrier_policy": base.CARRIER_POLICY,
                    "amplitude_policy": base.AMPLITUDE_POLICY,
                    "scoring_policy": SCORING_POLICY,
                }
            )
        matched_status = str(calibration[matched_family]["calibration_status"])
        wrong = [
            value["wrmse"]
            for fam, value in family_scores.items()
            if fam != matched_family and fam in calibrated_families
        ]
        scoreable = matched_family in calibrated_families and len(wrong) > 0
        if scoreable:
            matched = float(family_scores[matched_family]["wrmse"])
            wrong_mean = float(np.mean(wrong))
            wrong_best = float(np.min(wrong))
            matched_minus_baseline = matched - baseline_wrmse
            wrong_mean_minus_matched = wrong_mean - matched
            best_wrong_minus_matched = wrong_best - matched
        else:
            matched = float("nan")
            wrong_mean = float("nan")
            wrong_best = float("nan")
            matched_minus_baseline = float("nan")
            wrong_mean_minus_matched = float("nan")
            best_wrong_minus_matched = float("nan")
        summary_rows.append(
            {
                "galaxy": galaxy,
                "matched_source_family": matched_family,
                "matched_kernel_coordinate_status": coordinate_status,
                "n_points": int(len(group)),
                "baseline_carrier_weighted_rmse_kms": baseline_wrmse,
                "matched_weighted_rmse_kms": matched,
                "wrong_family_mean_weighted_rmse_kms": wrong_mean,
                "best_wrong_family_weighted_rmse_kms": wrong_best,
                "matched_minus_baseline_weighted_rmse_kms": matched_minus_baseline,
                "wrong_mean_minus_matched_weighted_rmse_kms": wrong_mean_minus_matched,
                "best_wrong_minus_matched_weighted_rmse_kms": best_wrong_minus_matched,
                "matched_beats_baryonic_carrier": "yes" if scoreable and matched < baseline_wrmse else "no",
                "matched_beats_wrong_mean": "yes" if scoreable and matched < wrong_mean else "no",
                "matched_beats_best_wrong": "yes" if scoreable and matched < wrong_best else "no",
                "endpoint_scoring_status": "scoreable" if scoreable else "calibration_blocked",
                "matched_family_calibration_status": matched_status,
                "n_calibrated_wrong_family_controls": int(len(wrong)),
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "carrier_policy": base.CARRIER_POLICY,
                "amplitude_policy": base.AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
            }
        )

    detail = pd.DataFrame(detail_rows).sort_values(["galaxy", "scored_family"])
    summary = pd.DataFrame(summary_rows).sort_values(["matched_source_family", "galaxy"])
    scoreable_summary = summary[summary["endpoint_scoring_status"] == "scoreable"].copy()
    aggregate = {
        "n_train_pool_galaxies": int(train["galaxy"].nunique()),
        "n_holdout_galaxies": int(holdout["galaxy"].nunique()),
        "n_scoreable_holdout_galaxies": int(len(scoreable_summary)),
        "n_calibration_blocked_holdout_galaxies": int(
            (summary["endpoint_scoring_status"] == "calibration_blocked").sum()
        ),
        "n_train_points": int(len(train)),
        "n_holdout_points": int(len(holdout)),
        "family_amplitudes_v2": amplitudes,
        "family_calibration": calibration,
        "matched_beats_baryonic_carrier": int(
            (scoreable_summary["matched_beats_baryonic_carrier"] == "yes").sum()
        ),
        "matched_beats_wrong_mean": int(
            (scoreable_summary["matched_beats_wrong_mean"] == "yes").sum()
        ),
        "matched_beats_best_wrong": int(
            (scoreable_summary["matched_beats_best_wrong"] == "yes").sum()
        ),
        "median_wrong_mean_minus_matched_weighted_rmse_kms": float(
            scoreable_summary["wrong_mean_minus_matched_weighted_rmse_kms"].median()
        )
        if not scoreable_summary.empty
        else None,
        "median_best_wrong_minus_matched_weighted_rmse_kms": float(
            scoreable_summary["best_wrong_minus_matched_weighted_rmse_kms"].median()
        )
        if not scoreable_summary.empty
        else None,
        "median_matched_minus_baseline_weighted_rmse_kms": float(
            scoreable_summary["matched_minus_baseline_weighted_rmse_kms"].median()
        )
        if not scoreable_summary.empty
        else None,
        "carrier_policy": base.CARRIER_POLICY,
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "amplitude_policy": base.AMPLITUDE_POLICY,
        "scoring_policy": SCORING_POLICY,
        "claim_boundary": "local_preflight_endpoint_scoring_not_population_validation",
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
