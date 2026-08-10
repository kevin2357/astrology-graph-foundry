# Thoughts on Future Transit Integration

**Status:** Append-per-slice research journal; not part of bounded Natal v1 scope

This document retains design evidence that may support a later sprint for transits
to bounded natal placements. Entries describe implications and possibilities, not
implemented guarantees. Each sprint slice appends its findings without rewriting
earlier observations.

## Slice 1 — Contract and fact-dependency audit

Current Transit and Transit Period pipelines consume one exact natal target
longitude and often natal houses. Bounded Natal v1 therefore rejects those paths,
but its evidence should avoid foreclosing a later interval-aware transit model.

Retain per body:

- circular natal longitude range, including explicit zodiac-wrap representation;
- possible and invariant signs;
- speed/motion-state range and station windows;
- transition windows and numerical tolerances;
- calculation interval and proof-profile version; and
- whether extrema are proven or merely sampled bounds.

Retain per invariant or conditional natal aspect:

- aspect type;
- minimum and maximum orb over the birth interval;
- intervals where the aspect is inside/outside allowed orb;
- closest-approach window; and
- applying/separating status only when proven invariant.

A future transit contact can be modeled as separation between one known transit
longitude and a natal longitude interval. That may support `always_in_orb`,
`possibly_in_orb`, and `never_in_orb` classifications. It cannot safely reuse the
current scalar-orb relationship or exact-event solver.

House transits remain unavailable without a separate bounded-house design. A later
Transit sprint should begin with body-to-body contacts only and treat every emitted
contact as interval evidence tied to both the natal uncertainty profile and transit
calculation profile.

The bounded package must retain compact ranges and transition evidence even when the
bounded Natal canonical graph promotes only categorical invariant facts. Discarding
those ranges would force a future Transit implementation to recalculate or infer
from lossy graph output.

## Slice 2 — Input, normalization, and provenance boundary

The normalized birth-time basis now preserves both local and UTC interval bounds,
boundary semantics, elapsed duration, IANA timezone, coordinates, and a versioned
source-input hash. A future Transit cache or proof must include that native identity;
two equal longitude ranges calculated under different time bases or normalization
policies are not automatically interchangeable.

Inclusive caller bounds versus half-open whole-local-day bounds are explicit. A
future contact solver must respect the stored boundary policy when deciding whether
an exact threshold contact at the edge is possible.

No longitude, speed, extrema, or transition evidence exists yet; Slice 2 only
ensures the input interval needed to calculate it is reproducible. Slice 3 should
retain circular range and proof-quality fields outside the canonical graph even when
the corresponding sign fact is invariant.
## Slice 3 implications

The interval engine now retains the minimum source evidence a later scalar-transit
versus bounded-natal classifier needs: an unwrapped natal longitude range, speed and
motion-state range, possible signs, aspect type possibilities, padded orb range,
proof profile, interval bounds, evaluation count, and explicit inconclusive status.

The one-minute grid and speed envelope must not automatically become the Transit
contract. A fast transit evaluated against a natal interval has two independent
motion bounds, and a future sprint should either reuse the generic pair evaluator
with both clocks explicit or define a stronger two-dimensional proof. Importantly,
provider failure and budget exhaustion are already distinct from a merely
conditional transit contact.
