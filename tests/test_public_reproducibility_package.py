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
