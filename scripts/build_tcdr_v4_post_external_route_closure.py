from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

ROUTE_CLOSURE = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_route_closure_local.csv"
SOURCE_GAP_AUDIT = EXTERNAL_DIR / "tcdr_v4_source_gap_external_literature_audit_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_post_external_route_closure_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_post_external_route_closure_summary_local.json"

CLAIM_BOUNDARY = "post_external_route_closure_local_diagnostic_not_validation"


def _post_external_status(row: pd.Series) -> dict[str, str]:
    final_status = str(row["final_route_status"])
    final_permission = str(row["final_endpoint_replay_permission"])
    external_permission = str(row.get("external_literature_route_permission", ""))

    if final_status == "SOURCE_GAP_STILL_BLOCKED":
        if external_permission == "keep_source_gap_blocked":
            return {
                "post_external_route_status": "SOURCE_GAP_BLOCKED_AFTER_EXTERNAL_AUDIT",
                "post_external_endpoint_replay_permission": "no",
                "post_external_reason": (
                    "External source/literature audit did not provide independent "
                    "spiral, projection, or history support."
                ),
            }
        return {
            "post_external_route_status": "SOURCE_GAP_REQUIRES_NEW_REVIEW",
            "post_external_endpoint_replay_permission": "no",
            "post_external_reason": (
                "External source/literature entry is not route permission; a separate "
                "source-review and null-control step would still be required."
            ),
        }

    return {
        "post_external_route_status": final_status,
        "post_external_endpoint_replay_permission": final_permission,
        "post_external_reason": str(row["final_reason"]),
    }


def build_post_external_closure() -> tuple[pd.DataFrame, dict[str, object]]:
    closure = pd.read_csv(ROUTE_CLOSURE)
    audit = pd.read_csv(
        SOURCE_GAP_AUDIT,
        usecols=[
            "support_safe_pool",
            "galaxy",
            "external_source_status",
            "external_literature_route_permission",
            "source_caveat",
            "reference_key",
        ],
    )
    merged = closure.merge(audit, on=["support_safe_pool", "galaxy"], how="left")
    post = merged.apply(_post_external_status, axis=1, result_type="expand")
    merged = pd.concat([merged, post], axis=1)
    merged["post_external_claim_boundary"] = CLAIM_BOUNDARY

    allowed = merged[
        merged["post_external_endpoint_replay_permission"].str.startswith("yes")
    ]
    blocked = merged[~merged.index.isin(allowed.index)]
    summary = {
        "n_rows": int(len(merged)),
        "post_external_route_status_counts": merged[
            "post_external_route_status"
        ].value_counts().to_dict(),
        "post_external_endpoint_replay_permission_counts": merged[
            "post_external_endpoint_replay_permission"
        ].value_counts().to_dict(),
        "allowed_rows": int(len(allowed)),
        "allowed_unique_galaxies": sorted(allowed["galaxy"].unique().tolist()),
        "blocked_rows": int(len(blocked)),
        "source_gap_external_route_permission_counts": merged[
            "external_literature_route_permission"
        ]
        .fillna("not_applicable")
        .value_counts()
        .to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The post-external route closure keeps the same six current-formula "
            "rows replay-ready and leaves all source-gap rows blocked. External "
            "literature/source lookup did not create a new endpoint route."
        ),
    }
    return merged.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    closure, summary = build_post_external_closure()
    closure.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "post_external_route_status",
        "post_external_endpoint_replay_permission",
        "external_source_status",
        "post_external_reason",
    ]
    print(closure[cols].to_string(index=False))


if __name__ == "__main__":
    main()
