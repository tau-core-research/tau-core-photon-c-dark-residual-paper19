from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT.parent
SOURCE_DIR = ROOT / "data" / "source_manifests"
PACKAGE_ROOT = ROOT / "data" / "reviewer_packages"
PACKAGE_NAME = "tcdr_v4_ngc2841_beta_closure_reformulation_reviewer_package_v0_1"
PACKAGE_DIR = PACKAGE_ROOT / PACKAGE_NAME
PACKAGE_ZIP = PACKAGE_ROOT / f"{PACKAGE_NAME}.zip"
DOWNLOADS_ZIP = Path.home() / "Downloads" / f"{PACKAGE_NAME}.zip"

PAPER9_DERIVED = PROJECTS / "tau-core-projection-readout-paper9" / "data" / "derived"

LOCAL_FILES = {
    "multiplicative_beta_preflight.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_v0_1.csv",
    "multiplicative_beta_preflight_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_summary_v0_1.json",
    "beta_closure_label_review.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_v0_1.csv",
    "beta_closure_label_review_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_summary_v0_1.json",
    "source_native_pa_inclination_table.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_source_native_pa_inclination_table_v0_1.csv",
    "source_native_pa_inclination_table_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_source_native_pa_inclination_table_summary_v0_1.json",
    "tilted_ring_geometry_source_review.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_v0_1.csv",
    "tilted_ring_geometry_source_review_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_summary_v0_1.json",
    "surviving_route_ledger.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_surviving_route_ledger_v0_1.csv",
    "positive_outer_capacity_route_reaudit.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_v0_1.csv",
}

PAPER9_ROW_FILES = {
    "paper9_ngc2841_beta_transfer_candidate_row.csv": PAPER9_DERIVED
    / "ugc12506_beta_closure_transfer_candidates.csv",
    "paper9_ngc2841_beta_transfer_priority_row.csv": PAPER9_DERIVED
    / "ugc12506_beta_closure_transfer_priority_gate.csv",
    "paper9_ngc2841_bullock_spin_proxy_row.csv": PAPER9_DERIVED
    / "ugc12506_beta_closure_bullock_spin_conversion_proxy_values.csv",
    "paper9_ngc2841_source_side_morphology_review_row.csv": PAPER9_DERIVED
    / "beta_transfer_source_side_morphology_review_gate.csv",
}

CLAIM_BOUNDARY = "ngc2841_beta_closure_reformulation_reviewer_package_not_endpoint"


README = """# NGC2841 beta/closure reformulation reviewer package

This package asks a narrow source-side question for Paper 19 / TCDR-v4:
is NGC2841 sufficiently supported, from residual-blind source material only,
to continue as a multiplicative beta/closure reformulation candidate?

This is not an endpoint replay package and not a request to judge a rotation
curve fit. The current status is:

`review_open_not_promoted`

## Context

The additive positive-load route remains blocked because no independent
velocity-squared `A_tau` source has been derived. A related Paper 9 audit found
a dimensionless Bullock-like spin/beta proxy for NGC2841:

- `lambda_spin ~= 0.02024`
- `beta_cl ~= 1.08034`

That proxy cannot be used as additive `A_tau`. It can only motivate a separate
multiplicative beta/closure shell:

`v_beta^2(R)=v_carrier^2(R)*[1+(beta_cl-1)*K_beta(R)]`

The three unresolved decisions are:

1. Spin route: can the Bullock-like disk conversion proxy be accepted, rejected,
   or retained only as caveated context for the beta/closure slot?
2. Carrier: is any carrier policy acceptable for preflight freeze, or must it
   remain blocked?
3. `K_beta(R)`: can a dimensionless beta kernel be derived/frozen from the
   included source-side morphology, or must it remain blocked?

## Your task

Fill `review_response_template.csv`.

Use only the included source-side artifacts. If the evidence is insufficient,
choose the blocked/caveated answer. Do not use any rotation-curve residual,
endpoint score, best baseline comparison, or required-load diagnostic.

## Forbidden inputs

Do not use:

- observed rotation curves or velocity residuals;
- SPARC `Vobs`/`errV`;
- endpoint RMSE, baseline scores, wrong-family ranks, or Tau Core endpoint scores;
- required `A_tau`, required lambda, or observed velocity gap diagnostics;
- any answer chosen because it improves or worsens a rotation-curve fit.

The completed CSV must keep:

- `endpoint_replay_permission=must_be_no`;
- `kernel_promotion_permission=must_be_no`;
- `formula_freeze_permission=must_be_no`;
- `uses_rotation_curve_or_velocity=must_be_false`;
- `uses_endpoint_rotation_residual=must_be_false`;
- `uses_tau_core_score_or_required_load=must_be_false`.

## Included files

- `multiplicative_beta_preflight.csv/json`: formula-shell preflight and blockers.
- `beta_closure_label_review.csv/json`: current source-side review-open verdict.
- `paper9_*_row.csv`: NGC2841 rows copied from Paper 9 beta/closure artifacts.
- `source_native_pa_inclination_table.csv/json`: Paper 19 scalar PA/inclination source support.
- `tilted_ring_geometry_source_review.csv/json`: Paper 19 warped-HI tilted-ring source context.
- `surviving_route_ledger.csv`: local NGC2841 route context.
- `positive_outer_capacity_route_reaudit.csv`: why additive positive-load remains blocked.
- `review_response_template.csv`: file to fill.

## Claim boundary

Package status: `ngc2841_beta_closure_reformulation_reviewer_package_not_endpoint`.

This package can only support a later source-side decision about whether a
beta/closure review remains open, is rejected, or may move to a separate
formula-freeze review. It cannot authorize endpoint replay or scoring.
"""


RESPONSE_ROWS = [
    {
        "galaxy": "NGC2841",
        "question_id": "Q1_spin_route",
        "question": (
            "Can the Bullock-like disk conversion proxy be accepted for the beta/closure "
            "spin-normalization slot?"
        ),
        "allowed_answer": (
            "accept_bullock_conversion_for_caveated_preflight|"
            "reject_bullock_conversion|"
            "retain_as_context_only|"
            "require_direct_source_native_spin|blocked_unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "formula_freeze_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q2_carrier_policy",
        "question": (
            "Is any carrier policy acceptable for a later beta/closure formula-freeze "
            "review, without using endpoint performance?"
        ),
        "allowed_answer": (
            "accept_baryonic_carrier_as_stress_control|"
            "accept_paper9_carrier_policy_as_caveated|"
            "reject_current_carriers|"
            "require_new_source_frozen_carrier|blocked_unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "formula_freeze_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q3_k_beta_kernel",
        "question": (
            "Can a dimensionless K_beta(R) kernel be source-frozen from the included "
            "warped-HI/tilted-ring and morphology context?"
        ),
        "allowed_answer": (
            "accept_scalar_projection_kernel_only|"
            "accept_caveated_radial_tilted_ring_kernel_for_preflight|"
            "reject_kernel_freeze|"
            "require_new_source_native_radial_profile|blocked_unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "formula_freeze_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q4_route_status",
        "question": (
            "Given Q1-Q3, what is the allowed status of the NGC2841 beta/closure "
            "reformulation route?"
        ),
        "allowed_answer": (
            "review_open_not_promoted|"
            "reject_beta_closure_reformulation|"
            "formula_freeze_review_allowed_endpoint_still_blocked|"
            "blocked_need_more_sources"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "formula_freeze_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy(path: Path, target_name: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing package input: {path}")
    shutil.copy2(path, PACKAGE_DIR / target_name)


def _write_ngc2841_row(source: Path, target_name: str) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing Paper 9 input: {source}")
    frame = pd.read_csv(source)
    if "galaxy" not in frame.columns:
        raise ValueError(f"No galaxy column in {source}")
    row = frame[frame["galaxy"] == "NGC2841"]
    if row.empty:
        raise ValueError(f"NGC2841 not present in {source}")
    row.to_csv(PACKAGE_DIR / target_name, index=False, quoting=csv.QUOTE_MINIMAL)


def _write_response_template() -> None:
    path = PACKAGE_DIR / "review_response_template.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RESPONSE_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(RESPONSE_ROWS)


def _write_manifest() -> None:
    files = sorted(p for p in PACKAGE_DIR.iterdir() if p.is_file() and p.name != "package_manifest.csv")
    manifest_rows = [
        {
            "file": path.name,
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in files
    ]
    with (PACKAGE_DIR / "package_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "sha256", "bytes"])
        writer.writeheader()
        writer.writerows(manifest_rows)


def _zip_package() -> None:
    for zip_path in [PACKAGE_ZIP, DOWNLOADS_ZIP]:
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(PACKAGE_DIR.iterdir()):
                if path.is_file():
                    zf.write(path, arcname=f"{PACKAGE_NAME}/{path.name}")


def main() -> None:
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    (PACKAGE_DIR / "README_REVIEWER.md").write_text(README, encoding="utf-8")
    for target_name, source in LOCAL_FILES.items():
        _copy(source, target_name)
    for target_name, source in PAPER9_ROW_FILES.items():
        _write_ngc2841_row(source, target_name)
    _write_response_template()
    _write_manifest()
    _zip_package()

    summary = {
        "package_dir": str(PACKAGE_DIR),
        "package_zip": str(PACKAGE_ZIP),
        "downloads_zip": str(DOWNLOADS_ZIP),
        "claim_boundary": CLAIM_BOUNDARY,
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "formula_freeze_permission": "no",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
