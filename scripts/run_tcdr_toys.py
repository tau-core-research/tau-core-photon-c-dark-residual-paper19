"""
Tau Core Dark Residual Protocol toy simulations.

This script runs three synthetic validations:

TCDR-v1: clean morphology residual recovery
TCDR-v2: noisy morphology residual recovery with nuisance/systematics
TCDR-v3: null/time split recovery

The purpose is methodological only. These toys do not prove Tau Core.
They test whether a pre-defined morphology/filament seed can be recovered
when present, and not falsely recovered when absent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
RESULT_DIR = ROOT / "data" / "derived"
FIG_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class RegressionResult:
    r2_base: float
    r2_tau: float
    delta_r2: float
    permutation_p: float
    score: int


def _linear_r2(x: np.ndarray, y: np.ndarray) -> Tuple[float, np.ndarray]:
    """Fit linear regression by least squares and return R² and coefficients."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x_design = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(x_design, y, rcond=None)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        y_hat = x_design @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 0.0 if ss_tot <= 0 else 1.0 - ss_res / ss_tot
    return float(r2), beta


def _score(delta_r2: float, p_value: float, strong_extra: bool = False) -> int:
    """Map toy result to a conservative TCDR-like score."""
    if p_value > 0.05 or delta_r2 <= 0.002:
        return 0
    if delta_r2 < 0.015:
        return 2
    if delta_r2 < 0.05:
        return 3
    if delta_r2 < 0.15:
        return 4
    return 5 if strong_extra else 4


def _permutation_test(
    y: np.ndarray,
    base_x: np.ndarray,
    tau_x: np.ndarray,
    rng: np.random.Generator,
    n_perm: int = 500,
) -> RegressionResult:
    """Compare base model to Tau-extended model using permutation of Tau columns."""
    r2_base, _ = _linear_r2(base_x, y)
    full_x = np.column_stack([base_x, tau_x])
    r2_tau, _ = _linear_r2(full_x, y)
    observed = r2_tau - r2_base

    perm_deltas = []
    for _ in range(n_perm):
        tau_perm = tau_x.copy()
        for col in range(tau_perm.shape[1]):
            tau_perm[:, col] = rng.permutation(tau_perm[:, col])
        perm_r2, _ = _linear_r2(np.column_stack([base_x, tau_perm]), y)
        perm_deltas.append(perm_r2 - r2_base)

    perm_deltas_arr = np.asarray(perm_deltas)
    p_value = (np.sum(perm_deltas_arr >= observed) + 1.0) / (n_perm + 1.0)
    return RegressionResult(
        r2_base=r2_base,
        r2_tau=r2_tau,
        delta_r2=float(observed),
        permutation_p=float(p_value),
        score=_score(float(observed), float(p_value), strong_extra=observed > 0.15),
    )


def _angle_alignment(theta_a: np.ndarray, theta_b: np.ndarray) -> np.ndarray:
    """Axis alignment statistic; 0 and π are treated as equivalent."""
    return np.cos(2.0 * (theta_a - theta_b))


def _make_base_galaxies(n: int, rng: np.random.Generator, noisy_angles: bool) -> pd.DataFrame:
    log_m = rng.normal(10.2, 0.45, n)
    break_feature = rng.normal(0.0, 1.0, n)
    halo_q = rng.normal(0.0, 1.0, n)
    theta_disk = rng.uniform(0.0, np.pi, n)
    theta_bar = (theta_disk + rng.normal(0.0, 0.55, n)) % np.pi
    theta_filament_true = rng.uniform(0.0, np.pi, n)

    if noisy_angles:
        theta_filament = (theta_filament_true + rng.normal(0.0, 0.18, n)) % np.pi
        theta_disk_obs = (theta_disk + rng.normal(0.0, 0.07, n)) % np.pi
        theta_bar_obs = (theta_bar + rng.normal(0.0, 0.12, n)) % np.pi
    else:
        theta_filament = theta_filament_true
        theta_disk_obs = theta_disk
        theta_bar_obs = theta_bar

    a_disk_fil = _angle_alignment(theta_disk_obs, theta_filament)
    a_bar_fil = _angle_alignment(theta_bar_obs, theta_filament)

    p_tau = 0.55 * a_disk_fil + 0.25 * a_bar_fil + 0.20 * break_feature

    return pd.DataFrame(
        {
            "logM": log_m,
            "break_feature": break_feature,
            "halo_q": halo_q,
            "theta_disk": theta_disk_obs,
            "theta_bar": theta_bar_obs,
            "theta_filament": theta_filament,
            "A_disk_fil": a_disk_fil,
            "A_bar_fil": a_bar_fil,
            "P_tau": p_tau,
        }
    )


def simulate_v1(tau_strength: float, rng: np.random.Generator, n: int = 450) -> RegressionResult:
    data = _make_base_galaxies(n=n, rng=rng, noisy_angles=False)
    standard = 0.18 * data["halo_q"].to_numpy() + 0.06 * (data["logM"].to_numpy() - 10.2)
    noise = rng.normal(0.0, 0.55, n)
    y = standard + tau_strength * data["P_tau"].to_numpy() + noise

    base_x = data[["halo_q", "logM"]].to_numpy()
    tau_x = data[["A_disk_fil", "A_bar_fil", "break_feature"]].to_numpy()
    return _permutation_test(y, base_x, tau_x, rng)


def simulate_v2(tau_strength: float, rng: np.random.Generator, n: int = 650) -> RegressionResult:
    data = _make_base_galaxies(n=n, rng=rng, noisy_angles=True)
    halo_nonlinear = data["halo_q"].to_numpy() ** 2 - 1.0
    baryon_error = rng.normal(0.0, 0.40, n)
    inclination_error = rng.normal(0.0, 0.35, n)
    survey_sys = 0.12 * np.sin(2.0 * data["theta_disk"].to_numpy()) + rng.normal(0.0, 0.18, n)

    standard = (
        0.22 * data["halo_q"].to_numpy()
        + 0.07 * halo_nonlinear
        + 0.05 * (data["logM"].to_numpy() - 10.2)
        + 0.18 * baryon_error
        + 0.14 * inclination_error
        + survey_sys
    )
    noise = rng.normal(0.0, 0.70, n)
    y = standard + tau_strength * data["P_tau"].to_numpy() + noise

    base_x = np.column_stack(
        [
            data["halo_q"].to_numpy(),
            data["logM"].to_numpy(),
            halo_nonlinear,
            baryon_error,
            inclination_error,
            survey_sys,
        ]
    )
    tau_x = data[["A_disk_fil", "A_bar_fil", "break_feature"]].to_numpy()
    return _permutation_test(y, base_x, tau_x, rng)


def simulate_v3(
    tau_strength: float,
    rng: np.random.Generator,
    n: int = 800,
    return_dataframe: bool = False,
) -> RegressionResult | Tuple[RegressionResult, pd.DataFrame]:
    data = _make_base_galaxies(n=n, rng=rng, noisy_angles=True)
    halo_nonlinear = data["halo_q"].to_numpy() ** 2 - 1.0
    survey_sys = 0.13 * np.sin(2.0 * data["theta_filament"].to_numpy()) + rng.normal(0.0, 0.15, n)
    common_standard = (
        0.20 * data["halo_q"].to_numpy()
        + 0.07 * halo_nonlinear
        + 0.05 * (data["logM"].to_numpy() - 10.2)
        + survey_sys
    )

    p_tau = data["P_tau"].to_numpy()
    time_noise = rng.normal(0.0, 0.72, n)
    null_noise = rng.normal(0.0, 0.72, n)

    # Tau split is intentionally differential: null channel receives stronger response.
    r_time = common_standard + 0.35 * tau_strength * p_tau + time_noise
    r_null = common_standard + 1.00 * tau_strength * p_tau + null_noise
    delta_tau = r_null - r_time

    base_x = np.column_stack(
        [
            data["halo_q"].to_numpy(),
            data["logM"].to_numpy(),
            halo_nonlinear,
            survey_sys,
        ]
    )
    tau_x = data[["A_disk_fil", "A_bar_fil", "break_feature"]].to_numpy()
    result = _permutation_test(delta_tau, base_x, tau_x, rng)

    if return_dataframe:
        out = data.copy()
        out["R_time"] = r_time
        out["R_null"] = r_null
        out["Delta_tau"] = delta_tau
        out["survey_sys"] = survey_sys
        return result, out
    return result


def run_all() -> pd.DataFrame:
    strengths_v1_v2 = [0.00, 0.15, 0.30, 0.60]
    strengths_v3 = [0.00, 0.10, 0.20, 0.35, 0.60]
    rows: List[Dict[str, float | str | int]] = []

    for module_name, strengths, fn in [
        ("TCDR-v1", strengths_v1_v2, simulate_v1),
        ("TCDR-v2", strengths_v1_v2, simulate_v2),
        ("TCDR-v3", strengths_v3, simulate_v3),
    ]:
        for idx, strength in enumerate(strengths):
            rng = np.random.default_rng(20260707 + idx + 1000 * len(rows))
            result = fn(strength, rng)
            assert isinstance(result, RegressionResult)
            rows.append(
                {
                    "module": module_name,
                    "tau_strength": strength,
                    "r2_base": result.r2_base,
                    "r2_tau": result.r2_tau,
                    "delta_r2": result.delta_r2,
                    "permutation_p": result.permutation_p,
                    "score": result.score,
                }
            )

    summary = pd.DataFrame(rows)
    summary.to_csv(RESULT_DIR / "tcdr_summary.csv", index=False)
    with open(RESULT_DIR / "tcdr_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary.to_dict(orient="records"), f, indent=2)
    return summary


def make_plots(summary: pd.DataFrame) -> None:
    modules = list(summary["module"].unique())

    plt.figure(figsize=(8, 5))
    for module in modules:
        subset = summary[summary["module"] == module]
        plt.plot(subset["tau_strength"], subset["delta_r2"], marker="o", label=module)
    plt.xlabel("Tau strength")
    plt.ylabel("ΔR² from Tau seed variables")
    plt.title("TCDR toy recovery: additional explained variance")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_delta_r2.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    for module in modules:
        subset = summary[summary["module"] == module]
        plt.plot(subset["tau_strength"], subset["permutation_p"], marker="o", label=module)
    plt.axhline(0.05, linestyle="--", linewidth=1)
    plt.xlabel("Tau strength")
    plt.ylabel("Permutation p-value")
    plt.title("TCDR toy recovery: permutation control")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_pvalues.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    for module in modules:
        subset = summary[summary["module"] == module]
        plt.plot(subset["tau_strength"], subset["score"], marker="o", label=module)
    plt.xlabel("Tau strength")
    plt.ylabel("Toy TCDR score")
    plt.title("TCDR toy score by injected morphology/readout strength")
    plt.yticks([0, 1, 2, 3, 4, 5])
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_score.png", dpi=160)
    plt.close()

    rng = np.random.default_rng(909090)
    result, data = simulate_v3(0.35, rng, return_dataframe=True)
    assert isinstance(result, RegressionResult)
    assert isinstance(data, pd.DataFrame)
    data.to_csv(RESULT_DIR / "tcdr_v3_example_data.csv", index=False)

    plt.figure(figsize=(7, 5))
    plt.scatter(data["P_tau"], data["Delta_tau"], s=10, alpha=0.55)
    plt.xlabel("Pre-defined Tau seed projection Pτ")
    plt.ylabel("Null/time split Δτ")
    plt.title("TCDR-v3 example: structured null/time split toy")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "tcdr_v3_split_scatter.png", dpi=160)
    plt.close()


def main() -> None:
    summary = run_all()
    make_plots(summary)
    print("TCDR toy simulations completed.")
    print(summary.to_string(index=False))
    print(f"\nResults written to: {RESULT_DIR}")
    print(f"Figures written to: {FIG_DIR}")


if __name__ == "__main__":
    main()
