from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

DIAGNOSTIC = EXTERNAL_DIR / "tcdr_v4_allowed_best_wrong_failure_diagnostic_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_allowed_failure_source_acquisition_worklist_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_failure_source_acquisition_worklist_summary_local.json"

CLAIM_BOUNDARY = "allowed_failure_source_acquisition_worklist_not_replay_permission"


def _evidence_request(component: str) -> str:
    if component == "spiral":
        return (
            "independent source-native spiral geometry or path/history support: "
            "pitch angle, arm segment/radial extent, spiral asymmetry, warp/path token, "
            "or literature-backed non-axisymmetric disk support not inferred from rotation residuals"
        )
    if component == "ring":
        return (
            "independent source-native ring/resonance support: ring radius, resonance label, "
            "feature-catalogue ring token, or literature-backed radial feature not inferred from endpoint scores"
        )
    if component == "bar":
        return (
            "independent source-native bar support: bar radius, position angle, strength proxy, "
            "feature-catalogue bar token, or literature-backed bar evidence not inferred from endpoint scores"
        )
    return "independent residual-blind source support for the competitive component"


def _priority(row: pd.Series) -> str:
    cls = str(row["allowed_best_wrong_diagnostic_class"])
    if cls.startswith("METRIC_SENSITIVE"):
        return "P1_METRIC_SENSITIVE_SOURCE_REVIEW"
    if cls.startswith("NEAR_TIE"):
        return "P2_NEAR_TIE_SOURCE_REVIEW"
    return "P3_CONTROL_PRESSURE_REVIEW"


def build_worklist() -> tuple[pd.DataFrame, dict[str, object]]:
    diagnostic = pd.read_csv(DIAGNOSTIC)
    failures = diagnostic[
        diagnostic["candidate_beats_best_wrong_component"] != "yes"
    ].copy()
    failures["requested_source_evidence"] = failures["best_wrong_component"].map(
        _evidence_request
    )
    failures["source_acquisition_priority"] = failures.apply(_priority, axis=1)
    failures["endpoint_replay_permission"] = "no"
    failures["kernel_promotion_permission"] = "no"
    failures["required_promotion_condition"] = (
        "route may reopen only after independent residual-blind source evidence "
        "supports the competitive component and a separate source-review artifact "
        "promotes it before endpoint scoring"
    )
    failures["worklist_claim_boundary"] = CLAIM_BOUNDARY

    keep_cols = [
        "support_safe_pool",
        "galaxy",
        "matched_component",
        "source_family_candidate",
        "source_positive_components",
        "best_wrong_component",
        "best_wrong_source_component_weight",
        "best_wrong_source_visible",
        "allowed_best_wrong_diagnostic_class",
        "source_acquisition_priority",
        "requested_source_evidence",
        "endpoint_replay_permission",
        "kernel_promotion_permission",
        "required_promotion_condition",
        "worklist_claim_boundary",
    ]
    worklist = failures[keep_cols].sort_values(
        ["source_acquisition_priority", "galaxy", "support_safe_pool"]
    )
    summary = {
        "n_rows": int(len(worklist)),
        "n_unique_galaxies": int(worklist["galaxy"].nunique()),
        "unique_galaxies": sorted(worklist["galaxy"].unique().tolist()),
        "priority_counts": worklist["source_acquisition_priority"].value_counts().to_dict(),
        "best_wrong_component_counts": worklist["best_wrong_component"].value_counts().to_dict(),
        "all_endpoint_replay_permission": sorted(
            worklist["endpoint_replay_permission"].unique().tolist()
        ),
        "all_kernel_promotion_permission": sorted(
            worklist["kernel_promotion_permission"].unique().tolist()
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The allowed-row strict best-wrong failures are converted into a "
            "source-acquisition worklist, not replay permission. NGC2841 and "
            "UGC00191 require independent residual-blind spiral/path/history "
            "evidence before any spiral-route reopening can be considered."
        ),
    }
    return worklist, summary


def main() -> None:
    worklist, summary = build_worklist()
    worklist.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        worklist[
            [
                "support_safe_pool",
                "galaxy",
                "best_wrong_component",
                "source_acquisition_priority",
                "endpoint_replay_permission",
                "kernel_promotion_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
