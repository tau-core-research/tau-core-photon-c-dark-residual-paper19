# Review completion notes

Completed file: `review_response_template.csv`.

Scope used: Zhang et al. (2018) mass-surface-density figure only, from the included rendered PNG / source PDF `prof_masses1and2_4.pdf`.

Digitized quantities:

- radial distance in kpc;
- stellar mass surface density `Sigma_star` in `M_sun pc^-2`;
- gas mass surface density `Sigma_gas` in `M_sun pc^-2` where the green HI profile is visible/readable;
- same-figure `Sigma_star/Sigma_gas` ratio as a quotient of the digitized surface-density values, not from any velocity or rotation-curve information.

Profile handling:

- `measured_color` rows represent the blue stellar error-bar/point profile and the green gas profile.
- `constant_outer_color` rows represent a caveated central estimate from the blue shaded constant-outer-colour stellar band, kept separate from the measured-colour rows.
- Rows in/near the grey sensitivity-limit region are retained only as figure-level source-side candidates; missing gas entries mean the gas curve was not readable/available there, not zero gas.

Forbidden inputs were not used. No rotation curve, velocity panel, SPARC observed velocity, endpoint residual, RMSE, baseline score, Tau Core score, required epsilon, or required lambda diagnostic was used.

Verdict: source-side review candidate only. This fills the review response but does not authorize endpoint replay, kernel promotion, or new route scoring by itself.
