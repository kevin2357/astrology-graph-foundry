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

## Slice 6 implications

The installed wheel proof establishes a portable participant artifact with stable
IDs, immutable source/configuration hashes, and resolvable uncertainty evidence.
Those are sufficient inputs for a future feasibility sprint without reopening the
Natal calculation contract.

Release sequencing remains important: AGF 0.7.0 supplies participant evidence, but
SPC and SBE support does not make bounded Synastry automatic. Exact-versus-bounded
and bounded-versus-bounded relationship evidence still need distinct semantics,
qualification fixtures, and compatibility versions.

## Coordinate-derived parity sprint qualification implications

The completed follow-on sprint supplies schema-qualified circular/scalar ranges,
transform prerequisites, counterexamples, and stable evidence references through
the 48-hour maximum. That materially lowers the cost of an exact-versus-bounded
Synastry prototype: the bounded participant's Natal evidence can remain immutable
and the new cross-chart engine can own only the scalar-versus-range proof.

It does not collapse the bounded-versus-bounded problem. Each participant retains
an independent minute domain and calculation identity; aligning minute index A with
minute index B would discard most valid combinations. Qualification also confirms
that wider domains increase conditional evidence even while canonical row counts
fall, so a Cartesian feasibility sprint needs explicit evaluation budgets and
compact counterexample/evidence policies before it promises 48-by-48-hour support.

## Terrestrial-frame Sprint 2, Slice 1 implications

House overlays must preserve the receiving participant's provider-defined cusp
numbering and house-system identity. Deriving house 1 by rotating toward the
Ascendant corrupts valid Whole Sign and other systems, so future Synastry must
consume labeled cusp evidence rather than infer the frame from angles.

A receiving participant's failed Placidus frame should make overlays inconclusive
without discarding cross-chart body-aspect evidence. Whole Sign may be configured as
a polar-capable frame, but cannot be an automatic fallback because that changes the
natal calculation contract.

## Terrestrial-frame Sprint 2, Slice 2 implications

The receiving participant can now contribute a labeled frame evidence registry to a
future overlay calculation. Exact-versus-bounded Synastry can pair one exact body
longitude with these possible cusp intervals; bounded-versus-bounded overlays still
require independent participant domains and cannot align sample indexes.

## Terrestrial-frame Sprint 2, Slice 3 implications

Future overlays now have the exact receiving-chart primitive they need: invariant
house numbers when proven, and possible-house sets with transition witnesses when
not. An exact-versus-bounded overlay can preserve that distinction without
recalculating the natal participant. Two bounded participants still require a
Cartesian cross-chart proof for aspects, even though each receiving frame's native
membership evidence is independently reusable.
