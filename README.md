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

## arXiv Source Package

`arxiv_submission_source.zip` is generated from
`paper19_submission_source/` and excludes the compiled PDF plus temporary TeX
build products.

## Scope

Paper 19 is a synthetic protocol paper. It extends the Paper 18 photon-lensing
MAR direction toward a broader Photon-C/null-probe and dark-residual audit
grammar. Its status is:

```text
CONTROLLED_SYNTHETIC_PHOTON_C_DARK_RESIDUAL_PROTOCOL
```

## Relation to Other Tau Core Papers

- Paper 7 gives lensing-observer feasibility and falsification discipline.
- Paper 14 gives the cosmic-web witness ladder.
- Paper 17 gives shared-parent covariance versus orientation-only guardrails.
- Paper 18 gives photon-lensing MAR synthetic bridge tests.
- Paper 19 turns the Photon-C/null probe intuition into a dark-residual
  residual-classification protocol with null/time split toys and a real-data
  TCDR-v4 skeleton.
