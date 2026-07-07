from __future__ import annotations

from pathlib import Path

import build_tcdr_v4_p0_source_native_shuffled_component_nulls as nulls


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

nulls.MIXED_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_v0_2.csv"
nulls.OUT_DETAIL = SOURCE_DIR / "tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls_v0_2.csv"
nulls.OUT_SUMMARY = SOURCE_DIR / "tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls_summary_v0_2.json"
nulls.SHUFFLE_POLICY = (
    "endpoint_blind_strength_weighted_component_package_shuffle_v0_2_within_pilot_role_"
    "preserve_role_counts_and_weight_distribution_seed_19019"
)


if __name__ == "__main__":
    nulls.main()
