from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

READINESS = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_readiness_ledger_local.csv"
MIXED_SHUFFLE = EXTERNAL_DIR / "tcdr_v4_support_safe_mixed_route_shuffle_control_local.csv"
KOBS_REVIEW = EXTERNAL_DIR / "tcdr_v4_kobs_kreadout_source_review_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_route_closure_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_route_closure_summary_local.json"

CLAIM_BOUNDARY = "paper8_paper9_scoring_route_closure_local_diagnostic_not_validation"


def _close_row(row: pd.Series) -> dict[str, str]:
    readiness_class = str(row["scoring_readiness_class"])
    mixed_permission = str(row.get("mixed_route_scoring_permission", ""))

    if readiness_class in {
        "READY_CURRENT_FORMULA_STRICT_SURVIVAL",
        "READY_CURRENT_FORMULA_NEAR_TIE_ROBUSTNESS_ONLY",
    }:
        return {
            "final_route_status": "CURRENT_FORMULA_REPLAY_READY",
            "final_endpoint_replay_permission": "yes_current_formula_only",
            "final_reason": "Route was already allowed by the Paper8/Paper9 readiness ledger.",
        }
    if readiness_class == "NOT_READY_MIXED_ROUTE_REQUIRES_NONOVERLAP":
        if mixed_permission == "ready_for_caveated_mixed_route_score":
            return {
                "final_route_status": "MIXED_ROUTE_CAVEATED_REPLAY_READY",
                "final_endpoint_replay_permission": "yes_caveated_mixed_route",
                "final_reason": "Mixed route passed source non-overlap and shuffled formula-package controls.",
            }
        return {
            "final_route_status": "MIXED_ROUTE_BLOCKED_BY_SHUFFLE_CONTROL",
            "final_endpoint_replay_permission": "no",
            "final_reason": "Source non-overlap may close, but shuffled formula-package control did not pass.",
        }
    if readiness_class == "NOT_READY_KOBS_KREADOUT_REVIEW_REQUIRED":
        if str(row.get("kobs_kreadout_replay_permission", "")) == (
            "yes_after_frozen_relabel_and_shuffle_control"
        ):
            return {
                "final_route_status": "KOBS_KREADOUT_RELABEL_CAVEATED_REPLAY_READY",
                "final_endpoint_replay_permission": "yes_after_frozen_relabel_and_shuffle_control",
                "final_reason": (
                    "Source-side K_obs/K_readout review supports a caveated relabel; "
                    "a frozen relabel plus shuffled-family control is still required."
                ),
            }
        if str(row.get("kobs_kreadout_replay_permission", "")) == "no":
            return {
                "final_route_status": "KOBS_KREADOUT_RELABEL_BLOCKED_BY_SOURCE_REVIEW",
                "final_endpoint_replay_permission": "no",
                "final_reason": (
                    "Source-side K_obs/K_readout review does not support relabel; "
                    "broad source-family language alone is insufficient."
                ),
            }
        return {
            "final_route_status": "KOBS_KREADOUT_REVIEW_STILL_REQUIRED",
            "final_endpoint_replay_permission": "no",
            "final_reason": "Relabel/review cannot be promoted by endpoint score.",
        }
    if readiness_class == "BLOCKED_SOURCE_GAP":
        return {
            "final_route_status": "SOURCE_GAP_STILL_BLOCKED",
            "final_endpoint_replay_permission": "no",
            "final_reason": "Independent projection/history/source token is still missing.",
        }
    return {
        "final_route_status": "UNCLASSIFIED_BLOCKED",
        "final_endpoint_replay_permission": "no",
        "final_reason": "No route closure rule applies.",
    }


def build_closure() -> tuple[pd.DataFrame, dict[str, object]]:
    readiness = pd.read_csv(READINESS)
    if MIXED_SHUFFLE.exists():
        mixed = pd.read_csv(
            MIXED_SHUFFLE,
            usecols=[
                "support_safe_pool",
                "galaxy",
                "nonoverlap_closed",
                "shuffle_control_pass",
                "empirical_shuffle_p_better_or_equal",
                "mixed_route_scoring_permission",
            ],
        )
        closure = readiness.merge(mixed, on=["support_safe_pool", "galaxy"], how="left")
    else:
        closure = readiness.copy()
        closure["mixed_route_scoring_permission"] = ""
    if KOBS_REVIEW.exists():
        kobs = pd.read_csv(
            KOBS_REVIEW,
            usecols=[
                "support_safe_pool",
                "galaxy",
                "source_spiral_relabel_support",
                "kobs_kreadout_review_status",
                "kobs_kreadout_replay_permission",
                "kobs_kreadout_review_reason",
            ],
        )
        closure = closure.merge(kobs, on=["support_safe_pool", "galaxy"], how="left")
    final = closure.apply(_close_row, axis=1, result_type="expand")
    closure = pd.concat([closure, final], axis=1)
    closure["claim_boundary"] = CLAIM_BOUNDARY

    allowed = closure[closure["final_endpoint_replay_permission"].str.startswith("yes")]
    summary = {
        "n_rows": int(len(closure)),
        "final_route_status_counts": closure["final_route_status"].value_counts().to_dict(),
        "final_endpoint_replay_permission_counts": closure[
            "final_endpoint_replay_permission"
        ].value_counts().to_dict(),
        "allowed_rows": int(len(allowed)),
        "allowed_unique_galaxies": sorted(allowed["galaxy"].unique().tolist()),
        "blocked_rows": int(len(closure) - len(allowed)),
        "mixed_route_shuffle_pass_counts": closure.get(
            "shuffle_control_pass", pd.Series(dtype=str)
        ).fillna("not_applicable").value_counts().to_dict(),
        "kobs_review_status_counts": closure.get(
            "kobs_kreadout_review_status", pd.Series(dtype=str)
        ).fillna("not_applicable").value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "After Paper8/Paper9 readiness filtering, K_obs/K_readout source "
            "review, and the mixed-route shuffle "
            "control, only current-formula rows remain replay-ready. Mixed routes "
            "are blocked by shuffled formula-package controls, and the NGC0024 "
            "broad disk/spiral relabel is blocked by source review."
        ),
    }
    return closure.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    closure, summary = build_closure()
    closure.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "scoring_readiness_class",
        "final_route_status",
        "final_endpoint_replay_permission",
        "final_reason",
    ]
    print(closure[cols].to_string(index=False))


if __name__ == "__main__":
    main()
