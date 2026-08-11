# Near-Term Engineering Outlook

**Status:** Living, non-normative planning context

**Authority:** Astrology Graph Foundry repository concerns only

This document preserves near-term engineering opportunities that are important
enough to remain visible but are not yet approved sprint commitments. Normative
behavior remains in the schemas, contract documentation, accepted ADRs, and released
artifacts.

## Decouple AGF from Semantic Projection Core

### Current state

AGF currently declares `semantic-projection-core>=0.10.0,<0.11` as a mandatory
distribution dependency. `projection_adapter.py` imports the `semantic_projection`
runtime directly, `doctor` reports an SPC compatibility line, and AGF's installed
qualification includes AGF-to-SPC projection tests.

This is stronger coupling than the ownership model requires. AGF calculates and
serializes canonical astrology artifacts. SPC consumes compatible canonical
artifacts and owns projection. Neither core runtime needs to import or install the
other merely to perform its own work.

The current dependency appears to be residue from projection's earlier development
inside Foundry plus the convenience of retaining an AGF-owned projection adapter
after the repository split. Cross-system compatibility tests are valuable, but they
do not require a production dependency in either direction.

### Intended direction

- AGF's base installation should calculate, validate, serialize, reload, and inspect
  its artifacts without SPC installed.
- SPC should consume AGF artifacts through versioned schemas and documented wire
  contracts without importing AGF.
- Projection contexts, target ontologies, projection request identity, and projected
  artifacts remain SPC/downstream-owned.
- Cross-repository qualification should continue against exact immutable artifacts
  in an integration harness or consumer environment.
- A convenience command may orchestrate both packages, but it should live in an
  explicitly optional integration layer rather than making either core package a
  runtime dependency of the other.

### Sprint questions

1. Should the existing adapter move to SPC, a small neutral bridge package, or an
   orchestration repository?
2. Is a temporary AGF `projection` extra useful during migration, or would it
   prolong an ownership ambiguity that should be removed directly?
3. Which current public AGF Python functions and CLI routes expose projection, and
   what deprecation/versioning policy do their users require?
4. How should `doctor` change so saved and live AGF readiness are wholly independent
   of SPC while optional integration diagnostics remain available elsewhere?
5. Which tests belong in AGF as schema/fixture export tests, which belong in SPC as
   consumer tests, and which belong in cross-project qualification?
6. Does removing the mandatory dependency warrant AGF 0.8.0 because public adapter
   imports or CLI behavior change, even though the canonical artifact contracts do
   not?

### Acceptance direction

A clean AGF base wheel must install and pass saved/live workflows without SPC. A
clean SPC wheel must install and project a compatible saved fixture without AGF.
The integration gate must then install the two exact artifacts independently and
prove their wire compatibility, identity preservation, and evidence preservation.

## Evaluate invariant house placements for bounded Natal

### Current state

Bounded Natal v1 classifies all houses, house placements, angles, sect, and
angle-dependent lots as unavailable. This was a deliberately conservative sprint
boundary, not proof that every planet's house necessarily changes across every
bounded interval.

The current minute-by-minute evaluator calculates body positions only. Exact Natal
calculates house cusps and angles for one instant and assigns bodies to houses from
those cusps. Extending bounded proof therefore requires evaluating a moving cusp set
at every valid minute and proving categorical membership across the complete
interval.

### Why this needs a separate slice

House membership is more involved than testing whether a body's zodiac sign stays
constant:

- both the body and every relevant cusp move;
- the first/last-house boundary wraps through zero degrees;
- cusp ordering and intercepted-sign behavior depend on the selected house system;
- high-latitude calculations can fail or become unsupported for some systems;
- an endpoint-only result can miss an interior boundary crossing;
- angles are themselves calculation outputs, but invariant planet-in-house
  membership is a separate categorical claim; and
- whole-sign houses still depend on the time-sensitive rising sign even though their
  boundaries are sign-aligned.

Minute-by-minute evaluation is nevertheless a promising and conceptually direct v1
proof strategy. For each successful instant, calculate the configured house system,
classify each eligible body into a house using the same exact-Natal rule, and promote
only a body whose house number is identical at every evaluation. Preserve cusp
ranges, observed house memberships, failures, and the proof profile as uncertainty
evidence; do not promote representative cusp degrees or an estimated Ascendant.

### Feasibility and contract questions

1. Which house systems are initially supported, and what happens when Swiss
   Ephemeris cannot calculate one anywhere inside the interval?
2. Should a single failed minute make all house evidence inconclusive, or only the
   affected house-related family?
3. Are invariant body-in-house facts useful without canonical angle or cusp objects,
   and can existing graph vocabulary express that distinction unambiguously?
4. Should house rulership be promoted when a cusp sign is invariant even if its
   degree is not, or deferred beyond body membership?
5. How are bodies whose own sign is variable but whose house membership is invariant
   represented?
6. What fixtures cover cusp crossings, zero-degree wraparound, intercepted houses,
   DST-adjacent intervals, polar latitudes, and multiple house systems?
7. Which future SPC vocabulary projects an invariant house placement while
   preserving the fact that its cusp and angle geometry is bounded rather than
   exact?

This extension should be additive to bounded Natal rather than weakening the v1
certainty rule. Until implemented and versioned, all bounded house features remain
explicitly unavailable.
