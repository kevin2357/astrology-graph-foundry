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
