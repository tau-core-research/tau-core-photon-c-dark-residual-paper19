from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from astroquery.vizier import Vizier


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"
CATALOG = "J/AJ/136/2563"
GALAXY = "NGC 2841"


def masked_to_float_array(column) -> np.ndarray:
    if hasattr(column, "filled"):
        return np.array(column.filled(np.nan), dtype=float)
    return np.array(column, dtype=float)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_v0_1.csv"
    summary_path = (
        OUT_DIR / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_summary_v0_1.json"
    )
    Vizier.ROW_LIMIT = -1
    try:
        tables = Vizier.get_catalogs(CATALOG)
    except Exception as exc:
        if csv_path.exists() and summary_path.exists():
            print(f"[OFFLINE-CACHE] VizieR query unavailable ({exc}); verified committed {csv_path.name}")
            return
        raise
    table1 = tables[f"{CATALOG}/table1"]
    table4 = tables[f"{CATALOG}/table4"]

    meta_rows = table1[table1["Name"] == GALAXY]
    if len(meta_rows) != 1:
        raise RuntimeError(f"Expected exactly one {GALAXY} metadata row, found {len(meta_rows)}")
    meta = meta_rows[0]

    spectrum = table4[table4["Name"] == GALAXY]
    if len(spectrum) == 0:
        raise RuntimeError(f"No {GALAXY} spectrum rows found in {CATALOG}/table4")

    velocity = np.array(spectrum["Vel"], dtype=float)
    flux_density = masked_to_float_array(spectrum["SHI"])
    valid = np.isfinite(flux_density)
    positive_flux_density = np.where(valid, np.clip(flux_density, 0.0, None), np.nan)
    sorted_velocity = np.sort(velocity)
    channel_width_kms = float(abs(np.nanmedian(np.diff(sorted_velocity))))
    integrated_flux_jy_kms = float(np.nansum(positive_flux_density) * channel_width_kms)
    distance_mpc = float(meta["Dist"])
    mhi_msun_from_spectrum = float(2.356e5 * distance_mpc**2 * integrated_flux_jy_kms)

    csv_path = OUT_DIR / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_v0_1.csv"
    summary_path = (
        OUT_DIR / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_summary_v0_1.json"
    )

    fieldnames = [
        "galaxy",
        "catalog",
        "source_table",
        "velocity_kms",
        "shi_jy",
        "shi_positive_jy",
        "channel_width_kms_used",
        "uses_vobs_or_residual",
        "endpoint_replay_permission",
        "kernel_promotion_permission",
        "positive_load_freeze_permission",
        "allowed_use",
        "blocked_use",
        "claim_boundary",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for vel, flux, pos_flux in zip(velocity, flux_density, positive_flux_density):
            writer.writerow(
                {
                    "galaxy": GALAXY,
                    "catalog": CATALOG,
                    "source_table": "table4_global_hi_profile",
                    "velocity_kms": f"{vel:.6g}",
                    "shi_jy": "" if not np.isfinite(flux) else f"{flux:.9g}",
                    "shi_positive_jy": ""
                    if not np.isfinite(pos_flux)
                    else f"{pos_flux:.9g}",
                    "channel_width_kms_used": f"{channel_width_kms:.9g}",
                    "uses_vobs_or_residual": "no",
                    "endpoint_replay_permission": "no",
                    "kernel_promotion_permission": "no",
                    "positive_load_freeze_permission": "no",
                    "allowed_use": "global_hi_support_and_consistency_context",
                    "blocked_use": "radial_or_2d_halo_capacity_conversion",
                    "claim_boundary": "ngc2841_things_vizier_global_hi_source_freeze_not_endpoint",
                }
            )

    summary = {
        "galaxy": GALAXY,
        "catalog": CATALOG,
        "source_reference": "Walter2008THINGS_VizieR_J_AJ_136_2563",
        "source_url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/136/2563",
        "n_spectrum_rows": int(len(spectrum)),
        "n_valid_flux_rows": int(valid.sum()),
        "velocity_min_kms": float(np.nanmin(velocity)),
        "velocity_max_kms": float(np.nanmax(velocity)),
        "channel_width_kms_used": channel_width_kms,
        "integrated_positive_hi_flux_jy_kms_proxy": integrated_flux_jy_kms,
        "distance_mpc_catalog": distance_mpc,
        "inclination_deg_catalog": float(meta["i"]),
        "position_angle_deg_catalog": float(meta["PA"]),
        "type_tt_catalog": int(meta["TT"]),
        "sfr_msun_per_yr_catalog": float(meta["SFR"]),
        "mhi_msun_from_spectrum_proxy": mhi_msun_from_spectrum,
        "global_hi_source_freeze_ready": True,
        "radial_hi_surface_density_ready": False,
        "positive_load_freeze_ready": False,
        "endpoint_ready": False,
        "endpoint_replay_permission_counts": {"no": int(len(spectrum))},
        "kernel_promotion_permission_counts": {"no": int(len(spectrum))},
        "positive_load_freeze_permission_counts": {"no": int(len(spectrum))},
        "uses_vobs_or_residual_counts": {"no": int(len(spectrum))},
        "claim_boundary": "ngc2841_things_vizier_global_hi_source_freeze_not_endpoint",
        "verdict": (
            "The THINGS/VizieR catalog supplies source-native NGC2841 global HI "
            "spectrum and basic geometry. This strengthens global HI support but "
            "does not provide the radial or 2D surface-density profile needed for "
            "a halo-capacity conversion."
        ),
        "next_allowed_action": (
            "Acquire/cache a source-native THINGS moment-0 map or accepted radial "
            "HI surface-density profile; do not promote the global spectrum into a "
            "positive-load kernel."
        ),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"WROTE {csv_path}")
    print(f"WROTE {summary_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
