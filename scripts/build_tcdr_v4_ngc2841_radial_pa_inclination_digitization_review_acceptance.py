from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
REVIEW_DIR = ROOT / "data" / "reviewer_responses"

FILLED_ZIP = (
    Path.home()
    / "Downloads"
    / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package_FILLED_v0_1.zip"
)
PACKAGE_SUBDIR = "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package_v0_1"
RESPONSE_NAME = "review_response_template.csv"

OUT_RESPONSE = REVIEW_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_response_v0_1.csv"
OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_radial_pa_inclination_digitization_review_acceptance_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_response() -> Path:
    if not FILLED_ZIP.exists():
        raise FileNotFoundError(f"Filled review zip not found: {FILLED_ZIP}")
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    member = f"{PACKAGE_SUBDIR}/{RESPONSE_NAME}"
    with zipfile.ZipFile(FILLED_ZIP) as archive:
        names = set(archive.namelist())
        if member not in names:
            raise FileNotFoundError(f"{member} not found in {FILLED_ZIP}")
        with archive.open(member) as source, OUT_RESPONSE.open("wb") as target:
            shutil.copyfileobj(source, target)
    return OUT_RESPONSE


def build_acceptance() -> tuple[pd.DataFrame, dict[str, object]]:
    response_path = _extract_response()
    frame = pd.read_csv(response_path)

    required_columns = {
        "galaxy",
        "radius_kpc",
        "position_angle_deg",
        "inclination_deg",
        "quality_flag",
        "forbidden_inputs_acknowledged",
        "uses_rotation_velocity_panel_c",
        "uses_surface_density_panel_d",
        "uses_endpoint_rotation_curve_or_residual",
    }
    missing = sorted(required_columns.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required response columns: {missing}")

    for col in ["radius_kpc", "position_angle_deg", "inclination_deg"]:
        frame[col] = pd.to_numeric(frame[col], errors="raise")

    bool_cols = [
        "forbidden_inputs_acknowledged",
        "uses_rotation_velocity_panel_c",
        "uses_surface_density_panel_d",
        "uses_endpoint_rotation_curve_or_residual",
    ]
    normalized = {col: frame[col].astype(str).str.strip().str.lower() for col in bool_cols}
    leakage_free = (
        (normalized["forbidden_inputs_acknowledged"] == "true").all()
        and (normalized["uses_rotation_velocity_panel_c"] == "false").all()
        and (normalized["uses_surface_density_panel_d"] == "false").all()
        and (normalized["uses_endpoint_rotation_curve_or_residual"] == "false").all()
    )

    monotonic_radius = bool(frame["radius_kpc"].is_monotonic_increasing)
    radius_unique = bool(frame["radius_kpc"].is_unique)
    range_ok = (
        frame["position_angle_deg"].between(120.0, 190.0).all()
        and frame["inclination_deg"].between(40.0, 90.0).all()
    )
    enough_points = len(frame) >= 10

    pa_delta = float(frame["position_angle_deg"].iloc[-1] - frame["position_angle_deg"].iloc[0])
    inc_delta = float(frame["inclination_deg"].iloc[-1] - frame["inclination_deg"].iloc[0])
    pa_span = float(frame["position_angle_deg"].max() - frame["position_angle_deg"].min())
    inc_span = float(frame["inclination_deg"].max() - frame["inclination_deg"].min())
    outer_rows = frame[frame["radius_kpc"] >= 20.0]
    inner_rows = frame[frame["radius_kpc"] <= 10.0]
    outer_pa_mean = float(outer_rows["position_angle_deg"].mean())
    outer_i_mean = float(outer_rows["inclination_deg"].mean())
    inner_pa_mean = float(inner_rows["position_angle_deg"].mean())
    inner_i_mean = float(inner_rows["inclination_deg"].mean())

    status = (
        "accepted_caveated_source_side_digitized_radial_pa_inclination_profile"
        if leakage_free and monotonic_radius and radius_unique and range_ok and enough_points
        else "blocked_failed_source_side_digitization_acceptance"
    )

    accepted = frame.copy()
    accepted["source_reference"] = "Bosma1981NGC2841HI"
    accepted["source_panels_used"] = "Bosma_Fig7a_position_angle;Bosma_Fig7b_inclination"
    accepted["source_panels_forbidden"] = "Bosma_Fig7c_rotation_velocity;Bosma_Fig7d_surface_density"
    accepted["profile_status"] = status
    accepted["formula_use_permission"] = (
        "caveated_source_side_profile_for_formula_freeze_review_no_endpoint"
        if status.startswith("accepted")
        else "blocked_no_formula_freeze"
    )
    accepted["endpoint_replay_permission"] = "no"
    accepted["kernel_promotion_permission"] = "no"
    accepted["new_route_scoring_permission"] = "no"
    accepted["uses_vobs_or_residual"] = "no"
    accepted["endpoint_data_policy"] = ENDPOINT_POLICY
    accepted["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(accepted)),
        "galaxies": sorted(accepted["galaxy"].unique().tolist()),
        "filled_zip": str(FILLED_ZIP),
        "filled_zip_sha256": _sha256(FILLED_ZIP),
        "response_csv": str(response_path.relative_to(ROOT)),
        "response_csv_sha256": _sha256(response_path),
        "leakage_free": bool(leakage_free),
        "monotonic_radius": monotonic_radius,
        "radius_unique": radius_unique,
        "range_ok": bool(range_ok),
        "enough_points": enough_points,
        "quality_flag_counts": accepted["quality_flag"].value_counts().to_dict(),
        "radius_range_kpc": [
            float(accepted["radius_kpc"].min()),
            float(accepted["radius_kpc"].max()),
        ],
        "position_angle_range_deg": [
            float(accepted["position_angle_deg"].min()),
            float(accepted["position_angle_deg"].max()),
        ],
        "inclination_range_deg": [
            float(accepted["inclination_deg"].min()),
            float(accepted["inclination_deg"].max()),
        ],
        "position_angle_delta_outer_minus_inner_deg": pa_delta,
        "inclination_delta_outer_minus_inner_deg": inc_delta,
        "position_angle_span_deg": pa_span,
        "inclination_span_deg": inc_span,
        "inner_mean_position_angle_deg_r_le_10": inner_pa_mean,
        "inner_mean_inclination_deg_r_le_10": inner_i_mean,
        "outer_mean_position_angle_deg_r_ge_20": outer_pa_mean,
        "outer_mean_inclination_deg_r_ge_20": outer_i_mean,
        "profile_status": status,
        "formula_ready": False,
        "formula_freeze_review_ready": status.startswith("accepted"),
        "endpoint_replay_permission_counts": accepted["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": accepted["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": accepted["new_route_scoring_permission"].value_counts().to_dict(),
        "forbidden_endpoint_inputs_used_counts": accepted["uses_vobs_or_residual"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The filled reviewer response is leakage-clean and supplies a caveated "
            "source-side digitized radial PA/inclination profile for NGC2841 from "
            "Bosma Figure 7 panels a and b only. It can support a later formula-freeze "
            "review, but it is not a formula freeze and does not authorize endpoint scoring."
            if status.startswith("accepted")
            else "The filled reviewer response failed one or more source-side acceptance checks."
        ),
        "next_allowed_action": (
            "Build a geometry-profile formula-freeze review that uses this profile as a "
            "caveated source-side input, checks dimensions/limits, and still keeps endpoint "
            "scoring closed until formula ingredients are frozen."
            if status.startswith("accepted")
            else "Request a corrected independent source-side digitization response."
        ),
    }
    return accepted, summary


def main() -> None:
    accepted, summary = build_acceptance()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    accepted.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_RESPONSE}")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        accepted[
            [
                "radius_kpc",
                "position_angle_deg",
                "inclination_deg",
                "profile_status",
                "formula_use_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
