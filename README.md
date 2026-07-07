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
   decomposition source-route artifact, and endpoint-blind coordinate-freeze
   manifest;
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
