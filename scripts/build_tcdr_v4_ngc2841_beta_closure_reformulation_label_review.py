from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT.parent
SOURCE_DIR = ROOT / "data" / "source_manifests"
PAPER9_DERIVED = PROJECTS / "tau-core-projection-readout-paper9" / "data" / "derived"

PREFLIGHT_SUMMARY = (
    SOURCE_DIR
    / "tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight_summary_v0_1.json"
)
PAPER9_TRANSFER_CANDIDATES = PAPER9_DERIVED / "ugc12506_beta_closure_transfer_candidates.csv"
PAPER9_TRANSFER_PRIORITY = PAPER9_DERIVED / "ugc12506_beta_closure_transfer_priority_gate.csv"
PAPER9_BULLOCK_PROXY = PAPER9_DERIVED / "ugc12506_beta_closure_bullock_spin_conversion_proxy_values.csv"
PAPER19_TILTED_RING = SOURCE_DIR / "tcdr_v4_ngc2841_tilted_ring_geometry_source_review_v0_1.csv"
PAPER19_PA_I_SUMMARY = (
    SOURCE_DIR / "tcdr_v4_ngc2841_source_native_pa_inclination_table_summary_v0_1.json"
)
PAPER19_SURVIVING_LEDGER = SOURCE_DIR / "tcdr_v4_ngc2841_surviving_route_ledger_v0_1.csv"

OUT_CSV = SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_v0_1.csv"
OUT_JSON = (
    SOURCE_DIR / "tcdr_v4_ngc2841_beta_closure_reformulation_label_review_summary_v0_1.json"
)

CLAIM_BOUNDARY = "ngc2841_beta_closure_reformulation_label_review_not_endpoint"
ENDPOINT_POLICY = (
    "source_side_reformulation_review_only_do_not_use_rotation_residuals_endpoint_scores_or_required_gap"
)
FORBIDDEN_INPUTS = (
    "Vobs;rotation_curve;residual;RMSE;baseline_score;endpoint_rank;"
    "required_A_tau;required_lambda;observed_velocity_gap;posthoc_family_choice"
)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_one(path: Path, galaxy: str) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite artifact: {path}")
    frame = pd.read_csv(path)
    row = frame[frame["galaxy"] == galaxy]
    if row.empty:
        raise ValueError(f"{galaxy} not present in {path}")
    return row.iloc[0].to_dict()


def _has_tilted_ring_support() -> bool:
    if not PAPER19_TILTED_RING.exists():
        return False
    frame = pd.read_csv(PAPER19_TILTED_RING)
    wanted = {
        "outer_hi_orientation_change",
        "annular_tilted_ring_model",
        "outer_inclination_adjustment",
    }
    return wanted.issubset(set(frame["geometry_item"].astype(str)))


def _has_surviving_outer_hi_route() -> bool:
    if not PAPER19_SURVIVING_LEDGER.exists():
        return False
    frame = pd.read_csv(PAPER19_SURVIVING_LEDGER)
    row = frame[frame["route_id"] == "composite_outer_morphology"]
    if row.empty:
        return False
    return str(row.iloc[0]["shape_status"]).startswith("source_supported")


def build_review() -> tuple[pd.DataFrame, dict[str, object]]:
    preflight = _load_json(PREFLIGHT_SUMMARY)
    pa_i_summary = _load_json(PAPER19_PA_I_SUMMARY)
    transfer_candidate = _read_one(PAPER9_TRANSFER_CANDIDATES, "NGC2841")
    transfer_priority = _read_one(PAPER9_TRANSFER_PRIORITY, "NGC2841")
    bullock = _read_one(PAPER9_BULLOCK_PROXY, "NGC2841")

    lambda_spin = float(bullock["lambda_bullock_disk_proxy"])
    beta_cl = float(bullock["beta_if_bullock_disk_proxy_used"])
    source_native_inclination = float(pa_i_summary["mean_source_native_inclination_deg"])
    transfer_inclination = float(transfer_candidate["inclination_deg"])
    transfer_score = float(transfer_candidate["transfer_priority_score"])
    nfw_load = float(transfer_priority["nfw_preference_load"])
    tilted_ring_support = _has_tilted_ring_support()
    composite_support = _has_surviving_outer_hi_route()

    rows = [
        {
            "galaxy": "NGC2841",
            "review_item": "paper9_predeclared_transfer_candidate",
            "source_status": "supportive_but_source_acquisition_required",
            "source_basis": (
                "Paper 9 predeclares NGC2841 as a beta-closure transfer candidate "
                f"with score={transfer_score:.6g}, inclination={transfer_inclination:.3g} deg, "
                "extended-HI/massive-gas context, and missing native spin/halo/PV fields."
            ),
            "reformulation_implication": "beta_closure_review_route_open_not_promoted",
            "blocker": str(transfer_candidate["missing_source_native_fields"]),
        },
        {
            "galaxy": "NGC2841",
            "review_item": "paper9_weak_nfw_preference_transfer_priority",
            "source_status": "weak_support_control_target",
            "source_basis": (
                "Paper 9 classifies NGC2841 as WEAK_NFW_PREFERENCE_TRANSFER_TARGET "
                f"with nfw_preference_load={nfw_load:.6g}; this is not a primary "
                "source-native closure confirmation."
            ),
            "reformulation_implication": "supports_secondary_or_control_beta_route_only",
            "blocker": str(transfer_priority["still_missing_fields"]),
        },
        {
            "galaxy": "NGC2841",
            "review_item": "bullock_disk_spin_conversion_proxy",
            "source_status": "dimensionless_proxy_available_review_required",
            "source_basis": (
                f"Paper 9 computes lambda_spin={lambda_spin:.12g} and "
                f"beta_cl={beta_cl:.12g} from a Bullock-like disk conversion proxy. "
                "The artifact itself marks accepted_as_beta_cl_lambda_spin=False."
            ),
            "reformulation_implication": "may_feed_preflight_beta_shell_after_independent_review",
            "blocker": "conversion_proxy_not_direct_halo_envelope_spin_measurement",
        },
        {
            "galaxy": "NGC2841",
            "review_item": "paper19_hi_warp_tilted_ring_source_context",
            "source_status": "supportive_geometry_context",
            "source_basis": (
                "Paper 19 source ledgers support an outer H I warp/tilted-ring and "
                "composite outer morphology context."
            ),
            "reformulation_implication": (
                "supports_reformulation_review_context_but_not_beta_kernel_or_carrier"
            ),
            "blocker": "geometry_context_does_not_supply_K_beta_or_beta_carrier",
        },
        {
            "galaxy": "NGC2841",
            "review_item": "source_native_inclination_crosscheck",
            "source_status": "supportive_scalar_projection_context",
            "source_basis": (
                f"Paper 19 source-native PA/i audit gives mean inclination "
                f"{source_native_inclination:.3g} deg, consistent with a high-inclination "
                "projection-sensitive object."
            ),
            "reformulation_implication": (
                "supports_observer_projection_context_not_beta_closure_promotion_by_itself"
            ),
            "blocker": "scalar_inclination_is_not_radial_K_beta_profile",
        },
        {
            "galaxy": "NGC2841",
            "review_item": "additive_route_separation",
            "source_status": "separation_required",
            "source_basis": (
                "The preflight formula is multiplicative and dimensionless; the additive "
                "A_tau positive-load theorem remains blocked."
            ),
            "reformulation_implication": "prevents_curve_rescue_by_relabeling_A_tau_as_beta",
            "blocker": "must_not_reuse_required_positive_load_gap_or_additive_A_tau_worklist",
        },
        {
            "galaxy": "NGC2841",
            "review_item": "label_review_verdict",
            "source_status": "review_open_not_promoted",
            "source_basis": (
                "The combined source-side record is sufficient to prepare a beta/closure "
                "review package, but insufficient to promote the family label or run scoring."
            ),
            "reformulation_implication": (
                "CAVEATED_REFORMULATION_REVIEW_OPEN_FORMULA_AND_ENDPOINT_BLOCKED"
            ),
            "blocker": (
                "need_independent_spin_route_decision;need_source_frozen_carrier;"
                "need_source_frozen_K_beta"
            ),
        },
    ]

    frame = pd.DataFrame(rows)
    frame["uses_vobs_or_residual"] = "no"
    frame["endpoint_replay_permission"] = "no"
    frame["kernel_promotion_permission"] = "no"
    frame["formula_freeze_permission"] = "no"
    frame["reformulation_label_promotion_permission"] = "no"
    frame["review_package_permission"] = "yes"
    frame["endpoint_data_policy"] = ENDPOINT_POLICY
    frame["forbidden_endpoint_inputs"] = FORBIDDEN_INPUTS
    frame["claim_boundary"] = CLAIM_BOUNDARY

    summary = {
        "artifact": OUT_CSV.name,
        "galaxy": "NGC2841",
        "n_rows": int(len(frame)),
        "claim_boundary": CLAIM_BOUNDARY,
        "preflight_claim_boundary": preflight["claim_boundary"],
        "lambda_spin": lambda_spin,
        "beta_cl_if_used": beta_cl,
        "paper9_transfer_priority_score": transfer_score,
        "paper9_transfer_priority_class": transfer_priority["transfer_priority_class"],
        "paper9_nfw_preference_load": nfw_load,
        "source_native_mean_inclination_deg": source_native_inclination,
        "tilted_ring_support_present": tilted_ring_support,
        "composite_outer_morphology_support_present": composite_support,
        "beta_closure_reformulation_review_open": True,
        "reformulation_label_promoted": False,
        "endpoint_ready": False,
        "formula_freeze_ready": False,
        "carrier_freeze_ready": False,
        "K_beta_freeze_ready": False,
        "review_package_permission": True,
        "blocked_requirement_ids": [
            "BETA_2A_INDEPENDENT_SPIN_ROUTE_DECISION",
            "BETA_2B_SOURCE_FROZEN_CARRIER",
            "BETA_2C_SOURCE_FROZEN_K_BETA",
        ],
        "permission_counts": {
            "endpoint_replay_permission": frame["endpoint_replay_permission"].value_counts().to_dict(),
            "kernel_promotion_permission": frame["kernel_promotion_permission"].value_counts().to_dict(),
            "formula_freeze_permission": frame["formula_freeze_permission"].value_counts().to_dict(),
            "reformulation_label_promotion_permission": frame[
                "reformulation_label_promotion_permission"
            ].value_counts().to_dict(),
            "review_package_permission": frame["review_package_permission"].value_counts().to_dict(),
            "uses_vobs_or_residual": frame["uses_vobs_or_residual"].value_counts().to_dict(),
        },
        "verdict": (
            "NGC2841 has enough residual-blind source context to open a beta/closure "
            "reformulation review package: Paper 9 predeclares it as a transfer "
            "candidate, supplies a Bullock-like dimensionless lambda/beta proxy, and "
            "Paper 19 supplies high-inclination warped-HI/tilted-ring context. The label "
            "is not promoted because the spin normalization route remains review-required, "
            "the NFW preference is weak, and no carrier or K_beta profile is frozen."
        ),
        "next_allowed_action": (
            "prepare_reviewer_package_for_spin_route_carrier_and_K_beta_decisions_or_keep_route_review_open"
        ),
    }
    return frame, summary


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    frame, summary = build_review()
    frame.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
