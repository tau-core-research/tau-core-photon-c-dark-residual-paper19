from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

ACCEPTANCE = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance_v0_1.csv"
ACCEPTANCE_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance_summary_v0_1.json"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_normalization_audit_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_normalization_audit_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_normalization_audit_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)

REFERENCE_OUTER_STELLAR_MASS_MSUN = 1.4e8


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


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    if not ACCEPTANCE.exists() or not ACCEPTANCE_SUMMARY.exists():
        raise FileNotFoundError("Run mass profile digitization acceptance before normalization audit.")
    frame = pd.read_csv(ACCEPTANCE)
    summary_in = json.loads(ACCEPTANCE_SUMMARY.read_text(encoding="utf-8"))
    if summary_in.get("leakage_free") is not True:
        raise ValueError("Cannot audit normalization for a leaked response.")

    rows: list[dict[str, object]] = []
    for variant, sub in frame.groupby("profile_variant"):
        outer = sub[pd.to_numeric(sub["radius_kpc"], errors="coerce") >= 30.0].copy()
        outer_star_mass = _trapezoid_mass_msun(outer["radius_kpc"], outer["sigma_star_msun_pc2"])
        scale_to_reference = REFERENCE_OUTER_STELLAR_MASS_MSUN / outer_star_mass
        rows.append(
            {
                "galaxy": "NGC2841",
                "profile_variant": variant,
                "n_rows": int(len(sub)),
                "n_outer_rows_ge30": int(len(outer)),
                "naive_integrated_star_mass_ge30_msun": outer_star_mass,
                "reference_outer_stellar_mass_msun": REFERENCE_OUTER_STELLAR_MASS_MSUN,
                "naive_to_reference_ratio": outer_star_mass / REFERENCE_OUTER_STELLAR_MASS_MSUN,
                "scale_factor_required_to_match_reference": scale_to_reference,
                "normalization_status": (
                    "blocked_component_semantics_required"
                    if outer_star_mass / REFERENCE_OUTER_STELLAR_MASS_MSUN > 10.0
                    else "consistent_with_reference_within_order_of_magnitude"
                ),
                "allowed_use": (
                    "shape_candidate_only_no_load"
                    if outer_star_mass / REFERENCE_OUTER_STELLAR_MASS_MSUN > 10.0
                    else "candidate_load_after_separate_review"
                ),
                "interpretation": (
                    "Naive annular integration of the digitized figure profile over "
                    "R>=30 kpc does not reproduce the quoted outer-disk stellar mass. "
                    "The digitized curve may represent total profile, component mixture, "
                    "or figure-level display values rather than the isolated outer-disk "
                    "mass component."
                ),
            }
        )

    audit = pd.DataFrame(rows)
    audit["endpoint_replay_permission"] = "no"
    audit["kernel_promotion_permission"] = "no"
    audit["new_route_scoring_permission"] = "no"
    audit["uses_vobs_or_residual"] = "no"
    audit["forbidden_inputs"] = FORBIDDEN_INPUTS
    audit["endpoint_data_policy"] = ENDPOINT_POLICY
    audit["claim_boundary"] = CLAIM_BOUNDARY

    blocked = bool(audit["normalization_status"].str.startswith("blocked").any())
    summary = {
        "n_rows": int(len(audit)),
        "galaxies": sorted(audit["galaxy"].unique().tolist()),
        "profile_variants": sorted(audit["profile_variant"].unique().tolist()),
        "reference_outer_stellar_mass_msun": REFERENCE_OUTER_STELLAR_MASS_MSUN,
        "normalization_status_counts": audit["normalization_status"].value_counts().sort_index().to_dict(),
        "allowed_use_counts": audit["allowed_use"].value_counts().sort_index().to_dict(),
        "normalization_blocked": blocked,
        "formula_ready": False,
        "endpoint_replay_permission_counts": audit["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": audit["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": audit["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": audit["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The Dragonfly mass-profile digitization is leakage-free but not load-ready. "
            "Naive annular integration over the outer disk does not reproduce the quoted "
            "Zhang et al. outer-disk stellar mass, so the profile can only be retained "
            "as a shape candidate until component/normalization semantics are resolved."
        ),
        "next_allowed_action": (
            "Ask the reviewer or source audit to identify whether the figure curve should "
            "be treated as total profile, outer-component profile, or renormalized shape; "
            "do not run endpoint scoring from this profile yet."
        ),
    }
    return audit, summary


def main() -> None:
    audit, summary = build_audit()
    audit.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
