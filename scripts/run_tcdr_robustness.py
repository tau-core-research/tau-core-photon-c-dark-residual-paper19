from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_tcdr_toys import RegressionResult, simulate_v1, simulate_v2, simulate_v3


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
RESULT_DIR = ROOT / "data" / "derived"
FIG_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

SimFn = Callable[[float, np.random.Generator], RegressionResult]


CASES: list[tuple[str, float, SimFn, int]] = [
    ("TCDR-v1", 0.00, simulate_v1, 0),
    ("TCDR-v1", 0.60, simulate_v1, 4),
    ("TCDR-v2", 0.00, simulate_v2, 0),
    ("TCDR-v2", 0.60, simulate_v2, 4),
    ("TCDR-v3", 0.00, simulate_v3, 0),
    ("TCDR-v3", 0.35, simulate_v3, 3),
    ("TCDR-v3", 0.60, simulate_v3, 3),
]


def run_multiseed(n_reps: int = 32) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for case_idx, (module, strength, fn, expected_score_floor) in enumerate(CASES):
        for rep in range(n_reps):
            rng = np.random.default_rng(190000 + 997 * rep + 10007 * case_idx)
            result = fn(strength, rng)
            rows.append(
                {
                    "module": module,
                    "tau_strength": strength,
                    "rep": rep,
                    "r2_base": result.r2_base,
                    "r2_tau": result.r2_tau,
                    "delta_r2": result.delta_r2,
                    "permutation_p": result.permutation_p,
                    "score": result.score,
                    "expected_score_floor": expected_score_floor,
                    "passes_floor": int(result.score >= expected_score_floor),
                    "is_null": int(strength == 0.0),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "tcdr_multiseed_robustness.csv", index=False)
    return out


def aggregate_multiseed(multiseed: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (module, strength), group in multiseed.groupby(["module", "tau_strength"]):
        rows.append(
            {
                "module": module,
                "tau_strength": strength,
                "n": len(group),
                "mean_delta_r2": group["delta_r2"].mean(),
                "median_delta_r2": group["delta_r2"].median(),
                "sd_delta_r2": group["delta_r2"].std(ddof=1),
                "mean_p": group["permutation_p"].mean(),
                "median_p": group["permutation_p"].median(),
                "mean_score": group["score"].mean(),
                "pass_rate_floor": group["passes_floor"].mean(),
                "false_positive_rate": (
                    (group["score"] > 0).mean() if float(strength) == 0.0 else np.nan
                ),
            }
        )
    out = pd.DataFrame(rows).sort_values(["module", "tau_strength"])
    out.to_csv(RESULT_DIR / "tcdr_multiseed_robustness_summary.csv", index=False)
    return out


def threshold_sensitivity(multiseed: pd.DataFrame) -> pd.DataFrame:
    delta_thresholds = [0.005, 0.010, 0.015, 0.030, 0.050, 0.100]
    p_thresholds = [0.01, 0.05, 0.10]
    positive = multiseed[multiseed["expected_score_floor"] > 0].copy()
    null = multiseed[multiseed["is_null"] == 1].copy()
    rows = []
    for p_thr in p_thresholds:
        for d_thr in delta_thresholds:
            pos_flag = (positive["permutation_p"] <= p_thr) & (positive["delta_r2"] >= d_thr)
            null_flag = (null["permutation_p"] <= p_thr) & (null["delta_r2"] >= d_thr)
            rows.append(
                {
                    "p_threshold": p_thr,
                    "delta_r2_threshold": d_thr,
                    "positive_recovery_fraction": pos_flag.mean(),
                    "null_false_positive_fraction": null_flag.mean(),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(RESULT_DIR / "tcdr_threshold_sensitivity.csv", index=False)
    return out


def make_plots(summary: pd.DataFrame, sensitivity: pd.DataFrame) -> None:
    null = summary[summary["tau_strength"] == 0.0].copy()
    injected = summary[summary["tau_strength"] > 0.0].copy()

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), sharey=True)
    injected_labels = [
        f"{row.module}\ntau={row.tau_strength:g}" for row in injected.itertuples(index=False)
    ]
    axes[0].bar(injected_labels, injected["pass_rate_floor"], color="#3b6fb6")
    axes[0].set_title("Injected cases")
    axes[0].set_ylabel("Fraction")
    axes[0].set_ylim(0, 1.05)
    axes[0].tick_params(axis="x", rotation=30)

    null_labels = [row.module for row in null.itertuples(index=False)]
    axes[1].bar(null_labels, null["false_positive_rate"], color="#b6533b")
    axes[1].set_title("No-injection null cases")
    axes[1].set_ylim(0, 1.05)
    axes[1].tick_params(axis="x", rotation=30)
    fig.suptitle("TCDR multi-seed robustness replay")
    axes[0].text(0.5, -0.27, "pass rate above declared floor", ha="center", transform=axes[0].transAxes)
    axes[1].text(0.5, -0.27, "false-positive rate", ha="center", transform=axes[1].transAxes)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_multiseed_passrate.png", dpi=170)
    plt.close()

    plt.figure(figsize=(7.5, 5))
    for p_thr, group in sensitivity.groupby("p_threshold"):
        group = group.sort_values("delta_r2_threshold")
        plt.plot(
            group["null_false_positive_fraction"],
            group["positive_recovery_fraction"],
            marker="o",
            label=f"p <= {p_thr:g}",
        )
    plt.xlabel("Null false-positive fraction")
    plt.ylabel("Injected-positive recovery fraction")
    plt.title("TCDR threshold sensitivity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_threshold_sensitivity.png", dpi=170)
    plt.close()


def main() -> None:
    multiseed = run_multiseed()
    summary = aggregate_multiseed(multiseed)
    sensitivity = threshold_sensitivity(multiseed)
    make_plots(summary, sensitivity)
    print("TCDR robustness replay completed.")
    print(summary.to_string(index=False))
    print(f"\nResults written to: {RESULT_DIR}")
    print(f"Figures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
