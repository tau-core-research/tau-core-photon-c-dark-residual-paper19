# NGC2841 beta/closure reformulation reviewer package

This package asks a narrow source-side question for Paper 19 / TCDR-v4:
is NGC2841 sufficiently supported, from residual-blind source material only,
to continue as a multiplicative beta/closure reformulation candidate?

This is not an endpoint replay package and not a request to judge a rotation
curve fit. The current status is:

`review_open_not_promoted`

## Context

The additive positive-load route remains blocked because no independent
velocity-squared `A_tau` source has been derived. A related Paper 9 audit found
a dimensionless Bullock-like spin/beta proxy for NGC2841:

- `lambda_spin ~= 0.02024`
- `beta_cl ~= 1.08034`

That proxy cannot be used as additive `A_tau`. It can only motivate a separate
multiplicative beta/closure shell:

`v_beta^2(R)=v_carrier^2(R)*[1+(beta_cl-1)*K_beta(R)]`

The three unresolved decisions are:

1. Spin route: can the Bullock-like disk conversion proxy be accepted, rejected,
   or retained only as caveated context for the beta/closure slot?
2. Carrier: is any carrier policy acceptable for preflight freeze, or must it
   remain blocked?
3. `K_beta(R)`: can a dimensionless beta kernel be derived/frozen from the
   included source-side morphology, or must it remain blocked?

## Your task

Fill `review_response_template.csv`.

Use only the included source-side artifacts. If the evidence is insufficient,
choose the blocked/caveated answer. Do not use any rotation-curve residual,
endpoint score, best baseline comparison, or required-load diagnostic.

## Forbidden inputs

Do not use:

- observed rotation curves or velocity residuals;
- SPARC `Vobs`/`errV`;
- endpoint RMSE, baseline scores, wrong-family ranks, or Tau Core endpoint scores;
- required `A_tau`, required lambda, or observed velocity gap diagnostics;
- any answer chosen because it improves or worsens a rotation-curve fit.

The completed CSV must keep:

- `endpoint_replay_permission=must_be_no`;
- `kernel_promotion_permission=must_be_no`;
- `formula_freeze_permission=must_be_no`;
- `uses_rotation_curve_or_velocity=must_be_false`;
- `uses_endpoint_rotation_residual=must_be_false`;
- `uses_tau_core_score_or_required_load=must_be_false`.

## Included files

- `multiplicative_beta_preflight.csv/json`: formula-shell preflight and blockers.
- `beta_closure_label_review.csv/json`: current source-side review-open verdict.
- `paper9_*_row.csv`: NGC2841 rows copied from Paper 9 beta/closure artifacts.
- `source_native_pa_inclination_table.csv/json`: Paper 19 scalar PA/inclination source support.
- `tilted_ring_geometry_source_review.csv/json`: Paper 19 warped-HI tilted-ring source context.
- `surviving_route_ledger.csv`: local NGC2841 route context.
- `positive_outer_capacity_route_reaudit.csv`: why additive positive-load remains blocked.
- `review_response_template.csv`: file to fill.

## Claim boundary

Package status: `ngc2841_beta_closure_reformulation_reviewer_package_not_endpoint`.

This package can only support a later source-side decision about whether a
beta/closure review remains open, is rejected, or may move to a separate
formula-freeze review. It cannot authorize endpoint replay or scoring.
