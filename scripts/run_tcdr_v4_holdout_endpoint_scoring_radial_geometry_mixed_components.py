from __future__ import annotations

from pathlib import Path

import run_tcdr_v4_holdout_endpoint_scoring_mixed_components as mixed


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

mixed.MIXED_KERNEL_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"
mixed.OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_radial_geometry_mixed_components_detail_local.csv"
mixed.OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_radial_geometry_mixed_components_summary_local.csv"
mixed.OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_scoring_radial_geometry_mixed_components_summary_local.json"
mixed.KERNEL_SHAPE_POLICY = (
    "source_native_radial_geometry_mixed_component_freeze_v0_3_"
    "strength_times_radial_zone_times_hierarchy_times_projection_reliability_no_endpoint_inputs"
)
mixed.SCORING_POLICY = "holdout_only_radial_geometry_mixed_component_vs_pure_family_controls_no_validation"


if __name__ == "__main__":
    mixed.main()
