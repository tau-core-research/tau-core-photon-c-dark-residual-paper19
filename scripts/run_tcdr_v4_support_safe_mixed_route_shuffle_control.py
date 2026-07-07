from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring as formula_aware
import run_tcdr_v4_support_safe_pool_loocv_scoring as pool_scoring


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

READINESS = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_readiness_ledger_local.csv"
FORMULA_AWARE_SUMMARY = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_summary_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_support_safe_mixed_route_shuffle_control_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_support_safe_mixed_route_shuffle_control_summary_local.json"

N_SHUFFLES = 64
RNG_SEED = 19019
SHUFFLE_PASS_P_MAX = 0.10
CLAIM_BOUNDARY = "support_safe_mixed_route_shuffle_control_local_diagnostic_not_validation"

SHUFFLE_COLUMNS = [
    "support_safe_compiled_formula",
    "bar_component_weight",
    "ring_component_weight",
    "spiral_component_weight",
]


def _candidate_wrmse_for_leftout(data: pd.DataFrame, galaxy: str) -> float:
    test = data[data["galaxy"] == galaxy].copy()
    train = data[data["galaxy"] != galaxy].copy()
    candidate_kernel_train = formula_aware._candidate_kernel(train)
    candidate_kernel_test = formula_aware._candidate_kernel(test)
    amp = pool_scoring._fit_amplitude(train, candidate_kernel_train)
    _, wrmse = pool_scoring._weighted_rmse(test, candidate_kernel_test, amp)
    return float(wrmse)


def _shuffle_formula_packages(data: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    shuffled = data.copy()
    galaxy_meta = (
        shuffled[["galaxy", *SHUFFLE_COLUMNS]]
        .drop_duplicates("galaxy")
        .sort_values("galaxy")
        .reset_index(drop=True)
    )
    permuted = galaxy_meta[SHUFFLE_COLUMNS].sample(
        frac=1.0,
        replace=False,
        random_state=int(rng.integers(0, 2**32 - 1)),
    ).reset_index(drop=True)
    replacement = pd.concat([galaxy_meta[["galaxy"]], permuted], axis=1)
    shuffled = shuffled.drop(columns=SHUFFLE_COLUMNS).merge(replacement, on="galaxy", how="left")
    return shuffled


def run_shuffle_control() -> tuple[pd.DataFrame, dict[str, object]]:
    readiness = pd.read_csv(READINESS)
    actual = pd.read_csv(FORMULA_AWARE_SUMMARY)
    mixed_rows = readiness[
        readiness["scoring_readiness_class"].eq("NOT_READY_MIXED_ROUTE_REQUIRES_NONOVERLAP")
    ].copy()
    actual_lookup = actual.set_index(["support_safe_pool", "galaxy"])
    rng = np.random.default_rng(RNG_SEED)

    rows: list[dict[str, object]] = []
    for pool_name, config in pool_scoring.POOL_CONFIGS.items():
        pool_mixed = mixed_rows[mixed_rows["support_safe_pool"].eq(pool_name)]
        if pool_mixed.empty:
            continue
        data = formula_aware._load_formula_data(pool_name, config)
        shuffled_scores: dict[str, list[float]] = {
            str(galaxy): [] for galaxy in pool_mixed["galaxy"]
        }
        for _ in range(N_SHUFFLES):
            shuffled_data = _shuffle_formula_packages(data, rng)
            for galaxy in shuffled_scores:
                shuffled_scores[galaxy].append(_candidate_wrmse_for_leftout(shuffled_data, galaxy))

        for _, row in pool_mixed.iterrows():
            galaxy = str(row["galaxy"])
            actual_wrmse = float(
                actual_lookup.loc[(pool_name, galaxy), "candidate_weighted_rmse_kms"]
            )
            values = np.array(shuffled_scores[galaxy], dtype=float)
            n_better_or_equal = int(np.sum(values <= actual_wrmse))
            empirical_p = float((n_better_or_equal + 1) / (len(values) + 1))
            median_shuffle = float(np.median(values))
            q10 = float(np.quantile(values, 0.10))
            q90 = float(np.quantile(values, 0.90))
            nonoverlap_closed = (
                str(row["support_aware_selector_status"])
                == "SUPPORT_AWARE_SELECTOR_SAFE_DOMINANT_DISJOINT"
            )
            shuffle_pass = empirical_p <= SHUFFLE_PASS_P_MAX and actual_wrmse < median_shuffle
            rows.append(
                {
                    "support_safe_pool": pool_name,
                    "galaxy": galaxy,
                    "matched_component": row["matched_component"],
                    "best_wrong_component": row["best_wrong_component"],
                    "positive_components": row["positive_components"],
                    "support_aware_selector_status": row["support_aware_selector_status"],
                    "nonoverlap_closed": "yes" if nonoverlap_closed else "no",
                    "actual_formula_candidate_weighted_rmse_kms": actual_wrmse,
                    "median_shuffled_formula_candidate_weighted_rmse_kms": median_shuffle,
                    "q10_shuffled_formula_candidate_weighted_rmse_kms": q10,
                    "q90_shuffled_formula_candidate_weighted_rmse_kms": q90,
                    "actual_minus_shuffle_median_weighted_rmse_kms": actual_wrmse - median_shuffle,
                    "n_shuffles": int(len(values)),
                    "n_shuffled_better_or_equal_actual": n_better_or_equal,
                    "empirical_shuffle_p_better_or_equal": empirical_p,
                    "shuffle_pass_threshold": SHUFFLE_PASS_P_MAX,
                    "shuffle_control_pass": "yes" if shuffle_pass else "no",
                    "mixed_route_scoring_permission": (
                        "ready_for_caveated_mixed_route_score"
                        if nonoverlap_closed and shuffle_pass
                        else "blocked_shuffle_or_nonoverlap_not_closed"
                    ),
                    "shuffle_policy": (
                        "support_safe_formula_package_shuffle_preserve_pool_membership_"
                        f"n{N_SHUFFLES}_seed{RNG_SEED}"
                    ),
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )

    result = pd.DataFrame(rows).sort_values(["support_safe_pool", "galaxy"])
    summary = {
        "n_rows": int(len(result)),
        "n_unique_galaxies": int(result["galaxy"].nunique()) if not result.empty else 0,
        "n_shuffles": N_SHUFFLES,
        "rng_seed": RNG_SEED,
        "shuffle_pass_threshold": SHUFFLE_PASS_P_MAX,
        "nonoverlap_closed_counts": result["nonoverlap_closed"].value_counts().to_dict()
        if not result.empty
        else {},
        "shuffle_control_pass_counts": result["shuffle_control_pass"].value_counts().to_dict()
        if not result.empty
        else {},
        "mixed_route_scoring_permission_counts": result[
            "mixed_route_scoring_permission"
        ].value_counts().to_dict()
        if not result.empty
        else {},
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Mixed-route rows require both source non-overlap and shuffled formula-package "
            "survival. Passing this diagnostic is caveated route permission only, not "
            "endpoint validation."
        ),
    }
    return result, summary


def main() -> None:
    result, summary = run_shuffle_control()
    result.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
