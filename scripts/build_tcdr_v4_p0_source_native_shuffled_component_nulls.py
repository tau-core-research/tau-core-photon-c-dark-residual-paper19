from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

MIXED_FREEZE = OUT_DIR / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_shuffled_component_nulls_v0_1.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_shuffled_component_nulls_summary_v0_1.json"

N_SHUFFLES = 64
RNG_SEED = 19019
SHUFFLE_POLICY = (
    "endpoint_blind_component_weight_package_shuffle_v0_1_within_pilot_role_"
    "preserve_role_counts_and_weight_distribution_seed_19019"
)

WEIGHT_COLUMNS = [
    "bar_component_weight",
    "ring_component_weight",
    "spiral_component_weight",
    "fallback_family_proxy_weight",
]


def _shuffle_role_block(block: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    source = block[["galaxy", "mixed_kernel_status", "active_source_native_components", *WEIGHT_COLUMNS]].reset_index(drop=True)
    perm = rng.permutation(len(source))
    shuffled_source = source.iloc[perm].reset_index(drop=True)
    result = block.reset_index(drop=True).copy()
    result["shuffled_component_source_galaxy"] = shuffled_source["galaxy"]
    result["shuffled_mixed_kernel_status"] = shuffled_source["mixed_kernel_status"]
    result["shuffled_active_source_native_components"] = shuffled_source["active_source_native_components"]
    for column in WEIGHT_COLUMNS:
        result[f"shuffled_{column}"] = shuffled_source[column]
    return result


def build_shuffled_nulls() -> tuple[pd.DataFrame, dict[str, object]]:
    freeze = pd.read_csv(MIXED_FREEZE)
    rng = np.random.default_rng(RNG_SEED)
    rows: list[pd.DataFrame] = []
    for shuffle_id in range(N_SHUFFLES):
        pieces = []
        for _, block in freeze.groupby("pilot_role", sort=False):
            pieces.append(_shuffle_role_block(block, rng))
        shuffled = pd.concat(pieces, ignore_index=True)
        shuffled.insert(0, "shuffle_id", shuffle_id)
        shuffled["shuffle_policy"] = SHUFFLE_POLICY
        shuffled["endpoint_data_policy"] = "do_not_use_rotation_residuals_or_endpoint_scores_for_shuffled_component_nulls"
        shuffled["claim_boundary"] = "source_native_shuffled_component_nulls_not_endpoint_validation"
        rows.append(shuffled)

    detail = pd.concat(rows, ignore_index=True)
    keep = [
        "shuffle_id",
        "galaxy",
        "pilot_role",
        "source_family_candidate",
        "component_mixture_status",
        "active_source_native_components",
        "mixed_kernel_status",
        "shuffled_component_source_galaxy",
        "shuffled_mixed_kernel_status",
        "shuffled_active_source_native_components",
        "bar_component_weight",
        "ring_component_weight",
        "spiral_component_weight",
        "fallback_family_proxy_weight",
        "shuffled_bar_component_weight",
        "shuffled_ring_component_weight",
        "shuffled_spiral_component_weight",
        "shuffled_fallback_family_proxy_weight",
        "shuffle_policy",
        "endpoint_data_policy",
        "claim_boundary",
    ]
    detail = detail[keep].sort_values(["shuffle_id", "pilot_role", "galaxy"]).reset_index(drop=True)
    holdout = detail[detail["pilot_role"] == "PILOT_HOLDOUT"].copy()
    summary = {
        "n_rows": int(len(detail)),
        "n_shuffles": N_SHUFFLES,
        "n_galaxies_per_shuffle": int(freeze["galaxy"].nunique()),
        "n_holdout_rows": int(len(holdout)),
        "rng_seed": RNG_SEED,
        "shuffle_policy": SHUFFLE_POLICY,
        "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_shuffled_component_nulls",
        "verdict": (
            "The shuffled component nulls are frozen source-side controls. "
            "They preserve pilot-role component-weight distributions while breaking "
            "the galaxy-to-component assignment before endpoint scoring."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_shuffled_nulls()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
