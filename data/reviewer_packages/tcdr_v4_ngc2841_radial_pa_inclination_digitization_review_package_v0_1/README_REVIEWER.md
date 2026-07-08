# NGC2841 radial PA/inclination digitization review package

This package is a source-side review package for the Tau Core TCDR-v4/Paper 19
NGC2841 outer-capacity route.

## Task

Digitize only the radial position-angle and inclination profiles from the
included Bosma Figure 7 image:

- allowed: panel a, position angle;
- allowed: panel b, inclination;
- forbidden: panel c, rotation velocity;
- forbidden: panel d, surface density;
- forbidden: any endpoint rotation curve, residual, RMSE, baseline score, or
  Tau Core scoring result.

Fill `review_response_template.csv`. Use one row per digitized radius.

## Required verdict fields

Set these values consistently in the completed response:

- `forbidden_inputs_acknowledged=true`
- `uses_rotation_velocity_panel_c=false`
- `uses_surface_density_panel_d=false`
- `uses_endpoint_rotation_curve_or_residual=false`

If any forbidden information was used, do not provide a promoted profile.
Instead mark the package as failed/leaked in the notes.

## Included reference material

- `bosma1981_ngc2841_figure4_6_7.jpg`: source image to digitize.
- `source_native_scalar_pa_inclination_table.csv`: scalar PA/i crosschecks from
  THINGS/de Blok and Samurovic. These are not an answer key.
- `existing_coarse_candidate_do_not_copy.csv`: previous low-resolution internal
  candidate. Use only to understand expected column semantics, not as a source.
- `radial_table_search_audit.csv`: records that no primary machine-readable
  radial PA/i table was located in the bounded source pass.

## Claim boundary

Package status: `ngc2841_radial_pa_inclination_digitization_review_package_not_scoring`.

Completing this package can support a source-side formula-freeze review. It
does not authorize endpoint replay by itself.
