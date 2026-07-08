# NGC2841 beta/closure endpoint authorization reviewer package

This package asks one bounded question:

Can the frozen NGC2841 beta/closure context formula be handed to a separate
endpoint scoring script unchanged?

This is not a scoring package and contains no endpoint results. It only contains
the frozen source-side formula-review artifacts.

## Frozen formula

`v_beta_context^2(R)=v_carrier^2(R)*[1+(beta_context-1)*K_beta_shape(R)]`

where:

- `beta_context = 1.0803447810919469`, retained only as a caveated
  dimensionless context coefficient, not as a direct physical spin measurement;
- `K_beta_shape(R)` is the accepted Bosma Fig. 7a/7b PA/inclination shape,
  min-max normalized and interpolated onto the carrier grid;
- `v_carrier^2(R)=sign(Vgas)Vgas^2 + 0.5 Vdisk^2 + 0.7 Vbul^2`, read only from
  SPARC source-side component columns.

## What you are allowed to decide

Fill `review_response_template.csv`.

You may authorize a future endpoint replay only if all of the following are
true:

1. the scoring script must read the frozen formula profile unchanged;
2. no formula term may be retuned after inspecting observed rotation data;
3. no morphology/readout label may be changed from endpoint performance;
4. the result must be reported as a single-object preliminary endpoint/control
   replay, not as validation;
5. the caveated `beta_context` coefficient must remain caveated and must not be
   described as a direct spin measurement.

## Forbidden inputs

Do not use:

- observed rotation curves or velocity residuals;
- SPARC `Vobs`/`errV`;
- endpoint RMSE, baseline scores, wrong-family ranks, or Tau Core endpoint scores;
- required `A_tau`, required lambda, or observed velocity gap diagnostics;
- any answer chosen because it improves or worsens a rotation-curve fit.

## Included files

- `beta_context_formula_freeze_review.csv/json`
- `k_beta_profile_freeze_review.csv/json`
- `baryonic_carrier_freeze_review.csv/json`
- `review_response_acceptance.csv/json`
- `multiplicative_beta_preflight.csv/json`
- `review_response_template.csv`

## Claim boundary

Package status: `ngc2841_beta_closure_endpoint_authorization_reviewer_package_not_scoring`.

Authorization, if granted, means only that a future separate scoring script may
read the frozen formula unchanged. It is not an empirical validation claim.
