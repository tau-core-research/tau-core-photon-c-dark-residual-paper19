from __future__ import annotations

import csv
import json
import math
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
PREFLIGHT_DIR = ROOT / "data" / "external" / "sparc_preflight"

ROTMOD_ZIP = PREFLIGHT_DIR / "Rotmod_LTG.zip"
ROTMOD_MEMBER = "NGC2841_rotmod.dat"
REQUIRED_SCALE = PREFLIGHT_DIR / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_sparc_hi_gas_load_proxy_freeze_not_positive_dark_residual"
ENDPOINT_POLICY = (
    "source_component_freeze_only_ignore_vobs_errv_endpoint_scores_and_rotation_residuals"
)
FORBIDDEN_ENDPOINT_INPUTS = (
    "Vobs;errV;rotation_residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _read_rotmod_gas_profile() -> pd.DataFrame:
    if not ROTMOD_ZIP.exists():
        raise FileNotFoundError(f"Missing SPARC Rotmod archive: {ROTMOD_ZIP}")
    with zipfile.ZipFile(ROTMOD_ZIP) as zf:
        if ROTMOD_MEMBER not in zf.namelist():
            raise FileNotFoundError(f"Missing {ROTMOD_MEMBER} in {ROTMOD_ZIP}")
        text = zf.read(ROTMOD_MEMBER).decode("utf-8")

    rows: list[dict[str, float]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        # Parse only source-side radius and gas contribution. The rotmod file
        # also contains observed velocities, but they are deliberately ignored.
        radius_kpc = float(parts[0])
        vgas_kms = float(parts[3])
        signed_vgas2 = math.copysign(vgas_kms * vgas_kms, vgas_kms)
        positive_vgas2 = max(signed_vgas2, 0.0)
        rows.append(
            {
                "galaxy": "NGC2841",
                "radius_kpc": radius_kpc,
                "vgas_kms_source_signed": vgas_kms,
                "vgas2_signed_km2s2": signed_vgas2,
                "vgas2_positive_load_proxy_km2s2": positive_vgas2,
                "outer_capacity_window_ge_30kpc": "yes" if radius_kpc >= 30.0 else "no",
            }
        )
    if not rows:
        raise ValueError(f"No data rows parsed from {ROTMOD_MEMBER}")
    frame = pd.DataFrame(rows)
    outer = frame[frame["outer_capacity_window_ge_30kpc"].eq("yes")]
    if outer.empty:
        raise ValueError("No outer R>=30 kpc rows found in NGC2841 gas profile")
    max_outer = float(outer["vgas2_positive_load_proxy_km2s2"].max())
    if max_outer <= 0:
        raise ValueError("Outer gas proxy is non-positive everywhere")
    frame["outer_hi_shape_kernel"] = 0.0
    outer_mask = frame["outer_capacity_window_ge_30kpc"].eq("yes")
    frame.loc[outer_mask, "outer_hi_shape_kernel"] = (
        frame.loc[outer_mask, "vgas2_positive_load_proxy_km2s2"] / max_outer
    )
    frame["source_reference"] = "SPARC_Lelli2016c_Rotmod_LTG;deBlok2008THINGS"
    frame["source_url"] = "https://astroweb.case.edu/SPARC/"
    frame["source_member"] = ROTMOD_MEMBER
    frame["source_component"] = "Vgas"
    frame["component_semantics"] = (
        "SPARC gas contribution derived for Newtonian mass models; used here only as "
        "a source-derived HI/gas load proxy and outer shape kernel"
    )
    frame["uses_vobs_or_residual"] = "no"
    frame["ignored_endpoint_columns_present_in_source_file"] = "Vobs;errV"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["positive_dark_residual_load_ready"] = "no"
    frame["gas_load_proxy_freeze_ready"] = "yes"
    frame["claim_boundary"] = CLAIM_BOUNDARY
    return frame


def build_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    frame = _read_rotmod_gas_profile()
    required = json.loads(REQUIRED_SCALE.read_text(encoding="utf-8"))
    outer = frame[frame["outer_capacity_window_ge_30kpc"].eq("yes")]
    max_outer_vgas2 = float(outer["vgas2_positive_load_proxy_km2s2"].max())
    median_outer_vgas2 = float(outer["vgas2_positive_load_proxy_km2s2"].median())
    required_outer_gap = float(required["outer_zone_median_positive_v2_gap_after_ceiling_control"])
    summary = {
        "n_rows": int(len(frame)),
        "n_outer_rows_ge_30kpc": int(len(outer)),
        "galaxies": ["NGC2841"],
        "source_archive": str(ROTMOD_ZIP.relative_to(ROOT)),
        "source_member": ROTMOD_MEMBER,
        "source_reference": "SPARC_Lelli2016c_Rotmod_LTG;deBlok2008THINGS",
        "source_url": "https://astroweb.case.edu/SPARC/",
        "gas_load_proxy_freeze_ready": True,
        "positive_dark_residual_load_ready": False,
        "endpoint_ready": False,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "positive_dark_residual_load_ready_counts": frame[
            "positive_dark_residual_load_ready"
        ].value_counts().to_dict(),
        "gas_load_proxy_freeze_ready_counts": frame["gas_load_proxy_freeze_ready"].value_counts().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "outer_max_vgas_kms": float(outer["vgas_kms_source_signed"].max()),
        "outer_max_vgas2_positive_load_proxy_km2s2": max_outer_vgas2,
        "outer_median_vgas2_positive_load_proxy_km2s2": median_outer_vgas2,
        "outer_median_required_positive_v2_gap_after_ceiling_km2s2": required_outer_gap,
        "outer_median_gas_proxy_fraction_of_required_gap": median_outer_vgas2 / required_outer_gap,
        "outer_max_gas_proxy_fraction_of_required_gap": max_outer_vgas2 / required_outer_gap,
        "frozen_kernel": "outer_hi_shape_kernel=max(Vgas^2,0)/max_outer(max(Vgas^2,0)) for R>=30kpc, else 0",
        "ignored_endpoint_columns_present_in_source_file": ["Vobs", "errV"],
        "forbidden_endpoint_inputs": FORBIDDEN_ENDPOINT_INPUTS,
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The SPARC/THINGS NGC2841 gas contribution supplies a reproducible "
            "source-derived radial HI/gas load proxy and an outer HI shape kernel. "
            "Its outer amplitude is only a small fraction of the required positive "
            "outer-capacity yardstick, so it is frozen as a gas-load proxy/control, "
            "not as the missing positive dark-residual load."
        ),
        "next_allowed_action": (
            "Use this frozen gas proxy as the lower-bound HI/gas shape component while "
            "searching for a source-native halo-capacity or extended-HI surface-density "
            "conversion. Do not score a new positive-load endpoint from this proxy alone."
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_freeze()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "radius_kpc",
                "vgas_kms_source_signed",
                "vgas2_positive_load_proxy_km2s2",
                "outer_hi_shape_kernel",
            ]
        ].tail(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
