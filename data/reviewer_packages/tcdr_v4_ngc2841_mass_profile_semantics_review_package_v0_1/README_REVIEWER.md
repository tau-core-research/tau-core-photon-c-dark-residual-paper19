# NGC2841 Dragonfly mass-profile semantics review package

This package asks a narrow source-side question for Paper 19 / TCDR-v4:
can the Zhang et al. mass-profile figure be converted into a load-bearing
outer-component formula without using any endpoint rotation information?

## Context

An earlier reviewer digitized the Dragonfly mass-profile figure. The response
passed leakage checks, but a source-side normalization audit found that naive
annular integration of the digitized profile is tens of times larger than the
quoted Zhang et al. integrated stellar mass beyond about 30 kpc. A separate
source-native table search found no machine-readable Sigma_star(R) or
Sigma_gas(R) table in the arXiv source package.

## Your task

Fill `review_response_template.csv`.

Do not digitize new points unless needed to support a source-side semantics
statement. The main questions are:

1. Which displayed curve, if any, corresponds to the isolated outer-disk
   component with quoted stellar mass 1.4e8 Msun?
2. Is there an explicit source-native normalization rule mapping the displayed
   profile to that integrated mass?
3. Can the tens-of-times mismatch be explained by source-side axis/unit/curve
   identity alone?
4. Should the profile remain shape-only, or can it become a load-bearing
   source formula without endpoint information?

## Forbidden inputs

Do not use:

- rotation curves or velocity data;
- SPARC observed velocity;
- endpoint residuals, RMSE, baseline scores, or Tau Core scores;
- required lambda or epsilon diagnostics;
- any answer chosen because it improves or worsens a rotation-curve fit.

The completed CSV must keep:

- `endpoint_replay_permission=must_be_no`;
- `kernel_promotion_permission=must_be_no`;
- `uses_rotation_curve_or_velocity=must_be_false`;
- `uses_endpoint_rotation_residual=must_be_false`;
- `uses_tau_core_score_or_required_lambda=must_be_false`.

## Included files

- `prof_masses1and2_4.pdf`: original mass-profile figure from the source package.
- `zhang2018_mass_surface_density_profile.png`: rendered convenience copy, if available.
- `Zhang_relevant_lines.txt`: relevant source text with line numbers.
- `source_native_table_search.csv/json`: negative search for machine-readable profile tables.
- `semantics_clarification.csv/json`: current blocker localization.
- `normalization_audit.csv`: ratio mismatch audit.
- `digitization_acceptance.csv`: earlier filled digitization acceptance artifact.
- `review_response_template.csv`: file to fill.

## Claim boundary

Package status: `ngc2841_mass_profile_semantics_review_package_not_scoring`.

This package cannot authorize endpoint replay. It can only support a later
source-side decision about whether the mass profile is shape-only or can be
promoted to a load-bearing formula under an explicit source-native rule.
