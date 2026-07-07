from __future__ import annotations

from pathlib import Path

import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring_mixed_components as mixed
import run_tcdr_v4_holdout_endpoint_scoring_shuffled_mixed_components as shuffled


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

READINESS = SOURCE_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
RADIAL_GEOMETRY_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"
RADIAL_GEOMETRY_NULLS = SOURCE_DIR / "tcdr_v4_p0_source_native_radial_geometry_shuffled_component_nulls_v0_3.csv"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_shuffled_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_shuffled_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_shuffled_summary_local.json"

READY_STATUS = "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
KERNEL_SHAPE_POLICY = (
    "source_frozen_formula_compiler_ready_v0_4_using_radial_geometry_mixed_freeze_v0_3_"
    "readiness_filtered_shuffled_component_nulls_no_holdout_shape_tuning"
)
SCORING_POLICY = (
    "holdout_only_formula_compiler_ready_subset_v0_4_"
    "source_frozen_readiness_filter_before_endpoint_scoring_no_validation"
)
SHUFFLE_SCORING_POLICY = (
    "holdout_only_formula_compiler_ready_subset_v0_4_shuffled_component_nulls_no_validation"
)


def _load_ready_data_with(original_loader) -> pd.DataFrame:
    data = original_loader()
    readiness = pd.read_csv(READINESS)[
        [
            "galaxy",
            "compiler_readiness_status",
            "compiled_formula_family_candidate",
            "available_formula_components",
        ]
    ]
    data = data.merge(readiness, on="galaxy", how="left")
    return data[data["compiler_readiness_status"] == READY_STATUS].copy()


def run_scoring():
    mixed.MIXED_KERNEL_FREEZE = RADIAL_GEOMETRY_FREEZE
    mixed.KERNEL_SHAPE_POLICY = KERNEL_SHAPE_POLICY
    mixed.SCORING_POLICY = SCORING_POLICY
    shuffled.SHUFFLED_NULLS = RADIAL_GEOMETRY_NULLS
    shuffled.OUT_DETAIL = OUT_DETAIL
    shuffled.OUT_SUMMARY = OUT_SUMMARY
    shuffled.OUT_JSON = OUT_JSON
    shuffled.SHUFFLE_SCORING_POLICY = SHUFFLE_SCORING_POLICY

    original_loader = mixed._load_data
    try:
        mixed._load_data = lambda: _load_ready_data_with(original_loader)
        detail, summary, aggregate = shuffled.run_scoring()
    finally:
        mixed._load_data = original_loader

    readiness = pd.read_csv(READINESS)
    holdout = readiness[readiness["pilot_role"] == "PILOT_HOLDOUT"].copy()
    aggregate.update(
        {
            "formula_compiler_ready_status": READY_STATUS,
            "formula_ready_holdout_galaxies": sorted(
                holdout.loc[
                    holdout["compiler_readiness_status"] == READY_STATUS,
                    "galaxy",
                ].tolist()
            ),
            "excluded_holdout_galaxies": sorted(
                holdout.loc[
                    holdout["compiler_readiness_status"] != READY_STATUS,
                    "galaxy",
                ].tolist()
            ),
            "readiness_manifest": str(READINESS.relative_to(ROOT)),
            "kernel_shape_policy": KERNEL_SHAPE_POLICY,
            "shuffle_scoring_policy": SHUFFLE_SCORING_POLICY,
            "claim_boundary": "formula_compiler_ready_shuffled_component_null_preflight_not_population_validation",
        }
    )
    return detail, summary, aggregate


def main() -> None:
    detail, summary, aggregate = run_scoring()
    detail.to_csv(OUT_DETAIL, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    OUT_JSON.write_text(__import__("json").dumps(aggregate, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(__import__("json").dumps(aggregate, indent=2))
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
