# TCDR-v4 Source-Frozen Formula Ladder Import

This note records the route by which Paper 19 returns to the earlier
Paper 8/Paper 9 morphology-readout formula discipline.  It is not an endpoint
score and it does not introduce a new fitted kernel.

## Verdict

The v0.1--v0.3 mixed-component kernels in Paper 19 are useful diagnostics, but
they are still proxy-level component templates.  The next kernel-development
step is not another hand-specified family template.  It is a source-frozen
formula compiler that imports the common morphology-readout ladder:

```text
source-native observables
  -> source load and support window
  -> dimensionally checked component formula
  -> zero-source / known-limit guard
  -> predeclared mixed composition rule
  -> endpoint replay and shuffled-component controls
```

## Imported Ladder

The imported source-frozen ladder is:

```text
tau-core-morphology-readout-common/reports/source_frozen_readout_formula_derivation_ladder.md
```

It contains formula-conditional component shells such as:

- exponential disk readout with scale radius and disk-load input;
- scale-tail spiral readout with tail/onset radius, H I outer support, and
  outer H I load;
- diffuse plus scale-tail mixed readout with gas load, H I support, and
  diffuse-index input;
- compact finite-source readout with compact support radius and compact mass;
- thick/flared readout with vertical/flare support fields.

These are not final Tau laws.  They are source-frozen formula targets that
become endpoint-eligible only when the required source observables, amplitude
or load rule, support window, sign, zero-source limit, and failure rules are
frozen before scoring.

## Relation To Paper 19 v0.1--v0.3

The current Paper 19 sequence established the blocker:

| layer | status | lesson |
| --- | --- | --- |
| v0.1 fixed primary/secondary weights | diagnostic | mixed components help, but shuffled nulls remain competitive |
| v0.2 source-strength weights | directional strengthening | source evidence improves selectivity but not enough for promotion |
| v0.3 radial/source-geometry stress | negative/cautionary | adding more source geometry does not automatically improve the score |

Therefore the next route must replace component-template guessing by formula
generation from source-frozen observables.

## TCDR-v4 Formula Compiler Target

For each galaxy and each active component \(a\), the compiler should emit:

```text
component_id
source_observables_a
support_window_a(R)
load_rule_a
dimensionless_shape_kernel_a(R | source_observables_a)
delta_v2_a(R) = load_rule_a * shape_kernel_a(R)
zero_source_limit_a
known_limit_a
source_overlap_decision_a
claim_boundary_a
```

The galaxy-level readout is then:

```text
delta v_TCDR^2(R) = Compose_a delta_v2_a(R)
```

where `Compose_a` must be declared before endpoint scoring.  Additivity is not
automatic; overlapping components must be merged, justified by a non-overlap
source ledger, or demoted to controls.

## v0.4 Readiness Implementation

Paper 19 now includes the first compiler-readiness implementation:

```text
scripts/build_tcdr_v4_p0_source_frozen_formula_compiler_readiness.py
```

This script emits:

```text
data/source_manifests/tcdr_v4_p0_source_frozen_formula_compiler_readiness_v0_4.csv
data/source_manifests/tcdr_v4_p0_source_frozen_formula_compiler_readiness_summary_v0_4.json
```

It is endpoint-blind.  It uses only residual-blind source observables to decide
whether a P0 object is formula-ready, partial, template-only, or blocked.  In
the current ledger:

```text
READY_FORMULA_COMPILER_REPLAY_CANDIDATE       30/66
PARTIAL_FORMULA_COMPILER_CANDIDATE            16/66
FALLBACK_TEMPLATE_ONLY_NOT_FORMULA_READY      19/66
BLOCKED_UNFREEZABLE_SOURCE_FAMILY              1/66
```

The formula-ready holdout subset is:

```text
NGC1090, NGC2841, NGC3198, NGC5033, NGC6503
```

The optional author-local endpoint preflight for that subset is:

```text
scripts/run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready.py
```

This replay writes only to the gitignored `data/external/` area.  It is a
scoring-direction check for the formula compiler route, not population
validation.

The matching shuffled-component control is:

```text
scripts/run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready_shuffled.py
```

It keeps the formula-ready holdout subset fixed and shuffles the source
component packages.  The current author-local result remains caveated: the
actual formula-ready median weighted RMSE is only slightly better than the
median shuffled-null median, and 25/64 shuffled nulls are at least as good as
the actual formula-ready kernel.  Therefore the compiler route is
scoring-directional but not endpoint-promotion ready.

The matching component-ablation diagnostic is:

```text
scripts/run_tcdr_v4_holdout_endpoint_scoring_formula_compiler_ready_component_ablation.py
```

It keeps the formula-ready holdout subset fixed and asks whether the full
source-frozen bar/ring/spiral mix is actually needed.  Component-only and
leave-one-out variants receive their own train-pool-only amplitude and do not
fall back to a family proxy.  The current author-local result is cautionary:
the full mix has median weighted RMSE 60.456 km/s, while the best ablation
median is 60.340 km/s for `spiral_only`.  Thus the available source
observables do not yet uniquely select the component composition.

The corresponding endpoint-blind source-side audit is:

```text
scripts/build_tcdr_v4_p0_source_composition_uniqueness_audit.py
```

It records whether each object has a unique, weakly unique, ambiguous, or
uncovered source-component composition before endpoint scoring.  In the
current v0.5 ledger, the five formula-ready holdout galaxies contain three
source-composition unique cases, one ambiguous case, and one source-native
component-uncovered case.

The optional post-freeze alignment diagnostic is:

```text
scripts/run_tcdr_v4_formula_ready_source_composition_vs_ablation_diagnostic.py
```

It compares the source-dominant component to the local ablation winner after
both artifacts are frozen.  The current local alignment is only 1/4 among
positive-source-component holdout objects.  This is diagnostic only and must
not be used as a kernel-selection rule.

The support-aware selector audit is:

```text
scripts/build_tcdr_v4_p0_support_aware_component_selector_audit.py
```

It keeps the source weights frozen but demotes apparent source-dominant
components when the declared bar/ring/spiral source supports overlap or are
adjacent.  In the current v0.6 ledger, only NGC2841 is selector-safe in the
formula-ready holdout subset; NGC1090, NGC3198, and NGC5033 are unresolved by
support overlap/adjacency, and NGC6503 is source-native component-uncovered.
This makes source-composition support safety a separate requirement from
formula readiness.

The support-safe expansion manifest is:

```text
scripts/build_tcdr_v4_p0_support_safe_expansion_manifest.py
```

It does not score galaxies.  It only asks which P0 objects are both
formula-ready and support-safe under the frozen source-side ledgers.  The
current v0.7 pool contains 7 galaxies: NGC0024, NGC2841, NGC5005, NGC7793,
UGC04499, UGC06917, and UGC06983.  This is the clean candidate pool for a
future support-safe replay, not evidence that the replay will pass.

The support-safe expansion opportunity ledger is:

```text
scripts/build_tcdr_v4_p0_support_safe_expansion_opportunity_ledger.py
```

It answers the narrower question: can the pool be expanded further without
endpoint leakage?  The current v0.8 answer is tiered.  Seven objects are
replay-eligible now; three more need formula completion; twelve are
formula-ready but need support-overlap review; eleven are formula-ready but
need a disk or other component-source rule.  Therefore the next bounded target
is a 10-object support-safe pool after formula completion, not unconstrained
sample expansion.

The support-safe formula-completion manifest is:

```text
scripts/build_tcdr_v4_p0_support_safe_formula_completion_manifest.py
```

It closes the bounded 7-to-10 step.  The three Tier1 objects enter by their
source-dominant support-safe component route: NGC3893 through the spiral route,
and UGC00191/UGC12732 through the bar route.  The 10-object pool is therefore
source-side formula-complete, but it is still not an endpoint result.

The optional local LOOCV scoring script is:

```text
scripts/run_tcdr_v4_support_safe_pool_loocv_scoring.py
```

It scores the frozen 7-object and 10-object pools only after source freeze.  In
the current local run, the 7-object pool beats the baryonic carrier in 6/7 and
the wrong-component mean in 2/7; the 10-object pool beats the baryonic carrier
in 9/10 and the wrong-component mean in 5/10.  The expansion is directionally
better, but strict wrong-component controls remain competitive.

The follow-up failure-ledger / formula-aware script is:

```text
scripts/run_tcdr_v4_support_safe_pool_failure_and_formula_aware_scoring.py
```

The failure ledger shows that the best-wrong blocker is mixed in kind: some
best-wrong wins are source-visible secondary components, some are broad-family
versus top-component mismatches, and several remain unexplained competitive
false-component controls.  The formula-aware replay then uses the frozen
`support_safe_compiled_formula` instead of the top component alone.  It
improves the 10-object pool to 10/10 against the baryonic carrier and 6/10
against the wrong-component mean, but only 2/10 against the best wrong
component.  Therefore formula awareness helps, but it does not close the
strict-control blocker.

The Paper8/Paper9 overlay script is:

```text
scripts/build_tcdr_v4_paper8_paper9_failure_overlay.py
```

This diagnostic imports two older morphology-readout lessons without changing
the endpoint scoring rule: (i) visible source morphology `K_obs` may differ
from readout-active `K_readout`, and (ii) projection/history routes require
independent residual-blind source tokens before use.  In the current local
overlay, the 17 rows split into 3 strict-control survivals, 3 near ties, 4
source-visible secondary-component cases, 2 broad-disk `K_obs`/`K_readout`
mismatch candidates, and 5 rows blocked until independent spiral/projection
or history evidence exists.  This is a route-permission diagnostic only; it
does not promote a repaired kernel.

The scoring-readiness and readiness-filtered scoring scripts are:

```text
scripts/build_tcdr_v4_paper8_paper9_scoring_readiness_ledger.py
scripts/run_tcdr_v4_paper8_paper9_readiness_filtered_scoring.py
scripts/run_tcdr_v4_readiness_filtered_metric_robustness.py
```

They filter the existing formula-aware rows through the route-permission
ledger.  Immediate current-formula replay is allowed only for strict survivals
and near ties.  In the current local run, the allowed six rows span four unique
galaxies and beat baryonic and wrong-component-mean controls in 6/6, while
strict best-wrong survival remains 3/6.  This is a bounded scoring diagnostic,
not endpoint validation.
The metric-robustness replay keeps strict best-wrong survival at 3/6 under
both weighted and unweighted RMSE.  However, wrong-component-mean survival
drops from 6/6 weighted to 4/6 unweighted, so the positive subset remains
useful but not validation-grade.

The mixed-route shuffle-control and route-closure scripts are:

```text
scripts/run_tcdr_v4_support_safe_mixed_route_shuffle_control.py
scripts/build_tcdr_v4_kobs_kreadout_source_review.py
scripts/build_tcdr_v4_paper8_paper9_scoring_route_closure.py
scripts/build_tcdr_v4_source_gap_blocker_ledger.py
```

They test the tempting Paper8 mixed-route opening.  Although the four
mixed-route rows close the source non-overlap condition, none passes the
shuffled formula-package control at the predeclared threshold.  The route
closure therefore keeps the mixed rows blocked and leaves only the six
current-formula rows replay-ready.  This is a preserved negative control.

The `K_obs`/`K_readout` source review then closes the two NGC0024 broad-disk
mismatch rows in the negative direction.  The visible source family is
disk/spiral, but the source-side component ledger is bar/ring, with zero
spiral component weight and no source-native spiral geometry.  Therefore the
NGC0024 rows are not relabeled from the endpoint control; they remain blocked
by source review.

The source-gap blocker ledger then inspects the remaining five source-gap rows.
All five are competitive spiral controls outside the frozen source family and
lack independent source-side spiral support.  They remain source-acquisition
tasks, not replay candidates.

## Claim Boundary

This import does not validate Paper 19 and does not claim dark-residual
detection.  It only fixes the next non-ad-hoc kernel-development route:

```text
TCDR-v4 v0.4 = source-frozen formula compiler readiness and formula-ready
preflight replay, not another family-template guess.
```
