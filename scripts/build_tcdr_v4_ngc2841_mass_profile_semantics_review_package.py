from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LIT_DIR = ROOT / "data" / "external" / "literature" / "ngc2841_load_source_search"
PACKAGE_DIR = ROOT / "data" / "reviewer_packages"
DOWNLOADS_DIR = Path.home() / "Downloads"

ZHANG_SRC = LIT_DIR / "zhang2018_src"
ZHANG_TEX = ZHANG_SRC / "Zhang_accepted_2col.tex"
MASS_PROFILE_PDF = ZHANG_SRC / "prof_masses1and2_4.pdf"
MASS_PROFILE_PNG = (
    ROOT
    / "data"
    / "reviewer_packages"
    / "tcdr_v4_ngc2841_mass_profile_digitization_review_package_v0_1"
    / "zhang2018_mass_surface_density_profile.png"
)
TABLE_SEARCH = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_source_native_table_search_v0_1.csv"
TABLE_SEARCH_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_source_native_table_search_summary_v0_1.json"
SEMANTICS_CLARIFICATION = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_clarification_v0_1.csv"
SEMANTICS_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_semantics_clarification_summary_v0_1.json"
NORMALIZATION_AUDIT = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_normalization_audit_v0_1.csv"
DIGITIZATION_ACCEPTANCE = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance_v0_1.csv"

PACKAGE_STEM = "tcdr_v4_ngc2841_mass_profile_semantics_review_package_v0_1"
PACKAGE_ROOT = PACKAGE_DIR / PACKAGE_STEM
ZIP_PATH = PACKAGE_DIR / f"{PACKAGE_STEM}.zip"
DOWNLOADS_ZIP_PATH = DOWNLOADS_DIR / f"{PACKAGE_STEM}.zip"
OUT_JSON = SOURCE_DIR / f"{PACKAGE_STEM}_summary.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_semantics_review_package_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"

TEMPLATE_ROWS = [
    {
        "galaxy": "NGC2841",
        "question_id": "Q1_curve_identity",
        "question": (
            "Which Figure mass-profile curve(s) correspond to the isolated outer-disk "
            "stellar component whose integrated mass is quoted as 1.4e8 Msun beyond ~30 kpc?"
        ),
        "allowed_answer": (
            "same_as_measured_color|same_as_constant_outer_color|neither_displayed_curve|"
            "figure_total_profile_not_isolated_component|unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_lambda": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q2_normalization_mapping",
        "question": (
            "Is there a source-native normalization rule that maps the displayed "
            "Sigma_star(R) curve to the quoted integrated outer stellar mass?"
        ),
        "allowed_answer": (
            "yes_explicit_in_source|yes_derivable_from_source_only|no_not_in_source|unclear"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_lambda": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q3_axis_or_units_issue",
        "question": (
            "Can the tens-of-times mismatch be explained by a figure axis/units/digitization "
            "interpretation issue using only source-side information?"
        ),
        "allowed_answer": "yes_source_side_fix_found|no|unclear",
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_lambda": "must_be_false",
    },
    {
        "galaxy": "NGC2841",
        "question_id": "Q4_allowed_use",
        "question": (
            "Given Q1-Q3, should the mass profile remain shape-only, or can a "
            "load-bearing source-side formula be derived without endpoint information?"
        ),
        "allowed_answer": (
            "shape_only|load_formula_possible_with_explicit_source_rule|blocked_need_author_table"
        ),
        "reviewer_answer": "",
        "evidence_quote_or_note": "",
        "confidence": "high|medium|low|blocked",
        "endpoint_replay_permission": "must_be_no",
        "kernel_promotion_permission": "must_be_no",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_lambda": "must_be_false",
    },
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_source_excerpt(path: Path) -> None:
    source = ZHANG_TEX.read_text(encoding="utf-8", errors="replace")
    line_ranges = [(115, 140), (167, 176)]
    lines = source.splitlines()
    chunks: list[str] = []
    for start, end in line_ranges:
        chunks.append("\n".join(f"{idx}: {lines[idx - 1]}" for idx in range(start, end + 1)))
    path.write_text("\n\n---\n\n".join(chunks), encoding="utf-8")


def _write_instructions(path: Path) -> None:
    text = f"""# NGC2841 Dragonfly mass-profile semantics review package

This package asks a narrow source-side question for Paper 19 / TCDR-v4:
can the Zhang et al. mass-profile figure be converted into a load-bearing
outer-component formula without using any endpoint rotation information?

## Context

An earlier reviewer digitized the Dragonfly mass-profile figure. The response
passed leakage checks, but a source-side normalization audit found that naive
annular integration of the digitized profile is tens of times larger than the
quoted Zhang et al. integrated stellar mass beyond about 30 kpc. A separate
source-native table search found no machine-readable Sigma_star(R) or
Sigma_gas(R) table in the arXiv source package.

## Your task

Fill `review_response_template.csv`.

Do not digitize new points unless needed to support a source-side semantics
statement. The main questions are:

1. Which displayed curve, if any, corresponds to the isolated outer-disk
   component with quoted stellar mass 1.4e8 Msun?
2. Is there an explicit source-native normalization rule mapping the displayed
   profile to that integrated mass?
3. Can the tens-of-times mismatch be explained by source-side axis/unit/curve
   identity alone?
4. Should the profile remain shape-only, or can it become a load-bearing
   source formula without endpoint information?

## Forbidden inputs

Do not use:

- rotation curves or velocity data;
- SPARC observed velocity;
- endpoint residuals, RMSE, baseline scores, or Tau Core scores;
- required lambda or epsilon diagnostics;
- any answer chosen because it improves or worsens a rotation-curve fit.

The completed CSV must keep:

- `endpoint_replay_permission=must_be_no`;
- `kernel_promotion_permission=must_be_no`;
- `uses_rotation_curve_or_velocity=must_be_false`;
- `uses_endpoint_rotation_residual=must_be_false`;
- `uses_tau_core_score_or_required_lambda=must_be_false`.

## Included files

- `prof_masses1and2_4.pdf`: original mass-profile figure from the source package.
- `zhang2018_mass_surface_density_profile.png`: rendered convenience copy, if available.
- `Zhang_relevant_lines.txt`: relevant source text with line numbers.
- `source_native_table_search.csv/json`: negative search for machine-readable profile tables.
- `semantics_clarification.csv/json`: current blocker localization.
- `normalization_audit.csv`: ratio mismatch audit.
- `digitization_acceptance.csv`: earlier filled digitization acceptance artifact.
- `review_response_template.csv`: file to fill.

## Claim boundary

Package status: `{CLAIM_BOUNDARY}`.

This package cannot authorize endpoint replay. It can only support a later
source-side decision about whether the mass profile is shape-only or can be
promoted to a load-bearing formula under an explicit source-native rule.
"""
    path.write_text(text, encoding="utf-8")


def build_package() -> dict[str, object]:
    required = [
        ZHANG_TEX,
        MASS_PROFILE_PDF,
        TABLE_SEARCH,
        TABLE_SEARCH_SUMMARY,
        SEMANTICS_CLARIFICATION,
        SEMANTICS_SUMMARY,
        NORMALIZATION_AUDIT,
        DIGITIZATION_ACCEPTANCE,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required semantics package inputs: {missing}")

    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)
    PACKAGE_ROOT.mkdir(parents=True, exist_ok=True)

    shutil.copy2(MASS_PROFILE_PDF, PACKAGE_ROOT / MASS_PROFILE_PDF.name)
    if MASS_PROFILE_PNG.exists():
        shutil.copy2(MASS_PROFILE_PNG, PACKAGE_ROOT / MASS_PROFILE_PNG.name)
    shutil.copy2(TABLE_SEARCH, PACKAGE_ROOT / "source_native_table_search.csv")
    shutil.copy2(TABLE_SEARCH_SUMMARY, PACKAGE_ROOT / "source_native_table_search_summary.json")
    shutil.copy2(SEMANTICS_CLARIFICATION, PACKAGE_ROOT / "semantics_clarification.csv")
    shutil.copy2(SEMANTICS_SUMMARY, PACKAGE_ROOT / "semantics_clarification_summary.json")
    shutil.copy2(NORMALIZATION_AUDIT, PACKAGE_ROOT / "normalization_audit.csv")
    shutil.copy2(DIGITIZATION_ACCEPTANCE, PACKAGE_ROOT / "digitization_acceptance.csv")
    _write_source_excerpt(PACKAGE_ROOT / "Zhang_relevant_lines.txt")
    _write_csv(PACKAGE_ROOT / "review_response_template.csv", TEMPLATE_ROWS)
    _write_instructions(PACKAGE_ROOT / "README_REVIEWER.md")

    manifest_rows = [
        {
            "file": path.name,
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(PACKAGE_ROOT.iterdir())
        if path.is_file()
    ]
    _write_csv(PACKAGE_ROOT / "package_manifest.csv", manifest_rows)

    for zip_target in [ZIP_PATH, DOWNLOADS_ZIP_PATH]:
        if zip_target.exists():
            zip_target.unlink()
        with zipfile.ZipFile(zip_target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(PACKAGE_ROOT.iterdir()):
                archive.write(path, arcname=f"{PACKAGE_STEM}/{path.name}")

    summary = {
        "package_stem": PACKAGE_STEM,
        "package_dir": str(PACKAGE_ROOT.relative_to(ROOT)),
        "zip_path": str(ZIP_PATH.relative_to(ROOT)),
        "downloads_zip_path": str(DOWNLOADS_ZIP_PATH),
        "zip_sha256": _sha256(ZIP_PATH),
        "downloads_zip_sha256": _sha256(DOWNLOADS_ZIP_PATH),
        "n_manifest_rows": int(len(manifest_rows)),
        "included_files": [row["file"] for row in manifest_rows],
        "uses_vobs_or_residual": "no",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "new_route_scoring_permission": "no",
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Reviewer package prepared for source-side semantics review of the NGC2841 "
            "Dragonfly mass-profile normalization blocker. This is not endpoint replay "
            "authorization."
        ),
        "next_allowed_action": (
            "External reviewer fills review_response_template.csv. A later acceptance "
            "script may then decide whether the profile remains shape-only or has a "
            "source-native load formula route."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = build_package()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
