from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
PACKAGE_ROOT = ROOT / "data" / "reviewer_packages"
PACKAGE_NAME = "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_reviewer_package_v0_1"
PACKAGE_DIR = PACKAGE_ROOT / PACKAGE_NAME
PACKAGE_ZIP = PACKAGE_ROOT / f"{PACKAGE_NAME}.zip"
DOWNLOADS_ZIP = Path.home() / "Downloads" / f"{PACKAGE_NAME}.zip"

CLAIM_BOUNDARY = "ngc2841_beta_closure_endpoint_authorization_reviewer_package_not_scoring"

LOCAL_FILES = {
    "beta_context_formula_freeze_review.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_v0_1.csv",
    "beta_context_formula_freeze_review_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_summary_v0_1.json",
    "k_beta_profile_freeze_review.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_v0_1.csv",
    "k_beta_profile_freeze_review_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_summary_v0_1.json",
    "baryonic_carrier_freeze_review.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_v0_1.csv",
    "baryonic_carrier_freeze_review_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_summary_v0_1.json",
    "review_response_acceptance.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_v0_1.csv",
    "review_response_acceptance_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json",
    "multiplicative_beta_preflight.csv": SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_v0_1.csv",
    "multiplicative_beta_preflight_summary.json": SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_summary_v0_1.json",
}

README = """# NGC2841 beta/closure endpoint authorization reviewer package

This package asks one bounded question:

Can the frozen NGC2841 beta/closure context formula be handed to a separate
endpoint scoring script unchanged?

This is not a scoring package and contains no endpoint results. It only contains
the frozen source-side formula-review artifacts.

## Frozen formula

`v_beta_context^2(R)=v_carrier^2(R)*[1+(beta_context-1)*K_beta_shape(R)]`

where:

- `beta_context = 1.0803447810919469`, retained only as a caveated
  dimensionless context coefficient, not as a direct physical spin measurement;
- `K_beta_shape(R)` is the accepted Bosma Fig. 7a/7b PA/inclination shape,
  min-max normalized and interpolated onto the carrier grid;
- `v_carrier^2(R)=sign(Vgas)Vgas^2 + 0.5 Vdisk^2 + 0.7 Vbul^2`, read only from
  SPARC source-side component columns.

## What you are allowed to decide

Fill `review_response_template.csv`.

You may authorize a future endpoint replay only if all of the following are
true:

1. the scoring script must read the frozen formula profile unchanged;
2. no formula term may be retuned after inspecting observed rotation data;
3. no morphology/readout label may be changed from endpoint performance;
4. the result must be reported as a single-object preliminary endpoint/control
   replay, not as validation;
5. the caveated `beta_context` coefficient must remain caveated and must not be
   described as a direct spin measurement.

## Forbidden inputs

Do not use:

- observed rotation curves or velocity residuals;
- SPARC `Vobs`/`errV`;
- endpoint RMSE, baseline scores, wrong-family ranks, or Tau Core endpoint scores;
- required `A_tau`, required lambda, or observed velocity gap diagnostics;
- any answer chosen because it improves or worsens a rotation-curve fit.

## Included files

- `beta_context_formula_freeze_review.csv/json`
- `k_beta_profile_freeze_review.csv/json`
- `baryonic_carrier_freeze_review.csv/json`
- `review_response_acceptance.csv/json`
- `multiplicative_beta_preflight.csv/json`
- `review_response_template.csv`

## Claim boundary

Package status: `ngc2841_beta_closure_endpoint_authorization_reviewer_package_not_scoring`.

Authorization, if granted, means only that a future separate scoring script may
read the frozen formula unchanged. It is not an empirical validation claim.
"""

RESPONSE_ROWS = [
    {
        "galaxy": "NGC2841",
        "question_id": "Q1_formula_integrity",
        "question": "Are all formula terms source-frozen before endpoint scoring?",
        "allowed_answer": "authorize_unchanged_formula_replay|block_formula_not_frozen|block_unclear",
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "may_be_yes_only_if_authorized",
        "formula_retuning_allowed": "must_be_no",
        "morphology_relabel_allowed": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q2_beta_context_boundary",
        "question": (
            "Is beta_context correctly bounded as a caveated context coefficient, "
            "not a direct source-native physical spin measurement?"
        ),
        "allowed_answer": "accept_caveated_beta_context|block_overclaims_spin|block_unclear",
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "may_be_yes_only_if_authorized",
        "formula_retuning_allowed": "must_be_no",
        "morphology_relabel_allowed": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q3_endpoint_scope",
        "question": (
            "If replay is allowed, what scope may be claimed for the result?"
        ),
        "allowed_answer": (
            "single_object_preliminary_control_replay_only|"
            "diagnostic_only_no_endpoint|block_unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "may_be_yes_only_if_authorized",
        "formula_retuning_allowed": "must_be_no",
        "morphology_relabel_allowed": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_load": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q4_final_authorization",
        "question": "May a separate endpoint scoring replay be prepared from this frozen formula?",
        "allowed_answer": (
            "authorize_endpoint_replay_preliminary_control|"
            "block_endpoint_replay|diagnostic_only_no_endpoint|block_unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "may_be_yes_only_if_authorized",
        "formula_retuning_allowed": "must_be_no",
        "morphology_relabel_allowed": "must_be_no",
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


def _write_response_template() -> None:
    path = PACKAGE_DIR / "review_response_template.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RESPONSE_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(RESPONSE_ROWS)


def _write_manifest() -> None:
    files = sorted(p for p in PACKAGE_DIR.iterdir() if p.is_file() and p.name != "package_manifest.csv")
    rows = [
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
        writer.writerows(rows)


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
    _write_response_template()
    _write_manifest()
    _zip_package()

    summary = {
        "package_dir": str(PACKAGE_DIR),
        "package_zip": str(PACKAGE_ZIP),
        "downloads_zip": str(DOWNLOADS_ZIP),
        "claim_boundary": CLAIM_BOUNDARY,
        "contains_endpoint_scores": False,
        "endpoint_replay_permission": "requires_completed_external_authorization",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
