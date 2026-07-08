from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready as ready
import run_tcdr_v4_holdout_endpoint_scoring_mixed_components as mixed
import run_tcdr_v4_holdout_endpoint_scoring as base


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
FIGURE_DIR = ROOT / "figures"
PAPER_FIGURE_DIR = ROOT / "paper19_submission_source" / "figures"

OUT_DETAIL = EXTERNAL_DIR / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay_detail_local.csv"
OUT_SUMMARY = EXTERNAL_DIR / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay_summary_local.json"
OUT_FIGURE = FIGURE_DIR / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay.png"
PAPER_OUT_FIGURE = PAPER_FIGURE_DIR / OUT_FIGURE.name

GALAXY = "NGC6503"
CLAIM_BOUNDARY = "ngc6503_clean_scale_tail_endpoint_replay_preliminary_not_validation"
REPLAY_POLICY = (
    "single_galaxy_formula_ready_replay_uses_existing_source_frozen_scale_tail_route_"
    "no_new_kernel_search_no_target_amplitude_tuning"
)


def _weighted_rmse(vobs: pd.Series, evobs: pd.Series, vpred: pd.Series) -> tuple[float, float]:
    residual = vobs - vpred
    rmse = float(np.sqrt(np.mean(residual**2)))
    wrmse = float(np.sqrt(np.average(residual**2, weights=1.0 / evobs.clip(lower=1.0) ** 2)))
    return rmse, wrmse


def _load_formula_ready_data() -> pd.DataFrame:
    mixed.MIXED_KERNEL_FREEZE = ready.RADIAL_GEOMETRY_FREEZE
    mixed.KERNEL_SHAPE_POLICY = ready.KERNEL_SHAPE_POLICY
    mixed.SCORING_POLICY = ready.SCORING_POLICY
    original_loader = mixed._load_data
    try:
        mixed._load_data = lambda: ready._load_ready_data_with(original_loader)
        data = mixed._load_data()
    finally:
        mixed._load_data = original_loader
    return data


def run_replay() -> tuple[pd.DataFrame, dict[str, object]]:
    data = _load_formula_ready_data()
    train = data[data["pilot_role"] == "PILOT_TRAIN_POOL"].copy()
    holdout = data[data["pilot_role"] == "PILOT_HOLDOUT"].copy()
    group = holdout[holdout["galaxy"] == GALAXY].copy().sort_values("radius_kpc")
    if group.empty:
        raise RuntimeError(f"{GALAXY} is not available in the formula-ready holdout packet.")

    mixed_amp = mixed._fit_mixed_amplitude(train)
    pure_calibration = mixed._fit_pure_amplitudes(train)
    pure_amplitudes = {
        family: float(values["family_amplitude_v2"]) for family, values in pure_calibration.items()
    }
    matched_family = str(group["source_family_candidate"].iloc[0])
    compiled_formula = str(group["compiled_formula_family_candidate"].iloc[0])
    available_components = str(group["available_formula_components"].iloc[0])
    component_status = str(group["component_mixture_status"].iloc[0])

    candidate_kernel = mixed._mixed_kernel_for_group(group)
    matched_kernel = mixed._source_native_kernel(matched_family, group)
    group["v_candidate_kms"] = np.sqrt((group["vbar2_fixed_mlr"] + mixed_amp * candidate_kernel).clip(lower=0))
    group["v_pure_matched_kms"] = np.sqrt(
        (group["vbar2_fixed_mlr"] + pure_amplitudes[matched_family] * matched_kernel).clip(lower=0)
    )

    wrong_rows = []
    for family in base.FAMILIES:
        if family == matched_family:
            continue
        kernel = mixed._source_native_kernel(family, group)
        amp = pure_amplitudes[family]
        vpred = np.sqrt((group["vbar2_fixed_mlr"] + amp * kernel).clip(lower=0))
        _, wrmse = _weighted_rmse(group["vobs_kms"], group["e_vobs_kms"], vpred)
        wrong_rows.append((family, wrmse, vpred))
    best_wrong_family, best_wrong_wrmse, best_wrong_vpred = min(wrong_rows, key=lambda item: item[1])
    group["v_best_wrong_kms"] = best_wrong_vpred

    _, bary_wrmse = _weighted_rmse(group["vobs_kms"], group["e_vobs_kms"], group["vbar_fixed_mlr_kms"])
    _, candidate_wrmse = _weighted_rmse(group["vobs_kms"], group["e_vobs_kms"], group["v_candidate_kms"])
    _, pure_matched_wrmse = _weighted_rmse(group["vobs_kms"], group["e_vobs_kms"], group["v_pure_matched_kms"])
    wrong_mean_wrmse = float(np.mean([row[1] for row in wrong_rows]))

    detail = group[
        [
            "galaxy",
            "radius_kpc",
            "vobs_kms",
            "e_vobs_kms",
            "vbar_fixed_mlr_kms",
            "v_candidate_kms",
            "v_pure_matched_kms",
            "v_best_wrong_kms",
        ]
    ].copy()
    detail["matched_source_family"] = matched_family
    detail["compiled_formula_family_candidate"] = compiled_formula
    detail["available_formula_components"] = available_components
    detail["component_mixture_status"] = component_status
    detail["candidate_amplitude_v2"] = mixed_amp
    detail["pure_matched_amplitude_v2"] = pure_amplitudes[matched_family]
    detail["best_wrong_family"] = best_wrong_family
    detail["best_wrong_weighted_rmse_kms"] = best_wrong_wrmse
    detail["replay_status"] = "preliminary_clean_scale_tail_replay_completed_no_validation"
    detail["target_amplitude_tuning"] = "no"
    detail["new_kernel_search"] = "no"
    detail["validation_claimed"] = "no"
    detail["replay_policy"] = REPLAY_POLICY
    detail["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "galaxy": GALAXY,
        "n_points": int(len(detail)),
        "matched_source_family": matched_family,
        "compiled_formula_family_candidate": compiled_formula,
        "available_formula_components": available_components,
        "component_mixture_status": component_status,
        "candidate_amplitude_v2": mixed_amp,
        "pure_matched_amplitude_v2": pure_amplitudes[matched_family],
        "baryonic_weighted_rmse_kms": bary_wrmse,
        "candidate_weighted_rmse_kms": candidate_wrmse,
        "pure_matched_weighted_rmse_kms": pure_matched_wrmse,
        "wrong_family_mean_weighted_rmse_kms": wrong_mean_wrmse,
        "best_wrong_family": best_wrong_family,
        "best_wrong_weighted_rmse_kms": best_wrong_wrmse,
        "candidate_minus_baryonic_weighted_rmse_kms": candidate_wrmse - bary_wrmse,
        "candidate_minus_pure_matched_weighted_rmse_kms": candidate_wrmse - pure_matched_wrmse,
        "wrong_mean_minus_candidate_weighted_rmse_kms": wrong_mean_wrmse - candidate_wrmse,
        "best_wrong_minus_candidate_weighted_rmse_kms": best_wrong_wrmse - candidate_wrmse,
        "candidate_beats_baryonic": bool(candidate_wrmse < bary_wrmse),
        "candidate_beats_pure_matched": bool(candidate_wrmse < pure_matched_wrmse),
        "candidate_beats_wrong_mean": bool(candidate_wrmse < wrong_mean_wrmse),
        "candidate_beats_best_wrong": bool(candidate_wrmse < best_wrong_wrmse),
        "kernel_shape_policy": ready.KERNEL_SHAPE_POLICY,
        "carrier_policy": base.CARRIER_POLICY,
        "amplitude_policy": mixed.AMPLITUDE_POLICY,
        "replay_policy": REPLAY_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC6503 is a clean formula-ready scale-tail candidate: the source-frozen "
            "candidate beats the baryonic carrier, pure matched exponential control, "
            "wrong-family mean, and best wrong-family control in this preliminary replay."
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
    ax.plot(detail["radius_kpc"], detail["v_pure_matched_kms"], color="#91cc75", lw=1.8, ls="--", label="Pure matched exponential")
    ax.plot(detail["radius_kpc"], detail["v_best_wrong_kms"], color="#fac858", lw=1.8, ls=":", label=f"Best wrong ({summary['best_wrong_family']})")
    ax.plot(detail["radius_kpc"], detail["v_candidate_kms"], color="#d94e5d", lw=2.8, label="Source-frozen scale-tail candidate")
    ax.set_xlabel("Radius [kpc]")
    ax.set_ylabel("Circular velocity [km/s]")
    ax.set_title("NGC6503 clean scale-tail preliminary replay")
    ax.grid(alpha=0.22)
    ax.legend(fontsize=8.3, frameon=True, loc="best")
    text = (
        f"weighted RMSE: candidate {summary['candidate_weighted_rmse_kms']:.2f} km/s\\n"
        f"baryonic {summary['baryonic_weighted_rmse_kms']:.2f}; "
        f"best wrong {summary['best_wrong_weighted_rmse_kms']:.2f}"
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
