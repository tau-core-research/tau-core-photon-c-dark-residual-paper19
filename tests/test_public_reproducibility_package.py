from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_publication_artifacts_exist() -> None:
    assert (ROOT / "paper19_submission_source" / "main.tex").exists()
    assert (ROOT / "paper19_submission_source" / "main.pdf").exists()
    assert (ROOT / "arxiv_submission_source.zip").exists()
    assert (ROOT / "data" / "derived" / "tcdr_summary.csv").exists()
    assert (ROOT / "data" / "derived" / "tcdr_multiseed_robustness_summary.csv").exists()
    assert (ROOT / "data" / "derived" / "tcdr_threshold_sensitivity.csv").exists()
    assert (ROOT / "data" / "derived" / "tcdr_blind_challenge_summary.csv").exists()
    assert (ROOT / "data" / "derived" / "tcdr_realistic_mock_challenge_summary.csv").exists()
    assert (ROOT / "data" / "derived" / "tcdr_realistic_mock_threshold_curve.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_real_data_source_manifest_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_sparc_source_freeze_queue_summary_v0_1.json").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_lookup_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_lookup_summary_v0_1.json").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_coordinate_lookup_summary_v0_1.json").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_simbad_fallback_lookup_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_simbad_fallback_lookup_summary_v0_1.json").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_tier_manifest_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_tier_manifest_summary_v0_1.json").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_family_freeze_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_family_freeze_summary_v0_1.json").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_pilot_holdout_manifest_summary_v0_1.json").exists()
    assert (
        ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_native_kernel_coordinate_audit_v0_1.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_kernel_coordinate_audit_summary_v0_1.json"
    ).exists()
    assert (
        ROOT / "data" / "source_manifests" / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_bar_ring_decomposition_source_route_summary_v0_1.json"
    ).exists()
    assert (
        ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_component_mixture_audit_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_v0_1.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_shuffled_component_nulls_v0_1.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_shuffled_component_nulls_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_v0_2.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_summary_v0_2.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls_v0_2.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls_summary_v0_2.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_summary_v0_4.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_composition_uniqueness_audit_v0_5.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_source_composition_uniqueness_audit_summary_v0_5.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_aware_component_selector_audit_v0_6.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_aware_component_selector_audit_summary_v0_6.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_safe_expansion_manifest_v0_7.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_safe_expansion_manifest_summary_v0_7.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_safe_expansion_opportunity_ledger_v0_8.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_safe_expansion_opportunity_ledger_summary_v0_8.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_safe_formula_completion_manifest_v0_9.csv"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_p0_support_safe_formula_completion_manifest_summary_v0_9.json"
    ).exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_holdout_endpoint_readiness_v0_1.csv").exists()
    assert (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_holdout_endpoint_readiness_summary_v0_1.json").exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_allowed_failure_numeric_source_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_summary_v0_1.json"
    ).exists()
    sparc_ext = ROOT / "data" / "external" / "sparc_preflight"
    has_sparc_ext = (
        (sparc_ext / "SPARC_Lelli2016c.mrt").exists()
        and (sparc_ext / "MassModels_Lelli2016c.mrt").exists()
    )
    if has_sparc_ext:
        assert (
            sparc_ext
            / "tcdr_v4_allowed_failure_scoring_preflight_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_absolute_residual_gap_diagnostic_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_beta_closure_endpoint_control_replay_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_outer_capacity_requirement_audit_summary_local.json"
        ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_policy_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_projection_control_preflight_summary_v0_1.json"
    ).exists()
    if has_sparc_ext:
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.json"
        ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_summary_v0_1.json"
    ).exists()
    if has_sparc_ext:
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.json"
        ).exists()
        assert (
            sparc_ext
            / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json"
        ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tau_side_load_theorem_readiness_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance_summary_v0_1.json"
    ).exists()
    assert (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate_summary_v0_1.json"
    ).exists()
    lit_dir = ROOT / "data" / "external" / "literature"
    if lit_dir.exists() and any(lit_dir.iterdir()):
        assert (lit_dir / "bosma1981_ngc2841_figure4_6_7.jpg").exists()
    assert (ROOT / "figures" / "tcdr_ngc2841_spiral_path_diagnostic_replay.png").exists()


def test_summary_contains_expected_modules_and_scores() -> None:
    rows = list(csv.DictReader((ROOT / "data" / "derived" / "tcdr_summary.csv").open()))
    assert {row["module"] for row in rows} == {"TCDR-v1", "TCDR-v2", "TCDR-v3"}
    assert len(rows) == 13
    max_scores = {}
    for row in rows:
        max_scores[row["module"]] = max(max_scores.get(row["module"], 0), int(row["score"]))
    assert max_scores == {"TCDR-v1": 5, "TCDR-v2": 4, "TCDR-v3": 3}


def test_manuscript_claim_boundary() -> None:
    text = (ROOT / "paper19_submission_source" / "main.tex").read_text(encoding="utf-8")
    required = [
        "does not prove Tau Core",
        "does not detect dark matter residuals",
        "controlled synthetic protocol paper",
        "realistic nuisance robustness",
        "real-data source manifest",
        "SPARC dynamics products",
        "endpoint/baseline inputs only",
        "P0\\_SOURCE\\_REVIEW",
        "S4G\\ matched\\ by\\ name",
        "S4G\\ coordinate\\ matched",
        "SIMBAD\\ morphology\\ type\\ available",
        "S4G\\_STRONG",
        "K\\_BARRED\\_M2",
        "PILOT\\_HOLDOUT",
        "PILOT\\_TRAIN\\_POOL",
        "endpoint-readiness only",
        "TCDR-v4",
    ]
    for marker in required:
        assert marker in text
    forbidden = [
        "This paper proves Tau Core",
        "Therefore dark matter is false",
        "This is a validated physical theory",
    ]
    for marker in forbidden:
        assert marker not in text


def test_arxiv_zip_is_source_only() -> None:
    zip_path = ROOT / "arxiv_submission_source.zip"
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    assert "main.tex" in names
    assert "refs.bib" in names
    assert "main.pdf" not in names
    assert any(name.startswith("figures/") and name.endswith(".png") for name in names)
    assert not any(".pytest_cache" in name or "__pycache__" in name for name in names)


def test_multiseed_robustness_has_null_and_positive_cases() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "derived" / "tcdr_multiseed_robustness_summary.csv").open()
        )
    )
    assert len(rows) == 7
    null_rows = [row for row in rows if float(row["tau_strength"]) == 0.0]
    assert len(null_rows) == 3
    for row in null_rows:
        assert float(row["false_positive_rate"]) <= 0.35
    positive_rows = [row for row in rows if float(row["tau_strength"]) > 0.0]
    assert positive_rows
    assert max(float(row["pass_rate_floor"]) for row in positive_rows) >= 0.75


def test_blind_challenge_keeps_null_controls_visible() -> None:
    row = next(
        csv.DictReader(
            (ROOT / "data" / "derived" / "tcdr_blind_challenge_summary.csv").open()
        )
    )
    assert int(row["n_challenges"]) == 26
    assert int(row["n_null"]) == 8
    assert float(row["accuracy"]) >= 0.70
    assert float(row["false_positive_rate"]) <= 0.20


def test_realistic_mock_challenge_is_specificity_first() -> None:
    row = next(
        csv.DictReader(
            (ROOT / "data" / "derived" / "tcdr_realistic_mock_challenge_summary.csv").open()
        )
    )
    assert int(row["n_challenges"]) == 32
    assert int(row["n_null"]) == 10
    assert float(row["false_positive_rate"]) <= 0.10
    assert float(row["true_positive_rate"]) >= 0.35


def test_real_data_manifest_separates_source_labels_from_endpoints() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_real_data_source_manifest_v0_1.csv").open()
        )
    )
    assert rows
    endpoint_rows = [row for row in rows if "endpoint" in row["tcdr_role"]]
    assert endpoint_rows
    for row in endpoint_rows:
        assert row["allowed_for_source_label"] == "no"
    source_rows = [row for row in rows if row["allowed_for_source_label"] == "yes"]
    assert source_rows
    for row in source_rows:
        assert row["allowed_for_endpoint_scoring"] == "no"


def test_sparc_source_freeze_queue_excludes_rotation_endpoints() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_sparc_source_freeze_queue_v0_1.csv").open()
        )
    )
    assert len(rows) == 175
    forbidden_columns = {"Vflat", "vflat", "e_Vflat", "rotation_residual", "delta_r2"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    priorities = {row["source_review_priority"] for row in rows}
    assert {"P0_SOURCE_REVIEW", "P1_SOURCE_REVIEW", "P2_SOURCE_REVIEW"}.issubset(priorities)
    for row in rows:
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_for_source_label"


def test_p0_s4g_lookup_is_source_side_only() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_lookup_v0_1.csv").open()
        )
    )
    assert len(rows) == 66
    matched = [row for row in rows if row["s4g_lookup_status"] == "matched_by_name"]
    assert len(matched) == 32
    forbidden_columns = {"Vflat", "vflat", "rotation_residual", "delta_r2", "score"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in matched:
        assert row["source_freeze_policy"] == "source_side_morphology_available_before_endpoint_scoring"


def test_p0_s4g_coordinate_lookup_is_source_side_only() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv").open()
        )
    )
    assert len(rows) == 34
    matched = [row for row in rows if row["coordinate_lookup_status"] == "matched_by_coordinate"]
    assert len(matched) == 11
    forbidden_columns = {"Vflat", "vflat", "rotation_residual", "delta_r2", "score"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in matched:
        assert float(row["nearest_sep_arcmin"]) <= 1.0
        assert row["source_freeze_policy"] == "source_side_morphology_available_by_coordinate_before_endpoint_scoring"


def test_p0_simbad_fallback_lookup_is_source_side_only() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_simbad_fallback_lookup_v0_1.csv").open()
        )
    )
    assert len(rows) == 23
    resolved = [row for row in rows if row["simbad_lookup_status"] != "not_resolved"]
    with_morphology = [row for row in rows if row["simbad_lookup_status"] == "resolved_with_morphology"]
    assert len(resolved) == 23
    assert len(with_morphology) == 22
    forbidden_columns = {"Vflat", "vflat", "rotation_residual", "delta_r2", "score"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in with_morphology:
        assert row["source_freeze_policy"] == "simbad_source_side_morphology_available_before_endpoint_scoring"


def test_p0_source_tier_manifest_is_freeze_ready_without_endpoint_fields() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_tier_manifest_v0_1.csv").open()
        )
    )
    assert len(rows) == 66
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["source_tier"]] = counts.get(row["source_tier"], 0) + 1
    assert counts == {
        "S4G_STRONG": 32,
        "S4G_COORD_RESCUE": 11,
        "SIMBAD_FALLBACK": 22,
        "SIMBAD_IDENTITY_ONLY": 1,
    }
    forbidden_columns = {"Vflat", "vflat", "rotation_residual", "delta_r2", "score"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert sum(1 for row in rows if row["homogeneous_structural_morphology"] == "yes") == 43
    assert sum(1 for row in rows if row["morphology_type"]) == 65
    for row in rows:
        assert row["source_freeze_policy"] == "source_tier_may_be_frozen_before_endpoint_scoring"
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_for_source_tier"


def test_p0_source_family_freeze_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_source_family_freeze_v0_1.csv").open()
        )
    )
    assert len(rows) == 66
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["source_family_candidate"]] = counts.get(row["source_family_candidate"], 0) + 1
    assert counts == {
        "K_BARRED_M2": 30,
        "K_COMPACT_EARLY_DISK": 5,
        "K_DIFFUSE_LATE_DISK": 6,
        "K_EXPONENTIAL_SPIRAL_DISK": 14,
        "K_RING_RESONANCE": 10,
        "K_UNFREEZABLE_IDENTITY_ONLY": 1,
    }
    forbidden_columns = {"Vflat", "vflat", "rotation_residual", "delta_r2", "score"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert sum(1 for row in rows if row["freeze_strength"] == "freeze_ready_homogeneous_s4g") == 43
    assert sum(1 for row in rows if row["projection_caveat"] == "yes") == 10
    for row in rows:
        assert row["source_family_policy"] == "freeze_before_endpoint_scoring"
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_for_family_selection"


def test_p0_pilot_holdout_manifest_is_endpoint_blind_and_balanced() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv").open()
        )
    )
    assert len(rows) == 66
    role_counts: dict[str, int] = {}
    family_holdout_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["pilot_role"]] = role_counts.get(row["pilot_role"], 0) + 1
        if row["pilot_role"] == "PILOT_HOLDOUT":
            family = row["source_family_candidate"]
            family_holdout_counts[family] = family_holdout_counts.get(family, 0) + 1
    assert role_counts == {
        "NON_HOMOGENEOUS_SOURCE_TIER": 23,
        "PILOT_HOLDOUT": 7,
        "PILOT_TRAIN_POOL": 36,
    }
    assert family_holdout_counts == {
        "K_BARRED_M2": 2,
        "K_DIFFUSE_LATE_DISK": 1,
        "K_EXPONENTIAL_SPIRAL_DISK": 2,
        "K_RING_RESONANCE": 2,
    }
    forbidden_columns = {"Vflat", "vflat", "rotation_residual", "delta_r2", "score"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert (
            row["pilot_selection_policy"]
            == "endpoint_blind_homogeneous_s4g_family_balanced_calibration_aware_projection_caveat_no_first_then_galaxy_name"
        )
        assert row["min_train_per_family"] == "1"
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_for_pilot_holdout_selection"


def test_p0_source_native_kernel_coordinate_audit_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_kernel_coordinate_audit_v0_1.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["kernel_coordinate_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_for_kernel_coordinate_audit"
        assert row["claim_boundary"] == "source_proxy_coordinate_audit_not_endpoint_scoring"
    assert status_counts == {
        "not_in_first_homogeneous_s4g_pilot": 5,
        "not_kernel_freeze_ready": 1,
        "partial_source_proxy_disk_hi_coordinates_available": 14,
        "source_proxy_only_needs_bar_decomposition": 30,
        "source_proxy_only_needs_ring_decomposition": 10,
        "underpowered_family_needs_more_train_support": 6,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_bar_ring_decomposition_source_route_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["bar_ring_decomposition_route_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_source_route"
        assert row["claim_boundary"] == "source_native_coordinate_route_not_kernel_validation"
    assert status_counts == {
        "compact_family_not_primary_bar_ring_route": 5,
        "diffuse_family_needs_additional_lsb_hi_support": 6,
        "disk_scale_proxy_available_no_spiral_feature": 12,
        "not_kernel_route_ready": 1,
        "source_native_feature_bar_available": 12,
        "source_native_feature_ring_available": 4,
        "source_native_spiral_pitch_available": 2,
        "source_proxy_only_bar_decomposition_missing": 18,
        "source_proxy_only_ring_decomposition_missing": 6,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert sum(1 for row in rows if int(row["p4_row_count"]) > 0) == 31
    assert sum(1 for row in rows if int(row["feature_row_count"]) > 0) == 21
    assert sum(1 for row in rows if int(row["spiral_row_count"]) > 0) == 16


def test_kobs_kreadout_review_blocks_ngc0024_relabel() -> None:
    review_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_kobs_kreadout_source_review_local.csv"
    )
    closure_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_paper8_paper9_scoring_route_closure_local.csv"
    )
    if not review_path.exists() or not closure_path.exists():
        return

    review_rows = list(
        csv.DictReader(
            review_path.open()
        )
    )
    assert len(review_rows) == 2
    assert {row["galaxy"] for row in review_rows} == {"NGC0024"}
    for row in review_rows:
        assert row["source_spiral_relabel_support"] == "no"
        assert row["kobs_kreadout_replay_permission"] == "no"
        assert row["kobs_kreadout_review_status"] == "KREADOUT_RELABEL_BLOCKED_BROAD_FAMILY_ONLY"

    closure_rows = list(
        csv.DictReader(
            closure_path.open()
        )
    )
    ngc0024 = [row for row in closure_rows if row["galaxy"] == "NGC0024"]
    assert len(ngc0024) == 2
    for row in ngc0024:
        assert row["final_route_status"] == "KOBS_KREADOUT_RELABEL_BLOCKED_BY_SOURCE_REVIEW"
        assert row["final_endpoint_replay_permission"] == "no"


def test_source_gap_ledger_keeps_unsupported_spiral_controls_blocked() -> None:
    source_gap_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_source_gap_blocker_ledger_local.csv"
    )
    if not source_gap_path.exists():
        return
    rows = list(csv.DictReader(source_gap_path.open()))
    assert len(rows) == 5
    assert {row["candidate_gap_component"] for row in rows} == {"spiral"}
    assert {row["gap_component_source_supported"] for row in rows} == {"no"}
    assert {row["source_gap_blocker_class"] for row in rows} == {
        "BLOCKED_WRONG_COMPONENT_OUTSIDE_SOURCE_FAMILY"
    }


def test_readiness_filtered_metric_robustness_preserves_strict_count() -> None:
    robustness_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_readiness_filtered_metric_robustness_local.csv"
    )
    if not robustness_path.exists():
        return
    rows = list(csv.DictReader(robustness_path.open()))
    by_metric: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_metric.setdefault(row["metric"], []).append(row)
    assert set(by_metric) == {"weighted_rmse_kms", "rmse_kms"}
    for metric_rows in by_metric.values():
        assert len(metric_rows) == 6
        assert sum(row["candidate_beats_best_wrong_metric"] == "yes" for row in metric_rows) == 3


def test_source_gap_external_literature_audit_does_not_promote_routes() -> None:
    audit_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_source_gap_external_literature_audit_local.csv"
    )
    if not audit_path.exists():
        return
    rows = list(csv.DictReader(audit_path.open()))
    assert len(rows) == 5
    assert {row["external_literature_route_permission"] for row in rows} == {
        "keep_source_gap_blocked"
    }


def test_post_external_route_closure_keeps_only_current_formula_rows_ready() -> None:
    closure_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_post_external_route_closure_local.csv"
    )
    if not closure_path.exists():
        return
    rows = list(csv.DictReader(closure_path.open()))
    assert len(rows) == 17
    allowed = [
        row
        for row in rows
        if row["post_external_endpoint_replay_permission"].startswith("yes")
    ]
    assert len(allowed) == 6
    assert {row["post_external_route_status"] for row in allowed} == {
        "CURRENT_FORMULA_REPLAY_READY"
    }
    source_gap = [
        row
        for row in rows
        if row["post_external_route_status"]
        == "SOURCE_GAP_BLOCKED_AFTER_EXTERNAL_AUDIT"
    ]
    assert len(source_gap) == 5
    assert {row["external_literature_route_permission"] for row in source_gap} == {
        "keep_source_gap_blocked"
    }


def test_post_external_scoring_boundary_scores_only_allowed_rows() -> None:
    boundary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_post_external_scoring_boundary_local.csv"
    )
    if not boundary_path.exists():
        return
    rows = list(csv.DictReader(boundary_path.open()))
    assert len(rows) == 17
    allowed = [
        row
        for row in rows
        if row["post_external_endpoint_replay_permission"].startswith("yes")
    ]
    blocked = [
        row
        for row in rows
        if not row["post_external_endpoint_replay_permission"].startswith("yes")
    ]
    assert len(allowed) == 6
    assert len(blocked) == 11
    assert sum(row["candidate_beats_baryonic"] == "yes" for row in allowed) == 6
    assert sum(row["candidate_beats_wrong_component_mean"] == "yes" for row in allowed) == 6
    assert sum(row["candidate_beats_best_wrong_component"] == "yes" for row in allowed) == 3
    assert all(row["candidate_beats_baryonic"] == "" for row in blocked)
    assert all(row["candidate_beats_wrong_component_mean"] == "" for row in blocked)


def test_post_external_scoring_boundary_figure_exists() -> None:
    figure_path = ROOT / "figures" / "tcdr_post_external_scoring_boundary.png"
    if not figure_path.exists():
        return
    assert figure_path.stat().st_size > 10_000


def test_allowed_best_wrong_failure_diagnostic_does_not_promote_mixed_routes() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_best_wrong_failure_diagnostic_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_allowed_rows"] == 6
    assert summary["n_strict_positive_rows"] == 3
    assert summary["n_strict_best_wrong_failures"] == 3
    assert summary["strict_failure_source_visible_secondary_count"] == 0
    assert summary["diagnostic_class_counts"] == {
        "STRICT_POSITIVE_CURRENT_FORMULA": 3,
        "METRIC_SENSITIVE_FALSE_COMPONENT_PRESSURE_NO_SOURCE_ROUTE": 2,
        "NEAR_TIE_FALSE_COMPONENT_NO_SOURCE_ROUTE": 1,
    }
    assert summary["claim_boundary"] == "allowed_best_wrong_failure_diagnostic_local_not_kernel_promotion"


def test_allowed_failure_source_acquisition_worklist_blocks_replay() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_failure_source_acquisition_worklist_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 3
    assert summary["n_unique_galaxies"] == 2
    assert summary["unique_galaxies"] == ["NGC2841", "UGC00191"]
    assert summary["best_wrong_component_counts"] == {"spiral": 3}
    assert summary["all_endpoint_replay_permission"] == ["no"]
    assert summary["all_kernel_promotion_permission"] == ["no"]
    assert summary["claim_boundary"] == "allowed_failure_source_acquisition_worklist_not_replay_permission"


def test_allowed_failure_external_source_review_still_blocks_endpoint_replay() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_failure_external_source_review_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 2
    assert summary["n_worklist_rows_covered"] == 3
    assert summary["galaxies"] == ["NGC2841", "UGC00191"]
    assert summary["source_review_status_counts"] == {
        "CAVEATED_SPIRAL_PATH_SOURCE_FOUND_REVIEW_ONLY": 1,
        "WEAK_ASYMMETRY_SOURCE_FOUND_NOT_SPIRAL_ROUTE_CLOSING": 1,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 2}
    assert summary["kernel_promotion_permission_counts"] == {"no": 2}
    assert summary["claim_boundary"] == "allowed_failure_external_source_review_not_endpoint_replay"


def test_allowed_failure_formula_freeze_readiness_still_blocks_new_scoring() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_failure_formula_freeze_readiness_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 2
    assert summary["galaxies"] == ["NGC2841", "UGC00191"]
    assert summary["formula_freeze_readiness_status_counts"] == {
        "ROUTE_REVIEW_OPEN_NUMERIC_SOURCE_FIELDS_FROZEN_FORMULA_FREEZE_READY": 1,
        "ROUTE_REVIEW_BLOCKED_WEAK_ASYMMETRY_NOT_SPIRAL_PATH_FORMULA": 1,
    }
    assert summary["source_side_route_review_permission_counts"] == {
        "yes_caveated_spiral_path_formula_freeze_ready_no_scoring": 1,
        "no_spiral_path_formula_freeze_review": 1,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 2}
    assert summary["kernel_promotion_permission_counts"] == {"no": 2}
    assert summary["new_route_scoring_permission_counts"] == {"no": 2}
    assert summary["claim_boundary"] == "allowed_failure_formula_freeze_readiness_not_endpoint_replay"


def test_allowed_failure_numeric_observable_worklist_is_source_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_failure_numeric_observable_worklist_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["galaxies"] == ["NGC2841", "UGC00191"]
    assert summary["rows_by_galaxy"] == {"NGC2841": 4, "UGC00191": 1}
    assert summary["priority_counts"] == {
        "P1_REQUIRED_FOR_SPIRAL_PATH_FORMULA_FREEZE": 4,
        "P2_REQUIRED_BEFORE_FORMULA_FREEZE_REVIEW_CAN_OPEN": 1,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["new_route_scoring_permission_counts"] == {"no": 5}
    assert summary["claim_boundary"] == "allowed_failure_numeric_observable_worklist_not_formula_freeze_not_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "external"
                / "sparc_preflight"
                / "tcdr_v4_allowed_failure_numeric_observable_worklist_local.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert row["endpoint_data_policy"] == "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"
        assert "rotation_curve" in row["forbidden_inputs"]


def test_allowed_failure_numeric_source_freeze_is_source_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_allowed_failure_numeric_source_freeze_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["n_galaxies"] == 2
    assert summary["numeric_source_freeze_status_counts"] == {
        "frozen_caveated_numeric_source": 4,
        "not_frozen_missing_route_closing_source": 1,
    }
    assert round(float(summary["ngc2841_r25_kpc_computed"]), 6) == 16.611171
    assert round(float(summary["ngc2841_break_0p45r25_kpc_computed"]), 6) == 7.475027
    assert summary["formula_freeze_permission_counts"] == {"no": 5}
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["new_route_scoring_permission_counts"] == {"no": 5}
    assert summary["claim_boundary"] == "allowed_failure_numeric_source_freeze_not_formula_not_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_allowed_failure_numeric_source_freeze_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    ngc_rows = [row for row in rows if row["galaxy"] == "NGC2841"]
    assert len(ngc_rows) == 4
    assert {row["numeric_source_freeze_status"] for row in ngc_rows} == {
        "frozen_caveated_numeric_source"
    }


def test_allowed_failure_spiral_path_formula_freeze_is_not_scoring_permission() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 2
    assert summary["galaxies"] == ["NGC2841", "UGC00191"]
    assert summary["formula_freeze_status_counts"] == {
        "frozen_caveated_source_formula_no_scoring": 1,
        "not_frozen_route_review_blocked": 1,
    }
    assert summary["formula_freeze_permission_counts"] == {
        "no": 1,
        "yes_source_formula_frozen_no_scoring": 1,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 2}
    assert summary["kernel_promotion_permission_counts"] == {"no": 2}
    assert summary["new_route_scoring_permission_counts"] == {"no": 2}
    assert summary["frozen_formula_ids"] == ["F_CAVEATED_SPIRAL_PATH_WINDOW_SOURCE_FROZEN"]
    assert summary["claim_boundary"] == "allowed_failure_spiral_path_formula_freeze_not_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_allowed_failure_spiral_path_formula_freeze_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    ngc = next(row for row in rows if row["galaxy"] == "NGC2841")
    assert ngc["formula_id"] == "F_CAVEATED_SPIRAL_PATH_WINDOW_SOURCE_FROZEN"
    assert ngc["dimension_check"] == "pass_positive_ordered_kpc_radii"
    assert round(float(ngc["r_in_kpc"]), 6) == 7.475027
    assert round(float(ngc["r_out_kpc"]), 6) == 16.611171
    assert round(float(ngc["r_path_kpc"]), 6) == 30.0
    assert float(ngc["epsilon_path"]) <= 0.20
    assert ngc["endpoint_replay_permission"] == "no"
    assert ngc["new_route_scoring_permission"] == "no"


def test_allowed_failure_scoring_preflight_blocks_endpoint_scoring() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_failure_scoring_preflight_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["n_galaxies"] == 2
    assert summary["galaxies"] == ["NGC2841", "UGC00191"]
    assert summary["filled_requested_observables"] == 4
    assert summary["missing_requested_observables"] == 1
    assert summary["row_scoring_preflight_status_counts"] == {
        "REQUESTED_SOURCE_OBSERVABLE_AND_FORMULA_FROZEN_AUTHORIZATION_REQUIRED": 4,
        "SCORING_BLOCKED_ROUTE_REVIEW_NOT_OPEN": 1,
    }
    assert summary["galaxy_scoring_preflight_status_counts"] == {
        "SCORING_PREFLIGHT_FORMULA_FROZEN_AUTHORIZATION_REQUIRED": 1,
        "SCORING_BLOCKED_ROUTE_REVIEW_NOT_OPEN": 1,
    }
    assert summary["formula_freeze_status_counts"] == {
        "formula_frozen_no_scoring": 4,
        "formula_not_frozen": 1,
    }
    assert summary["formula_freeze_permission_counts"] == {
        "yes_source_formula_frozen_no_scoring": 4,
        "no": 1,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["new_route_scoring_permission_counts"] == {"no": 5}
    assert summary["claim_boundary"] == "allowed_failure_scoring_preflight_not_endpoint_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "external"
                / "sparc_preflight"
                / "tcdr_v4_allowed_failure_scoring_preflight_local.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert "rotation_curve" in row["forbidden_inputs_checked"]


def test_allowed_failure_spiral_path_diagnostic_scoring_is_not_validation() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 2
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["formula_ids"] == ["F_CAVEATED_SPIRAL_PATH_WINDOW_SOURCE_FROZEN"]
    assert summary["diagnostic_status_counts"] == {
        "diagnostic_replay_completed_no_validation": 2,
    }
    assert summary["endpoint_validation_claimed_counts"] == {"no": 2}
    assert summary["kernel_promotion_permission_counts"] == {"no": 2}
    assert summary["spiral_path_beats_current_formula_counts"] == {"yes": 2}
    assert summary["spiral_path_beats_best_wrong_counts"] == {"yes": 2}
    assert summary["spiral_path_beats_baryonic_counts"] == {"yes": 2}
    assert "target_galaxy_formula_shape_source_frozen" in summary["amplitude_policy"]
    assert "no_target_amplitude_tuning" in summary["amplitude_policy"]
    assert summary["claim_boundary"] == "allowed_failure_spiral_path_diagnostic_scoring_not_validation"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "external"
                / "sparc_preflight"
                / "tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring_summary_local.csv"
            ).open()
        )
    )
    assert {row["support_safe_pool"] for row in rows} == {
        "support_safe_7_v0_7",
        "support_safe_10_v0_9",
    }
    for row in rows:
        assert row["diagnostic_scoring_status"] == "diagnostic_replay_completed_no_validation"
        assert row["endpoint_validation_claimed"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["new_route_scoring_permission"] == "diagnostic_only_no_promotion"


def test_ngc2841_absolute_residual_gap_diagnostic_preserves_deficit() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_absolute_residual_gap_diagnostic_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["zones"] == ["inner_lt_10kpc", "mid_10_30kpc", "outer_ge_30kpc"]
    assert summary["verdict_counts"] == {
        "large_capacity_deficit_not_solved_by_spiral_path_shell": 4,
        "large_outer_capacity_deficit_requires_independent_outer_path_or_dark_residual_source": 2,
    }
    assert summary["median_pred_over_obs_by_zone"]["outer_ge_30kpc"] < 0.50
    assert summary["median_missing_v2_fraction_by_zone"]["outer_ge_30kpc"] > 0.80
    assert summary["claim_boundary"] == "ngc2841_absolute_residual_gap_diagnostic_not_kernel_repair"


def test_ngc2841_outer_capacity_requirement_audit_blocks_amplitude_rescue() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_outer_capacity_requirement_audit_summary_local.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["zones"] == ["inner_lt_10kpc", "mid_10_30kpc", "outer_ge_30kpc"]
    assert summary["capacity_verdict_counts"] == {
        "capacity_requirement_exceeds_source_frozen_path_cap": 4,
        "outer_capacity_requires_new_independent_dark_residual_or_path_source": 2,
    }
    assert summary["epsilon_path_cap"] < 0.13
    assert summary["median_required_epsilon_by_zone"]["outer_ge_30kpc"] > 20.0
    assert summary["median_required_to_cap_ratio_by_zone"]["outer_ge_30kpc"] > 180.0
    assert summary["claim_boundary"] == "ngc2841_outer_capacity_requirement_audit_not_kernel_repair"


def test_ngc2841_outer_capacity_source_search_is_source_side_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_source_search_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["n_strong_source_candidates"] == 3
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["endpoint_replay_permission_counts"] == {"no": 6}
    assert summary["kernel_promotion_permission_counts"] == {"no": 6}
    assert summary["forbidden_endpoint_inputs_used_counts"] == {"no": 6}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 6}
    assert summary["claim_boundary"] == "ngc2841_outer_capacity_source_search_not_formula_not_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_outer_capacity_source_search_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    strong_ids = {
        row["source_id"]
        for row in rows
        if row["source_status"].startswith("STRONG")
    }
    assert strong_ids == {
        "dragonfly_extended_stellar_hi_uv_disk",
        "bosma_extended_hi_warp_tilted_ring",
        "galex_xuv_hi_outer_star_formation",
    }
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_outer_capacity_formula_freeze_worklist_blocks_scoring() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 8
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["formula_ready"] is False
    assert summary["candidate_numeric_or_lower_bound_fields"] == 5
    assert summary["blocked_formula_fields"] == 2
    assert summary["not_frozen_formula_fields"] == 3
    assert summary["endpoint_replay_permission_counts"] == {"no": 8}
    assert summary["kernel_promotion_permission_counts"] == {"no": 8}
    assert summary["new_route_scoring_permission_counts"] == {"no": 8}
    assert (
        summary["claim_boundary"]
        == "ngc2841_outer_capacity_formula_freeze_worklist_not_formula_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    field_status = {row["requested_field"]: row["formula_freeze_status"] for row in rows}
    assert field_status["tilted_ring_geometry_profile"] == "blocked_needs_source_native_geometry_extraction"
    assert field_status["outer_component_weight_rule"] == "blocked_needs_residual_blind_component_weight_rule"
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert "required_epsilon_fit" in row["forbidden_inputs"]


def test_ngc2841_outer_capacity_policy_freeze_closes_only_source_policies() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_policy_freeze_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 4
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["onset_priority_blocker_closed"] is True
    assert summary["component_weight_blocker_closed"] is True
    assert summary["xuv_exact_shape_blocker_closed"] is False
    assert summary["tilted_ring_geometry_blocker_closed"] is False
    assert summary["formula_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 4}
    assert summary["kernel_promotion_permission_counts"] == {"no": 4}
    assert summary["new_route_scoring_permission_counts"] == {"no": 4}
    assert summary["claim_boundary"] == "ngc2841_outer_capacity_policy_freeze_not_formula_not_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_outer_capacity_policy_freeze_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    policies = {row["policy_id"]: row for row in rows}
    assert policies["P_NGC2841_NESTED_OUTER_ONSET_V0_1"]["formula_use_permission"] == (
        "yes_policy_only_no_scoring"
    )
    assert policies["P_NGC2841_MAX_ENTROPY_STRONG_ROUTE_WEIGHTS_V0_1"][
        "formula_use_permission"
    ] == "yes_policy_only_no_scoring"
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert "required_epsilon_fit" in row["forbidden_inputs"]


def test_ngc2841_tilted_ring_geometry_source_review_is_not_formula_freeze() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["geometry_route_supported"] is True
    assert summary["exact_tilted_ring_numeric_profile_frozen"] is False
    assert summary["digitization_or_native_table_required"] is True
    assert summary["endpoint_replay_permission_counts"] == {"no": 6}
    assert summary["kernel_promotion_permission_counts"] == {"no": 6}
    assert summary["new_route_scoring_permission_counts"] == {"no": 6}
    assert summary["forbidden_endpoint_inputs_used_counts"] == {"no": 6}
    assert summary["claim_boundary"] == "ngc2841_tilted_ring_geometry_source_review_not_formula_not_scoring"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    freeze_status = {row["geometry_item"]: row["formula_freeze_status"] for row in rows}
    assert freeze_status["annular_tilted_ring_model"] == "numeric_profile_requires_digitization_or_table"
    assert (
        freeze_status["figure7_profile_availability"]
        == "blocked_needs_source_side_digitization_or_native_table"
    )
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"
        assert "required_epsilon_fit" in row["forbidden_inputs"]


def test_ngc2841_tilted_ring_digitized_profile_candidate_is_review_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 13
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["figure_sha256"] == "f21c99f58e35a04401578573ad75e568b21ac387e81eb8e35ed02532eb5e66b1"
    assert summary["figure_image_size_px"] == [360, 805]
    assert summary["digitized_panels_used"] == [
        "figure7a_position_angle",
        "figure7b_inclination",
    ]
    assert "figure7c_rotation_velocity" in summary["digitized_panels_excluded"]
    assert summary["position_angle_delta_deg"] >= 10.0
    assert summary["inclination_delta_deg"] >= 14.0
    assert summary["formula_ready"] is False
    assert summary["profile_use_permission_counts"] == {"review_candidate_only_no_scoring": 13}
    assert summary["endpoint_replay_permission_counts"] == {"no": 13}
    assert summary["kernel_promotion_permission_counts"] == {"no": 13}
    assert summary["new_route_scoring_permission_counts"] == {"no": 13}
    assert summary["forbidden_endpoint_inputs_used_counts"] == {"no": 13}
    assert summary["claim_boundary"] == "ngc2841_tilted_ring_digitized_profile_candidate_not_endpoint"

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert all(row["profile_use_permission"] == "review_candidate_only_no_scoring" for row in rows)
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["uses_vobs_or_residual"] == "no" for row in rows)
    assert all("figure7c_rotation_velocity" in row["forbidden_inputs"] for row in rows)


def test_ngc2841_source_native_pa_inclination_table_is_scalar_support_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_source_native_pa_inclination_table_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 4
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["has_source_native_numeric_pa_inclination_scalar"] is True
    assert summary["has_source_native_numeric_radial_pa_inclination_table"] is False
    assert summary["has_published_figure_radial_pa_inclination_profile"] is True
    assert summary["position_angle_deg_values"] == [152.6, 150.7]
    assert summary["inclination_deg_values"] == [69.0, 73.7, 73.5]
    assert summary["formula_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 4}
    assert summary["kernel_promotion_permission_counts"] == {"no": 4}
    assert summary["new_route_scoring_permission_counts"] == {"no": 4}
    assert summary["forbidden_endpoint_inputs_used_counts"] == {"no": 4}
    assert (
        summary["claim_boundary"]
        == "ngc2841_source_native_pa_inclination_table_not_radial_formula_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_source_native_pa_inclination_table_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_source = {row["source_id"]: row for row in rows}
    assert (
        by_source["DEBLOK2008_THINGS_TABLE2_TILTED_RING_MEAN_PA_INCLINATION"][
            "formula_use_permission"
        ]
        == "scalar_geometry_support_only_no_radial_kernel_freeze"
    )
    assert (
        by_source["BOSMA1981_FIGURE7_PA_INCLINATION_PROFILE"]["formula_use_permission"]
        == "review_candidate_only_requires_digitization_or_native_table"
    )
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["uses_vobs_or_residual"] == "no" for row in rows)
    assert all("required_epsilon_fit" in row["forbidden_inputs"] for row in rows)


def test_ngc2841_radial_pa_inclination_table_search_audit_keeps_kernel_blocked() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 4
    assert summary["has_source_native_numeric_radial_pa_inclination_table"] is False
    assert summary["has_source_native_numeric_scalar_pa_inclination_support"] is True
    assert summary["has_figure_level_radial_pa_inclination_profile"] is True
    assert summary["radial_kernel_formula_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 4}
    assert summary["kernel_promotion_permission_counts"] == {"no": 4}
    assert summary["new_route_scoring_permission_counts"] == {"no": 4}
    assert summary["forbidden_endpoint_inputs_used_counts"] == {"no": 4}
    assert (
        summary["claim_boundary"]
        == "ngc2841_radial_pa_inclination_table_search_audit_not_formula_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_source = {row["source_checked"]: row for row in rows}
    assert (
        by_source["general_web_primary_source_pass"]["source_status"]
        == "no_primary_machine_readable_radial_pa_i_table_found"
    )
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["kernel_promotion_permission"] == "no" for row in rows)
    assert all(row["uses_vobs_or_residual"] == "no" for row in rows)


def test_ngc2841_radial_pa_inclination_digitization_review_package_is_source_side() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package_v0_1_summary.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_manifest_rows"] == 6
    assert "review_response_template.csv" in summary["included_files"]
    assert "bosma1981_ngc2841_figure4_6_7.jpg" in summary["included_files"]
    assert "source_native_scalar_pa_inclination_table.csv" in summary["included_files"]
    assert "existing_coarse_candidate_do_not_copy.csv" in summary["included_files"]
    assert summary["uses_vobs_or_residual"] == "no"
    assert summary["endpoint_replay_permission"] == "no"
    assert summary["kernel_promotion_permission"] == "no"
    assert summary["new_route_scoring_permission"] == "no"
    assert "Bosma_Fig7c_rotation_velocity" in summary["forbidden_inputs"]
    assert "Bosma_Fig7d_surface_density" in summary["forbidden_inputs"]
    assert (
        summary["claim_boundary"]
        == "ngc2841_radial_pa_inclination_digitization_review_package_not_scoring"
    )
    zip_path = ROOT / summary["zip_path"]
    assert zip_path.exists()
    package_dir = ROOT / summary["package_dir"]
    template = package_dir / "review_response_template.csv"
    assert template.exists()
    rows = list(csv.DictReader(template.open()))
    assert rows[0]["uses_rotation_velocity_panel_c"] == "must_be_false"
    assert rows[0]["uses_surface_density_panel_d"] == "must_be_false"
    assert rows[0]["uses_endpoint_rotation_curve_or_residual"] == "must_be_false"


def test_ngc2841_radial_pa_inclination_digitization_review_acceptance_is_not_scoring() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 16
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["leakage_free"] is True
    assert summary["monotonic_radius"] is True
    assert summary["radius_unique"] is True
    assert summary["range_ok"] is True
    assert summary["enough_points"] is True
    assert summary["quality_flag_counts"] == {"caveated": 16}
    assert summary["profile_status"] == (
        "accepted_caveated_source_side_digitized_radial_pa_inclination_profile"
    )
    assert summary["formula_ready"] is False
    assert summary["formula_freeze_review_ready"] is True
    assert summary["position_angle_span_deg"] > 10.0
    assert summary["inclination_span_deg"] > 13.0
    assert summary["endpoint_replay_permission_counts"] == {"no": 16}
    assert summary["kernel_promotion_permission_counts"] == {"no": 16}
    assert summary["new_route_scoring_permission_counts"] == {"no": 16}
    assert summary["forbidden_endpoint_inputs_used_counts"] == {"no": 16}
    assert (
        summary["claim_boundary"]
        == "ngc2841_radial_pa_inclination_digitization_review_acceptance_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["kernel_promotion_permission"] == "no" for row in rows)
    assert all(row["uses_vobs_or_residual"] == "no" for row in rows)
    assert all(row["profile_status"].startswith("accepted_caveated_source_side") for row in rows)


def test_ngc2841_tilted_ring_geometry_kernel_freeze_review_is_shape_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 16
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["kernel_id"] == "K_NGC2841_TILTED_RING_PA_I_SOURCE_REVIEW_V0_1"
    assert summary["formula_freeze_review_ready"] is True
    assert summary["formula_ready"] is False
    assert summary["endpoint_replay_allowed"] is False
    assert summary["kernel_promotion_allowed"] is False
    assert summary["new_route_scoring_allowed"] is False
    assert summary["uses_vobs_or_residual_counts"] == {"no": 16}
    assert summary["formula_ready_counts"] == {"no": 16}
    assert summary["endpoint_replay_permission_counts"] == {"no": 16}
    assert summary["kernel_promotion_permission_counts"] == {"no": 16}
    assert summary["new_route_scoring_permission_counts"] == {"no": 16}
    assert summary["dimension_check"].startswith("pass_dimensionless_kernel")
    assert summary["kernel_min"] >= 0.0
    assert summary["kernel_max"] == 1.0
    assert summary["kernel_outer_value"] == 1.0
    assert (
        summary["claim_boundary"]
        == "ngc2841_tilted_ring_geometry_kernel_freeze_review_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    values = [float(row["k_tilted_ring_geometry_0_1"]) for row in rows]
    assert min(values) >= 0.0
    assert max(values) == 1.0
    assert all(row["formula_ready"] == "no" for row in rows)
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["geometry_kernel_role"].endswith("no_amplitude_no_sign_no_carrier") for row in rows)


def test_ngc2841_tilted_ring_formula_rule_review_keeps_sign_and_load_blocked() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tilted_ring_formula_rule_review_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["formula_ready"] is False
    assert summary["endpoint_replay_allowed"] is False
    assert summary["kernel_promotion_allowed"] is False
    assert summary["new_route_scoring_allowed"] is False
    assert summary["blocked_rule_items"] == [
        "amplitude_or_load_rule",
        "endpoint_authorization",
        "sign_rule",
    ]
    assert summary["candidate_review_rule_items"] == ["carrier_rule"]
    assert summary["frozen_review_rule_items"] == ["geometry_kernel_shape"]
    assert summary["formula_ready_counts"] == {"no": 5}
    assert summary["formula_freeze_review_ready_counts"] == {
        "no_blocked": 3,
        "yes_caveated": 2,
    }
    assert (
        summary["claim_boundary"]
        == "ngc2841_tilted_ring_formula_rule_review_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_tilted_ring_formula_rule_review_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_item = {row["rule_item"]: row for row in rows}
    assert by_item["geometry_kernel_shape"]["allowed_formula_use"].startswith("yes_shape_only")
    assert by_item["sign_rule"]["allowed_formula_use"] == "no_sign_not_frozen"
    assert by_item["amplitude_or_load_rule"]["allowed_formula_use"] == "no_amplitude_not_frozen"
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)


def test_ngc2841_projection_sign_load_derivation_is_projection_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_projection_sign_load_derivation_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 20
    assert summary["n_derivation_rows"] == 4
    assert summary["n_projection_profile_rows"] == 16
    assert summary["derived_projection_sign"] == "negative_multiplicative_attenuation"
    assert summary["added_capacity_sign_status"] == "not_derived_from_PA_i_alone"
    assert summary["amplitude_load_status"] == (
        "projection_factor_source_fixed;added_capacity_load_blocked"
    )
    assert summary["gamma_i_max"] > 0.12
    assert summary["outer_projection_factor"] < 0.89
    assert summary["endpoint_replay_permission_counts"] == {"no": 20}
    assert summary["kernel_promotion_permission_counts"] == {"no": 20}
    assert summary["new_route_scoring_permission_counts"] == {"no": 20}
    assert (
        summary["claim_boundary"]
        == "ngc2841_projection_sign_load_derivation_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_projection_sign_load_derivation_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_item = {row["derived_item"]: row for row in rows[:4]}
    assert by_item["projection_deprojection_identity"]["formula_use_permission"].startswith(
        "yes_projection_branch"
    )
    assert by_item["positive_outer_capacity_branch"]["formula_use_permission"] == (
        "no_added_capacity_not_frozen"
    )
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)


def test_ngc2841_outer_capacity_load_source_derivation_blocks_positive_load() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_load_source_derivation_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["projection_control_ready"] is True
    assert summary["positive_added_capacity_load_ready"] is False
    assert summary["positive_added_capacity_formula_ready"] is False
    assert summary["load_blocker"] == "missing_independent_velocity_squared_load"
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["new_route_scoring_permission_counts"] == {"no": 5}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 5}
    assert (
        summary["claim_boundary"]
        == "ngc2841_outer_capacity_load_source_derivation_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_outer_capacity_load_source_derivation_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_channel = {row["load_channel"]: row for row in rows}
    assert by_channel["strict_projection_control"]["formula_readiness"] == (
        "projection_control_ready_not_added_capacity"
    )
    assert by_channel["composite_positive_outer_capacity"]["load_status"] == (
        "blocked_missing_independent_velocity_squared_load"
    )
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["uses_vobs_or_residual"] == "no" for row in rows)


def test_ngc2841_outer_capacity_load_source_search_finds_only_control_load() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_outer_capacity_load_source_search_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 4
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["promoted_load_source_ready"] is False
    assert summary["best_next_source_route"] == "dragonfly_mass_surface_density_profile_digitization"
    assert summary["outer_stellar_mass_msun"] == 140000000.0
    assert 26.0 < summary["v2_ceiling_30kpc_km2s2"] < 27.5
    assert 5.0 < summary["v_ceiling_30kpc_kms"] < 5.4
    assert summary["endpoint_replay_permission_counts"] == {"no": 4}
    assert summary["kernel_promotion_permission_counts"] == {"no": 4}
    assert summary["new_route_scoring_permission_counts"] == {"no": 4}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 4}
    assert (
        summary["claim_boundary"]
        == "ngc2841_outer_capacity_load_source_search_not_scoring"
    )

    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_ngc2841_outer_capacity_load_source_search_v0_1.csv"
            ).open()
        )
    )
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_source = {row["candidate_load_source"]: row for row in rows}
    assert by_source["dragonfly_integrated_outer_baryonic_mass_ceiling"]["load_use_status"] == (
        "usable_as_baryonic_ceiling_control_not_dark_residual_load"
    )
    assert by_source["dragonfly_mass_surface_density_profile_digitization"]["source_status"] == (
        "PROMISING_LOAD_ROUTE_REQUIRES_REVIEW_DIGITIZATION"
    )
    assert all(row["endpoint_replay_permission"] == "no" for row in rows)
    assert all(row["uses_vobs_or_residual"] == "no" for row in rows)


def test_ngc2841_mass_profile_digitization_review_package_is_source_side_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_digitization_review_package_v0_1_summary.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["package_stem"] == (
        "tcdr_v4_ngc2841_mass_profile_digitization_review_package_v0_1"
    )
    assert summary["png_rendered"] is True
    assert summary["n_manifest_rows"] >= 7
    assert "prof_masses1and2_4.pdf" in summary["included_files"]
    assert "review_response_template.csv" in summary["included_files"]
    assert "README_REVIEWER.md" in summary["included_files"]
    assert "zhang2018_mass_surface_density_profile.png" in summary["included_files"]
    assert summary["endpoint_replay_permission"] == "no"
    assert summary["kernel_promotion_permission"] == "no"
    assert summary["new_route_scoring_permission"] == "no"
    assert summary["uses_vobs_or_residual"] == "no"
    assert (
        summary["claim_boundary"]
        == "ngc2841_mass_profile_digitization_review_package_not_scoring"
    )
    package_dir = ROOT / summary["package_dir"]
    template_rows = list(csv.DictReader((package_dir / "review_response_template.csv").open()))
    assert template_rows[0]["uses_rotation_curve_or_velocity"] == "must_be_false"
    assert template_rows[0]["uses_endpoint_rotation_residual"] == "must_be_false"
    assert template_rows[0]["uses_tau_core_score_or_required_lambda"] == "must_be_false"


def test_ngc2841_mass_profile_source_native_table_search_is_negative() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_source_native_table_search_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_source_native_table_search_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 3
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["source_native_profile_table_found"] is False
    assert summary["component_normalization_resolved"] is False
    assert summary["formula_ready"] is False
    assert summary["machine_table_like_members"] == []
    assert "prof_masses1and2_4.pdf" in summary["figure_members"]
    assert summary["text_checks"] == {
        "stellar_gas_profile_figure_statement": True,
        "measured_color_and_constant_color_variants": True,
        "outer_3_to_1_ratio_statement": True,
        "outer_integrated_mass_statement": True,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 3}
    assert summary["kernel_promotion_permission_counts"] == {"no": 3}
    assert summary["new_route_scoring_permission_counts"] == {"no": 3}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 3}
    assert summary["claim_boundary"] == (
        "ngc2841_mass_profile_source_native_table_search_not_scoring"
    )

    rows = list(csv.DictReader(csv_path.open()))
    by_target = {row["search_target"]: row for row in rows}
    assert by_target["arxiv_source_machine_readable_profile_table"]["search_result"] == (
        "not_found_in_arxiv_source_package"
    )
    assert by_target["component_normalization_resolution"]["allowed_use"] == (
        "shape_candidate_only"
    )


def test_ngc2841_mass_profile_digitization_review_acceptance_is_scale_blocked() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 29
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["leakage_free"] is True
    assert summary["formula_ready"] is False
    assert summary["accepted_source_side_profile_candidate"] == (
        "yes_caveated_profile_received_but_load_conversion_blocked"
    )
    assert summary["scale_consistency_status"] == (
        "blocked_profile_normalization_semantics_mismatch"
    )
    assert summary["measured_color_integrated_star_mass_ge30_ratio_to_reference"] > 10.0
    assert summary["endpoint_replay_permission_counts"] == {"no": 29}
    assert summary["kernel_promotion_permission_counts"] == {"no": 29}
    assert summary["new_route_scoring_permission_counts"] == {"no": 29}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 29}


def test_ngc2841_mass_profile_normalization_audit_keeps_shape_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_normalization_audit_summary_v0_1.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 2
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["normalization_blocked"] is True
    assert summary["formula_ready"] is False
    assert summary["normalization_status_counts"] == {
        "blocked_component_semantics_required": 2
    }
    assert summary["allowed_use_counts"] == {"shape_candidate_only_no_load": 2}
    assert summary["endpoint_replay_permission_counts"] == {"no": 2}
    assert summary["kernel_promotion_permission_counts"] == {"no": 2}
    assert summary["new_route_scoring_permission_counts"] == {"no": 2}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 2}


def test_ngc2841_mass_profile_semantics_clarification_keeps_load_blocked() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_semantics_clarification_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_semantics_clarification_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["normalization_blocked"] is True
    assert summary["formula_ready"] is False
    assert summary["minimum_naive_to_reference_ratio"] > 10.0
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["new_route_scoring_permission_counts"] == {"no": 5}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 5}
    assert summary["claim_boundary"] == (
        "ngc2841_mass_profile_semantics_clarification_not_scoring"
    )

    rows = list(csv.DictReader(csv_path.open()))
    verdict_rows = [
        row for row in rows if row["clarification_item"] == "claim_safe_verdict"
    ]
    assert len(verdict_rows) == 1
    assert verdict_rows[0]["status"] == "load_formula_blocked"
    assert verdict_rows[0]["endpoint_replay_permission"] == "no"


def test_ngc2841_mass_profile_semantics_review_package_is_source_side_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_semantics_review_package_v0_1_summary.json"
    )
    if not summary_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["package_stem"] == (
        "tcdr_v4_ngc2841_mass_profile_semantics_review_package_v0_1"
    )
    assert summary["n_manifest_rows"] >= 10
    assert "README_REVIEWER.md" in summary["included_files"]
    assert "review_response_template.csv" in summary["included_files"]
    assert "Zhang_relevant_lines.txt" in summary["included_files"]
    assert "source_native_table_search.csv" in summary["included_files"]
    assert "semantics_clarification.csv" in summary["included_files"]
    assert "normalization_audit.csv" in summary["included_files"]
    assert summary["endpoint_replay_permission"] == "no"
    assert summary["kernel_promotion_permission"] == "no"
    assert summary["new_route_scoring_permission"] == "no"
    assert summary["uses_vobs_or_residual"] == "no"
    assert summary["claim_boundary"] == (
        "ngc2841_mass_profile_semantics_review_package_not_scoring"
    )

    package_dir = ROOT / summary["package_dir"]
    template_rows = list(csv.DictReader((package_dir / "review_response_template.csv").open()))
    assert [row["question_id"] for row in template_rows] == [
        "Q1_curve_identity",
        "Q2_normalization_mapping",
        "Q3_axis_or_units_issue",
        "Q4_allowed_use",
    ]
    assert all(row["endpoint_replay_permission"] == "must_be_no" for row in template_rows)
    assert all(row["kernel_promotion_permission"] == "must_be_no" for row in template_rows)
    assert all(row["uses_rotation_curve_or_velocity"] == "must_be_false" for row in template_rows)
    assert all(row["uses_endpoint_rotation_residual"] == "must_be_false" for row in template_rows)


def test_ngc2841_mass_profile_semantics_review_acceptance_blocks_load_formula() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 4
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["answer_validation_pass"] is True
    assert summary["guardrail_pass"] is True
    assert summary["accepted_source_side_shape_candidate"] is True
    assert summary["source_native_normalization_rule_found"] is False
    assert summary["axis_or_units_fix_found"] is False
    assert summary["component_identity_resolved_for_load"] is False
    assert summary["allowed_use"] == "shape_candidate_only_no_load"
    assert summary["formula_ready"] is False
    assert summary["final_status"] == "ACCEPT_SHAPE_ONLY_LOAD_FORMULA_BLOCKED"
    assert summary["endpoint_replay_permission_counts"] == {"no": 4}
    assert summary["kernel_promotion_permission_counts"] == {"no": 4}
    assert summary["new_route_scoring_permission_counts"] == {"no": 4}
    assert summary["claim_boundary"] == (
        "ngc2841_mass_profile_semantics_review_acceptance_not_scoring"
    )
    assert summary["reviewer_answers"] == {
        "Q1_curve_identity": "figure_total_profile_not_isolated_component",
        "Q2_normalization_mapping": "no_not_in_source",
        "Q3_axis_or_units_issue": "no",
        "Q4_allowed_use": "shape_only",
    }

    rows = list(csv.DictReader(csv_path.open()))
    assert {row["allowed_use_after_acceptance"] for row in rows} == {
        "shape_candidate_only_no_load"
    }
    assert {row["formula_ready"] for row in rows} == {"no"}


def test_ngc2841_surviving_route_ledger_preserves_load_blockers() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_surviving_route_ledger_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_surviving_route_ledger_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["shape_ready_route_count"] == 5
    assert summary["positive_load_ready_route_count"] == 0
    assert summary["endpoint_ready_route_count"] == 0
    assert summary["preferred_next_route"] == "tilted_ring_projection_control"
    assert summary["diagnostic_control_candidate_routes"] == [
        "tilted_ring_projection_control"
    ]
    assert summary["endpoint_replay_permission_counts"] == {"no": 6}
    assert summary["kernel_promotion_permission_counts"] == {"no": 6}
    assert summary["new_route_scoring_permission_counts"] == {"no": 6}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 6}
    assert summary["claim_boundary"] == "ngc2841_surviving_route_ledger_not_scoring"

    rows = list(csv.DictReader(csv_path.open()))
    by_route = {row["route_id"]: row for row in rows}
    assert by_route["dragonfly_mass_profile_load"]["survival_class"] == (
        "closed_as_load_route_preserve_shape"
    )
    assert by_route["tilted_ring_projection_control"]["survival_class"] == (
        "survives_as_projection_control_not_positive_dark_residual"
    )
    assert by_route["composite_outer_morphology"]["load_status"] == (
        "blocked_missing_independent_positive_load"
    )


def test_ngc2841_projection_control_preflight_is_diagnostic_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_projection_control_preflight_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_projection_control_preflight_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["route_id"] == "tilted_ring_projection_control"
    assert summary["preferred_next_route"] == "tilted_ring_projection_control"
    assert summary["projection_control_preflight_ready"] is True
    assert summary["diagnostic_only"] is True
    assert summary["positive_load_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_allowed"] is False
    assert summary["diagnostic_replay_permission"] == "separate_authorization_required"
    assert summary["kernel_promotion_allowed"] is False
    assert summary["new_route_scoring_allowed"] is False
    assert summary["uses_vobs_or_residual_counts"] == {"no": 5}
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["new_route_scoring_permission_counts"] == {"no": 5}
    assert summary["claim_boundary"] == "ngc2841_projection_control_preflight_not_endpoint_scoring"

    rows = list(csv.DictReader(csv_path.open()))
    assert {row["projection_control_preflight_ready"] for row in rows} == {"yes"}
    assert {row["diagnostic_only"] for row in rows} == {"yes"}
    assert {row["positive_load_ready"] for row in rows} == {"no"}
    assert {row["endpoint_replay_permission"] for row in rows} == {"no"}
    assert {row["diagnostic_replay_permission"] for row in rows} == {
        "separate_authorization_required"
    }
    assert {row["uses_vobs_or_residual"] for row in rows} == {"no"}


def test_ngc2841_projection_control_diagnostic_replay_preserves_negative_control() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_projection_control_diagnostic_replay_summary_local.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_points"] == 50
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["projection_improves_baryonic"] is False
    assert summary["projection_minus_baryonic_weighted_rmse_kms"] > 0.0
    assert summary["diagnostic_replay_status_counts"] == {
        "diagnostic_replay_completed_no_validation": 50
    }
    assert summary["endpoint_validation_claimed_counts"] == {"no": 50}
    assert summary["kernel_promotion_permission_counts"] == {"no": 50}
    assert summary["positive_load_promotion_permission_counts"] == {"no": 50}
    assert summary["preflight_claim_boundary"] == (
        "ngc2841_projection_control_preflight_not_endpoint_scoring"
    )
    assert summary["claim_boundary"] == (
        "ngc2841_projection_control_diagnostic_replay_not_endpoint_validation"
    )

    rows = list(csv.DictReader(csv_path.open()))
    assert {row["endpoint_validation_claimed"] for row in rows} == {"no"}
    assert {row["kernel_promotion_permission"] for row in rows} == {"no"}
    assert {row["positive_load_promotion_permission"] for row in rows} == {"no"}
    by_zone = {row["zone"]: row for row in rows}
    assert float(by_zone["outer_ge_30kpc"]["projection_minus_baryonic_weighted_rmse_kms"]) > 0.0


def test_ngc2841_integrated_outer_baryonic_ceiling_is_tiny_control_not_load() -> None:
    freeze_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze_summary_v0_1.json"
    )
    replay_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_summary_local.csv"
    )
    if not freeze_path.exists() or not replay_path.exists() or not csv_path.exists():
        return
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    assert freeze["control_freeze_ready"] is True
    assert freeze["positive_dark_residual_load_ready"] is False
    assert freeze["endpoint_ready"] is False
    assert freeze["v2_ceiling_30kpc_km2s2"] < 30.0
    assert freeze["endpoint_replay_permission_counts"] == {"no": 6}
    assert freeze["claim_boundary"] == (
        "ngc2841_integrated_outer_baryonic_ceiling_control_freeze_not_endpoint"
    )

    assert replay["n_points"] == 50
    assert replay["ceiling_control_improves_baryonic"] is True
    assert replay["ceiling_minus_baryonic_weighted_rmse_kms"] < 0.0
    assert abs(replay["ceiling_minus_baryonic_weighted_rmse_kms"]) < 0.1
    assert replay["max_delta_v2_outer_baryonic_ceiling"] < 30.0
    assert replay["endpoint_validation_claimed_counts"] == {"no": 50}
    assert replay["kernel_promotion_permission_counts"] == {"no": 50}
    assert replay["positive_dark_residual_load_promotion_permission_counts"] == {"no": 50}
    assert replay["claim_boundary"] == (
        "ngc2841_integrated_outer_baryonic_ceiling_control_diagnostic_not_validation"
    )

    rows = list(csv.DictReader(csv_path.open()))
    by_zone = {row["zone"]: row for row in rows}
    assert float(by_zone["outer_ge_30kpc"]["ceiling_minus_baryonic_weighted_rmse_kms"]) < 0.0
    assert abs(float(by_zone["outer_ge_30kpc"]["ceiling_minus_baryonic_weighted_rmse_kms"])) < 0.1


def test_ngc2841_post_control_gap_remains_large_after_frozen_controls() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_post_control_positive_load_gap_summary_local.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_points"] == 50
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["outer_zone_median_positive_v2_gap_after_baryonic"] > 65000.0
    assert summary["outer_zone_median_positive_v2_gap_after_ceiling_control"] > 65000.0
    assert summary["outer_zone_median_positive_v2_gap_after_projection_control"] > (
        summary["outer_zone_median_positive_v2_gap_after_baryonic"]
    )
    assert summary["ceiling_fraction_of_outer_baryonic_gap"] < 0.001
    assert summary["endpoint_validation_claimed_counts"] == {"no": 50}
    assert summary["kernel_promotion_permission_counts"] == {"no": 50}
    assert summary["positive_load_promotion_permission_counts"] == {"no": 50}
    assert summary["claim_boundary"] == (
        "ngc2841_post_control_positive_load_gap_diagnostic_not_kernel_fit"
    )

    rows = list(csv.DictReader(csv_path.open()))
    by_zone = {row["zone"]: row for row in rows}
    outer = by_zone["outer_ge_30kpc"]
    assert float(outer["median_positive_v2_gap_after_ceiling_control"]) > 65000.0
    assert float(outer["outer_baryonic_ceiling_delta_v2_median"]) < 20.0


def test_ngc2841_required_positive_load_scale_worklist_is_not_mass_claim() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_required_positive_load_scale_worklist_summary_local.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_points"] == 50
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["outer_zone_median_positive_v2_gap_after_ceiling_control"] > 65000.0
    assert summary["outer_zone_median_required_equivalent_load_mass_after_ceiling_msun"] > 6.0e11
    assert summary["outer_zone_median_known_outer_baryon_ceiling_fraction_of_required"] < 0.001
    assert summary["endpoint_validation_claimed_counts"] == {"no": 50}
    assert summary["kernel_promotion_permission_counts"] == {"no": 50}
    assert summary["positive_load_promotion_permission_counts"] == {"no": 50}
    assert summary["claim_boundary"] == (
        "ngc2841_required_positive_load_scale_worklist_not_physical_mass_claim"
    )

    rows = list(csv.DictReader(csv_path.open()))
    by_zone = {row["zone"]: row for row in rows}
    assert by_zone["outer_ge_30kpc"]["source_priority"] == "primary_outer_positive_load_target"
    assert float(
        by_zone["outer_ge_30kpc"][
            "median_required_equivalent_load_mass_after_ceiling_msun"
        ]
    ) > 6.0e11


def test_ngc2841_sparc_hi_gas_load_proxy_freeze_is_lower_bound_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 50
    assert summary["n_outer_rows_ge_30kpc"] == 17
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["gas_load_proxy_freeze_ready"] is True
    assert summary["positive_dark_residual_load_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 50}
    assert summary["kernel_promotion_permission_counts"] == {"no": 50}
    assert summary["positive_dark_residual_load_ready_counts"] == {"no": 50}
    assert summary["gas_load_proxy_freeze_ready_counts"] == {"yes": 50}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 50}
    assert summary["outer_max_vgas_kms"] > 60.0
    assert summary["outer_max_vgas2_positive_load_proxy_km2s2"] > 4000.0
    assert summary["outer_median_gas_proxy_fraction_of_required_gap"] < 0.10
    assert summary["outer_max_gas_proxy_fraction_of_required_gap"] < 0.10
    assert summary["claim_boundary"] == (
        "ngc2841_sparc_hi_gas_load_proxy_freeze_not_positive_dark_residual"
    )

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "errV", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    outer_rows = [row for row in rows if row["outer_capacity_window_ge_30kpc"] == "yes"]
    assert len(outer_rows) == 17
    assert max(float(row["outer_hi_shape_kernel"]) for row in rows) == 1.0
    for row in rows:
        assert row["uses_vobs_or_residual"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_dark_residual_load_ready"] == "no"
        assert row["gas_load_proxy_freeze_ready"] == "yes"


def test_ngc2841_things_ned_mom0_radial_profile_freeze_is_shape_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["galaxy"] == "NGC2841"
    assert summary["products"] == ["NA", "RO"]
    assert summary["n_rows"] == 120
    assert summary["radial_profile_freeze_ready"] is True
    assert summary["absolute_surface_density_or_load_ready"] is False
    assert summary["positive_load_freeze_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 120}
    assert summary["kernel_promotion_permission_counts"] == {"no": 120}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 120}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 120}
    assert summary["claim_boundary"] == (
        "ngc2841_things_ned_mom0_radial_profile_freeze_not_endpoint"
    )

    by_product = {item["product"]: item for item in summary["product_summaries"]}
    assert set(by_product) == {"NA", "RO"}
    for product_summary in by_product.values():
        assert product_summary["support_outer_radius_kpc_1pct_peak"] == 60.0
        assert product_summary["outer_ge_30kpc_peak_shape"] > 0.5
        assert product_summary["outer_ge_30kpc_mean_shape"] > 0.2
        assert product_summary["beam_from_history"]["bmaj_deg"] > 0.0
        assert product_summary["beam_from_history"]["bmin_deg"] > 0.0

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 120
    forbidden_columns = {"Vobs", "vobs", "errV", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert {row["product"] for row in rows} == {"NA", "RO"}
    for row in rows:
        assert row["uses_vobs_or_residual"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"
        assert row["allowed_use"] == "source_native_mom0_radial_shape_support"
        assert row["blocked_use"] == (
            "absolute_velocity_squared_load_without_beam_and_mass_conversion_audit"
        )


def test_ngc2841_things_mom0_beam_unit_mass_conversion_audit_is_not_endpoint() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["galaxy"] == "NGC2841"
    assert summary["products"] == ["NA", "RO"]
    assert summary["n_rows"] == 120
    assert summary["source_native_flux_consistency_ready"] is True
    assert summary["mass_profile_proxy_ready"] is True
    assert summary["disk_gravity_load_review_ready"] is False
    assert summary["positive_load_freeze_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 120}
    assert summary["kernel_promotion_permission_counts"] == {"no": 120}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 120}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 120}
    assert summary["claim_boundary"] == (
        "ngc2841_things_mom0_beam_unit_mass_conversion_audit_not_endpoint"
    )

    by_product = {item["product"]: item for item in summary["product_summaries"]}
    assert set(by_product) == {"NA", "RO"}
    assert 0.95 < by_product["NA"]["flux_ratio_to_vizier_global"] < 1.01
    assert 0.95 < by_product["RO"]["flux_ratio_to_vizier_global"] < 1.01
    assert by_product["NA"]["integrated_mom0_hi_mass_msun_proxy"] > 8.0e9
    assert by_product["RO"]["integrated_mom0_hi_mass_msun_proxy"] > 8.0e9
    assert by_product["NA"]["outer_ge_30kpc_enclosed_spherical_v2_max_km2s2_proxy"] > 700.0
    assert by_product["RO"]["outer_ge_30kpc_enclosed_spherical_v2_max_km2s2_proxy"] > 700.0

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 120
    forbidden_columns = {"Vobs", "vobs", "errV", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert {row["product"] for row in rows} == {"NA", "RO"}
    for row in rows:
        assert row["uses_vobs_or_residual"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"
        assert row["allowed_use"] == "source_native_mom0_mass_calibration_audit"
        assert row["blocked_use"] == (
            "endpoint_replay_or_absolute_dark_residual_claim_without_disk_gravity_review"
        )


def test_ngc2841_mom0_disk_load_promotion_review_only_promotes_physical_hi_control() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_mom0_disk_load_promotion_review_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["galaxy"] == "NGC2841"
    assert summary["products"] == ["NA", "RO"]
    assert summary["n_rows"] == 120
    assert summary["formula_shell_status"] == (
        "source_frozen_physical_hi_disk_load_control_ready"
    )
    assert summary["primary_product"] == "RO"
    assert summary["amplitude_rule"] == "lambda_HI=1_physical_hi_mass_only_no_residual_fit"
    assert summary["standard_gas_factor_rule"] == (
        "optional_lambda_gas=1.36_standard_helium_correction_no_residual_fit"
    )
    assert summary["standard_helium_gas_factor"] == 1.36
    assert summary["source_frozen_physical_hi_disk_load_control_ready"] is True
    assert summary["source_frozen_standard_hi_plus_helium_gas_control_ready"] is True
    assert summary["positive_dark_residual_load_ready"] is False
    assert summary["halo_capacity_multiplier_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 120}
    assert summary["kernel_promotion_permission_counts"] == {"no": 120}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 120}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 120}
    assert summary["claim_boundary"] == (
        "ngc2841_mom0_disk_load_promotion_review_not_endpoint"
    )

    by_product = {item["product"]: item for item in summary["product_summaries"]}
    assert by_product["NA"]["outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy"] > 1000.0
    assert by_product["RO"]["outer_ge_30kpc_axisymmetric_disk_v2_max_km2s2_proxy"] > 1000.0
    assert by_product["NA"]["outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy"] > 1500.0
    assert by_product["RO"]["outer_ge_30kpc_hi_plus_helium_disk_v2_max_km2s2_proxy"] > 1500.0
    assert by_product["RO"]["flux_ratio_to_vizier_global"] > by_product["NA"][
        "flux_ratio_to_vizier_global"
    ]

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 120
    forbidden_columns = {"Vobs", "vobs", "errV", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    assert {row["product"] for row in rows} == {"NA", "RO"}
    assert {row["amplitude_rule"] for row in rows} == {
        "lambda_HI=1_physical_hi_mass_only_no_residual_fit"
    }
    assert {row["standard_gas_factor_rule"] for row in rows} == {
        "optional_lambda_gas=1.36_standard_helium_correction_no_residual_fit"
    }
    for row in rows:
        assert row["uses_vobs_or_residual"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"
        assert row["allowed_use"] == "source_frozen_physical_hi_disk_load_control"
        assert row["blocked_use"] == (
            "positive_dark_residual_or_halo_capacity_kernel_without_independent_multiplier"
        )


def test_ngc2841_halo_capacity_conversion_search_keeps_endpoint_fits_forbidden() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 5
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["frozen_lower_bound_routes"] == ["sparc_things_vgas_lower_bound"]
    assert summary["frozen_global_hi_support_routes"] == ["things_vizier_global_hi_spectrum"]
    assert summary["frozen_mom0_radial_shape_routes"] == [
        "things_moment0_radial_hi_surface_density"
    ]
    assert (
        summary["next_primary_source_acquisition_target"]
        == "independent_extended_hi_multiplier_or_tau_side_load_theorem"
    )
    assert summary["rejected_endpoint_fit_routes"] == ["nfw_iso_halo_fit_parameters"]
    assert summary["positive_load_freeze_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["hi_gas_lower_bound_fraction_of_required_gap_median"] < 0.10
    assert summary["hi_gas_lower_bound_fraction_of_required_gap_max"] < 0.10
    assert summary["global_hi_spectrum_freeze_ready"] is True
    assert summary["global_hi_spectrum_mhi_msun_proxy"] > 8.0e9
    assert summary["mom0_radial_profile_freeze_ready"] is True
    assert summary["mom0_beam_unit_mass_audit_ready"] is True
    assert summary["mom0_mass_profile_proxy_ready"] is True
    assert summary["mom0_disk_gravity_load_review_ready"] is True
    assert summary["mom0_physical_hi_disk_load_control_ready"] is True
    assert summary["mom0_standard_hi_plus_helium_gas_control_ready"] is True
    assert summary["mom0_standard_helium_gas_factor"] == 1.36
    assert summary["mom0_absolute_load_ready"] is True
    assert summary["mom0_positive_dark_residual_load_ready"] is False
    assert summary["mom0_na_outer_ge_30kpc_mean_shape"] > 0.2
    assert summary["mom0_na_outer_ge_30kpc_peak_shape"] > 0.5
    assert summary["mom0_ro_outer_ge_30kpc_mean_shape"] > 0.2
    assert summary["mom0_ro_outer_ge_30kpc_peak_shape"] > 0.5
    assert 0.95 < summary["mom0_na_flux_ratio_to_vizier_global"] < 1.01
    assert 0.95 < summary["mom0_ro_flux_ratio_to_vizier_global"] < 1.01
    assert summary["mom0_primary_disk_load_product"] == "RO"
    assert summary["mom0_na_outer_disk_v2_proxy"] > 1000.0
    assert summary["mom0_ro_outer_disk_v2_proxy"] > 1000.0
    assert summary["mom0_na_outer_hi_plus_helium_disk_v2_proxy"] > 1500.0
    assert summary["mom0_ro_outer_hi_plus_helium_disk_v2_proxy"] > 1500.0
    assert summary["conversion_status_counts"] == {
        "FROZEN_GLOBAL_HI_SUPPORT_RADIAL_CONVERSION_MISSING": 1,
        "FROZEN_LOWER_BOUND_GAS_PROXY": 1,
        "FROZEN_PHYSICAL_HI_DISK_LOAD_CONTROL_POSITIVE_RESIDUAL_MULTIPLIER_MISSING": 1,
        "MOTIVATED_BUT_NO_SOURCE_FROZEN_SCALE": 1,
        "REJECTED_FOR_SOURCE_FREEZE": 1,
    }
    assert summary["endpoint_replay_permission_counts"] == {"no": 5}
    assert summary["kernel_promotion_permission_counts"] == {"no": 5}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 5}
    assert summary["uses_vobs_or_residual_counts"] == {
        "no": 4,
        "yes_endpoint_fit_route_rejected": 1,
    }
    assert summary["claim_boundary"] == (
        "ngc2841_halo_capacity_conversion_search_freeze_not_endpoint"
    )

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_route = {row["conversion_route"]: row for row in rows}
    assert by_route["sparc_things_vgas_lower_bound"]["conversion_status"] == (
        "FROZEN_LOWER_BOUND_GAS_PROXY"
    )
    assert by_route["sparc_things_vgas_lower_bound"]["positive_load_status"] == (
        "insufficient_for_outer_capacity"
    )
    assert by_route["things_moment0_radial_hi_surface_density"]["conversion_status"] == (
        "FROZEN_PHYSICAL_HI_DISK_LOAD_CONTROL_POSITIVE_RESIDUAL_MULTIPLIER_MISSING"
    )
    assert by_route["things_moment0_radial_hi_surface_density"]["allowed_use"] == (
        "source_native_mom0_radial_shape_support"
    )
    assert by_route["things_moment0_radial_hi_surface_density"]["blocked_use"] == (
        "positive_dark_residual_or_halo_capacity_kernel_without_independent_multiplier"
    )
    assert by_route["things_vizier_global_hi_spectrum"]["conversion_status"] == (
        "FROZEN_GLOBAL_HI_SUPPORT_RADIAL_CONVERSION_MISSING"
    )
    assert by_route["things_vizier_global_hi_spectrum"]["allowed_use"] == (
        "global_hi_support_and_consistency_context"
    )
    assert by_route["nfw_iso_halo_fit_parameters"]["conversion_status"] == (
        "REJECTED_FOR_SOURCE_FREEZE"
    )
    assert by_route["nfw_iso_halo_fit_parameters"]["positive_load_status"] == (
        "forbidden_as_tau_source_route"
    )
    assert by_route["nfw_iso_halo_fit_parameters"]["uses_vobs_or_residual"] == (
        "yes_endpoint_fit_route_rejected"
    )
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"


def test_ngc2841_positive_outer_capacity_source_route_reaudit_blocks_scoring() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 8
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["primary_positive_load_candidates"] == ["outer_hi_warp_halo_capacity"]
    assert summary["endpoint_ready"] is False
    assert summary["positive_load_ready"] is False
    assert summary["projection_dominated_interpretation_supported"] is False
    assert summary["outer_capacity_dominated_interpretation_supported"] is True
    assert summary["required_equivalent_load_scale_msun_yardstick"] > 6.0e11
    assert summary["required_scale_is_physical_mass_claim"] is False
    assert summary["sourced_hi_gas_proxy_frozen"] is True
    assert summary["sourced_hi_gas_proxy_fraction_of_required_gap_median"] < 0.10
    assert summary["sourced_hi_gas_proxy_fraction_of_required_gap_max"] < 0.10
    assert summary["halo_capacity_or_extended_hi_load_still_missing"] is True
    assert summary["known_outer_baryon_ceiling_fraction_of_required"] < 0.001
    assert summary["endpoint_replay_permission_counts"] == {"no": 8}
    assert summary["kernel_promotion_permission_counts"] == {"no": 8}
    assert summary["new_route_scoring_permission_counts"] == {"no": 8}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 8}
    assert summary["uses_endpoint_diagnostic_as_yardstick_counts"] == {
        "no": 7,
        "yes_not_for_label_or_kernel": 1,
    }
    assert summary["claim_boundary"] == (
        "ngc2841_positive_outer_capacity_source_route_reaudit_not_scoring"
    )

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_route = {row["route_id"]: row for row in rows}
    assert by_route["tilted_ring_projection_control"]["priority"] == "closed_control"
    assert by_route["tilted_ring_projection_control"]["load_status"] == (
        "negative_multiplicative_control_wrong_sign_for_positive_load"
    )
    assert by_route["known_integrated_outer_baryonic_ceiling"]["load_status"] == (
        "velocity_squared_units_but_too_small"
    )
    assert by_route["dragonfly_mass_profile_shape"]["load_status"] == (
        "shape_only_load_formula_blocked"
    )
    assert by_route["outer_hi_warp_halo_capacity"]["priority"] == (
        "high_primary_positive_load_candidate"
    )
    assert by_route["outer_hi_warp_halo_capacity"]["load_status"] == (
        "lower_bound_gas_proxy_frozen_halo_capacity_load_still_missing"
    )
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_independent_multiplier_rejection_audit_blocks_extra_capacity_fit() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_independent_multiplier_rejection_audit_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 7
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["control_ready_routes"] == ["physical_hi_plus_helium_gas_control"]
    assert summary["theory_route_open"] == ["tau_side_outer_capacity_load_theorem"]
    assert summary["rejected_endpoint_fit_routes"] == ["nfw_iso_halo_fit_parameters"]
    assert summary["independent_multiplier_ready"] is False
    assert summary["positive_dark_residual_load_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 7}
    assert summary["kernel_promotion_permission_counts"] == {"no": 7}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 7}
    assert summary["independent_multiplier_ready_counts"] == {"no": 7}
    assert summary["uses_vobs_or_residual_counts"] == {
        "no": 6,
        "yes_endpoint_fit_route_rejected": 1,
    }
    assert summary["claim_boundary"] == (
        "ngc2841_independent_multiplier_rejection_audit_not_endpoint"
    )

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_route = {row["multiplier_route"]: row for row in rows}
    assert by_route["physical_hi_plus_helium_gas_control"]["multiplier_status"] == (
        "CONTROL_READY_NOT_EXTRA_DARK_RESIDUAL_MULTIPLIER"
    )
    assert by_route["physical_hi_plus_helium_gas_control"]["allowed_use"] == (
        "physical_gas_control_only"
    )
    assert by_route["bosma_hi_scaling_outer_disk"]["multiplier_status"] == (
        "REJECTED_NO_SOURCE_FROZEN_SCALE"
    )
    assert by_route["nfw_iso_halo_fit_parameters"]["multiplier_status"] == (
        "REJECTED_ENDPOINT_FIT"
    )
    assert by_route["nfw_iso_halo_fit_parameters"]["uses_vobs_or_residual"] == (
        "yes_endpoint_fit_route_rejected"
    )
    for row in rows:
        assert row["independent_multiplier_ready"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"


def test_ngc2841_tau_side_load_theorem_readiness_keeps_theorem_blocked() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tau_side_load_theorem_readiness_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_tau_side_load_theorem_readiness_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["candidate_formula_shell"] == "Delta_v_tau^2(R)=A_tau*K_outer(R)"
    assert summary["formula_shell_dimension_status"] == (
        "dimensionally_valid_if_A_tau_has_velocity_squared_units"
    )
    assert summary["theorem_ready"] is False
    assert summary["positive_load_freeze_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["blocked_requirement_ids"] == [
        "TLOAD_2_UNIT_MAP",
        "TLOAD_3_AMPLITUDE_SOURCE",
    ]
    assert summary["ready_as_audit_constraint_ids"] == [
        "TLOAD_5_LIMITS_AND_GAUGE",
        "TLOAD_6_ENDPOINT_LEAKAGE",
    ]
    assert summary["partial_requirement_ids"] == [
        "TLOAD_1_SUPPORT_FIELD",
        "TLOAD_4_SIGN_RULE",
    ]
    assert summary["endpoint_replay_permission_counts"] == {"no": 6}
    assert summary["kernel_promotion_permission_counts"] == {"no": 6}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 6}
    assert summary["theorem_promotion_permission_counts"] == {"no": 6}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 6}
    assert summary["independent_multiplier_ready_from_previous_audit"] is False
    assert summary["previous_audit_endpoint_ready"] is False
    assert summary["claim_boundary"] == (
        "ngc2841_tau_side_load_theorem_readiness_not_theorem_not_endpoint"
    )

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_req = {row["requirement_id"]: row for row in rows}
    assert by_req["TLOAD_2_UNIT_MAP"]["current_status"] == "BLOCKED"
    assert by_req["TLOAD_3_AMPLITUDE_SOURCE"]["current_status"] == "BLOCKED"
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"
        assert row["theorem_promotion_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_related_paper_proxy_transfer_audit_finds_no_direct_a_tau() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_related_paper_proxy_transfer_audit_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 6
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["related_papers_checked"] == [
        "paper8_morphology_forward_readout",
        "paper9_projection_readout",
        "paper19_current",
    ]
    assert summary["paper9_bullock_ngc2841_available"] is True
    assert 0.02 < summary["paper9_bullock_ngc2841_lambda_spin"] < 0.021
    assert 1.08 < summary["paper9_bullock_ngc2841_beta_if_used"] < 1.081
    assert summary["direct_A_tau_proxy_found"] is False
    assert summary["dimensionless_context_proxy_found"] is True
    assert summary["transferable_as_additive_outer_capacity"] is False
    assert summary["theorem_ready_from_previous_audit"] is False
    assert summary["independent_multiplier_ready_from_previous_audit"] is False
    assert summary["endpoint_replay_permission_counts"] == {"no": 6}
    assert summary["kernel_promotion_permission_counts"] == {"no": 6}
    assert summary["positive_load_freeze_permission_counts"] == {"no": 6}
    assert summary["A_tau_freeze_permission_counts"] == {"no": 6}
    assert summary["uses_vobs_or_residual_counts"] == {"no": 6}
    assert summary["claim_boundary"] == (
        "ngc2841_related_paper_proxy_transfer_audit_not_endpoint"
    )

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_route = {row["proxy_route"]: row for row in rows}
    assert by_route["paper9_bullock_disk_spin_proxy"]["transfer_status"] == (
        "TRANSFERABLE_AS_DIMENSIONLESS_CONTEXT_NOT_A_TAU"
    )
    assert by_route["paper8_ngc4088_minimal_euler_warp_amplitude"]["transfer_status"] == (
        "FORMULA_CONDITIONAL_NOT_DIRECTLY_TRANSFERABLE"
    )
    assert by_route["paper19_physical_hi_plus_helium_control"]["transfer_status"] == (
        "CONTROL_READY_NOT_EXTRA_A_TAU"
    )
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["positive_load_freeze_permission"] == "no"
        assert row["A_tau_freeze_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_multiplicative_beta_reformulation_preflight_is_not_endpoint() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 7
    assert summary["reformulation_open"] is True
    assert summary["beta_proxy_available"] is True
    assert 0.02 < summary["lambda_spin"] < 0.021
    assert 1.08 < summary["beta_cl_if_used"] < 1.081
    assert summary["formula_shell"] == (
        "v_beta^2(R)=v_carrier^2(R)*[1+(beta_cl-1)*K_beta(R)]"
    )
    assert summary["endpoint_ready"] is False
    assert summary["formula_freeze_ready"] is False
    assert summary["source_label_promotion_ready"] is False
    assert summary["blocked_requirement_ids"] == [
        "BETA_2_FAMILY_REFORMULATION_LABEL",
        "BETA_4_CARRIER",
        "BETA_5_K_BETA_KERNEL",
    ]
    for field in [
        "endpoint_replay_permission",
        "formula_freeze_permission",
        "kernel_promotion_permission",
        "reformulation_label_promotion_permission",
        "uses_vobs_or_residual",
    ]:
        assert summary["permission_counts"][field] == {"no": 7, "yes": 0}

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 7
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_gate = {row["gate_id"]: row for row in rows}
    assert by_gate["BETA_1_PROXY_AVAILABLE"]["status"] == "PASS_CAVEATED"
    assert by_gate["BETA_2_FAMILY_REFORMULATION_LABEL"]["status"].startswith("BLOCKED")
    assert by_gate["BETA_4_CARRIER"]["status"].startswith("BLOCKED")
    assert by_gate["BETA_5_K_BETA_KERNEL"]["status"].startswith("BLOCKED")
    for row in rows:
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_freeze_permission"] == "no"
        assert row["reformulation_label_promotion_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_beta_closure_label_review_opens_review_but_not_promotion() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 7
    assert summary["beta_closure_reformulation_review_open"] is True
    assert summary["review_package_permission"] is True
    assert summary["reformulation_label_promoted"] is False
    assert summary["endpoint_ready"] is False
    assert summary["formula_freeze_ready"] is False
    assert summary["carrier_freeze_ready"] is False
    assert summary["K_beta_freeze_ready"] is False
    assert 0.02 < summary["lambda_spin"] < 0.021
    assert 1.08 < summary["beta_cl_if_used"] < 1.081
    assert summary["paper9_transfer_priority_class"] == "WEAK_NFW_PREFERENCE_TRANSFER_TARGET"
    assert summary["paper9_nfw_preference_load"] < 0.1
    assert summary["tilted_ring_support_present"] is True
    assert summary["composite_outer_morphology_support_present"] is True
    assert summary["blocked_requirement_ids"] == [
        "BETA_2A_INDEPENDENT_SPIN_ROUTE_DECISION",
        "BETA_2B_SOURCE_FROZEN_CARRIER",
        "BETA_2C_SOURCE_FROZEN_K_BETA",
    ]
    assert summary["permission_counts"]["review_package_permission"] == {"yes": 7}
    for field in [
        "endpoint_replay_permission",
        "kernel_promotion_permission",
        "formula_freeze_permission",
        "reformulation_label_promotion_permission",
        "uses_vobs_or_residual",
    ]:
        assert summary["permission_counts"][field] == {"no": 7}

    rows = list(csv.DictReader(csv_path.open()))
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    by_item = {row["review_item"]: row for row in rows}
    assert by_item["label_review_verdict"]["source_status"] == "review_open_not_promoted"
    assert by_item["bullock_disk_spin_conversion_proxy"]["source_status"] == (
        "dimensionless_proxy_available_review_required"
    )
    for row in rows:
        assert row["review_package_permission"] == "yes"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_freeze_permission"] == "no"
        assert row["reformulation_label_promotion_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_beta_closure_review_response_acceptance_keeps_route_blocked() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["review_response_accepted"] is True
    assert summary["all_decisions_high_confidence"] is True
    assert summary["overall_verdict"] == "review_open_not_promoted"
    assert summary["beta_closure_route_status"] == "review_open_not_promoted"
    assert summary["spin_route_status"] == "context_only_not_spin_freeze"
    assert summary["carrier_status"] == "blocked_requires_new_source_frozen_carrier"
    assert summary["K_beta_status"] == "blocked_requires_source_native_radial_profile"
    assert summary["endpoint_ready"] is False
    assert summary["formula_freeze_ready"] is False
    assert summary["kernel_promotion_ready"] is False
    assert summary["blocked_requirement_ids"] == [
        "BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE",
        "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE",
        "BETA_K_REQUIRES_SOURCE_NATIVE_RADIAL_PROFILE",
    ]
    assert summary["permission_counts"]["endpoint_replay_permission"] == {"no": 4}
    assert summary["permission_counts"]["formula_freeze_permission"] == {"no": 4}
    assert summary["permission_counts"]["kernel_promotion_permission"] == {"no": 4}
    assert summary["permission_counts"]["uses_vobs_or_residual"] == {"no": 4}

    rows = list(csv.DictReader(csv_path.open()))
    by_q = {row["question_id"]: row for row in rows}
    assert by_q["Q1_spin_route"]["reviewer_answer"] == "retain_as_context_only"
    assert by_q["Q2_carrier_policy"]["reviewer_answer"] == "require_new_source_frozen_carrier"
    assert by_q["Q3_k_beta_kernel"]["reviewer_answer"] == "require_new_source_native_radial_profile"
    assert by_q["Q4_route_status"]["reviewer_answer"] == "review_open_not_promoted"
    for row in rows:
        assert row["acceptance_status"] == "ACCEPT_REVIEW_DECISION"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_freeze_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_beta_closure_k_beta_profile_freeze_review_closes_only_shape() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 16
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["K_beta_profile_ready_for_formula_freeze_review"] is True
    assert summary["K_beta_kernel_promoted"] is False
    assert summary["source_profile_leakage_free"] is True
    assert summary["resolved_blocker_id"] == "BETA_K_REQUIRES_SOURCE_NATIVE_RADIAL_PROFILE"
    assert summary["resolved_blocker_status"] == (
        "resolved_as_caveated_digitized_pa_inclination_profile_shape"
    )
    assert summary["remaining_blockers"] == [
        "BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE",
        "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE",
    ]
    assert summary["full_formula_freeze_ready"] is False
    assert summary["formula_freeze_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["kernel_promotion_ready"] is False
    assert summary["endpoint_replay_allowed"] is False
    assert summary["new_route_scoring_allowed"] is False
    assert abs(summary["k_beta_min"]) < 1e-12
    assert abs(summary["k_beta_max"] - 1.0) < 1e-12
    for field in [
        "endpoint_replay_permission",
        "formula_freeze_permission",
        "kernel_promotion_permission",
        "new_route_scoring_permission",
        "uses_vobs_or_residual",
    ]:
        assert summary["permission_counts"][field] == {"no": 16}

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 16
    values = [float(row["k_beta_shape_0_1"]) for row in rows]
    assert min(values) == 0.0
    assert max(values) == 1.0
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert row["k_beta_profile_status"] == (
            "k_beta_shape_ready_for_formula_freeze_review_no_scoring"
        )
        assert row["source_profile_leakage_free"] == "yes"
        assert row["formula_freeze_ready"] == "no"
        assert row["endpoint_ready"] == "no"
        assert row["kernel_promotion_ready"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_freeze_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_beta_closure_baryonic_carrier_freeze_review_closes_only_carrier() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 50
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["carrier_ready_for_beta_formula_freeze_review"] is True
    assert summary["carrier_promoted_as_physical_baseline"] is False
    assert summary["source_profile_leakage_free"] is True
    assert summary["resolved_blocker_id"] == "BETA_CARRIER_REQUIRES_NEW_SOURCE_FREEZE"
    assert summary["resolved_blocker_status"] == (
        "resolved_as_fixed_mlr_baryonic_velocity_squared_carrier"
    )
    assert summary["remaining_blockers"] == ["BETA_SPIN_CONTEXT_ONLY_NOT_FREEZE"]
    assert summary["full_formula_freeze_ready"] is False
    assert summary["formula_freeze_ready"] is False
    assert summary["endpoint_ready"] is False
    assert summary["kernel_promotion_ready"] is False
    assert summary["endpoint_replay_allowed"] is False
    assert summary["new_route_scoring_allowed"] is False
    assert summary["carrier_min_v2_km2s2"] > 0
    assert summary["dimension_check"] == "pass_velocity_squared_from_sparc_component_velocities"
    assert summary["ignored_endpoint_columns_present_in_source_file"] == ["Vobs", "errV"]
    for field in [
        "endpoint_replay_permission",
        "formula_freeze_permission",
        "kernel_promotion_permission",
        "new_route_scoring_permission",
        "uses_vobs_or_residual",
    ]:
        assert summary["permission_counts"][field] == {"no": 50}

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 50
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert row["carrier_status"] == (
            "baryonic_carrier_ready_for_beta_formula_freeze_review_no_scoring"
        )
        assert float(row["v_carrier2_fixed_ml_km2s2"]) > 0
        assert row["ignored_endpoint_columns_present_in_source_file"] == "Vobs;errV"
        assert row["source_profile_leakage_free"] == "yes"
        assert row["formula_freeze_ready"] == "no"
        assert row["endpoint_ready"] == "no"
        assert row["kernel_promotion_ready"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_freeze_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"


def test_ngc2841_beta_closure_context_formula_freeze_review_is_not_endpoint() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_rows"] == 50
    assert summary["galaxies"] == ["NGC2841"]
    assert summary["all_formula_terms_frozen_for_review"] is True
    assert summary["formula_freeze_review_ready"] is True
    assert summary["physical_spin_claim"] is False
    assert summary["spin_blocker_disposition"] == (
        "retired_for_formula_review_by_recasting_as_beta_context_not_spin_freeze"
    )
    assert 1.08 < summary["beta_context"] < 1.081
    assert 0.02 < summary["lambda_spin_context"] < 0.021
    assert summary["dimension_check"] == (
        "pass_beta_context_and_K_beta_dimensionless_carrier_supplies_velocity_squared"
    )
    assert summary["endpoint_ready"] is False
    assert summary["endpoint_replay_allowed"] is False
    assert summary["kernel_promotion_ready"] is False
    assert summary["new_route_scoring_allowed"] is False
    for field in [
        "endpoint_replay_permission",
        "formula_freeze_permission",
        "kernel_promotion_permission",
        "new_route_scoring_permission",
        "uses_vobs_or_residual",
    ]:
        assert summary["permission_counts"][field] == {"no": 50}

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 50
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert row["formula_freeze_review_status"] == (
            "all_terms_frozen_for_formula_review_endpoint_still_forbidden"
        )
        assert row["beta_context_role"] == (
            "caveated_context_coefficient_not_direct_source_native_spin_measurement"
        )
        assert row["spin_blocker_disposition"] == (
            "retired_for_formula_review_by_recasting_as_beta_context_not_spin_freeze"
        )
        assert row["physical_spin_claim"] == "no"
        assert row["formula_freeze_review_ready"] == "yes"
        assert row["endpoint_ready"] == "no"
        assert row["endpoint_replay_permission"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_freeze_permission"] == "no"
        assert row["new_route_scoring_permission"] == "no"
        assert row["uses_vobs_or_residual"] == "no"
        assert float(row["v_beta_context2_km2s2"]) >= float(row["v_carrier2_fixed_ml_km2s2"])


def test_ngc2841_beta_closure_endpoint_authorization_reviewer_package_exists() -> None:
    package_dir = (
        ROOT
        / "data"
        / "reviewer_packages"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_reviewer_package_v0_1"
    )
    package_zip = (
        ROOT
        / "data"
        / "reviewer_packages"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_reviewer_package_v0_1.zip"
    )
    if not package_dir.exists() or not package_zip.exists():
        return
    required = {
        "README_REVIEWER.md",
        "review_response_template.csv",
        "package_manifest.csv",
        "beta_context_formula_freeze_review.csv",
        "beta_context_formula_freeze_review_summary.json",
        "k_beta_profile_freeze_review.csv",
        "k_beta_profile_freeze_review_summary.json",
        "baryonic_carrier_freeze_review.csv",
        "baryonic_carrier_freeze_review_summary.json",
    }
    present = {path.name for path in package_dir.iterdir() if path.is_file()}
    assert required.issubset(present)
    with zipfile.ZipFile(package_zip) as zf:
        names = set(zf.namelist())
    for filename in required:
        assert (
            "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_reviewer_package_v0_1/"
            f"{filename}"
        ) in names

    rows = list(csv.DictReader((package_dir / "review_response_template.csv").open()))
    assert [row["question_id"] for row in rows] == [
        "Q1_formula_integrity",
        "Q2_beta_context_boundary",
        "Q3_endpoint_scope",
        "Q4_final_authorization",
    ]
    for row in rows:
        assert row["formula_retuning_allowed"] == "must_be_no"
        assert row["morphology_relabel_allowed"] == "must_be_no"
        assert row["uses_rotation_curve_or_velocity"] == "must_be_false"
        assert row["uses_endpoint_rotation_residual"] == "must_be_false"
        assert row["uses_tau_core_score_or_required_load"] == "must_be_false"


def test_ngc2841_beta_closure_endpoint_authorization_accepts_preliminary_control_only() -> None:
    summary_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance_summary_v0_1.json"
    )
    csv_path = (
        ROOT
        / "data"
        / "source_manifests"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance_v0_1.csv"
    )
    if not summary_path.exists() or not csv_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["review_response_accepted"] is True
    assert summary["all_decisions_high_confidence"] is True
    assert summary["overall_verdict"] == "authorize_endpoint_replay_preliminary_control"
    assert summary["endpoint_replay_authorized"] is True
    assert summary["endpoint_ready"] is True
    assert summary["endpoint_scope"] == "single_object_preliminary_endpoint_control_replay_only"
    assert summary["kernel_promotion_ready"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["formula_retuning_allowed"] is False
    assert summary["morphology_relabel_allowed"] is False
    assert summary["scoring_script_may_read_vobs_after_authorization"] is True
    assert summary["formula_must_be_read_unchanged"] is True
    assert summary["legacy_blocked_review_artifact_present"] is True
    assert summary["legacy_blocked_review_disposition"] == (
        "superseded_for_endpoint_authorization_by_later_k_beta_carrier_and_formula_freeze_reviews"
    )
    assert summary["permission_counts"]["endpoint_replay_permission"] == {"yes": 4}
    assert summary["permission_counts"]["formula_retuning_allowed"] == {"no": 4}
    assert summary["permission_counts"]["morphology_relabel_allowed"] == {"no": 4}
    assert summary["permission_counts"]["validation_claim_allowed"] == {"no": 4}
    assert summary["permission_counts"]["uses_vobs_or_residual_in_review"] == {"no": 4}

    rows = list(csv.DictReader(csv_path.open()))
    by_q = {row["question_id"]: row for row in rows}
    assert by_q["Q1_formula_integrity"]["reviewer_answer"] == "authorize_unchanged_formula_replay"
    assert by_q["Q2_beta_context_boundary"]["reviewer_answer"] == "accept_caveated_beta_context"
    assert by_q["Q3_endpoint_scope"]["reviewer_answer"] == "single_object_preliminary_control_replay_only"
    assert by_q["Q4_final_authorization"]["reviewer_answer"] == "authorize_endpoint_replay_preliminary_control"
    for row in rows:
        assert row["acceptance_status"] == "ACCEPT_ENDPOINT_AUTHORIZATION"
        assert row["endpoint_replay_permission"] == "yes"
        assert row["kernel_promotion_permission"] == "no"
        assert row["formula_retuning_allowed"] == "no"
        assert row["morphology_relabel_allowed"] == "no"
        assert row["validation_claim_allowed"] == "no"
        assert row["scoring_script_may_read_vobs_after_authorization"] == "yes"
        assert row["formula_must_be_read_unchanged"] == "yes"
        assert row["uses_vobs_or_residual_in_review"] == "no"


def test_ngc2841_beta_closure_endpoint_control_replay_is_preliminary_and_weak() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_control_replay_summary_local.json"
    )
    detail_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc2841_beta_closure_endpoint_control_replay_detail_local.csv"
    )
    if not summary_path.exists() or not detail_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["n_points"] == 50
    assert summary["beta_context_improves_baryonic"] is True
    assert summary["beta_minus_baryonic_weighted_rmse_kms"] < 0
    assert summary["outer_zone_median_missing_velocity_after_beta_kms"] > 100
    assert summary["formula_retuned_after_authorization_counts"] == {"no": 50}
    assert summary["morphology_relabel_after_authorization_counts"] == {"no": 50}
    assert summary["kernel_promotion_permission_counts"] == {"no": 50}
    assert summary["validation_claimed_counts"] == {"no": 50}
    assert summary["claim_boundary"] == (
        "ngc2841_beta_closure_endpoint_control_replay_preliminary_not_validation"
    )

    rows = list(csv.DictReader(detail_path.open()))
    assert len(rows) == 50
    for row in rows:
        assert row["endpoint_control_status"] == "preliminary_control_replay_completed_no_validation"
        assert row["formula_retuned_after_authorization"] == "no"
        assert row["morphology_relabel_after_authorization"] == "no"
        assert row["kernel_promotion_permission"] == "no"
        assert row["validation_claimed"] == "no"


def test_ngc6503_clean_scale_tail_replay_beats_immediate_controls_without_retuning() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay_summary_local.json"
    )
    detail_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay_detail_local.csv"
    )
    figure_path = ROOT / "figures" / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay.png"
    paper_figure_path = (
        ROOT
        / "paper19_submission_source"
        / "figures"
        / "tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay.png"
    )
    if not summary_path.exists() or not detail_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["galaxy"] == "NGC6503"
    assert summary["matched_source_family"] == "K_EXPONENTIAL_SPIRAL_DISK"
    assert summary["compiled_formula_family_candidate"] == "F_EXPONENTIAL_DISK_SCALE_TAIL_SOURCE_FROZEN"
    assert summary["available_formula_components"] == "exponential_disk"
    assert summary["component_mixture_status"] == "no_source_native_bar_ring_spiral_component"
    assert summary["candidate_beats_baryonic"] is True
    assert summary["candidate_beats_pure_matched"] is True
    assert summary["candidate_beats_wrong_mean"] is True
    assert summary["candidate_beats_best_wrong"] is True
    assert summary["candidate_weighted_rmse_kms"] < summary["baryonic_weighted_rmse_kms"]
    assert summary["candidate_weighted_rmse_kms"] < summary["best_wrong_weighted_rmse_kms"]
    assert summary["claim_boundary"] == "ngc6503_clean_scale_tail_endpoint_replay_preliminary_not_validation"
    assert figure_path.exists()
    assert paper_figure_path.exists()

    rows = list(csv.DictReader(detail_path.open()))
    assert len(rows) == 31
    for row in rows:
        assert row["replay_status"] == "preliminary_clean_scale_tail_replay_completed_no_validation"
        assert row["target_amplitude_tuning"] == "no"
        assert row["new_kernel_search"] == "no"
        assert row["validation_claimed"] == "no"


def test_ngc7793_support_safe_spiral_replay_beats_wrong_controls_with_caveat() -> None:
    summary_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay_summary_local.json"
    )
    detail_path = (
        ROOT
        / "data"
        / "external"
        / "sparc_preflight"
        / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay_detail_local.csv"
    )
    figure_path = ROOT / "figures" / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay.png"
    paper_figure_path = (
        ROOT
        / "paper19_submission_source"
        / "figures"
        / "tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay.png"
    )
    if not summary_path.exists() or not detail_path.exists():
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["galaxy"] == "NGC7793"
    assert summary["matched_component"] == "spiral"
    assert summary["support_safe_compiled_formula"] == (
        "F_EXPONENTIAL_DISK_WITH_SPIRAL_PITCH_SOURCE_FROZEN"
    )
    assert summary["positive_components"] == "spiral"
    assert summary["candidate_beats_baryonic"] is True
    assert summary["candidate_beats_wrong_mean"] is True
    assert summary["candidate_beats_best_wrong"] is True
    assert summary["candidate_beats_matched_component"] is False
    assert summary["candidate_weighted_rmse_kms"] < summary["baryonic_weighted_rmse_kms"]
    assert summary["candidate_weighted_rmse_kms"] < summary["best_wrong_component_weighted_rmse_kms"]
    assert summary["claim_boundary"] == "ngc7793_support_safe_spiral_endpoint_replay_preliminary_not_validation"
    assert figure_path.exists()
    assert paper_figure_path.exists()

    rows = list(csv.DictReader(detail_path.open()))
    assert len(rows) == 46
    for row in rows:
        assert row["replay_status"] == "preliminary_support_safe_spiral_replay_completed_no_validation"
        assert row["target_amplitude_tuning"] == "no"
        assert row["new_kernel_search"] == "no"
        assert row["validation_claimed"] == "no"


def test_p0_source_native_kernel_coordinate_freeze_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["kernel_coordinate_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_coordinate_freeze"
        assert row["claim_boundary"] == "source_native_coordinate_freeze_not_kernel_validation"
    assert status_counts == {
        "source_native_bar_radius_frozen": 12,
        "source_native_ring_radius_frozen": 4,
        "source_native_spiral_pitch_recorded_disk_proxy_center": 2,
        "source_proxy_kernel_fallback": 48,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_component_mixture_audit_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    holdout_status_counts: dict[str, int] = {}
    for row in rows:
        status = row["component_mixture_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["pilot_role"] == "PILOT_HOLDOUT":
            holdout_status_counts[status] = holdout_status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_component_mixture_audit"
        assert row["claim_boundary"] == "source_native_component_mixture_audit_not_endpoint_validation"
    assert status_counts == {
        "mixed_source_native_multicomponent": 17,
        "no_source_native_bar_ring_spiral_component": 42,
        "single_source_native_primary_component": 4,
        "single_source_native_secondary_component_only": 3,
    }
    assert holdout_status_counts == {
        "mixed_source_native_multicomponent": 3,
        "no_source_native_bar_ring_spiral_component": 3,
        "single_source_native_primary_component": 1,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_mixed_component_kernel_freeze_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_mixed_component_kernel_freeze_v0_1.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    holdout_status_counts: dict[str, int] = {}
    for row in rows:
        status = row["mixed_kernel_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["pilot_role"] == "PILOT_HOLDOUT":
            holdout_status_counts[status] = holdout_status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_mixed_component_kernel_freeze"
        assert row["claim_boundary"] == "source_native_mixed_component_kernel_freeze_not_endpoint_validation"
        total_weight = (
            float(row["bar_component_weight"])
            + float(row["ring_component_weight"])
            + float(row["spiral_component_weight"])
            + float(row["fallback_family_proxy_weight"])
        )
        assert abs(total_weight - 1.0) < 1e-12
    assert status_counts == {
        "fallback_family_proxy_kernel": 42,
        "mixed_source_native_component_kernel": 17,
        "single_source_native_component_kernel": 7,
    }
    assert holdout_status_counts == {
        "fallback_family_proxy_kernel": 3,
        "mixed_source_native_component_kernel": 3,
        "single_source_native_component_kernel": 1,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_shuffled_component_nulls_are_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_shuffled_component_nulls_v0_1.csv"
            ).open()
        )
    )
    assert len(rows) == 64 * 66
    assert {row["shuffle_id"] for row in rows} == {str(i) for i in range(64)}
    for row in rows:
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_shuffled_component_nulls"
        assert row["claim_boundary"] == "source_native_shuffled_component_nulls_not_endpoint_validation"
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_strength_weighted_mixed_component_kernel_freeze_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze_v0_2.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    holdout_status_counts: dict[str, int] = {}
    for row in rows:
        status = row["mixed_kernel_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["pilot_role"] == "PILOT_HOLDOUT":
            holdout_status_counts[status] = holdout_status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_strength_weighted_mixed_component_kernel_freeze"
        assert row["claim_boundary"] == "source_native_strength_weighted_mixed_component_kernel_freeze_not_endpoint_validation"
        total_weight = (
            float(row["bar_component_weight"])
            + float(row["ring_component_weight"])
            + float(row["spiral_component_weight"])
            + float(row["fallback_family_proxy_weight"])
        )
        assert abs(total_weight - 1.0) < 1e-12
    assert status_counts == {
        "fallback_family_proxy_kernel": 42,
        "mixed_strength_weighted_source_native_component_kernel": 17,
        "single_strength_weighted_source_native_component_kernel": 7,
    }
    assert holdout_status_counts == {
        "fallback_family_proxy_kernel": 3,
        "mixed_strength_weighted_source_native_component_kernel": 3,
        "single_strength_weighted_source_native_component_kernel": 1,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_strength_weighted_shuffled_component_nulls_are_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls_v0_2.csv"
            ).open()
        )
    )
    assert len(rows) == 64 * 66
    assert {row["shuffle_id"] for row in rows} == {str(i) for i in range(64)}
    for row in rows:
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_shuffled_component_nulls"
        assert row["claim_boundary"] == "source_native_shuffled_component_nulls_not_endpoint_validation"
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_radial_geometry_mixed_component_kernel_freeze_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze_v0_3.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    holdout_status_counts: dict[str, int] = {}
    for row in rows:
        status = row["mixed_kernel_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["pilot_role"] == "PILOT_HOLDOUT":
            holdout_status_counts[status] = holdout_status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_radial_geometry_mixed_component_kernel_freeze"
        assert row["claim_boundary"] == "source_native_radial_geometry_mixed_component_kernel_freeze_not_endpoint_validation"
        total_weight = (
            float(row["bar_component_weight"])
            + float(row["ring_component_weight"])
            + float(row["spiral_component_weight"])
            + float(row["fallback_family_proxy_weight"])
        )
        assert abs(total_weight - 1.0) < 1e-12
    assert status_counts == {
        "fallback_family_proxy_kernel": 42,
        "mixed_radial_geometry_source_native_component_kernel": 17,
        "single_radial_geometry_source_native_component_kernel": 7,
    }
    assert holdout_status_counts == {
        "fallback_family_proxy_kernel": 3,
        "mixed_radial_geometry_source_native_component_kernel": 3,
        "single_radial_geometry_source_native_component_kernel": 1,
    }
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_native_radial_geometry_shuffled_component_nulls_are_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_native_radial_geometry_shuffled_component_nulls_v0_3.csv"
            ).open()
        )
    )
    assert len(rows) == 64 * 66
    assert {row["shuffle_id"] for row in rows} == {str(i) for i in range(64)}
    for row in rows:
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_shuffled_component_nulls"
        assert row["claim_boundary"] == "source_native_shuffled_component_nulls_not_endpoint_validation"
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_source_frozen_formula_compiler_readiness_is_endpoint_blind() -> None:
    rows = list(
        csv.DictReader(
            (
                ROOT
                / "data"
                / "source_manifests"
                / "tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv"
            ).open()
        )
    )
    assert len(rows) == 66
    status_counts: dict[str, int] = {}
    holdout_status_counts: dict[str, int] = {}
    for row in rows:
        status = row["compiler_readiness_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["pilot_role"] == "PILOT_HOLDOUT":
            holdout_status_counts[status] = holdout_status_counts.get(status, 0) + 1
        assert row["endpoint_data_policy"] == "do_not_use_rotation_residuals_or_endpoint_scores_for_formula_compiler_readiness"
        assert row["claim_boundary"] == "source_frozen_formula_compiler_readiness_not_endpoint_validation"
    assert status_counts == {
        "BLOCKED_UNFREEZABLE_SOURCE_FAMILY": 1,
        "FALLBACK_TEMPLATE_ONLY_NOT_FORMULA_READY": 19,
        "PARTIAL_FORMULA_COMPILER_CANDIDATE": 16,
        "READY_FORMULA_COMPILER_REPLAY_CANDIDATE": 30,
    }
    assert holdout_status_counts == {
        "FALLBACK_TEMPLATE_ONLY_NOT_FORMULA_READY": 1,
        "PARTIAL_FORMULA_COMPILER_CANDIDATE": 1,
        "READY_FORMULA_COMPILER_REPLAY_CANDIDATE": 5,
    }
    ready_holdout = sorted(
        row["galaxy"]
        for row in rows
        if row["pilot_role"] == "PILOT_HOLDOUT"
        and row["compiler_readiness_status"] == "READY_FORMULA_COMPILER_REPLAY_CANDIDATE"
    )
    assert ready_holdout == ["NGC1090", "NGC2841", "NGC3198", "NGC5033", "NGC6503"]
    forbidden_columns = {"Vobs", "vobs", "rotation_residual", "delta_r2", "score", "rmse"}
    assert forbidden_columns.isdisjoint(rows[0].keys())


def test_p0_holdout_endpoint_readiness_excludes_endpoint_values() -> None:
    rows = list(
        csv.DictReader(
            (ROOT / "data" / "source_manifests" / "tcdr_v4_p0_holdout_endpoint_readiness_v0_1.csv").open()
        )
    )
    assert len(rows) == 7
    assert sum(1 for row in rows if row["endpoint_availability"] == "available") == 7
    assert sum(int(row["n_rotation_points"]) for row in rows) == 215
    forbidden_columns = {
        "Vflat",
        "vflat",
        "Vobs",
        "vobs",
        "e_Vobs",
        "rotation_residual",
        "delta_r2",
        "score",
        "rmse",
    }
    assert forbidden_columns.isdisjoint(rows[0].keys())
    for row in rows:
        assert row["endpoint_policy"] == "endpoint_values_local_only_not_committed"
        assert row["score_policy"] == "readiness_only_no_endpoint_score"
        assert row["source_label_policy"] == "source_family_already_frozen_before_endpoint_packet"


def test_clean_clone_reproducibility_guard(tmp_path: Path, monkeypatch, capsys) -> None:
    import sys

    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import reproduce
    import run_tcdr_v4_holdout_endpoint_scoring as endpoint_base

    expected_msg = (
        "[SKIP-CLEAN-CLONE] Optional external SPARC MRT files not present; "
        "verified committed derived artifacts"
    )

    # Mode 1: Clean-clone mode (absent external SPARC MRT files)
    monkeypatch.delenv("TCDR_FORCE_CLEAN_CLONE", raising=False)
    assert reproduce.has_external_sparc_inputs(tmp_path) is False
    assert endpoint_base.has_external_sparc_mrt(tmp_path / "data" / "external" / "sparc_preflight") is False

    monkeypatch.setenv("TCDR_FORCE_CLEAN_CLONE", "1")
    mode = reproduce.run_external_or_verify(ROOT)
    out = capsys.readouterr().out
    assert mode == "clean_clone_verified"
    assert expected_msg in out

    endpoint_base.main()
    out_endpoint = capsys.readouterr().out
    assert expected_msg in out_endpoint

    # Mode 2: External SPARC MRT files present (live scoring guard detection + live scoring if local MRT present)
    monkeypatch.delenv("TCDR_FORCE_CLEAN_CLONE", raising=False)
    sim_sparc = tmp_path / "data" / "external" / "sparc_preflight"
    sim_sparc.mkdir(parents=True, exist_ok=True)
    (sim_sparc / "SPARC_Lelli2016c.mrt").write_text("# mock mrt\n", encoding="utf-8")
    (sim_sparc / "MassModels_Lelli2016c.mrt").write_text("# mock mass models\n", encoding="utf-8")
    assert reproduce.has_external_sparc_inputs(tmp_path) is True
    assert endpoint_base.has_external_sparc_mrt(sim_sparc) is True

    if reproduce.has_external_sparc_inputs(ROOT):
        detail, summary, aggregate = endpoint_base.run_scoring()
        assert not detail.empty
        assert not summary.empty
        assert aggregate["n_scoreable_holdout_galaxies"] == 6
