from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LIT_DIR = ROOT / "data" / "external" / "literature" / "ngc2841_load_source_search"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_search_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_search_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_outer_capacity_load_source_search_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)

G_KPC_KMS2_PER_MSUN = 4.30091e-6


def _v2_from_mass_at_radius(mass_msun: float, radius_kpc: float) -> float:
    return G_KPC_KMS2_PER_MSUN * mass_msun / radius_kpc


def build_load_source_search() -> tuple[pd.DataFrame, dict[str, object]]:
    zhang_source_tex = LIT_DIR / "zhang2018_src" / "Zhang_accepted_2col.tex"
    zhang_mass_profile_pdf = LIT_DIR / "zhang2018_src" / "prof_masses1and2_4.pdf"
    zhang_source_tar = LIT_DIR / "zhang2018_arxiv_source.tar"

    outer_stellar_mass_msun = 1.4e8
    outer_stellar_mass_err_msun = 0.2e8
    gas_mass_from_3_to_1_msun = outer_stellar_mass_msun / 3.0
    total_outer_baryonic_mass_msun = outer_stellar_mass_msun + gas_mass_from_3_to_1_msun
    v2_30 = _v2_from_mass_at_radius(total_outer_baryonic_mass_msun, 30.0)
    v2_50 = _v2_from_mass_at_radius(total_outer_baryonic_mass_msun, 50.0)
    v2_70 = _v2_from_mass_at_radius(total_outer_baryonic_mass_msun, 70.0)

    rows = [
        {
            "galaxy": "NGC2841",
            "candidate_load_source": "dragonfly_integrated_outer_baryonic_mass_ceiling",
            "source_status": "SOURCE_NATIVE_BARYONIC_LOAD_CEILING_DERIVED",
            "source_basis": (
                "Zhang et al. report M_star=1.4+/-0.2e8 Msun beyond the warp-dominated "
                "R>30 kpc outer disk; the outer stellar/gas surface-density ratio is "
                "about 3:1 beyond about 20 kpc."
            ),
            "source_reference": "Zhang2018NGC2841Dragonfly",
            "source_url": "https://arxiv.org/abs/1802.02583",
            "local_source_artifact": str(zhang_source_tex.relative_to(ROOT)),
            "load_quantity_type": "integrated_outer_baryonic_mass_to_velocity_squared_ceiling",
            "source_value": (
                f"M_star_outer_msun={outer_stellar_mass_msun:.3e};"
                f"M_gas_outer_from_3to1_msun={gas_mass_from_3_to_1_msun:.3e};"
                f"M_baryon_outer_msun={total_outer_baryonic_mass_msun:.3e}"
            ),
            "source_native_conversion": "v2_ceiling(R)=G*M_outer_baryon/R",
            "derived_load_values": (
                f"v2_ceiling_30kpc_km2s2={v2_30:.3f};"
                f"v2_ceiling_50kpc_km2s2={v2_50:.3f};"
                f"v2_ceiling_70kpc_km2s2={v2_70:.3f};"
                f"v_ceiling_30kpc_kms={math.sqrt(v2_30):.3f}"
            ),
            "load_use_status": "usable_as_baryonic_ceiling_control_not_dark_residual_load",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "notes": (
                "This gives a genuine source-native quantity with velocity-squared units, "
                "but only as a conservative baryonic ceiling/control. It does not supply "
                "a positive dark-residual lambda and should not be used to rescue the "
                "rotation curve."
            ),
        },
        {
            "galaxy": "NGC2841",
            "candidate_load_source": "dragonfly_mass_surface_density_profile_digitization",
            "source_status": "PROMISING_LOAD_ROUTE_REQUIRES_REVIEW_DIGITIZATION",
            "source_basis": (
                "The arXiv source package contains prof_masses1and2_4.pdf with stellar "
                "and gas mass-surface-density profiles and their ratio."
            ),
            "source_reference": "Zhang2018NGC2841Dragonfly",
            "source_url": "https://arxiv.org/e-print/1802.02583",
            "local_source_artifact": str(zhang_mass_profile_pdf.relative_to(ROOT)),
            "load_quantity_type": "radial_stellar_and_gas_surface_density_profile",
            "source_value": "figure_profile_available_not_machine_table",
            "source_native_conversion": (
                "digitize Sigma_star(R), Sigma_gas(R); convert to disk gravitational "
                "contribution or bounded load after independent reviewer acceptance"
            ),
            "derived_load_values": "pending_review_digitization",
            "load_use_status": "blocked_until_digitization_and_conversion_review",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "notes": (
                "This is the best next source-native route if a radial load profile is "
                "needed. The figure is not a table, so a reviewer package is required "
                "before formula freeze."
            ),
        },
        {
            "galaxy": "NGC2841",
            "candidate_load_source": "things_hi_map_gas_surface_density_route",
            "source_status": "FORMULA_EXISTS_MAP_PROFILE_NOT_CACHED_FOR_LOAD",
            "source_basis": (
                "Zhang et al. use the Leroy et al. gas-surface-density conversion from "
                "THINGS HI intensity, including helium, but this repo does not yet cache "
                "a source-native radial HI intensity or gas surface-density table."
            ),
            "source_reference": "Zhang2018NGC2841Dragonfly;Leroy2008THINGS",
            "source_url": "https://arxiv.org/abs/1802.02583",
            "local_source_artifact": str(zhang_source_tar.relative_to(ROOT)),
            "load_quantity_type": "HI_intensity_to_gas_surface_density",
            "source_value": "Sigma_gas=0.020*cos(i)*I_21cm",
            "source_native_conversion": "requires source-native I_21cm(R) or accepted digitized Sigma_gas(R)",
            "derived_load_values": "blocked_profile_missing",
            "load_use_status": "blocked_until_hi_profile_cached_or_digitized",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "notes": (
                "This route can become source-native, but the formula alone is not a "
                "load profile."
            ),
        },
        {
            "galaxy": "NGC2841",
            "candidate_load_source": "sparc_baryonic_mass_model_carrier",
            "source_status": "EXISTING_BARYONIC_CARRIER_NOT_NEW_OUTER_LOAD",
            "source_basis": (
                "The local SPARC preflight files contain baryonic velocity components "
                "used under fixed M/L as a carrier. These may be used for carrier checks, "
                "not for a new dark-residual load."
            ),
            "source_reference": "Lelli2016SPARC",
            "source_url": "https://astroweb.cwru.edu/SPARC/",
            "local_source_artifact": "data/external/sparc_preflight/MassModels_Lelli2016c.mrt",
            "load_quantity_type": "existing_baryonic_velocity_components",
            "source_value": "Vgas,Vdisk,Vbul under SPARC conventions",
            "source_native_conversion": "already velocity components but already part of carrier bookkeeping",
            "derived_load_values": "not_a_new_outer_capacity_load",
            "load_use_status": "carrier_crosscheck_only",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "notes": (
                "Using the existing carrier as the missing lambda would double-count "
                "the baryonic lane."
            ),
        },
    ]

    frame = pd.DataFrame(rows)
    frame["uses_vobs_or_residual"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "source_status_counts": frame["source_status"].value_counts().sort_index().to_dict(),
        "load_use_status_counts": frame["load_use_status"].value_counts().sort_index().to_dict(),
        "outer_stellar_mass_msun": outer_stellar_mass_msun,
        "outer_stellar_mass_err_msun": outer_stellar_mass_err_msun,
        "outer_gas_mass_from_3to1_msun": gas_mass_from_3_to_1_msun,
        "outer_baryonic_mass_from_3to1_msun": total_outer_baryonic_mass_msun,
        "v2_ceiling_30kpc_km2s2": v2_30,
        "v2_ceiling_50kpc_km2s2": v2_50,
        "v2_ceiling_70kpc_km2s2": v2_70,
        "v_ceiling_30kpc_kms": math.sqrt(v2_30),
        "promoted_load_source_ready": False,
        "best_next_source_route": "dragonfly_mass_surface_density_profile_digitization",
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The search found a source-native baryonic load ceiling from the Dragonfly "
            "outer-disk mass and a stronger future route through digitizing the published "
            "stellar/gas mass-surface-density profile. It did not find a ready positive "
            "dark-residual lambda. Endpoint replay remains closed."
        ),
        "next_allowed_action": (
            "Create a reviewer package for digitizing prof_masses1and2_4.pdf, or freeze "
            "the integrated outer baryonic mass ceiling as a non-endpoint control."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_load_source_search()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "candidate_load_source",
                "source_status",
                "load_use_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
