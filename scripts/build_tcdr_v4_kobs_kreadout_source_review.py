from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
MANIFEST_DIR = ROOT / "data" / "source_manifests"

READINESS = EXTERNAL_DIR / "tcdr_v4_paper8_paper9_scoring_readiness_ledger_local.csv"
SUPPORT_AWARE = MANIFEST_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"
FORMULA_COMPLETION = MANIFEST_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_kobs_kreadout_source_review_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_kobs_kreadout_source_review_summary_local.json"

CLAIM_BOUNDARY = (
    "kobs_kreadout_source_review_local_not_endpoint_relabel_not_validation"
)

SPIRAL_COMPONENT_WEIGHT_MIN = 0.15
SPIRAL_GEOMETRY_FIELD_MIN = 2


def _is_filled(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text not in {"", "nan", "none", "null"}


def _positive_components(value: object) -> set[str]:
    if not _is_filled(value):
        return set()
    return {part.strip().lower() for part in str(value).replace(",", ";").split(";") if part.strip()}


def _review_row(row: pd.Series) -> dict[str, object]:
    positive = _positive_components(row.get("positive_components_source", row.get("positive_components")))
    spiral_weight = float(row.get("spiral_component_weight", 0.0) or 0.0)
    spiral_fields = [
        "spiral_inner_kpc_source_source",
        "spiral_outer_kpc_source_source",
        "spiral_pitch_median_abs_deg_source_source",
    ]
    # If suffixing did not happen because only one table had a column, fall back
    # to the unsuffixed names.
    geometry_present = 0
    for field in spiral_fields:
        base_field = field.replace("_source_source", "_source")
        if _is_filled(row.get(field, row.get(base_field))):
            geometry_present += 1

    broad_family_has_spiral = "spiral" in str(row.get("source_family_candidate", "")).lower()
    positive_component_has_spiral = "spiral" in positive
    spiral_weight_sufficient = spiral_weight >= SPIRAL_COMPONENT_WEIGHT_MIN
    spiral_geometry_sufficient = geometry_present >= SPIRAL_GEOMETRY_FIELD_MIN

    source_spiral_support = (
        positive_component_has_spiral
        and spiral_weight_sufficient
        and spiral_geometry_sufficient
    )

    if source_spiral_support:
        review_status = "KREADOUT_RELABEL_SOURCE_SUPPORTED_CAVEATED"
        replay_permission = "yes_after_frozen_relabel_and_shuffle_control"
        reason = (
            "Source-side spiral component, strength, and geometry support are all "
            "present. Endpoint scores still cannot choose the relabel; a frozen "
            "relabel plus shuffled-family control would be required next."
        )
    elif broad_family_has_spiral:
        review_status = "KREADOUT_RELABEL_BLOCKED_BROAD_FAMILY_ONLY"
        replay_permission = "no"
        reason = (
            "The broad source family contains spiral/disk language, but the "
            "source-side active component ledger does not support a spiral "
            "readout relabel."
        )
    else:
        review_status = "KREADOUT_RELABEL_BLOCKED_NO_SOURCE_FAMILY_SUPPORT"
        replay_permission = "no"
        reason = "No source-side family support exists for the proposed readout relabel."

    return {
        "broad_family_has_spiral": "yes" if broad_family_has_spiral else "no",
        "positive_component_has_spiral": "yes" if positive_component_has_spiral else "no",
        "review_spiral_component_weight": spiral_weight,
        "spiral_component_weight_min": SPIRAL_COMPONENT_WEIGHT_MIN,
        "spiral_weight_sufficient": "yes" if spiral_weight_sufficient else "no",
        "spiral_geometry_fields_present": geometry_present,
        "spiral_geometry_field_min": SPIRAL_GEOMETRY_FIELD_MIN,
        "spiral_geometry_sufficient": "yes" if spiral_geometry_sufficient else "no",
        "source_spiral_relabel_support": "yes" if source_spiral_support else "no",
        "kobs_kreadout_review_status": review_status,
        "kobs_kreadout_replay_permission": replay_permission,
        "kobs_kreadout_review_reason": reason,
    }


def build_review() -> tuple[pd.DataFrame, dict[str, object]]:
    readiness = pd.read_csv(READINESS)
    review = readiness[
        readiness["scoring_readiness_class"].eq("NOT_READY_KOBS_KREADOUT_REVIEW_REQUIRED")
    ].copy()
    support = pd.read_csv(SUPPORT_AWARE)
    formula = pd.read_csv(FORMULA_COMPLETION)

    support_cols = [
        "galaxy",
        "top_component",
        "positive_components",
        "bar_component_weight",
        "ring_component_weight",
        "review_spiral_component_weight",
        "bar_radius_kpc_source",
        "ring_radius_kpc_source",
        "spiral_inner_kpc_source",
        "spiral_outer_kpc_source",
        "spiral_pitch_median_abs_deg_source",
        "feature_types_present",
        "endpoint_data_policy",
        "claim_boundary",
    ]
    formula_cols = [
        "galaxy",
        "rdisk_kpc_source",
        "spiral_pitch_median_abs_deg_source",
        "support_safe_compiled_formula",
        "support_safe_formula_required_observables",
        "support_safe_formula_completion_reason",
    ]

    review = review.merge(
        support[[col for col in support_cols if col in support.columns]],
        on="galaxy",
        how="left",
        suffixes=("", "_source"),
    )
    review = review.merge(
        formula[[col for col in formula_cols if col in formula.columns]],
        on="galaxy",
        how="left",
    )
    verdict = review.apply(_review_row, axis=1, result_type="expand")
    review = pd.concat([review, verdict], axis=1)
    review["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(review)),
        "n_unique_galaxies": int(review["galaxy"].nunique()),
        "review_status_counts": review["kobs_kreadout_review_status"].value_counts().to_dict(),
        "replay_permission_counts": review["kobs_kreadout_replay_permission"].value_counts().to_dict(),
        "spiral_support_counts": review["source_spiral_relabel_support"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The K_obs/K_readout review does not promote the broad disk/spiral "
            "NGC0024 rows: the source ledger has bar/ring support, zero spiral "
            "component weight, and no source-native spiral geometry."
        ),
    }
    return review.sort_values(["support_safe_pool", "galaxy"]), summary


def main() -> None:
    review, summary = build_review()
    review.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    cols = [
        "support_safe_pool",
        "galaxy",
        "source_family_candidate",
        "positive_components_source",
        "review_spiral_component_weight",
        "spiral_geometry_fields_present",
        "source_spiral_relabel_support",
        "kobs_kreadout_review_status",
        "kobs_kreadout_replay_permission",
    ]
    print(review[cols].to_string(index=False))


if __name__ == "__main__":
    main()
