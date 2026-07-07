from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
FIG_DIR = ROOT / "figures"

IN_JSON = EXTERNAL_DIR / "tcdr_v4_post_external_scoring_boundary_summary_local.json"
OUT_FIG = FIG_DIR / "tcdr_post_external_scoring_boundary.png"


ROUTE_ORDER = [
    "CURRENT_FORMULA_REPLAY_READY",
    "SOURCE_GAP_BLOCKED_AFTER_EXTERNAL_AUDIT",
    "MIXED_ROUTE_BLOCKED_BY_SHUFFLE_CONTROL",
    "KOBS_KREADOUT_RELABEL_BLOCKED_BY_SOURCE_REVIEW",
]

ROUTE_LABELS = {
    "CURRENT_FORMULA_REPLAY_READY": "Replay-ready\ncurrent formula",
    "SOURCE_GAP_BLOCKED_AFTER_EXTERNAL_AUDIT": "Source gap\nblocked after audit",
    "MIXED_ROUTE_BLOCKED_BY_SHUFFLE_CONTROL": "Mixed route\nblocked by shuffle",
    "KOBS_KREADOUT_RELABEL_BLOCKED_BY_SOURCE_REVIEW": "K_obs/K_readout\nblocked by review",
}


def main() -> None:
    summary = json.loads(IN_JSON.read_text(encoding="utf-8"))
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    route_counts = summary["post_external_route_status_counts"]
    route_values = [route_counts.get(key, 0) for key in ROUTE_ORDER]
    weighted = summary["weighted_score_counts_on_allowed_rows"]
    metrics = summary["metric_robustness_on_allowed_rows"]

    metric_labels = [
        "Baryonic\ncarrier",
        "Wrong-component\nmean",
        "Strict\nbest-wrong",
        "Unweighted\nwrong mean",
        "Unweighted\nbest-wrong",
    ]
    metric_values = [
        weighted["beats_baryonic"],
        weighted["beats_wrong_mean"],
        weighted["beats_best_wrong"],
        metrics["rmse_kms"]["beats_wrong_mean"],
        metrics["rmse_kms"]["beats_best_wrong"],
    ]

    fig, (ax0, ax1) = plt.subplots(
        1,
        2,
        figsize=(11.2, 5.05),
        gridspec_kw={"width_ratios": [1.05, 1.0]},
    )

    route_colors = ["#2f6f9f", "#9b3d3d", "#b9792a", "#7c5da8"]
    ax0.bar(range(len(ROUTE_ORDER)), route_values, color=route_colors)
    ax0.set_xticks(range(len(ROUTE_ORDER)))
    ax0.set_xticklabels([ROUTE_LABELS[key] for key in ROUTE_ORDER], fontsize=8)
    ax0.set_ylabel("Rows")
    ax0.set_ylim(0, max(route_values) + 1.6)
    ax0.set_title("Post-external route closure")
    for idx, value in enumerate(route_values):
        ax0.text(idx, value + 0.12, str(value), ha="center", va="bottom", fontsize=10)
    ax0.grid(axis="y", alpha=0.22)
    ax0.text(
        0.02,
        0.96,
        "17 candidate/control rows\n6 score-bearing, 11 blocked",
        transform=ax0.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        color="#333333",
    )

    metric_colors = ["#3a7f5f", "#3a7f5f", "#2f6f9f", "#c9792b", "#c9792b"]
    ax1.bar(range(len(metric_labels)), metric_values, color=metric_colors)
    ax1.set_xticks(range(len(metric_labels)))
    ax1.set_xticklabels(metric_labels, fontsize=8)
    ax1.set_ylabel("Allowed rows passing control")
    ax1.set_ylim(0, 6.8)
    ax1.set_yticks(range(0, 7))
    ax1.set_title("Scoring boundary on allowed rows only")
    for idx, value in enumerate(metric_values):
        ax1.text(idx, value + 0.12, f"{value}/6", ha="center", va="bottom", fontsize=10)
    ax1.grid(axis="y", alpha=0.22)
    fig.suptitle("Paper19 final local scoring boundary after external source audit", y=1.01)
    fig.text(
        0.53,
        0.012,
        "Blocked rows are intentionally score-blank: they preserve negative/source-gap status and carry no scoring claim.",
        ha="center",
        va="bottom",
        fontsize=8.6,
        color="#333333",
    )
    fig.tight_layout(rect=(0, 0.045, 1, 0.98))
    fig.savefig(OUT_FIG, dpi=190, bbox_inches="tight")
    plt.close(fig)
    print(f"WROTE {OUT_FIG}")


if __name__ == "__main__":
    main()
