from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
PILOT = SOURCE_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"
SAMPLE = EXTERNAL_DIR / "SPARC_Lelli2016c.mrt"
MASS_MODELS = EXTERNAL_DIR / "MassModels_Lelli2016c.mrt"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_summary_local.json"

FAMILIES = [
    "K_BARRED_M2",
    "K_DIFFUSE_LATE_DISK",
    "K_EXPONENTIAL_SPIRAL_DISK",
    "K_RING_RESONANCE",
]

CARRIER_POLICY = "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_amplitude_fit"
MIN_TRAIN_GALAXIES_PER_FAMILY = 2
KERNEL_SHAPE_POLICY = "train_pool_only_specificity_first_v4_penalty_1p5_no_holdout_shape_tuning"
AMPLITUDE_POLICY = (
    "family_amplitude_fit_on_pilot_train_pool_only_nonnegative_weighted_v3_"
    "specificity_guarded_min2_train"
)
SCORING_POLICY = (
    "holdout_only_matched_vs_calibrated_wrong_family_specificity_guarded_"
    "preflight_no_validation"
)


def _sample_rows(galaxies: set[str]) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    for line in SAMPLE.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if not parts or parts[0] not in galaxies:
            continue
        rows[parts[0]] = {
            "distance_mpc": float(parts[2]),
            "inclination_deg": float(parts[5]),
            "rdisk_kpc": float(parts[11]),
            "rhi_kpc": float(parts[14]),
            "quality_flag": float(parts[17]),
        }
    return rows


def _mass_model_rows(galaxies: set[str]) -> pd.DataFrame:
    rows = []
    for line in MASS_MODELS.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if not parts or parts[0] not in galaxies:
            continue
        rows.append(
            {
                "galaxy": parts[0],
                "distance_mpc": float(parts[1]),
                "radius_kpc": float(parts[2]),
                "vobs_kms": float(parts[3]),
                "e_vobs_kms": float(parts[4]),
                "vgas_kms": float(parts[5]),
                "vdisk_kms": float(parts[6]),
                "vbul_kms": float(parts[7]),
            }
        )
    detail = pd.DataFrame(rows)
    if detail.empty:
        return detail
    vbar2 = (
        detail["vgas_kms"] * detail["vgas_kms"].abs()
        + 0.5 * detail["vdisk_kms"] ** 2
        + 0.7 * detail["vbul_kms"] ** 2
    )
    detail["vbar2_fixed_mlr"] = vbar2
    detail["vbar_fixed_mlr_kms"] = vbar2.map(lambda x: math.sqrt(x) if x > 0 else 0.0)
    detail["y_residual_v2"] = detail["vobs_kms"] ** 2 - detail["vbar2_fixed_mlr"]
    detail["sigma_v2"] = (2.0 * detail["vobs_kms"].abs() * detail["e_vobs_kms"].clip(lower=1.0)).clip(lower=1.0)
    return detail


def _kernel(family: str, radius: pd.Series, rdisk: pd.Series, rhi: pd.Series) -> pd.Series:
    rd = rdisk.replace(0, np.nan).fillna(rdisk[rdisk > 0].median())
    rh = rhi.replace(0, np.nan).fillna(rhi[rhi > 0].median())
    x = (radius / rd).clip(lower=0)
    h = (radius / rh).clip(lower=0)
    if family == "K_BARRED_M2":
        # Specificity-first train-pool scan selects compact inner/mid-disk
        # support: a bar control should not behave like a generic outer tail.
        return (x**1.2 * np.exp(-x / 0.45) / (1.0 + np.exp((x - 1.6) / 0.35))).clip(lower=0)
    if family == "K_DIFFUSE_LATE_DISK":
        # HI-dominated support must turn on late; otherwise this family becomes
        # a generic outer-tail control for ordinary disks.
        radial_gate = 1.0 / (1.0 + np.exp(-(x - 2.5) / 0.35))
        return ((1.0 - np.exp(-h / 0.45)) * radial_gate).clip(lower=0)
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        # Ordinary exponential disks get a disk-scale bump with an explicit
        # outer guard. This intentionally avoids the old saturating tail that
        # acted as a near-universal missing-velocity control.
        outer_guard = 1.0 / (1.0 + np.exp((x - 2.5) / 0.2))
        return ((x / 1.4) * np.exp(1.0 - x / 1.4) * outer_guard).clip(lower=0)
    if family == "K_RING_RESONANCE":
        # Specificity-first narrow shell. A broad ring kernel too easily
        # becomes an ordinary-disk correction in wrong-family controls.
        return np.exp(-0.5 * ((x - 1.4) / 0.18) ** 2)
    raise ValueError(f"unknown family: {family}")


def _fit_amplitude(train: pd.DataFrame, family: str) -> float:
    subset = train[train["source_family_candidate"] == family].copy()
    if subset.empty:
        return 0.0
    k = _kernel(family, subset["radius_kpc"], subset["rdisk_kpc"], subset["rhi_kpc"]).to_numpy()
    y = subset["y_residual_v2"].to_numpy()
    w = 1.0 / (subset["sigma_v2"].to_numpy() ** 2)
    denom = float(np.sum(w * k * k))
    if denom <= 0:
        return 0.0
    amp = float(np.sum(w * k * y) / denom)
    return max(0.0, amp)


def _family_calibration(train: pd.DataFrame) -> dict[str, dict[str, object]]:
    calibration: dict[str, dict[str, object]] = {}
    for family in FAMILIES:
        subset = train[train["source_family_candidate"] == family].copy()
        n_galaxies = int(subset["galaxy"].nunique())
        n_points = int(len(subset))
        if n_galaxies < MIN_TRAIN_GALAXIES_PER_FAMILY:
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
    k = _kernel(family, group["radius_kpc"], group["rdisk_kpc"], group["rhi_kpc"])
    vpred2 = (group["vbar2_fixed_mlr"] + amp * k).clip(lower=0)
    vpred = np.sqrt(vpred2)
    residual = group["vobs_kms"] - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(np.sqrt(np.average(residual**2, weights=1.0 / group["e_vobs_kms"].clip(lower=1.0) ** 2)))
    return rmse, wrmse


def run_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    pilot = pd.read_csv(PILOT)
    pilot = pilot[pilot["pilot_role"].isin(["PILOT_HOLDOUT", "PILOT_TRAIN_POOL"])].copy()
    galaxies = set(str(g) for g in pilot["galaxy"])
    sample = _sample_rows(galaxies)
    curves = _mass_model_rows(galaxies)
    if curves.empty:
        raise RuntimeError("No local SPARC endpoint rows found. Run/download SPARC preflight first.")

    meta_rows = []
    for _, row in pilot.iterrows():
        galaxy = str(row["galaxy"])
        meta = sample.get(galaxy)
        if meta is None:
            continue
        meta_rows.append(
            {
                "galaxy": galaxy,
                "pilot_role": row["pilot_role"],
                "source_family_candidate": row["source_family_candidate"],
                "projection_caveat": row["projection_caveat"],
                **meta,
            }
        )
    meta = pd.DataFrame(meta_rows)
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
        family_scores = {}
        for family in FAMILIES:
            rmse, wrmse = _rmse(group, family, amplitudes[family])
            family_scores[family] = {"rmse": rmse, "wrmse": wrmse}
            calibration_row = calibration[family]
            detail_rows.append(
                {
                    "galaxy": galaxy,
                    "matched_source_family": matched_family,
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
                    "carrier_policy": CARRIER_POLICY,
                    "amplitude_policy": AMPLITUDE_POLICY,
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
                "carrier_policy": CARRIER_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
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
        "carrier_policy": CARRIER_POLICY,
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
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
