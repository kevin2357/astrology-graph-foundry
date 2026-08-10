# Slice 4 - Bounded Artifact, Canonical Graph, and Capabilities

**Status:** Gate-ready for review; uncommitted

**Starting boundary:** `b6e9a9b`

## Outcome

Validated bounded input now produces a distinct `bounded_natal_dataset` package and
`bounded_canonical_astrology_graph`. Only invariant sign, motion, sign-only dignity,
and body-aspect categories enter the canonical graph. Exact longitude, exact degree,
exact orb, strength, and application values are prohibited from that layer. Their
ranges and classifications remain in an addressable uncertainty-evidence registry.

## Contract boundary

- Bounded Natal Dataset schema: `1.0.0`.
- Bounded canonical graph version: `1.0.0`.
- Bounded calculation provenance contract: `1.0.0`.
- Exact Birth Data, Natal Dataset, canonical graph 1.3.0, and exact
  `TransitableChart` behavior remain unchanged.
- Bounded objects use `bounded_natal_body`; invariant relationships use
  `BOUNDED_INVARIANT_ASPECT`.
- The existing finalizer recognizes bounded Natal as a chart identity family,
  scopes local IDs beneath `source_chart_id`, migrates endpoints, and remains
  idempotent.
- Bounded artifacts do not advertise the exact `TransitableChart` interface.

## Uncertainty and omission semantics

Every configured ordinary body and body pair remains represented in
`uncertainty_assessment`, even when it cannot enter the canonical graph. Canonical
rows carry resolvable `uncertainty_evidence_ref` values. Houses, house placements,
angles, sect, lots, deferred techniques, and prohibited representative longitudes
all receive explicit feature dispositions rather than silently disappearing.

The reduced capability block explicitly disables exact longitudes, ordinary
longitude aspects, house/angle transits, semantic graph activation, returns, and
annual profections. This prevents exact-only timing consumers from inferring support
from the mere existence of canonical objects.

## Findings

The first artifact test exposed that shared identity finalization scopes only the
recognized local Natal namespace. Bounded IDs initially used an unrelated prefix and
therefore remained unscoped. The fix retains distinct bounded object vocabulary but
uses the Foundry-local `natal:bounded:*` pre-finalization namespace. Finalized IDs now
inherit caller identity exactly like exact Natal IDs, and relationship endpoints
migrate with them.

The semantic identity classifier also needed to recognize `bounded_natal_dataset`
as chart identity rather than invocation identity. Otherwise finalization metadata
could influence the sensor identifier and defeat idempotence. The bounded family now
uses stable chart identity while calculation identity remains separately bound to
the birth interval and proof profile.

## Gate evidence

- Focused artifact/input/resource/engine suite: **36 passed in 2.36 seconds**.
- Final full suite: **209 passed in 17.54 seconds**.
- Real Docker Linux/Python 3.11 unknown-time package: 11 invariant objects, 13
  invariant relationships, 12 body assessments, and 66 aspect assessments in 0.655
  seconds.
- The real graph contained no exact object degrees or relationship orbs, had no
  dangling endpoints, disabled exact-longitude capability, and produced graph hash
  `c1d8bdaed9b9ede73e159b60cde8dbb77068b6d53cd36bb9dc527c0a709c02c4`.
- Compact evidence: [`bounded-artifact-summary.json`](bounded-artifact-summary.json).

## Gate assessment

Slice 4 establishes the separate public artifact family without changing exact
Natal semantics or laundering a midpoint/noon calculation into source fact. The
bounded vocabulary is intentionally not yet accepted by SPC; that compatibility and
all other package-family rejection checks belong to Slice 5.
