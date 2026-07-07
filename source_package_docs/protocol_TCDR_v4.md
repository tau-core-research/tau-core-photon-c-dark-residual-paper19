# Tau Core Dark Residual Protocol v4

**Short name:** TCDR-v4
**Status:** real-data-ready protocol skeleton
**Purpose:** pre-registered residual test framework for Tau Core-compatible morphology, filament-boundary, and null/time split signatures.

---

## 1. Purpose

TCDR-v4 tests whether residual gravitational signals remaining after standard baryonic and halo modeling contain structured components linked to pre-defined morphology, environmental boundary, or null/time split variables.

The protocol does not assume that dark matter is absent. It tests whether a subset of dark-sector residuals behaves as if it includes a parent-morphological readout-geometric contribution.

---

## 2. Primary hypotheses

### H1 — Morphological Residual Hypothesis

Residuals after standard baryon+halo modeling correlate with pre-registered galaxy morphology seeds.

Allowed morphology seeds:

```text
θ_disk
θ_bar
bar_strength
bulge_to_disk
r_break
gas_extent
spiral_pitch_or_arm_contrast, if available
```

### H2 — Filament Boundary Hypothesis

Residuals correlate with cosmic environment or filament-boundary variables.

Allowed environment seeds:

```text
θ_filament
D_filament
D_node
θ_tidal
dominant_neighbor_direction
void_boundary_distance
isolation_flag
```

### H3 — Null/Time Split Hypothesis

Residuals inferred from null probes and timelike probes differ in a morphology/environment-dependent way.

```text
R_null = lensing residual
R_time = dynamical or rotation residual
Δτ = standardized(R_null) - standardized(R_time)
```

Tau Core-compatible expectation:

```text
Δτ ∼ morphology + filament + break-radius + controls
```

---

## 3. Recommended analysis stages

```text
Stage 1: nearby spiral galaxies with rotation curves and baryonic profiles
Stage 2: add morphology and filament/environment variables
Stage 3: stacked galaxy-galaxy lensing by morphology/filament classes
Stage 4: null/time split analysis on populations with lensing and dynamics
Stage 5: cluster lensing + dynamics, only after lower-complexity stages
```

---

## 4. Minimum sample requirements

Recommended first sample:

```text
N ≥ 100–300 spiral galaxies
quality rotation curves
good stellar and gas mass profiles
known inclination and distance uncertainties
morphological classification
bar/disk information where possible
environment or filament information if testing H2
```

Quality cuts:

```text
exclude severely disturbed mergers for primary run
flag non-circular motions
remove extreme inclination uncertainty
track distance uncertainty
track low-surface-brightness selection bias
```

---

## 5. Standard model fitting

Before Tau Core variables are tested, fit standard baryon+halo models.

Rotational form:

```text
v_obs²(r) = v_bar²(r) + v_halo²(r)
```

Residual:

```text
R_rot(r) = v_obs²(r) - v_model²(r)
```

or acceleration form:

```text
R_g(r) = g_obs(r) - g_model(r)
```

Minimum halo families:

```text
NFW
Burkert or cored halo
Einasto or comparable flexible halo
```

Optional:

```text
contracted halo
feedback-modified halo
triaxial halo for lensing/dynamics comparison
```

---

## 6. Primary metrics

### Metric 1 — Morphological residual alignment

```text
A_disk = cos(2(θ_R - θ_disk))
A_bar  = cos(2(θ_R - θ_bar))
```

### Metric 2 — Filament boundary alignment

```text
A_fil = cos(2(θ_R - θ_filament))
```

### Metric 3 — Break-radius handoff

```text
r_b = baryonic transition / break radius
r_R = residual transition / mode-change radius
```

Test:

```text
r_R ≈ λτ r_b
```

or:

```text
r_R / r_b ∼ morphology + environment + controls
```

### Metric 4 — Null/time split

```text
Δτ = standardized(R_null) - standardized(R_time)
```

Test:

```text
Δτ ∼ A_disk + A_fil + Break + tidal/environment + controls
```

---

## 7. Required controls

### Halo controls

```text
halo-family variation
halo parameter uncertainty
cored vs cusped halo comparison
triaxial halo check where applicable
```

### Baryonic controls

```text
stellar mass-to-light marginalization
gas mass uncertainty
distance uncertainty
inclination uncertainty
IMF prior variation
```

### Dynamical controls

```text
non-circular motion flag
pressure support
asymmetric drift where relevant
bar-driven motion flag
```

### Lensing controls

```text
lensing reconstruction uncertainty
source redshift uncertainty
PSF and shear calibration
mass-sheet / projection effects
```

### Environment controls

```text
neighbor catalog
tidal index
isolation cut
merger/disturbance flag
```

### Survey/systematics controls

```text
survey footprint
sky position
selection function
surface brightness bias
redshift bias
inclination selection bias
```

### Permutation controls

```text
random filament angle permutation within mass/morphology bins
morphology scramble within matched bins
mass-matched environment shuffle
```

### OOS validation

```text
train: define weights/thresholds/model form
test: evaluate frozen model without adjustment
```

---

## 8. Pre-registration requirements

Before analysis, freeze:

```text
1. sample selection
2. quality cuts
3. allowed halo families
4. allowed baryonic uncertainty priors
5. allowed morphology seeds
6. allowed environment seeds
7. primary metrics
8. permutation controls
9. OOS split
10. success/failure thresholds
11. claim language
```

No post-hoc seed expansion is allowed for primary claims.

---

## 9. Minimal regression forms

Single residual:

```text
R_i = α0
    + α1 H_i
    + α2 B_i
    + β1 A_disk,i
    + β2 A_fil,i
    + β3 Break_i
    + ε_i
```

Null/time split:

```text
Δτ_i = α0
     + α1 H_i
     + α2 B_i
     + α3 S_i
     + β1 A_disk,i
     + β2 A_fil,i
     + β3 Break_i
     + ε_i
```

where:

```text
H_i = halo uncertainty / fit quality
B_i = baryonic uncertainty summary
S_i = survey/systematics summary
```

Tau Core-compatible evidence requires stable non-zero `β` terms under controls.

---

## 10. Scoring

```text
Score 0: residual absent or absorbed by standard controls
Score 1: residual present but unstructured
Score 2: one pre-registered morphology/filament correlation survives weakly
Score 3: structured residual survives halo+baryon controls
Score 4: structured residual survives OOS and permutation tests
Score 5: morphology/filament residual + null/time split survive across independent datasets
```

Interpretation:

```text
0–1: no Tau Core support
2: anomaly candidate
3: Tau Core-compatible structured residual
4: strong candidate
5: serious readout-geometry / new-physics candidate
```

---

## 11. Failure conditions

TCDR-v4 fails for a dataset if:

```text
residual disappears under improved halo model
residual disappears under baryonic uncertainty marginalization
alignment disappears under permutation
OOS validation fails
survey/systematics reproduce the signal
null/time split is absent for strong claims
```

A failed dataset does not kill all Tau Core ideas, but it does reject the TCDR-v4 dark residual hypothesis for that dataset.

---

## 12. Claim discipline

Allowed claims:

```text
Tau Core-compatible structured residual candidate
residual not fully absorbed by tested controls
null/time split motivates further investigation
readout-geometry interpretation remains viable
```

Forbidden claims:

```text
Tau Core proven
dark matter disproven
ΛCDM dead
MOND invalidated
photon proves parent field
```

---

## 13. Output artifacts

A completed TCDR-v4 run should output:

```text
sample manifest
quality cut report
standard fit table
residual table
seed table
permutation test results
OOS validation results
scoring summary
claim boundary note
plots
```
