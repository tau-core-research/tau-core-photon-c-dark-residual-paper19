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
