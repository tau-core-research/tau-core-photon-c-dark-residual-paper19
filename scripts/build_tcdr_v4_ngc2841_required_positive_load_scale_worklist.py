from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

GAP_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_post_control_positive_load_gap_detail_local.csv"
GAP_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.json"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json"

CLAIM_BOUNDARY = "ngc2841_required_positive_load_scale_worklist_not_physical_mass_claim"
AUDIT_POLICY = (
    "convert_remaining_positive_v2_gap_to_equivalent_GM_over_R_scale_for_source_search_"
    "no_fit_no_kernel_promotion_no_dark_matter_claim"
)
G_KPC_KMS2_PER_MSUN = 4.30091e-6


def build_worklist() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    gap_summary = json.loads(GAP_SUMMARY.read_text(encoding="utf-8"))
    detail = pd.read_csv(GAP_DETAIL)
    if set(detail["endpoint_validation_claimed"].astype(str)) != {"no"}:
        raise ValueError("Gap detail unexpectedly claims endpoint validation.")
    if set(detail["kernel_promotion_permission"].astype(str)) != {"no"}:
        raise ValueError("Gap detail unexpectedly grants kernel promotion.")

    detail["required_equivalent_load_mass_after_ceiling_msun"] = (
        detail["positive_v2_gap_after_ceiling_control"] * detail["radius_kpc"] / G_KPC_KMS2_PER_MSUN
    )
    detail["required_equivalent_load_mass_after_projection_plus_ceiling_msun"] = (
        detail["positive_v2_gap_after_projection_plus_ceiling_control"]
        * detail["radius_kpc"]
        / G_KPC_KMS2_PER_MSUN
    )
    detail["known_outer_baryon_ceiling_fraction_of_required"] = (
        detail["delta_v2_outer_baryonic_ceiling"]
        / detail["positive_v2_gap_after_baryonic"].replace(0.0, pd.NA)
    ).fillna(0.0)
    detail["source_search_interpretation"] = (
        "equivalent_scale_requirement_only_not_a_physical_mass_or_fit"
    )
    detail["source_priority"] = detail["zone"].map(
        {
            "inner_lt_10kpc": "not_primary_outer_capacity_target",
            "mid_10_30kpc": "secondary_transition_capacity_target",
            "outer_ge_30kpc": "primary_outer_positive_load_target",
        }
    )
    detail["endpoint_validation_claimed"] = "no"
    detail["kernel_promotion_permission"] = "no"
    detail["positive_load_promotion_permission"] = "no"
    detail["audit_policy"] = AUDIT_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    summary_rows = []
    for zone, group in detail.groupby("zone", sort=False):
        summary_rows.append(
            {
                "galaxy": "NGC2841",
                "zone": zone,
                "n_points": int(len(group)),
                "radius_min_kpc": float(group["radius_kpc"].min()),
                "radius_max_kpc": float(group["radius_kpc"].max()),
                "median_positive_v2_gap_after_ceiling_control": float(
                    group["positive_v2_gap_after_ceiling_control"].median()
                ),
                "median_required_equivalent_load_mass_after_ceiling_msun": float(
                    group["required_equivalent_load_mass_after_ceiling_msun"].median()
                ),
                "q25_required_equivalent_load_mass_after_ceiling_msun": float(
                    group["required_equivalent_load_mass_after_ceiling_msun"].quantile(0.25)
                ),
                "q75_required_equivalent_load_mass_after_ceiling_msun": float(
                    group["required_equivalent_load_mass_after_ceiling_msun"].quantile(0.75)
                ),
                "median_known_outer_baryon_ceiling_fraction_of_required": float(
                    group["known_outer_baryon_ceiling_fraction_of_required"].median()
                ),
                "source_priority": str(group["source_priority"].iloc[0]),
                "endpoint_validation_claimed": "no",
                "kernel_promotion_permission": "no",
                "positive_load_promotion_permission": "no",
                "audit_policy": AUDIT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    summary_frame = pd.DataFrame(summary_rows)
    outer = summary_frame[summary_frame["zone"].eq("outer_ge_30kpc")].iloc[0]

    summary = {
        "n_points": int(len(detail)),
        "galaxies": ["NGC2841"],
        "zones": summary_frame["zone"].tolist(),
        "outer_zone_median_positive_v2_gap_after_ceiling_control": float(
            outer["median_positive_v2_gap_after_ceiling_control"]
        ),
        "outer_zone_median_required_equivalent_load_mass_after_ceiling_msun": float(
            outer["median_required_equivalent_load_mass_after_ceiling_msun"]
        ),
        "outer_zone_q25_required_equivalent_load_mass_after_ceiling_msun": float(
            outer["q25_required_equivalent_load_mass_after_ceiling_msun"]
        ),
        "outer_zone_q75_required_equivalent_load_mass_after_ceiling_msun": float(
            outer["q75_required_equivalent_load_mass_after_ceiling_msun"]
        ),
        "outer_zone_median_known_outer_baryon_ceiling_fraction_of_required": float(
            outer["median_known_outer_baryon_ceiling_fraction_of_required"]
        ),
        "ceiling_fraction_of_outer_baryonic_gap_from_previous_audit": float(
            gap_summary["ceiling_fraction_of_outer_baryonic_gap"]
        ),
        "endpoint_validation_claimed_counts": (
            detail["endpoint_validation_claimed"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            detail["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "positive_load_promotion_permission_counts": (
            detail["positive_load_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "audit_policy": AUDIT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The remaining NGC2841 outer positive-load requirement corresponds to a "
            "very large GM/R-equivalent scale. This is a source-search yardstick only: "
            "it is not a physical dark-matter mass claim and it must not be used to "
            "choose or tune a kernel."
        ),
        "next_allowed_action": (
            "Search only residual-blind source-native channels capable of producing a "
            "large positive outer load scale, or derive a Tau-side load theorem. Do not "
            "use this diagnostic scale as a fitted endpoint amplitude."
        ),
    }
    return detail, summary_frame, summary


def main() -> None:
    detail, summary_frame, summary = build_worklist()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_frame.to_csv(OUT_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(summary_frame.to_string(index=False))


if __name__ == "__main__":
    main()
