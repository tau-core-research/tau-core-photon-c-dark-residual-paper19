from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
FIG_DIR = ROOT / "figures"

IN_CSV = EXTERNAL_DIR / "tcdr_v4_readiness_filtered_metric_robustness_local.csv"
OUT_FIG = FIG_DIR / "tcdr_readiness_filtered_metric_robustness.png"


def main() -> None:
    data = pd.read_csv(IN_CSV)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    data["row_label"] = data["support_safe_pool"].str.replace("support_safe_", "pool ", regex=False)
    data["row_label"] = data["row_label"].str.replace("_v0_9", "", regex=False)
    data["row_label"] = data["row_label"].str.replace("_v0_7", "", regex=False)
    data["row_label"] = data["galaxy"] + "\n" + data["row_label"]

    pivot = data.pivot(
        index="row_label",
        columns="metric",
        values="best_wrong_minus_candidate_metric",
    )
    ordered = data[["row_label", "support_safe_pool", "galaxy"]].drop_duplicates()
    ordered = ordered.sort_values(["support_safe_pool", "galaxy"])
    pivot = pivot.loc[ordered["row_label"]]

    labels = list(pivot.index)
    x = range(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9.2, 4.9))
    ax.axhspan(-0.1, 0.1, color="#f2e8b8", alpha=0.55, label="near-tie band")
    ax.axhline(0, color="#222222", linewidth=1.0)
    ax.bar(
        [i - width / 2 for i in x],
        pivot["weighted_rmse_kms"],
        width=width,
        color="#2f6f9f",
        label="weighted RMSE",
    )
    ax.bar(
        [i + width / 2 for i in x],
        pivot["rmse_kms"],
        width=width,
        color="#c9792b",
        label="unweighted RMSE",
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=0, fontsize=8)
    ax.set_ylabel("Best-wrong margin (km/s)")
    ax.set_title("Readiness-filtered metric robustness: current-formula rows")
    ax.text(
        0.01,
        0.97,
        "positive margin = candidate beats best wrong component",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8.5,
        color="#333333",
    )
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="lower right", frameon=True)
    fig.tight_layout()
    fig.savefig(OUT_FIG, dpi=190)
    plt.close(fig)
    print(f"WROTE {OUT_FIG}")


if __name__ == "__main__":
    main()
