from __future__ import annotations

import csv
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
