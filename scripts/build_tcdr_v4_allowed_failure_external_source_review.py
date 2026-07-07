from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

WORKLIST = EXTERNAL_DIR / "tcdr_v4_allowed_failure_source_acquisition_worklist_local.csv"

OUT_CSV = EXTERNAL_DIR / "tcdr_v4_allowed_failure_external_source_review_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_allowed_failure_external_source_review_summary_local.json"

CLAIM_BOUNDARY = "allowed_failure_external_source_review_not_endpoint_replay"


SOURCE_NOTES = {
    "NGC2841": {
        "source_review_status": "CAVEATED_SPIRAL_PATH_SOURCE_FOUND_REVIEW_ONLY",
        "source_support_level": "caveated_yes",
        "source_review_permission": "yes_source_side_route_review_only",
        "evidence_summary": (
            "Independent source-side evidence supports a flocculent spiral/path-history "
            "interpretation: Hubble/ESA describes NGC 2841 as a flocculent spiral with "
            "short spiral arms; Dragonfly reports an extended stellar disk with an outer "
            "warp beyond about 30 kpc; molecular-gas morphology also supports the already "
            "frozen ring component. This can motivate a source-side route review, but not "
            "endpoint replay or endpoint-derived kernel promotion."
        ),
        "source_urls": (
            "https://esahubble.org/images/heic1104a/ ; "
            "https://ui.adsabs.harvard.edu/abs/2018ApJ...855...78Z/abstract ; "
            "https://ned.ipac.caltech.edu/level5/March14/Buta/Buta7.html"
        ),
        "source_labels": "flocculent_spiral;outer_warp;large_molecular_ring",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "next_allowed_action": (
            "build a separate source-side spiral/path formula-freeze review for NGC2841; "
            "do not score a new route until that review freezes a kernel without residual input"
        ),
    },
    "UGC00191": {
        "source_review_status": "WEAK_ASYMMETRY_SOURCE_FOUND_NOT_SPIRAL_ROUTE_CLOSING",
        "source_support_level": "weak_caveated",
        "source_review_permission": "yes_source_side_asymmetry_review_only",
        "evidence_summary": (
            "Independent source-side evidence is weaker: the S4G outer-feature catalogue "
            "lists UGC 191 with a tentative asymmetry flag (A?), while the DensePak LSB "
            "study records H-alpha coverage and a linearly rising curve but does not give "
            "source-native spiral geometry. This does not close a spiral route; at most it "
            "motivates a residual-blind asymmetry/path source review."
        ),
        "source_urls": (
            "https://academic.oup.com/mnras/article/444/4/3015/1018101 ; "
            "https://astroweb.case.edu/ssm/papers/ApJv676p920.pdf"
        ),
        "source_labels": "tentative_outer_asymmetry;no_source_native_spiral_geometry_found",
        "endpoint_replay_permission": "no",
        "kernel_promotion_permission": "no",
        "next_allowed_action": (
            "seek stronger residual-blind imaging or catalogue morphology for UGC00191; "
            "keep the spiral best-wrong pressure as a false-component/control-pressure diagnostic"
        ),
    },
}


def build_review() -> tuple[pd.DataFrame, dict[str, object]]:
    worklist = pd.read_csv(WORKLIST)
    galaxies = sorted(worklist["galaxy"].unique().tolist())
    rows: list[dict[str, object]] = []
    for galaxy in galaxies:
        subset = worklist[worklist["galaxy"] == galaxy]
        note = SOURCE_NOTES[galaxy]
        rows.append(
            {
                "galaxy": galaxy,
                "n_worklist_rows": int(len(subset)),
                "worklist_priorities": ";".join(
                    sorted(subset["source_acquisition_priority"].unique().tolist())
                ),
                "best_wrong_components": ";".join(
                    sorted(subset["best_wrong_component"].unique().tolist())
                ),
                **note,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    review = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(review)),
        "n_worklist_rows_covered": int(review["n_worklist_rows"].sum()),
        "galaxies": galaxies,
        "source_review_status_counts": review["source_review_status"].value_counts().to_dict(),
        "source_review_permission_counts": review["source_review_permission"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": review["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": review["kernel_promotion_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The external source review separates source-side route review from endpoint "
            "permission. NGC2841 has caveated independent spiral/path evidence sufficient "
            "for a future source-side formula-freeze review; UGC00191 has only weak "
            "asymmetry support and no route-closing spiral geometry. Neither object gains "
            "endpoint replay or kernel-promotion permission."
        ),
    }
    return review, summary


def main() -> None:
    review, summary = build_review()
    review.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        review[
            [
                "galaxy",
                "source_review_status",
                "source_review_permission",
                "endpoint_replay_permission",
                "kernel_promotion_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
