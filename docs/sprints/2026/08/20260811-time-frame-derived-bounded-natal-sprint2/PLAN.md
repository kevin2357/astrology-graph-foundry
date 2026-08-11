# Time-Frame and Derived-Structure Bounded Natal Expansion Sprint Plan

**Status:** Active; Slice 1 Gate 1 candidate awaiting human review

**Repository:** `astrology-graph-foundry`

**Sequence:** Second of two planned bounded-Natal parity sprints

## Outcome

Complete the bounded-Natal feature assessment for exact-Natal material that depends
on the moving terrestrial chart frame, formula branches, optional external data, or
whole-chart derived structure. Calculate the full uncertainty domain, promote only
invariant semantics, preserve ranges and alternatives as evidence, and ensure every
normal exact-Natal feature family ends with an explicit bounded disposition.

## Entry gate

The coordinate-derived bounded-Natal sprint is implemented, tested, documented,
approved, committed, and published as AGF 0.7.0. Its parity matrix,
normalized semantic predicates, generalized evidence primitives, profile versions,
and exhaustive-oracle harness become inputs to this sprint and may not be silently
redesigned here.

## Current evidence and assumptions

- Exact Natal calculates houses and angles at one UT Julian day before assigning
  bodies to houses and deriving sect, lots, rulers, angle aspects, and graph
  structures.
- Bounded Natal currently marks houses, house placements, angles, sect, and
  angle/sect-dependent lots unavailable as a conservative v1 decision, not because
  invariance is impossible.
- Minute-by-minute exact-chart enumeration can serve as the correctness oracle for
  terrestrial-frame predicates, but continuous safety, house-system failure,
  circular wraparound, and prerequisite propagation require explicit contracts.
- A body may retain invariant house membership even when its exact longitude,
  cusp degrees, Ascendant degree, or zodiac sign varies.
- Lots may branch by sect and yield disconnected possibility regions. Optional
  bodies and fixed stars require pinned external-data provenance or explicit
  unavailability.
- Complete-chart scores and summaries cannot be copied from one representative
  chart; their bounded meaning must be defined separately.

## Scope

- house cusp and angle interval proof for explicitly supported house systems;
- invariant planet/point-in-house membership and possible-house evidence;
- angle, cusp, rulership, and angle-aspect relationships;
- day/night sect classification and dependency propagation;
- lots, Vertex, and other angle/sect-derived points;
- optional bodies and fixed stars under explicit qualified data profiles;
- complete-chart patterns, structures, indexes, scores, claims, and summaries;
- full exact-to-bounded parity qualification, installed-runtime evidence,
  documentation, compatibility handoff, and version/release recommendation.

## Non-goals

- birth-time rectification or probability-weighted guesses;
- representative/noon/midpoint canonical values;
- bounded Transit, Synastry, Composite, Davison, return, or timing implementation;
- SPC, SBE, API, or frontend implementation;
- automatic fallback to a different house system when configured calculation fails;
  or
- release publication without separate explicit approval.

## Slice 1 — Terrestrial-Frame Contract and House-System Audit

Consume Sprint 1's parity matrix and audit Swiss Ephemeris house/angle behavior,
exact-Natal assignment rules, configured systems, circular topology, polar/high-
latitude failure modes, and provider flags. Define whether failure affects one
feature family or the complete artifact, which systems enter the initial profile,
and how continuous proof differs from minute observation.

**Gate 1:** Reviewed supported-system matrix; failure and continuity policy;
high-latitude/polar and wraparound baseline fixtures; unchanged Sprint 1 evidence
contract or explicit approved amendment; full baseline tests; `git diff --check`;
diff/log/result review and human approval.

## Slice 2 — House Cusp and Angle Interval Evidence

Calculate all cusps, Ascendant, Descendant, MC, IC, and supported auxiliary angles
at every valid minute. Produce circular/disjoint ranges, possible/invariant signs,
transition evidence, provider failure classification, and continuous-safety
metadata. Do not promote representative degrees.

**Gate 2:** Cusp/angle crossing, zero wrap, rapid movement, DST-adjacent,
high-latitude, and calculation-failure fixtures; exhaustive-oracle agreement;
schema/provenance/capability tests; performance evidence; full relevant suite;
diff/log/result review and approval.

## Slice 3 — Invariant Body and Point House Membership

Assign eligible bodies and coordinate-derived points to houses at every state using
the exact-Natal rule. Promote invariant house numbers; preserve possible-house sets,
crossing intervals, and cusp evidence references. Support the logically valid case
where sign is variable but house membership is invariant.

**Gate 3:** Every cusp boundary and first/twelfth wrap fixture; intercepted-house and
multiple-system cases; exact-enumeration agreement; deterministic IDs and no dangling
references; directional vocabulary suitable for later Synastry; full graph suite;
diff/log/result review and approval.

## Slice 4 — Angle Relationships, Cusp Signs, and Rulership

Assess planet/point-to-angle aspects, invariant cusp signs, and traditional/modern
house rulership only when their prerequisites remain invariant. Keep angle degrees,
orbs, possible signs, and relationship ranges in evidence. Distinguish invariant
relationship semantics from invariant angle identity.

**Gate 4:** Angle-aspect entry/exit and cusp-ingress fixtures; rulership dependency
tests; normalized-oracle agreement; no prerequisite certainty inversion; exact-Natal
regression; full relevant suite; diff/log/result review and approval.

## Slice 5 — Sect and Dependency Propagation

Classify the complete interval as invariant day, invariant night, variable day/night,
or inconclusive. Propagate that result to sect-dependent dignity, formula, scoring,
and interpretation inputs through explicit prerequisite references.

**Gate 5:** Day, night, sunrise-crossing, sunset-crossing, horizon-boundary, and
calculation-failure fixtures; dependency propagation audit; no dependent fact more
certain than sect; schema and regression tests; full relevant suite; diff/log/result
review and approval.

## Slice 6 — Lots, Vertex, and Branched Calculated Points

Evaluate Part of Fortune, Lot of Spirit, other currently emitted lots, Vertex, and
supported angle/sect-derived points across the domain. Preserve possible formula
identities, disconnected ranges, signs, houses, relationships, and prerequisite
lineage. Promote only semantics invariant across all applicable branches.

**Gate 6:** Day/night formula branch, sunrise/sunset, disconnected-range, cusp/sign
crossing, and unavailable-prerequisite fixtures; exact-oracle agreement; complete
evidence/reference integrity; full relevant suite; diff/log/result review and
approval.

## Slice 7 — Optional Objects and External-Data Profiles

Audit configured asteroids, Chiron/file-dependent bodies, fixed stars, Swiss
Ephemeris data files, and star catalogs. Define optional qualified profiles with
provider/library/data identities and hashes. When a profile or resource is absent,
emit explicit unavailability without invalidating independent bounded features.

**Gate 7:** No-file baseline remains valid; pinned-data controlled fixtures;
missing/corrupt/version-mismatch classification; reproducible data manifest and
hashes; no accidental network/data lookup; full relevant suite; diff/log/result
review and approval.

## Slice 8 — Complete-Chart Structures, Scores, and Parity Closure

Review aspect patterns, dispositorship/rulership networks, elemental/modal balance,
angularity, emphasis, structural scores, indexes, claims, and summaries. For each,
adopt an invariant category, sampled complete-chart range, possibility set,
invariant-subgraph result, or explicit unavailability. Run complete parity and
installed qualification, update downstream handoff and versioning, and make a
release recommendation.

**Gate 8:** Every exact-Natal feature has a final bounded disposition; complete-chart
versus invariant-subgraph semantics are explicit; exhaustive oracle equivalence over
diverse intervals; deterministic replay; installed Linux live/saved tests; packaged
resource/data manifests; full suite; JSON/schema/Markdown/link validation; artifact
hashes and cleanup; clean diff/worktree review; consolidated result; human approval
and approved commit. No tag/publication without separate authorization.

## Controls and safety rules

- Enforce the Sprint 1 entry gate and preserve its accepted evidence semantics.
- Evaluate the entire normalized uncertainty domain; never infer invariance from
  endpoints alone.
- Do not silently fall back between house systems, providers, formulas, or data
  profiles.
- A dependent fact cannot be more certain than its least-certain prerequisite.
- Treat circular/disconnected possibilities honestly; never collapse them into a
  misleading scalar envelope.
- Never emit representative cusp, angle, lot, house, orb, score, or summary values as
  canonical bounded facts.
- Distinguish expected variability, unavailable configuration, unsupported
  semantics, and provider/calculation failure.
- Prefer deterministic no-file fixtures before optional-data and live calculation.
- Installed tests run outside the source checkout with exact dependency artifacts.
- At every gate: tests, `git diff --check`, actual diff review, append-only LOG,
  slice result, findings report, human approval, then commit.
- Preserve compact evidence and hashes; clean bulky chart corpora, environments,
  build trees, data copies, caches, and generated packages.
- Do not modify downstream repositories or publish/tag/use credentials without
  explicit approval.

## Dependencies

- completed and committed coordinate-derived bounded-Natal Sprint 1;
- accepted generalized uncertainty evidence and predicate contracts;
- exact-Natal house, angle, sect, lot, and structure behavior;
- pinned pyswisseph/Swiss Ephemeris provider profile;
- explicit decision before introducing any external ephemeris/star data; and
- later independent SPC/SBE compatibility work for newly promoted vocabulary.

## Exit criteria

- Supported house systems and failure behavior are explicit and tested.
- Cusp/angle evidence covers the complete interval without representative precision.
- Invariant house placements, angle relationships, cusp signs, and rulership promote
  only with complete prerequisite evidence.
- Sect and all dependent facts preserve their uncertainty lineage.
- Lots and other branched calculated points retain formula and possibility evidence.
- Optional features carry exact data provenance or explicit unavailability.
- Every normal exact-Natal feature family has an accepted bounded disposition.
- Complete-chart structures and scores state whether they describe candidate-chart
  ranges or the invariant subgraph.
- Exhaustive exact-chart oracle and specialized bounded output agree.
- Exact Natal remains compatible or has an approved versioned migration.
- Full tests and installed qualification pass; docs, schemas, profiles, versions,
  handoffs, and release recommendation are complete.
- Every slice ends at a reviewed, approved, committed boundary.

## Deferred work

- bounded Transit, Synastry, Composite, Davison, returns, and timing;
- SPC/SBE/API/frontend enablement;
- rectification and probability-weighted uncertainty;
- unsupported house systems or optional-data profiles; and
- immutable release publication unless separately approved.
