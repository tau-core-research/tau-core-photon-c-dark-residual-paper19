from __future__ import annotations

import csv
import gzip
import json
import re
import urllib.request
from pathlib import Path

import numpy as np
from astropy.io import fits


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LOCAL_DIR = ROOT / "data" / "external" / "literature" / "ngc2841_things_ned"

CLAIM_BOUNDARY = "ngc2841_things_ned_mom0_radial_profile_freeze_not_endpoint"
CATALOG_REFERENCE = "Walter2008THINGS_NED_Images_2008AJ_136_2563W"

MOM0_PRODUCTS = {
    "NA": "https://ned.ipac.caltech.edu/img/2008AJ....136.2563W/NGC_2841_NA_MOM0:I:HI:wbb2008.fits.gz",
    "RO": "https://ned.ipac.caltech.edu/img/2008AJ....136.2563W/NGC_2841_RO_MOM0:I:HI:wbb2008.fits.gz",
}

# THINGS/VizieR metadata frozen in the companion global-HI source artifact.
DISTANCE_MPC = 14.1
INCLINATION_DEG = 74.0
POSITION_ANGLE_DEG = 153.0


def local_name(url: str) -> str:
    return url.rsplit("/", 1)[-1].replace(":", "_")


def download_if_missing(url: str) -> Path:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    path = LOCAL_DIR / local_name(url)
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    return path


def parse_history_beam_deg(header: fits.Header) -> dict[str, float | None]:
    history = "\n".join(str(card) for card in header.get("HISTORY", []))
    match = re.search(
        r"CLEAN\s+BMAJ=\s*([0-9.Ee+-]+)\s+BMIN=\s*([0-9.Ee+-]+)\s+BPA=\s*([0-9.Ee+-]+)",
        history,
    )
    if not match:
        return {"bmaj_deg": None, "bmin_deg": None, "bpa_deg": None}
    return {
        "bmaj_deg": float(match.group(1)),
        "bmin_deg": float(match.group(2)),
        "bpa_deg": float(match.group(3)),
    }


def radial_profile(path: Path, product: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    with fits.open(path) as hdul:
        header = hdul[0].header
        data = np.squeeze(hdul[0].data).astype(float)

    # Moment-0 maps may contain small negative cleaning/noise residuals.  The
    # source-freeze profile uses positive emission support only and does not
    # attempt absolute surface-density calibration.
    positive = np.clip(data, 0.0, None)
    y_index, x_index = np.indices(data.shape)
    pixscale_arcsec = abs(float(header["CDELT2"])) * 3600.0
    x_east_arcsec = -(x_index + 1.0 - float(header["CRPIX1"])) * pixscale_arcsec
    y_north_arcsec = (y_index + 1.0 - float(header["CRPIX2"])) * pixscale_arcsec

    pa = np.deg2rad(POSITION_ANGLE_DEG)
    incl = np.deg2rad(INCLINATION_DEG)
    x_major = x_east_arcsec * np.sin(pa) + y_north_arcsec * np.cos(pa)
    y_minor = x_east_arcsec * np.cos(pa) - y_north_arcsec * np.sin(pa)
    radius_arcsec = np.sqrt(x_major**2 + (y_minor / np.cos(incl)) ** 2)
    kpc_per_arcsec = DISTANCE_MPC * 1.0e3 / 206265.0
    radius_kpc = radius_arcsec * kpc_per_arcsec

    bin_width_kpc = 1.0
    max_radius_kpc = 60.0
    bins = np.arange(0.0, max_radius_kpc + bin_width_kpc, bin_width_kpc)
    peak_mean = 0.0
    raw_rows: list[dict[str, object]] = []
    for r0, r1 in zip(bins[:-1], bins[1:]):
        mask = (radius_kpc >= r0) & (radius_kpc < r1)
        values = positive[mask]
        finite = values[np.isfinite(values)]
        positive_finite = finite[finite > 0.0]
        mean_positive = float(np.mean(positive_finite)) if len(positive_finite) else 0.0
        median_positive = float(np.median(positive_finite)) if len(positive_finite) else 0.0
        sum_positive = float(np.sum(positive_finite)) if len(positive_finite) else 0.0
        peak_mean = max(peak_mean, mean_positive)
        raw_rows.append(
            {
                "product": product,
                "radius_inner_kpc": r0,
                "radius_outer_kpc": r1,
                "radius_mid_kpc": 0.5 * (r0 + r1),
                "n_pixels_total": int(len(finite)),
                "n_pixels_positive": int(len(positive_finite)),
                "mom0_positive_mean_source_units": mean_positive,
                "mom0_positive_median_source_units": median_positive,
                "mom0_positive_sum_source_units": sum_positive,
            }
        )

    rows: list[dict[str, object]] = []
    support_threshold = 0.01
    for row in raw_rows:
        shape = (
            float(row["mom0_positive_mean_source_units"]) / peak_mean
            if peak_mean > 0.0
            else 0.0
        )
        rows.append(
            {
                **row,
                "mom0_shape_kernel": shape,
                "support_above_1pct_peak": "yes" if shape >= support_threshold else "no",
                "uses_vobs_or_residual": "no",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "positive_load_freeze_permission": "no",
                "allowed_use": "source_native_mom0_radial_shape_support",
                "blocked_use": "absolute_velocity_squared_load_without_beam_and_mass_conversion_audit",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    supported = [row for row in rows if row["support_above_1pct_peak"] == "yes"]
    support_outer_kpc = max((float(row["radius_outer_kpc"]) for row in supported), default=0.0)
    outer_rows = [row for row in rows if float(row["radius_mid_kpc"]) >= 30.0]
    outer_peak_shape = max((float(row["mom0_shape_kernel"]) for row in outer_rows), default=0.0)
    outer_mean_shape = float(np.mean([float(row["mom0_shape_kernel"]) for row in outer_rows]))
    header_beam = parse_history_beam_deg(header)
    summary = {
        "product": product,
        "local_fits_gz": str(path.relative_to(ROOT)),
        "source_url": MOM0_PRODUCTS[product],
        "bunit": header.get("BUNIT"),
        "naxis1": int(header["NAXIS1"]),
        "naxis2": int(header["NAXIS2"]),
        "pixel_scale_arcsec": pixscale_arcsec,
        "distance_mpc_used": DISTANCE_MPC,
        "inclination_deg_used": INCLINATION_DEG,
        "position_angle_deg_used": POSITION_ANGLE_DEG,
        "beam_from_history": header_beam,
        "peak_mean_positive_source_units": peak_mean,
        "support_outer_radius_kpc_1pct_peak": support_outer_kpc,
        "outer_ge_30kpc_peak_shape": outer_peak_shape,
        "outer_ge_30kpc_mean_shape": outer_mean_shape,
    }
    return rows, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    product_summaries: list[dict[str, object]] = []
    for product, url in MOM0_PRODUCTS.items():
        path = download_if_missing(url)
        rows, summary = radial_profile(path, product)
        all_rows.extend(rows)
        product_summaries.append(summary)

    out_csv = SOURCE_DIR / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_v0_1.csv"
    out_json = (
        SOURCE_DIR / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_summary_v0_1.json"
    )
    fieldnames = list(all_rows[0].keys())
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    summary = {
        "galaxy": "NGC2841",
        "source_reference": CATALOG_REFERENCE,
        "source_urls": MOM0_PRODUCTS,
        "products": [item["product"] for item in product_summaries],
        "n_rows": int(len(all_rows)),
        "bin_width_kpc": 1.0,
        "radial_profile_freeze_ready": True,
        "absolute_surface_density_or_load_ready": False,
        "positive_load_freeze_ready": False,
        "endpoint_ready": False,
        "product_summaries": product_summaries,
        "endpoint_replay_permission_counts": {"no": int(len(all_rows))},
        "kernel_promotion_permission_counts": {"no": int(len(all_rows))},
        "positive_load_freeze_permission_counts": {"no": int(len(all_rows))},
        "uses_vobs_or_residual_counts": {"no": int(len(all_rows))},
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NED exposes THINGS NGC2841 natural- and robust-weighted moment-0 FITS "
            "products. A residual-blind radial MOM0 shape/support profile can be "
            "frozen. Absolute surface-density, beam, and velocity-squared load "
            "conversion remain blocked pending a dedicated calibration audit."
        ),
        "next_allowed_action": (
            "Use the frozen MOM0 radial shape only as source-native HI support. "
            "Before endpoint replay, derive a beam/unit/mass conversion and a "
            "source-frozen velocity-squared load rule."
        ),
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {out_csv}")
    print(f"WROTE {out_json}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
