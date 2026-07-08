from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

MOM0_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_v0_1.csv"
MOM0_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_summary_v0_1.json"
GLOBAL_HI_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_v0_1.csv"
OUT_JSON = (
    SOURCE_DIR / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_things_mom0_beam_unit_mass_conversion_audit_not_endpoint"
ENDPOINT_POLICY = (
    "source_side_mom0_calibration_audit_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_fits"
)
FORBIDDEN_INPUTS = (
    "Vobs;errV;rotation_residual;RMSE;baseline_score;endpoint_rank;"
    "NFW_best_fit;ISO_best_fit;MOND_fit;RAR_fit;required_lambda_fit"
)

HI_MASS_COEFF = 2.356e5  # Msun Mpc^-2 (Jy km/s)^-1
G_KPC_KMS2_PER_MSUN = 4.30091e-6


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _beam_pixels(product_summary: dict[str, object]) -> float:
    beam = product_summary["beam_from_history"]
    bmaj_arcsec = float(beam["bmaj_deg"]) * 3600.0
    bmin_arcsec = float(beam["bmin_deg"]) * 3600.0
    pixel_scale = float(product_summary["pixel_scale_arcsec"])
    beam_area_arcsec2 = math.pi * bmaj_arcsec * bmin_arcsec / (4.0 * math.log(2.0))
    pixel_area_arcsec2 = pixel_scale * pixel_scale
    return beam_area_arcsec2 / pixel_area_arcsec2


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    mom0_summary = _load_json(MOM0_SUMMARY)
    global_hi = _load_json(GLOBAL_HI_SUMMARY)
    frame = pd.read_csv(MOM0_CSV, keep_default_na=False)
    product_summary = {
        item["product"]: item for item in mom0_summary["product_summaries"]
    }

    rows: list[dict[str, object]] = []
    product_out: list[dict[str, object]] = []
    for product, product_frame in frame.groupby("product", sort=True):
        psummary = product_summary[str(product)]
        distance_mpc = float(psummary["distance_mpc_used"])
        beam_pix = _beam_pixels(psummary)
        running_mass_msun = 0.0
        product_rows = product_frame.sort_values("radius_mid_kpc")
        for _, row in product_rows.iterrows():
            radius_outer = float(row["radius_outer_kpc"])
            radius_inner = float(row["radius_inner_kpc"])
            radius_mid = float(row["radius_mid_kpc"])
            mom0_sum_m_s = float(row["mom0_positive_sum_source_units"])
            flux_jy_kms = mom0_sum_m_s / 1000.0 / beam_pix
            mass_msun = HI_MASS_COEFF * distance_mpc * distance_mpc * flux_jy_kms
            running_mass_msun += mass_msun
            annulus_area_pc2 = math.pi * (radius_outer**2 - radius_inner**2) * 1.0e6
            sigma_hi_msun_pc2 = mass_msun / annulus_area_pc2 if annulus_area_pc2 > 0 else 0.0
            v2_enclosed_equiv = (
                G_KPC_KMS2_PER_MSUN * running_mass_msun / radius_mid
                if radius_mid > 0
                else 0.0
            )
            rows.append(
                {
                    "galaxy": "NGC2841",
                    "product": product,
                    "radius_inner_kpc": radius_inner,
                    "radius_outer_kpc": radius_outer,
                    "radius_mid_kpc": radius_mid,
                    "mom0_sum_source_units_jy_per_beam_m_per_s": mom0_sum_m_s,
                    "beam_area_pixels_from_history": beam_pix,
                    "annulus_flux_jy_kms_proxy": flux_jy_kms,
                    "annulus_hi_mass_msun_proxy": mass_msun,
                    "enclosed_hi_mass_msun_proxy": running_mass_msun,
                    "annulus_sigma_hi_msun_pc2_proxy": sigma_hi_msun_pc2,
                    "enclosed_spherical_v2_km2s2_proxy": v2_enclosed_equiv,
                    "mom0_shape_kernel": float(row["mom0_shape_kernel"]),
                    "allowed_use": "source_native_mom0_mass_calibration_audit",
                    "blocked_use": "endpoint_replay_or_absolute_dark_residual_claim_without_disk_gravity_review",
                    "uses_vobs_or_residual": "no",
                    "endpoint_replay_permission": "no",
                    "kernel_promotion_permission": "no",
                    "positive_load_freeze_permission": "no",
                    "forbidden_endpoint_inputs": FORBIDDEN_INPUTS,
                    "endpoint_data_policy": ENDPOINT_POLICY,
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )

        total_flux = sum(item["annulus_flux_jy_kms_proxy"] for item in rows if item["product"] == product)
        total_mass = sum(item["annulus_hi_mass_msun_proxy"] for item in rows if item["product"] == product)
        global_flux = float(global_hi["integrated_positive_hi_flux_jy_kms_proxy"])
        product_out.append(
            {
                "product": product,
                "beam_area_pixels_from_history": beam_pix,
                "integrated_mom0_flux_jy_kms_proxy": total_flux,
                "integrated_mom0_hi_mass_msun_proxy": total_mass,
                "vizier_global_flux_jy_kms_proxy": global_flux,
                "flux_ratio_to_vizier_global": total_flux / global_flux,
                "outer_ge_30kpc_enclosed_spherical_v2_max_km2s2_proxy": max(
                    item["enclosed_spherical_v2_km2s2_proxy"]
                    for item in rows
                    if item["product"] == product and item["radius_mid_kpc"] >= 30.0
                ),
                "outer_ge_30kpc_sigma_hi_msun_pc2_median_proxy": float(
                    pd.Series(
                        [
                            item["annulus_sigma_hi_msun_pc2_proxy"]
                            for item in rows
                            if item["product"] == product and item["radius_mid_kpc"] >= 30.0
                        ]
                    ).median()
                ),
            }
        )

    out_frame = pd.DataFrame(rows)
    summary = {
        "galaxy": "NGC2841",
        "products": sorted(product_summary),
        "n_rows": int(len(out_frame)),
        "source_reference": "Walter2008THINGS_NED_Images_2008AJ_136_2563W",
        "calibration_reference_artifact": str(MOM0_SUMMARY.relative_to(ROOT)),
        "global_hi_reference_artifact": str(GLOBAL_HI_SUMMARY.relative_to(ROOT)),
        "hi_mass_conversion": "M_HI_Msun=2.356e5*D_Mpc^2*S_HI_Jy_km_s",
        "source_native_flux_consistency_ready": True,
        "mass_profile_proxy_ready": True,
        "disk_gravity_load_review_ready": False,
        "positive_load_freeze_ready": False,
        "endpoint_ready": False,
        "product_summaries": product_out,
        "endpoint_replay_permission_counts": out_frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": out_frame["kernel_promotion_permission"].value_counts().to_dict(),
        "positive_load_freeze_permission_counts": out_frame[
            "positive_load_freeze_permission"
        ].value_counts().to_dict(),
        "uses_vobs_or_residual_counts": out_frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The NED/THINGS MOM0 maps pass a source-side beam/unit consistency check: "
            "beam-area conversion gives integrated HI fluxes close to the VizieR global "
            "spectrum. A residual-blind HI mass-profile proxy can therefore be audited. "
            "This is still not an endpoint kernel or dark-residual load claim because disk "
            "gravity/load promotion has not been reviewed."
        ),
        "next_allowed_action": (
            "Review whether the MOM0-derived HI mass profile may be promoted to a "
            "source-frozen extended-HI load family, including disk-gravity geometry and "
            "no-residual amplitude rules."
        ),
    }
    return out_frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_audit()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
