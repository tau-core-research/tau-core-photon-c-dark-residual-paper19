from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

MOM0_MASS_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_v0_1.csv"
MOM0_MASS_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_summary_v0_1.json"
)

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_mom0_disk_load_promotion_review_not_endpoint"
ENDPOINT_POLICY = (
    "source_side_disk_load_review_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_fits"
)
FORBIDDEN_INPUTS = (
    "Vobs;errV;rotation_residual;RMSE;baseline_score;endpoint_rank;"
    "NFW_best_fit;ISO_best_fit;MOND_fit;RAR_fit;required_lambda_fit"
)

G_KPC_KMS2_PER_MSUN = 4.30091e-6
ANGLE_SAMPLES = 720
SOFTENING_KPC = 0.5
STANDARD_HELIUM_GAS_FACTOR = 1.36


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _ring_disk_v2(
    eval_radii: np.ndarray,
    ring_radii: np.ndarray,
    ring_masses: np.ndarray,
    softening_kpc: float,
) -> np.ndarray:
    phi = np.linspace(0.0, 2.0 * math.pi, ANGLE_SAMPLES, endpoint=False)
    cos_phi = np.cos(phi)
    out = np.zeros_like(eval_radii, dtype=float)
    for i, radius in enumerate(eval_radii):
        if radius <= 0.0:
            continue
        total = 0.0
        for ring_radius, mass in zip(ring_radii, ring_masses):
            if mass <= 0.0:
                continue
            d2 = (
                radius * radius
                + ring_radius * ring_radius
                - 2.0 * radius * ring_radius * cos_phi
                + softening_kpc * softening_kpc
            )
            radial_kernel = np.mean((radius - ring_radius * cos_phi) / np.power(d2, 1.5))
            total += G_KPC_KMS2_PER_MSUN * mass * radius * radial_kernel
        out[i] = total
    return out


def build_review() -> tuple[pd.DataFrame, dict[str, object]]:
    mom0_summary = _load_json(MOM0_MASS_SUMMARY)
    frame = pd.read_csv(MOM0_MASS_CSV, keep_default_na=False)
    product_summaries = {
        item["product"]: item for item in mom0_summary["product_summaries"]
    }

    rows: list[pd.DataFrame] = []
    product_out: list[dict[str, object]] = []
    for product, product_frame in frame.groupby("product", sort=True):
        product_frame = product_frame.sort_values("radius_mid_kpc").copy()
        radii = product_frame["radius_mid_kpc"].to_numpy(float)
        masses = product_frame["annulus_hi_mass_msun_proxy"].to_numpy(float)
        disk_v2 = _ring_disk_v2(radii, radii, masses, SOFTENING_KPC)
        disk_v2_positive = np.clip(disk_v2, 0.0, None)
        outer = radii >= 30.0
        outer_max = float(np.max(disk_v2_positive[outer])) if np.any(outer) else 0.0
        product_frame["axisymmetric_disk_v2_km2s2_proxy"] = disk_v2
        product_frame["axisymmetric_disk_v2_positive_km2s2_proxy"] = disk_v2_positive
        product_frame["standard_hi_plus_helium_disk_v2_positive_km2s2_proxy"] = (
            STANDARD_HELIUM_GAS_FACTOR * disk_v2_positive
        )
        product_frame["disk_load_shape_kernel_outer_ge_30kpc"] = np.where(
            outer & (outer_max > 0.0), disk_v2_positive / outer_max, 0.0
        )
        product_frame["disk_load_formula_shell"] = (
            "v2_HI_disk(R)=G*R*sum_j M_j*<"
            "(R-R_j*cos(phi))/(R^2+R_j^2-2RR_j*cos(phi)+eps^2)^(3/2)>_phi"
        )
        product_frame["amplitude_rule"] = "lambda_HI=1_physical_hi_mass_only_no_residual_fit"
        product_frame["standard_gas_factor_rule"] = (
            "optional_lambda_gas=1.36_standard_helium_correction_no_residual_fit"
        )
        product_frame["softening_kpc"] = SOFTENING_KPC
        product_frame["angle_samples"] = ANGLE_SAMPLES
        product_frame["allowed_use"] = "source_frozen_physical_hi_disk_load_control"
        product_frame["blocked_use"] = (
            "positive_dark_residual_or_halo_capacity_kernel_without_independent_multiplier"
        )
        product_frame["uses_vobs_or_residual"] = "no"
        product_frame["endpoint_replay_permission"] = "no"
        product_frame["kernel_promotion_permission"] = "no"
        product_frame["positive_load_freeze_permission"] = "no"
        product_frame["forbidden_endpoint_inputs"] = FORBIDDEN_INPUTS
        product_frame["endpoint_data_policy"] = ENDPOINT_POLICY
        product_frame["claim_boundary"] = CLAIM_BOUNDARY
        rows.append(product_frame)

        product_info = product_summaries[str(product)]
        product_out.append(
            {
                "product": product,
                "flux_ratio_to_vizier_global": product_info["flux_ratio_to_vizier_global"],
                "integrated_hi_mass_msun_proxy": product_info[
                    "integrated_mom0_hi_mass_msun_proxy"
                ],
                "outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy": outer_max,
                "outer_ge_30kpc_axisymmetric_disk_v2_median_km2s2_proxy": float(
                    np.median(disk_v2_positive[outer])
                )
                if np.any(outer)
                else 0.0,
                "outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy": (
                    STANDARD_HELIUM_GAS_FACTOR * outer_max
                ),
                "outer_ge_30kpc_hi_plus_helium_disk_v2_median_km2s2_proxy": (
                    STANDARD_HELIUM_GAS_FACTOR
                    * (
                        float(np.median(disk_v2_positive[outer]))
                        if np.any(outer)
                        else 0.0
                    )
                ),
                "inner_any_negative_raw_disk_v2": bool(np.any(disk_v2 < 0.0)),
            }
        )

    out_frame = pd.concat(rows, ignore_index=True)
    primary_product = "RO"
    summary = {
        "galaxy": "NGC2841",
        "products": sorted(product_summaries),
        "n_rows": int(len(out_frame)),
        "source_reference": mom0_summary["source_reference"],
        "input_artifact": str(MOM0_MASS_CSV.relative_to(ROOT)),
        "formula_shell": "softened_axisymmetric_annular_disk_from_source_native_MOM0_HI_mass_profile",
        "formula_shell_status": "source_frozen_physical_hi_disk_load_control_ready",
        "primary_product_rule": (
            "RO is the primary source-side product because it has the smaller beam and "
            "the closer integrated-flux match to the independent VizieR global spectrum; "
            "NA is retained as a cross-check product."
        ),
        "primary_product": primary_product,
        "amplitude_rule": "lambda_HI=1_physical_hi_mass_only_no_residual_fit",
        "standard_gas_factor_rule": (
            "optional_lambda_gas=1.36_standard_helium_correction_no_residual_fit"
        ),
        "standard_helium_gas_factor": STANDARD_HELIUM_GAS_FACTOR,
        "softening_kpc": SOFTENING_KPC,
        "angle_samples": ANGLE_SAMPLES,
        "source_frozen_physical_hi_disk_load_control_ready": True,
        "source_frozen_standard_hi_plus_helium_gas_control_ready": True,
        "positive_dark_residual_load_ready": False,
        "halo_capacity_multiplier_ready": False,
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
            "The MOM0-derived HI mass profile can be promoted only to a source-frozen "
            "physical-HI disk-load control with lambda_HI=1, with an optional standard "
            "HI+helium gas bookkeeping factor of 1.36. It cannot yet be promoted to a "
            "positive dark-residual or halo-capacity kernel, because any additional "
            "multiplier would need an independent residual-blind source."
        ),
        "next_allowed_action": (
            "If the theory needs extra outer capacity beyond physical HI, find an "
            "independent source-native multiplier or Tau-side load theorem. Do not infer "
            "a multiplier from the rotation residual."
        ),
    }
    return out_frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
