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
CONTROL_MARGIN_THRESHOLD = 0.008


def _realistic_challenge_strengths() -> list[float]:
    return [
        0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        0.06, 0.06, 0.08, 0.08, 0.10, 0.10,
        0.14, 0.14, 0.18, 0.18, 0.22, 0.22,
        0.28, 0.28, 0.34, 0.34, 0.42, 0.42,
        0.52, 0.52, 0.64, 0.64,
    ]


def _standardize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    scale = x.std()
    if scale <= 0:
        return x - x.mean()
    return (x - x.mean()) / scale


def _select_observed_rows(rng: np.random.Generator, score: np.ndarray, target_n: int) -> np.ndarray:
    score = _standardize(score)
    prob = 1.0 / (1.0 + np.exp(-score))
    prob = 0.16 + 0.68 * prob
    selected = rng.random(len(score)) < prob
    idx = np.flatnonzero(selected)
    if len(idx) < target_n:
        idx = np.argsort(score)[-target_n:]
    else:
        idx = rng.choice(idx, size=target_n, replace=False)
    return np.sort(idx)


def _evaluate_one(challenge_id: int, tau_strength: float) -> dict[str, float | int]:
    rng = np.random.default_rng(910000 + 193 * challenge_id)
    n_pool = int(rng.integers(1450, 1800))
    target_n = int(rng.integers(620, 760))
    data = _make_base_galaxies(n=n_pool, rng=rng, noisy_angles=True)

    sky_ra = rng.uniform(0.0, 2.0 * np.pi, n_pool)
    sky_dec = rng.normal(0.0, 0.72, n_pool)
    survey_mask = (
        0.46 * np.sin(2.0 * sky_ra)
        + 0.28 * np.cos(3.0 * sky_ra + 0.6 * sky_dec)
        + 0.22 * np.sin(1.7 * sky_dec)
    )
    foreground = (
        0.50 * np.cos(sky_ra - 0.35)
        + 0.30 * np.sin(2.3 * sky_dec)
        + rng.normal(0.0, 0.18, n_pool)
    )
    selection_latent = (
        0.70 * survey_mask
        + 0.35 * foreground
        + 0.18 * data["halo_q"].to_numpy()
        - 0.10 * np.abs(data["break_feature"].to_numpy())
        + rng.normal(0.0, 0.55, n_pool)
    )
    idx = _select_observed_rows(rng, selection_latent, target_n=target_n)
    data = data.iloc[idx].reset_index(drop=True)
    sky_ra = sky_ra[idx]
    sky_dec = sky_dec[idx]
    survey_mask = survey_mask[idx]
    foreground = foreground[idx]
    selection_latent = selection_latent[idx]
    n = len(data)

    filament_distance = np.abs(rng.normal(0.0, 1.0, n) - 0.18 * _standardize(survey_mask))
    node_distance = np.abs(rng.normal(0.0, 1.0, n) + 0.14 * _standardize(foreground))
    local_density = (
        rng.normal(0.0, 1.0, n)
        + 0.26 * _standardize(foreground)
        - 0.18 * _standardize(filament_distance)
    )
    boundary_seed = np.exp(-0.55 * filament_distance) - np.exp(-0.85 * node_distance)
    halo_nonlinear = data["halo_q"].to_numpy() ** 2 - 1.0
    baryon_error = rng.normal(0.0, 0.42, n) + 0.10 * _standardize(selection_latent)
    inclination_error = rng.normal(0.0, 0.37, n) + 0.12 * np.sin(2.0 * data["theta_disk"].to_numpy())
    shear_cal_like = rng.normal(0.0, 0.26, n) + 0.10 * _standardize(foreground)

    correct_seed = (
        0.43 * data["A_disk_fil"].to_numpy()
        + 0.22 * data["A_bar_fil"].to_numpy()
        + 0.17 * data["break_feature"].to_numpy()
        + 0.18 * boundary_seed
    )
    line_of_sight = (sky_ra + 0.35 * np.sin(sky_dec)) % np.pi
    orient_disk = _angle_alignment(data["theta_disk"].to_numpy(), line_of_sight)
    orient_bar = _angle_alignment(data["theta_bar"].to_numpy(), line_of_sight)
    orientation_seed = 0.62 * orient_disk + 0.38 * orient_bar
    wrong_theta = (line_of_sight + rng.normal(0.75, 0.35, n)) % np.pi
    wrong_seed = (
        0.50 * _angle_alignment(data["theta_disk"].to_numpy(), wrong_theta)
        + 0.22 * _angle_alignment(data["theta_bar"].to_numpy(), wrong_theta)
        + 0.16 * rng.permutation(data["break_feature"].to_numpy())
        + 0.12 * rng.permutation(boundary_seed)
    )
    random_seed = rng.normal(0.0, 1.0, n)

    common_systematics = (
        0.23 * _standardize(survey_mask)
        + 0.20 * _standardize(foreground)
        + 0.13 * _standardize(selection_latent)
        + 0.11 * orientation_seed
        + rng.normal(0.0, 0.17, n)
    )
    standard = (
        0.20 * data["halo_q"].to_numpy()
        + 0.08 * halo_nonlinear
        + 0.07 * (data["logM"].to_numpy() - 10.2)
        + 0.14 * baryon_error
        + 0.12 * inclination_error
        + 0.10 * shear_cal_like
        + 0.07 * local_density
        + common_systematics
    )
    y = standard + tau_strength * correct_seed + rng.normal(0.0, 0.76, n)

    base_x = np.column_stack(
        [
            data["halo_q"].to_numpy(),
            data["logM"].to_numpy(),
            halo_nonlinear,
            baryon_error,
            inclination_error,
            shear_cal_like,
            local_density,
            survey_mask,
            foreground,
            selection_latent,
            sky_ra,
            sky_dec,
        ]
    )
    correct_x = np.column_stack(
        [
            data["A_disk_fil"].to_numpy(),
            data["A_bar_fil"].to_numpy(),
            data["break_feature"].to_numpy(),
            boundary_seed,
        ]
    )
    wrong_x = np.column_stack(
        [
            _standardize(wrong_seed),
            rng.permutation(data["A_bar_fil"].to_numpy()),
            rng.permutation(data["break_feature"].to_numpy()),
            rng.permutation(boundary_seed),
        ]
    )
    orientation_x = np.column_stack([orient_disk, orient_bar, orientation_seed])
    random_x = np.column_stack([random_seed, rng.permutation(random_seed), rng.normal(0.0, 1.0, n)])

    correct_result = _permutation_test(y, base_x, correct_x, rng, n_perm=220)
    wrong_result = _permutation_test(y, base_x, wrong_x, rng, n_perm=220)
    orient_result = _permutation_test(y, base_x, orientation_x, rng, n_perm=220)
    random_result = _permutation_test(y, base_x, random_x, rng, n_perm=220)

    max_control = max(wrong_result.delta_r2, orient_result.delta_r2, random_result.delta_r2)
    control_margin = correct_result.delta_r2 - max_control
    predicted = int(
        correct_result.permutation_p <= P_THRESHOLD
        and correct_result.delta_r2 >= DELTA_THRESHOLD
        and control_margin >= CONTROL_MARGIN_THRESHOLD
    )
    injected = int(tau_strength > 0.0)

    return {
        "challenge_id": challenge_id,
        "n": n,
        "hidden_tau_strength": tau_strength,
        "true_injected": injected,
        "correct_delta_r2": correct_result.delta_r2,
        "correct_p": correct_result.permutation_p,
        "wrong_delta_r2": wrong_result.delta_r2,
        "wrong_p": wrong_result.permutation_p,
        "orientation_delta_r2": orient_result.delta_r2,
        "orientation_p": orient_result.permutation_p,
        "random_delta_r2": random_result.delta_r2,
        "random_p": random_result.permutation_p,
        "max_control_delta_r2": max_control,
        "control_margin_delta_r2": control_margin,
        "predicted_injected": predicted,
        "correct": int(predicted == injected),
    }


def _confusion(detail: pd.DataFrame) -> dict[str, float | int]:
    tp = int(((detail["true_injected"] == 1) & (detail["predicted_injected"] == 1)).sum())
    fp = int(((detail["true_injected"] == 0) & (detail["predicted_injected"] == 1)).sum())
    tn = int(((detail["true_injected"] == 0) & (detail["predicted_injected"] == 0)).sum())
    fn = int(((detail["true_injected"] == 1) & (detail["predicted_injected"] == 0)).sum())
    n_pos = int((detail["true_injected"] == 1).sum())
    n_null = int((detail["true_injected"] == 0).sum())
    return {
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
        "median_correct_delta_r2": float(detail["correct_delta_r2"].median()),
        "median_max_control_delta_r2": float(detail["max_control_delta_r2"].median()),
        "median_control_margin_delta_r2": float(detail["control_margin_delta_r2"].median()),
    }


def _threshold_curve(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    p_cuts = [0.01, 0.03, 0.05, 0.08, 0.10]
    delta_cuts = np.round(np.arange(0.005, 0.051, 0.005), 3)
    margin_cuts = np.round(np.arange(-0.005, 0.026, 0.005), 3)
    for p_cut in p_cuts:
        for delta_cut in delta_cuts:
            for margin_cut in margin_cuts:
                pred = (
                    (detail["correct_p"] <= p_cut)
                    & (detail["correct_delta_r2"] >= delta_cut)
                    & (detail["control_margin_delta_r2"] >= margin_cut)
                ).astype(int)
                injected = detail["true_injected"].astype(int)
                tp = int(((injected == 1) & (pred == 1)).sum())
                fp = int(((injected == 0) & (pred == 1)).sum())
                tn = int(((injected == 0) & (pred == 0)).sum())
                fn = int(((injected == 1) & (pred == 0)).sum())
                tpr = tp / max(1, int((injected == 1).sum()))
                fpr = fp / max(1, int((injected == 0).sum()))
                precision = tp / max(1, tp + fp)
                rows.append(
                    {
                        "p_cut": p_cut,
                        "delta_cut": delta_cut,
                        "margin_cut": margin_cut,
                        "true_positive_rate": tpr,
                        "false_positive_rate": fpr,
                        "precision": precision,
                        "true_positive": tp,
                        "false_positive": fp,
                        "true_negative": tn,
                        "false_negative": fn,
                    }
                )
    return pd.DataFrame(rows)


def run_realistic_challenge() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    strengths = _realistic_challenge_strengths()
    detail = pd.DataFrame([_evaluate_one(i, strength) for i, strength in enumerate(strengths)])
    detail.to_csv(RESULT_DIR / "tcdr_realistic_mock_challenge_results.csv", index=False)
    summary = pd.DataFrame([_confusion(detail)])
    summary.to_csv(RESULT_DIR / "tcdr_realistic_mock_challenge_summary.csv", index=False)
    thresholds = _threshold_curve(detail)
    thresholds.to_csv(RESULT_DIR / "tcdr_realistic_mock_threshold_curve.csv", index=False)
    return detail, summary, thresholds


def make_plots(detail: pd.DataFrame, summary: pd.DataFrame, thresholds: pd.DataFrame) -> None:
    colors = np.where(detail["true_injected"] == 1, "#2f6f9f", "#a84d3a")
    markers = np.where(detail["predicted_injected"] == 1, "o", "s")

    plt.figure(figsize=(8.4, 5.2))
    for marker in ["o", "s"]:
        mask = markers == marker
        plt.scatter(
            detail.loc[mask, "max_control_delta_r2"],
            detail.loc[mask, "correct_delta_r2"],
            c=colors[mask],
            marker=marker,
            s=54,
            alpha=0.86,
            edgecolor="white",
            linewidth=0.5,
        )
    lim = max(float(detail[["max_control_delta_r2", "correct_delta_r2"]].to_numpy().max()), 0.08)
    plt.plot([0, lim], [0, lim], linestyle="--", color="black", linewidth=1)
    plt.xlabel("Best control ΔR²")
    plt.ylabel("Correct source-seed ΔR²")
    plt.title("Realistic mock challenge: candidate versus strongest control")
    legend_handles = [
        Line2D([0], [0], marker="o", color="w", label="Injected", markerfacecolor="#2f6f9f", markersize=8),
        Line2D([0], [0], marker="o", color="w", label="Null", markerfacecolor="#a84d3a", markersize=8),
        Line2D([0], [0], marker="o", color="black", label="Predicted injected", markerfacecolor="white", markersize=8),
        Line2D([0], [0], marker="s", color="black", label="Predicted null", markerfacecolor="white", markersize=8),
    ]
    plt.legend(handles=legend_handles, loc="upper left", frameon=True)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_realistic_candidate_vs_controls.png", dpi=180)
    plt.close()

    s = summary.iloc[0]
    matrix = np.array([[s["true_negative"], s["false_positive"]], [s["false_negative"], s["true_positive"]]], dtype=float)
    plt.figure(figsize=(5.8, 4.9))
    plt.imshow(matrix, cmap="Greens")
    plt.xticks([0, 1], ["Pred null", "Pred injected"])
    plt.yticks([0, 1], ["True null", "True injected"])
    for i in range(2):
        for j in range(2):
            plt.text(j, i, f"{int(matrix[i, j])}", ha="center", va="center", fontsize=14)
    plt.title("Realistic mock challenge confusion matrix")
    plt.colorbar(label="count")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_realistic_confusion.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7.4, 5.1))
    for p_cut, group in thresholds.groupby("p_cut"):
        best_by_fpr = group.sort_values(["false_positive_rate", "true_positive_rate"]).groupby(
            "false_positive_rate", as_index=False
        )["true_positive_rate"].max()
        plt.plot(
            best_by_fpr["false_positive_rate"],
            best_by_fpr["true_positive_rate"],
            marker="o",
            linewidth=1.4,
            label=f"p≤{p_cut:g}",
        )
    plt.xlabel("False-positive rate")
    plt.ylabel("True-positive rate")
    plt.title("Threshold-free stress view")
    plt.xlim(-0.01, 1.01)
    plt.ylim(-0.01, 1.01)
    plt.grid(alpha=0.25)
    plt.legend(loc="lower right", title="permutation cut")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_realistic_threshold_curve.png", dpi=180)
    plt.close()


def main() -> None:
    detail, summary, thresholds = run_realistic_challenge()
    make_plots(detail, summary, thresholds)
    print("TCDR realistic mock challenge completed.")
    print(summary.to_string(index=False))
    print(f"\nResults written to: {RESULT_DIR}")
    print(f"Figures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
