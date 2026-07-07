from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper19_submission_source"
OUT = ROOT / "arxiv_submission_source.zip"

EXCLUDE_SUFFIXES = {
    ".aux",
    ".bbl",
    ".bcf",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdf",
    ".run.xml",
    ".synctex.gz",
}


def should_include(path: Path) -> bool:
    return path.is_file() and path.suffix not in EXCLUDE_SUFFIXES


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SOURCE.rglob("*")):
            if should_include(path):
                zf.write(path, path.relative_to(SOURCE))
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    main()
