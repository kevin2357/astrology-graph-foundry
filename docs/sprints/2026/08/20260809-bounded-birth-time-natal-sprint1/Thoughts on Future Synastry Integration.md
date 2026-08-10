# Thoughts on Future Synastry Integration

**Status:** Append-per-slice research journal; not part of bounded Natal v1 scope

This document retains design evidence that may support a later sprint for Synastry
with one or two bounded-time participants. Entries describe implications and
possibilities, not implemented guarantees. Each sprint slice appends its findings
without rewriting earlier observations.

## Slice 1 — Contract and fact-dependency audit

Current Synastry assumes exact participant longitudes for cross-chart aspects and
exact houses for overlays. Bounded Natal v1 therefore rejects Synastry, but the
source artifact should preserve sufficient ranges for later pairwise interval
reasoning.

Useful retained evidence includes:

- circular longitude range and proof quality for each participant body;
- invariant/possible signs and motion states;
- per-body transition windows;
- independent source calculation interval and profile identity for each participant;
- stable participant `source_chart_id` independent of birth-bound corrections; and
- scalar exact values only for an exact-time participant, never midpoint substitutes
  for a bounded participant.

For a pair of longitude intervals, a later Synastry engine may classify an aspect as
`always_in_orb`, `possibly_in_orb`, or `never_in_orb`, with a cross-chart orb range.
The extrema cannot generally be obtained by comparing only interval endpoints,
especially with circular wrap, retrograde motion, or correlated motion within each
participant's birth interval.

If one participant is exact and one bounded, the problem reduces to one scalar
against one interval and should be the first feasibility case. Two independently
bounded participants create a Cartesian product of possible instants and need a
separate proof/performance policy.

House overlays remain unavailable unless the receiving participant has an exact
chart or a future bounded-house contract. Later Synastry output must distinguish
exact cross-aspects, invariant bounded cross-aspects, possible contacts, and omitted
overlays rather than presenting them under today's single relationship vocabulary.

## Slice 2 — Input, normalization, and provenance boundary

Each bounded participant can now carry a deterministic normalized interval and
source-input hash without coupling that identity to display name or
`source_chart_id`. A future Synastry request should retain both participants' native
time-basis/provenance blocks independently before constructing any cross-chart range
evidence.

The 48-hour maximum bounds each participant independently. Two bounded participants
still create a two-dimensional possibility space; a later Synastry profile must not
interpret the pair as one shared time axis unless the source events are actually
correlated.

No pairwise geometry is calculated in this slice. Slice 3's per-body circular ranges,
station evidence, and proof-quality markers will determine whether scalar-versus-
range and range-versus-range Synastry feasibility can proceed without recalculating
the native Natal intervals.
## Slice 3 implications

The generic evaluator demonstrates the exact-versus-bounded first feasibility case:
one participant can be represented as a scalar longitude while the other retains
the bounded range, speed envelope, possible signs, and padded aspect-orb evidence.
Those records should survive Slice 4 even when only invariant categories enter the
canonical graph.

Two bounded participants remain a distinct problem. Their birth intervals are
independent axes, so walking both along the same sample index would be semantically
wrong. A future Synastry sprint needs a Cartesian/extrema strategy and independent
proof identities. The current fail-closed vocabulary and circular unwrapping are
reusable, while the one-dimensional sampling schedule is not sufficient by itself.

## Slice 4 implications

The artifact separates durable participant/body identity from each calculation's
longitude range. That is a useful future Synastry boundary: cross-chart results can
reference stable body IDs while citing each participant's independent uncertainty
registry and calculation profile.

The graph intentionally contains no scalar longitude or orb, so existing Synastry
code must reject it rather than infer exact endpoints. An exact-versus-bounded sprint
can use one uncertainty registry directly; bounded-versus-bounded still requires a
Cartesian proof and must never align the two participants by sample index.

## Slice 5 implications

Synastry and Composite now reject bounded participants at their shared pair-input
boundary, while Davison rejects independently because it requires exact birth event
times. This preserves a clean future split: exact-versus-bounded or
bounded-versus-bounded Synastry may become meaningful, but Composite midpoint and
Davison event construction cannot inherit that support merely because Synastry does.

SPC currently supports exact Synastry vocabulary only. Any future bounded Synastry
projection needs compatibility for both bounded participant evidence and the new
cross-chart relationship proof; accepting bounded Natal objects alone is not enough.
