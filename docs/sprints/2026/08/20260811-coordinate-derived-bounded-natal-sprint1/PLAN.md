# Coordinate-Derived Bounded Natal Expansion Sprint Plan

**Status:** Slice 7 Gate 7 pending review; implementation complete

**Repository:** `astrology-graph-foundry`

**Sequence:** First of two planned bounded-Natal parity sprints

## Outcome

Expand bounded birth-time Natal artifacts to assess and preserve the useful
coordinate-derived feature families emitted by exact Natal calculation without yet
depending on houses, angles, sect, branching lots, or optional external ephemeris
data. Promote only facts proven invariant across the complete normalized birth-time
domain; retain ranges, alternatives, transitions, and counterexamples as structured
uncertainty evidence.

## Current evidence and assumptions

- AGF 0.7.0 candidate bounded Natal evaluates every valid minute, applies
  speed-derived safety envelopes, and currently covers ordinary body signs, motion,
  sign dignity, longitude ranges, and body-to-body aspects.
- The exact Natal path additionally emits latitude, declination, declination
  aspects, antiscia, harmonics, houses, angles, sect, lots, optional bodies, fixed
  stars, and broader derived structures.
- The four-hour Kevin artifact retained all twelve configured body signs and 21
  invariant aspects from 241 inclusive minute states, demonstrating that exhaustive
  domain intersection can preserve substantial chart material.
- Complete exact-chart enumeration is a useful correctness oracle, but canonical
  comparison must operate on normalized semantic predicates rather than serialized
  rows containing exact degrees, timestamps, or invocation-specific metadata.
- One min/max interval is not always an honest possibility representation. Circular
  wraparound, branching, and transformed positions may require disjoint ranges.
- SPC and SBE bounded consumption are separate downstream sprints. This sprint owns
  only AGF source calculation, evidence, schemas, capabilities, and handoff facts.

## Scope

- exact-to-bounded feature/disposition inventory;
- reusable circular, disjoint, scalar, categorical, dependency, and counterexample
  evidence primitives;
- richer ordinary-body coordinate and motion evidence;
- coordinate-derived transforms such as antiscia and configured harmonics;
- declination, parallel/contraparallel, and expanded coordinate-derived
  relationships;
- carefully delimited invariant-subgraph structural material;
- exhaustive exact-chart oracle fixtures and installed-runtime qualification; and
- documentation, schema/profile versions, migration, and downstream handoff.

## Non-goals

- houses, cusps, angles, planet-in-house membership, sect, lots, Vertex, or other
  moving terrestrial-frame features;
- optional file-dependent bodies or fixed-star catalogs;
- Transit, Synastry, Composite, Davison, returns, or timing support;
- SPC, SBE, API, or frontend implementation;
- rectification, representative-time values, probability estimates, or inferred
  exact positions; or
- release publication without a separate explicit decision.

## Slice 1 — Exact-to-Bounded Parity and Dependency Inventory

Trace every exact Natal field, canonical object/relationship, structural-evidence
row, capability, registry, score, and provenance input to its calculation
prerequisites. Produce a machine-readable parity matrix classifying each feature as
already bounded, coordinate-derived Sprint 1 scope, terrestrial/branching Sprint 2
scope, optional-data-dependent, downstream-owned, or inappropriate for bounded
canonical promotion. Define normalized semantic predicates used by the exhaustive
oracle.

**Gate 1:** Reviewed parity/dependency matrix; explicit Sprint 1/Sprint 2 boundary;
baseline exact and bounded fixtures; focused and full current tests; JSON/Markdown
validation; `git diff --check`; diff/log/result review; human approval before commit.

## Slice 2 — Generalized Uncertainty Evidence Primitives

Define and implement versioned representations for circular and disjoint ranges,
scalar ranges, categorical possibility sets, prerequisite references, transition
samples, counterexamples, and `invariant`/`conditional`/`variable`/`unavailable`/
`inconclusive` classification. Specify continuous-safety evidence independently of
sampling frequency and migrate existing bounded evidence without losing exact 0.7.0
meaning.

**Gate 2:** Schema-valid wraparound and disconnected-range vectors; deterministic
serialization and IDs; prerequisite/counterexample integrity; backward-compatibility
decision; no precision laundering; focused evidence tests; full relevant suite;
diff/log/result review and approval.

## Slice 3 — Rich Body Coordinate, Motion, and Dignity Evidence

Assess longitude, latitude, declination, available speeds, direct/retrograde/
stationary state, possible signs, and all non-sect-dependent dignity components for
each configured ordinary body. Promote only invariant categorical properties while
keeping numeric ranges in evidence. Distinguish unsupported provider fields from
variable or failed calculation.

**Gate 3:** Stable, crossing, station, wraparound, missing-field, and provider-failure
fixtures; exhaustive-oracle agreement; evidence coverage for every configured body;
schema/capability/provenance tests; performance evidence; full calculation suite;
diff/log/result review and approval.

## Slice 4 — Coordinate-Derived Points and Transforms

Add bounded assessment for antiscia, contra-antiscia, and currently configured
harmonic positions. Define source identity and prerequisite lineage for derived
objects, protect circular multiplication and repeated wraparound, and suppress any
transform whose complete-domain result cannot be represented honestly.

**Gate 4:** Antiscia boundary and multiple-harmonic wrap fixtures; exact-enumeration
agreement; no stale derived reference after filtering; deterministic IDs/order;
schema and regression tests; full relevant suite; diff/log/result review and
approval.

## Slice 5 — Expanded Coordinate-Derived Relationships

Add declination parallels/contraparallels, antiscia and harmonic relationships, and
richer ordinary-aspect evidence. Decide continuous presence, invariant absence,
possible type sets, and applying/separating semantics only where coordinate evidence
can prove them without houses, angles, or sect.

**Gate 5:** Relationship entry/exit, type-change, leave-and-return, declination
boundary, and application-state fixtures; normalized-oracle agreement; complete
endpoint/evidence integrity; no scalar orb laundering; full graph suite;
diff/log/result review and approval.

## Slice 6 — Invariant-Subgraph Structural Material

Audit exact structural evidence, scores, indexes, claims, and summaries. Implement
only structures whose bounded meaning is accepted and clearly distinguish a result
derived from the invariant subgraph from a range observed over complete candidate
charts. Defer any score that cannot preserve that distinction.

**Gate 6:** Reviewed semantic definition for every retained structure; sampled
complete-chart versus invariant-subgraph fixtures; no exact score reused under a
different meaning; evidence/claim lineage tests; full relevant suite; diff/log/result
review and approval.

## Slice 7 — Oracle Qualification, Documentation, and Version Decision

Generate exact charts across four-hour, whole-day, and maximum-duration reference
intervals and compare their normalized intersection with specialized bounded output.
Qualify the installed wheel on Linux/Python 3.11 with pinned live dependencies.
Update consumer guidance, parity inventory, limitations, profile/schema versions,
and release recommendation.

**Gate 7:** Exact-oracle equivalence; deterministic replay; controlled live and
saved-only installed tests; packaged-resource manifest; full suite; JSON/schema/
Markdown/link validation; performance and artifact hashes; clean diff/worktree
review; consolidated result; human approval and approved commit. No tag or
publication without separate authorization.

## Controls and safety rules

- Begin every slice from an approved committed boundary and preserve unrelated work.
- Treat exhaustive minute enumeration as the reference oracle, not permission to
  ignore between-minute continuity hazards.
- Never intersect raw serialized graph rows; compare versioned normalized semantic
  predicates.
- Never place representative, midpoint, endpoint, or sampled scalar precision in a
  canonical bounded fact.
- A dependent fact cannot be more certain than any prerequisite.
- Calculation failure, disabled configuration, unsupported provider data,
  unavailable semantics, and ordinary variability remain distinct.
- Prefer deterministic fixtures before controlled live calculation.
- Installed-runtime qualification must occur outside the source checkout.
- At every gate: tests, `git diff --check`, actual diff review, append-only LOG,
  slice result, findings report, human approval, then commit.
- Preserve compact evidence and hashes; remove environments, build trees, expanded
  exact-chart corpora, caches, and duplicate packages after qualification.
- Do not modify SPC, SBE, API, project, or frontend implementation in this sprint.
- Do not tag, push, publish, or use credentials without explicit approval.

## Dependencies

- completed bounded-Natal v1 implementation at AGF commit `00e6c2a`;
- current exact Natal calculation and canonical graph contracts;
- pinned pyswisseph/Swiss Ephemeris Moshier live profile;
- accepted evidence-schema and compatibility version decisions at early gates; and
- Sprint 2 consuming the final parity matrix and evidence primitives from this
  sprint rather than redesigning them silently.

## Exit criteria

- Every exact Natal feature has an explicit disposition in the parity matrix.
- Generalized uncertainty evidence represents circular/disjoint ranges,
  possibilities, prerequisites, transitions, and counterexamples deterministically.
- Rich ordinary-body, declination, antiscia, harmonic, and accepted relationship
  features are completely assessed across the interval.
- Canonical output contains only invariant categorical facts with resolvable
  evidence and dependency lineage.
- Specialized bounded output matches the normalized intersection of exhaustive
  exact-chart oracle fixtures.
- Exact Natal contracts remain unchanged or have an approved versioned migration.
- Houses, angles, sect, lots, optional-file features, and complete terrestrial-frame
  synthesis remain explicitly deferred to Sprint 2.
- Full tests and installed Linux controlled-live qualification pass.
- Docs, schemas, versions, consumer handoff, and release recommendation are complete.
- All slices end at reviewed, approved, committed boundaries.

## Deferred work

- all Sprint 2 terrestrial-frame and branching-derived features;
- bounded Transit and Synastry;
- downstream projection and authoring enablement;
- probabilistic/rectification features; and
- immutable release publication unless separately approved.
