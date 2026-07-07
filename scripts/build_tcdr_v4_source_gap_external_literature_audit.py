from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"

BLOCKER = EXTERNAL_DIR / "tcdr_v4_source_gap_blocker_ledger_local.csv"
OUT_CSV = EXTERNAL_DIR / "tcdr_v4_source_gap_external_literature_audit_local.csv"
OUT_JSON = EXTERNAL_DIR / "tcdr_v4_source_gap_external_literature_audit_summary_local.json"

CLAIM_BOUNDARY = "source_gap_external_literature_audit_local_not_route_promotion"


SOURCE_EVIDENCE = {
    "UGC04499": {
        "external_source_status": "ANTI_SPIRAL_SOURCE_FOUND_KEEP_BLOCKED",
        "source_summary": (
            "Matthews et al.-style late-type/bulgeless study reports UGC 4499 "
            "among featureless disks without large-scale spiral structure; this "
            "argues against promoting the competitive spiral control."
        ),
        "source_supports_spiral_route": "no",
        "source_supports_projection_or_history_route": "no",
        "source_caveat": "anti_spiral_source_not_kernel_repair",
        "reference_key": "DamasSegovia2012Bulgeless",
        "reference_url": "https://academic.oup.com/mnras/article/423/4/3274/1747333",
    },
    "UGC06917": {
        "external_source_status": "NO_NEW_INDEPENDENT_SPIRAL_OR_PATH_SOURCE_FOUND",
        "source_summary": (
            "The frozen S4G-side manifest gives a strong barred late-type source "
            "route and no independent spiral geometry. The quick external pass "
            "did not find a source-native spiral/projection/history token that is "
            "non-overlapping with the existing bar route."
        ),
        "source_supports_spiral_route": "no",
        "source_supports_projection_or_history_route": "no",
        "source_caveat": "quick_literature_pass_not_exhaustive",
        "reference_key": "Salo2015S4GPipeline4;HerreraEndoqui2015S4GFeatures",
        "reference_url": "https://www.oulu.fi/astronomy/S4G_PIPELINE4/html180614.dir/",
    },
    "UGC12732": {
        "external_source_status": "WEAK_NONBAR_SOURCE_FOUND_NOT_ROUTE_CLOSING",
        "source_summary": (
            "Source-side catalogues provide low-inclination H I/global angular "
            "momentum and star-formation morphology entries, and the frozen S4G "
            "manifest records a ring/bar family. These are useful caveats, but "
            "they do not supply a source-native spiral geometry or independent "
            "projection/history token sufficient to promote the spiral control."
        ),
        "source_supports_spiral_route": "no",
        "source_supports_projection_or_history_route": "caveated_no",
        "source_caveat": "nonbar_morphology_proxy_without_spiral_geometry",
        "reference_key": "Murugeshan2020AngularMomentum;DiazGarcia2020SFbars",
        "reference_url": "https://academic.oup.com/mnras/article/496/2/2516/5858925",
    },
}


def build_audit() -> tuple[pd.DataFrame, dict[str, object]]:
    blocker = pd.read_csv(BLOCKER)
    rows: list[dict[str, object]] = []
    for _, row in blocker.iterrows():
        galaxy = str(row["galaxy"])
        evidence = SOURCE_EVIDENCE.get(galaxy)
        if evidence is None:
            evidence = {
                "external_source_status": "NO_EXTERNAL_REVIEW_ENTRY",
                "source_summary": "No external literature audit entry was declared.",
                "source_supports_spiral_route": "no",
                "source_supports_projection_or_history_route": "no",
                "source_caveat": "not_reviewed",
                "reference_key": "",
                "reference_url": "",
            }
        route_permission = (
            "keep_source_gap_blocked"
            if evidence["source_supports_spiral_route"] != "yes"
            and evidence["source_supports_projection_or_history_route"] != "yes"
            else "requires_new_review_before_replay"
        )
        rows.append(
            {
                "support_safe_pool": row["support_safe_pool"],
                "galaxy": galaxy,
                "source_family_candidate": row["source_family_candidate"],
                "matched_component": row["matched_component"],
                "best_wrong_component": row["best_wrong_component"],
                "external_source_status": evidence["external_source_status"],
                "source_supports_spiral_route": evidence["source_supports_spiral_route"],
                "source_supports_projection_or_history_route": evidence[
                    "source_supports_projection_or_history_route"
                ],
                "external_literature_route_permission": route_permission,
                "source_caveat": evidence["source_caveat"],
                "source_summary": evidence["source_summary"],
                "reference_key": evidence["reference_key"],
                "reference_url": evidence["reference_url"],
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    audit = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(audit)),
        "n_unique_galaxies": int(audit["galaxy"].nunique()),
        "external_source_status_counts": audit["external_source_status"].value_counts().to_dict(),
        "route_permission_counts": audit["external_literature_route_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The quick external literature/source pass does not close the source-gap "
            "blocker. UGC04499 gains anti-spiral support, UGC06917 remains bar-only "
            "under the available source ledger, and UGC12732 has weak non-bar "
            "caveats without source-native spiral geometry or independent path/history "
            "support."
        ),
    }
    return audit, summary


def main() -> None:
    audit, summary = build_audit()
    audit.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE LOCAL {OUT_CSV}")
    print(f"WROTE LOCAL {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        audit[
            [
                "support_safe_pool",
                "galaxy",
                "best_wrong_component",
                "external_source_status",
                "external_literature_route_permission",
                "source_caveat",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
