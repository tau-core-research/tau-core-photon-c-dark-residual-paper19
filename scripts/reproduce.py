from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def build_pdf() -> None:
    source = ROOT / "paper19_submission_source"
    if shutil.which("tectonic"):
        run(["tectonic", "main.tex"], cwd=source)
    elif shutil.which("latexmk"):
        run(["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"], cwd=source)
    elif shutil.which("pdflatex"):
        run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=source)
        run(["bibtex", "main"], cwd=source)
        run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=source)
        run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=source)
    else:
        raise RuntimeError("No LaTeX engine found: install tectonic, latexmk, or pdflatex.")


def main() -> None:
    run([sys.executable, "scripts/run_tcdr_toys.py"])
    run([sys.executable, "scripts/run_tcdr_robustness.py"])
    run([sys.executable, "scripts/run_tcdr_blind_challenge.py"])
    run([sys.executable, "scripts/run_tcdr_realistic_mock_challenge.py"])
    run([sys.executable, "scripts/build_tcdr_v4_real_data_manifest.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_pilot_holdout_manifest.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_kernel_coordinate_audit.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_bar_ring_decomposition_source_route.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_kernel_coordinate_freeze.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_component_mixture_audit.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_mixed_component_kernel_freeze.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_shuffled_component_nulls.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_native_radial_geometry_shuffled_component_nulls.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_frozen_formula_compiler_readiness.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_source_composition_uniqueness_audit.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_support_aware_component_selector_audit.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_support_safe_expansion_manifest.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_support_safe_expansion_opportunity_ledger.py"])
    run([sys.executable, "scripts/build_tcdr_v4_p0_support_safe_formula_completion_manifest.py"])
    run([sys.executable, "scripts/run_tcdr_v4_support_safe_pool_loocv_scoring.py"])
    run([sys.executable, "scripts/run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring.py"])
    run([sys.executable, "scripts/build_tcdr_v4_paper8_paper9_failure_overlay.py"])
    run([sys.executable, "scripts/build_tcdr_v4_paper8_paper9_scoring_readiness_ledger.py"])
    run([sys.executable, "scripts/run_tcdr_v4_paper8_paper9_readiness_filtered_scoring.py"])
    run([sys.executable, "scripts/run_tcdr_v4_readiness_filtered_metric_robustness.py"])
    run([sys.executable, "scripts/build_tcdr_v4_readiness_filtered_metric_robustness_figure.py"])
    run([sys.executable, "scripts/run_tcdr_v4_support_safe_mixed_route_shuffle_control.py"])
    run([sys.executable, "scripts/build_tcdr_v4_kobs_kreadout_source_review.py"])
    run([sys.executable, "scripts/build_tcdr_v4_paper8_paper9_scoring_route_closure.py"])
    run([sys.executable, "scripts/build_tcdr_v4_source_gap_blocker_ledger.py"])
    run([sys.executable, "scripts/build_tcdr_v4_source_gap_external_literature_audit.py"])
    run([sys.executable, "scripts/build_tcdr_v4_post_external_route_closure.py"])
    run([sys.executable, "scripts/build_tcdr_v4_post_external_scoring_boundary_summary.py"])
    run([sys.executable, "scripts/build_tcdr_v4_allowed_best_wrong_failure_diagnostic.py"])
    run([sys.executable, "scripts/build_tcdr_v4_allowed_failure_source_acquisition_worklist.py"])
    run([sys.executable, "scripts/build_tcdr_v4_allowed_failure_external_source_review.py"])
    run([sys.executable, "scripts/build_tcdr_v4_post_external_scoring_boundary_figure.py"])
    run([sys.executable, "scripts/build_figures.py"])
    build_pdf()
    run([sys.executable, "scripts/build_arxiv_source.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    print("PAPER19_PHOTON_C_DARK_RESIDUAL_REPRODUCTION_COMPLETE")


if __name__ == "__main__":
    main()
