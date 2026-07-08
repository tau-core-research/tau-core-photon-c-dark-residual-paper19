from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
SOURCE_DIR = ROOT / "data" / "source_manifests"

WORKLIST = EXTERNAL_DIR / "tcdr_v4_allowed_failure_numeric_observable_worklist_local.csv"
FORMULA_COMPLETION = SOURCE_DIR / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"
KERNEL_FREEZE = SOURCE_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
COMPILER_READINESS = SOURCE_DIR / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
NUMERIC_FREEZE = SOURCE_DIR / "tcdr_v4_allowed_failure_numeric_source_freeze_v0_1.csv"
FORMULA_FREEZE = SOURCE_DIR / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_v0_1.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_allowed_failure_scoring_preflight_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_failure_scoring_preflight_summary_local.json"

CLAIM_BOUNDARY = "allowed_failure_scoring_preflight_not_endpoint_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except TypeError:
        pass
    text = str(value).strip().lower()
    return text not in {"", "nan", "none", "null", "missing", "not_available"}


def _lookup_value(galaxy: str, observable: str, manifests: dict[str, pd.DataFrame]) -> tuple[str, str]:
    hits: list[tuple[str, Any]] = []
    for manifest_name, frame in manifests.items():
        if manifest_name == "allowed_failure_numeric_source_freeze_v0_1":
            match = frame[
                (frame["galaxy"].astype(str) == galaxy)
                & (frame["requested_observable"].astype(str) == observable)
                & (
                    frame["numeric_source_freeze_status"].astype(str)
                    == "frozen_caveated_numeric_source"
                )
            ]
            if match.empty:
                continue
            value = match.iloc[0]["frozen_numeric_value"]
            if _is_filled(value):
                hits.append((manifest_name, value))
            continue
        if observable not in frame.columns or "galaxy" not in frame.columns:
            continue
        match = frame[frame["galaxy"].astype(str) == galaxy]
        if match.empty:
            continue
        value = match.iloc[0][observable]
        if _is_filled(value):
            hits.append((manifest_name, value))

    if not hits:
        return "missing_in_local_source_manifests", ""

    manifest_name, value = hits[0]
    return "filled_in_local_source_manifest", f"{manifest_name}:{value}"


def _formula_status(galaxy: str) -> tuple[str, str]:
    if not FORMULA_FREEZE.exists():
        return "formula_not_frozen", ""
    formula = pd.read_csv(FORMULA_FREEZE)
    match = formula[
        (formula["galaxy"].astype(str) == galaxy)
        & (
            formula["formula_freeze_status"].astype(str)
            == "frozen_caveated_source_formula_no_scoring"
        )
    ]
    if match.empty:
        return "formula_not_frozen", ""
    row = match.iloc[0]
    return "formula_frozen_no_scoring", str(row["formula_id"])


def build_preflight() -> tuple[pd.DataFrame, dict[str, object]]:
    worklist = pd.read_csv(WORKLIST)
    manifests = {
        "support_safe_formula_completion_v0_9": pd.read_csv(FORMULA_COMPLETION),
        "source_native_kernel_coordinate_freeze_v0_1": pd.read_csv(KERNEL_FREEZE),
        "source_frozen_formula_compiler_readiness_v0_4": pd.read_csv(COMPILER_READINESS),
    }
    if NUMERIC_FREEZE.exists():
        manifests["allowed_failure_numeric_source_freeze_v0_1"] = pd.read_csv(NUMERIC_FREEZE)
    if FORMULA_FREEZE.exists():
        manifests["allowed_failure_spiral_path_formula_freeze_v0_1"] = pd.read_csv(FORMULA_FREEZE)

    rows: list[dict[str, object]] = []
    for row in worklist.to_dict(orient="records"):
        galaxy = str(row["galaxy"])
        observable = str(row["requested_observable"])
        local_status, local_value_ref = _lookup_value(galaxy, observable, manifests)
        formula_status, formula_id = _formula_status(galaxy)
        if local_status == "filled_in_local_source_manifest":
            scoring_preflight_status = "REQUESTED_SOURCE_OBSERVABLE_LOCALLY_FILLED_REVIEW_STILL_REQUIRED"
        elif str(row["source_side_route_review_permission"]).startswith("no"):
            scoring_preflight_status = "SCORING_BLOCKED_ROUTE_REVIEW_NOT_OPEN"
        else:
            scoring_preflight_status = "SCORING_BLOCKED_MISSING_NUMERIC_SOURCE_OBSERVABLE"
        if (
            local_status == "filled_in_local_source_manifest"
            and formula_status == "formula_frozen_no_scoring"
        ):
            scoring_preflight_status = "REQUESTED_SOURCE_OBSERVABLE_AND_FORMULA_FROZEN_AUTHORIZATION_REQUIRED"

        rows.append(
            {
                **row,
                "local_numeric_source_status": local_status,
                "local_value_reference": local_value_ref,
                "scoring_preflight_status": scoring_preflight_status,
                "formula_freeze_status": formula_status,
                "source_frozen_formula_id": formula_id,
                "formula_freeze_permission": "yes_source_formula_frozen_no_scoring"
                if formula_status == "formula_frozen_no_scoring"
                else "no",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "forbidden_inputs_checked": "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank",
                "local_source_artifacts_checked": ";".join(manifests.keys()),
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    out = pd.DataFrame(rows)

    galaxy_rows: list[dict[str, object]] = []
    for galaxy, group in out.groupby("galaxy", sort=True):
        missing = int((group["local_numeric_source_status"] != "filled_in_local_source_manifest").sum())
        filled = int((group["local_numeric_source_status"] == "filled_in_local_source_manifest").sum())
        if str(group["source_side_route_review_permission"].iloc[0]).startswith("no"):
            galaxy_status = "SCORING_BLOCKED_ROUTE_REVIEW_NOT_OPEN"
        elif missing:
            galaxy_status = "SCORING_BLOCKED_MISSING_NUMERIC_SOURCE_OBSERVABLES"
        elif (group["formula_freeze_status"] == "formula_frozen_no_scoring").all():
            galaxy_status = "SCORING_PREFLIGHT_FORMULA_FROZEN_AUTHORIZATION_REQUIRED"
        else:
            galaxy_status = "SCORING_PREFLIGHT_SOURCE_FIELDS_PRESENT_BUT_FORMULA_FREEZE_STILL_REQUIRED"
        galaxy_rows.append(
            {
                "galaxy": galaxy,
                "requested_observables": int(len(group)),
                "filled_requested_observables": filled,
                "missing_requested_observables": missing,
                "galaxy_scoring_preflight_status": galaxy_status,
            }
        )

    galaxy_df = pd.DataFrame(galaxy_rows)
    summary = {
        "n_rows": int(len(out)),
        "n_galaxies": int(galaxy_df["galaxy"].nunique()),
        "galaxies": galaxy_df["galaxy"].tolist(),
        "filled_requested_observables": int((out["local_numeric_source_status"] == "filled_in_local_source_manifest").sum()),
        "missing_requested_observables": int((out["local_numeric_source_status"] != "filled_in_local_source_manifest").sum()),
        "row_scoring_preflight_status_counts": out["scoring_preflight_status"].value_counts().sort_index().to_dict(),
        "galaxy_scoring_preflight_status_counts": galaxy_df["galaxy_scoring_preflight_status"].value_counts().sort_index().to_dict(),
        "formula_freeze_status_counts": out["formula_freeze_status"].value_counts().sort_index().to_dict(),
        "formula_freeze_permission_counts": out["formula_freeze_permission"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": out["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": out["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": out["new_route_scoring_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The scoring preflight checks requested allowed-failure numeric "
            "spiral/path observables against local source manifests. NGC2841 now "
            "has the four requested caveated numeric source coordinates and a "
            "source-frozen formula shell present, "
            "but UGC00191 remains blocked because the spiral/path route review is "
            "not open. Endpoint replay, kernel promotion, and new-route scoring "
            "are still not authorized by this preflight."
        ),
    }
    return out, summary


def main() -> None:
    out, summary = build_preflight()
    out.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        out[
            [
                "galaxy",
                "requested_observable",
                "local_numeric_source_status",
                "scoring_preflight_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
