from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

HI_PROXY_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json"
GLOBAL_HI_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_summary_v0_1.json"
)
MOM0_PROFILE_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_summary_v0_1.json"
)
MOM0_MASS_AUDIT_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_summary_v0_1.json"
)
MOM0_DISK_LOAD_REVIEW_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_halo_capacity_conversion_search_freeze_not_endpoint"
ENDPOINT_POLICY = (
    "source_side_conversion_search_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_fits"
)
FORBIDDEN_INPUTS = (
    "Vobs;errV;rotation_residual;RMSE;baseline_score;endpoint_rank;"
    "NFW_best_fit;ISO_best_fit;MOND_fit;RAR_fit;required_lambda_fit"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_conversion_search() -> tuple[pd.DataFrame, dict[str, object]]:
    hi_proxy = _load_json(HI_PROXY_SUMMARY)
    global_hi = _load_json(GLOBAL_HI_SUMMARY) if GLOBAL_HI_SUMMARY.exists() else None
    mom0_profile = _load_json(MOM0_PROFILE_SUMMARY) if MOM0_PROFILE_SUMMARY.exists() else None
    mom0_products = {
        item["product"]: item for item in mom0_profile["product_summaries"]
    } if mom0_profile else {}
    mom0_mass_audit = (
        _load_json(MOM0_MASS_AUDIT_SUMMARY) if MOM0_MASS_AUDIT_SUMMARY.exists() else None
    )
    mom0_mass_products = {
        item["product"]: item for item in mom0_mass_audit["product_summaries"]
    } if mom0_mass_audit else {}
    mom0_disk_review = (
        _load_json(MOM0_DISK_LOAD_REVIEW_SUMMARY)
        if MOM0_DISK_LOAD_REVIEW_SUMMARY.exists()
        else None
    )
    mom0_disk_products = {
        item["product"]: item for item in mom0_disk_review["product_summaries"]
    } if mom0_disk_review else {}
    rows = [
        {
            "galaxy": "NGC2841",
            "conversion_route": "sparc_things_vgas_lower_bound",
            "route_kind": "source_derived_gas_proxy",
            "source_basis": (
                "SPARC rotmod gas contribution Vgas(R), with observed velocities ignored"
            ),
            "source_reference": "SPARCWebsite;deBlok2008THINGS",
            "source_url": "https://astroweb.case.edu/SPARC/",
            "local_artifact": "data/source_manifests/tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json",
            "conversion_status": "FROZEN_LOWER_BOUND_GAS_PROXY",
            "velocity_squared_status": "ready_as_gas_proxy_only",
            "positive_load_status": "insufficient_for_outer_capacity",
            "allowed_use": "lower_bound_hi_gas_shape_component",
            "blocked_use": "positive_dark_residual_endpoint_kernel",
            "next_action": "combine_only_with_independent_halo_or_extended_hi_conversion",
            "numeric_context": (
                "outer_median_fraction_of_required_gap="
                f"{hi_proxy['outer_median_gas_proxy_fraction_of_required_gap']:.6f};"
                "outer_max_fraction_of_required_gap="
                f"{hi_proxy['outer_max_gas_proxy_fraction_of_required_gap']:.6f}"
            ),
        },
        {
            "galaxy": "NGC2841",
            "conversion_route": "things_moment0_radial_hi_surface_density",
            "route_kind": "source_native_hi_map_profile",
            "source_basis": (
                "NED-hosted THINGS HI moment-0/intensity maps yield a residual-blind "
                "deprojected radial MOM0 shape/support profile with frozen THINGS geometry; "
                "beam/unit conversion also yields a source-side HI mass-profile proxy, "
                "and a lambda=1 physical-HI disk-load control can be derived; extra "
                "positive residual capacity still requires an independent multiplier; "
                "standard HI+helium gas bookkeeping is tracked only as a physical-gas control"
            ),
            "source_reference": "Walter2008THINGS;deBlok2008THINGS;Leroy2008THINGS",
            "source_url": (
                "https://ned.ipac.caltech.edu/img/2008AJ....136.2563W/"
                "NGC_2841_NA_MOM0:I:HI:wbb2008.fits.gz"
            ),
            "local_artifact": (
                "data/source_manifests/"
                "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_summary_v0_1.json"
            )
            if mom0_disk_review
            else (
                "data/source_manifests/"
                "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_summary_v0_1.json"
            )
            if mom0_mass_audit
            else (
                "data/source_manifests/"
                "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_summary_v0_1.json"
            )
            if mom0_profile
            else "not_cached",
            "conversion_status": (
                "FROZEN_PHYSICAL_HI_DISK_LOAD_CONTROL_POSITIVE_RESIDUAL_MULTIPLIER_MISSING"
                if mom0_disk_review
                else "FROZEN_MOM0_MASS_PROFILE_DISK_LOAD_REVIEW_MISSING"
                if mom0_mass_audit
                else "FROZEN_MOM0_RADIAL_SHAPE_LOAD_CONVERSION_MISSING"
                if mom0_profile
                else "SOURCE_NATIVE_ROUTE_OPEN_PROFILE_NOT_CACHED"
            ),
            "velocity_squared_status": (
                "physical_hi_disk_load_control_ready_lambda_one_only"
                if mom0_disk_review
                else "mass_profile_proxy_ready_disk_gravity_load_review_missing"
                if mom0_mass_audit
                else "radial_shape_ready_absolute_load_conversion_missing"
                if mom0_profile
                else "requires_map_to_radial_profile_and_disk_gravity_conversion"
            ),
            "positive_load_status": (
                "physical_hi_control_ready_positive_dark_residual_not_ready"
                if mom0_disk_review
                else "not_ready"
            ),
            "allowed_use": (
                "source_native_mom0_radial_shape_support"
                if mom0_profile
                else "next_primary_source_acquisition_target"
            ),
            "blocked_use": (
                "positive_dark_residual_or_halo_capacity_kernel_without_independent_multiplier"
                if mom0_disk_review
                else "endpoint_replay_without_disk_gravity_and_no_residual_amplitude_review"
                if mom0_mass_audit
                else "absolute_velocity_squared_load_without_beam_unit_mass_conversion_audit"
                if mom0_profile
                else "scoring_without_cached_map_profile_and_conversion_review"
            ),
            "next_action": (
                "find independent source-native multiplier or Tau-side load theorem before positive residual promotion"
                if mom0_disk_review
                else "review disk-gravity geometry and no-residual amplitude rule for MOM0-derived load promotion"
                if mom0_mass_audit
                else "derive beam/unit/mass conversion and a residual-blind velocity-squared load rule"
                if mom0_profile
                else (
                    "download/cache NGC2841 THINGS moment-0 map or accepted radial HI profile; "
                    "derive residual-blind Sigma_HI(R) kernel and conversion"
                )
            ),
            "numeric_context": (
                "NA_outer_ge_30kpc_mean_shape="
                f"{mom0_products['NA']['outer_ge_30kpc_mean_shape']:.6f};"
                "NA_outer_ge_30kpc_peak_shape="
                f"{mom0_products['NA']['outer_ge_30kpc_peak_shape']:.6f};"
                "RO_outer_ge_30kpc_mean_shape="
                f"{mom0_products['RO']['outer_ge_30kpc_mean_shape']:.6f};"
                "RO_outer_ge_30kpc_peak_shape="
                f"{mom0_products['RO']['outer_ge_30kpc_peak_shape']:.6f};"
                "support_outer_radius_kpc_1pct_peak=60.0"
                + (
                    ";NA_flux_ratio_to_vizier_global="
                    f"{mom0_mass_products['NA']['flux_ratio_to_vizier_global']:.6f};"
                    "RO_flux_ratio_to_vizier_global="
                    f"{mom0_mass_products['RO']['flux_ratio_to_vizier_global']:.6f};"
                    "NA_outer_spherical_v2_proxy="
                    f"{mom0_mass_products['NA']['outer_ge_30kpc_enclosed_spherical_v2_max_km2s2_proxy']:.6f};"
                    "RO_outer_spherical_v2_proxy="
                    f"{mom0_mass_products['RO']['outer_ge_30kpc_enclosed_spherical_v2_max_km2s2_proxy']:.6f}"
                    + (
                        ";NA_outer_disk_v2_proxy="
                        f"{mom0_disk_products['NA']['outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy']:.6f};"
                        "RO_outer_disk_v2_proxy="
                        f"{mom0_disk_products['RO']['outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy']:.6f};"
                        "NA_outer_hi_plus_helium_disk_v2_proxy="
                        f"{mom0_disk_products['NA']['outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy']:.6f};"
                        "RO_outer_hi_plus_helium_disk_v2_proxy="
                        f"{mom0_disk_products['RO']['outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy']:.6f};"
                        "primary_product="
                        f"{mom0_disk_review['primary_product']}"
                        if mom0_disk_review
                        else ""
                    )
                    if mom0_mass_audit
                    else ""
                )
            )
            if mom0_profile
            else "not_available_until_map_or_profile_cached",
        },
        {
            "galaxy": "NGC2841",
            "conversion_route": "things_vizier_global_hi_spectrum",
            "route_kind": "source_native_global_hi_spectrum",
            "source_basis": (
                "VizieR mirror of the THINGS catalog gives NGC2841 global HI spectrum "
                "and basic geometry, but not the radial or 2D surface-density map"
            ),
            "source_reference": "Walter2008THINGS_VizieR_J_AJ_136_2563",
            "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/136/2563",
            "local_artifact": (
                "data/source_manifests/"
                "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_summary_v0_1.json"
            )
            if global_hi
            else "not_cached",
            "conversion_status": (
                "FROZEN_GLOBAL_HI_SUPPORT_RADIAL_CONVERSION_MISSING"
                if global_hi
                else "SOURCE_NATIVE_ROUTE_OPEN_GLOBAL_SPECTRUM_NOT_CACHED"
            ),
            "velocity_squared_status": "global_flux_not_radial_velocity_squared_kernel",
            "positive_load_status": "not_ready",
            "allowed_use": "global_hi_support_and_consistency_context",
            "blocked_use": "radial_or_2d_positive_load_kernel",
            "next_action": (
                "use only as global HI support; still acquire THINGS moment-0 or radial profile"
            ),
            "numeric_context": (
                "integrated_positive_hi_flux_jy_kms_proxy="
                f"{global_hi['integrated_positive_hi_flux_jy_kms_proxy']:.6f};"
                "mhi_msun_from_spectrum_proxy="
                f"{global_hi['mhi_msun_from_spectrum_proxy']:.6e}"
            )
            if global_hi
            else "not_available_until_vizier_catalog_cached",
        },
        {
            "galaxy": "NGC2841",
            "conversion_route": "bosma_hi_scaling_outer_disk",
            "route_kind": "literature_hypothesis_or_scaling_control",
            "source_basis": (
                "HI-scaling/Bosma-effect style ideas may motivate comparing HI shape "
                "with missing capacity, but any scale factor must be source-frozen and "
                "not inferred from the rotation residual"
            ),
            "source_reference": "Bosma1981NGC2841HI;BosmaEffectLiterature",
            "source_url": "https://ned.ipac.caltech.edu/level5/March05/Bosma/Bosma4_6.html",
            "local_artifact": "data/external/literature/bosma1981_ngc2841_figure4_6_7.jpg",
            "conversion_status": "MOTIVATED_BUT_NO_SOURCE_FROZEN_SCALE",
            "velocity_squared_status": "shape_possible_scale_blocked",
            "positive_load_status": "not_ready",
            "allowed_use": "theory_context_or_future_control",
            "blocked_use": "free_scale_factor_chosen_from_endpoint_gap",
            "next_action": "find independent HI-scaling coefficient or reject as endpoint-fit route",
            "numeric_context": "no_residual_blind_scale_coefficient",
        },
        {
            "galaxy": "NGC2841",
            "conversion_route": "nfw_iso_halo_fit_parameters",
            "route_kind": "endpoint_fit_baseline",
            "source_basis": (
                "Published NFW/ISO halo models for NGC2841 fit the rotation curve and "
                "therefore are not source-side halo-capacity conversions for Tau kernel selection"
            ),
            "source_reference": "Samurovic2015NGC2841",
            "source_url": "https://academic.oup.com/mnras/article/451/4/4073/1115650",
            "local_artifact": "none",
            "conversion_status": "REJECTED_FOR_SOURCE_FREEZE",
            "velocity_squared_status": "endpoint_fit_not_source_freeze",
            "positive_load_status": "forbidden_as_tau_source_route",
            "allowed_use": "baseline_context_only",
            "blocked_use": "morphology_label;kernel;amplitude;halo_capacity_freeze",
            "next_action": "do_not_use_for_source_route_freeze",
            "numeric_context": "uses_rotation_curve_model_fit",
        },
    ]
    frame = pd.DataFrame(rows)
    frame["uses_vobs_or_residual"] = "no"
    frame.loc[
        frame["conversion_route"].eq("nfw_iso_halo_fit_parameters"),
        "uses_vobs_or_residual",
    ] = "yes_endpoint_fit_route_rejected"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["positive_load_freeze_permission"] = "no"
    frame["forbidden_endpoint_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "frozen_lower_bound_routes": ["sparc_things_vgas_lower_bound"],
        "frozen_global_hi_support_routes": (
            ["things_vizier_global_hi_spectrum"] if global_hi else []
        ),
        "frozen_mom0_radial_shape_routes": (
            ["things_moment0_radial_hi_surface_density"] if mom0_profile else []
        ),
        "next_primary_source_acquisition_target": (
            "independent_extended_hi_multiplier_or_tau_side_load_theorem"
            if mom0_disk_review
            else "mom0_disk_gravity_load_promotion_review"
            if mom0_mass_audit
            else "mom0_beam_unit_mass_conversion_audit"
            if mom0_profile
            else "things_moment0_radial_hi_surface_density"
        ),
        "rejected_endpoint_fit_routes": ["nfw_iso_halo_fit_parameters"],
        "positive_load_freeze_ready": False,
        "endpoint_ready": False,
        "hi_gas_lower_bound_fraction_of_required_gap_median": (
            hi_proxy["outer_median_gas_proxy_fraction_of_required_gap"]
        ),
        "hi_gas_lower_bound_fraction_of_required_gap_max": (
            hi_proxy["outer_max_gas_proxy_fraction_of_required_gap"]
        ),
        "global_hi_spectrum_freeze_ready": bool(global_hi),
        "global_hi_spectrum_mhi_msun_proxy": (
            global_hi["mhi_msun_from_spectrum_proxy"] if global_hi else None
        ),
        "global_hi_spectrum_integrated_flux_jy_kms_proxy": (
            global_hi["integrated_positive_hi_flux_jy_kms_proxy"] if global_hi else None
        ),
        "mom0_radial_profile_freeze_ready": bool(mom0_profile),
        "mom0_beam_unit_mass_audit_ready": bool(mom0_mass_audit),
        "mom0_mass_profile_proxy_ready": (
            bool(mom0_mass_audit and mom0_mass_audit["mass_profile_proxy_ready"])
        ),
        "mom0_disk_gravity_load_review_ready": bool(mom0_disk_review),
        "mom0_physical_hi_disk_load_control_ready": (
            bool(
                mom0_disk_review
                and mom0_disk_review["source_frozen_physical_hi_disk_load_control_ready"]
            )
        ),
        "mom0_standard_hi_plus_helium_gas_control_ready": (
            bool(
                mom0_disk_review
                and mom0_disk_review["source_frozen_standard_hi_plus_helium_gas_control_ready"]
            )
        ),
        "mom0_standard_helium_gas_factor": (
            mom0_disk_review["standard_helium_gas_factor"] if mom0_disk_review else None
        ),
        "mom0_absolute_load_ready": bool(mom0_disk_review),
        "mom0_positive_dark_residual_load_ready": False,
        "mom0_na_outer_ge_30kpc_mean_shape": (
            mom0_products["NA"]["outer_ge_30kpc_mean_shape"] if mom0_profile else None
        ),
        "mom0_na_outer_ge_30kpc_peak_shape": (
            mom0_products["NA"]["outer_ge_30kpc_peak_shape"] if mom0_profile else None
        ),
        "mom0_ro_outer_ge_30kpc_mean_shape": (
            mom0_products["RO"]["outer_ge_30kpc_mean_shape"] if mom0_profile else None
        ),
        "mom0_ro_outer_ge_30kpc_peak_shape": (
            mom0_products["RO"]["outer_ge_30kpc_peak_shape"] if mom0_profile else None
        ),
        "mom0_na_flux_ratio_to_vizier_global": (
            mom0_mass_products["NA"]["flux_ratio_to_vizier_global"] if mom0_mass_audit else None
        ),
        "mom0_ro_flux_ratio_to_vizier_global": (
            mom0_mass_products["RO"]["flux_ratio_to_vizier_global"] if mom0_mass_audit else None
        ),
        "mom0_primary_disk_load_product": (
            mom0_disk_review["primary_product"] if mom0_disk_review else None
        ),
        "mom0_na_outer_disk_v2_proxy": (
            mom0_disk_products["NA"]["outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy"]
            if mom0_disk_review
            else None
        ),
        "mom0_ro_outer_disk_v2_proxy": (
            mom0_disk_products["RO"]["outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy"]
            if mom0_disk_review
            else None
        ),
        "mom0_na_outer_hi_plus_helium_disk_v2_proxy": (
            mom0_disk_products["NA"]["outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy"]
            if mom0_disk_review
            else None
        ),
        "mom0_ro_outer_hi_plus_helium_disk_v2_proxy": (
            mom0_disk_products["RO"]["outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy"]
            if mom0_disk_review
            else None
        ),
        "conversion_status_counts": frame["conversion_status"].value_counts().sort_index().to_dict(),
        "positive_load_status_counts": frame["positive_load_status"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "positive_load_freeze_permission_counts": frame["positive_load_freeze_permission"].value_counts().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "A lower-bound SPARC/THINGS gas proxy is frozen, and the NED-hosted THINGS "
            "moment-0 products now provide source-native radial MOM0 shape/support, "
            "a beam/unit-consistent HI mass-profile proxy, and a lambda=1 physical-HI "
            "disk-load control, with standard HI+helium gas bookkeeping tracked only as "
            "a physical-gas control. A THINGS/VizieR global HI spectrum strengthens global "
            "support, but these artifacts are not yet an accepted positive dark-residual "
            "or halo-capacity kernel. The blocker has advanced to the need for an "
            "independent source-native multiplier or Tau-side load theorem. Published "
            "NFW/ISO halo fits are explicitly rejected for source-freeze use because "
            "they are endpoint-fit baselines."
        ),
        "next_allowed_action": (
            "If extra outer capacity beyond physical HI is needed, find an independent "
            "source-native multiplier or Tau-side load theorem. Do not infer a multiplier "
            "from the rotation residual, and do not use NFW/ISO fitted halo parameters "
            "for Tau source freeze."
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_conversion_search()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "conversion_route",
                "conversion_status",
                "positive_load_status",
                "allowed_use",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
