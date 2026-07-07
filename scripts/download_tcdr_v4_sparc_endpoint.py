from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "external" / "sparc"

SPARC_ENDPOINT_FILES = {
    "Rotmod_LTG.zip": "https://astroweb.case.edu/SPARC/Rotmod_LTG.zip",
    "MassModels_Lelli2016c.mrt": "https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt",
    "SPARC_Lelli2016c.mrt": "https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, out: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "tau-core-paper19-preflight/0.5"})
    with urllib.request.urlopen(request, timeout=60) as response:
        out.write_bytes(response.read())


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download compact SPARC endpoint/baseline files for local TCDR-v4 preflight. "
            "These files are endpoint-side data and must not be used to choose Tau morphology labels."
        )
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--extract-rotmod", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for filename, url in SPARC_ENDPOINT_FILES.items():
        target = args.out_dir / filename
        _download(url, target)
        manifest.append(
            {
                "filename": filename,
                "url": url,
                "bytes": target.stat().st_size,
                "sha256": _sha256(target),
                "tcdr_role": "endpoint_or_baseline_data",
                "allowed_for_source_label": False,
            }
        )

    if args.extract_rotmod:
        extract_dir = args.out_dir / "Rotmod_LTG"
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(args.out_dir / "Rotmod_LTG.zip") as zf:
            zf.extractall(extract_dir)

    manifest_path = args.out_dir / "download_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"WROTE {manifest_path}")
    print("Downloaded SPARC endpoint/baseline files. Do not use these files for source-label selection.")


if __name__ == "__main__":
    main()
