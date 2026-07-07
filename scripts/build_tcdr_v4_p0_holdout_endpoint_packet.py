from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
PILOT = SOURCE_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"
SAMPLE = EXTERNAL_DIR / "SPARC_Lelli2016c.mrt"
MASS_MODELS = EXTERNAL_DIR / "MassModels_Lelli2016c.mrt"

READINESS_CSV = SOURCE_DIR / "tcdr_v4_p0_holdout_endpoint_readiness_v0_1.csv"
READINESS_JSON = SOURCE_DIR / "tcdr_v4_p0_holdout_endpoint_readiness_summary_v0_1.json"
LOCAL_CURVES = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_curves_local.csv"
LOCAL_SUMMARY = EXTERNAL_DIR / "tcdr_v4_p0_holdout_endpoint_curves_local_summary.json"

ENDPOINT_POLICY = "endpoint_values_local_only_not_committed"
CARRIER_POLICY = "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_amplitude_fit"


def _sample_rows(galaxies: set[str]) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    for line in SAMPLE.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if not parts or parts[0] not in galaxies:
            continue
        # Table 1 has fixed columns. Use split parsing only after matching the
        # galaxy id; reference codes at the end are not needed for this packet.
        rows[parts[0]] = {
            "sample_t": int(parts[1]),
            "distance_mpc": float(parts[2]),
            "distance_error_mpc": float(parts[3]),
            "distance_method_flag": int(parts[4]),
            "inclination_deg": float(parts[5]),
            "inclination_error_deg": float(parts[6]),
            "rdisk_kpc": float(parts[11]),
            "mhi_1e9_msun": float(parts[13]),
            "rhi_kpc": float(parts[14]),
            "quality_flag": int(parts[17]),
        }
    return rows


def _mass_model_rows(galaxies: set[str]) -> pd.DataFrame:
    rows = []
    for line in MASS_MODELS.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if not parts or parts[0] not in galaxies:
            continue
        rows.append(
            {
                "galaxy": parts[0],
                "distance_mpc": float(parts[1]),
                "radius_kpc": float(parts[2]),
                "vobs_kms": float(parts[3]),
                "e_vobs_kms": float(parts[4]),
                "vgas_kms": float(parts[5]),
                "vdisk_kms": float(parts[6]),
                "vbul_kms": float(parts[7]),
                "sbdisk_lsun_pc2": float(parts[8]),
                "sbbul_lsun_pc2": float(parts[9]),
            }
        )
    detail = pd.DataFrame(rows)
    if detail.empty:
        return detail
    # SPARC gas terms can be signed; keep the conventional signed-square gas
    # contribution for the local preflight carrier. This is not a fit.
    vbar2 = (
        detail["vgas_kms"] * detail["vgas_kms"].abs()
        + 0.5 * detail["vdisk_kms"] ** 2
        + 0.7 * detail["vbul_kms"] ** 2
    )
    detail["vbar_fixed_mlr_kms"] = vbar2.map(lambda x: math.sqrt(x) if x > 0 else 0.0)
    detail["carrier_policy"] = CARRIER_POLICY
    detail["endpoint_policy"] = ENDPOINT_POLICY
    return detail


def build_endpoint_packet() -> tuple[pd.DataFrame, dict[str, object]]:
    pilot = pd.read_csv(PILOT)
    holdout = pilot[pilot["pilot_role"] == "PILOT_HOLDOUT"].copy()
    galaxies = set(str(galaxy) for galaxy in holdout["galaxy"])
    sample = _sample_rows(galaxies)
    curves = _mass_model_rows(galaxies)

    readiness_rows = []
    for _, row in holdout.sort_values(["source_family_candidate", "galaxy"]).iterrows():
        galaxy = str(row["galaxy"])
        curve = curves[curves["galaxy"] == galaxy] if not curves.empty else pd.DataFrame()
        sample_row = sample.get(galaxy, {})
        readiness_rows.append(
            {
                "galaxy": galaxy,
                "source_family_candidate": row["source_family_candidate"],
                "source_tier": row["source_tier"],
                "projection_caveat": row["projection_caveat"],
                "endpoint_availability": "available" if not curve.empty else "missing",
                "n_rotation_points": int(len(curve)),
                "r_min_kpc": "" if curve.empty else float(curve["radius_kpc"].min()),
                "r_max_kpc": "" if curve.empty else float(curve["radius_kpc"].max()),
                "has_bulge_component": "" if curve.empty else ("yes" if (curve["vbul_kms"].abs() > 0).any() else "no"),
                "has_signed_gas_terms": "" if curve.empty else ("yes" if (curve["vgas_kms"] < 0).any() else "no"),
                "distance_mpc": sample_row.get("distance_mpc", ""),
                "inclination_deg": sample_row.get("inclination_deg", ""),
                "quality_flag": sample_row.get("quality_flag", ""),
                "rhi_kpc": sample_row.get("rhi_kpc", ""),
                "rdisk_kpc": sample_row.get("rdisk_kpc", ""),
                "carrier_policy": CARRIER_POLICY,
                "endpoint_policy": ENDPOINT_POLICY,
                "source_label_policy": "source_family_already_frozen_before_endpoint_packet",
                "score_policy": "readiness_only_no_endpoint_score",
            }
        )

    readiness = pd.DataFrame(readiness_rows)
    if not curves.empty:
        curves = curves.merge(
            holdout[
                [
                    "galaxy",
                    "source_family_candidate",
                    "projection_caveat",
                    "pilot_selection_policy",
                ]
            ],
            on="galaxy",
            how="left",
        ).sort_values(["source_family_candidate", "galaxy", "radius_kpc"])

    role_counts = readiness["endpoint_availability"].value_counts().sort_index().to_dict()
    summary = {
        "n_holdout_objects": int(len(readiness)),
        "endpoint_availability_counts": {key: int(value) for key, value in role_counts.items()},
        "n_total_rotation_points_local": int(len(curves)),
        "carrier_policy": CARRIER_POLICY,
        "endpoint_policy": ENDPOINT_POLICY,
        "local_curve_packet": str(LOCAL_CURVES.relative_to(ROOT)),
        "committed_readiness_manifest": str(READINESS_CSV.relative_to(ROOT)),
        "claim_boundary": "readiness_only_no_scoring_no_baseline_comparison_no_validation",
    }
    return readiness, curves, summary


def main() -> None:
    readiness, curves, summary = build_endpoint_packet()
    readiness.to_csv(READINESS_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    READINESS_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not curves.empty:
        curves.to_csv(LOCAL_CURVES, index=False, quoting=csv.QUOTE_MINIMAL)
    LOCAL_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {READINESS_CSV}")
    print(f"WROTE {READINESS_JSON}")
    print(f"WROTE LOCAL {LOCAL_CURVES}")
    print(f"WROTE LOCAL {LOCAL_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
