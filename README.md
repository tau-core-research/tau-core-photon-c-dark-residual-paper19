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
figures/*.png
source_package_docs/
source_package_figures/
code/toy_simulation_source.py
```

No real galaxy, lensing, rotation-curve, or cosmology survey data are included.

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
6. copies figures into the paper source tree;
7. compiles `paper19_submission_source/main.tex`;
8. builds `arxiv_submission_source.zip`;
9. runs public package tests;
10. prints `PAPER19_PHOTON_C_DARK_RESIDUAL_REPRODUCTION_COMPLETE`.

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
