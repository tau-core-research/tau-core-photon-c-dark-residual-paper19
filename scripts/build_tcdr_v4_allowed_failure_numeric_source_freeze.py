from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "data" / "external" / "sparc_preflight"
SOURCE_DIR = ROOT / "data" / "source_manifests"

WORKLIST = EXTERNAL_DIR / "tcdr_v4_allowed_failure_numeric_observable_worklist_local.csv"
COORDINATES = SOURCE_DIR / "tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_allowed_failure_numeric_source_freeze_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_allowed_failure_numeric_source_freeze_summary_v0_1.json"

CLAIM_BOUNDARY = "allowed_failure_numeric_source_freeze_not_formula_not_scoring"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


def _arcmin_to_kpc(arcmin: float, distance_mpc: float) -> float:
    return float(arcmin * distance_mpc * 1000.0 * math.pi / 10800.0)


def build_freeze() -> tuple[pd.DataFrame, dict[str, object]]:
    worklist = pd.read_csv(WORKLIST)
    coords = pd.read_csv(COORDINATES).set_index("galaxy")

    ngc2841_distance_mpc = float(coords.loc["NGC2841", "distance_mpc_source"])
    ngc2841_r25_arcmin = 4.05
    ngc2841_r25_kpc = _arcmin_to_kpc(ngc2841_r25_arcmin, ngc2841_distance_mpc)
    ngc2841_break_kpc = 0.45 * ngc2841_r25_kpc

    frozen_values = {
        ("NGC2841", "spiral_inner_kpc_source"): {
            "value": ngc2841_break_kpc,
            "unit": "kpc",
            "source_basis": "Kendall2011PaperI_R25_4p05_arcmin_break_0p45R25_distance_14p1Mpc",
            "source_reference": "KendallClarkeKennicutt2011SpiralI",
            "source_url": "https://academic.oup.com/mnras/article/414/1/538/1094847",
            "freeze_status": "frozen_caveated_numeric_source",
            "freeze_caveat": (
                "NGC2841 is highly inclined and flocculent; Kendall et al. explicitly "
                "treat the two-winding interpretation as tenuous. The break radius is "
                "therefore a caveated source-coordinate, not a validation-grade kernel."
            ),
        },
        ("NGC2841", "spiral_outer_kpc_source"): {
            "value": ngc2841_r25_kpc,
            "unit": "kpc",
            "source_basis": "Kendall2011PaperI_R25_4p05_arcmin_distance_14p1Mpc",
            "source_reference": "KendallClarkeKennicutt2011SpiralI",
            "source_url": "https://academic.oup.com/mnras/article/414/1/538/1094847",
            "freeze_status": "frozen_caveated_numeric_source",
            "freeze_caveat": (
                "Outer spiral support is capped at the quoted optical R25 value. This "
                "does not claim that the full low-surface-brightness disk follows the same "
                "spiral/path formula."
            ),
        },
        ("NGC2841", "spiral_pitch_median_abs_deg_source"): {
            "value": 7.0,
            "unit": "deg",
            "source_basis": "Kendall2011PaperI_outer_spiral_pitch_about_7deg_for_R_gte_0p45R25",
            "source_reference": "KendallClarkeKennicutt2011SpiralI;KendallClarkeKennicutt2015SpiralII",
            "source_url": "https://academic.oup.com/mnras/article/414/1/538/1094847 ; https://academic.oup.com/mnras/article-pdf/446/4/4155/9389617/stu2431.pdf",
            "freeze_status": "frozen_caveated_numeric_source",
            "freeze_caveat": (
                "The single pitch angle is explicitly uncertain because NGC2841 has high "
                "inclination and complex/flocculent spiral structure."
            ),
        },
        ("NGC2841", "warp_onset_or_path_environment_numeric_source"): {
            "value": 30.0,
            "unit": "kpc",
            "source_basis": "Zhang2018Dragonfly_outer_disk_warp_beyond_about_30kpc",
            "source_reference": "Zhang2018NGC2841Dragonfly",
            "source_url": "https://ui.adsabs.harvard.edu/abs/2018ApJ...855...78Z/abstract",
            "freeze_status": "frozen_caveated_numeric_source",
            "freeze_caveat": (
                "The warp onset is a path/history support coordinate. It does not by itself "
                "define a score-bearing spiral formula."
            ),
        },
    }

    rows: list[dict[str, object]] = []
    for request in worklist.to_dict(orient="records"):
        galaxy = str(request["galaxy"])
        observable = str(request["requested_observable"])
        freeze = frozen_values.get((galaxy, observable))
        if freeze is None:
            rows.append(
                {
                    **request,
                    "frozen_numeric_value": "",
                    "frozen_numeric_unit": "",
                    "numeric_source_freeze_status": "not_frozen_missing_route_closing_source",
                    "numeric_source_basis": "",
                    "numeric_source_reference": "",
                    "numeric_source_url": "",
                    "numeric_source_caveat": "No residual-blind route-closing numeric source was found in the current bounded pass.",
                    "formula_freeze_permission": "no",
                    "endpoint_replay_permission": "no",
                    "kernel_promotion_permission": "no",
                    "new_route_scoring_permission": "no",
                    "endpoint_data_policy": ENDPOINT_POLICY,
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
            continue

        rows.append(
            {
                **request,
                "frozen_numeric_value": freeze["value"],
                "frozen_numeric_unit": freeze["unit"],
                "numeric_source_freeze_status": freeze["freeze_status"],
                "numeric_source_basis": freeze["source_basis"],
                "numeric_source_reference": freeze["source_reference"],
                "numeric_source_url": freeze["source_url"],
                "numeric_source_caveat": freeze["freeze_caveat"],
                "formula_freeze_permission": "no",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    out = pd.DataFrame(rows)
    summary = {
        "n_rows": int(len(out)),
        "n_galaxies": int(out["galaxy"].nunique()),
        "galaxies": sorted(out["galaxy"].unique().tolist()),
        "numeric_source_freeze_status_counts": out["numeric_source_freeze_status"].value_counts().sort_index().to_dict(),
        "ngc2841_r25_arcmin_source": ngc2841_r25_arcmin,
        "ngc2841_distance_mpc_source": ngc2841_distance_mpc,
        "ngc2841_r25_kpc_computed": ngc2841_r25_kpc,
        "ngc2841_break_0p45r25_kpc_computed": ngc2841_break_kpc,
        "formula_freeze_permission_counts": out["formula_freeze_permission"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": out["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": out["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": out["new_route_scoring_permission"].value_counts().to_dict(),
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "The bounded source pass freezes four caveated numeric NGC2841 "
            "spiral/path observables from Kendall et al. and Zhang et al. UGC00191 "
            "remains missing a route-closing numeric source. These values are source "
            "coordinates only; they do not authorize formula freeze or scoring."
        ),
    }
    return out, summary


def main() -> None:
    out, summary = build_freeze()
    out.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        out[
            [
                "galaxy",
                "requested_observable",
                "frozen_numeric_value",
                "frozen_numeric_unit",
                "numeric_source_freeze_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
