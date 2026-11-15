from __future__ import annotations

import csv
import json
import tarfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LIT_DIR = ROOT / "data" / "external" / "literature" / "ngc2841_load_source_search"

ZHANG_SRC = LIT_DIR / "zhang2018_src"
ZHANG_TEX = ZHANG_SRC / "Zhang_accepted_2col.tex"
ZHANG_TAR = LIT_DIR / "zhang2018_arxiv_source.tar"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_source_native_table_search_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_mass_profile_source_native_table_search_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_mass_profile_source_native_table_search_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
FORBIDDEN_INPUTS = (
    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
    "required_epsilon_fit;required_lambda_fit;observed_velocity_gap"
)


def _tar_members() -> list[str]:
    if not ZHANG_TAR.exists():
        return []
    with tarfile.open(ZHANG_TAR) as archive:
        return sorted(member.name for member in archive.getmembers())


def _tex_contains(fragment: str) -> bool:
    if not ZHANG_TEX.exists():
        return False
    return fragment in ZHANG_TEX.read_text(encoding="utf-8", errors="replace")


def build_source_native_table_search() -> tuple[pd.DataFrame, dict[str, object]]:
    if not ZHANG_TAR.exists() and OUT_CSV.exists() and OUT_JSON.exists():
        return pd.read_csv(OUT_CSV), json.loads(OUT_JSON.read_text(encoding="utf-8"))
    members = _tar_members()
    machine_table_like = [
        name
        for name in members
        if Path(name).suffix.lower()
        in {".csv", ".tsv", ".dat", ".txt", ".fits", ".fit", ".ecsv", ".vot", ".xml"}
    ]
    figure_members = [
        name
        for name in members
        if Path(name).name
        in {
            "prof_masses1and2_4.pdf",
            "profile_original.pdf",
            "profile_withjpg.pdf",
            "prof_timescales1and2_4.pdf",
        }
    ]

    text_checks = {
        "stellar_gas_profile_figure_statement": _tex_contains(
            "The stellar and the gas mass surface density profiles of NGC 2841 are shown"
        ),
        "measured_color_and_constant_color_variants": _tex_contains(
            "we explored the impact of color on the inferred mass density using two different approaches"
        ),
        "outer_3_to_1_ratio_statement": _tex_contains(
            "ratio of stellar mass to gas mass remains remarkably constant"
        ),
        "outer_integrated_mass_statement": _tex_contains(
            "The total stellar mass in the disk beyond"
        ),
    }

    rows = [
        {
            "galaxy": "NGC2841",
            "search_target": "arxiv_source_machine_readable_profile_table",
            "source_reference": "Zhang2018NGC2841Dragonfly",
            "source_url": "https://arxiv.org/abs/1802.02583",
            "local_artifact": str(ZHANG_TAR.relative_to(ROOT)),
            "search_result": "not_found_in_arxiv_source_package",
            "evidence": (
                "The local arXiv source tar lists TeX and figure PDFs, but no CSV/TSV/DAT/FITS/"
                "VOTable-style source-native table for Sigma_star(R) or Sigma_gas(R)."
            ),
            "machine_table_like_members": ";".join(machine_table_like),
            "figure_members": ";".join(figure_members),
            "allowed_use": "negative_source_finding_only",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "new_route_scoring_permission": "no",
        },
        {
            "galaxy": "NGC2841",
            "search_target": "published_tex_component_semantics",
            "source_reference": "Zhang2018NGC2841Dragonfly",
            "source_url": "https://arxiv.org/e-print/1802.02583",
            "local_artifact": str(ZHANG_TEX.relative_to(ROOT)),
            "search_result": "text_supports_semantics_split",
            "evidence": (
                "The TeX source separately describes the Figure mass-surface-density profiles, "
                "the measured-color/constant-color variants, the approximately 3:1 outer "
                "stellar/gas ratio, and the total stellar mass beyond about 30 kpc."
            ),
            "machine_table_like_members": "",
            "figure_members": "prof_masses1and2_4.pdf",
            "allowed_use": "source_semantics_context_not_load",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "new_route_scoring_permission": "no",
        },
        {
            "galaxy": "NGC2841",
            "search_target": "component_normalization_resolution",
            "source_reference": "Zhang2018NGC2841Dragonfly",
            "source_url": "https://doi.org/10.3847/1538-4357/aaac81",
            "local_artifact": str(ZHANG_TEX.relative_to(ROOT)),
            "search_result": "blocked_requires_author_or_source_native_component_model",
            "evidence": (
                "The available source package does not specify a machine-readable mapping from "
                "the displayed profile curves to the isolated outer-disk integrated mass. The "
                "digitized profile therefore cannot be normalized into a load-bearing formula."
            ),
            "machine_table_like_members": "",
            "figure_members": "prof_masses1and2_4.pdf",
            "allowed_use": "shape_candidate_only",
            "endpoint_replay_permission": "no",
            "kernel_promotion_permission": "no",
            "new_route_scoring_permission": "no",
        },
    ]
    frame = pd.DataFrame(rows)
    frame["uses_vobs_or_residual"] = "no"
    frame["forbidden_inputs"] = FORBIDDEN_INPUTS
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "arxiv_source_members": members,
        "machine_table_like_members": machine_table_like,
        "figure_members": figure_members,
        "text_checks": text_checks,
        "source_native_profile_table_found": False,
        "component_normalization_resolved": False,
        "formula_ready": False,
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().sort_index().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().sort_index().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().sort_index().to_dict(),
        "uses_vobs_or_residual_counts": frame["uses_vobs_or_residual"].value_counts().sort_index().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "No source-native machine-readable Zhang et al. mass-profile table was found in "
            "the arXiv source package. The source text supports the semantics split between "
            "displayed surface-density profiles and the quoted integrated outer-disk mass, "
            "but does not resolve the normalization mapping. The profile remains shape-only."
        ),
        "next_allowed_action": (
            "Either contact/ask a reviewer to confirm the Figure curve identity and component "
            "normalization, or obtain an independent source-native component model/table."
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_source_native_table_search()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
