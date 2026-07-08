# Review completion notes - NGC2841 mass-profile semantics

## Completed artifact

`review_response_template.csv` has been filled with four source-side semantic answers.

## Reviewer verdict

The displayed Zhang et al. mass-profile curves are useful as source-side morphology/shape information, but the included source materials do not provide an explicit source-native rule that maps the displayed `Sigma_star(R)` profile to the quoted integrated outer-disk stellar mass of `1.4e8 Msun` beyond about 30 kpc.

The safest interpretation is therefore:

- do not promote the profile to a load-bearing normalized formula;
- do not perform endpoint replay;
- do not use any rotation curve, residual, RMSE, Tau Core score, required lambda, or required epsilon information;
- retain the profile as `shape_only` unless an author/source-native component table or explicit normalization rule is obtained.

## Key source-side reasoning

1. The source text defines the plotted stellar profiles as mass surface-density profiles derived from photometry and color assumptions.
2. The measured-color and constant outer-color variants are display/profile variants, not explicitly declared as the isolated outer-disk component normalized to the quoted integrated mass.
3. The quoted `1.4 +/- 0.2 x 10^8 Msun` mass appears as a separate integrated outer-disk statement.
4. The arXiv source package search found no machine-readable `Sigma_star(R)` or `Sigma_gas(R)` table and no explicit component-normalization mapping.
5. The normalization audit shows tens-of-times mismatch under naive annular integration, so the displayed curve cannot be used as a normalized load without additional source semantics.

## Completed answers

| question_id | reviewer_answer | confidence |
|---|---:|---:|
| Q1_curve_identity | figure_total_profile_not_isolated_component | medium |
| Q2_normalization_mapping | no_not_in_source | high |
| Q3_axis_or_units_issue | no | medium |
| Q4_allowed_use | shape_only | high |

## Guardrails preserved

All rows keep:

- `endpoint_replay_permission=must_be_no`
- `kernel_promotion_permission=must_be_no`
- `uses_rotation_curve_or_velocity=must_be_false`
- `uses_endpoint_rotation_residual=must_be_false`
- `uses_tau_core_score_or_required_lambda=must_be_false`
