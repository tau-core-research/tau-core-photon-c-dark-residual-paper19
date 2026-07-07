from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

READINESS = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_readiness_ledger_local.csv"
FORMULA_AWARE = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_summary_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_readiness_filtered_scoring_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_readiness_filtered_scoring_summary_local.json"

CLAIM_BOUNDARY = (
    "paper8_paper9_readiness_filtered_scoring_local_diagnostic_not_validation"
)


def _yes_count(series: pd.Series) -> int:
    return int(series.astype(str).eq("yes").sum())


def build_filtered_score() -> tuple[pd.DataFrame, dict[str, object]]:
    readiness = pd.read_csv(READINESS)
    formula = pd.read_csv(FORMULA_AWARE)

    allowed = readiness[
        readiness["endpoint_replay_allowed_now"].isin(
            {
                "yes_current_formula_only",
                "yes_current_formula_robustness_only",
            }
        )
    ][
        [
            "support_safe_pool",
            "galaxy",
            "paper8_paper9_overlay_class",
            "scoring_readiness_class",
            "endpoint_replay_allowed_now",
            "next_scoring_action",
        ]
    ]
    filtered = formula.merge(allowed, on=["support_safe_pool", "galaxy"], how="inner")
    filtered["claim_boundary"] = CLAIM_BOUNDARY
    filtered["score_interpretation"] = filtered["scoring_readiness_class"].map(
        {
            "READY_CURRENT_FORMULA_STRICT_SURVIVAL": "strict_positive_row",
            "READY_CURRENT_FORMULA_NEAR_TIE_ROBUSTNESS_ONLY": "near_tie_robustness_row_not_strict_win",
        }
    )

    pool_summary: dict[str, dict[str, object]] = {}
    for pool, group in filtered.groupby("support_safe_pool"):
        pool_summary[pool] = {
            "n_rows": int(len(group)),
            "beats_baryonic": _yes_count(group["candidate_beats_baryonic"]),
            "beats_wrong_component_mean": _yes_count(
                group["candidate_beats_wrong_component_mean"]
            ),
            "beats_best_wrong_component": _yes_count(
                group["candidate_beats_best_wrong_component"]
            ),
            "strict_survival_rows": int(
                (group["scoring_readiness_class"] == "READY_CURRENT_FORMULA_STRICT_SURVIVAL").sum()
            ),
            "near_tie_rows": int(
                (
                    group["scoring_readiness_class"]
                    == "READY_CURRENT_FORMULA_NEAR_TIE_ROBUSTNESS_ONLY"
                ).sum()
            ),
            "median_best_wrong_minus_candidate_kms": float(
                group["best_wrong_minus_candidate_weighted_rmse_kms"].median()
            ),
            "median_wrong_mean_minus_candidate_kms": float(
                group["wrong_mean_minus_candidate_weighted_rmse_kms"].median()
            ),
        }

    summary = {
        "n_rows": int(len(filtered)),
        "n_unique_galaxies": int(filtered["galaxy"].nunique()),
        "unique_galaxies": sorted(filtered["galaxy"].unique().tolist()),
        "beats_baryonic": _yes_count(filtered["candidate_beats_baryonic"]),
        "beats_wrong_component_mean": _yes_count(
            filtered["candidate_beats_wrong_component_mean"]
        ),
        "beats_best_wrong_component": _yes_count(
            filtered["candidate_beats_best_wrong_component"]
        ),
        "strict_survival_rows": int(
            (filtered["scoring_readiness_class"] == "READY_CURRENT_FORMULA_STRICT_SURVIVAL").sum()
        ),
        "near_tie_rows": int(
            (
                filtered["scoring_readiness_class"]
                == "READY_CURRENT_FORMULA_NEAR_TIE_ROBUSTNESS_ONLY"
            ).sum()
        ),
        "pool_summary": pool_summary,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Readiness-filtered scoring is positive against baryonic and wrong-mean "
            "controls for current-formula rows, but strict best-wrong survival remains "
            "limited because near ties are not counted as strict wins."
        ),
    }
    return filtered.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    filtered, summary = build_filtered_score()
    filtered.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "candidate_beats_baryonic",
        "candidate_beats_wrong_component_mean",
        "candidate_beats_best_wrong_component",
        "best_wrong_minus_candidate_weighted_rmse_kms",
        "scoring_readiness_class",
    ]
    print(filtered[cols].to_string(index=False))


if __name__ == "__main__":
    main()
