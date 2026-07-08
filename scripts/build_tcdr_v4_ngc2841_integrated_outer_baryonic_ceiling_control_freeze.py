from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"

LOAD_SEARCH_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_search_summary_v0_1.json"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_v0_1.csv"
OUT_JSON = (
    SOURCE_DIR / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_integrated_outer_baryonic_ceiling_control_freeze_not_endpoint"
CONTROL_ID = "C_NGC2841_DRAGONFLY_INTEGRATED_OUTER_BARYONIC_CEILING_V0_1"
G_KPC_KMS2_PER_MSUN = 4.30091e-6
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_lambda_fit;observed_velocity_gap"
)


def _load_summary() -> dict[str, object]:
    return json.loads(LOAD_SEARCH_SUMMARY.read_text(encoding="utf-8"))


def build_control_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    source = _load_summary()
    if source.get("promoted_load_source_ready") is not False:
        raise ValueError("This control freeze requires the source search to keep load promotion blocked.")

    m_star = float(source["outer_stellar_mass_msun"])
    m_gas = float(source["outer_gas_mass_from_3to1_msun"])
    m_baryon = float(source["outer_baryonic_mass_from_3to1_msun"])
    if m_baryon <= 0:
        raise ValueError("Outer baryonic mass ceiling must be positive.")

    radii = [20.0, 30.0, 40.0, 50.0, 63.64, 70.0]
    rows = []
    for radius in radii:
        active = radius >= 30.0
        v2 = G_KPC_KMS2_PER_MSUN * m_baryon / radius if active else 0.0
        rows.append(
            {
                "galaxy": "NGC2841",
                "control_id": CONTROL_ID,
                "radius_kpc": radius,
                "active_outer_window": "yes" if active else "no",
                "outer_window_rule": "active_only_for_R_ge_30kpc_from_Zhang_outer_disk_statement",
                "m_star_outer_msun": m_star,
                "m_gas_outer_from_3to1_msun": m_gas,
                "m_baryon_outer_msun": m_baryon,
                "v2_ceiling_km2s2": v2,
                "formula": "Delta_v2_ceiling(R)=G*M_outer_baryon/R for R>=30 kpc else 0",
                "dimension_check": "pass_G_M_over_R_has_velocity_squared_units",
                "source_basis": (
                    "Zhang2018 outer stellar mass beyond about 30 kpc plus reported "
                    "outer stellar-to-gas surface-density ratio about 3:1"
                ),
                "allowed_use": "non_endpoint_baryonic_ceiling_control",
                "blocked_use": "positive_dark_residual_load_or_endpoint_amplitude_rescue",
            }
        )

    frame = pd.DataFrame(rows)
    frame["control_freeze_status"] = "frozen_non_endpoint_baryonic_ceiling_control"
    frame["formula_ready_as_dark_residual_load"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["diagnostic_replay_permission"] = "separate_authorization_required"
    frame["kernel_promotion_permission"] = "no"
    frame["new_route_scoring_permission"] = "no"
    frame["uses_vobs_or_residual"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["claim_boundary"] = CLAIM_BOUNDARY

    active_frame = frame[frame["active_outer_window"].eq("yes")]
    summary = {
        "n_rows": int(len(frame)),
        "galaxies": ["NGC2841"],
        "control_id": CONTROL_ID,
        "control_freeze_ready": True,
        "positive_dark_residual_load_ready": False,
        "endpoint_ready": False,
        "outer_stellar_mass_msun": m_star,
        "outer_gas_mass_from_3to1_msun": m_gas,
        "outer_baryonic_mass_from_3to1_msun": m_baryon,
        "active_radius_min_kpc": float(active_frame["radius_kpc"].min()),
        "v2_ceiling_30kpc_km2s2": float(
            frame.loc[frame["radius_kpc"].eq(30.0), "v2_ceiling_km2s2"].iloc[0]
        ),
        "v2_ceiling_50kpc_km2s2": float(
            frame.loc[frame["radius_kpc"].eq(50.0), "v2_ceiling_km2s2"].iloc[0]
        ),
        "v2_ceiling_70kpc_km2s2": float(
            frame.loc[frame["radius_kpc"].eq(70.0), "v2_ceiling_km2s2"].iloc[0]
        ),
        "endpoint_replay_permission_counts": (
            frame["endpoint_replay_permission"].value_counts().sort_index().to_dict()
        ),
        "kernel_promotion_permission_counts": (
            frame["kernel_promotion_permission"].value_counts().sort_index().to_dict()
        ),
        "new_route_scoring_permission_counts": (
            frame["new_route_scoring_permission"].value_counts().sort_index().to_dict()
        ),
        "uses_vobs_or_residual_counts": (
            frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict()
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The integrated Dragonfly outer baryonic mass can be frozen as a "
            "non-endpoint velocity-squared ceiling control. It is physically "
            "dimensioned, but it is too conservative to be promoted as a positive "
            "dark-residual load and grants no endpoint replay permission."
        ),
        "next_allowed_action": (
            "Optionally run a diagnostic-only ceiling replay that reads this frozen "
            "control unchanged; do not promote it as the missing NGC2841 load."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_control_freeze()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(frame[["radius_kpc", "active_outer_window", "v2_ceiling_km2s2"]].to_string(index=False))


if __name__ == "__main__":
    main()
