from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
SOURCE_DIR = ROOT / "data" / "source_manifests"

SOURCE_REVIEW = EXTERNAL_DIR / "tcdr_v4_allowed_failure_external_source_review_local.csv"
FORMULA_COMPLETION = SOURCE_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"
NUMERIC_FREEZE = SOURCE_DIR / "tcdr_v4_allowed_failure_numeric_source_freeze_v0_1.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_allowed_failure_formula_freeze_readiness_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_failure_formula_freeze_readiness_summary_local.json"

CLAIM_BOUNDARY = "allowed_failure_formula_freeze_readiness_not_endpoint_replay"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


def _as_source_value(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    if text.lower() == "nan":
        return ""
    return text


def build_readiness() -> tuple[pd.DataFrame, dict[str, object]]:
    review = pd.read_csv(SOURCE_REVIEW)
    formula = pd.read_csv(FORMULA_COMPLETION)
    numeric = pd.read_csv(NUMERIC_FREEZE) if NUMERIC_FREEZE.exists() else pd.DataFrame()
    formula_by_galaxy = formula.set_index("galaxy")
    rows: list[dict[str, object]] = []

    for source_row in review.to_dict(orient="records"):
        galaxy = source_row["galaxy"]
        formula_row = formula_by_galaxy.loc[galaxy].to_dict()
        current_formula = formula_row.get("support_safe_compiled_formula", "")
        current_required = formula_row.get("support_safe_formula_required_observables", "")

        if galaxy == "NGC2841":
            requested_numeric = [
                "spiral_inner_kpc_source",
                "spiral_outer_kpc_source",
                "spiral_pitch_median_abs_deg_source",
                "warp_onset_or_path_environment_numeric_source",
            ]
            if numeric.empty:
                frozen_requested = set()
            else:
                frozen_requested = set(
                    numeric[
                        (numeric["galaxy"] == galaxy)
                        & (
                            numeric["numeric_source_freeze_status"]
                            == "frozen_caveated_numeric_source"
                        )
                    ]["requested_observable"].tolist()
                )
            missing_requested = [
                observable
                for observable in requested_numeric
                if observable not in frozen_requested
            ]
            if missing_requested:
                status = "ROUTE_REVIEW_OPEN_FORMULA_FREEZE_BLOCKED_NUMERIC_SOURCE_OBSERVABLES"
                route_permission = "yes_caveated_spiral_path_formula_freeze_review_only"
                available_extra = [
                    "qualitative_flocculent_spiral_label",
                    "qualitative_outer_warp_label",
                ]
                missing = ";".join(missing_requested)
            else:
                status = "ROUTE_REVIEW_OPEN_NUMERIC_SOURCE_FIELDS_FROZEN_FORMULA_FREEZE_READY"
                route_permission = "yes_caveated_spiral_path_formula_freeze_ready_no_scoring"
                available_extra = [
                    "spiral_inner_kpc_source",
                    "spiral_outer_kpc_source",
                    "spiral_pitch_median_abs_deg_source",
                    "warp_onset_or_path_environment_numeric_source",
                    "qualitative_flocculent_spiral_label",
                    "qualitative_outer_warp_label",
                ]
                missing = "none"
            requested_route = "spiral_path"
            required = (
                "spiral_inner_kpc_source;spiral_outer_kpc_source;"
                "spiral_pitch_median_abs_deg_source;warp_onset_or_path_environment_numeric_source"
            )
            available = ";".join(
                item
                for item in [
                    "rdisk_kpc_source" if _as_source_value(formula_row.get("rdisk_kpc_source")) else "",
                    "ring_radius_kpc_source" if _as_source_value(formula_row.get("ring_radius_kpc_source")) else "",
                    "ring_strength_proxy" if _as_source_value(formula_row.get("ring_strength_proxy")) else "",
                    *available_extra,
                ]
                if item
            )
            verdict = (
                "NGC2841 can enter a source-side spiral/path formula-freeze review with "
                "caveated numeric source coordinates, but it still has no endpoint replay "
                "or new-route scoring permission until a separate formula artifact is "
                "frozen and reviewed."
            )
        else:
            status = "ROUTE_REVIEW_BLOCKED_WEAK_ASYMMETRY_NOT_SPIRAL_PATH_FORMULA"
            route_permission = "no_spiral_path_formula_freeze_review"
            requested_route = "spiral_path"
            required = (
                "route_closing_spiral_geometry_or_path_history_source;"
                "numeric_asymmetry_or_path_environment_source"
            )
            available = "tentative_outer_asymmetry_label"
            missing = "route_closing_spiral_geometry_or_path_history_source"
            verdict = (
                "UGC00191 has only weak asymmetry support and no route-closing spiral/path "
                "geometry. It remains a source-acquisition/control-pressure case, not a "
                "formula-freeze candidate."
            )

        rows.append(
            {
                "galaxy": galaxy,
                "requested_route": requested_route,
                "external_source_review_status": source_row["source_review_status"],
                "external_source_support_level": source_row["source_support_level"],
                "current_source_formula": current_formula,
                "current_formula_required_observables": current_required,
                "formula_freeze_readiness_status": status,
                "source_side_route_review_permission": route_permission,
                "requested_route_required_observables": required,
                "requested_route_available_observables": available,
                "requested_route_missing_observables": missing,
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
                "verdict": verdict,
            }
        )

    out = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(out)),
        "galaxies": out["galaxy"].tolist(),
        "formula_freeze_readiness_status_counts": out["formula_freeze_readiness_status"].value_counts().to_dict(),
        "source_side_route_review_permission_counts": out[
            "source_side_route_review_permission"
        ].value_counts().to_dict(),
        "endpoint_replay_permission_counts": out["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": out["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": out["new_route_scoring_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Allowed-failure source evidence now moves NGC2841 to a caveated numeric-source "
            "formula-freeze-ready review state, but it still does not create a score-bearing "
            "formula by itself. UGC00191 remains weak/asymmetry-only and not route-closing. "
            "Endpoint replay, kernel promotion, and new-route scoring remain closed for both."
        ),
    }
    return out, summary


def main() -> None:
    out, summary = build_readiness()
    out.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        out[
            [
                "galaxy",
                "formula_freeze_readiness_status",
                "source_side_route_review_permission",
                "new_route_scoring_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
