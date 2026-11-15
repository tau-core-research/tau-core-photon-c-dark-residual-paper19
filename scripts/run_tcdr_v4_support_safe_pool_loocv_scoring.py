from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring as base
from run_tcdr_v4_holdout_endpoint_scoring_source_native_coordinates import (
    _source_native_kernel,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

POOL7 = SOURCE_DIR / "tcdr_v4_p0_support_safe_expansion_manifest_v0_7.csv"
POOL10 = SOURCE_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"
COORDINATES = SOURCE_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
SUPPORT = SOURCE_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_support_safe_pool_loocv_scoring_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_support_safe_pool_loocv_scoring_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_support_safe_pool_loocv_scoring_summary_local.json"

COMPONENTS = ("bar", "ring", "spiral")
POOL_CONFIGS = {
    "support_safe_7_v0_7": {
        "manifest": POOL7,
        "pool_role_column": "selector_expansion_role",
        "pool_roles": {
            "EXISTING_SUPPORT_SAFE_HOLDOUT",
            "SUPPORT_SAFE_HOLDOUT_EXPANSION_CANDIDATE",
        },
        "claim_boundary": "support_safe_7_pool_loocv_diagnostic_not_validation",
    },
    "support_safe_10_v0_9": {
        "manifest": POOL10,
        "pool_role_column": "support_safe_10_pool_role",
        "pool_roles": {
            "SUPPORT_SAFE_10_POOL_READY_CARRIED_FROM_V0_7",
            "SUPPORT_SAFE_10_POOL_READY_BY_COMPONENT_ROUTE_COMPLETION",
        },
        "claim_boundary": "support_safe_10_pool_loocv_diagnostic_not_validation",
    },
}

SCORING_POLICY = (
    "support_safe_pool_leave_one_galaxy_out_local_endpoint_diagnostic_"
    "candidate_and_component_controls_share_same_pool_cv_no_population_validation"
)
AMPLITUDE_POLICY = (
    "nonnegative_weighted_v2_amplitude_fit_on_other_pool_galaxies_only_"
    "no_target_galaxy_endpoint_tuning"
)
KERNEL_SHAPE_POLICY = (
    "source_native_support_safe_component_route_bar_ring_spiral_"
    "from_frozen_v0_7_v0_9_manifests"
)


def _component_kernel(component: str, group: pd.DataFrame) -> pd.Series:
    if component == "bar":
        return _source_native_kernel("K_BARRED_M2", group)
    if component == "ring":
        return _source_native_kernel("K_RING_RESONANCE", group)
    if component == "spiral":
        return _source_native_kernel("K_EXPONENTIAL_SPIRAL_DISK", group)
    raise ValueError(f"unknown component: {component}")


def _candidate_kernel(data: pd.DataFrame) -> pd.Series:
    pieces: list[pd.Series] = []
    for _, group in data.groupby("galaxy", sort=False):
        component = str(group["top_component"].iloc[0])
        pieces.append(_component_kernel(component, group))
    if not pieces:
        return pd.Series(dtype=float)
    return pd.concat(pieces).sort_index()


def _fit_amplitude(train: pd.DataFrame, kernel: pd.Series) -> float:
    if train.empty or kernel.empty:
        return 0.0
    k = kernel.loc[train.index].to_numpy()
    y = train["y_residual_v2"].to_numpy()
    w = 1.0 / (train["sigma_v2"].to_numpy() ** 2)
    denom = float(np.sum(w * k * k))
    if denom <= 0.0:
        return 0.0
    return max(0.0, float(np.sum(w * k * y) / denom))


def _weighted_rmse(group: pd.DataFrame, kernel: pd.Series, amp: float) -> tuple[float, float]:
    vpred2 = (group["vbar2_fixed_mlr"] + amp * kernel.loc[group.index]).clip(lower=0)
    vpred = np.sqrt(vpred2)
    residual = group["vobs_kms"] - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(
        np.sqrt(
            np.average(
                residual**2,
                weights=1.0 / group["e_vobs_kms"].clip(lower=1.0) ** 2,
            )
        )
    )
    return rmse, wrmse


def _pool_manifest(pool_name: str, config: dict[str, object]) -> pd.DataFrame:
    manifest = pd.read_csv(config["manifest"])
    role_col = str(config["pool_role_column"])
    pool_roles = set(config["pool_roles"])
    pool = manifest[manifest[role_col].isin(pool_roles)].copy()
    keep = [
        "galaxy",
        "pilot_role",
        "source_family_candidate",
        "top_component",
        "positive_components",
    ]
    optional = [
        "support_safe_compiled_formula",
        "support_safe_formula_completion_status",
        role_col,
    ]
    keep += [col for col in optional if col in pool.columns]
    pool = pool[keep].copy()
    pool["support_safe_pool"] = pool_name
    return pool


def _load_pool_data(pool_name: str, config: dict[str, object]) -> pd.DataFrame:
    pool = _pool_manifest(pool_name, config)
    galaxies = set(str(g) for g in pool["galaxy"])
    sample = base._sample_rows(galaxies)
    curves = base._mass_model_rows(galaxies)
    if curves.empty:
        raise RuntimeError(f"No local SPARC endpoint rows found for {pool_name}.")

    meta_rows = []
    for _, row in pool.iterrows():
        galaxy = str(row["galaxy"])
        sample_meta = sample.get(galaxy)
        if sample_meta is None:
            continue
        meta_rows.append({**row.to_dict(), **sample_meta})
    meta = pd.DataFrame(meta_rows)
    coords = pd.read_csv(
        COORDINATES,
        usecols=[
            "galaxy",
            "bar_radius_kpc_source",
            "ring_radius_kpc_source",
            "spiral_pitch_median_abs_deg_source",
        ],
    )
    support = pd.read_csv(
        SUPPORT,
        usecols=[
            "galaxy",
            "spiral_inner_kpc_source",
            "spiral_outer_kpc_source",
            "top_component_weight",
            "dominance_margin",
        ],
    )
    meta = meta.merge(coords, on="galaxy", how="left").merge(support, on="galaxy", how="left")
    return curves.merge(meta, on="galaxy", how="inner")


def _score_pool(pool_name: str, config: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    data = _load_pool_data(pool_name, config)
    detail_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for galaxy, test in data.groupby("galaxy", sort=True):
        train = data[data["galaxy"] != galaxy].copy()
        matched_component = str(test["top_component"].iloc[0])
        candidate_kernel_train = _candidate_kernel(train)
        candidate_kernel_test = _candidate_kernel(test)
        candidate_amp = _fit_amplitude(train, candidate_kernel_train)
        candidate_rmse, candidate_wrmse = _weighted_rmse(test, candidate_kernel_test, candidate_amp)

        baryonic_rmse, baryonic_wrmse = _weighted_rmse(
            test,
            pd.Series(0.0, index=test.index),
            0.0,
        )

        control_scores = {}
        for component in COMPONENTS:
            train_kernel = _component_kernel(component, train)
            test_kernel = _component_kernel(component, test)
            amp = _fit_amplitude(train, train_kernel)
            rmse, wrmse = _weighted_rmse(test, test_kernel, amp)
            control_scores[component] = {"rmse": rmse, "wrmse": wrmse, "amp": amp}
            detail_rows.append(
                {
                    "support_safe_pool": pool_name,
                    "left_out_galaxy": galaxy,
                    "matched_component": matched_component,
                    "scored_model": f"CONTROL_{component}",
                    "model_type": "component_control",
                    "n_train_galaxies": int(train["galaxy"].nunique()),
                    "n_test_points": int(len(test)),
                    "rmse_kms": rmse,
                    "weighted_rmse_kms": wrmse,
                    "amplitude_v2": amp,
                    "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                    "amplitude_policy": AMPLITUDE_POLICY,
                    "scoring_policy": SCORING_POLICY,
                    "claim_boundary": config["claim_boundary"],
                }
            )
        detail_rows.append(
            {
                "support_safe_pool": pool_name,
                "left_out_galaxy": galaxy,
                "matched_component": matched_component,
                "scored_model": "SUPPORT_SAFE_CANDIDATE",
                "model_type": "candidate",
                "n_train_galaxies": int(train["galaxy"].nunique()),
                "n_test_points": int(len(test)),
                "rmse_kms": candidate_rmse,
                "weighted_rmse_kms": candidate_wrmse,
                "amplitude_v2": candidate_amp,
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
                "claim_boundary": config["claim_boundary"],
            }
        )

        wrong = [
            score["wrmse"]
            for component, score in control_scores.items()
            if component != matched_component
        ]
        wrong_mean = float(np.mean(wrong))
        best_wrong = float(np.min(wrong))
        matched_control_wrmse = float(control_scores[matched_component]["wrmse"])
        summary_rows.append(
            {
                "support_safe_pool": pool_name,
                "galaxy": galaxy,
                "matched_component": matched_component,
                "source_family_candidate": str(test["source_family_candidate"].iloc[0]),
                "pilot_role_original": str(test["pilot_role"].iloc[0]),
                "n_train_galaxies": int(train["galaxy"].nunique()),
                "n_test_points": int(len(test)),
                "baryonic_carrier_weighted_rmse_kms": baryonic_wrmse,
                "candidate_weighted_rmse_kms": candidate_wrmse,
                "matched_component_control_weighted_rmse_kms": matched_control_wrmse,
                "wrong_component_mean_weighted_rmse_kms": wrong_mean,
                "best_wrong_component_weighted_rmse_kms": best_wrong,
                "candidate_minus_baryonic_weighted_rmse_kms": candidate_wrmse - baryonic_wrmse,
                "matched_control_minus_candidate_weighted_rmse_kms": matched_control_wrmse - candidate_wrmse,
                "wrong_mean_minus_candidate_weighted_rmse_kms": wrong_mean - candidate_wrmse,
                "best_wrong_minus_candidate_weighted_rmse_kms": best_wrong - candidate_wrmse,
                "candidate_beats_baryonic": "yes" if candidate_wrmse < baryonic_wrmse else "no",
                "candidate_beats_matched_component_control": "yes"
                if candidate_wrmse < matched_control_wrmse
                else "no",
                "candidate_beats_wrong_component_mean": "yes" if candidate_wrmse < wrong_mean else "no",
                "candidate_beats_best_wrong_component": "yes" if candidate_wrmse < best_wrong else "no",
                "candidate_amplitude_v2": candidate_amp,
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
                "claim_boundary": config["claim_boundary"],
            }
        )
    scoreable = pd.DataFrame(summary_rows)
    aggregate = {
        "support_safe_pool": pool_name,
        "n_pool_galaxies": int(data["galaxy"].nunique()),
        "n_pool_points": int(len(data)),
        "candidate_beats_baryonic": int((scoreable["candidate_beats_baryonic"] == "yes").sum()),
        "candidate_beats_matched_component_control": int(
            (scoreable["candidate_beats_matched_component_control"] == "yes").sum()
        ),
        "candidate_beats_wrong_component_mean": int(
            (scoreable["candidate_beats_wrong_component_mean"] == "yes").sum()
        ),
        "candidate_beats_best_wrong_component": int(
            (scoreable["candidate_beats_best_wrong_component"] == "yes").sum()
        ),
        "median_candidate_minus_baryonic_weighted_rmse_kms": float(
            scoreable["candidate_minus_baryonic_weighted_rmse_kms"].median()
        ),
        "median_wrong_mean_minus_candidate_weighted_rmse_kms": float(
            scoreable["wrong_mean_minus_candidate_weighted_rmse_kms"].median()
        ),
        "median_best_wrong_minus_candidate_weighted_rmse_kms": float(
            scoreable["best_wrong_minus_candidate_weighted_rmse_kms"].median()
        ),
        "scoring_policy": SCORING_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "claim_boundary": config["claim_boundary"],
    }
    return detail_rows, summary_rows, aggregate


def run_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    details: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    aggregates: dict[str, object] = {}
    for pool_name, config in POOL_CONFIGS.items():
        detail_rows, summary_rows, aggregate = _score_pool(pool_name, config)
        details.extend(detail_rows)
        summaries.extend(summary_rows)
        aggregates[pool_name] = aggregate
    detail = pd.DataFrame(details).sort_values(["support_safe_pool", "left_out_galaxy", "model_type", "scored_model"])
    summary = pd.DataFrame(summaries).sort_values(["support_safe_pool", "galaxy"])
    return detail, summary, {
        "pools": aggregates,
        "endpoint_data_policy": "local_sparc_endpoint_curves_used_only_after_source_pool_freeze",
        "claim_boundary": "support_safe_pool_loocv_scoring_local_diagnostic_not_population_validation",
    }


def main() -> None:
    if not base.has_external_sparc_mrt():
        base.verify_clean_clone_committed_artifacts(ROOT)
        return
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
