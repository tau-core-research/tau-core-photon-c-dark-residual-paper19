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
