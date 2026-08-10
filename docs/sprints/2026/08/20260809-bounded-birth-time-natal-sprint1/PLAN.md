# Bounded Birth-Time Natal Sprint Plan

**Status:** Proposed for review; planning and documentation only so far

**Repository:** `astrology-graph-foundry`

## Outcome

Implement and qualify an uncertainty-aware Natal mode that accepts exact, bounded,
or whole-local-day birth-time bases; proves which source facts remain invariant
throughout the normalized interval; emits structured uncertainty evidence and
reduced capabilities; and prevents representative-time values from becoming false
exact canonical facts.

## Current evidence and assumptions

- AGF 0.6.0 accepts one exact `birth_local` string and attaches `ZoneInfo` directly;
  it has no bounded civil-time contract.
- Live Natal calculates one Julian day, houses, angles, bodies, sect, lots,
  dignities, antiscia, harmonics, declinations, and exact aspects before graph
  compilation.
- Current graph objects and `TransitableChart` capabilities primarily assume exact
  longitude-bearing objects.
- Swiss Ephemeris supports arbitrary UT position/house calls and returns longitudinal
  speed, but AGF must own the interval proof/classification algorithm.
- AstroWoof currently documents warned local noon as implemented MVP behavior. The
  accepted successor direction is bounded invariant evidence, not silent noon.
- SPC, SBE, API, and UI support is not assumed. Cross-repository changes require
  their own authority and compatibility gates.

## Scope

- birth-time precision contract and civil-time normalization boundary;
- interval calculation and invariant/conditional classification;
- structured uncertainty evidence;
- canonical graph and capability semantics for bounded facts;
- provenance, hashing, schemas, CLI/Python interfaces, fixtures, and migration;
- installed AGF-to-SPC compatibility evidence; and
- AGF and authorized cross-project documentation.

## Non-goals

- astrological rectification or guessing an exact birth time;
- product warning copy, payment policy, UI design, or database implementation;
- complete interval-aware houses, angles, lots, returns, or timing techniques in the
  first release;
- hiding uncertainty only at rendering time; or
- rewriting historical warned-noon artifacts.

## Slice 1 — Contract and Fact-Dependency Audit

Trace exact-time assumptions through birth schemas, CLI/Python entry points,
providers, Natal calculation, graph compilation, claims/evidence, provenance,
`TransitableChart`, projection adapters, fixtures, and every package family. Produce
a fact-dependency matrix classifying exact, bounded, invariant-capable, conditional,
and initially unavailable features. Decide names, modes, bounds, inclusivity,
maximum duration, zero-width behavior, and civil-time responsibility.

**Gate 1:** Reviewed contract decision, dependency/capability matrix, version-impact
proposal, focused baseline tests, full current suite, `git diff --check`, diff/log/
result review, and human approval before commit.

## Slice 2 — Input, Normalization, and Provenance Boundary

Implement a tagged exact/bounded/unknown-day model, schemas, CLI/Python surfaces,
validation, UTC normalization, DST fold/gap behavior, normalized source hashing, and
calculation-profile fields. Preserve legacy exact calls and keep API-derived warned
noon distinguishable from genuine bounds.

**Gate 2:** Boundary fixtures for exact, bounded, unknown day, DST-short/long days,
cross-midnight intervals, invalid/inverted bounds, and deterministic hashes; schema
and CLI tests; full relevant suite; whitespace/diff review; result and approval.

## Slice 3 — Interval Evaluation and Classification Engine

Add provider-independent feature classification above point calculations. Implement
conservative adaptive evaluation, circular longitude ranges, ingress and station
detection/refinement, aspect-boundary/extrema handling, explicit tolerances, and
inconclusive-proof behavior. Initially cover configured ordinary bodies, signs,
motion state, sign-dependent dignity, and body-to-body aspects.

**Gate 3:** Machine-readable vectors for stable/variable Moon, ingress, station,
aspect entry/exit, wraparound, multiple-crossing threat cases, provider failure, and
repeat determinism; algorithm review; performance evidence; full calculation tests;
diff/log/result review and approval.

## Slice 4 — Bounded Artifact, Canonical Graph, and Capabilities

Define and implement `birth_time_basis`, uncertainty assessment, compact calculation
evidence, bounded object/relationship vocabulary, stable IDs, invariant-only graph
promotion, and reduced capability advertisement. Suppress houses, angles, sect, and
dependent lots initially. Ensure omitted facts remain explainable and failures remain
distinct.

**Gate 4:** Schema-valid artifacts proving no midpoint/noon precision laundering,
no dangling references, deterministic IDs/order, uncertainty coverage for every
excluded configured feature, exact-package regression, serialization/reload, full
graph/evidence tests, diff/log/result review and approval.

## Slice 5 — Downstream and Package-Family Compatibility

Qualify the bounded source boundary through the exact supported SPC artifact. Audit
SBE eligibility expectations and every relationship/temporal consumer; implement
only compatibility that belongs in AGF and publish explicit rejections/capabilities
elsewhere. Confirm source identity is independent of narrowed/corrected bounds and
that projection context remains downstream-owned.

**Gate 5:** Installed AGF-to-SPC projection proof, consumer capability matrix,
exact-only rejection tests, saved/reloaded projection fixtures, source/evidence
preservation, full relevant suite, diff/log/result review and approval.

## Slice 6 — Migration, Qualification, Documentation, and Release Decision

Document exact versus bounded versus legacy warned-noon behavior, consumer migration,
provenance/cache keys, limitations, and API handoff. Run installed-wheel deterministic
and controlled-live qualification in the intended production runtime. Decide package,
schema, graph, profile, and compatibility versions and whether publication requires a
separate release-engineering sprint.

**Gate 6:** Complete installed tests, deterministic fixture replay, controlled live
evidence, documentation/link/schema validation, release/version recommendation,
cross-project handoff, `git diff --check`, clean-worktree review, consolidated result,
human approval, and approved commits. No tag/push/publication without separate
authorization.

## Controls and safety rules

- Inspect status before editing and preserve unrelated work.
- Use explicit Moshier/no-file calculation unless a separately approved profile says
  otherwise.
- Never use endpoint equality alone as invariance proof.
- Inconclusive proof fails closed to conditional/variable evidence.
- Never conflate uncertainty, disabled configuration, unsupported capability, and
  calculation failure.
- Never put representative-time degrees in an exact canonical fact.
- Preserve stable `source_chart_id`; birth-bound correction changes calculation
  identity, not automatically chart lineage.
- Run proportionate tests, broad tests for broad contracts, `git diff --check`, diff
  review, append-only log, slice result, approval, then commit at every gate.
- Do not modify SPC, SBE, API, project, or frontend implementation without explicit
  authority.
- Do not tag, push, publish, or use release credentials without explicit approval.

## Dependencies

- Swiss Ephemeris/pyswisseph point calculations under an exact qualified runtime;
- current AGF identity and calculation-provenance contracts;
- reviewed SPC handling of bounded canonical vocabulary and evidence;
- SBE eligibility/portfolio behavior for reduced evidence;
- API civil-time and immutable birth-version policy; and
- product decision on when bounded behavior replaces warned-noon MVP.

## Exit criteria

- One documented exact/bounded/unknown-day input and precedence contract.
- Civil-time bounds, DST behavior, inclusivity, duration, and hashing are explicit.
- Invariant classification is conservative, deterministic, versioned, and tested.
- Canonical graph contains no unsupported exact values.
- Every excluded configured feature has classified evidence or explicit profile
  exclusion.
- Houses, angles, sect, and dependent lots are absent under the initial bounded
  profile and capabilities say so.
- Calculation failure cannot appear as ordinary uncertainty.
- Exact Natal behavior remains compatible or has an approved versioned break.
- Explicit source identity survives bounded generation, serialization, and
  projection.
- Exact installed AGF-to-SPC compatibility passes.
- SBE/API/frontend obligations and unsupported paths are documented.
- Provenance, cache identities, schemas, docs, and migration policy are complete.
- Full relevant tests and installed controlled-live qualification pass.
- Every gate is reviewed and committed from a clean named boundary.

## Deferred work

- rectification;
- interval-aware house/angle/lot claims;
- bounded timing activation and relationship synthesis beyond the first consumer
  contract;
- non-canonical estimated-position views unless justified by a consumer;
- product/UI implementation; and
- release publication unless separately planned and authorized.
