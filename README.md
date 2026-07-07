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
