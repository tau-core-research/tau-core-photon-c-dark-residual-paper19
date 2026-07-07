from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "source_manifests"

MIXTURE_AUDIT = OUT_DIR / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"

OUT_DETAIL = OUT_DIR / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_v0_1.csv"
OUT_SUMMARY = OUT_DIR / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_summary_v0_1.json"

WEIGHT_POLICY = (
    "source_native_mixed_component_freeze_v0_1_primary_0p5_secondary_equal_"
    "when_multicomponent_single_component_1p0_no_component_family_proxy_fallback"
)


def _family_primary_component(family: str) -> str:
    if family == "K_BARRED_M2":
        return "bar"
    if family == "K_RING_RESONANCE":
        return "ring"
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        return "spiral"
    return "none"


def _active_components(text: object) -> list[str]:
    if text is None or pd.isna(text):
        return []
    return [
        item
        for item in str(text).split(";")
        if item in {"bar", "ring", "spiral"}
    ]


def _weights(family: str, active: list[str]) -> dict[str, float]:
    if not active:
        return {"bar": 0.0, "ring": 0.0, "spiral": 0.0, "fallback_family_proxy": 1.0}
    if len(active) == 1:
        return {
            "bar": 1.0 if active[0] == "bar" else 0.0,
            "ring": 1.0 if active[0] == "ring" else 0.0,
            "spiral": 1.0 if active[0] == "spiral" else 0.0,
            "fallback_family_proxy": 0.0,
        }

    primary = _family_primary_component(family)
    result = {"bar": 0.0, "ring": 0.0, "spiral": 0.0, "fallback_family_proxy": 0.0}
    if primary in active:
        result[primary] = 0.5
        secondary = [component for component in active if component != primary]
        for component in secondary:
            result[component] = 0.5 / len(secondary)
    else:
        for component in active:
            result[component] = 1.0 / len(active)
    return result


def _kernel_status(active: list[str]) -> str:
    if not active:
        return "fallback_family_proxy_kernel"
    if len(active) == 1:
        return "single_source_native_component_kernel"
    return "mixed_source_native_component_kernel"


def build_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    audit = pd.read_csv(MIXTURE_AUDIT)
    rows: list[dict[str, object]] = []
    for _, row in audit.iterrows():
        family = str(row["source_family_candidate"])
        active = _active_components(row["active_source_native_components"])
        weights = _weights(family, active)
        total_weight = sum(weights.values())
        rows.append(
            {
                "galaxy": row["galaxy"],
                "pilot_role": row["pilot_role"],
                "source_family_candidate": family,
                "component_mixture_status": row["component_mixture_status"],
                "active_source_native_components": row["active_source_native_components"],
                "mixed_kernel_status": _kernel_status(active),
                "bar_component_weight": weights["bar"],
                "ring_component_weight": weights["ring"],
                "spiral_component_weight": weights["spiral"],
                "fallback_family_proxy_weight": weights["fallback_family_proxy"],
                "total_kernel_weight": total_weight,
                "weight_policy": WEIGHT_POLICY,
                "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_mixed_component_kernel_freeze",
                "claim_boundary": "source_native_mixed_component_kernel_freeze_not_endpoint_validation",
            }
        )
    detail = pd.DataFrame(rows).sort_values(["mixed_kernel_status", "source_family_candidate", "pilot_role", "galaxy"]).reset_index(drop=True)
    holdout = detail[detail["pilot_role"] == "PILOT_HOLDOUT"].copy()
    summary = {
        "n_rows": int(len(detail)),
        "mixed_kernel_status_counts": {
            str(key): int(value)
            for key, value in detail["mixed_kernel_status"].value_counts().sort_index().items()
        },
        "holdout_mixed_kernel_status_counts": {
            str(key): int(value)
            for key, value in holdout["mixed_kernel_status"].value_counts().sort_index().items()
        },
        "weight_policy": WEIGHT_POLICY,
        "endpoint_data_policy": "do_not_use_rotation_residuals_or_endpoint_scores_for_mixed_component_kernel_freeze",
        "verdict": (
            "The source-native mixed-component kernel weights are frozen before endpoint scoring. "
            "This creates an auditable mixed-kernel rule for later shuffled-component nulls; "
            "it is not endpoint validation."
        ),
    }
    return detail, summary


def main() -> None:
    detail, summary = build_freeze()
    detail.to_csv(OUT_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_DETAIL}")
    print(f"WROTE {OUT_SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
