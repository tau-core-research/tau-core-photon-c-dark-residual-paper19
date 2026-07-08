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

REVIEW_ACCEPTANCE_SUMMARY = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json"
)
K_BETA_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_summary_v0_1.json"
)
ROTMOD_ZIP = PREFLIGHT_DIR / "Rotmod_LTG.zip"
ROTMOD_MEMBER = "NGC2841_rotmod.dat"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_v0_1.csv"
OUT_JSON = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_beta_closure_baryonic_carrier_freeze_review_not_scoring"
CARRIER_ID = "V2_CARRIER_NGC2841_SPARC_FIXED_ML_BARYONIC_V0_1"
CARRIER_POLICY = "fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_endpoint_fit"
CARRIER_EXPRESSION = (
    "v_carrier^2(R)=sign(Vgas)Vgas^2 + 0.5*Vdisk^2 + 0.7*Vbul^2"
)
ENDPOINT_POLICY = "source_component_carrier_freeze_only_ignore_vobs_errv_endpoint_scores_and_residuals"
FORBIDDEN_INPUTS = (
    "Vobs;errV;rotation_curve;rotation_residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _read_rotmod_components() -> pd.DataFrame:
    if not ROTMOD_ZIP.exists():
        raise FileNotFoundError(f"Missing SPARC Rotmod archive: {ROTMOD_ZIP}")
    with zipfile.ZipFile(ROTMOD_ZIP) as zf:
        if ROTMOD_MEMBER not in zf.namelist():
            raise FileNotFoundError(f"Missing {ROTMOD_MEMBER} in {ROTMOD_ZIP}")
        text = zf.read(ROTMOD_MEMBER).decode("utf-8")

    rows: list[dict[str, float | str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        # Deliberately parse only radius and source-side baryonic components.
        # The same file contains Vobs and errV, but those endpoint columns are
        # forbidden for this carrier-freeze review.
        radius_kpc = float(parts[0])
        vgas = float(parts[3])
        vdisk = float(parts[4])
        vbul = float(parts[5])
        signed_gas_v2 = math.copysign(vgas * vgas, vgas)
        disk_v2 = 0.5 * vdisk * vdisk
        bulge_v2 = 0.7 * vbul * vbul
        carrier_v2 = signed_gas_v2 + disk_v2 + bulge_v2
        rows.append(
            {
                "galaxy": "NGC2841",
                "radius_kpc": radius_kpc,
                "vgas_kms_source_signed": vgas,
                "vdisk_kms_source": vdisk,
                "vbul_kms_source": vbul,
                "vgas2_signed_km2s2": signed_gas_v2,
                "disk_component_v2_fixed_ml_km2s2": disk_v2,
                "bulge_component_v2_fixed_ml_km2s2": bulge_v2,
                "v_carrier2_fixed_ml_km2s2": carrier_v2,
                "v_carrier_fixed_ml_kms": math.sqrt(carrier_v2) if carrier_v2 > 0 else 0.0,
            }
        )
    if not rows:
        raise ValueError(f"No component rows parsed from {ROTMOD_MEMBER}")
    return pd.DataFrame(rows)


def build_carrier_freeze_review() -> tuple[pd.DataFrame, dict[str, object]]:
    review = _load_json(REVIEW_ACCEPTANCE_SUMMARY)
    k_beta = _load_json(K_BETA_SUMMARY)
    if review.get("review_response_accepted") is not True:
        raise ValueError("Beta/closure reviewer response has not been accepted.")
    if review.get("carrier_status") != "blocked_requires_new_source_frozen_carrier":
        raise ValueError("Unexpected carrier status; this builder resolves only the carrier blocker.")
    if k_beta.get("K_beta_profile_ready_for_formula_freeze_review") is not True:
        raise ValueError("K_beta profile must be frozen before carrier formula review.")

    frame = _read_rotmod_components().sort_values("radius_kpc").reset_index(drop=True)
    if (frame["v_carrier2_fixed_ml_km2s2"] <= 0).any():
        raise ValueError("Carrier velocity-squared field is not strictly positive everywhere.")

    frame["source_archive"] = str(ROTMOD_ZIP.relative_to(ROOT))
    frame["source_member"] = ROTMOD_MEMBER
    frame["source_reference"] = "SPARC_Lelli2016c_Rotmod_LTG"
    frame["source_url"] = "https://astroweb.case.edu/SPARC/"
    frame["carrier_id"] = CARRIER_ID
    frame["carrier_policy"] = CARRIER_POLICY
    frame["carrier_expression"] = CARRIER_EXPRESSION
    frame["carrier_status"] = "baryonic_carrier_ready_for_beta_formula_freeze_review_no_scoring"
    frame["carrier_role"] = "velocity_squared_carrier_only_no_beta_amplitude_no_endpoint_fit"
    frame["ignored_endpoint_columns_present_in_source_file"] = "Vobs;errV"
    frame["uses_vobs_or_residual"] = "no"
    frame["source_profile_leakage_free"] = "yes"
    frame["resolved_blocker_id"] = "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE"
    frame["remaining_blockers"] = "BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE"
    frame["formula_freeze_ready"] = "no"
    frame["endpoint_ready"] = "no"
    frame["kernel_promotion_ready"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["formula_freeze_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "carrier_id": CARRIER_ID,
        "carrier_policy": CARRIER_POLICY,
        "carrier_expression": CARRIER_EXPRESSION,
        "source_archive": str(ROTMOD_ZIP.relative_to(ROOT)),
        "source_member": ROTMOD_MEMBER,
        "source_reference": "SPARC_Lelli2016c_Rotmod_LTG",
        "ignored_endpoint_columns_present_in_source_file": ["Vobs", "errV"],
        "dimension_check": "pass_velocity_squared_from_sparc_component_velocities",
        "carrier_min_v2_km2s2": float(frame["v_carrier2_fixed_ml_km2s2"].min()),
        "carrier_max_v2_km2s2": float(frame["v_carrier2_fixed_ml_km2s2"].max()),
        "carrier_outer_median_v2_ge_30kpc_km2s2": float(
            frame.loc[frame["radius_kpc"] >= 30.0, "v_carrier2_fixed_ml_km2s2"].median()
        ),
        "carrier_ready_for_beta_formula_freeze_review": True,
        "carrier_promoted_as_physical_baseline": False,
        "source_profile_leakage_free": True,
        "resolved_blocker_id": "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE",
        "resolved_blocker_status": "resolved_as_fixed_mlr_baryonic_velocity_squared_carrier",
        "remaining_blockers": ["BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE"],
        "full_formula_freeze_ready": False,
        "formula_freeze_ready": False,
        "endpoint_ready": False,
        "kernel_promotion_ready": False,
        "endpoint_replay_allowed": False,
        "new_route_scoring_allowed": False,
        "permission_counts": {
            "endpoint_replay_permission": (
                frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
            ),
            "formula_freeze_permission": (
                frame["formula_freeze_permission"].value_counts().sort_index().to_dict()
            ),
            "kernel_promotion_permission": (
                frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
            ),
            "new_route_scoring_permission": (
                frame["new_route_scoring_permission"].value_counts().sort_index().to_dict()
            ),
            "uses_vobs_or_residual": (
                frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
            ),
        },
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The SPARC rotmod baryonic components support a fixed-M/L velocity-squared "
            "carrier for beta/closure formula-freeze review. This is a carrier field, "
            "not a fitted endpoint baseline, and it does not freeze beta/spin amplitude."
        ),
        "next_allowed_action": (
            "Resolve the spin-normalization blocker or explicitly keep beta_cl as "
            "context-only before any endpoint replay."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_carrier_freeze_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "radius_kpc",
                "v_carrier2_fixed_ml_km2s2",
                "v_carrier_fixed_ml_kms",
                "carrier_status",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
