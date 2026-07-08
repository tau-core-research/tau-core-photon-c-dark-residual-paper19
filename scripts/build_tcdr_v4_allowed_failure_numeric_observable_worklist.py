from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

READINESS = EXTERNAL_DIR / "tcdr_v4_allowed_failure_formula_freeze_readiness_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_allowed_failure_numeric_observable_worklist_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_failure_numeric_observable_worklist_summary_local.json"

CLAIM_BOUNDARY = "allowed_failure_numeric_observable_worklist_not_formula_freeze_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


NUMERIC_REQUESTS = [
    {
        "galaxy": "NGC2841",
        "requested_observable": "spiral_inner_kpc_source",
        "observable_role": "spiral_path_formula_domain",
        "priority": "P1_REQUIRED_FOR_SPIRAL_PATH_FORMULA_FREEZE",
        "accepted_source_types": "source-native image decomposition;published arm-segment radius;catalogue spiral-geometry measurement",
        "why_needed": "sets the inner radial support of a possible spiral/path kernel without using rotation residuals",
    },
    {
        "galaxy": "NGC2841",
        "requested_observable": "spiral_outer_kpc_source",
        "observable_role": "spiral_path_formula_domain",
        "priority": "P1_REQUIRED_FOR_SPIRAL_PATH_FORMULA_FREEZE",
        "accepted_source_types": "source-native image decomposition;published arm-segment radius;catalogue spiral-geometry measurement",
        "why_needed": "sets the outer radial support of a possible spiral/path kernel without using rotation residuals",
    },
    {
        "galaxy": "NGC2841",
        "requested_observable": "spiral_pitch_median_abs_deg_source",
        "observable_role": "spiral_path_kernel_shape",
        "priority": "P1_REQUIRED_FOR_SPIRAL_PATH_FORMULA_FREEZE",
        "accepted_source_types": "published pitch-angle measurement;source-native spiral fit;catalogue pitch-angle proxy",
        "why_needed": "turns qualitative flocculent spiral evidence into a frozen shape parameter",
    },
    {
        "galaxy": "NGC2841",
        "requested_observable": "warp_onset_or_path_environment_numeric_source",
        "observable_role": "path_history_projection_support",
        "priority": "P1_REQUIRED_FOR_SPIRAL_PATH_FORMULA_FREEZE",
        "accepted_source_types": "published warp onset radius;outer-disk profile break;source-native path/environment coordinate",
        "why_needed": "turns qualitative outer-warp evidence into a bounded path/history support coordinate",
    },
    {
        "galaxy": "UGC00191",
        "requested_observable": "route_closing_spiral_geometry_or_path_history_source",
        "observable_role": "pre_formula_review_blocker",
        "priority": "P2_REQUIRED_BEFORE_FORMULA_FREEZE_REVIEW_CAN_OPEN",
        "accepted_source_types": "source-native spiral geometry;published path/history evidence;non-tentative asymmetry geometry",
        "why_needed": "the current tentative asymmetry label is not enough to open a spiral/path formula-freeze review",
    },
]


def build_worklist() -> tuple[pd.DataFrame, dict[str, object]]:
    readiness = pd.read_csv(READINESS)
    readiness_by_galaxy = readiness.set_index("galaxy")

    rows: list[dict[str, object]] = []
    for request in NUMERIC_REQUESTS:
        galaxy = request["galaxy"]
        ready = readiness_by_galaxy.loc[galaxy]
        rows.append(
            {
                **request,
                "formula_freeze_readiness_status": ready["formula_freeze_readiness_status"],
                "source_side_route_review_permission": ready["source_side_route_review_permission"],
                "forbidden_inputs": "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    out = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(out)),
        "galaxies": sorted(out["galaxy"].unique().tolist()),
        "rows_by_galaxy": out["galaxy"].value_counts().sort_index().to_dict(),
        "priority_counts": out["priority"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": out["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": out["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": out["new_route_scoring_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The numeric-observable worklist converts the formula-freeze blocker into "
            "concrete residual-blind acquisition targets. NGC2841 needs four numeric "
            "spiral/path observables before a new formula can be frozen; UGC00191 needs "
            "route-closing source evidence before formula-freeze review can even open. "
            "No endpoint replay, kernel promotion, or new-route scoring is authorized."
        ),
    }
    return out, summary


def main() -> None:
    out, summary = build_worklist()
    out.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(out[["galaxy", "requested_observable", "priority"]].to_string(index=False))


if __name__ == "__main__":
    main()
