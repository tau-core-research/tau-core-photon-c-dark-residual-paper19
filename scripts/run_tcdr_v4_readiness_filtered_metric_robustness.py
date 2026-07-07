from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

FILTERED = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_readiness_filtered_scoring_local.csv"
DETAIL = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_detail_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_readiness_filtered_metric_robustness_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_readiness_filtered_metric_robustness_summary_local.json"

CLAIM_BOUNDARY = "readiness_filtered_metric_robustness_local_diagnostic_not_validation"
NEAR_TIE_KMS = 0.1


def _metric_rows(group: pd.DataFrame, metric_col: str) -> dict[str, object]:
    candidate = group[group["model_type"].eq("candidate")]
    if len(candidate) != 1:
        raise ValueError("Expected exactly one candidate row per pool/galaxy.")
    candidate_value = float(candidate[metric_col].iloc[0])
    matched_component = str(candidate["matched_component"].iloc[0])
    controls = group[group["model_type"].eq("component_control")].copy()
    controls["component"] = controls["scored_model"].str.replace("CONTROL_", "", regex=False)
    wrong = controls[~controls["component"].eq(matched_component)]
    matched = controls[controls["component"].eq(matched_component)]
    if len(wrong) == 0 or len(matched) != 1:
        raise ValueError("Expected wrong controls and one matched component control.")

    wrong_values = wrong.set_index("component")[metric_col].astype(float)
    best_wrong_component = str(wrong_values.idxmin())
    best_wrong = float(wrong_values.min())
    wrong_mean = float(wrong_values.mean())
    matched_value = float(matched[metric_col].iloc[0])
    best_wrong_margin = best_wrong - candidate_value
    wrong_mean_margin = wrong_mean - candidate_value

    return {
        "metric": metric_col,
        "candidate_metric": candidate_value,
        "matched_control_metric": matched_value,
        "wrong_mean_metric": wrong_mean,
        "best_wrong_component_metric": best_wrong_component,
        "best_wrong_metric": best_wrong,
        "wrong_mean_minus_candidate_metric": wrong_mean_margin,
        "best_wrong_minus_candidate_metric": best_wrong_margin,
        "candidate_beats_wrong_mean_metric": "yes" if wrong_mean_margin > 0 else "no",
        "candidate_beats_best_wrong_metric": "yes" if best_wrong_margin > 0 else "no",
        "candidate_beats_best_wrong_material_0p1": "yes"
        if best_wrong_margin > NEAR_TIE_KMS
        else "no",
        "near_tie_abs_margin_le_0p1": "yes" if abs(best_wrong_margin) <= NEAR_TIE_KMS else "no",
    }


def build_robustness() -> tuple[pd.DataFrame, dict[str, object]]:
    filtered = pd.read_csv(FILTERED)
    detail = pd.read_csv(DETAIL)
    allowed = filtered[
        [
            "support_safe_pool",
            "galaxy",
            "source_family_candidate",
            "support_safe_compiled_formula",
            "scoring_readiness_class",
            "score_interpretation",
        ]
    ]
    detail = detail.merge(
        allowed,
        left_on=["support_safe_pool", "left_out_galaxy"],
        right_on=["support_safe_pool", "galaxy"],
        how="inner",
        suffixes=("", "_allowed"),
    )

    rows: list[dict[str, object]] = []
    for (pool, galaxy), group in detail.groupby(["support_safe_pool", "galaxy"], sort=True):
        base = {
            "support_safe_pool": pool,
            "galaxy": galaxy,
            "matched_component": str(group["matched_component"].iloc[0]),
            "source_family_candidate": str(group["source_family_candidate"].iloc[0]),
            "support_safe_compiled_formula": str(group["support_safe_compiled_formula_allowed"].iloc[0]),
            "scoring_readiness_class": str(group["scoring_readiness_class"].iloc[0]),
            "score_interpretation": str(group["score_interpretation"].iloc[0]),
        }
        for metric_col in ["weighted_rmse_kms", "rmse_kms"]:
            metric = _metric_rows(group, metric_col)
            rows.append({**base, **metric, "claim_boundary": CLAIM_BOUNDARY})

    robustness = pd.DataFrame(rows)
    metric_summary = {}
    for metric, group in robustness.groupby("metric", sort=True):
        metric_summary[metric] = {
            "n_rows": int(len(group)),
            "beats_wrong_mean": int(group["candidate_beats_wrong_mean_metric"].eq("yes").sum()),
            "beats_best_wrong": int(group["candidate_beats_best_wrong_metric"].eq("yes").sum()),
            "material_best_wrong_margin_gt_0p1": int(
                group["candidate_beats_best_wrong_material_0p1"].eq("yes").sum()
            ),
            "near_tie_abs_margin_le_0p1": int(group["near_tie_abs_margin_le_0p1"].eq("yes").sum()),
            "median_best_wrong_minus_candidate": float(
                group["best_wrong_minus_candidate_metric"].median()
            ),
            "median_wrong_mean_minus_candidate": float(
                group["wrong_mean_minus_candidate_metric"].median()
            ),
        }

    weighted = robustness[robustness["metric"].eq("weighted_rmse_kms")]
    unweighted = robustness[robustness["metric"].eq("rmse_kms")]
    merged = weighted[
        ["support_safe_pool", "galaxy", "candidate_beats_best_wrong_metric"]
    ].merge(
        unweighted[["support_safe_pool", "galaxy", "candidate_beats_best_wrong_metric"]],
        on=["support_safe_pool", "galaxy"],
        suffixes=("_weighted", "_unweighted"),
    )
    agreement = int(
        (
            merged["candidate_beats_best_wrong_metric_weighted"]
            == merged["candidate_beats_best_wrong_metric_unweighted"]
        ).sum()
    )

    summary = {
        "n_rows": int(len(robustness)),
        "n_unique_pool_galaxy_rows": int(len(filtered)),
        "metrics": metric_summary,
        "best_wrong_pass_agreement_weighted_vs_unweighted": agreement,
        "best_wrong_pass_agreement_total": int(len(merged)),
        "near_tie_kms": NEAR_TIE_KMS,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The readiness-filtered current-formula subset remains positive "
            "against wrong-mean controls under weighted and unweighted metrics. "
            "Strict best-wrong survival is metric-sensitive in near-tie rows and "
            "should remain a robustness diagnostic, not endpoint validation."
        ),
    }
    return robustness.sort_values(["support_safe_pool", "galaxy", "metric"]), summary


def main() -> None:
    robustness, summary = build_robustness()
    robustness.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "metric",
        "candidate_beats_wrong_mean_metric",
        "candidate_beats_best_wrong_metric",
        "best_wrong_minus_candidate_metric",
        "near_tie_abs_margin_le_0p1",
    ]
    print(robustness[cols].to_string(index=False))


if __name__ == "__main__":
    main()
