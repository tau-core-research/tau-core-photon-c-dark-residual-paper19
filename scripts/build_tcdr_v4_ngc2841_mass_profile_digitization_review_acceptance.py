from __future__ import annotations

import csv
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
RESPONSE_DIR = ROOT / "data" / "reviewer_responses"

FILLED_ZIP = Path.home() / "Downloads" / "tcdr_v4_ngc2841_mass_profile_digitization_review_package_FILLED_v0_1.zip"
EXTRACT_DIR = RESPONSE_DIR / "tcdr_v4_ngc2841_mass_profile_digitization_review_package_FILLED_v0_1"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_digitization_review_acceptance_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _extract_response() -> Path:
    if not FILLED_ZIP.exists():
        raise FileNotFoundError(f"Missing filled reviewer package: {FILLED_ZIP}")
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(FILLED_ZIP) as archive:
        archive.extractall(EXTRACT_DIR)
    matches = list(EXTRACT_DIR.rglob("review_response_template.csv"))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one review_response_template.csv, found {len(matches)}")
    return matches[0]


def _as_bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().map({"true": True, "false": False})


def _trapezoid_mass_msun(radius_kpc: pd.Series, sigma_msun_pc2: pd.Series) -> float:
    valid = radius_kpc.notna() & sigma_msun_pc2.notna()
    radius = radius_kpc[valid].astype(float).to_numpy()
    sigma = sigma_msun_pc2[valid].astype(float).to_numpy()
    if len(radius) < 2:
        return float("nan")
    order = np.argsort(radius)
    radius = radius[order]
    sigma = sigma[order]
    integrand = 2.0 * np.pi * radius * sigma * 1.0e6
    return float(np.trapezoid(integrand, radius))


def _summarize_variant(frame: pd.DataFrame, variant: str) -> dict[str, object]:
    sub = frame[frame["profile_variant"].eq(variant)].copy().sort_values("radius_kpc")
    outer = sub[sub["radius_kpc"] >= 30.0].copy()
    star_mass = _trapezoid_mass_msun(sub["radius_kpc"], sub["sigma_star_msun_pc2"])
    gas_mass = _trapezoid_mass_msun(sub["radius_kpc"], sub["sigma_gas_msun_pc2"])
    outer_star_mass = _trapezoid_mass_msun(outer["radius_kpc"], outer["sigma_star_msun_pc2"])
    outer_gas_mass = _trapezoid_mass_msun(outer["radius_kpc"], outer["sigma_gas_msun_pc2"])
    with_gas = sub.dropna(subset=["sigma_gas_msun_pc2"])
    ratios_outer = with_gas[with_gas["radius_kpc"] >= 20.0]["sigma_star_to_gas_ratio"].dropna()
    return {
        "profile_variant": variant,
        "n_rows": int(len(sub)),
        "n_gas_rows": int(sub["sigma_gas_msun_pc2"].notna().sum()),
        "r_min_kpc": float(sub["radius_kpc"].min()) if not sub.empty else float("nan"),
        "r_max_kpc": float(sub["radius_kpc"].max()) if not sub.empty else float("nan"),
        "integrated_star_mass_msun": star_mass,
        "integrated_gas_mass_msun": gas_mass,
        "integrated_baryonic_mass_msun": float(star_mass + gas_mass)
        if np.isfinite(star_mass) and np.isfinite(gas_mass)
        else float("nan"),
        "integrated_star_mass_ge30_msun": outer_star_mass,
        "integrated_gas_mass_ge30_msun": outer_gas_mass,
        "integrated_baryonic_mass_ge30_msun": float(outer_star_mass + outer_gas_mass)
        if np.isfinite(outer_star_mass) and np.isfinite(outer_gas_mass)
        else float("nan"),
        "median_outer_star_to_gas_ratio_ge20": float(np.median(ratios_outer)) if len(ratios_outer) else float("nan"),
        "max_sigma_uncertainty_dex": float(sub["estimated_sigma_uncertainty_dex"].max()) if not sub.empty else float("nan"),
        "quality_flags": ";".join(sorted(sub["quality_flag"].astype(str).unique().tolist())),
    }


def build_acceptance() -> tuple[pd.DataFrame, dict[str, object]]:
    response_path = _extract_response()
    response = pd.read_csv(response_path)
    required_columns = {
        "galaxy",
        "radius_kpc",
        "sigma_star_msun_pc2",
        "sigma_gas_msun_pc2",
        "sigma_star_to_gas_ratio",
        "profile_variant",
        "quality_flag",
        "forbidden_inputs_acknowledged",
        "uses_rotation_curve_or_velocity",
        "uses_endpoint_rotation_residual",
        "uses_tau_core_score_or_required_lambda",
    }
    missing = required_columns.difference(response.columns)
    if missing:
        raise ValueError(f"Missing response columns: {sorted(missing)}")

    bool_checks = {
        "forbidden_inputs_acknowledged": _as_bool_series(response["forbidden_inputs_acknowledged"]),
        "uses_rotation_curve_or_velocity": _as_bool_series(response["uses_rotation_curve_or_velocity"]),
        "uses_endpoint_rotation_residual": _as_bool_series(response["uses_endpoint_rotation_residual"]),
        "uses_tau_core_score_or_required_lambda": _as_bool_series(
            response["uses_tau_core_score_or_required_lambda"]
        ),
    }
    leakage_free = (
        bool_checks["forbidden_inputs_acknowledged"].eq(True).all()
        and bool_checks["uses_rotation_curve_or_velocity"].eq(False).all()
        and bool_checks["uses_endpoint_rotation_residual"].eq(False).all()
        and bool_checks["uses_tau_core_score_or_required_lambda"].eq(False).all()
    )
    if not leakage_free:
        raise ValueError("Reviewer response failed leakage flags.")

    for column in [
        "radius_kpc",
        "sigma_star_msun_pc2",
        "sigma_gas_msun_pc2",
        "sigma_star_to_gas_ratio",
        "estimated_radius_uncertainty_kpc",
        "estimated_sigma_uncertainty_dex",
    ]:
        response[column] = pd.to_numeric(response[column], errors="coerce")

    response = response.sort_values(["profile_variant", "radius_kpc"]).reset_index(drop=True)
    response["accepted_source_side_profile_candidate"] = "yes_caveated"
    response["endpoint_replay_permission"] = "no"
    response["kernel_promotion_permission"] = "no"
    response["new_route_scoring_permission"] = "no"
    response["uses_vobs_or_residual"] = "no"
    response["forbidden_inputs"] = FORBIDDEN_INPUTS
    response["endpoint_data_policy"] = ENDPOINT_POLICY
    response["claim_boundary"] = CLAIM_BOUNDARY

    variant_summaries = [
        _summarize_variant(response, variant)
        for variant in sorted(response["profile_variant"].dropna().unique().tolist())
    ]
    variants_by_name = {row["profile_variant"]: row for row in variant_summaries}
    measured = variants_by_name.get("measured_color", {})
    constant = variants_by_name.get("constant_outer_color", {})

    reference_outer_stellar_mass_msun = 1.4e8
    measured_outer = variants_by_name.get("measured_color", {}).get("integrated_star_mass_ge30_msun")
    measured_outer_ratio_to_reference = (
        float(measured_outer) / reference_outer_stellar_mass_msun
        if measured_outer is not None and np.isfinite(measured_outer)
        else float("nan")
    )
    scale_consistency_status = (
        "blocked_profile_normalization_semantics_mismatch"
        if np.isfinite(measured_outer_ratio_to_reference) and measured_outer_ratio_to_reference > 10.0
        else "scale_consistency_not_blocking"
    )

    summary = {
        "n_rows": int(len(response)),
        "galaxies": sorted(response["galaxy"].astype(str).unique().tolist()),
        "profile_variants": sorted(response["profile_variant"].astype(str).unique().tolist()),
        "leakage_free": True,
        "quality_flags": sorted(response["quality_flag"].astype(str).unique().tolist()),
        "accepted_source_side_profile_candidate": (
            "yes_caveated_profile_received_but_load_conversion_blocked"
        ),
        "formula_ready": False,
        "reference_outer_stellar_mass_msun": reference_outer_stellar_mass_msun,
        "measured_color_integrated_star_mass_ge30_ratio_to_reference": (
            measured_outer_ratio_to_reference
        ),
        "scale_consistency_status": scale_consistency_status,
        "endpoint_replay_permission_counts": response["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": response["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": response["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": response["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "variant_summaries": variant_summaries,
        "measured_color_integrated_star_mass_msun": measured.get("integrated_star_mass_msun"),
        "measured_color_integrated_gas_mass_msun": measured.get("integrated_gas_mass_msun"),
        "measured_color_integrated_baryonic_mass_msun": measured.get("integrated_baryonic_mass_msun"),
        "measured_color_median_outer_star_to_gas_ratio_ge20": measured.get(
            "median_outer_star_to_gas_ratio_ge20"
        ),
        "constant_outer_color_integrated_star_mass_msun": constant.get("integrated_star_mass_msun"),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The filled NGC2841 Dragonfly mass-profile review response passes leakage "
            "flags and is accepted only as a caveated source-side profile response. It "
            "is not formula-ready: a naive annular integration of the digitized profile "
            "is not directly compatible with the quoted Zhang et al. outer-disk stellar "
            "mass, so profile normalization/component semantics must be resolved before "
            "any disk-load conversion or endpoint replay."
        ),
        "next_allowed_action": (
            "Build a source-side profile-normalization audit comparing the digitized "
            "curve, the two-disk component model, and the quoted outer-disk mass before "
            "any load formula is frozen."
        ),
    }
    return response, summary


def main() -> None:
    response, summary = build_acceptance()
    response.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
