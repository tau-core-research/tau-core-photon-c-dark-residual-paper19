from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_tcdr_v4_support_safe_pool_loocv_scoring as top_component


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

SUPPORT = SOURCE_DIR / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"

OUT_FAILURE = EXTERNAL_DIR / "tcdr_v4_support_safe_pool_loocv_failure_ledger_local.csv"
OUT_FAILURE_JSON = EXTERNAL_DIR / "tcdr_v4_support_safe_pool_loocv_failure_ledger_summary_local.json"
OUT_FORMULA_DETAIL = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_detail_local.csv"
OUT_FORMULA_SUMMARY = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_summary_local.csv"
OUT_FORMULA_JSON = EXTERNAL_DIR / "tcdr_v4_support_safe_formula_aware_loocv_scoring_summary_local.json"

COMPONENTS = top_component.COMPONENTS

SCORING_POLICY = (
    "support_safe_formula_aware_pool_leave_one_galaxy_out_local_endpoint_diagnostic_"
    "candidate_uses_frozen_compiled_formula_not_top_component_only"
)
AMPLITUDE_POLICY = top_component.AMPLITUDE_POLICY
KERNEL_SHAPE_POLICY = (
    "source_native_support_safe_compiled_formula_route_from_frozen_v0_7_v0_9_manifest"
)
CLAIM_BOUNDARY = "support_safe_formula_aware_loocv_local_diagnostic_not_validation"


def _split_components(value: object) -> set[str]:
    text = "" if pd.isna(value) else str(value)
    return {part.strip() for part in text.split(";") if part.strip() and part.strip() != "none"}


def _formula_family(formula: str) -> str | None:
    if "RING" in formula:
        return "K_RING_RESONANCE"
    if "BAR" in formula:
        return "K_BARRED_M2"
    if "SPIRAL" in formula or "EXPONENTIAL" in formula or "DISK_SCALE_TAIL" in formula:
        return "K_EXPONENTIAL_SPIRAL_DISK"
    return None


def _formula_kernel(group: pd.DataFrame) -> pd.Series:
    formula = str(group["support_safe_compiled_formula"].iloc[0])
    if formula == "F_MIXED_BAR_SOURCE_NATIVE_COMPONENTS":
        def _weight(name: str) -> float:
            value = pd.to_numeric(group[name].iloc[0], errors="coerce")
            if pd.isna(value):
                return 0.0
            return float(value)

        weights = {
            "bar": _weight("bar_component_weight"),
            "ring": _weight("ring_component_weight"),
            "spiral": _weight("spiral_component_weight"),
        }
        total = sum(max(0.0, w) for w in weights.values())
        if total <= 0.0:
            component = str(group["top_component"].iloc[0])
            return top_component._component_kernel(component, group)
        kernel = pd.Series(0.0, index=group.index, dtype=float)
        for component, weight in weights.items():
            if weight > 0.0:
                kernel = kernel + (weight / total) * top_component._component_kernel(component, group)
        return kernel.clip(lower=0)

    family = _formula_family(formula)
    if family == "K_BARRED_M2":
        return top_component._component_kernel("bar", group)
    if family == "K_RING_RESONANCE":
        return top_component._component_kernel("ring", group)
    if family == "K_EXPONENTIAL_SPIRAL_DISK":
        return top_component._component_kernel("spiral", group)

    component = str(group["top_component"].iloc[0])
    return top_component._component_kernel(component, group)


def _candidate_kernel(data: pd.DataFrame) -> pd.Series:
    pieces: list[pd.Series] = []
    for _, group in data.groupby("galaxy", sort=False):
        pieces.append(_formula_kernel(group))
    if not pieces:
        return pd.Series(dtype=float)
    return pd.concat(pieces).sort_index()


def _load_formula_data(pool_name: str, config: dict[str, object]) -> pd.DataFrame:
    data = top_component._load_pool_data(pool_name, config).copy()
    formulas = pd.read_csv(
        top_component.POOL10,
        usecols=[
            "galaxy",
            "support_safe_compiled_formula",
            "support_safe_formula_completion_status",
        ],
    )
    if "support_safe_compiled_formula" not in data.columns:
        data = data.merge(formulas, on="galaxy", how="left")
    else:
        missing = data["support_safe_compiled_formula"].isna()
        if missing.any():
            fill = data.loc[missing, ["galaxy"]].merge(formulas, on="galaxy", how="left")
            data.loc[missing, "support_safe_compiled_formula"] = fill[
                "support_safe_compiled_formula"
            ].to_numpy()
    support = pd.read_csv(
        SUPPORT,
        usecols=[
            "galaxy",
            "bar_component_weight",
            "ring_component_weight",
            "spiral_component_weight",
            "support_aware_selector_reason",
            "support_overlap_reasons",
            "missing_support_reasons",
        ],
    )
    data = data.merge(support, on="galaxy", how="left")
    return data


def _score_pool(pool_name: str, config: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    data = _load_formula_data(pool_name, config)
    detail_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for galaxy, test in data.groupby("galaxy", sort=True):
        train = data[data["galaxy"] != galaxy].copy()
        matched_component = str(test["top_component"].iloc[0])
        formula = str(test["support_safe_compiled_formula"].iloc[0])
        candidate_kernel_train = _candidate_kernel(train)
        candidate_kernel_test = _candidate_kernel(test)
        candidate_amp = top_component._fit_amplitude(train, candidate_kernel_train)
        candidate_rmse, candidate_wrmse = top_component._weighted_rmse(
            test, candidate_kernel_test, candidate_amp
        )
        baryonic_rmse, baryonic_wrmse = top_component._weighted_rmse(
            test, pd.Series(0.0, index=test.index), 0.0
        )

        control_scores = {}
        for component in COMPONENTS:
            train_kernel = top_component._component_kernel(component, train)
            test_kernel = top_component._component_kernel(component, test)
            amp = top_component._fit_amplitude(train, train_kernel)
            rmse, wrmse = top_component._weighted_rmse(test, test_kernel, amp)
            control_scores[component] = {"rmse": rmse, "wrmse": wrmse, "amp": amp}
            detail_rows.append(
                {
                    "support_safe_pool": pool_name,
                    "left_out_galaxy": galaxy,
                    "matched_component": matched_component,
                    "support_safe_compiled_formula": formula,
                    "scored_model": f"CONTROL_{component}",
                    "model_type": "component_control",
                    "n_train_galaxies": int(train["galaxy"].nunique()),
                    "n_test_points": int(len(test)),
                    "rmse_kms": rmse,
                    "weighted_rmse_kms": wrmse,
                    "amplitude_v2": amp,
                    "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                    "amplitude_policy": AMPLITUDE_POLICY,
                    "scoring_policy": SCORING_POLICY,
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )

        detail_rows.append(
            {
                "support_safe_pool": pool_name,
                "left_out_galaxy": galaxy,
                "matched_component": matched_component,
                "support_safe_compiled_formula": formula,
                "scored_model": "SUPPORT_SAFE_FORMULA_AWARE_CANDIDATE",
                "model_type": "candidate",
                "n_train_galaxies": int(train["galaxy"].nunique()),
                "n_test_points": int(len(test)),
                "rmse_kms": candidate_rmse,
                "weighted_rmse_kms": candidate_wrmse,
                "amplitude_v2": candidate_amp,
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

        wrong = {
            component: float(score["wrmse"])
            for component, score in control_scores.items()
            if component != matched_component
        }
        best_wrong_component = min(wrong, key=wrong.get)
        best_wrong = wrong[best_wrong_component]
        wrong_mean = float(np.mean(list(wrong.values())))
        matched_control_wrmse = float(control_scores[matched_component]["wrmse"])
        summary_rows.append(
            {
                "support_safe_pool": pool_name,
                "galaxy": galaxy,
                "matched_component": matched_component,
                "source_family_candidate": str(test["source_family_candidate"].iloc[0]),
                "support_safe_compiled_formula": formula,
                "positive_components": str(test["positive_components"].iloc[0]),
                "n_train_galaxies": int(train["galaxy"].nunique()),
                "n_test_points": int(len(test)),
                "baryonic_carrier_weighted_rmse_kms": baryonic_wrmse,
                "candidate_weighted_rmse_kms": candidate_wrmse,
                "matched_component_control_weighted_rmse_kms": matched_control_wrmse,
                "wrong_component_mean_weighted_rmse_kms": wrong_mean,
                "best_wrong_component": best_wrong_component,
                "best_wrong_component_weighted_rmse_kms": best_wrong,
                "candidate_minus_baryonic_weighted_rmse_kms": candidate_wrmse - baryonic_wrmse,
                "wrong_mean_minus_candidate_weighted_rmse_kms": wrong_mean - candidate_wrmse,
                "best_wrong_minus_candidate_weighted_rmse_kms": best_wrong - candidate_wrmse,
                "candidate_beats_baryonic": "yes" if candidate_wrmse < baryonic_wrmse else "no",
                "candidate_beats_matched_component_control": "yes"
                if candidate_wrmse < matched_control_wrmse
                else "no",
                "candidate_beats_wrong_component_mean": "yes" if candidate_wrmse < wrong_mean else "no",
                "candidate_beats_best_wrong_component": "yes" if candidate_wrmse < best_wrong else "no",
                "candidate_amplitude_v2": candidate_amp,
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
                "amplitude_policy": AMPLITUDE_POLICY,
                "scoring_policy": SCORING_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    scoreable = pd.DataFrame(summary_rows)
    aggregate = {
        "support_safe_pool": pool_name,
        "n_pool_galaxies": int(data["galaxy"].nunique()),
        "n_pool_points": int(len(data)),
        "candidate_beats_baryonic": int((scoreable["candidate_beats_baryonic"] == "yes").sum()),
        "candidate_beats_matched_component_control": int(
            (scoreable["candidate_beats_matched_component_control"] == "yes").sum()
        ),
        "candidate_beats_wrong_component_mean": int(
            (scoreable["candidate_beats_wrong_component_mean"] == "yes").sum()
        ),
        "candidate_beats_best_wrong_component": int(
            (scoreable["candidate_beats_best_wrong_component"] == "yes").sum()
        ),
        "median_candidate_minus_baryonic_weighted_rmse_kms": float(
            scoreable["candidate_minus_baryonic_weighted_rmse_kms"].median()
        ),
        "median_wrong_mean_minus_candidate_weighted_rmse_kms": float(
            scoreable["wrong_mean_minus_candidate_weighted_rmse_kms"].median()
        ),
        "median_best_wrong_minus_candidate_weighted_rmse_kms": float(
            scoreable["best_wrong_minus_candidate_weighted_rmse_kms"].median()
        ),
        "scoring_policy": SCORING_POLICY,
        "amplitude_policy": AMPLITUDE_POLICY,
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return detail_rows, summary_rows, aggregate


def _build_failure_ledger() -> tuple[pd.DataFrame, dict[str, object]]:
    _, top_summary, _ = top_component.run_scoring()
    top_detail = pd.read_csv(top_component.OUT_DETAIL)
    manifest = pd.read_csv(top_component.POOL10)
    manifest = manifest[
        [
            "galaxy",
            "positive_components",
            "source_family_candidate",
            "support_safe_compiled_formula",
            "support_safe_formula_completion_status",
            "support_safe_10_pool_role",
            "support_aware_selector_status",
            "top_component_weight",
            "dominance_margin",
            "bar_strength_proxy",
            "ring_strength_proxy",
            "bar_radius_kpc_source",
            "ring_radius_kpc_source",
            "spiral_inner_kpc_source",
            "spiral_outer_kpc_source",
            "spiral_pitch_median_abs_deg_source",
        ]
    ]

    rows: list[dict[str, object]] = []
    for _, row in top_summary.iterrows():
        pool = str(row["support_safe_pool"])
        galaxy = str(row["galaxy"])
        controls = top_detail[
            (top_detail["support_safe_pool"] == pool)
            & (top_detail["left_out_galaxy"] == galaxy)
            & (top_detail["model_type"] == "component_control")
        ].copy()
        controls["component"] = controls["scored_model"].str.replace("CONTROL_", "", regex=False)
        matched = str(row["matched_component"])
        wrong = controls[controls["component"] != matched].sort_values("weighted_rmse_kms")
        best_wrong = wrong.iloc[0]
        best_wrong_component = str(best_wrong["component"])
        meta = manifest[manifest["galaxy"] == galaxy].iloc[0].to_dict()
        positive = _split_components(meta.get("positive_components"))
        family = str(meta.get("source_family_candidate"))
        formula = str(meta.get("support_safe_compiled_formula"))
        if str(row["candidate_beats_best_wrong_component"]) == "yes":
            failure_class = "candidate_survives_strict_best_wrong_control"
        elif best_wrong_component in positive:
            failure_class = "best_wrong_is_source_visible_secondary_component"
        elif best_wrong_component == "spiral" and "EXPONENTIAL" in family:
            failure_class = "best_wrong_matches_broad_disk_family_not_top_component"
        elif best_wrong_component == "ring" and "RING" in family:
            failure_class = "best_wrong_matches_broad_ring_family_not_top_component"
        else:
            failure_class = "best_wrong_is_unexplained_competitive_false_component"

        rows.append(
            {
                "support_safe_pool": pool,
                "galaxy": galaxy,
                "matched_component": matched,
                "positive_components": meta.get("positive_components"),
                "source_family_candidate": family,
                "support_safe_compiled_formula": formula,
                "support_safe_formula_completion_status": meta.get("support_safe_formula_completion_status"),
                "support_safe_10_pool_role": meta.get("support_safe_10_pool_role"),
                "support_aware_selector_status": meta.get("support_aware_selector_status"),
                "top_component_weight": meta.get("top_component_weight"),
                "dominance_margin": meta.get("dominance_margin"),
                "best_wrong_component": best_wrong_component,
                "best_wrong_is_source_visible": "yes" if best_wrong_component in positive else "no",
                "candidate_weighted_rmse_kms": row["candidate_weighted_rmse_kms"],
                "best_wrong_component_weighted_rmse_kms": best_wrong["weighted_rmse_kms"],
                "best_wrong_minus_candidate_weighted_rmse_kms": row[
                    "best_wrong_minus_candidate_weighted_rmse_kms"
                ],
                "wrong_mean_minus_candidate_weighted_rmse_kms": row[
                    "wrong_mean_minus_candidate_weighted_rmse_kms"
                ],
                "candidate_beats_baryonic": row["candidate_beats_baryonic"],
                "candidate_beats_wrong_component_mean": row["candidate_beats_wrong_component_mean"],
                "candidate_beats_best_wrong_component": row["candidate_beats_best_wrong_component"],
                "failure_class": failure_class,
                "bar_strength_proxy": meta.get("bar_strength_proxy"),
                "ring_strength_proxy": meta.get("ring_strength_proxy"),
                "bar_radius_kpc_source": meta.get("bar_radius_kpc_source"),
                "ring_radius_kpc_source": meta.get("ring_radius_kpc_source"),
                "spiral_inner_kpc_source": meta.get("spiral_inner_kpc_source"),
                "spiral_outer_kpc_source": meta.get("spiral_outer_kpc_source"),
                "spiral_pitch_median_abs_deg_source": meta.get("spiral_pitch_median_abs_deg_source"),
                "claim_boundary": "failure_ledger_interpretation_local_diagnostic_not_kernel_selector",
            }
        )
    ledger = pd.DataFrame(rows).sort_values(["support_safe_pool", "galaxy"])
    summary = {
        "n_rows": int(len(ledger)),
        "failure_class_counts": ledger["failure_class"].value_counts().to_dict(),
        "best_wrong_component_counts": ledger["best_wrong_component"].value_counts().to_dict(),
        "best_wrong_source_visible_counts": ledger["best_wrong_is_source_visible"].value_counts().to_dict(),
        "claim_boundary": "failure_ledger_interpretation_local_diagnostic_not_kernel_selector",
    }
    return ledger, summary


def run_formula_aware_scoring() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    details: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    aggregates: dict[str, object] = {}
    for pool_name, config in top_component.POOL_CONFIGS.items():
        detail_rows, summary_rows, aggregate = _score_pool(pool_name, config)
        details.extend(detail_rows)
        summaries.extend(summary_rows)
        aggregates[pool_name] = aggregate
    detail = pd.DataFrame(details).sort_values(["support_safe_pool", "left_out_galaxy", "model_type", "scored_model"])
    summary = pd.DataFrame(summaries).sort_values(["support_safe_pool", "galaxy"])
    return detail, summary, {
        "pools": aggregates,
        "endpoint_data_policy": "local_sparc_endpoint_curves_used_only_after_source_pool_freeze",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def main() -> None:
    ledger, ledger_summary = _build_failure_ledger()
    ledger.to_csv(OUT_FAILURE, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_FAILURE_JSON.write_text(json.dumps(ledger_summary, indent=2), encoding="utf-8")

    detail, summary, aggregate = run_formula_aware_scoring()
    detail.to_csv(OUT_FORMULA_DETAIL, index=False, quoting=csv.QUOTE_MINIMAL)
    summary.to_csv(OUT_FORMULA_SUMMARY, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_FORMULA_JSON.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")

    print(f"WROTE LOCAL {OUT_FAILURE}")
    print(f"WROTE LOCAL {OUT_FAILURE_JSON}")
    print(json.dumps(ledger_summary, indent=2))
    print(f"WROTE LOCAL {OUT_FORMULA_DETAIL}")
    print(f"WROTE LOCAL {OUT_FORMULA_SUMMARY}")
    print(f"WROTE LOCAL {OUT_FORMULA_JSON}")
    print(json.dumps(aggregate, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
