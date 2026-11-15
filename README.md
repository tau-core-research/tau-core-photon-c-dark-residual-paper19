# Tau Core Photon-C Dark Residual Paper 19

Private Paper 19 scaffold:

**Photon-C dark residuals: a synthetic null/time split protocol for
morphology-seeded Tau Core tests**

This repository turns `Tau_Core_Photon_C_DarkResidual_Package.zip` into a
reproducible paper package. It preserves the source package as provenance,
promotes the TCDR-v1/v2/v3 synthetic toys and TCDR-v4 protocol skeleton into a
structured manuscript, compiles a PDF, and prepares an arXiv source archive.

## Main Claim

The paper defines a controlled synthetic methodology for testing whether
pre-registered morphology, filament-boundary, break-radius, and null/time split
seed variables can be recovered when injected into dark-residual-like mock data.

The included toy summary reports:

```text
TCDR-v1 clean morphology toy:       max score 5 at tau_strength=0.60
TCDR-v2 noisy controls toy:         max score 4 at tau_strength=0.30/0.60
TCDR-v3 null/time split toy:        max score 3 at tau_strength=0.35/0.60
Null runs at tau_strength=0:        score 0 across v1, v2, and v3
Permutation p-values at strong tau: p ~= 0.001996 in the fixed-seed runs
```

The v0.2 package also includes a 32-seed robustness replay on null and
strong-injection cases. The replay keeps null false positives low in the toy
and shows stable recovery for TCDR-v1/v2 strong injections and TCDR-v3 strong
split injection. The intermediate TCDR-v3 split case remains sensitivity
limited and is reported as a caveat, not hidden.

The v0.3 package adds a blinded synthetic injection challenge with realistic
nuisance columns and a wrong-seed control. The frozen classifier correctly
rejects all 8 null cases and recovers 12 of 18 injected cases, while missing 6
weak/borderline injections. This is intentionally conservative: the challenge
demonstrates controlled false-positive behavior, not universal sensitivity.

The v0.4 package adds a harder realistic-mock stress test with shared survey
mask structure, foreground-like contamination, source selection bias,
orientation-only controls, wrong-seed controls, and random controls. The frozen
specificity-first classifier rejects all 10 null cases and recovers 11 of 22
injected cases. This is a realistic nuisance robustness check, not a validation
claim: the protocol remains conservative and misses many weak or borderline
injections.

The scientific value is protocol-level: the toys show a recovery/failure
discipline for a morphology-seeded residual family and motivate a real-data
TCDR-v4 ladder.

The v0.5 preparation step starts that real-data ladder without performing
endpoint scoring. It adds a reproducible TCDR-v4 source manifest that separates
source-side morphology/proxy inputs from endpoint dynamics inputs. In
particular, SPARC rotation/mass-model products are endpoint/baseline data and
are explicitly forbidden for morphology-label rescue, while S4G and Galaxy Zoo
are source-side morphology routes that must be frozen before scoring.

The next preflight artifact builds a SPARC source-freeze queue from SPARC
sample metadata only, intentionally excluding `Vflat` and rotation endpoint
values. It currently lists 175 SPARC objects: 66 `P0_SOURCE_REVIEW`, 60
`P1_SOURCE_REVIEW`, and 49 `P2_SOURCE_REVIEW` candidates for external
morphology/source review.

The first external source-side lookup checks the 66 P0 objects against the S4G
catalogue through IRSA TAP. It finds 32 name-based S4G morphology matches and
leaves 34 objects as `not_found_by_name` for alias/manual-source review. This
is source-side morphology acquisition only; no SPARC endpoint residual is
inspected.

A second source-side resolver pass uses SIMBAD coordinates for those 34
name-unmatched objects and cross-matches them to S4G within 1 arcmin. It
recovers 11 additional coordinate matches, bringing the current P0 S4G
source-side coverage to 43/66 and leaving 23 P0 objects for non-S4G routes or
manual source review.

For the 23 non-S4G P0 objects, a SIMBAD fallback manifest resolves all 23
objects and records morphology-type fields for 22 of them. This fallback is
weaker than S4G structural morphology because it is a catalogue type/identity
source, not a homogeneous infrared morphology table, but it closes the first
P0 identity/morphology source ledger without touching rotation endpoints.

The combined P0 source-tier manifest freezes this source hierarchy:
`S4G_STRONG=32`, `S4G_COORD_RESCUE=11`, `SIMBAD_FALLBACK=22`, and
`SIMBAD_IDENTITY_ONLY=1`. Thus all 66 P0 objects have an identity tier, 65 have
some source-side morphology type, and 43 have homogeneous S4G structural
morphology before any endpoint scoring.

The first endpoint-blind morphology-family freeze maps those source tiers to
candidate readout families by morphology alone: `K_BARRED_M2=30`,
`K_EXPONENTIAL_SPIRAL_DISK=14`, `K_RING_RESONANCE=10`,
`K_DIFFUSE_LATE_DISK=6`, `K_COMPACT_EARLY_DISK=5`, and
`K_UNFREEZABLE_IDENTITY_ONLY=1`. These are source-side family candidates, not
fit outcomes.

The first homogeneous-S4G pilot holdout manifest then selects an
endpoint-blind, family-balanced pilot subset from the 43 homogeneous S4G P0
objects only. It freezes 7 `PILOT_HOLDOUT` objects, leaves 36 homogeneous S4G
objects in the `PILOT_TRAIN_POOL`, and marks 23 non-homogeneous source-tier
objects as outside the first homogeneous-S4G pilot. The split is calibration
aware: it leaves at least one train object in each selected homogeneous family
instead of exhausting small families into holdout. This is a scoring-prep ledger
only; it is not an endpoint result.

The first endpoint-readiness pass checks those 7 holdout objects against the
local SPARC preflight files. All 7 have available SPARC mass-model/rotation
rows, with 215 total local rotation points. The committed readiness manifest
records only availability and coarse radial/count metadata; the actual
endpoint curve packet is written under `data/external/` and remains
gitignored. No endpoint score or baseline comparison is run.

## Does Not Claim

- It does not prove Tau Core.
- It does not detect dark matter residuals in nature.
- It does not reject dark matter, GR, QED, MOND, or LCDM.
- It does not derive photons, special relativity, or gravity from bare Tau
  principles.
- It does not provide observational evidence.
- It is not a validated physical theory.

## Source-Transport Boundary

The null/time split does not derive a non-scalar photon transport. Scalar
phase or clock holonomy may survive, but a full photon/polarization transport
requires either an independently sourced full body connection or Kato
transport of a varying, constant-rank, source-owned access projector. A TCDR
score therefore remains a terminal association and cannot reconstruct the
missing parent arrows or connection.

## Included Data

Only compact synthetic derived artifacts are included:

```text
data/derived/tcdr_summary.csv
data/derived/tcdr_summary.json
data/derived/tcdr_v3_example_data.csv
data/derived/tcdr_multiseed_robustness.csv
data/derived/tcdr_multiseed_robustness_summary.csv
data/derived/tcdr_threshold_sensitivity.csv
data/derived/tcdr_blind_challenge_results.csv
data/derived/tcdr_blind_challenge_summary.csv
data/derived/tcdr_realistic_mock_challenge_results.csv
data/derived/tcdr_realistic_mock_challenge_summary.csv
data/derived/tcdr_realistic_mock_threshold_curve.csv
data/source_manifests/tcdr_v4_real_data_source_manifest_v0_1.csv
data/source_manifests/tcdr_v4_sparc_source_freeze_queue_v0_1.csv
data/source_manifests/tcdr_v4_sparc_source_freeze_queue_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_s4g_lookup_v0_1.csv
data/source_manifests/tcdr_v4_p0_s4g_lookup_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_s4g_coordinate_lookup_v0_1.csv
data/source_manifests/tcdr_v4_p0_s4g_coordinate_lookup_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_simbad_fallback_lookup_v0_1.csv
data/source_manifests/tcdr_v4_p0_simbad_fallback_lookup_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_source_tier_manifest_v0_1.csv
data/source_manifests/tcdr_v4_p0_source_tier_manifest_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_source_family_freeze_v0_1.csv
data/source_manifests/tcdr_v4_p0_source_family_freeze_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_pilot_holdout_manifest_v0_1.csv
data/source_manifests/tcdr_v4_p0_pilot_holdout_manifest_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_source_native_kernel_coordinate_audit_v0_1.csv
data/source_manifests/tcdr_v4_p0_source_native_kernel_coordinate_audit_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_bar_ring_decomposition_source_route_v0_1.csv
data/source_manifests/tcdr_v4_p0_bar_ring_decomposition_source_route_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_source_native_kernel_coordinate_freeze_v0_1.csv
data/source_manifests/tcdr_v4_p0_source_native_kernel_coordinate_freeze_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_source_native_component_mixture_audit_v0_1.csv
data/source_manifests/tcdr_v4_p0_source_native_component_mixture_audit_summary_v0_1.json
data/source_manifests/tcdr_v4_p0_holdout_endpoint_readiness_v0_1.csv
data/source_manifests/tcdr_v4_p0_holdout_endpoint_readiness_summary_v0_1.json
figures/*.png
source_package_docs/
source_package_figures/
code/toy_simulation_source.py
```

No real endpoint curve packets, lensing maps, cosmology survey products, or
population-validation datasets are included. The committed source manifests do
include compact source-side catalogue metadata needed to reproduce the
endpoint-blind morphology and kernel-coordinate ledgers.

## Full-4D Score Boundary

The TCDR kernels do not reconstruct the source-side standard excess
`E_K = (K_HH - K_std) - C K_VV^-1 C^dagger`. Their current scores remain
diagnostic and non-validating; a later physical score requires one common
coframe excess and the full covariance of its nonduplicated terminal images.

## Reproduce

```bash
python scripts/reproduce.py
```

The command:

1. regenerates the TCDR synthetic toy outputs;
2. runs the multi-seed robustness replay and threshold sensitivity sweep;
3. runs the blind synthetic injection challenge with wrong-seed controls;
4. runs the realistic-mock nuisance challenge with threshold-free diagnostics;
5. regenerates the TCDR-v4 real-data source manifest;
6. regenerates the endpoint-blind P0 pilot holdout manifest from the committed
   source-family freeze artifact;
7. regenerates the source-native kernel-coordinate audit, S4G bar/ring
   decomposition source-route artifact, endpoint-blind coordinate-freeze
   manifest, source-native component-mixture audit, and source-native
   mixed-component kernel freezes, shuffled-component null controls, and the
   v0.4 source-frozen formula-compiler readiness manifest;
8. copies figures into the paper source tree;
9. compiles `paper19_submission_source/main.tex`;
10. builds `arxiv_submission_source.zip`;
11. runs public package tests;
12. prints `PAPER19_PHOTON_C_DARK_RESIDUAL_REPRODUCTION_COMPLETE`.

## Optional Real-Data Preflight

The repository does not commit real survey data. To begin a local TCDR-v4
endpoint preflight, download compact SPARC endpoint/baseline files into the
gitignored `data/external/` area:

```bash
python scripts/download_tcdr_v4_sparc_endpoint.py --out-dir data/external/sparc_preflight
```

This downloads `Rotmod_LTG.zip`, `MassModels_Lelli2016c.mrt`, and
`SPARC_Lelli2016c.mrt`, plus a local checksum manifest. These files are
endpoint/baseline inputs only. They must not be used to choose or rescue
source-side morphology labels.

After the SPARC sample table is available locally, build the endpoint-free
source-review queue:

```bash
python scripts/build_tcdr_v4_sparc_source_freeze_queue.py
```

This generates a candidate list for later S4G/Galaxy Zoo source-side morphology
lookup. It does not read SPARC rotation residuals or run endpoint scoring.

Then run the P0 S4G source-side lookup:

```bash
python scripts/build_tcdr_v4_p0_s4g_lookup.py
```

This uses IRSA TAP table `s4gcat` and records only source-side morphology
columns such as type, bar/ring flags, position angle, ellipticity,
concentration, and stellar-mass proxy fields.

For P0 objects not found by name, run the coordinate resolver pass:

```bash
python scripts/build_tcdr_v4_p0_s4g_coordinate_lookup.py
```

This uses SIMBAD name resolution and a 1 arcmin S4G coordinate match. It is
still source-side morphology acquisition only and must not be used as endpoint
scoring.

Finally, build the SIMBAD fallback manifest for the remaining non-S4G P0
objects:

```bash
python scripts/build_tcdr_v4_p0_simbad_fallback_lookup.py
```

This records SIMBAD identity, object type, morphology type, morphology
bibcode, and aliases for non-S4G source review. It is intentionally a fallback
source ledger, not an endpoint or validation input.

Build the combined P0 source-tier manifest:

```bash
python scripts/build_tcdr_v4_p0_source_tier_manifest.py
```

This combines the name, coordinate, and SIMBAD fallback ledgers into a frozen
source-tier hierarchy. It still does not inspect rotation endpoints.

Build the endpoint-blind source-family freeze:

```bash
python scripts/build_tcdr_v4_p0_source_family_freeze.py
```

This assigns candidate morphology/readout families from source-side morphology
fields only. The output is not a score table and must not be interpreted as
showing which family fits a galaxy.

Build the first homogeneous-S4G pilot holdout manifest:

```bash
python scripts/build_tcdr_v4_p0_pilot_holdout_manifest.py
```

This reads the source-family freeze artifact and deterministically selects up
to two homogeneous S4G objects per available source family, preferring objects
without projection caveats and then sorting by galaxy name while leaving at
least one train object in each selected homogeneous family. It produces a
source-side holdout/train-pool ledger for later endpoint work. It does not read
rotation residuals, fit amplitudes, or score baselines.

Build the source-native kernel-coordinate audit:

```bash
python scripts/build_tcdr_v4_p0_source_native_kernel_coordinate_audit.py
```

This committed source-side audit records which P0 family labels are only
binary/proxy morphology labels and which source-native coordinates are still
needed before the kernels can be promoted. The current summary is: 30 barred
objects need bar decomposition, 10 ring/resonance objects need ring
decomposition, 14 exponential disks have partial disk/H I proxy coordinates,
6 diffuse late disks are underpowered for train support, 5 compact early disks
are outside the first homogeneous-S4G pilot, and 1 identity-only case is not
kernel-freeze ready. It does not read rotation residuals or endpoint scores.

Prepare the local endpoint-readiness packet for the 7 holdout objects:

```bash
python scripts/build_tcdr_v4_p0_holdout_endpoint_packet.py
```

This requires the optional SPARC files in `data/external/sparc_preflight/`.
It writes a committed readiness manifest without `Vobs`, `Vflat`, residual, or
score fields, and writes the actual local endpoint curve packet only under
`data/external/`, which is ignored by git. The carrier is frozen as
`fixed_baryonic_mlr_disk_0p5_bulge_0p7_no_amplitude_fit`; this is a preflight
carrier policy, not an endpoint fit.

Run the first local holdout endpoint-scoring preflight:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring.py
```

This command uses only the frozen pilot split and the local SPARC endpoint
packet under `data/external/`. Family amplitudes are fit on the
`PILOT_TRAIN_POOL` only, then evaluated on the `PILOT_HOLDOUT` objects against
calibrated wrong-family controls. Families with fewer than two train galaxies
are marked calibration-blocked and are not allowed to act as endpoint controls.
The current local kernel pass uses
`train_pool_only_specificity_first_v4_penalty_1p5_no_holdout_shape_tuning`,
meaning the radial kernel shapes were selected from train-pool specificity
criteria rather than holdout performance. In the author-local diagnostic run,
6 holdout galaxies are scoreable and 1 is calibration-blocked; the matched
family beats the frozen baryonic carrier in 6/6 scoreable cases, beats the
calibrated wrong-family mean in 3/6, and beats the best calibrated wrong family
in 2/6. The outputs stay local under `data/external/` and are not part of the
public release. This is diagnostic scoring, not population validation or a
physical dark-residual claim.

Diagnose why the current source-family kernels do or do not separate matched
families from calibrated wrong-family controls:

```bash
python scripts/diagnose_tcdr_v4_kernel_specificity.py
```

This writes local-only diagnosis files under `data/external/`. It reports the
matched-family rank, the best calibrated wrong family, and the next
source-native coordinate needed for each holdout family. It is a kernel
development aid, not an endpoint score or validation artifact. In the current
author-local run, the calibrated wrong-family winners are all
`K_EXPONENTIAL_SPIRAL_DISK` against barred or ring/resonance holdout objects,
which points to missing source-native bar/ring coordinates rather than an
amplitude-tuning target.

Build the machine-readable S4G bar/ring decomposition source route:

```bash
python scripts/build_tcdr_v4_p0_bar_ring_decomposition_source_route.py
```

This uses VizieR catalogues `J/ApJS/219/4` and `J/A+A/582/A86` to check
whether P0 galaxies already have source-native Pipeline 4 bar-decomposition
rows, bar/ring feature sizes, or spiral pitch-angle segments. The current
committed route summary finds 31 P0 objects with Pipeline 4 rows, 21 with
feature-catalogue rows, and 16 with spiral-segment rows. Within the frozen
family labels, 12 barred objects already have source-native bar features, 4
ring/resonance objects have source-native ring features, and 2 exponential
spiral disks have source-native spiral pitch information. The remaining
barred/ring objects are still source-proxy cases requiring additional
decomposition review. This route artifact is endpoint-blind and must not be
read as kernel validation.

Build the endpoint-blind source-native kernel-coordinate freeze:

```bash
python scripts/build_tcdr_v4_p0_source_native_kernel_coordinate_freeze.py
```

This converts covered S4G bar/ring angular coordinates to physical source
coordinates using source-side SPARC sample distances and disk scales, without
reading rotation curves or endpoint residuals. The frozen v0.1 rule sets the
bar kernel center to the S4G bar radius when available, sets the ring kernel
center to the S4G ring radius when available, records spiral pitch information
without using it to tune endpoint curves, and leaves uncovered objects on the
proxy fallback. The current freeze records 12 `source_native_bar_radius_frozen`
objects, 4 `source_native_ring_radius_frozen` objects, 2
`source_native_spiral_pitch_recorded_disk_proxy_center` objects, and 48
`source_proxy_kernel_fallback` objects.

Run the optional source-native coordinate local scoring replay:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring_source_native_coordinates.py
```

This is a local endpoint diagnostic only. In the current author-local replay,
the source-native coordinate rule improves the median matched-minus-baryonic
carrier margin from `-0.392` to `-0.682 km/s`, but the matched family still
beats the calibrated wrong-family mean in only 3/6 scoreable cases and the
best calibrated wrong family in 2/6. The scientific interpretation is not
validation; it is that source-native coordinates improve several matched
objects, while mixed/multi-component galaxies can also activate wrong-family
controls unless the next rule separates mixed components source-side.

Build the source-native component-mixture audit:

```bash
python scripts/build_tcdr_v4_p0_source_native_component_mixture_audit.py
```

This endpoint-blind manifest records whether source-native bar, ring, and
spiral-pitch components coexist in the same P0 galaxy. The current audit finds
17 `mixed_source_native_multicomponent` objects, 42 objects with no
source-native bar/ring/spiral component in the current S4G route, 4 single
primary-component objects, and 3 single secondary-component-only objects. In
the 7-object holdout, 3 galaxies are mixed: NGC1090 (`bar;ring;spiral`),
NGC5033 (`ring;spiral`), and NGC3198 (`bar;ring;spiral`). This explains why a
calibrated wrong-family control can sometimes be a physically meaningful
component control rather than a pure false label. It does not promote any
endpoint validation claim.

Freeze the endpoint-blind mixed-component kernel weights:

```bash
python scripts/build_tcdr_v4_p0_source_native_mixed_component_kernel_freeze.py
```

This source-side artifact turns the component-mixture audit into an auditable
kernel rule before endpoint scoring. The current freeze contains 17
`mixed_source_native_component_kernel` rows, 7
`single_source_native_component_kernel` rows, and 42
`fallback_family_proxy_kernel` rows. Its rule gives a primary component weight
of `0.5` and lets source-visible secondary components share the remaining
`0.5` in multicomponent cases; single-component cases get weight `1.0`, and
uncovered objects remain family-proxy fallbacks. This is a kernel-freeze
artifact, not endpoint validation.

Build the endpoint-blind shuffled-component null controls:

```bash
python scripts/build_tcdr_v4_p0_source_native_shuffled_component_nulls.py
```

This manifest creates 64 deterministic source-side shuffles.  It preserves the
component-weight distribution within each pilot role while breaking the
galaxy-to-component assignment before endpoint scoring.  The artifact has 4224
rows and uses seed `19019`.  It is a null-control freeze, not a scoring result.

Run the optional mixed-component local scoring replay:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring_mixed_components.py
```

This local diagnostic fits one source-frozen `K_SOURCE_NATIVE_MIXED_COMPONENT`
amplitude on the pilot train pool and evaluates it on the holdout. The current
author-local replay beats the baryonic carrier in 6/6 scoreable cases and
beats the pure matched family in 4/6, but it still beats the calibrated
wrong-family mean in only 3/6 and the best wrong family in 2/6. Among the
three mixed holdout objects, the mixed model beats the pure matched model in
2/3 and the wrong-family mean in 1/3. This is not an endpoint validation
claim; it shows that source-side mixed components are useful but not yet
sufficiently selective.

Run the optional shuffled-component local scoring replay:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring_shuffled_mixed_components.py
```

This local diagnostic compares the source-frozen mixed kernel against the 64
endpoint-blind shuffled component assignments.  In the current author-local
run, the actual mixed kernel has median weighted RMSE `60.103 km/s`, while the
median shuffled-null median is `60.371 km/s`; however, 25/64 shuffled nulls
(`0.390625`) have median RMSE less than or equal to the actual mixed kernel.
This is a caveated/weak selectivity result: the mixed rule is useful, but the
present component weighting is not yet strong enough for endpoint promotion.

Build the source-strength-weighted mixed-component kernel freeze:

```bash
python scripts/build_tcdr_v4_p0_source_native_strength_weighted_mixed_kernel_freeze.py
```

This v0.2 source-side rule replaces the fixed primary/secondary split with
component-evidence weights. Bar and ring use the frozen source strength
proxies; spiral uses pitch, segment count, and radial span from the S4G/VizieR
route artifact. It produces the same coverage classes as v0.1: 17 mixed
kernels, 7 single-component kernels, and 42 family-proxy fallbacks. It is a
source-side refinement, not endpoint tuning.

Build and run the matching v0.2 shuffled null diagnostic:

```bash
python scripts/build_tcdr_v4_p0_source_native_strength_weighted_shuffled_component_nulls.py
python scripts/run_tcdr_v4_holdout_endpoint_scoring_strength_weighted_mixed_components.py
python scripts/run_tcdr_v4_holdout_endpoint_scoring_strength_weighted_shuffled_mixed_components.py
```

The current author-local v0.2 replay improves the wrong-family mean beat count
from `3/6` to `4/6`, and among mixed holdout objects from `1/3` to `2/3`. The
actual v0.2 mixed median weighted RMSE is `59.746 km/s`, while the median
shuffled-null median is `60.319 km/s`; however, `22/64` shuffled nulls
(`0.34375`) remain at least as good. This is directionally stronger than v0.1,
but still a caveated selectivity diagnostic, not endpoint promotion.

Build and run the v0.3 radial/source-geometry stress refinement:

```bash
python scripts/build_tcdr_v4_p0_source_native_radial_geometry_mixed_kernel_freeze.py
python scripts/build_tcdr_v4_p0_source_native_radial_geometry_shuffled_component_nulls.py
python scripts/run_tcdr_v4_holdout_endpoint_scoring_radial_geometry_mixed_components.py
python scripts/run_tcdr_v4_holdout_endpoint_scoring_radial_geometry_shuffled_mixed_components.py
```

The v0.3 rule multiplies source evidence by endpoint-blind radial-zone,
primary-family hierarchy, and conservative projection-reliability factors. It
keeps the same coverage classes as v0.2. In the current author-local replay it
does not improve on v0.2: it keeps the wrong-family mean beat count at `4/6`
and mixed-holdout wrong-mean count at `2/3`, but the actual mixed median
weighted RMSE weakens to `59.933 km/s` and the median wrong-mean margin shrinks
to `0.120 km/s`. The shuffled-null fraction remains `22/64` (`0.34375`). This
is useful as a source-side stress test, not as the preferred endpoint kernel.

The next route is therefore not another hand-selected family template. Paper
19 now returns to the Paper 8/Paper 9/common source-frozen readout formula
ladder:

```text
source-native observables
  -> source load and support window
  -> dimensionally checked component formula
  -> zero-source / known-limit guard
  -> predeclared mixed composition rule
  -> endpoint replay and shuffled-component controls
```

See:

```text
source_package_docs/tcdr_v4_source_frozen_formula_ladder_import.md
```

This records the next TCDR-v4 v0.4 target as a source-frozen formula compiler,
not a new curve-selected or family-template kernel.

Build the v0.4 formula-compiler readiness manifest:

```bash
python scripts/build_tcdr_v4_p0_source_frozen_formula_compiler_readiness.py
```

This is still endpoint-blind. It classifies the 66 P0 objects into formula
replay readiness states using only residual-blind source observables. The
current ledger contains 30 `READY_FORMULA_COMPILER_REPLAY_CANDIDATE` objects,
16 `PARTIAL_FORMULA_COMPILER_CANDIDATE` objects, 19 template-only fallbacks,
and 1 unfreezable identity-only source. In the 7-object holdout, 5 objects are
formula-ready (`NGC1090`, `NGC2841`, `NGC3198`, `NGC5033`, `NGC6503`), while
`UGC08490` remains diffuse-partial and `ESO116-G012` remains template-only.

If the local SPARC preflight files are present under `data/external/`, the
formula-ready subset can be scored with:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready.py
```

This local preflight replay scores only the five readiness-filtered holdout
objects. In the current author-local run, the formula-ready mixed rule beats
the fixed baryonic carrier in `5/5`, the wrong-family mean in `4/5`, and the
best wrong-family control in `2/5`; the median wrong-mean margin is
`0.576 km/s`. This is a scoring-direction signal for the source-frozen formula
compiler route, not population validation.

After the NGC2841 stress case, the cleanest single-object follow-up is NGC6503.
Its source-frozen candidate is the exponential-disk scale-tail formula, with no
source-native bar/ring/spiral mixture active. The focused replay can be run
with:

```bash
python scripts/run_tcdr_v4_ngc6503_clean_scale_tail_endpoint_replay.py
```

The current local result is a clean preliminary positive: the candidate
weighted RMSE is `58.074 km/s`, versus `58.672 km/s` for the fixed baryonic
carrier, `58.182 km/s` for the pure matched exponential control, `59.208 km/s`
for the wrong-family mean, and `58.661 km/s` for the best wrong-family control.
This is useful because the improvement comes from the predeclared source-frozen
scale-tail route, not from an NGC6503-specific kernel search or target-galaxy
amplitude retuning.

NGC7793 provides a second focused support-safe spiral/scale-tail case:

```bash
python scripts/run_tcdr_v4_ngc7793_support_safe_spiral_endpoint_replay.py
```

Here the support-safe candidate weighted RMSE is `19.543 km/s`, versus
`23.991 km/s` for the fixed baryonic carrier, `23.653 km/s` for the
wrong-component mean, and `23.331 km/s` for the best wrong-component control.
It does not beat the matched spiral component control by itself
(`19.532 km/s`), so it is not an overclaim. It is nevertheless a useful
preliminary positive because the source-frozen spiral/scale-tail route beats
the wrong-family controls with leave-one-galaxy-out amplitude freeze.

Run the corresponding readiness-filtered shuffled-component null:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready_shuffled.py
```

This keeps the same five formula-ready holdout objects but replaces the
source-frozen component packages by endpoint-blind shuffled component packages.
In the current author-local run, the actual formula-ready median weighted RMSE
is `60.471 km/s`, the median shuffled-null median is `60.483 km/s`, and
`25/64` shuffled nulls are at least as good as the actual formula-ready kernel.
Thus the formula-ready route is directionally useful, but it is not yet
source-selective enough for endpoint promotion.

Run the formula-ready component-ablation diagnostic:

```bash
python scripts/run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready_component_ablation.py
```

This keeps the same five formula-ready holdout objects and the same
train-pool-only amplitude policy, but compares the full source-frozen
bar/ring/spiral mix against `bar_only`, `ring_only`, `spiral_only`, and
leave-one-component-out variants. Ablation variants do not fall back to a
family proxy when a component is absent. In the current author-local run, the
full source mix has median weighted RMSE `60.456 km/s`, while the best ablation
median is `60.340 km/s` for `spiral_only`; by object, the best variant is
`spiral_only` for 2 galaxies, `ring_only` for 2 galaxies, and the full mix for
1 galaxy. This explains why shuffled component packages remain competitive:
the present source-frozen composition is not yet uniquely selected by the
available source observables. The result is a component-specificity diagnostic,
not a validation or kernel-promotion result.

Build the endpoint-blind source-composition uniqueness audit:

```bash
python scripts/build_tcdr_v4_p0_source_composition_uniqueness_audit.py
```

This v0.5 audit uses only the frozen source-side component weights and tags
each object as source-composition unique, weakly unique, ambiguous, or
component-uncovered. In the current ledger, the 66 P0 objects split into 17
unique, 1 weakly unique, 6 ambiguous, and 42 with no source-native
bar/ring/spiral component. Among the five formula-ready holdout galaxies, 3
are source-composition unique, 1 is ambiguous, and 1 has no source-native
component coverage. This is the source-side explanation of the ablation result:
formula readiness alone does not imply component-composition uniqueness.

If the local ablation output is present under `data/external/`, the diagnostic
alignment check can be run with:

```bash
python scripts/run_tcdr_v4_formula_ready_source_composition_vs_ablation_diagnostic.py
```

This check is explicitly post-source-freeze and endpoint-diagnostic only. In
the current author-local run, the endpoint-blind top source component agrees
with the local ablation winner in only `1/4` positive-source-component holdout
galaxies (`1/3` among strongly unique source cases). Therefore the next
kernel-development blocker is not amplitude fitting, but a better
source-native rule for mapping source morphology to the readout-active
component.

Build the support-aware selector audit:

```bash
python scripts/build_tcdr_v4_p0_support_aware_component_selector_audit.py
```

This v0.6 audit keeps the v0.5 source weights frozen but demotes apparent
dominant components when their source radial supports overlap or are adjacent.
It is still endpoint-blind. Across the 66 P0 objects, only 10 remain
support-aware selector-safe, while 14 are unresolved by overlapping/adjacent
support and 42 are uncovered. Among the five formula-ready holdout galaxies,
only `NGC2841` is selector-safe; `NGC1090`, `NGC3198`, and `NGC5033` are
unresolved by support overlap/adjacency, and `NGC6503` is uncovered. This
explains why the source selector should not be promoted yet: formula readiness
does not imply support-safe component selection.

Build the support-safe expansion manifest:

```bash
python scripts/build_tcdr_v4_p0_support_safe_expansion_manifest.py
```

This v0.7 manifest uses only the endpoint-blind v0.6 selector-safety ledger.
It declares a future replay pool only for objects that are both formula-ready
and support-safe. The resulting support-safe replay pool has 7 galaxies:
`NGC0024`, `NGC2841`, `NGC5005`, `NGC7793`, `UGC04499`, `UGC06917`, and
`UGC06983`. Of these, `NGC2841` is the existing support-safe holdout object,
while the other 6 are expansion candidates from the train pool. This is a
source-side eligibility manifest, not endpoint scoring.

Build the support-safe expansion opportunity ledger:

```bash
python scripts/build_tcdr_v4_p0_support_safe_expansion_opportunity_ledger.py
```

This v0.8 ledger answers whether the pool can be enlarged further without
using endpoint information. It separates the 66 P0 objects into tiers:
7 are replay-eligible now; 3 more are support-safe but need source-frozen
formula completion (`NGC3893`, `UGC00191`, `UGC12732`); 12 are formula-ready
but need overlapping-support review; 11 are formula-ready but need a disk or
other component-source rule; and 33 are not near-term expansion-ready. Thus
the clean near-term path is 7 now, 10 after bounded formula completion, and
larger expansion only after independent source-support work.

Build the support-safe formula-completion manifest:

```bash
python scripts/build_tcdr_v4_p0_support_safe_formula_completion_manifest.py
```

This v0.9 manifest closes the bounded 7 -> 10 step without endpoint fields. It
admits the three Tier1 objects by using their source-dominant support-safe
component route instead of forcing the broad family label: `NGC3893` enters
through a spiral component route, while `UGC00191` and `UGC12732` enter through
bar component routes. The resulting 10-object source-side replay pool is:
`NGC0024`, `NGC2841`, `NGC3893`, `NGC5005`, `NGC7793`, `UGC00191`,
`UGC04499`, `UGC06917`, `UGC06983`, and `UGC12732`. This is formula-completion
eligibility, not endpoint scoring.

Run the local support-safe pool LOOCV endpoint diagnostic:

```bash
python scripts/run_tcdr_v4_support_safe_pool_loocv_scoring.py
```

This optional local script writes only under `data/external/sparc_preflight/`
because it uses SPARC endpoint curves after the source pools are frozen. It
scores the 7-object v0.7 pool and the 10-object v0.9 pool with leave-one-galaxy
out amplitude calibration. In the current local run, the 7-object pool beats
the baryonic carrier in `6/7`, the matched-component control in `5/7`, the
wrong-component mean in `2/7`, and the best wrong component in `1/7`. The
10-object pool beats the baryonic carrier in `9/10`, the matched-component
control in `5/10`, the wrong-component mean in `5/10`, and the best wrong
component in `3/10`. The 10-object expansion is directionally better, but it is
still a local diagnostic rather than endpoint validation because strict
wrong-component controls remain competitive.

Build the support-safe failure ledger and run the formula-aware LOOCV replay:

```bash
python scripts/run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring.py
```

This optional local script writes only under `data/external/sparc_preflight/`.
It first explains which component wins when the candidate fails the strict
best-wrong control. In the current ledger, 4/17 rows survive the strict
best-wrong control, 4/17 are cases where the best wrong component is actually a
source-visible secondary component, 2/17 are broad-disk-family/top-component
mismatches, and 7/17 remain unexplained competitive false-component cases.

The second half reruns LOOCV with the candidate using the frozen
`support_safe_compiled_formula` rather than the top component alone. This
formula-aware replay improves the 10-object pool to `10/10` against the
baryonic carrier and `6/10` against the wrong-component mean, but it reaches
only `2/10` against the best wrong component. Thus the compiled formula route
is better aligned with the manifest, but it does not close the strict
wrong-component blocker.

Apply the Paper8/Paper9 failure-overlay diagnostic:

```bash
python scripts/build_tcdr_v4_paper8_paper9_failure_overlay.py
```

This optional local diagnostic does not select a new kernel. It re-reads the
strict-control failures through the Paper8/Paper9 distinction between visible
source morphology (`K_obs`) and readout-active kernel (`K_readout`), plus the
Paper9 non-overlap rule for projection/history routes. In the current local
overlay, 3/17 rows are strict-control survivals, 3/17 are near ties within
`0.1 km/s`, 4/17 are source-visible secondary-component cases, 2/17 are
broad-disk `K_obs`/`K_readout` mismatch candidates, and 5/17 remain blocked
until independent spiral/projection/history source evidence exists. This is a
failure taxonomy and route-permission ledger only, not endpoint validation and
not a post-hoc family rescue.

Build the scoring-readiness ledger and run the readiness-filtered local score:

```bash
python scripts/build_tcdr_v4_paper8_paper9_scoring_readiness_ledger.py
python scripts/run_tcdr_v4_paper8_paper9_readiness_filtered_scoring.py
python scripts/run_tcdr_v4_readiness_filtered_metric_robustness.py
python scripts/build_tcdr_v4_readiness_filtered_metric_robustness_figure.py
```

The readiness ledger permits immediate replay only for current-formula strict
survivals and near ties. Mixed, `K_obs`/`K_readout`, and projection/history
routes remain blocked until source-side conditions close. In the current local
readiness-filtered scoring run, the six allowed rows cover four unique
galaxies (`NGC2841`, `NGC3893`, `NGC7793`, `UGC00191`) and beat the baryonic
carrier in `6/6`, the wrong-component mean in `6/6`, and the best wrong
component in `3/6`. The strict result remains limited because the three
near-tie rows are robustness rows, not strict wins.
The metric-robustness audit repeats the allowed-row comparison under both
weighted RMSE and unweighted RMSE. Strict best-wrong survival remains `3/6`
under both metrics, but wrong-component-mean survival falls from `6/6`
weighted to `4/6` unweighted. This preserves the positive sub-ledger while
keeping it diagnostic rather than validation-grade. The companion figure is
written to `figures/tcdr_readiness_filtered_metric_robustness.png`.

Test the mixed-route opening against shuffled formula-package controls:

```bash
python scripts/run_tcdr_v4_support_safe_mixed_route_shuffle_control.py
python scripts/build_tcdr_v4_kobs_kreadout_source_review.py
python scripts/build_tcdr_v4_paper8_paper9_scoring_route_closure.py
python scripts/build_tcdr_v4_source_gap_blocker_ledger.py
```

The source non-overlap condition closes for the four mixed-route rows, but the
shuffled formula-package control does not pass: `0/4` mixed rows beat the
shuffle criterion at the predeclared `p <= 0.10` threshold. The final route
closure therefore leaves only the six current-formula rows replay-ready and
keeps `11/17` rows blocked or review-required. This is a useful negative
control: source-visible secondary components are not automatically promoted to
new endpoint kernels. The separate `K_obs`/`K_readout` source review closes
the two NGC0024 broad-disk mismatch rows in the negative direction: the broad
family label contains disk/spiral structure, but the frozen source ledger has
bar/ring support, zero spiral component weight, and no source-native spiral
geometry. The final route closure therefore marks those rows as
`KOBS_KREADOUT_RELABEL_BLOCKED_BY_SOURCE_REVIEW`, not as replay-ready.
The source-gap blocker ledger then inspects the remaining five blocked rows
(`UGC04499`, `UGC06917`, and `UGC12732` across the two support-safe pools).
All five are competitive spiral controls outside the frozen source family and
lack independent source-side spiral support, so they remain source-acquisition
tasks rather than replay candidates.

The bounded external literature/source audit keeps the same rows blocked:

```bash
python scripts/build_tcdr_v4_source_gap_external_literature_audit.py
python scripts/build_tcdr_v4_post_external_route_closure.py
python scripts/build_tcdr_v4_post_external_scoring_boundary_summary.py
python scripts/build_tcdr_v4_allowed_best_wrong_failure_diagnostic.py
python scripts/build_tcdr_v4_allowed_failure_source_acquisition_worklist.py
python scripts/build_tcdr_v4_allowed_failure_external_source_review.py
python scripts/build_tcdr_v4_allowed_failure_formula_freeze_readiness.py
python scripts/build_tcdr_v4_allowed_failure_numeric_observable_worklist.py
python scripts/build_tcdr_v4_allowed_failure_numeric_source_freeze.py
python scripts/build_tcdr_v4_allowed_failure_spiral_path_formula_freeze.py
python scripts/build_tcdr_v4_allowed_failure_scoring_preflight.py
python scripts/run_tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring.py
python scripts/build_tcdr_v4_ngc2841_absolute_residual_gap_diagnostic.py
python scripts/build_tcdr_v4_ngc2841_outer_capacity_requirement_audit.py
python scripts/build_tcdr_v4_post_external_scoring_boundary_figure.py
```

`UGC04499` gains anti-spiral support from an external late-type/bulgeless
source, `UGC06917` remains bar-only under the available source ledger, and
`UGC12732` has weak non-bar caveats without source-native spiral geometry or an
independent projection/history token. The audit writes
`data/external/sparc_preflight/tcdr_v4_source_gap_external_literature_audit_local.csv`
and does not promote any new replay route. The post-external route closure then
records the final scoring permission state: six current-formula rows remain
replay-ready, while eleven rows remain blocked or review-required. The
post-external scoring-boundary summary then scores only those six allowed rows:
weighted RMSE gives 6/6 versus baryonic, 6/6 versus wrong-component mean, and
3/6 versus strict best-wrong; unweighted RMSE gives 4/6 versus wrong-component
mean and 3/6 versus strict best-wrong. Blocked rows carry no scoring claim.
The companion paper figure is generated from the frozen summary artifact at
`figures/tcdr_post_external_scoring_boundary.png`.
The allowed-row best-wrong failure diagnostic then checks whether the three
strict best-wrong failures can be honestly promoted into source-visible mixed
routes. It finds `0/3` source-visible best-wrong secondary components, so those
rows remain near-tie or metric-sensitive control-pressure diagnostics rather
than new mixed-kernel replay candidates.
The follow-up source-acquisition worklist converts those failures into explicit
residual-blind source requests: three row-level spiral/path/history requests
across `NGC2841` and `UGC00191`, with endpoint replay and kernel promotion both
kept at `no`.
The bounded external source review then checks those requests without reading
endpoint residuals. It finds caveated independent spiral/path evidence for
`NGC2841` and only weak asymmetry support, not route-closing spiral geometry,
for `UGC00191`. The artifact
`data/external/sparc_preflight/tcdr_v4_allowed_failure_external_source_review_local.csv`
keeps endpoint replay and kernel promotion at `no` for both galaxies; it only
authorizes future source-side route review.
The follow-up formula-freeze readiness artifact then asks whether that source
review is already enough to freeze a new score-bearing formula. It is not:
`NGC2841` is review-open but blocked by missing numeric source-native
spiral/path observables, while `UGC00191` remains weak/asymmetry-only and not a
spiral/path formula candidate. The artifact
`data/external/sparc_preflight/tcdr_v4_allowed_failure_formula_freeze_readiness_local.csv`
keeps endpoint replay, kernel promotion, and new-route scoring at `no` for both
objects.
The final numeric-observable worklist turns that blocker into concrete
source-acquisition targets: four NGC2841 spiral/path observables
(`spiral_inner_kpc_source`, `spiral_outer_kpc_source`,
`spiral_pitch_median_abs_deg_source`, and
`warp_onset_or_path_environment_numeric_source`) plus one UGC00191
route-closing prerequisite. This remains a source-only worklist, not formula
freeze, endpoint replay, or scoring permission.
The bounded numeric source-freeze pass then closes the NGC2841 side of that
blocker with caveats: Kendall et al. provide a spiral break at `0.45 R25`, a
quoted `R25 = 4.05 arcmin`, and an outer pitch-angle estimate of about `7 deg`;
using the already frozen `14.1 Mpc` distance gives `spiral_inner_kpc_source =
7.475`, `spiral_outer_kpc_source = 16.611`, and
`spiral_pitch_median_abs_deg_source = 7.0`. Zhang et al. provide the
outer-warp/path coordinate, frozen here as
`warp_onset_or_path_environment_numeric_source = 30.0 kpc`. These are
source coordinates only, with high-inclination/flocculent caveats.
The scoring preflight then checks those requested observables against the local
source manifests.  The new source-frozen formula artifact
`data/source_manifests/tcdr_v4_allowed_failure_spiral_path_formula_freeze_v0_1.csv`
then freezes the caveated NGC2841 shell
`F_CAVEATED_SPIRAL_PATH_WINDOW_SOURCE_FROZEN`:

```text
K_sp(r)   = 0.5 [tanh((r-r_in)/sigma_edge) - tanh((r-r_out)/sigma_edge)]
K_path(r) = 1 / (1 + exp(-(r-r_path)/sigma_path))
K_total(r)= clip(K_sp(r) + epsilon_path K_path(r), 0, 1)
```

Here `r_in = 7.475 kpc`, `r_out = 16.611 kpc`, `r_path = 30.0 kpc`,
and `epsilon_path = min(0.20, max(0.02, pitch_rad))` with the source pitch
`7 deg`.  This is a source-side formula shell only: it does not fit an
amplitude, read endpoint residuals, or authorize replay.
The scoring preflight now finds `4/5` requested numeric/source route fields
filled and formula-frozen for NGC2841, while UGC00191 still lacks a
route-opening source field. The artifact
`data/external/sparc_preflight/tcdr_v4_allowed_failure_scoring_preflight_local.csv`
therefore keeps endpoint replay, kernel promotion, and new-route scoring at
`no`. This is the current scoring-facing boundary, not an endpoint score.
The bounded diagnostic replay can then be run explicitly:

```bash
python scripts/run_tcdr_v4_allowed_failure_spiral_path_diagnostic_scoring.py
```

This replay applies the source-frozen NGC2841 spiral/path formula shell to the
local SPARC curve while fitting only a spiral-control amplitude on the other
support-safe pool galaxies. In the current local run it improves the weighted
RMSE relative to the previous NGC2841 formula, the best wrong-component
control, and the baryonic carrier in both support-safe pools, with a median
improvement of `1.179 km/s` against the previous formula and `1.149 km/s`
against the best wrong control. This is a diagnostic score only:
`endpoint_validation_claimed = no`, `kernel_promotion_permission = no`.
The companion absolute-gap diagnostic,
`data/external/sparc_preflight/tcdr_v4_ngc2841_absolute_residual_gap_diagnostic_local.csv`,
records the cautionary part of the same result. The source-frozen spiral/path
shell remains far below the observed NGC2841 rotation curve in absolute terms:
the median predicted/observed velocity ratio is about `0.69` inside 10 kpc,
`0.60` from 10--30 kpc, and only `0.43` beyond 30 kpc. The outer missing
`v^2` fraction is about `0.81`. Therefore the replay is a directional
improvement, not a sufficient NGC2841 readout. The next source-side target is
an independent outer path or dark-residual capacity route, not endpoint
amplitude tuning.

The follow-up capacity-requirement audit,
`data/external/sparc_preflight/tcdr_v4_ngc2841_outer_capacity_requirement_audit_local.csv`,
asks a deliberately diagnostic question: how large would the path weight have
to be if the present spiral/path shell were forced to close the remaining
`v^2` gap without changing its source-frozen shape? The frozen cap is
`epsilon_path = 0.122`, while the required median outer-zone value is about
`26.3`, more than `200x` above the cap. This rules out endpoint amplitude rescue
for the current shell. It does not promote a new kernel; it identifies the
missing ingredient as a separate, independently sourced outer path or
dark-residual capacity route.

The source-side search for that missing route is recorded in
`data/source_manifests/tcdr_v4_ngc2841_outer_capacity_source_search_v0_1.csv`
and can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_outer_capacity_source_search.py
```

It does not use the rotation curve, endpoint residuals, RMSE values, or the
capacity requirement as formula input. It records three strong independent
source candidates for a future outer-capacity formula-freeze review: the
Dragonfly extended stellar/HI/UV disk route, the Bosma extended HI warp and
tilted-ring route, and the GALEX/XUV outer-disk star-formation route. Three
additional rows are retained only as caveated path-context evidence. Endpoint
replay and kernel promotion remain `no` for all rows; the artifact closes a
source-search blocker, not the NGC2841 kernel.

The next worklist,
`data/source_manifests/tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist_v0_1.csv`,
can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_outer_capacity_formula_freeze_worklist.py
```

It converts the source search into eight formula-freeze fields. Five fields
already have candidate numeric or lower-bound source values (`20 kpc`,
`30 kpc`, `70 kpc`, `2.5` Holmberg diameters, and `>=4 D25`), but the route is
not formula-ready. The remaining blockers are the source-side onset-priority
rule, the extraction of a source-native tilted-ring geometry profile, and a
residual-blind component-weight rule for combining the stellar/HI/UV, warped
HI, and XUV routes. The worklist keeps `formula_ready = false` and all scoring
permissions closed.

The bounded policy-freeze pass then closes two of those blockers without using
endpoint information:

```bash
python scripts/build_tcdr_v4_ngc2841_outer_capacity_policy_freeze.py
```

It freezes a nested onset rule (`20 kpc` for the general outer-capacity ramp,
`30 kpc` for the warp/path subchannel) and a maximum-entropy equal prior over
the three strong source routes (`1/3`, `1/3`, `1/3`) while assigning zero
primary formula weight to caveated context rows. It does not make the route
scoreable: exact XUV radial shape and source-native tilted-ring geometry remain
blocked, so `formula_ready = false`.

The remaining tilted-ring blocker is narrowed by:

```bash
python scripts/build_tcdr_v4_ngc2841_tilted_ring_geometry_source_review.py
```

This source-review artifact records the Bosma/NED evidence that the NGC2841
outer HI route is genuinely geometry-bearing: outer HI orientation differs from
the main body, the kinematical major axis changes in the outer parts, and an
annular tilted-ring model is constructed. It also records the blocker: the
radial PA/inclination profile is available in the local source representation
as a figure rather than as a machine-readable table. Therefore the result is
`geometry_route_supported = true` but
`exact_tilted_ring_numeric_profile_frozen = false`; endpoint replay, kernel
promotion, and new-route scoring remain closed.

A coarse review-candidate digitization of that figure can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_tilted_ring_digitized_profile_candidate.py
```

The script caches Bosma Figure 7 under
`data/external/literature/bosma1981_ngc2841_figure4_6_7.jpg` and digitizes only
the position-angle and inclination panels. It explicitly excludes the rotation
velocity and surface-density panels from the candidate profile. The result is a
low-resolution source-side profile candidate with an outer PA change of about
`12 deg` and inclination change of about `15 deg` across `0--37 kpc`. It is
`review_candidate_only_no_scoring`, not a frozen formula input.

A source-native PA/inclination support table can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_source_native_pa_inclination_table.py
```

This artifact records primary-source numeric geometry summaries without reading
endpoint residuals: THINGS/de Blok Table 1 lists the indicative global H I
inclination (`69 deg`) and LEDA optical inclination (`61 deg`); THINGS/de Blok
Table 2 gives the tilted-ring mean geometry (`<PA> = 152.6 deg`,
`<i> = 73.7 deg`); and Samurovic et al. give median ROTCUR geometry
(`PA = 150.7 deg`, `i = 73.5 deg`). These rows support the scalar geometry
scale of the tilted-ring route and cross-check the Bosma digitized candidate.
They do not close the radial-profile blocker: no source-native numeric radial
PA/inclination table has been located in this pass, so endpoint replay and
kernel promotion remain closed.

A bounded radial-table search audit can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_radial_pa_inclination_table_search_audit.py
```

This artifact preserves the negative source result explicitly: Bosma and
Samurovic expose radial PA/inclination shape at figure level, while de
Blok/THINGS and Samurovic provide source-native scalar summaries. No primary
machine-readable radial PA/i table was located in the bounded pass.

The corresponding independent-review package can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package.py
```

It writes
`data/reviewer_packages/tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_package_v0_1.zip`
and copies the same zip to `~/Downloads/`. The package asks an external
reviewer to digitize only Bosma Figure 7 panels a and b. The rotation-velocity
and surface-density panels are explicitly forbidden, as are all endpoint
rotation curves, residuals, and baseline scores. A completed response can
support a later source-side formula-freeze review, but the package itself does
not authorize endpoint replay.

The filled review response can be audited with:

```bash
python scripts/build_tcdr_v4_ngc2841_radial_pa_inclination_digitization_review_acceptance.py
```

For the current completed response, the audit is leakage-clean and accepts a
caveated source-side digitized radial PA/inclination profile: 16 points over
`0--37 kpc`, PA span about `12.1 deg`, and inclination span about `13.8 deg`.
This promotes the profile only to `formula_freeze_review_ready = true`; it does
not set `formula_ready = true` and does not authorize endpoint replay.

The accepted profile can then be converted into a source-side tilted-ring
geometry kernel review artifact with:

```bash
python scripts/build_tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review.py
```

This writes
`data/source_manifests/tcdr_v4_ngc2841_tilted_ring_geometry_kernel_freeze_review_v0_1.csv`
and its JSON summary. The kernel is dimensionless:
`K_geom(R)` is the normalized PA/inclination displacement from the inner
`R <= 10 kpc` orientation mean. It is a shape-only source artifact with no
sign, no carrier, and no amplitude. Therefore it is
`formula_freeze_review_ready = true`, but `formula_ready = false`, and endpoint
replay, kernel promotion, and new-route scoring remain closed.

The corresponding formula-rule review can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_tilted_ring_formula_rule_review.py
```

This manifest separates what is frozen from what remains blocked. The geometry
shape is frozen for formula review, and the fixed baryonic carrier is recorded
as a reviewable candidate inherited from the TCDR-v4 preflight convention.
However, the sign rule remains blocked because the same PA/i geometry can be
read as either projection/attenuation or added outer-capacity support, and the
amplitude/load rule remains blocked because the PA/i profile supplies no
velocity-squared load scale. Endpoint replay remains closed.

The source-side sign/load derivation can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_projection_sign_load_derivation.py
```

This derives only the strict projection branch. Using
`v_los(R) = v_c(R) sin i(R)` and the inner `R <= 10 kpc` inclination as the
reference, the projection branch is
`v_proj^2/v_carrier^2 = (sin i_ref / sin i(R))^2`. For the accepted profile
this gives an outer projection factor of about `0.878` and a maximum
attenuation cap of about `0.122`. This fixes a negative multiplicative
projection sign without fitting an amplitude. It does **not** derive the
positive added outer-capacity branch, because that would require an independent
velocity-squared load source.

The follow-up load-source derivation can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_outer_capacity_load_source_derivation.py
```

It separates five channels: the strict projection control, the Dragonfly
extended stellar/HI/UV capacity route, the warped-HI tilted-ring capacity route,
the XUV/HI outer star-forming capacity route, and their composite positive
outer-capacity shell. The conclusion is deliberately conservative:
`projection_control_ready = true`, but
`positive_added_capacity_load_ready = false`. Route support, radial support,
geometry, and equal source-side weights do not by themselves supply the
velocity-squared load needed by an additive
`v_readout^2 = v_carrier^2 + lambda K(R)` formula. Endpoint replay and kernel
promotion remain closed until an independent source-native load conversion,
predeclared train-only amplitude rule, or Tau-side load theorem is frozen.

A focused load-source search can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_outer_capacity_load_source_search.py
```

This search found one source-native baryonic ceiling/control from the Dragonfly
outer-disk mass statement. Zhang et al. report an outer stellar mass of
`1.4 +/- 0.2e8 Msun` beyond the warp-dominated `R > 30 kpc` region and an
outer stellar-to-gas surface-density ratio of about `3:1`. Treating this as an
outer baryonic mass ceiling gives only
`v2_ceiling_30kpc ~= 26.8 km^2/s^2`, or `v ~= 5.17 km/s`, under the simple
`G M / R` envelope. That is useful as a residual-blind baryonic control, but it
is not a positive dark-residual load. The best next source-native route is to
review-digitize `prof_masses1and2_4.pdf` from the Dragonfly arXiv source
package and convert the stellar/gas surface-density profiles under a frozen
disk-load rule.

The corresponding external-review package can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_mass_profile_digitization_review_package.py
```

It writes
`data/reviewer_packages/tcdr_v4_ngc2841_mass_profile_digitization_review_package_v0_1.zip`
and also copies the same ZIP to
`~/Downloads/tcdr_v4_ngc2841_mass_profile_digitization_review_package_v0_1.zip`
for a reviewer without repository access. The package contains the original
Dragonfly mass-profile PDF, a rendered PNG, a source-text excerpt, the
load-source search ledger, and a `review_response_template.csv`. The requested
review is strictly source-side: digitize only `Sigma_star(R)`, `Sigma_gas(R)`,
and optionally `Sigma_star/Sigma_gas`; do not use rotation curves, endpoint
residuals, Tau Core scores, or required-lambda diagnostics.

The filled reviewer response can be accepted and audited with:

```bash
python scripts/build_tcdr_v4_ngc2841_mass_profile_digitization_review_acceptance.py
python scripts/build_tcdr_v4_ngc2841_mass_profile_normalization_audit.py
python scripts/build_tcdr_v4_ngc2841_mass_profile_source_native_table_search.py
python scripts/build_tcdr_v4_ngc2841_mass_profile_semantics_clarification.py
python scripts/build_tcdr_v4_ngc2841_mass_profile_semantics_review_package.py
python scripts/build_tcdr_v4_ngc2841_mass_profile_semantics_review_acceptance.py
python scripts/build_tcdr_v4_ngc2841_surviving_route_ledger.py
```

The response passes the leakage flags and provides 29 caveated source-side
profile rows. However, the normalisation audit blocks load promotion: naive
annular integration of the digitized measured-color profile over `R >= 30 kpc`
is about `46x` larger than the quoted Zhang et al. outer-disk stellar mass.
Therefore the digitized profile is retained only as a shape candidate until the
component/normalization semantics are resolved. Endpoint replay and kernel
promotion remain closed. The follow-up semantics clarification localizes the
blocker to source-profile component identity and normalization, not endpoint
leakage. Area/inclination conventions alone are insufficient to explain the
tens-of-times mismatch, so the next allowed action is a focused reviewer
follow-up on curve identity/axis mapping or a source-native isolated-component
table/model. A focused source-native table search found no machine-readable
`Sigma_star(R)`/`Sigma_gas(R)` table in the Zhang et al. arXiv source package:
the package contains TeX and figure PDFs, including `prof_masses1and2_4.pdf`.
The TeX supports the split between displayed surface-density profiles and the
quoted integrated outer-disk mass, but does not resolve the normalization
mapping. The filled semantics review passes guardrails and closes the mass
profile route as `ACCEPT_SHAPE_ONLY_LOAD_FORMULA_BLOCKED`: the displayed
profile is not source-resolved as the isolated outer component, no
source-native normalization rule or axis/unit fix was found, and the profile
remains shape-only. Load formula, kernel promotion, and endpoint replay remain
closed unless an author/source-native isolated-component table or explicit
normalization rule is obtained.

The follow-up NGC2841 surviving-route ledger consolidates the local result:
five source-side shape/context routes survive, but zero positive
outer-capacity load routes are formula-ready. The Dragonfly mass profile is
closed as a load route and preserved only as shape context. The only clean
near-term replay direction is a projection-control diagnostic/preflight from
the tilted-ring PA/inclination branch; a positive dark-residual endpoint remains
blocked by missing independent velocity-squared load evidence.

That diagnostic boundary is frozen explicitly by:

```bash
python scripts/build_tcdr_v4_ngc2841_projection_control_preflight.py
```

The preflight records `tilted_ring_projection_control` as the only near-term
route. It is leakage-clean and source-side only: the accepted PA/inclination
profile supports a negative multiplicative projection/deprojection control with
outer factor about `0.878`, but it does not authorize endpoint scoring, kernel
promotion, or a positive additive dark-residual load. Any later projection
replay must be a separate diagnostic run that reads this frozen preflight
unchanged.

The corresponding diagnostic replay can be regenerated with:

```bash
python scripts/run_tcdr_v4_ngc2841_projection_control_diagnostic_replay.py
```

The replay preserves the expected negative-control result. With the fixed
baryonic carrier, the source-frozen projection control has weighted RMSE
`150.95 km/s`, compared with `144.88 km/s` for the unmodified baryonic carrier.
The outer-zone penalty is positive as well. This is not a failed endpoint; it
confirms that the tilted-ring projection branch is an attenuation/control lane,
not the missing positive dark-residual capacity for NGC2841.

The integrated Dragonfly outer baryonic mass ceiling is frozen separately with:

```bash
python scripts/build_tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_freeze.py
python scripts/run_tcdr_v4_ngc2841_integrated_outer_baryonic_ceiling_control_diagnostic.py
```

This is the strongest source-native velocity-squared control currently
available from the local Zhang et al. material, but it is very small:
`Delta v^2 = G M_outer / R` gives only about `26.8 km^2/s^2` at `30 kpc`.
The diagnostic replay moves the weighted RMSE from `144.876 km/s` to
`144.825 km/s`, a tiny improvement. It is therefore preserved as a baryonic
ceiling/control, not promoted as the positive dark-residual load.

The remaining positive-load gap after both frozen controls is measured by:

```bash
python scripts/build_tcdr_v4_ngc2841_post_control_positive_load_gap_diagnostic.py
```

The outer-zone median positive velocity-squared gap remains about
`65,313 km^2/s^2` after the baryonic ceiling control. The known outer baryonic
ceiling contributes a median `17.05 km^2/s^2`, only about `0.026%` of the
outer baryonic-carrier gap. Adding the projection control has the wrong sign
for closure and increases the outer gap. This diagnostic does not fit or
promote a kernel; it quantifies that the NGC2841 positive load must come from
a different source-native channel or a Tau-side load theorem.

The required-scale worklist can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_required_positive_load_scale_worklist.py
```

It converts the remaining positive `v^2` gap into a `G M / R`-equivalent scale
only as a source-search yardstick. In the outer zone the median equivalent
scale is about `6.88e11 Msun`, with interquartile range roughly
`5.45e11--8.75e11 Msun`. This is not a physical dark-matter mass claim and
must not be used as a fitted endpoint amplitude; it simply tells us that any
successful source-native channel or Tau-side load theorem must operate at a
much larger scale than the known integrated outer baryonic ceiling.

The source-native SPARC/THINGS gas proxy can be frozen with:

```bash
python scripts/build_tcdr_v4_ngc2841_sparc_hi_gas_load_proxy_freeze.py
```

This script reads only `Rad` and `Vgas` from `NGC2841_rotmod.dat` inside the
local SPARC `Rotmod_LTG.zip`; observed velocities and errors in the source file
are deliberately ignored. The frozen outer kernel is
`max(Vgas^2, 0) / max_outer(max(Vgas^2, 0))` for `R >= 30 kpc`, and zero
inside that window. It is a reproducible lower-bound HI/gas load proxy and
shape kernel. It is not the missing positive dark-residual load: the outer
median gas proxy is only about `6.5%` of the required post-control
velocity-squared yardstick, and even the outer maximum is only about `7.3%`.

The source-native THINGS/VizieR global HI packet can be frozen with:

```bash
python scripts/build_tcdr_v4_ngc2841_things_vizier_global_hi_source_freeze.py
```

This script queries the public VizieR mirror of the THINGS catalog
(`J/AJ/136/2563`) and caches the NGC2841 global HI spectrum and catalog
geometry. It yields 132 spectral rows, 123 finite flux rows, catalog
`D=14.1 Mpc`, `i=74 deg`, `PA=153 deg`, and a global positive-flux proxy of
about `183.31 Jy km/s`, corresponding to about `8.59e9 Msun` under the standard
HI-mass conversion at the catalog distance. This is useful source-side support
for substantial HI content, but it is still not a radial surface-density map or
velocity-squared load kernel.

The source-native THINGS/NED moment-0 radial shape freeze can be regenerated
with:

```bash
python scripts/build_tcdr_v4_ngc2841_things_ned_mom0_radial_profile_freeze.py
```

This script uses NED-hosted THINGS natural- and robust-weighted NGC2841 MOM0
FITS products, with the frozen THINGS catalog geometry `D=14.1 Mpc`,
`i=74 deg`, and `PA=153 deg`, to construct a residual-blind deprojected radial
MOM0 shape/support profile. It records 120 one-kpc radial-bin rows across the
NA and RO products. Both products retain source-native MOM0 support out to the
outermost 60 kpc bin at the 1% peak threshold, with outer `R >= 30 kpc` mean
shape values of about `0.236` and `0.261`, and peak shape values of about
`0.596` and `0.611`. This closes the profile-cache blocker. It does not close
the physical positive-load blocker, because the beam/unit/mass conversion and a
velocity-squared load rule still require a dedicated calibration audit.

The MOM0 beam/unit mass-conversion audit can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_things_mom0_beam_unit_mass_conversion_audit.py
```

This audit uses the CLEAN beam recorded in the FITS history to convert the MOM0
map sums into integrated HI-flux and HI-mass proxies. As a source-side
calibration check, the NA and RO products give integrated flux ratios of about
`0.960` and `0.988` relative to the VizieR global HI spectrum. This supports a
residual-blind HI mass-profile proxy, with integrated HI masses of about
`8.24e9 Msun` and `8.48e9 Msun`. The artifact also writes an enclosed
spherical `G M(<R) / R` diagnostic for triage, but this is not a promoted disk
gravity kernel, not a positive dark-residual load claim, and not endpoint-ready.
The remaining blocker is a source-frozen disk-gravity/load-promotion review.

The MOM0 disk-load promotion review can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_mom0_disk_load_promotion_review.py
```

This review promotes only the physical HI component to a source-frozen disk-load
control with `lambda_HI=1`, and separately records the standard `1.36`
HI+helium gas bookkeeping factor used in THINGS-based gas-surface-density work.
It uses a softened axisymmetric annular disk integral over the MOM0-derived HI
mass profile and chooses the RO product as the primary source-side product
because it has the smaller beam and the closer global-flux match to VizieR; NA
is retained as a cross-check. The outer `R >= 30 kpc` physical-HI disk-load
proxy reaches about `1128 km^2/s^2` in the RO product and about
`1107 km^2/s^2` in NA; the corresponding standard HI+He controls are about
`1534 km^2/s^2` and `1506 km^2/s^2`. This is a reproducible physical-gas
control, not a dark-residual kernel. Any extra halo-capacity or positive
residual multiplier remains blocked unless it is supplied by an independent
source-native rule or a Tau-side load theorem.

The halo-capacity conversion search can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_halo_capacity_conversion_search_freeze.py
```

This ledger keeps the SPARC/THINGS gas proxy only as the frozen lower-bound
component above, keeps the VizieR/THINGS global HI spectrum only as global
HI support, and now keeps the THINGS/NED MOM0 radial profile and mass-profile
proxy only as source-side support. It also records the MOM0-derived physical HI
disk load as a `lambda_HI=1` control and the standard HI+He gas control with no
residual-tuned multiplier. The next primary blocker is no longer profile
acquisition, beam/unit conversion, or physical-gas disk-load review; it is the
lack of an independent source-native multiplier or Tau-side load theorem for
any extra positive residual capacity. Bosma-style HI scaling remains
blocked until an independent scale is source-frozen, and published NFW/ISO
halo-fit parameters are rejected as Tau source-freeze inputs because they are
endpoint rotation-curve fits. The ledger still does not permit endpoint scoring,
kernel promotion, or positive-load freeze.

The source-route re-audit can then be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_positive_outer_capacity_source_route_reaudit.py
```

This artifact closes the NGC2841 projection route as an attenuation/control
layer, closes the known integrated outer baryonic mass as a tiny ceiling
control, and keeps the Dragonfly mass-profile material as shape context only.
It records the SPARC/THINGS gas proxy as frozen lower-bound HI/gas support, but
still keeps `outer_hi_warp_halo_capacity` blocked as the primary residual-blind
positive-load candidate because a halo-capacity or extended-HI load conversion
is still missing. XUV/HI, diffuse-envelope, history/environment, and Tau-side
theorem routes remain secondary worklist entries. It does not permit endpoint
scoring or kernel promotion.

The independent multiplier rejection audit can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_independent_multiplier_rejection_audit.py
```

This final NGC2841 source-side guard separates a legitimate physical-gas
bookkeeping control from any extra dark-residual multiplier. The standard
HI+He factor remains usable only as a baryonic gas control. Bosma-style HI
scaling, XUV/HI support, diffuse-envelope support, and history/environment
routes are retained as source/context candidates but do not supply a
source-frozen multiplier. Published NFW/ISO halo-fit parameters are rejected as
endpoint-fit routes. Thus the next admissible positive-load step is either an
independent source-native extra-capacity multiplier or a Tau-side load theorem,
not a replay from the required residual scale.

The Tau-side load theorem readiness audit can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_tau_side_load_theorem_readiness.py
```

This audit makes the minimal theorem shell explicit,
`Delta_v_tau^2(R)=A_tau*K_outer(R)`, while keeping it blocked. The support
field and positive-load route anatomy are only partially ready, and the
no-double-counting plus endpoint-leakage boundaries are ready as audit
constraints. The two theorem-level blockers are sharper now: no Tau-side unit
map has been derived from the outer-capacity class into velocity-squared units,
and no protected residual-blind amplitude source `A_tau` exists. Therefore the
Tau-side route is a focused derivation target, not an endpoint permission.

The related-paper proxy-transfer audit can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_related_paper_proxy_transfer_audit.py
```

This audit checks whether earlier Paper 8/9 proxy machinery can close the
NGC2841 `A_tau` blocker. It finds a useful Paper 9 Bullock-disk spin proxy for
NGC2841 (`lambda_spin ~= 0.02024`, corresponding to `beta ~= 1.08034` if used
inside that beta-transfer grammar), but this is dimensionless and belongs to a
multiplicative beta/closure route, not the present additive
`Delta_v_tau^2=A_tau*K_outer` route. Paper 8's `lambda_w=sigma*q*x_w*Vflat^2`
ansatz is a useful source-factored amplitude pattern, but remains
formula-conditional and not directly transferable. The audit therefore finds no
direct `A_tau` proxy; it only opens a possible future reclassification question:
whether NGC2841 should be treated as a multiplicative beta/closure candidate
instead of an additive outer-capacity candidate.

The multiplicative beta/closure reformulation preflight can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_multiplicative_beta_closure_reformulation_preflight.py
```

This follow-up opens that reclassification question without scoring it. It
uses the Paper 9 Bullock proxy only as a dimensionless beta-context signal and
records the conditional shell
`v_beta^2(R)=v_carrier^2(R)*[1+(beta_cl-1)*K_beta(R)]`, equivalently
`Delta_v_beta^2(R)=(beta_cl-1)*K_beta(R)*v_carrier^2(R)`. The shell is
dimensionally coherent if `beta_cl` and `K_beta` are dimensionless and the
carrier has velocity-squared units. It does not authorize replay: a source-side
beta/closure reformulation label, a source-frozen carrier, and a source-frozen
`K_beta(R)` remain blocked prerequisites. The additive `A_tau` route remains
blocked separately.

The beta/closure reformulation label review can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_reformulation_label_review.py
```

This source-side review advances only the review status. It combines the Paper
9 predeclared beta-transfer candidate row, the weak NFW-preference transfer
priority, the Bullock-like spin conversion proxy, and Paper 19's
high-inclination warped-HI/tilted-ring context. The verdict is
`review_open_not_promoted`: NGC2841 has enough residual-blind context to prepare
a beta/closure reviewer package, but not enough to promote the family label,
freeze the formula, or run endpoint scoring. The remaining blockers are an
independent spin-route decision, a source-frozen carrier, and a source-frozen
`K_beta(R)`.

The filled beta/closure reviewer response can be accepted with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_reformulation_review_acceptance.py
```

The reviewer keeps the route open but not promoted. The Bullock-like spin proxy
is retained as context only, not as a frozen spin-normalization source; the
carrier still requires a new source-frozen velocity-squared field; and
`K_beta(R)` still requires a residual-blind radial PA/inclination profile or a
source-native radial table. Endpoint replay, kernel promotion, and formula
freeze remain closed.

The beta/closure `K_beta(R)` profile freeze review can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_k_beta_profile_freeze_review.py
```

This follow-up uses the accepted Bosma Fig. 7a/7b PA/inclination digitization
through the tilted-ring geometry profile to freeze only a caveated
dimensionless radial shape,
`K_beta_shape(R)=minmax_0_1(K_geom_raw(R))`. This resolves the radial-shape
part of the `K_beta` blocker for a later formula-freeze review, but it does
not freeze the spin normalization, sign, amplitude, or carrier. Full formula
freeze and endpoint replay remain closed; the remaining blockers are the
context-only spin route and the missing source-frozen velocity-squared carrier.

The beta/closure baryonic carrier freeze review can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_baryonic_carrier_freeze_review.py
```

This artifact reads only the SPARC rotmod source-side component columns
`Vgas`, `Vdisk`, and `Vbul` for NGC2841 and freezes the fixed-M/L carrier
`v_carrier^2(R)=sign(Vgas)Vgas^2 + 0.5 Vdisk^2 + 0.7 Vbul^2`. The same file
contains `Vobs` and `errV`, but these are recorded as forbidden endpoint
columns and are not parsed into the artifact. This closes the carrier blocker
for formula-freeze review only. The remaining blocker is the spin/beta
normalization, because the Bullock-like proxy is still context-only and not a
frozen beta amplitude. Endpoint replay remains closed.

The beta/closure context-formula freeze review can be regenerated with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_context_formula_freeze_review.py
```

This final pre-endpoint step resolves the remaining spin-normalization blocker
by not treating it as a physical spin measurement. Instead, the Paper 9
Bullock-like value is frozen only as a caveated dimensionless `beta_context`
coefficient inside
`v_beta_context^2(R)=v_carrier^2(R)*[1+(beta_context-1)*K_beta_shape(R)]`.
All terms are now frozen for formula review, with `K_beta_shape` interpolated
onto the frozen carrier grid. This is still not endpoint authorization:
endpoint replay, kernel promotion, and validation claims remain closed until a
separate endpoint authorization review is prepared.

The beta/closure endpoint authorization reviewer package can be regenerated
with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_endpoint_authorization_reviewer_package.py
```

This writes a repo-local package and a copy under `~/Downloads/`. It contains
only frozen formula-review artifacts and a `review_response_template.csv`.
It contains no endpoint scores. A later replay may be prepared only if an
external reviewer authorizes `authorize_endpoint_replay_preliminary_control`
while preserving the no-retuning, no-relabeling, and no-validation boundaries.

The filled endpoint-authorization response can be accepted with:

```bash
python scripts/build_tcdr_v4_ngc2841_beta_closure_endpoint_authorization_review_acceptance.py
```

The accepted response authorizes only a separate NGC2841 single-object
preliminary endpoint/control replay. The scoring script may read observed
rotation data only after this authorization, must read the frozen
`v_beta_context^2(R)=v_carrier^2(R)*[1+(beta_context-1)*K_beta_shape(R)]`
profile unchanged, and may not retune the formula, relabel the morphology or
readout route, promote the kernel, or claim validation.

The authorized preliminary replay can then be run with:

```bash
python scripts/run_tcdr_v4_ngc2841_beta_closure_endpoint_control_replay.py
```

The current local result is a weak positive control: the beta-context replay
improves the fixed-M/L baryonic carrier by about `3.71 km/s` in weighted RMSE,
but the remaining velocity gap is still large, especially in the outer zone.
It is therefore retained as a preliminary endpoint/control replay, not as a
validated or sufficient NGC2841 readout.

## Draft-close interpretation

The current draft can be closed as a controlled Photon-C dark residual protocol,
not as observational validation. Its real-data lesson is deliberately bounded:
source-frozen Tau kernels can move rotation curves in the correct direction
against selected controls, but the present TCDR-v4 kernels are not yet complete
curve predictors. `NGC6503` is the cleanest preliminary positive control,
`NGC7793` is a caveated support-safe positive, and `NGC2841` remains a stress
case where the score improves but the absolute readout capacity is insufficient.

This points to the next required kernel class: not only morphology-labelled
templates, but source-frozen observer-conditioned readout kernels that include
projection, path, history, and capacity components where residual-blind source
data justify them. Until such kernels are frozen and tested on a predeclared
sample, the paper should claim protocol viability and directional evidence only,
not a final Tau Core rotation-curve law.

## arXiv Source Package

`arxiv_submission_source.zip` is generated from
`paper19_submission_source/` and excludes the compiled PDF plus temporary TeX
build products.

## Scope

Paper 19 is a controlled draft protocol with synthetic tests and preliminary
real-data stress tests. It extends the Paper 18 photon-lensing MAR direction
toward a broader Photon-C/null-probe and dark-residual audit grammar. Its
status is:

```text
CONTROLLED_PHOTON_C_DARK_RESIDUAL_DRAFT_PROTOCOL
```

## Relation to Other Tau Core Papers

- Paper 7 gives lensing-observer feasibility and falsification discipline.
- Paper 14 gives the cosmic-web witness ladder.
- Paper 17 gives shared-parent covariance versus orientation-only guardrails.
- Paper 18 gives photon-lensing MAR synthetic bridge tests.
- Paper 19 turns the Photon-C/null probe intuition into a dark-residual
  residual-classification protocol with null/time split toys and a real-data
  TCDR-v4 skeleton.

## Upstream Ownership, Inherited Results, and Scope Boundary

- **Source selection and finite laboratory:** Foundation Papers I, III, IV (`TD-0`), and V retain physical source selection, geometric readout, and clock/inertial descent; numerical checks in [`seed_evolution_lab`](https://github.com/tau-core-research/tau-core-theory/tree/main/experiments/seed_evolution_lab) and [`lab_update_2026_09_15.json`](data/derived/lab_update_2026_09_15.json) remain conditional internal recoveries rather than SI-constant or gravitational derivations.
- **Observer contact and conditional access (`CPR1`, `MSI1`):** Inherited BRAC contact, coherent-state uniqueness, and coupled harmonic covariance ([`observer_update_2026_09_14.json`](data/derived/observer_update_2026_09_14.json), [`state_update_20260918.json`](data/derived/state_update_20260918.json)) together with [Paper 4 / Paper V `CPR1(b,c)`](https://github.com/tau-core-research/tau-core-higgs-module-paper4/blob/main/paper4_full_derivation/full_derivation.pdf#nameddest=cpr1) ([`pair_readout_update_20260927.json`](data/derived/pair_readout_update_20260927.json)) and [`MSI1 v1.0`](https://github.com/tau-core-research/tau-core-higgs-module-paper4/blob/main/paper4_full_derivation/full_derivation.pdf#nameddest=msi1) distinguish access-specific nulls and positive work from complete-channel nulls or unique mass pairings.
- **Surviving-source instruments (`OIR1`) and terminal boundary:** [Foundation VI / Paper VII-A `OIR1(a–c) v1.0`](https://github.com/tau-core-research/tau-core-quantum-readout-foundation-paper-vi/blob/main/paperVI_submission_source/main.pdf#nameddest=oir1) and `ORA-T1` ([`publication_state_20261009.json`](data/derived/publication_state_20261009.json)) separate ideal optical transfer, absorptive count records, and retained-source QND operations; physical source occupation, detector calibration, and operational `Q_OS` remain open, and no synthetic or preflight score in Paper 19 is altered.
