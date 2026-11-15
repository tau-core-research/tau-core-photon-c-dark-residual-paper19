from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring_mixed_components as mixed


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

SHUFFLED_NULLS = SOURCE_DIR / "tcdr_v4_p0_source_native_shuffled_component_nulls_v0_1.csv"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_shuffled_mixed_components_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_shuffled_mixed_components_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_shuffled_mixed_components_summary_local.json"

SHUFFLE_SCORING_POLICY = (
    "holdout_only_shuffled_component_null_vs_source_frozen_mixed_component_no_validation"
)


def _apply_shuffle(data: pd.DataFrame, shuffled: pd.DataFrame) -> pd.DataFrame:
    replace_cols = [
        "active_source_native_components",
        "mixed_kernel_status",
        "bar_component_weight",
        "ring_component_weight",
        "spiral_component_weight",
        "fallback_family_proxy_weight",
    ]
    base = data.drop(columns=replace_cols)
    mapping = shuffled[
        [
            "galaxy",
            "shuffled_active_source_native_components",
            "shuffled_mixed_kernel_status",
            "shuffled_bar_component_weight",
            "shuffled_ring_component_weight",
            "shuffled_spiral_component_weight",
            "shuffled_fallback_family_proxy_weight",
            "shuffled_component_source_galaxy",
        ]
    ].rename(
        columns={
            "shuffled_active_source_native_components": "active_source_native_components",
            "shuffled_mixed_kernel_status": "mixed_kernel_status",
            "shuffled_bar_component_weight": "bar_component_weight",
            "shuffled_ring_component_weight": "ring_component_weight",
            "shuffled_spiral_component_weight": "spiral_component_weight",
            "shuffled_fallback_family_proxy_weight": "fallback_family_proxy_weight",
        }
    )
    return base.merge(mapping, on="galaxy", how="left")


def _score_shuffled(data: pd.DataFrame, shuffle_id: int) -> tuple[pd.DataFrame, dict[str, object]]:
    train = data[data["pilot_role"] == "PILOT_TRAIN_POOL"].copy()
    holdout = data[data["pilot_role"] == "PILOT_HOLDOUT"].copy()
    amp = mixed._fit_mixed_amplitude(train)

    rows = []
    for galaxy, group in holdout.groupby("galaxy", sort=True):
        _, wrmse = mixed._rmse_with_kernel(group, mixed._mixed_kernel_for_group(group), amp)
        rows.append(
            {
                "shuffle_id": shuffle_id,
                "galaxy": galaxy,
                "matched_source_family": str(group["source_family_candidate"].iloc[0]),
                "component_mixture_status": str(group["component_mixture_status"].iloc[0]),
                "active_source_native_components": str(group["active_source_native_components"].iloc[0]),
                "shuffled_component_source_galaxy": str(group["shuffled_component_source_galaxy"].iloc[0]),
                "n_points": int(len(group)),
                "shuffled_mixed_component_weighted_rmse_kms": wrmse,
                "shuffled_mixed_component_amplitude_v2": amp,
                "kernel_shape_policy": mixed.KERNEL_SHAPE_POLICY,
                "amplitude_policy": mixed.AMPLITUDE_POLICY,
                "scoring_policy": SHUFFLE_SCORING_POLICY,
                "claim_boundary": "local_preflight_shuffled_component_null_diagnostic_not_population_validation",
            }
        )
    detail = pd.DataFrame(rows)
    aggregate = {
        "shuffle_id": shuffle_id,
        "shuffled_mixed_component_amplitude_v2": amp,
        "median_shuffled_mixed_component_weighted_rmse_kms": float(
            detail["shuffled_mixed_component_weighted_rmse_kms"].median()
        ),
    }
    return detail, aggregate


def run_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    base_data = mixed._load_data()
    _, actual_summary, actual_aggregate = mixed.run_scoring()
    actual_scoreable = actual_summary[actual_summary["endpoint_scoring_status"] == "scoreable"].copy()

    shuffled_nulls = pd.read_csv(SHUFFLED_NULLS)
    detail_frames = []
    aggregate_rows = []
    for shuffle_id, shuffled in shuffled_nulls.groupby("shuffle_id", sort=True):
        shuffled_data = _apply_shuffle(base_data, shuffled)
        detail, aggregate = _score_shuffled(shuffled_data, int(shuffle_id))
        detail_frames.append(detail)
        aggregate_rows.append(aggregate)

    detail_all = pd.concat(detail_frames, ignore_index=True)
    compare = detail_all.merge(
        actual_scoreable[
            [
                "galaxy",
                "pure_matched_weighted_rmse_kms",
                "mixed_component_weighted_rmse_kms",
                "wrong_family_mean_weighted_rmse_kms",
                "best_wrong_family_weighted_rmse_kms",
            ]
        ],
        on="galaxy",
        how="inner",
    )
    compare["shuffled_minus_actual_mixed_weighted_rmse_kms"] = (
        compare["shuffled_mixed_component_weighted_rmse_kms"]
        - compare["mixed_component_weighted_rmse_kms"]
    )
    compare["shuffled_beats_actual_mixed"] = np.where(
        compare["shuffled_mixed_component_weighted_rmse_kms"]
        < compare["mixed_component_weighted_rmse_kms"],
        "yes",
        "no",
    )
    compare["shuffled_beats_pure_matched"] = np.where(
        compare["shuffled_mixed_component_weighted_rmse_kms"]
        < compare["pure_matched_weighted_rmse_kms"],
        "yes",
        "no",
    )
    compare["shuffled_beats_wrong_mean"] = np.where(
        compare["shuffled_mixed_component_weighted_rmse_kms"]
        < compare["wrong_family_mean_weighted_rmse_kms"],
        "yes",
        "no",
    )

    per_shuffle = compare.groupby("shuffle_id").agg(
        n_scoreable_holdout_galaxies=("galaxy", "nunique"),
        shuffled_beats_actual_mixed=("shuffled_beats_actual_mixed", lambda s: int((s == "yes").sum())),
        shuffled_beats_pure_matched=("shuffled_beats_pure_matched", lambda s: int((s == "yes").sum())),
        shuffled_beats_wrong_mean=("shuffled_beats_wrong_mean", lambda s: int((s == "yes").sum())),
        median_shuffled_minus_actual_mixed_weighted_rmse_kms=(
            "shuffled_minus_actual_mixed_weighted_rmse_kms",
            "median",
        ),
    ).reset_index()

    aggregate_df = pd.DataFrame(aggregate_rows)
    per_shuffle = per_shuffle.merge(aggregate_df, on="shuffle_id", how="left")

    actual_median = float(actual_scoreable["mixed_component_weighted_rmse_kms"].median())
    null_medians = per_shuffle["median_shuffled_mixed_component_weighted_rmse_kms"].to_numpy()
    aggregate = {
        "n_shuffles": int(per_shuffle["shuffle_id"].nunique()),
        "n_scoreable_holdout_galaxies": int(actual_scoreable["galaxy"].nunique()),
        "actual_mixed_median_weighted_rmse_kms": actual_median,
        "median_null_median_weighted_rmse_kms": float(np.median(null_medians)),
        "null_fraction_with_median_rmse_le_actual": float(np.mean(null_medians <= actual_median)),
        "actual_mixed_beats_pure_matched": int(actual_aggregate["mixed_beats_pure_matched"]),
        "median_shuffled_beats_pure_matched": float(per_shuffle["shuffled_beats_pure_matched"].median()),
        "actual_mixed_beats_wrong_mean": int(actual_aggregate["mixed_beats_wrong_mean"]),
        "median_shuffled_beats_wrong_mean": float(per_shuffle["shuffled_beats_wrong_mean"].median()),
        "shuffle_scoring_policy": SHUFFLE_SCORING_POLICY,
        "claim_boundary": "local_preflight_shuffled_component_null_diagnostic_not_population_validation",
        "verdict": (
            "Diagnostic only: compares the source-frozen mixed component kernel "
            "against endpoint-blind shuffled component assignments. This is not "
            "population validation."
        ),
    }
    return compare.sort_values(["shuffle_id", "galaxy"]), per_shuffle, aggregate


def main() -> None:
    if not mixed.base.has_external_sparc_mrt():
        mixed.base.verify_clean_clone_committed_artifacts(ROOT)
        return
    detail, summary, aggregate = run_scoring()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    summary.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(aggregate, indent=2))
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
