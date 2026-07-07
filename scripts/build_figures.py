from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
PAPER_FIG_DIR = ROOT / "paper19_submission_source" / "figures"


def main() -> None:
    PAPER_FIG_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(FIG_DIR.glob("tcdr_*.png")):
        shutil.copy2(path, PAPER_FIG_DIR / path.name)
    print(f"COPIED figures to {PAPER_FIG_DIR}")


if __name__ == "__main__":
    main()
