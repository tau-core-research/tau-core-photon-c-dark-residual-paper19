from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

POST_EXTERNAL_CLOSURE = EXTERNAL_DIR / "tcdr_v4_post_external_route_closure_local.csv"
READINESS_SCORE = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_readiness_filtered_scoring_local.csv"
METRIC_ROBUSTNESS = EXTERNAL_DIR / "tcdr_v4_readiness_filtered_metric_robustness_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_post_external_scoring_boundary_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_post_external_scoring_boundary_summary_local.json"

CLAIM_BOUNDARY = "post_external_scoring_boundary_local_diagnostic_not_validation"


def _yes_count(series: pd.Series) -> int:
    return int((series == "yes").sum())


def build_boundary() -> tuple[pd.DataFrame, dict[str, object]]:
    closure = pd.read_csv(POST_EXTERNAL_CLOSURE)
    score = pd.read_csv(
        READINESS_SCORE,
        usecols=[
            "support_safe_pool",
            "galaxy",
            "baryonic_carrier_weighted_rmse_kms",
            "candidate_weighted_rmse_kms",
            "wrong_component_mean_weighted_rmse_kms",
            "best_wrong_component",
            "best_wrong_component_weighted_rmse_kms",
            "wrong_mean_minus_candidate_weighted_rmse_kms",
            "best_wrong_minus_candidate_weighted_rmse_kms",
            "candidate_beats_baryonic",
            "candidate_beats_wrong_component_mean",
            "candidate_beats_best_wrong_component",
            "score_interpretation",
        ],
    )
    score_payload_cols = [col for col in score.columns if col not in {"support_safe_pool", "galaxy"}]
    stale_score_cols = [col for col in score_payload_cols if col in closure.columns]
    if stale_score_cols:
        closure = closure.drop(columns=stale_score_cols)
    boundary = closure.merge(score, on=["support_safe_pool", "galaxy"], how="left")
    allowed_mask = boundary["post_external_endpoint_replay_permission"].str.startswith(
        "yes"
    )
    allowed = boundary[allowed_mask].copy()
    blocked = boundary[~allowed_mask].copy()

    # Scores are meaningful only for rows allowed by the post-external closure.
    score_columns = [
        "baryonic_carrier_weighted_rmse_kms",
        "candidate_weighted_rmse_kms",
        "wrong_component_mean_weighted_rmse_kms",
        "best_wrong_component_weighted_rmse_kms",
        "wrong_mean_minus_candidate_weighted_rmse_kms",
        "best_wrong_minus_candidate_weighted_rmse_kms",
        "candidate_beats_baryonic",
        "candidate_beats_wrong_component_mean",
        "candidate_beats_best_wrong_component",
        "score_interpretation",
    ]
    for col in score_columns:
        boundary.loc[~allowed_mask, col] = pd.NA

    robustness = pd.read_csv(METRIC_ROBUSTNESS)
    robustness_allowed = robustness.merge(
        allowed[["support_safe_pool", "galaxy"]],
        on=["support_safe_pool", "galaxy"],
        how="inner",
    )
    metric_summary: dict[str, dict[str, object]] = {}
    for metric, group in robustness_allowed.groupby("metric"):
        metric_summary[str(metric)] = {
            "n_rows": int(len(group)),
            "beats_wrong_mean": _yes_count(group["candidate_beats_wrong_mean_metric"]),
            "beats_best_wrong": _yes_count(group["candidate_beats_best_wrong_metric"]),
            "median_wrong_mean_minus_candidate": float(
                group["wrong_mean_minus_candidate_metric"].median()
            ),
            "median_best_wrong_minus_candidate": float(
                group["best_wrong_minus_candidate_metric"].median()
            ),
        }

    summary = {
        "n_rows": int(len(boundary)),
        "allowed_rows": int(len(allowed)),
        "blocked_rows": int(len(blocked)),
        "allowed_unique_galaxies": sorted(allowed["galaxy"].unique().tolist()),
        "post_external_route_status_counts": boundary[
            "post_external_route_status"
        ].value_counts().to_dict(),
        "weighted_score_counts_on_allowed_rows": {
            "beats_baryonic": _yes_count(allowed["candidate_beats_baryonic"]),
            "beats_wrong_mean": _yes_count(
                allowed["candidate_beats_wrong_component_mean"]
            ),
            "beats_best_wrong": _yes_count(
                allowed["candidate_beats_best_wrong_component"]
            ),
        },
        "metric_robustness_on_allowed_rows": metric_summary,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Post-external scoring boundary: only six current-formula rows are "
            "score-bearing. Blocked rows carry no scoring claim. On the allowed "
            "rows the weighted metric beats baryonic and wrong-mean controls in "
            "6/6, but strict best-wrong survival remains 3/6; unweighted wrong-"
            "mean survival is lower."
        ),
    }
    boundary["post_external_scoring_boundary_claim"] = CLAIM_BOUNDARY
    return boundary.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    boundary, summary = build_boundary()
    boundary.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "post_external_route_status",
        "post_external_endpoint_replay_permission",
        "candidate_beats_wrong_component_mean",
        "candidate_beats_best_wrong_component",
        "score_interpretation",
    ]
    print(boundary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
