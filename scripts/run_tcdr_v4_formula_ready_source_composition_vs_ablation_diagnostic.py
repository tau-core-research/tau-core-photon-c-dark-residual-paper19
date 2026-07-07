from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

UNIQUENESS = SOURCE_DIR / "tcdr_v4_p0_source_composition_uniqueness_audit_v0_5.csv"
ABLATION = (
    EXTERNAL_DIR
    / "tcdr_v4_p0_holdout_endpoint_scoring_formula_compiler_ready_component_ablation_detail_local.csv"
)

OUT_DETAIL = (
    EXTERNAL_DIR
    / "tcdr_v4_p0_formula_ready_source_composition_vs_ablation_diagnostic_detail_local.csv"
)
OUT_JSON = (
    EXTERNAL_DIR
    / "tcdr_v4_p0_formula_ready_source_composition_vs_ablation_diagnostic_summary_local.json"
)

READY_STATUS = "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
ENDPOINT_POLICY = (
    "uses_local_ablation_endpoint_scores_only_after_source_uniqueness_freeze_for_diagnostic"
)
CLAIM_BOUNDARY = "source_composition_vs_ablation_alignment_diagnostic_not_kernel_selection"


def _component_from_variant(variant: str) -> str:
    if variant.endswith("_only"):
        return variant.removesuffix("_only")
    if variant == "full_source_mix":
        return "full_source_mix"
    if variant.startswith("leaveout_"):
        return variant
    return "unknown"


def run_diagnostic() -> tuple[pd.DataFrame, dict[str, object]]:
    source = pd.read_csv(UNIQUENESS)
    source = source[source["compiler_readiness_status"] == READY_STATUS].copy()
    source = source[source["pilot_role"] == "PILOT_HOLDOUT"].copy()

    ablation = pd.read_csv(ABLATION)
    best_rows = []
    for galaxy, group in ablation.groupby("galaxy", sort=True):
        ordered = group.sort_values(["weighted_rmse_kms", "variant"])
        best_rows.append(
            {
                "galaxy": galaxy,
                "best_ablation_variant": str(ordered.iloc[0]["variant"]),
                "best_ablation_component": _component_from_variant(str(ordered.iloc[0]["variant"])),
                "best_ablation_weighted_rmse_kms": float(ordered.iloc[0]["weighted_rmse_kms"]),
                "full_source_mix_weighted_rmse_kms": float(
                    group.loc[group["variant"] == "full_source_mix", "weighted_rmse_kms"].iloc[0]
                ),
            }
        )
    best = pd.DataFrame(best_rows)
    detail = source.merge(best, on="galaxy", how="inner")
    detail["source_top_matches_best_component"] = detail.apply(
        lambda row: (
            "yes"
            if row["top_component"] == row["best_ablation_component"]
            and row["top_component"] != "none"
            else "no"
        ),
        axis=1,
    )
    detail["ablation_best_minus_full_mix_weighted_rmse_kms"] = (
        detail["best_ablation_weighted_rmse_kms"] - detail["full_source_mix_weighted_rmse_kms"]
    )
    detail["endpoint_data_policy"] = ENDPOINT_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    positive_source = detail[detail["top_component"] != "none"].copy()
    strong_source = positive_source[
        positive_source["source_composition_uniqueness_status"]
        == "SOURCE_COMPOSITION_UNIQUE_CANDIDATE"
    ].copy()
    summary = {
        "n_formula_ready_holdout_galaxies": int(len(detail)),
        "n_positive_source_component_galaxies": int(len(positive_source)),
        "n_strong_source_unique_galaxies": int(len(strong_source)),
        "top_component_alignment_count_positive_source": int(
            (positive_source["source_top_matches_best_component"] == "yes").sum()
        ),
        "top_component_alignment_rate_positive_source": (
            float((positive_source["source_top_matches_best_component"] == "yes").mean())
            if not positive_source.empty
            else None
        ),
        "top_component_alignment_count_strong_source": int(
            (strong_source["source_top_matches_best_component"] == "yes").sum()
        ),
        "top_component_alignment_rate_strong_source": (
            float((strong_source["source_top_matches_best_component"] == "yes").mean())
            if not strong_source.empty
            else None
        ),
        "source_vs_ablation_by_galaxy": {
            str(row["galaxy"]): {
                "source_status": str(row["source_composition_uniqueness_status"]),
                "source_top_component": str(row["top_component"]),
                "best_ablation_variant": str(row["best_ablation_variant"]),
                "matches": str(row["source_top_matches_best_component"]),
            }
            for _, row in detail.sort_values("galaxy").iterrows()
        },
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "This diagnostic checks whether the endpoint-blind source-dominant "
            "component agrees with the local endpoint ablation winner. Low alignment "
            "means the current source weights are not yet a reliable component "
            "selector and must not be promoted."
        ),
    }
    return detail.sort_values("galaxy"), summary


def main() -> None:
    detail, summary = run_diagnostic()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        detail[
            [
                "galaxy",
                "source_composition_uniqueness_status",
                "top_component",
                "best_ablation_variant",
                "source_top_matches_best_component",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
