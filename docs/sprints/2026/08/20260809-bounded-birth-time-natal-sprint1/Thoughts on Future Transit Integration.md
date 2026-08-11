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

## Slice 4 implications

The bounded artifact preserves all body and aspect ranges in an addressable
uncertainty registry even though only invariant categories enter its canonical
graph. A future Transit implementation should consume those range records directly;
it must not treat `bounded_natal_body` as an exact transit target. Accordingly, the
initial capability block disables exact longitude aspects and semantic activation.

Stable source-scoped bounded body IDs give later transit results durable endpoints,
while calculation provenance identifies which interval/proof profile supplied the
range. Correcting bounds can therefore retain chart lineage but must produce new
calculation and transit-contact evidence.

## Slice 5 implications

All current `TransitableChart` consumers now reject bounded Natal through one shared
guard. A future Transit sprint therefore has an intentional opening point: it should
add a new bounded capability/interface rather than relax the exact interface or
special-case one pipeline. The present rejection covers transit periods, returns,
eclipse target activation, and profections consistently.

Current SPC compatibility does not alter this conclusion. Even after SPC can project
bounded categorical facts for authoring, timing remains an AGF calculation contract
that needs range-versus-scalar evidence and its own acceptance tests.

## Slice 6 implications

Installed qualification proves the bounded evidence survives a real wheel/runtime
boundary and that saved mode can inspect it without pyswisseph. A future Transit
worker can therefore separate stored-source consumption from live recomputation and
pin the bounded proof-profile/configuration hashes in its own contact cache key.

AGF 0.7.0 publication alone will not enable Transit. The exact `TransitableChart`
guard remains binding until a separately versioned range-aware interface and
acceptance matrix are implemented.

## Coordinate-derived parity sprint qualification implications

The completed follow-on sprint qualifies portable longitude, coordinate-speed,
declination, antiscia, harmonic, ordinary-aspect, derived-aspect, and declination-
relationship evidence across 4/24/48-hour domains. A future Transit feasibility
sprint can therefore consume a versioned evidence registry rather than rebuild
Natal coordinates, but it still needs a two-clock contact proof: transit time and
possible natal time are independent axes.

Maximum-duration qualification showed the expected monotonic semantic pressure:
canonical invariant relationships fell as conditional/variable evidence grew. A
timing API must therefore budget by proof domain and retained evidence surface, not
assume a bounded artifact is smaller merely because it contains fewer canonical
facts. Structural family groups may help downstream selection, but are not contact
probabilities or timing weights.

## Terrestrial-frame Sprint 2, Slice 1 implications

House-system identity belongs in any later transit-house proof. Provider success is
system- and latitude-dependent, Whole Sign has piecewise frame jumps at Ascendant
sign ingress, and some legitimate systems do not identify cusp 1 with the
Ascendant. A future transit engine must consume labeled cusp evidence and must not
silently substitute a polar-capable system after Placidus failure.

Family-scoped failure also supports phased Transit behavior: a failed terrestrial
frame can make house contacts inconclusive while independently proven contacts to
bounded celestial bodies remain available.

## Terrestrial-frame Sprint 2, Slice 2 implications

Transit-house feasibility now has portable inputs: seventeen labeled frame records,
circular ranges, transition witnesses, a pinned system, and feature-scoped failure.
Future work should reference those registry records rather than recompute cusps or
read a representative frame. Placidus and Whole Sign must remain distinct cache and
calculation profiles.

## Terrestrial-frame Sprint 2, Slice 3 implications

Invariant natal-house membership can now be consumed directly as a categorical
fact, while variable memberships retain possible houses and cusp-transition
evidence. Future Transit must still distinguish “transiting body enters a possible
natal house” from an invariant natal placement; the new membership registry is an
input, not permission to enable today's exact house-transit interface.

## Terrestrial-frame Sprint 2, Slice 4 implications

Invariant angle identities and body-to-angle aspects now have portable evidence,
but exact angle degrees remain unavailable. Future Transit must classify contacts
to angle ranges rather than reuse exact event solvers.

## Terrestrial-frame Sprint 2, Slice 5 implications

Sect is now portable prerequisite evidence rather than a recalculated downstream
guess. Transit techniques that branch on sect must cite this record and remain
conditional when the natal interval crosses the horizon.

## Terrestrial-frame Sprint 2, Slice 6 implications

Fortune and Spirit now expose disconnected formula-branch ranges rather than one
representative degree. Future Transit contact proofs must evaluate every branch and
may promote a contact only when the same predicate holds over all applicable
branches. An invariant house is independently reusable even when a lot's sign or
degree range remains variable. Vertex house evidence is likewise reusable without
reconstructing the terrestrial frame.
