from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"
FAMILY_FREEZE = OUT_DIR / "tcdr_v4_p0_source_family_freeze_v0_1.csv"

HOLDOUT_PER_FAMILY = 2
MIN_TRAIN_PER_FAMILY = 1
SELECTION_POLICY = (
    "endpoint_blind_homogeneous_s4g_family_balanced_"
    "calibration_aware_projection_caveat_no_first_then_galaxy_name"
)
ENDPOINT_DATA_POLICY = "do_not_use_rotation_residuals_for_pilot_holdout_selection"


def build_pilot_holdout() -> tuple[pd.DataFrame, dict[str, object]]:
    source = pd.read_csv(FAMILY_FREEZE)
    homogeneous = source[source["freeze_strength"] == "freeze_ready_homogeneous_s4g"].copy()

    selected: set[str] = set()
    family_holdout_counts: dict[str, int] = {}
    for family, group in homogeneous.groupby("source_family_candidate", sort=True):
        ordered = group.assign(
            _projection_rank=group["projection_caveat"].map({"no": 0, "yes": 1}).fillna(2)
        ).sort_values(["_projection_rank", "galaxy"])
        n_holdout = min(HOLDOUT_PER_FAMILY, max(1, len(ordered) - MIN_TRAIN_PER_FAMILY))
        holdout = ordered.head(n_holdout)
        family_holdout_counts[family] = int(len(holdout))
        selected.update(str(galaxy) for galaxy in holdout["galaxy"].tolist())

    rows = []
    for _, row in source.iterrows():
        galaxy = str(row["galaxy"])
        if row["freeze_strength"] != "freeze_ready_homogeneous_s4g":
            role = "NON_HOMOGENEOUS_SOURCE_TIER"
            reason = "outside_first_homogeneous_s4g_pilot"
        elif galaxy in selected:
            role = "PILOT_HOLDOUT"
            reason = "family_balanced_homogeneous_s4g_holdout"
        else:
            role = "PILOT_TRAIN_POOL"
            reason = "homogeneous_s4g_not_selected_for_first_holdout"

        rows.append(
            {
                **row.to_dict(),
                "pilot_role": role,
                "pilot_selection_policy": SELECTION_POLICY,
                "holdout_selection_reason": reason,
                "holdout_per_family_target": HOLDOUT_PER_FAMILY,
                "min_train_per_family": MIN_TRAIN_PER_FAMILY,
                "endpoint_data_policy": ENDPOINT_DATA_POLICY,
            }
        )

    detail = (
        pd.DataFrame(rows)
        .sort_values(["pilot_role", "source_family_candidate", "projection_caveat", "galaxy"])
        .reset_index(drop=True)
    )
    role_counts = detail["pilot_role"].value_counts().sort_index().to_dict()
    train_pool = detail[detail["pilot_role"] == "PILOT_TRAIN_POOL"]
    holdout = detail[detail["pilot_role"] == "PILOT_HOLDOUT"]
    summary = {
        "selection_policy": SELECTION_POLICY,
        "endpoint_data_policy": ENDPOINT_DATA_POLICY,
        "holdout_per_family_target": HOLDOUT_PER_FAMILY,
        "min_train_per_family": MIN_TRAIN_PER_FAMILY,
        "n_p0_objects": int(len(detail)),
        "n_homogeneous_s4g": int(len(homogeneous)),
        "n_pilot_holdout": int(len(holdout)),
        "n_pilot_train_pool": int(len(train_pool)),
        "n_non_homogeneous_source_tier": int(
            (detail["pilot_role"] == "NON_HOMOGENEOUS_SOURCE_TIER").sum()
        ),
        "pilot_role_counts": {key: int(value) for key, value in role_counts.items()},
        "family_holdout_counts": family_holdout_counts,
        "holdout_galaxies": holdout["galaxy"].tolist(),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_pilot_holdout()
    detail_out = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv"
    summary_out = OUT_DIR / "tcdr_v4_p0_pilot_holdout_manifest_summary_v0_1.json"
    detail.to_csv(detail_out, index=False, quoting=csv.QUOTE_MINIMAL)
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {detail_out}")
    print(f"WROTE {summary_out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
