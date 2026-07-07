# Tau Core Photon-C Dark Residual Package

This package contains a working paper draft and executable toy simulations for a Tau Core research line connecting:

- Photon-C Module
- Tau Core Relativity Module
- Gravity / Dark Residual Module
- TCDR-v1 toy
- TCDR-v2 noisy toy
- TCDR-v3 null/time split toy
- TCDR-v4 real-data-ready protocol skeleton

## Files

```text
paper_draft.md          Main detailed markdown paper draft
protocol_TCDR_v4.md     Real-data-ready protocol skeleton
toy_simulation.py       Executable Python toy simulations
README.md               This file
figures/                Generated plots
results/                CSV/JSON result outputs
```

## How to run

From this directory:

```bash
python toy_simulation.py
```

The script generates:

```text
results/tcdr_summary.csv
results/tcdr_summary.json
figures/tcdr_delta_r2.png
figures/tcdr_pvalues.png
figures/tcdr_score.png
figures/tcdr_v3_split_scatter.png
```

## What the toy simulations do

### TCDR-v1

Clean synthetic residual recovery. Tests whether a pre-defined morphology/filament seed can be recovered when inserted into otherwise simple mock residuals.

### TCDR-v2

Noisy synthetic residual recovery. Adds halo misspecification, baryonic uncertainty, orientation errors, and survey-like systematics.

### TCDR-v3

Null/time split toy. Simulates separate timelike/dynamical and null/lensing residual channels and tests whether their split correlates with pre-defined morphology/filament/break seed variables.

## Important scientific boundary

These toys do not prove Tau Core. They validate only a methodology:

> If a pre-defined morphology/readout residual exists in mock data, the protocol can recover it; if it does not exist, the protocol should not produce a strong false positive.

A real claim would require real astronomical data, pre-registration, standard halo and baryonic controls, permutation controls, survey-systematics checks, and out-of-sample validation.

## Suggested next branch

After this package, continue with the quantum branch:

```text
TCQ-1 Measurement Closure Module
TCQ-2 Photon Interference Module
TCQ-3 Entanglement Compatibility Module
```
