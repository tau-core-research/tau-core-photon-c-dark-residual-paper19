from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
MANIFEST_DIR = ROOT / "data" / "source_manifests"

ROUTE_CLOSURE = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_route_closure_local.csv"
SUPPORT_AWARE = MANIFEST_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"
FORMULA_COMPLETION = MANIFEST_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_source_gap_blocker_ledger_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_source_gap_blocker_ledger_summary_local.json"

CLAIM_BOUNDARY = "source_gap_blocker_ledger_local_not_source_acquisition_not_validation"


def _is_filled(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text not in {"", "nan", "none", "null"}


def _split_components(value: object) -> set[str]:
    if not _is_filled(value):
        return set()
    return {part.strip().lower() for part in str(value).replace(",", ";").split(";") if part.strip()}


def _component_support(row: pd.Series, component: str) -> dict[str, object]:
    positive = _split_components(row.get("positive_components_source", row.get("positive_components")))
    weight = float(row.get(f"{component}_component_weight", 0.0) or 0.0)
    geometry_fields = []
    if component == "spiral":
        geometry_fields = [
            "spiral_inner_kpc_source_source",
            "spiral_outer_kpc_source_source",
            "spiral_pitch_median_abs_deg_source",
        ]
    elif component == "bar":
        geometry_fields = ["bar_radius_kpc_source_source"]
    elif component == "ring":
        geometry_fields = ["ring_radius_kpc_source_source"]

    geometry_present = sum(1 for field in geometry_fields if _is_filled(row.get(field)))
    has_component = component in positive
    has_weight = weight > 0.0
    has_geometry = geometry_present > 0

    return {
        "candidate_gap_component": component,
        "gap_component_in_positive_components": "yes" if has_component else "no",
        "gap_component_weight": weight,
        "gap_component_weight_positive": "yes" if has_weight else "no",
        "gap_component_geometry_fields_present": geometry_present,
        "gap_component_geometry_present": "yes" if has_geometry else "no",
        "gap_component_source_supported": "yes" if (has_component and has_weight and has_geometry) else "no",
    }


def _blocker(row: pd.Series) -> dict[str, object]:
    component = str(row.get("best_wrong_component", "")).strip().lower()
    support = _component_support(row, component)
    source_family = str(row.get("source_family_candidate", "")).upper()

    if support["gap_component_source_supported"] == "yes":
        blocker_class = "SOURCE_GAP_POTENTIALLY_CLOSABLE_REVIEW_REQUIRED"
        next_step = "freeze_independent_source_token_then_run_shuffle_control"
        reason = (
            "The competitive component has residual-blind source support; a "
            "separate non-overlap token and shuffled control would still be required."
        )
    elif component == "spiral" and "SPIRAL" not in source_family:
        blocker_class = "BLOCKED_WRONG_COMPONENT_OUTSIDE_SOURCE_FAMILY"
        next_step = "seek_independent_spiral_projection_history_source_or_keep_false_component_control"
        reason = (
            "The competitive spiral component is outside the frozen source family "
            "and has no independent source support in the current ledger."
        )
    else:
        blocker_class = "BLOCKED_COMPONENT_SOURCE_SUPPORT_MISSING"
        next_step = "seek_source_native_component_geometry_or_keep_blocked"
        reason = (
            "The competitive component lacks the source-side component and/or "
            "geometry support required for a readout route."
        )

    return {
        **support,
        "source_gap_blocker_class": blocker_class,
        "source_gap_next_step": next_step,
        "source_gap_reason": reason,
    }


def build_ledger() -> tuple[pd.DataFrame, dict[str, object]]:
    closure = pd.read_csv(ROUTE_CLOSURE)
    gaps = closure[closure["final_route_status"].eq("SOURCE_GAP_STILL_BLOCKED")].copy()

    support = pd.read_csv(SUPPORT_AWARE)
    formula = pd.read_csv(FORMULA_COMPLETION)
    support_cols = [
        "galaxy",
        "positive_components",
        "bar_component_weight",
        "ring_component_weight",
        "spiral_component_weight",
        "bar_radius_kpc_source",
        "ring_radius_kpc_source",
        "spiral_inner_kpc_source",
        "spiral_outer_kpc_source",
        "feature_types_present",
        "claim_boundary",
    ]
    formula_cols = [
        "galaxy",
        "spiral_pitch_median_abs_deg_source",
        "support_safe_compiled_formula",
    ]

    gaps = gaps.merge(
        support[[col for col in support_cols if col in support.columns]],
        on="galaxy",
        how="left",
        suffixes=("", "_source"),
    )
    gaps = gaps.merge(
        formula[[col for col in formula_cols if col in formula.columns]],
        on="galaxy",
        how="left",
    )
    verdict = gaps.apply(_blocker, axis=1, result_type="expand")
    gaps = pd.concat([gaps, verdict], axis=1)
    gaps["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(gaps)),
        "n_unique_galaxies": int(gaps["galaxy"].nunique()),
        "blocker_class_counts": gaps["source_gap_blocker_class"].value_counts().to_dict(),
        "gap_component_counts": gaps["candidate_gap_component"].value_counts().to_dict(),
        "gap_component_source_supported_counts": gaps[
            "gap_component_source_supported"
        ].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The current source-gap rows remain blocked. In this ledger all "
            "competitive gap components lack the independent source-side support "
            "needed to become readout routes."
        ),
    }
    return gaps.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    ledger, summary = build_ledger()
    ledger.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "source_family_candidate",
        "best_wrong_component",
        "gap_component_source_supported",
        "source_gap_blocker_class",
        "source_gap_next_step",
    ]
    print(ledger[cols].to_string(index=False))


if __name__ == "__main__":
    main()
