from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CLEAN_CLONE_SKIP_MESSAGE = (
    "[SKIP-CLEAN-CLONE] Optional external SPARC MRT files not present; "
    "verified committed derived artifacts"
)

CORE_CLEAN_CLONE_SCRIPTS = [
    "scripts/run_tcdr_toys.py",
    "scripts/run_tcdr_robustness.py",
    "scripts/run_tcdr_blind_challenge.py",
    "scripts/run_tcdr_realistic_mock_challenge.py",
    "scripts/build_tcdr_v4_real_data_manifest.py",
    "scripts/build_tcdr_v4_p0_pilot_holdout_manifest.py",
    "scripts/build_tcdr_v4_p0_source_native_kernel_coordinate_audit.py",
    "scripts/build_tcdr_v4_p0_bar_ring_decomposition_source_route.py",
    "scripts/build_tcdr_v4_p0_source_native_kernel_coordinate_freeze.py",
    "scripts/build_tcdr_v4_p0_source_native_component_mixture_audit.py",
    "scripts/build_tcdr_v4_p0_source_native_mixed_component_kernel_freeze.py",
    "scripts/build_tcdr_v4_p0_source_native_shuffled_component_nulls.py",
    "scripts/build_tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze.py",
    "scripts/build_tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls.py",
    "scripts/build_tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze.py",
    "scripts/build_tcdr_v4_p0_source_native_radial_geometry_shuffled_component_nulls.py",
    "scripts/build_tcdr_v4_p0_source_frozen_formula_compiler_readiness.py",
    "scripts/build_tcdr_v4_p0_source_composition_uniqueness_audit.py",
    "scripts/build_tcdr_v4_p0_support_aware_component_selector_audit.py",
    "scripts/build_tcdr_v4_p0_support_safe_expansion_manifest.py",
    "scripts/build_tcdr_v4_p0_support_safe_expansion_opportunity_ledger.py",
    "scripts/build_tcdr_v4_p0_support_safe_formula_completion_manifest.py",
]

EXTERNAL_SPARC_PIPELINE_SCRIPTS = [
    "scripts/run_tcdr_v4_support_safe_pool_loocv_scoring.py",
    "scripts/run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring.py",
    "scripts/build_tcdr_v4_paper8_paper9_failure_overlay.py",
    "scripts/build_tcdr_v4_paper8_paper9_scoring_readiness_ledger.py",
    "scripts/run_tcdr_v4_paper8_paper9_readiness_filtered_scoring.py",
    "scripts/run_tcdr_v4_readiness_filtered_metric_robustness.py",
    "scripts/build_tcdr_v4_readiness_filtered_metric_robustness_figure.py",
    "scripts/run_tcdr_v4_support_safe_mixed_route_shuffle_control.py",
    "scripts/build_tcdr_v4_kobs_kreadout_source_review.py",
    "scripts/build_tcdr_v4_paper8_paper9_scoring_route_closure.py",
    "scripts/build_tcdr_v4_source_gap_blocker_ledger.py",
    "scripts/build_tcdr_v4_source_gap_external_literature_audit.py",
    "scripts/build_tcdr_v4_post_external_route_closure.py",
    "scripts/build_tcdr_v4_post_external_scoring_boundary_summary.py",
    "scripts/build_tcdr_v4_allowed_best_wrong_failure_diagnostic.py",
    "scripts/build_tcdr_v4_allowed_failure_source_acquisition_worklist.py",
    "scripts/build_tcdr_v4_allowed_failure_external_source_review.py",
    "scripts/build_tcdr_v4_allowed_failure_numeric_source_freeze.py",
    "scripts/build_tcdr_v4_allowed_failure_formula_freeze_readiness.py",
    "scripts/build_tcdr_v4_allowed_failure_numeric_observable_worklist.py",
    "scripts/build_tcdr_v4_allowed_failure_spiral_path_formula_freeze.py",
    "scripts/build_tcdr_v4_allowed_failure_scoring_preflight.py",
    "scripts/run_tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring.py",
    "scripts/build_tcdr_v4_ngc2841_absolute_residual_gap_diagnostic.py",
    "scripts/build_tcdr_v4_ngc2841_outer_capacity_requirement_audit.py",
    "scripts/build_tcdr_v4_ngc2841_outer_capacity_source_search.py",
    "scripts/build_tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist.py",
    "scripts/build_tcdr_v4_ngc2841_outer_capacity_policy_freeze.py",
    "scripts/build_tcdr_v4_ngc2841_tilted_ring_geometry_source_review.py",
    "scripts/build_tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate.py",
    "scripts/build_tcdr_v4_ngc2841_source_native_pa_inclination_table.py",
    "scripts/build_tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit.py",
    "scripts/build_tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package.py",
    "scripts/build_tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance.py",
    "scripts/build_tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review.py",
    "scripts/build_tcdr_v4_ngc2841_tilted_ring_formula_rule_review.py",
    "scripts/build_tcdr_v4_ngc2841_projection_sign_load_derivation.py",
    "scripts/build_tcdr_v4_ngc2841_outer_capacity_load_source_derivation.py",
    "scripts/build_tcdr_v4_ngc2841_outer_capacity_load_source_search.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_source_native_table_search.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_digitization_review_package.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_normalization_audit.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_semantics_clarification.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_semantics_review_package.py",
    "scripts/build_tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance.py",
    "scripts/build_tcdr_v4_ngc2841_surviving_route_ledger.py",
    "scripts/build_tcdr_v4_ngc2841_projection_control_preflight.py",
    "scripts/run_tcdr_v4_ngc2841_projection_control_diagnostic_replay.py",
    "scripts/build_tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze.py",
    "scripts/run_tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_diagnostic.py",
    "scripts/build_tcdr_v4_ngc2841_post_control_positive_load_gap_diagnostic.py",
    "scripts/build_tcdr_v4_ngc2841_required_positive_load_scale_worklist.py",
    "scripts/build_tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze.py",
    "scripts/build_tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze.py",
    "scripts/build_tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze.py",
    "scripts/build_tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit.py",
    "scripts/build_tcdr_v4_ngc2841_mom0_disk_load_promotion_review.py",
    "scripts/build_tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze.py",
    "scripts/build_tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit.py",
    "scripts/build_tcdr_v4_ngc2841_independent_multiplier_rejection_audit.py",
    "scripts/build_tcdr_v4_ngc2841_tau_side_load_theorem_readiness.py",
    "scripts/build_tcdr_v4_ngc2841_related_paper_proxy_transfer_audit.py",
    "scripts/build_tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_reformulation_label_review.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_endpoint_authorization_reviewer_package.py",
    "scripts/build_tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance.py",
    "scripts/run_tcdr_v4_ngc2841_beta_closure_endpoint_control_replay.py",
    "scripts/run_tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay.py",
    "scripts/run_tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay.py",
    "scripts/build_tcdr_v4_allowed_failure_spiral_path_diagnostic_figure.py",
    "scripts/build_tcdr_v4_post_external_scoring_boundary_figure.py",
]


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def has_external_sparc_inputs(root: Path = ROOT) -> bool:
    if os.environ.get("TCDR_FORCE_CLEAN_CLONE") == "1":
        return False
    sparc_dir = root / "data" / "external" / "sparc_preflight"
    return (
        (sparc_dir / "SPARC_Lelli2016c.mrt").exists()
        and (sparc_dir / "MassModels_Lelli2016c.mrt").exists()
    )


def verify_committed_clean_clone_artifacts(root: Path = ROOT) -> None:
    required = [
        root / "data" / "derived" / "tcdr_summary.csv",
        root / "data" / "derived" / "tcdr_summary.json",
        root / "data" / "derived" / "tcdr_multiseed_robustness_summary.csv",
        root / "data" / "derived" / "tcdr_threshold_sensitivity.csv",
        root / "data" / "derived" / "tcdr_blind_challenge_summary.csv",
        root / "data" / "derived" / "tcdr_realistic_mock_challenge_summary.csv",
        root / "data" / "derived" / "tcdr_realistic_mock_threshold_curve.csv",
        root / "data" / "source_manifests" / "tcdr_v4_real_data_source_manifest_v0_1.csv",
        root / "data" / "source_manifests" / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv",
        root / "data" / "source_manifests" / "tcdr_v4_p0_holdout_endpoint_readiness_v0_1.csv",
        root / "data" / "source_manifests" / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv",
        root / "figures" / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay.png",
        root / "figures" / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay.png",
        root / "figures" / "tcdr_readiness_filtered_metric_robustness.png",
        root / "figures" / "tcdr_post_external_scoring_boundary.png",
        root / "figures" / "tcdr_ngc2841_spiral_path_diagnostic_replay.png",
    ]
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing committed clean-clone artifacts: {missing}")
    print(CLEAN_CLONE_SKIP_MESSAGE)


def run_external_or_verify(root: Path = ROOT) -> str:
    if has_external_sparc_inputs(root):
        for script in EXTERNAL_SPARC_PIPELINE_SCRIPTS:
            run([sys.executable, script], cwd=root)
        return "live_external_scoring"
    verify_committed_clean_clone_artifacts(root)
    return "clean_clone_verified"


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
    for script in CORE_CLEAN_CLONE_SCRIPTS:
        run([sys.executable, script])
    run_external_or_verify(ROOT)
    run([sys.executable, "scripts/build_figures.py"])
    build_pdf()
    run([sys.executable, "scripts/build_arxiv_source.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    print("PAPER19_PHOTON_C_DARK_RESIDUAL_REPRODUCTION_COMPLETE")


if __name__ == "__main__":
    main()
