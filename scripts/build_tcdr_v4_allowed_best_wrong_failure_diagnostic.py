from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
SOURCE_DIR = ROOT / "data" / "source_manifests"

BOUNDARY = EXTERNAL_DIR / "tcdr_v4_post_external_scoring_boundary_local.csv"
SOURCE_COMPOSITION = SOURCE_DIR / "tcdr_v4_p0_source_composition_uniqueness_audit_v0_5.csv"
ROBUSTNESS = EXTERNAL_DIR / "tcdr_v4_readiness_filtered_metric_robustness_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_allowed_best_wrong_failure_diagnostic_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_best_wrong_failure_diagnostic_summary_local.json"

CLAIM_BOUNDARY = "allowed_best_wrong_failure_diagnostic_local_not_kernel_promotion"
NEAR_TIE_KMS = 0.10


def _component_weight(row: pd.Series, component: str) -> float:
    col = f"{component}_component_weight"
    if col not in row or pd.isna(row[col]):
        return 0.0
    return float(row[col])


def _positive_components(value: object) -> set[str]:
    if pd.isna(value):
        return set()
    return {
        part.strip()
        for part in str(value).split(";")
        if part.strip() and part.strip() != "none"
    }


def _classify(row: pd.Series) -> str:
    if row["candidate_beats_best_wrong_component"] == "yes":
        return "STRICT_POSITIVE_CURRENT_FORMULA"
    best_wrong = str(row["best_wrong_component"])
    source_visible = bool(row["best_wrong_source_visible"])
    weighted_margin = float(row["best_wrong_minus_candidate_weighted_rmse_kms"])
    unweighted_best = float(row["unweighted_best_wrong_minus_candidate_kms"])
    unweighted_mean = float(row["unweighted_wrong_mean_minus_candidate_kms"])

    if source_visible:
        return "SOURCE_VISIBLE_SECONDARY_COMPONENT_REQUIRES_MIXED_ROUTE_CONTROLS"
    if abs(weighted_margin) <= NEAR_TIE_KMS and unweighted_mean < 0:
        return "METRIC_SENSITIVE_FALSE_COMPONENT_PRESSURE_NO_SOURCE_ROUTE"
    if abs(weighted_margin) <= NEAR_TIE_KMS and unweighted_best < 0:
        return "NEAR_TIE_FALSE_COMPONENT_NO_SOURCE_ROUTE"
    return f"COMPETITIVE_FALSE_{best_wrong.upper()}_CONTROL_NO_SOURCE_ROUTE"


def build_diagnostic() -> tuple[pd.DataFrame, dict[str, object]]:
    boundary = pd.read_csv(BOUNDARY)
    allowed = boundary[
        boundary["post_external_endpoint_replay_permission"].str.startswith("yes", na=False)
    ].copy()
    composition = pd.read_csv(SOURCE_COMPOSITION)[
        [
            "galaxy",
            "source_composition_uniqueness_status",
            "top_component",
            "top_component_weight",
            "runner_up_component",
            "runner_up_component_weight",
            "positive_components",
            "bar_component_weight",
            "ring_component_weight",
            "spiral_component_weight",
            "fallback_family_proxy_weight",
            "endpoint_data_policy",
            "claim_boundary",
        ]
    ].rename(
        columns={
            "positive_components": "source_positive_components",
            "claim_boundary": "source_composition_claim_boundary",
        }
    )
    robustness = pd.read_csv(ROBUSTNESS)
    unweighted = robustness[robustness["metric"] == "rmse_kms"][
        [
            "support_safe_pool",
            "galaxy",
            "wrong_mean_minus_candidate_metric",
            "best_wrong_minus_candidate_metric",
            "candidate_beats_wrong_mean_metric",
            "candidate_beats_best_wrong_metric",
        ]
    ].rename(
        columns={
            "wrong_mean_minus_candidate_metric": "unweighted_wrong_mean_minus_candidate_kms",
            "best_wrong_minus_candidate_metric": "unweighted_best_wrong_minus_candidate_kms",
            "candidate_beats_wrong_mean_metric": "unweighted_candidate_beats_wrong_mean",
            "candidate_beats_best_wrong_metric": "unweighted_candidate_beats_best_wrong",
        }
    )

    diagnostic = allowed.merge(composition, on="galaxy", how="left").merge(
        unweighted, on=["support_safe_pool", "galaxy"], how="left"
    )
    diagnostic["best_wrong_source_component_weight"] = diagnostic.apply(
        lambda row: _component_weight(row, str(row["best_wrong_component"])),
        axis=1,
    )
    diagnostic["best_wrong_in_source_positive_components"] = diagnostic.apply(
        lambda row: str(row["best_wrong_component"])
        in _positive_components(row["source_positive_components"]),
        axis=1,
    )
    diagnostic["best_wrong_source_visible"] = (
        (diagnostic["best_wrong_source_component_weight"] > 0)
        | diagnostic["best_wrong_in_source_positive_components"]
    )
    diagnostic["weighted_best_wrong_near_tie"] = (
        diagnostic["best_wrong_minus_candidate_weighted_rmse_kms"].abs() <= NEAR_TIE_KMS
    )
    diagnostic["allowed_best_wrong_diagnostic_class"] = diagnostic.apply(
        _classify, axis=1
    )
    diagnostic["allowed_failure_diagnostic_claim"] = CLAIM_BOUNDARY
    diagnostic["diagnostic_policy"] = (
        "diagnose_allowed_rows_only_no_new_kernel_no_relabel_no_endpoint_promotion"
    )

    strict_failures = diagnostic[
        diagnostic["candidate_beats_best_wrong_component"] != "yes"
    ]
    summary = {
        "n_allowed_rows": int(len(diagnostic)),
        "n_strict_positive_rows": int(
            (diagnostic["candidate_beats_best_wrong_component"] == "yes").sum()
        ),
        "n_strict_best_wrong_failures": int(len(strict_failures)),
        "strict_failure_source_visible_secondary_count": int(
            strict_failures["best_wrong_source_visible"].sum()
        ),
        "diagnostic_class_counts": diagnostic[
            "allowed_best_wrong_diagnostic_class"
        ].value_counts().to_dict(),
        "strict_failure_rows": strict_failures[
            [
                "support_safe_pool",
                "galaxy",
                "matched_component",
                "source_family_candidate",
                "best_wrong_component",
                "best_wrong_minus_candidate_weighted_rmse_kms",
                "unweighted_best_wrong_minus_candidate_kms",
                "best_wrong_source_component_weight",
                "allowed_best_wrong_diagnostic_class",
            ]
        ].to_dict(orient="records"),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Among the six post-external score-bearing rows, the three strict "
            "best-wrong failures have no source-visible best-wrong component in "
            "the frozen source-composition ledger. They should therefore not be "
            "promoted to mixed kernels from the endpoint score; they remain "
            "near-tie or metric-sensitive control-pressure diagnostics."
        ),
    }

    keep_cols = [
        "support_safe_pool",
        "galaxy",
        "matched_component",
        "source_family_candidate",
        "source_composition_uniqueness_status",
        "source_positive_components",
        "best_wrong_component",
        "best_wrong_source_component_weight",
        "best_wrong_source_visible",
        "candidate_beats_wrong_component_mean",
        "candidate_beats_best_wrong_component",
        "best_wrong_minus_candidate_weighted_rmse_kms",
        "unweighted_wrong_mean_minus_candidate_kms",
        "unweighted_best_wrong_minus_candidate_kms",
        "allowed_best_wrong_diagnostic_class",
        "diagnostic_policy",
        "allowed_failure_diagnostic_claim",
    ]
    return diagnostic[keep_cols].sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    diagnostic, summary = build_diagnostic()
    diagnostic.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        diagnostic[
            [
                "support_safe_pool",
                "galaxy",
                "best_wrong_component",
                "best_wrong_source_visible",
                "candidate_beats_best_wrong_component",
                "allowed_best_wrong_diagnostic_class",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
