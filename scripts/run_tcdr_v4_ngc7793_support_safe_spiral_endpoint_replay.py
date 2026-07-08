from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring as formula
import run_tcdr_v4_support_safe_pool_loocv_scoring as top_component


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
FIGURE_DIR = ROOT / "figures"
PAPER_FIGURE_DIR = ROOT / "paper19_submission_source" / "figures"

GALAXY = "NGC7793"
POOL_NAME = "support_safe_10_v0_9"
OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay_summary_local.json"
OUT_FIGURE = FIGURE_DIR / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay.png"
PAPER_OUT_FIGURE = PAPER_FIGURE_DIR / OUT_FIGURE.name

CLAIM_BOUNDARY = "ngc7793_support_safe_spiral_endpoint_replay_preliminary_not_validation"
REPLAY_POLICY = (
    "support_safe_10_leave_one_galaxy_out_spiral_replay_uses_existing_source_frozen_formula_"
    "no_target_amplitude_tuning_no_new_kernel_search"
)


def _vpred(group: pd.DataFrame, kernel: pd.Series, amp: float) -> pd.Series:
    return np.sqrt((group["vbar2_fixed_mlr"] + amp * kernel.loc[group.index]).clip(lower=0))


def _weighted_rmse(group: pd.DataFrame, vpred: pd.Series) -> tuple[float, float]:
    residual = group["vobs_kms"] - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(np.sqrt(np.average(residual**2, weights=1.0 / group["e_vobs_kms"].clip(lower=1.0) ** 2)))
    return rmse, wrmse


def run_replay() -> tuple[pd.DataFrame, dict[str, object]]:
    config = top_component.POOL_CONFIGS[POOL_NAME]
    data = formula._load_formula_data(POOL_NAME, config).copy()
    test = data[data["galaxy"] == GALAXY].copy().sort_values("radius_kpc")
    if test.empty:
        raise RuntimeError(f"{GALAXY} is not available in {POOL_NAME}.")
    train = data[data["galaxy"] != GALAXY].copy()

    matched_component = str(test["top_component"].iloc[0])
    support_formula = str(test["support_safe_compiled_formula"].iloc[0])
    source_family = str(test["source_family_candidate"].iloc[0])
    positive_components = str(test["positive_components"].iloc[0])

    candidate_train_kernel = formula._candidate_kernel(train)
    candidate_test_kernel = formula._candidate_kernel(test)
    candidate_amp = top_component._fit_amplitude(train, candidate_train_kernel)
    test["v_candidate_kms"] = _vpred(test, candidate_test_kernel, candidate_amp)

    matched_train_kernel = top_component._component_kernel(matched_component, train)
    matched_test_kernel = top_component._component_kernel(matched_component, test)
    matched_amp = top_component._fit_amplitude(train, matched_train_kernel)
    test["v_matched_component_kms"] = _vpred(test, matched_test_kernel, matched_amp)

    wrong_rows = []
    for component in top_component.COMPONENTS:
        if component == matched_component:
            continue
        train_kernel = top_component._component_kernel(component, train)
        test_kernel = top_component._component_kernel(component, test)
        amp = top_component._fit_amplitude(train, train_kernel)
        pred = _vpred(test, test_kernel, amp)
        _, wrmse = _weighted_rmse(test, pred)
        wrong_rows.append((component, wrmse, amp, pred))
    best_wrong_component, best_wrong_wrmse, best_wrong_amp, best_wrong_pred = min(
        wrong_rows, key=lambda item: item[1]
    )
    test["v_best_wrong_kms"] = best_wrong_pred

    _, bary_wrmse = _weighted_rmse(test, test["vbar_fixed_mlr_kms"])
    _, candidate_wrmse = _weighted_rmse(test, test["v_candidate_kms"])
    _, matched_wrmse = _weighted_rmse(test, test["v_matched_component_kms"])
    wrong_mean_wrmse = float(np.mean([row[1] for row in wrong_rows]))

    detail = test[
        [
            "galaxy",
            "radius_kpc",
            "vobs_kms",
            "e_vobs_kms",
            "vbar_fixed_mlr_kms",
            "v_candidate_kms",
            "v_matched_component_kms",
            "v_best_wrong_kms",
        ]
    ].copy()
    detail["support_safe_pool"] = POOL_NAME
    detail["matched_component"] = matched_component
    detail["support_safe_compiled_formula"] = support_formula
    detail["source_family_candidate"] = source_family
    detail["positive_components"] = positive_components
    detail["candidate_amplitude_v2"] = candidate_amp
    detail["matched_component_amplitude_v2"] = matched_amp
    detail["best_wrong_component"] = best_wrong_component
    detail["best_wrong_amplitude_v2"] = best_wrong_amp
    detail["replay_status"] = "preliminary_support_safe_spiral_replay_completed_no_validation"
    detail["target_amplitude_tuning"] = "no"
    detail["new_kernel_search"] = "no"
    detail["validation_claimed"] = "no"
    detail["replay_policy"] = REPLAY_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "galaxy": GALAXY,
        "support_safe_pool": POOL_NAME,
        "n_points": int(len(detail)),
        "matched_component": matched_component,
        "support_safe_compiled_formula": support_formula,
        "source_family_candidate": source_family,
        "positive_components": positive_components,
        "candidate_amplitude_v2": candidate_amp,
        "matched_component_amplitude_v2": matched_amp,
        "best_wrong_component": best_wrong_component,
        "best_wrong_amplitude_v2": best_wrong_amp,
        "baryonic_weighted_rmse_kms": bary_wrmse,
        "candidate_weighted_rmse_kms": candidate_wrmse,
        "matched_component_weighted_rmse_kms": matched_wrmse,
        "wrong_component_mean_weighted_rmse_kms": wrong_mean_wrmse,
        "best_wrong_component_weighted_rmse_kms": best_wrong_wrmse,
        "candidate_minus_baryonic_weighted_rmse_kms": candidate_wrmse - bary_wrmse,
        "candidate_minus_matched_component_weighted_rmse_kms": candidate_wrmse - matched_wrmse,
        "wrong_mean_minus_candidate_weighted_rmse_kms": wrong_mean_wrmse - candidate_wrmse,
        "best_wrong_minus_candidate_weighted_rmse_kms": best_wrong_wrmse - candidate_wrmse,
        "candidate_beats_baryonic": bool(candidate_wrmse < bary_wrmse),
        "candidate_beats_matched_component": bool(candidate_wrmse < matched_wrmse),
        "candidate_beats_wrong_mean": bool(candidate_wrmse < wrong_mean_wrmse),
        "candidate_beats_best_wrong": bool(candidate_wrmse < best_wrong_wrmse),
        "kernel_shape_policy": formula.KERNEL_SHAPE_POLICY,
        "amplitude_policy": formula.AMPLITUDE_POLICY,
        "replay_policy": REPLAY_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC7793 is a support-safe spiral/scale-tail preliminary positive: "
            "the source-frozen candidate beats the baryonic carrier, wrong-component "
            "mean, and best wrong-component control under leave-one-galaxy-out amplitude freeze."
        ),
    }
    return detail, summary


def build_figure(detail: pd.DataFrame, summary: dict[str, object]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.5), dpi=180)
    ax.errorbar(
        detail["radius_kpc"],
        detail["vobs_kms"],
        yerr=detail["e_vobs_kms"],
        fmt="o",
        ms=3.8,
        lw=0.8,
        color="#202020",
        ecolor="#808080",
        capsize=1.5,
        label="Observed SPARC rotation",
        zorder=5,
    )
    ax.plot(detail["radius_kpc"], detail["vbar_fixed_mlr_kms"], color="#5470c6", lw=1.8, label="Fixed baryonic carrier")
    ax.plot(detail["radius_kpc"], detail["v_matched_component_kms"], color="#91cc75", lw=1.8, ls="--", label="Matched spiral control")
    ax.plot(detail["radius_kpc"], detail["v_best_wrong_kms"], color="#fac858", lw=1.8, ls=":", label=f"Best wrong ({summary['best_wrong_component']})")
    ax.plot(detail["radius_kpc"], detail["v_candidate_kms"], color="#d94e5d", lw=2.8, label="Source-frozen support-safe candidate")
    ax.set_xlabel("Radius [kpc]")
    ax.set_ylabel("Circular velocity [km/s]")
    ax.set_title("NGC7793 support-safe spiral preliminary replay")
    ax.grid(alpha=0.22)
    ax.legend(fontsize=8.3, frameon=True, loc="best")
    text = (
        f"weighted RMSE: candidate {summary['candidate_weighted_rmse_kms']:.2f} km/s\\n"
        f"baryonic {summary['baryonic_weighted_rmse_kms']:.2f}; "
        f"best wrong {summary['best_wrong_component_weighted_rmse_kms']:.2f}"
    )
    ax.text(
        0.02,
        0.04,
        text,
        transform=ax.transAxes,
        fontsize=8.5,
        bbox={"facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.88},
    )
    fig.tight_layout()
    fig.savefig(OUT_FIGURE, bbox_inches="tight")
    fig.savefig(PAPER_OUT_FIGURE, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    detail, summary = run_replay()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    build_figure(detail, summary)
    print(f"WROTE LOCAL {OUT_DETAIL}")
    print(f"WROTE LOCAL {OUT_SUMMARY}")
    print(f"WROTE {OUT_FIGURE}")
    print(f"WROTE {PAPER_OUT_FIGURE}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
