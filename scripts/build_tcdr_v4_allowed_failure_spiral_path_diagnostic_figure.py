from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import run_tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring as diagnostic
import run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring as formula_aware
import run_tcdr_v4_support_safe_pool_loocv_scoring as top_component


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
FIG_DIR = ROOT / "figures"

READINESS_SCORING = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_readiness_filtered_scoring_local.csv"
OUT_FIG = FIG_DIR / "tcdr_ngc2841_spiral_path_diagnostic_replay.png"


def _velocity(vbar2: pd.Series, kernel: pd.Series, amp: float) -> np.ndarray:
    return np.sqrt((vbar2 + amp * kernel).clip(lower=0)).to_numpy()


def _pool_curves(pool_name: str, config: dict[str, object], formula_row: pd.Series) -> dict[str, object]:
    data = formula_aware._load_formula_data(pool_name, config)
    galaxy = str(formula_row["galaxy"])
    test = data[data["galaxy"].eq(galaxy)].copy().sort_values("radius_kpc")
    train = data[~data["galaxy"].eq(galaxy)].copy()

    readiness = pd.read_csv(READINESS_SCORING)
    row = readiness[readiness["support_safe_pool"].eq(pool_name) & readiness["galaxy"].eq(galaxy)].iloc[0]
    best_wrong = str(row["best_wrong_component"])

    current_kernel_train = formula_aware._candidate_kernel(train)
    current_kernel_test = formula_aware._candidate_kernel(test)
    current_amp = top_component._fit_amplitude(train, current_kernel_train)

    best_wrong_kernel_train = top_component._component_kernel(best_wrong, train)
    best_wrong_kernel_test = top_component._component_kernel(best_wrong, test)
    best_wrong_amp = top_component._fit_amplitude(train, best_wrong_kernel_train)

    spiral_path_kernel_test = diagnostic._spiral_path_kernel(test, formula_row)
    spiral_path_amp = top_component._fit_amplitude(train, top_component._component_kernel("spiral", train))

    return {
        "pool_name": pool_name,
        "test": test,
        "current_velocity": _velocity(test["vbar2_fixed_mlr"], current_kernel_test, current_amp),
        "best_wrong_velocity": _velocity(test["vbar2_fixed_mlr"], best_wrong_kernel_test, best_wrong_amp),
        "spiral_path_velocity": _velocity(test["vbar2_fixed_mlr"], spiral_path_kernel_test, spiral_path_amp),
        "best_wrong": best_wrong,
        "current_amp": current_amp,
        "best_wrong_amp": best_wrong_amp,
        "spiral_path_amp": spiral_path_amp,
    }


def main() -> None:
    formula = diagnostic._load_formula_rows()
    formula_row = formula[formula["galaxy"].eq("NGC2841")].iloc[0]
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    panels = [
        _pool_curves(pool_name, config, formula_row)
        for pool_name, config in top_component.POOL_CONFIGS.items()
    ]
    panels = sorted(panels, key=lambda item: item["pool_name"])

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(12.2, 7.2),
        sharex="col",
        gridspec_kw={"height_ratios": [2.15, 1.0]},
    )
    top_axes = axes[0]
    delta_axes = axes[1]
    for ax, dax, panel in zip(top_axes, delta_axes, panels, strict=True):
        test = panel["test"]
        radius = test["radius_kpc"].to_numpy()
        ax.errorbar(
            radius,
            test["vobs_kms"].to_numpy(),
            yerr=test["e_vobs_kms"].clip(lower=1.0).to_numpy(),
            fmt="o",
            ms=3.4,
            lw=0.8,
            color="#1f1f1f",
            ecolor="#9a9a9a",
            alpha=0.84,
            label="SPARC observed",
        )
        ax.plot(
            radius,
            test["vbar_fixed_mlr_kms"].to_numpy(),
            color="#777777",
            lw=1.9,
            ls="--",
            label="fixed baryonic carrier",
        )
        ax.plot(
            radius,
            panel["current_velocity"],
            color="#2f6f9f",
            lw=2.0,
            label="previous frozen formula",
        )
        ax.plot(
            radius,
            panel["best_wrong_velocity"],
            color="#b9792a",
            lw=2.0,
            label=f"best wrong ({panel['best_wrong']})",
        )
        ax.plot(
            radius,
            panel["spiral_path_velocity"],
            color="#7b3f98",
            lw=2.6,
            label="source-frozen spiral/path",
        )
        dax.axhline(0, color="#444444", lw=1.0)
        dax.plot(
            radius,
            panel["spiral_path_velocity"] - panel["current_velocity"],
            color="#7b3f98",
            lw=2.2,
            label="spiral/path - previous",
        )
        dax.plot(
            radius,
            panel["best_wrong_velocity"] - panel["current_velocity"],
            color="#b9792a",
            lw=1.8,
            label=f"best wrong - previous",
        )
        ax.axvspan(
            float(formula_row["r_in_kpc"]),
            float(formula_row["r_out_kpc"]),
            color="#7b3f98",
            alpha=0.09,
            label="frozen spiral window",
        )
        ax.axvline(float(formula_row["r_path_kpc"]), color="#7b3f98", lw=1.1, ls=":", alpha=0.8)
        dax.axvspan(
            float(formula_row["r_in_kpc"]),
            float(formula_row["r_out_kpc"]),
            color="#7b3f98",
            alpha=0.09,
        )
        dax.axvline(float(formula_row["r_path_kpc"]), color="#7b3f98", lw=1.1, ls=":", alpha=0.8)
        title = panel["pool_name"].replace("support_safe_10_v0_9", "support-safe 10")
        title = title.replace("support_safe_7_v0_7", "support-safe 7")
        ax.set_title(title)
        ax.grid(alpha=0.22)
        dax.grid(alpha=0.22)
        dax.set_xlabel("Radius (kpc)")
        dax.set_ylabel("Delta v (km/s)")
        ax.text(
            0.03,
            0.04,
            "shape: source-frozen\namplitude: other galaxies only",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8.2,
            color="#333333",
            bbox={"facecolor": "white", "alpha": 0.78, "edgecolor": "#cccccc", "pad": 3},
        )
    top_axes[0].set_ylabel("Circular velocity (km/s)")
    handles, labels = top_axes[1].get_legend_handles_labels()
    dhandles, dlabels = delta_axes[1].get_legend_handles_labels()
    handles += dhandles
    labels += dlabels
    by_label = dict(zip(labels, handles))
    fig.legend(
        by_label.values(),
        by_label.keys(),
        loc="lower center",
        ncol=3,
        fontsize=8.4,
        frameon=True,
        bbox_to_anchor=(0.5, 0.005),
    )
    fig.suptitle("NGC2841 allowed-failure diagnostic replay: source-frozen spiral/path shell")
    fig.tight_layout(rect=(0, 0.12, 1, 0.94))
    fig.savefig(OUT_FIG, dpi=190, bbox_inches="tight")
    plt.close(fig)
    print(f"WROTE {OUT_FIG}")


if __name__ == "__main__":
    main()
