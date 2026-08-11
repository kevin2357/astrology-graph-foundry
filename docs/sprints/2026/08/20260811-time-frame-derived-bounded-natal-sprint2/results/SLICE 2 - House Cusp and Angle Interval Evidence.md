# Slice 2 — House Cusp and Angle Interval Evidence

**Status:** Gate 2 candidate; awaiting human review

## Outcome

Bounded Natal now evaluates twelve labeled house cusps plus ASC, DSC, MC, IC, and
Vertex at every minute using `swisseph.houses_ex2`. Each coordinate receives a
continuous-safety circular range, possible signs, sampled transition witnesses,
provider prerequisites, and a feature-scoped availability classification. No
representative degree enters the bounded graph.

The initial qualified profile is deliberately limited to Placidus (`P`) and Whole
Sign (`W`). Other valid exact-chart systems return an explicit unsupported result in
bounded mode rather than inheriting untested topology assumptions.

## Exact-path repairs

The two defects discovered in Slice 1 are fixed before new evidence is built:

- `house_data` preserves Swiss Ephemeris cusp numbering instead of rotating the
  nearest cusp toward the Ascendant. Whole Sign therefore retains its correct first
  house even when another cusp is nearer the Ascendant.
- `ProviderConfig` accepts only reviewed uppercase twelve-house codes. Unknown `Z`,
  lowercase aliases, and 36-sector Gauquelin `G` are rejected before provider
  invocation, preventing mislabeled Placidus fallback output.

This exact-path correction is behaviorally significant for non-Ascendant-first
systems and must remain visible in eventual release notes.

## Evidence contract

`terrestrial_frame.coordinates` contains 17 evidence records. Smooth coordinates
use labeled unwrapped paths plus conservative `houses_ex2` speed padding between
minute evaluations. Origin crossings become ordered circular segments. Whole Sign
cusp jumps are retained as variable ranges and transition witnesses; no scalar
midpoint fills the gap.

Provider failure is scoped. If Placidus fails in the polar circle, the frame and all
future dependent families are inconclusive, but the already-qualified celestial
body, coordinate, and body-aspect evidence remains usable. Swiss Ephemeris' reported
Porphyry substitution is not accepted as configured Placidus output.

The package now exposes terrestrial evidence under both `bounded_natal` and
`uncertainty_assessment`, and every coordinate is addressable in the uncertainty
registry. Houses and angles are marked `assessed_as_terrestrial_frame_ranges`;
placements, sect, and lots remain unavailable until their later slices.

Calculation provenance advances from bounded profile v1.5.0 to v1.6.0 and records
the configured system, qualified systems, `houses_ex2`, and half-open circular
assignment rule. The dataset schema remains additive at 1.0.0.

## Controlled qualification

The retained Linux QA image evaluated a four-hour Denver interval for both systems:

- Placidus: complete, 241 evaluations, 17 coordinate records;
- Whole Sign: complete, 241 evaluations, 17 coordinate records; and
- Placidus at latitude 67 degrees: terrestrial frame inconclusive with explicit
  polar/provider failure and no accepted fallback.

Compact evidence is in
[`terrestrial-frame-live-summary.json`](terrestrial-frame-live-summary.json).

## Gate checks

- Cusp/angle zero-wrap and transition evidence: passed.
- Whole Sign frame-transition and numbering regression: passed.
- Polar provider-failure classification: passed in controlled Linux execution.
- Unsupported-system and invalid-code behavior: passed.
- Provenance, registry, schema, and precision-safety tests: passed.
- Full host suite: 244 passed.
- JSON validation and `git diff --check`: passed.
- Human review: pending.

## Deliberate boundary

This slice does not yet assign bodies to houses or emit cusp/angle canonical objects.
It establishes their evidence prerequisites. Slice 3 consumes these labeled frames
to promote only invariant house membership and preserve possible-house alternatives.
