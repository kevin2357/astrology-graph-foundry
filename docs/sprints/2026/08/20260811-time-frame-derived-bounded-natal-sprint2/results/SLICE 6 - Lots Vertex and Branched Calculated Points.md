# Slice 6 — Lots, Vertex, and Branched Calculated Points

## Outcome

Gate 6 is ready for human review. Bounded Natal now evaluates the exact-Natal Part
of Fortune and Lot of Spirit formulas across the complete normalized birth-time
domain, preserves formula discontinuities, and promotes only invariant sign or
house semantics. Vertex now participates in house-membership evidence.

## Contract

- Fortune uses `ASC + Moon - Sun` by day and `ASC + Sun - Moon` by night.
- Spirit uses the inverse day/night ordering.
- Every contiguous day/night run has its own speed-enveloped circular range.
- Formula branches are never interpolated across a sect transition.
- Canonical objects contain invariant categorical facts and evidence references,
  never a midpoint or representative longitude.
- Disabling sect disables branched lots rather than choosing a formula silently.

## Implementation and versioning

- Added calculated-point terrestrial-frame evidence and evidence-registry rows.
- Added calculated-point and Vertex house assessment.
- Added calculated-point relationship proof that requires every formula branch to
  establish the same aspect before canonical promotion.
- Added `bounded_calculated_point` canonical objects and capability metadata.
- Bounded canonical graph advanced additively from `1.6.0` to `1.7.0`.
- Bounded calculation profile advanced from `v1.9.0` to `v1.10.0`.
- Dataset schema remains `1.0.0`.

## Verification

- Pure Gate 6 tests: 22 passed.
- Full host suite: 253 passed.
- Controlled Linux live cases: invariant day, invariant night, and sunrise crossing.
- Sunrise produced two separate formula branches for Fortune and Spirit.
- Daytime Fortune demonstrated independent categorical promotion: house 11 was
  invariant while zodiac sign varied.
- Schema validation and canonical evidence-reference closure passed.
- `git diff --check` passed.

Compact live evidence is retained in `calculated-points-live-summary.json`.

## Gate disposition

Candidate for Gate 6 approval. No downstream repository, release, tag, external
ephemeris file, or publication was changed.
