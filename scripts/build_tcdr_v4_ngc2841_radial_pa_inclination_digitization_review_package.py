from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LITERATURE_DIR = ROOT / "data" / "external" / "literature"
PACKAGE_DIR = ROOT / "data" / "reviewer_packages"
DOWNLOADS_DIR = Path.home() / "Downloads"

FIGURE = LITERATURE_DIR / "bosma1981_ngc2841_figure4_6_7.jpg"
CANDIDATE = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate_v0_1.csv"
SCALAR_TABLE = SOURCE_DIR / "tcdr_v4_ngc2841_source_native_pa_inclination_table_v0_1.csv"
SEARCH_AUDIT = SOURCE_DIR / "tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit_v0_1.csv"

PACKAGE_STEM = "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package_v0_1"
PACKAGE_ROOT = PACKAGE_DIR / PACKAGE_STEM
ZIP_PATH = PACKAGE_DIR / f"{PACKAGE_STEM}.zip"
DOWNLOADS_ZIP_PATH = DOWNLOADS_DIR / f"{PACKAGE_STEM}.zip"
OUT_JSON = SOURCE_DIR / f"{PACKAGE_STEM}_summary.json"

CLAIM_BOUNDARY = "ngc2841_radial_pa_inclination_digitization_review_package_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"

TEMPLATE_ROWS = [
    {
        "galaxy": "NGC2841",
        "radius_kpc": "",
        "position_angle_deg": "",
        "inclination_deg": "",
        "source_panel": "Bosma_Fig7a_PA_and_Fig7b_inclination_only",
        "reviewer_id": "",
        "digitization_tool": "",
        "digitization_date_utc": "",
        "estimated_pa_uncertainty_deg": "",
        "estimated_inclination_uncertainty_deg": "",
        "quality_flag": "accepted|caveated|unreadable|out_of_range",
        "notes": "",
        "forbidden_inputs_acknowledged": "must_be_true",
        "uses_rotation_velocity_panel_c": "must_be_false",
        "uses_surface_density_panel_d": "must_be_false",
        "uses_endpoint_rotation_curve_or_residual": "must_be_false",
    }
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_instructions(path: Path) -> None:
    text = f"""# NGC2841 radial PA/inclination digitization review package

This package is a source-side review package for the Tau Core TCDR-v4/Paper 19
NGC2841 outer-capacity route.

## Task

Digitize only the radial position-angle and inclination profiles from the
included Bosma Figure 7 image:

- allowed: panel a, position angle;
- allowed: panel b, inclination;
- forbidden: panel c, rotation velocity;
- forbidden: panel d, surface density;
- forbidden: any endpoint rotation curve, residual, RMSE, baseline score, or
  Tau Core scoring result.

Fill `review_response_template.csv`. Use one row per digitized radius.

## Required verdict fields

Set these values consistently in the completed response:

- `forbidden_inputs_acknowledged=true`
- `uses_rotation_velocity_panel_c=false`
- `uses_surface_density_panel_d=false`
- `uses_endpoint_rotation_curve_or_residual=false`

If any forbidden information was used, do not provide a promoted profile.
Instead mark the package as failed/leaked in the notes.

## Included reference material

- `bosma1981_ngc2841_figure4_6_7.jpg`: source image to digitize.
- `source_native_scalar_pa_inclination_table.csv`: scalar PA/i crosschecks from
  THINGS/de Blok and Samurovic. These are not an answer key.
- `existing_coarse_candidate_do_not_copy.csv`: previous low-resolution internal
  candidate. Use only to understand expected column semantics, not as a source.
- `radial_table_search_audit.csv`: records that no primary machine-readable
  radial PA/i table was located in the bounded source pass.

## Claim boundary

Package status: `{CLAIM_BOUNDARY}`.

Completing this package can support a source-side formula-freeze review. It
does not authorize endpoint replay by itself.
"""
    path.write_text(text, encoding="utf-8")


def build_package() -> dict[str, object]:
    required = [FIGURE, CANDIDATE, SCALAR_TABLE, SEARCH_AUDIT]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required review package inputs: {missing}")

    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)
    PACKAGE_ROOT.mkdir(parents=True, exist_ok=True)

    shutil.copy2(FIGURE, PACKAGE_ROOT / FIGURE.name)
    shutil.copy2(SCALAR_TABLE, PACKAGE_ROOT / "source_native_scalar_pa_inclination_table.csv")
    shutil.copy2(CANDIDATE, PACKAGE_ROOT / "existing_coarse_candidate_do_not_copy.csv")
    shutil.copy2(SEARCH_AUDIT, PACKAGE_ROOT / "radial_table_search_audit.csv")
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
        "forbidden_inputs": (
            "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
            "Bosma_Fig7c_rotation_velocity;Bosma_Fig7d_surface_density"
        ),
        "uses_vobs_or_residual": "no",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "new_route_scoring_permission": "no",
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Reviewer package prepared for independent source-side digitization of "
            "NGC2841 radial PA/inclination from Bosma Figure 7 panels a and b. "
            "The package is not an endpoint replay authorization."
        ),
        "next_allowed_action": (
            "External reviewer completes review_response_template.csv. A separate "
            "source-side acceptance script may then check leakage flags, uncertainties, "
            "and consistency with scalar PA/i support before any formula-freeze decision."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = build_package()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
