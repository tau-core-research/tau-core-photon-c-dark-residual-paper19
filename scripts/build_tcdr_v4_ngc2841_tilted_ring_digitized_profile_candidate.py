from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_manifests"
LITERATURE_DIR = ROOT / "data" / "external" / "literature"

FIGURE_URL = "https://ned.ipac.caltech.edu/level5/March05/Bosma/Figures/figure4_6_7.jpg"
FIGURE_CACHE = LITERATURE_DIR / "bosma1981_ngc2841_figure4_6_7.jpg"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate_v0_1.csv"
OUT_JSON = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate_summary_v0_1.json"

CLAIM_BOUNDARY = "ngc2841_tilted_ring_digitized_profile_candidate_not_endpoint"
ENDPOINT_POLICY = "source_side_only_do_not_use_rotation_residuals_endpoint_scores_or_baseline_scores"


# Coarse, residual-blind manual digitization from Bosma Fig. 7 panels a and b.
# Panel c (rotation velocity) and panel d (surface density) are intentionally not used.
PROFILE_POINTS = [
    {"radius_kpc": 0.0, "position_angle_deg": 148.0, "inclination_deg": 68.0},
    {"radius_kpc": 5.0, "position_angle_deg": 148.0, "inclination_deg": 68.0},
    {"radius_kpc": 8.0, "position_angle_deg": 148.0, "inclination_deg": 68.0},
    {"radius_kpc": 10.0, "position_angle_deg": 150.0, "inclination_deg": 68.0},
    {"radius_kpc": 13.0, "position_angle_deg": 148.5, "inclination_deg": 69.0},
    {"radius_kpc": 16.0, "position_angle_deg": 150.0, "inclination_deg": 70.5},
    {"radius_kpc": 19.0, "position_angle_deg": 150.0, "inclination_deg": 72.5},
    {"radius_kpc": 21.0, "position_angle_deg": 154.0, "inclination_deg": 75.0},
    {"radius_kpc": 24.0, "position_angle_deg": 154.0, "inclination_deg": 76.0},
    {"radius_kpc": 27.0, "position_angle_deg": 158.0, "inclination_deg": 76.0},
    {"radius_kpc": 30.0, "position_angle_deg": 158.0, "inclination_deg": 78.5},
    {"radius_kpc": 34.0, "position_angle_deg": 160.0, "inclination_deg": 81.0},
    {"radius_kpc": 37.0, "position_angle_deg": 160.0, "inclination_deg": 83.0},
]


def _ensure_figure_cache() -> tuple[str, int, tuple[int, int]]:
    LITERATURE_DIR.mkdir(parents=True, exist_ok=True)
    if not FIGURE_CACHE.exists():
        raw = urlopen(FIGURE_URL, timeout=30).read()
        FIGURE_CACHE.write_bytes(raw)
    raw = FIGURE_CACHE.read_bytes()
    image = Image.open(FIGURE_CACHE)
    digest = hashlib.sha256(raw).hexdigest()
    return digest, len(raw), image.size


def build_candidate() -> tuple[pd.DataFrame, dict[str, object]]:
    digest, byte_size, image_size = _ensure_figure_cache()
    rows = []
    for point in PROFILE_POINTS:
        rows.append(
            {
                "galaxy": "NGC2841",
                **point,
                "source_reference": "Bosma1981NGC2841HI",
                "source_url": FIGURE_URL,
                "source_figure_cache": str(FIGURE_CACHE.relative_to(ROOT)),
                "source_figure_sha256": digest,
                "digitized_panels_used": "figure7a_position_angle;figure7b_inclination",
                "digitized_panels_excluded": "figure7c_rotation_velocity;figure7d_surface_density",
                "digitization_method": "coarse_manual_low_resolution_source_figure_digitization",
                "digitization_status": "candidate_profile_needs_independent_review",
                "profile_use_permission": "review_candidate_only_no_scoring",
                "endpoint_replay_permission": "no",
                "kernel_promotion_permission": "no",
                "new_route_scoring_permission": "no",
                "forbidden_inputs": (
                    "rotation_curve;Vobs;residual;RMSE;baseline_score;endpoint_rank;"
                    "required_epsilon_fit;figure7c_rotation_velocity"
                ),
                "uses_vobs_or_residual": "no",
                "endpoint_data_policy": ENDPOINT_POLICY,
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    frame = pd.DataFrame(rows)
    pa_delta = float(frame["position_angle_deg"].max() - frame["position_angle_deg"].min())
    inc_delta = float(frame["inclination_deg"].max() - frame["inclination_deg"].min())
    summary = {
        "n_rows": int(len(frame)),
        "galaxies": sorted(frame["galaxy"].unique().tolist()),
        "figure_url": FIGURE_URL,
        "figure_cache": str(FIGURE_CACHE.relative_to(ROOT)),
        "figure_sha256": digest,
        "figure_byte_size": int(byte_size),
        "figure_image_size_px": list(image_size),
        "digitized_panels_used": ["figure7a_position_angle", "figure7b_inclination"],
        "digitized_panels_excluded": ["figure7c_rotation_velocity", "figure7d_surface_density"],
        "radius_range_kpc": [float(frame["radius_kpc"].min()), float(frame["radius_kpc"].max())],
        "position_angle_range_deg": [
            float(frame["position_angle_deg"].min()),
            float(frame["position_angle_deg"].max()),
        ],
        "inclination_range_deg": [
            float(frame["inclination_deg"].min()),
            float(frame["inclination_deg"].max()),
        ],
        "position_angle_delta_deg": pa_delta,
        "inclination_delta_deg": inc_delta,
        "digitization_status_counts": frame["digitization_status"].value_counts().to_dict(),
        "profile_use_permission_counts": frame["profile_use_permission"].value_counts().to_dict(),
        "endpoint_replay_permission_counts": frame["endpoint_replay_permission"].value_counts().to_dict(),
        "kernel_promotion_permission_counts": frame["kernel_promotion_permission"].value_counts().to_dict(),
        "new_route_scoring_permission_counts": frame["new_route_scoring_permission"].value_counts().to_dict(),
        "forbidden_endpoint_inputs_used_counts": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        "formula_ready": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": (
            "A residual-blind coarse tilted-ring profile candidate can be digitized from "
            "Bosma Figure 7 panels a and b only. It indicates an outer PA change of about "
            f"{pa_delta:.1f} deg and an inclination change of about {inc_delta:.1f} deg "
            "over 0--37 kpc. Because the digitization is low-resolution and unreviewed, "
            "it is not a frozen formula input and does not authorize endpoint replay."
        ),
        "next_allowed_action": (
            "independent reviewer digitization or source-native table lookup; after that, "
            "a geometry-only formula-freeze candidate may be built without using panel c "
            "or any endpoint residual"
        ),
    }
    return frame, summary


def main() -> None:
    frame, summary = build_candidate()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {OUT_CSV}")
    print(f"WROTE {OUT_JSON}")
    print(json.dumps(summary, indent=2))
    print(
        frame[
            [
                "radius_kpc",
                "position_angle_deg",
                "inclination_deg",
                "digitization_status",
                "profile_use_permission",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
