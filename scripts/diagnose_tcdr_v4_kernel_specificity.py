from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from run_tcdr_v4_holdout_endpoint_scoring import (
    EXTERNAL_DIR,
    KERNEL_SHAPE_POLICY,
    run_scoring,
)


OUT_DIAG = EXTERNAL_DIR / "tcdr_v4_p0_kernel_specificity_diagnosis_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_p0_kernel_specificity_diagnosis_local.json"


SOURCE_NATIVE_NEEDS = {
    "K_BARRED_M2": (
        "bar length, bar strength, phase/orientation, and radial bar-support "
        "window; a binary barred flag is not enough"
    ),
    "K_DIFFUSE_LATE_DISK": (
        "source-native H I extent, low-surface-brightness support, outer gas "
        "transition, and diffuse-disk quality; current family is calibration-blocked"
    ),
    "K_EXPONENTIAL_SPIRAL_DISK": (
        "disk scale, bulge/disk split, outer H I transition, and smooth-tail "
        "guard; avoid turning the disk kernel into a universal residual absorber"
    ),
    "K_RING_RESONANCE": (
        "ring radius, ring width, resonance/onset class, and whether the ring "
        "is inner, outer, pseudo-ring, or projection-driven"
    ),
}


def _diagnosis_status(
    endpoint_status: str,
    matched_rank: int | None,
    matched_beats_wrong_mean: str,
    matched_beats_best_wrong: str,
) -> str:
    if endpoint_status != "scoreable":
        return "calibration_blocked_no_family_verdict"
    if matched_rank == 1:
        return "matched_is_best_calibrated_family"
    if matched_beats_wrong_mean == "yes" and matched_beats_best_wrong == "no":
        return "single_wrong_family_leakage"
    if matched_beats_wrong_mean == "no":
        return "wrong_family_mean_dominance"
    return "mixed_specificity_warning"


def _diagnosis_note(matched: str, best: str | None, status: str) -> str:
    if status == "calibration_blocked_no_family_verdict":
        return "Matched family has insufficient train-pool calibration; do not score as endpoint evidence."
    if status == "matched_is_best_calibrated_family":
        return "Matched family is currently the best calibrated family on this holdout object."
    if best == "K_EXPONENTIAL_SPIRAL_DISK" and matched in {"K_BARRED_M2", "K_RING_RESONANCE"}:
        return "Ordinary disk-scale control is absorbing structure that the matched bar/ring proxy does not localize."
    if best == "K_BARRED_M2" and matched == "K_RING_RESONANCE":
        return "Inner compact support beats the ring proxy; ring radius/onset may be mislocalized or projection-smeared."
    if best == "K_RING_RESONANCE" and matched == "K_BARRED_M2":
        return "Narrow resonance support beats the bar proxy; bar radial support may be too compact or missing ring/spiral coupling."
    return "Matched family is not sufficiently separated from calibrated wrong-family controls."


def build_diagnosis() -> tuple[pd.DataFrame, dict[str, object]]:
    detail, summary, aggregate = run_scoring()
    calibrated = detail[detail["is_calibrated_family"] == "yes"].copy()
    rows = []
    confusion = Counter()
    status_counts = Counter()

    for _, row in summary.sort_values("galaxy").iterrows():
        galaxy = str(row["galaxy"])
        matched = str(row["matched_source_family"])
        endpoint_status = str(row["endpoint_scoring_status"])
        scores = calibrated[calibrated["galaxy"] == galaxy].sort_values("weighted_rmse_kms")

        best_family = None
        best_wrong_family = None
        matched_rank = None
        if not scores.empty:
            best_family = str(scores.iloc[0]["scored_family"])
            for idx, score_row in enumerate(scores.itertuples(index=False), start=1):
                family = str(score_row.scored_family)
                if family == matched:
                    matched_rank = idx
                elif best_wrong_family is None:
                    best_wrong_family = family

        status = _diagnosis_status(
            endpoint_status,
            matched_rank,
            str(row["matched_beats_wrong_mean"]),
            str(row["matched_beats_best_wrong"]),
        )
        status_counts[status] += 1
        if endpoint_status == "scoreable" and best_family and best_family != matched:
            confusion[(matched, best_family)] += 1

        rows.append(
            {
                "galaxy": galaxy,
                "matched_source_family": matched,
                "endpoint_scoring_status": endpoint_status,
                "matched_rank_among_calibrated": matched_rank if matched_rank is not None else "",
                "best_calibrated_family": best_family or "",
                "best_wrong_family": best_wrong_family or "",
                "matched_beats_baryonic_carrier": row["matched_beats_baryonic_carrier"],
                "matched_beats_wrong_mean": row["matched_beats_wrong_mean"],
                "matched_beats_best_wrong": row["matched_beats_best_wrong"],
                "matched_minus_baseline_weighted_rmse_kms": row[
                    "matched_minus_baseline_weighted_rmse_kms"
                ],
                "wrong_mean_minus_matched_weighted_rmse_kms": row[
                    "wrong_mean_minus_matched_weighted_rmse_kms"
                ],
                "best_wrong_minus_matched_weighted_rmse_kms": row[
                    "best_wrong_minus_matched_weighted_rmse_kms"
                ],
                "diagnosis_status": status,
                "diagnosis_note": _diagnosis_note(matched, best_family, status),
                "next_source_native_coordinate_need": SOURCE_NATIVE_NEEDS[matched],
                "kernel_shape_policy": KERNEL_SHAPE_POLICY,
            }
        )

    diagnosis = pd.DataFrame(rows)
    summary_payload = {
        "kernel_shape_policy": KERNEL_SHAPE_POLICY,
        "claim_boundary": "local_kernel_specificity_diagnosis_not_endpoint_validation",
        "aggregate_scoring": aggregate,
        "diagnosis_status_counts": dict(status_counts),
        "wrong_winner_confusion_counts": {
            f"{matched}->{winner}": count for (matched, winner), count in sorted(confusion.items())
        },
        "next_kernel_development_verdict": (
            "Do not tune holdout amplitudes. The next finite improvement is "
            "source-native family coordinates: bar length/phase/support, ring "
            "radius/width/onset, disk/H I transition, and diffuse-disk calibration."
        ),
    }
    return diagnosis, summary_payload


def main() -> None:
    diagnosis, summary = build_diagnosis()
    OUT_DIAG.parent.mkdir(parents=True, exist_ok=True)
    diagnosis.to_csv(OUT_DIAG, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_DIAG}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(diagnosis.to_string(index=False))


if __name__ == "__main__":
    main()
