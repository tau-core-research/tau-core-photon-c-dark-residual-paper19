# NGC2841 Dragonfly mass-profile digitization review package

This package is a source-side review package for the Tau Core TCDR-v4/Paper 19
NGC2841 outer-capacity load route.

## Task

Digitize only the mass-surface-density profile in Zhang et al. (2018),
`prof_masses1and2_4.pdf`.

Allowed quantities:

- radius in kpc;
- stellar mass surface density, Sigma_star [M_sun pc^-2];
- gas mass surface density, Sigma_gas [M_sun pc^-2];
- optional Sigma_star/Sigma_gas ratio if read directly from the same figure;
- profile variant if visually distinguishable: measured color, constant outer
  color, or unclear.

Forbidden quantities:

- any rotation curve or velocity data;
- SPARC observed velocity;
- endpoint residuals, RMSE, baseline scores, or Tau Core scores;
- required lambda or required epsilon diagnostics;
- any choice of points designed to improve a rotation-curve fit.

Fill `review_response_template.csv`. Use one row per digitized radius. If the
figure is unreadable at a radius, mark `quality_flag=unreadable` rather than
guessing.

## Required leakage flags

The completed CSV must set:

- `forbidden_inputs_acknowledged=true`
- `uses_rotation_curve_or_velocity=false`
- `uses_endpoint_rotation_residual=false`
- `uses_tau_core_score_or_required_lambda=false`

If any forbidden information was used, do not promote the profile. Mark the
response as leaked/failed in the notes.

## Included files

- `prof_masses1and2_4.pdf`: original arXiv source figure.
- `zhang2018_mass_surface_density_profile.png`: rendered convenience copy, if
  Poppler was available when the package was built.
- `Zhang_accepted_2col_excerpt.txt`: source text lines documenting the formula,
  mass ratio, and outer stellar mass statements.
- `load_source_search.csv` and `load_source_search_summary.json`: the local
  source-side audit that explains why this review package is needed.
- `review_response_template.csv`: file to fill.

## Claim boundary

Package status: `ngc2841_mass_profile_digitization_review_package_not_scoring`.

Completing this package can support a future source-side load-profile
acceptance review. It does not authorize endpoint replay or kernel promotion by
itself.
