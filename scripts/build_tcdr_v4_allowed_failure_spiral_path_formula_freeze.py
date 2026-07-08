from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

NUMERIC_FREEZE = SOURCE_DIR / "tcdr_v4_allowed_failure_numeric_source_freeze_v0_1.csv"
READINESS = EXTERNAL_DIR / "tcdr_v4_allowed_failure_formula_freeze_readiness_local.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_summary_v0_1.json"

CLAIM_BOUNDARY = "allowed_failure_spiral_path_formula_freeze_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORMULA_ID = "F_CAVEATED_SPIRAL_PATH_WINDOW_SOURCE_FROZEN"
FORMULA_EXPRESSION = (
    "K_sp(r)=0.5*(tanh((r-r_in)/sigma_edge)-tanh((r-r_out)/sigma_edge)); "
    "K_path(r)=1/(1+exp(-(r-r_path)/sigma_path)); "
    "K_total(r)=clip(K_sp(r)+epsilon_path*K_path(r),0,1)"
)
FORBIDDEN_INPUTS = "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank"


def _value(frame: pd.DataFrame, galaxy: str, observable: str) -> float | None:
    row = frame[
        (frame["galaxy"].astype(str) == galaxy)
        & (frame["requested_observable"].astype(str) == observable)
        & (frame["numeric_source_freeze_status"].astype(str) == "frozen_caveated_numeric_source")
    ]
    if row.empty:
        return None
    value = pd.to_numeric(row.iloc[0]["frozen_numeric_value"], errors="coerce")
    if pd.isna(value):
        return None
    return float(value)


def build_formula_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    numeric = pd.read_csv(NUMERIC_FREEZE)
    readiness = pd.read_csv(READINESS)
    rows: list[dict[str, object]] = []

    for readiness_row in readiness.to_dict(orient="records"):
        galaxy = str(readiness_row["galaxy"])
        if galaxy != "NGC2841":
            rows.append(
                {
                    "galaxy": galaxy,
                    "formula_id": "",
                    "formula_freeze_status": "not_frozen_route_review_blocked",
                    "formula_expression": "",
                    "r_in_kpc": "",
                    "r_out_kpc": "",
                    "pitch_abs_deg": "",
                    "r_path_kpc": "",
                    "sigma_edge_kpc": "",
                    "sigma_path_kpc": "",
                    "epsilon_path": "",
                    "dimension_check": "not_applicable",
                    "source_basis": "weak_asymmetry_only_no_route_closing_spiral_path_source",
                    "formula_freeze_permission": "no",
                    "endpoint_replay_permission": "no",
                    "kernel_promotion_permission": "no",
                    "new_route_scoring_permission": "no",
                    "forbidden_inputs": FORBIDDEN_INPUTS,
                    "endpoint_data_policy": ENDPOINT_POLICY,
                    "claim_boundary": CLAIM_BOUNDARY,
                    "verdict": (
                        "UGC00191 remains route-review blocked and receives no "
                        "spiral/path formula freeze."
                    ),
                }
            )
            continue

        required = {
            "r_in_kpc": _value(numeric, galaxy, "spiral_inner_kpc_source"),
            "r_out_kpc": _value(numeric, galaxy, "spiral_outer_kpc_source"),
            "pitch_abs_deg": _value(numeric, galaxy, "spiral_pitch_median_abs_deg_source"),
            "r_path_kpc": _value(numeric, galaxy, "warp_onset_or_path_environment_numeric_source"),
        }
        missing = [key for key, value in required.items() if value is None]
        if missing:
            rows.append(
                {
                    "galaxy": galaxy,
                    "formula_id": "",
                    "formula_freeze_status": "not_frozen_missing_numeric_source_fields",
                    "formula_expression": "",
                    "r_in_kpc": required["r_in_kpc"] or "",
                    "r_out_kpc": required["r_out_kpc"] or "",
                    "pitch_abs_deg": required["pitch_abs_deg"] or "",
                    "r_path_kpc": required["r_path_kpc"] or "",
                    "sigma_edge_kpc": "",
                    "sigma_path_kpc": "",
                    "epsilon_path": "",
                    "dimension_check": "fail_missing_" + ";".join(missing),
                    "source_basis": "numeric_source_freeze_incomplete",
                    "formula_freeze_permission": "no",
                    "endpoint_replay_permission": "no",
                    "kernel_promotion_permission": "no",
                    "new_route_scoring_permission": "no",
                    "forbidden_inputs": FORBIDDEN_INPUTS,
                    "endpoint_data_policy": ENDPOINT_POLICY,
                    "claim_boundary": CLAIM_BOUNDARY,
                    "verdict": "Formula freeze remains blocked because required numeric source fields are missing.",
                }
            )
            continue

        r_in = required["r_in_kpc"]
        r_out = required["r_out_kpc"]
        pitch = required["pitch_abs_deg"]
        r_path = required["r_path_kpc"]
        assert r_in is not None and r_out is not None and pitch is not None and r_path is not None

        span = r_out - r_in
        sigma_edge = max(0.15 * span, 0.5)
        sigma_path = max(0.2 * r_path, 1.0)
        epsilon_path = min(0.20, max(0.02, math.radians(pitch)))
        dimension_pass = r_in > 0 and r_out > r_in and r_path > r_out and sigma_edge > 0 and sigma_path > 0

        rows.append(
            {
                "galaxy": galaxy,
                "formula_id": FORMULA_ID,
                "formula_freeze_status": "frozen_caveated_source_formula_no_scoring",
                "formula_expression": FORMULA_EXPRESSION,
                "r_in_kpc": r_in,
                "r_out_kpc": r_out,
                "pitch_abs_deg": pitch,
                "r_path_kpc": r_path,
                "sigma_edge_kpc": sigma_edge,
                "sigma_path_kpc": sigma_path,
                "epsilon_path": epsilon_path,
                "dimension_check": "pass_positive_ordered_kpc_radii" if dimension_pass else "fail_dimension_order",
                "source_basis": (
                    "Kendall2011_R25_break_pitch_plus_Zhang2018_outer_warp_path_coordinate; "
                    "all caveated; no rotation endpoints used"
                ),
                "formula_freeze_permission": "yes_source_formula_frozen_no_scoring",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "forbidden_inputs": FORBIDDEN_INPUTS,
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
                "verdict": (
                    "NGC2841 receives a caveated source-frozen spiral/path formula shell. "
                    "This is a scoring-preparation artifact only; replay requires a separate "
                    "authorization and must use this frozen formula without endpoint tuning."
                ),
            }
        )

    out = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(out)),
        "galaxies": out["galaxy"].tolist(),
        "formula_freeze_status_counts": out["formula_freeze_status"].value_counts().sort_index().to_dict(),
        "formula_freeze_permission_counts": out["formula_freeze_permission"].value_counts().sort_index().to_dict(),
        "endpoint_replay_permission_counts": out["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": out["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": out["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "frozen_formula_ids": sorted(
            formula for formula in out["formula_id"].astype(str).unique().tolist() if formula
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "NGC2841 now has a caveated source-frozen spiral/path formula shell built from "
            "the four numeric source coordinates. UGC00191 remains blocked. The artifact "
            "prepares scoring but does not authorize endpoint replay, kernel promotion, or "
            "new-route scoring."
        ),
    }
    return out, summary


def main() -> None:
    out, summary = build_formula_freeze()
    out.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        out[
            [
                "galaxy",
                "formula_id",
                "formula_freeze_status",
                "formula_freeze_permission",
                "new_route_scoring_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
