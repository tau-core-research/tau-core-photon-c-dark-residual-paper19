from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LIT_DIR = ROOT / "data" / "external" / "literature" / "ngc2841_load_source_search"
PACKAGE_DIR = ROOT / "data" / "reviewer_packages"
DOWNLOADS_DIR = Path.home() / "Downloads"

ZHANG_SOURCE_TEX = LIT_DIR / "zhang2018_src" / "Zhang_accepted_2col.tex"
MASS_PROFILE_PDF = LIT_DIR / "zhang2018_src" / "prof_masses1and2_4.pdf"
SOURCE_SEARCH = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_search_v0_1.csv"
SOURCE_SUMMARY = SOURCE_DIR / "tcdr_v4_ngc2841_outer_capacity_load_source_search_summary_v0_1.json"

PACKAGE_STEM = "tcdr_v4_ngc2841_mass_profile_digitization_review_package_v0_1"
PACKAGE_ROOT = PACKAGE_DIR / PACKAGE_STEM
ZIP_PATH = PACKAGE_DIR / f"{PACKAGE_STEM}.zip"
DOWNLOADS_ZIP_PATH = DOWNLOADS_DIR / f"{PACKAGE_STEM}.zip"
OUT_JSON = SOURCE_DIR / f"{PACKAGE_STEM}_summary.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_digitization_review_package_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


TEMPLATE_ROWS = [
    {
        "galaxy": "NGC2841",
        "radius_kpc": "",
        "sigma_star_msun_pc2": "",
        "sigma_gas_msun_pc2": "",
        "sigma_star_to_gas_ratio": "",
        "profile_variant": "measured_color|constant_outer_color|unclear",
        "source_panel": "Zhang2018_Fig_mass_surface_density_only",
        "reviewer_id": "",
        "digitization_tool": "",
        "digitization_date_utc": "",
        "estimated_radius_uncertainty_kpc": "",
        "estimated_sigma_uncertainty_dex": "",
        "quality_flag": "accepted|caveated|unreadable|out_of_range",
        "notes": "",
        "forbidden_inputs_acknowledged": "must_be_true",
        "uses_rotation_curve_or_velocity": "must_be_false",
        "uses_endpoint_rotation_residual": "must_be_false",
        "uses_tau_core_score_or_required_lambda": "must_be_false",
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


def _render_profile_png() -> Path | None:
    if not shutil.which("pdftoppm"):
        return None
    prefix = PACKAGE_ROOT / "zhang2018_mass_surface_density_profile"
    subprocess.run(
        ["pdftoppm", "-png", "-singlefile", "-r", "240", str(MASS_PROFILE_PDF), str(prefix)],
        check=True,
    )
    png = prefix.with_suffix(".png")
    return png if png.exists() else None


def _write_instructions(path: Path) -> None:
    text = f"""# NGC2841 Dragonfly mass-profile digitization review package

This package is a source-side review package for the Tau Core TCDR-v4/Paper 19
NGC2841 outer-capacity load route.

## Task

Digitize only the mass-surface-density profile in Zhang et al. (2018),
`prof_masses1and2_4.pdf`.

Allowed quantities:

- radius in kpc;
- stellar mass surface density, Sigma_star [M_sun pc^-2];
- gas mass surface density, Sigma_gas [M_sun pc^-2];
- optional Sigma_star/Sigma_gas ratio if read directly from the same figure;
- profile variant if visually distinguishable: measured color, constant outer
  color, or unclear.

Forbidden quantities:

- any rotation curve or velocity data;
- SPARC observed velocity;
- endpoint residuals, RMSE, baseline scores, or Tau Core scores;
- required lambda or required epsilon diagnostics;
- any choice of points designed to improve a rotation-curve fit.

Fill `review_response_template.csv`. Use one row per digitized radius. If the
figure is unreadable at a radius, mark `quality_flag=unreadable` rather than
guessing.

## Required leakage flags

The completed CSV must set:

- `forbidden_inputs_acknowledged=true`
- `uses_rotation_curve_or_velocity=false`
- `uses_endpoint_rotation_residual=false`
- `uses_tau_core_score_or_required_lambda=false`

If any forbidden information was used, do not promote the profile. Mark the
response as leaked/failed in the notes.

## Included files

- `prof_masses1and2_4.pdf`: original arXiv source figure.
- `zhang2018_mass_surface_density_profile.png`: rendered convenience copy, if
  Poppler was available when the package was built.
- `Zhang_accepted_2col_excerpt.txt`: source text lines documenting the formula,
  mass ratio, and outer stellar mass statements.
- `load_source_search.csv` and `load_source_search_summary.json`: the local
  source-side audit that explains why this review package is needed.
- `review_response_template.csv`: file to fill.

## Claim boundary

Package status: `{CLAIM_BOUNDARY}`.

Completing this package can support a future source-side load-profile
acceptance review. It does not authorize endpoint replay or kernel promotion by
itself.
"""
    path.write_text(text, encoding="utf-8")


def _write_source_excerpt(path: Path) -> None:
    source = ZHANG_SOURCE_TEX.read_text(encoding="utf-8", errors="replace")
    needles = [
        "The stellar and the gas mass surface density profiles",
        "\\Sigma_{\\text{gas}}",
        "ratio of stellar mass to gas mass remains",
        "The total stellar mass in the disk beyond",
    ]
    paragraphs: list[str] = []
    for needle in needles:
        idx = source.find(needle)
        if idx == -1:
            continue
        start = max(0, source.rfind("\n", 0, idx - 500))
        end = source.find("\n\n", idx)
        if end == -1:
            end = min(len(source), idx + 1200)
        paragraphs.append(source[start:end].strip())
    path.write_text("\n\n---\n\n".join(paragraphs), encoding="utf-8")


def build_package() -> dict[str, object]:
    required = [ZHANG_SOURCE_TEX, MASS_PROFILE_PDF, SOURCE_SEARCH, SOURCE_SUMMARY]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required review package inputs: {missing}")

    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)
    PACKAGE_ROOT.mkdir(parents=True, exist_ok=True)

    shutil.copy2(MASS_PROFILE_PDF, PACKAGE_ROOT / MASS_PROFILE_PDF.name)
    png = _render_profile_png()
    _write_source_excerpt(PACKAGE_ROOT / "Zhang_accepted_2col_excerpt.txt")
    shutil.copy2(SOURCE_SEARCH, PACKAGE_ROOT / "load_source_search.csv")
    shutil.copy2(SOURCE_SUMMARY, PACKAGE_ROOT / "load_source_search_summary.json")
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
        "png_rendered": png is not None,
        "n_manifest_rows": int(len(manifest_rows)),
        "included_files": [row["file"] for row in manifest_rows],
        "forbidden_inputs": (
            "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
            "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
        ),
        "uses_vobs_or_residual": "no",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "new_route_scoring_permission": "no",
        "endpoint_data_policy": ENDPOINT_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "Reviewer package prepared for independent source-side digitization of "
            "the NGC2841 Dragonfly stellar/gas mass-surface-density profile. The "
            "package is not an endpoint replay authorization."
        ),
        "next_allowed_action": (
            "External reviewer completes review_response_template.csv. A separate "
            "source-side acceptance script may then check leakage flags, units, "
            "monotonicity/caveats, and conversion readiness."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = build_package()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
