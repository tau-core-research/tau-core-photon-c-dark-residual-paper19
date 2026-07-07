from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from run_tcdr_toys import _angle_alignment, _make_base_galaxies, _permutation_test


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
RESULT_DIR = ROOT / "data" / "derived"
FIG_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

P_THRESHOLD = 0.05
DELTA_THRESHOLD = 0.020
WRONG_MARGIN_THRESHOLD = 0.010


def _challenge_strengths() -> list[float]:
    # Hidden to the scoring stage. Includes null, borderline weak, medium, and
    # strong cases. The weak cases are intentionally allowed to fail the
    # conservative classifier; this keeps the challenge from being a trivial
    # "large injected signal" recovery exercise.
    return [
        0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        0.08, 0.08, 0.12, 0.12, 0.18, 0.18,
        0.24, 0.24, 0.32, 0.32, 0.40, 0.40,
        0.50, 0.50, 0.62, 0.62, 0.74, 0.74,
    ]


def _make_realistic_mock(challenge_id: int, tau_strength: float) -> dict[str, float | int]:
    rng = np.random.default_rng(730000 + challenge_id * 131)
    n = int(rng.integers(520, 900))
    data = _make_base_galaxies(n=n, rng=rng, noisy_angles=True)

    halo_nonlinear = data["halo_q"].to_numpy() ** 2 - 1.0
    baryon_error = rng.normal(0.0, 0.42, n)
    inclination_error = rng.normal(0.0, 0.36, n)
    shear_cal_like = rng.normal(0.0, 0.28, n)
    footprint_x = rng.normal(0.0, 1.0, n)
    footprint_y = rng.normal(0.0, 1.0, n)
    filament_distance = np.abs(rng.normal(0.0, 1.0, n))
    node_distance = np.abs(rng.normal(0.0, 1.0, n))
    local_density = rng.normal(0.0, 1.0, n)

    boundary_seed = np.exp(-0.5 * filament_distance) - np.exp(-0.8 * node_distance)
    p_tau = (
        0.48 * data["A_disk_fil"].to_numpy()
        + 0.22 * data["A_bar_fil"].to_numpy()
        + 0.18 * data["break_feature"].to_numpy()
        + 0.12 * boundary_seed
    )

    # Wrong seed: plausible morphology/environment columns, but with incorrect
    # source-side alignment. This is a wrong-family control, not a shuffled
    # endpoint residual.
    wrong_theta = rng.uniform(0.0, np.pi, n)
    wrong_disk = _angle_alignment(data["theta_disk"].to_numpy(), wrong_theta)
    wrong_bar = _angle_alignment(data["theta_bar"].to_numpy(), wrong_theta)
    wrong_boundary = rng.permutation(boundary_seed)

    survey_sys = (
        0.11 * np.sin(2.0 * data["theta_disk"].to_numpy())
        + 0.07 * footprint_x
        - 0.05 * footprint_y
        + rng.normal(0.0, 0.15, n)
    )
    standard = (
        0.20 * data["halo_q"].to_numpy()
        + 0.08 * halo_nonlinear
        + 0.06 * (data["logM"].to_numpy() - 10.2)
        + 0.16 * baryon_error
        + 0.13 * inclination_error
        + 0.10 * shear_cal_like
        + 0.09 * local_density
        + 0.06 * boundary_seed
        + survey_sys
    )
    noise = rng.normal(0.0, 0.72, n)
    y = standard + tau_strength * p_tau + noise

    base_x = np.column_stack(
        [
            data["halo_q"].to_numpy(),
            data["logM"].to_numpy(),
            halo_nonlinear,
            baryon_error,
            inclination_error,
            shear_cal_like,
            footprint_x,
            footprint_y,
            local_density,
            filament_distance,
            node_distance,
            survey_sys,
        ]
    )
    tau_x = np.column_stack(
        [
            data["A_disk_fil"].to_numpy(),
            data["A_bar_fil"].to_numpy(),
            data["break_feature"].to_numpy(),
            boundary_seed,
        ]
    )
    wrong_x = np.column_stack(
        [
            wrong_disk,
            wrong_bar,
            rng.permutation(data["break_feature"].to_numpy()),
            wrong_boundary,
        ]
    )

    result = _permutation_test(y, base_x, tau_x, rng, n_perm=300)
    wrong_result = _permutation_test(y, base_x, wrong_x, rng, n_perm=300)
    wrong_margin = result.delta_r2 - wrong_result.delta_r2
    predicted_injected = int(
        (result.permutation_p <= P_THRESHOLD)
        and (result.delta_r2 >= DELTA_THRESHOLD)
        and (wrong_margin >= WRONG_MARGIN_THRESHOLD)
    )
    true_injected = int(tau_strength > 0.0)

    return {
        "challenge_id": challenge_id,
        "n": n,
        "hidden_tau_strength": tau_strength,
        "true_injected": true_injected,
        "r2_base": result.r2_base,
        "r2_tau": result.r2_tau,
        "delta_r2": result.delta_r2,
        "permutation_p": result.permutation_p,
        "wrong_delta_r2": wrong_result.delta_r2,
        "wrong_permutation_p": wrong_result.permutation_p,
        "wrong_margin_delta_r2": wrong_margin,
        "predicted_injected": predicted_injected,
        "correct": int(predicted_injected == true_injected),
    }


def run_blind_challenge() -> tuple[pd.DataFrame, pd.DataFrame]:
    strengths = _challenge_strengths()
    rows = [_make_realistic_mock(idx, strength) for idx, strength in enumerate(strengths)]
    detail = pd.DataFrame(rows)
    detail.to_csv(RESULT_DIR / "tcdr_blind_challenge_results.csv", index=False)

    tp = int(((detail["true_injected"] == 1) & (detail["predicted_injected"] == 1)).sum())
    fp = int(((detail["true_injected"] == 0) & (detail["predicted_injected"] == 1)).sum())
    tn = int(((detail["true_injected"] == 0) & (detail["predicted_injected"] == 0)).sum())
    fn = int(((detail["true_injected"] == 1) & (detail["predicted_injected"] == 0)).sum())
    n_pos = int((detail["true_injected"] == 1).sum())
    n_null = int((detail["true_injected"] == 0).sum())
    summary = pd.DataFrame(
        [
            {
                "n_challenges": len(detail),
                "n_injected": n_pos,
                "n_null": n_null,
                "true_positive": tp,
                "false_positive": fp,
                "true_negative": tn,
                "false_negative": fn,
                "accuracy": (tp + tn) / len(detail),
                "true_positive_rate": tp / n_pos if n_pos else np.nan,
                "false_positive_rate": fp / n_null if n_null else np.nan,
                "median_correct_delta_r2": detail["delta_r2"].median(),
                "median_wrong_delta_r2": detail["wrong_delta_r2"].median(),
                "median_wrong_margin_delta_r2": detail["wrong_margin_delta_r2"].median(),
            }
        ]
    )
    summary.to_csv(RESULT_DIR / "tcdr_blind_challenge_summary.csv", index=False)
    return detail, summary


def make_plots(detail: pd.DataFrame, summary: pd.DataFrame) -> None:
    colors = np.where(detail["true_injected"] == 1, "#3b6fb6", "#b6533b")

    plt.figure(figsize=(8, 5))
    plt.scatter(detail["wrong_delta_r2"], detail["delta_r2"], c=colors, s=45, alpha=0.85)
    lim = max(float(detail[["wrong_delta_r2", "delta_r2"]].to_numpy().max()), 0.08)
    plt.plot([0, lim], [0, lim], linestyle="--", color="black", linewidth=1)
    plt.xlabel("Wrong-seed ΔR²")
    plt.ylabel("Correct-seed ΔR²")
    plt.title("Blind challenge: correct seed versus wrong-seed control")
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", label="Injected", markerfacecolor="#3b6fb6", markersize=8),
        Line2D([0], [0], marker="o", color="w", label="Null", markerfacecolor="#b6533b", markersize=8),
    ]
    plt.legend(handles=legend_handles, loc="upper right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_blind_correct_vs_wrong.png", dpi=170)
    plt.close()

    s = summary.iloc[0]
    matrix = np.array([[s["true_negative"], s["false_positive"]], [s["false_negative"], s["true_positive"]]], dtype=float)
    plt.figure(figsize=(5.6, 4.8))
    plt.imshow(matrix, cmap="Blues")
    plt.xticks([0, 1], ["Pred null", "Pred injected"])
    plt.yticks([0, 1], ["True null", "True injected"])
    for i in range(2):
        for j in range(2):
            plt.text(j, i, f"{int(matrix[i, j])}", ha="center", va="center", fontsize=14)
    plt.title("Blind injection challenge confusion matrix")
    plt.colorbar(label="count")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_blind_confusion.png", dpi=170)
    plt.close()


def main() -> None:
    detail, summary = run_blind_challenge()
    make_plots(detail, summary)
    print("TCDR blind injection challenge completed.")
    print(summary.to_string(index=False))
    print(f"\nResults written to: {RESULT_DIR}")
    print(f"Figures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
