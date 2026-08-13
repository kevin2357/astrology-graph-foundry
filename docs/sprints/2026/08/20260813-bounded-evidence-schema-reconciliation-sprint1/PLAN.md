# Bounded Evidence Schema Reconciliation Sprint Plan

**Status:** Gate 4 candidate; awaiting review

**Repository:** `astrology-graph-foundry`

## Outcome

Make AGF's bounded uncertainty evidence implementation, standalone JSON Schema,
containing package validation, tests, and consumer documentation agree. Every
availability token emitted by a supported bounded-Natal producer must be defined,
and whole-artifact qualification must fail when an evidence record violates the
versioned evidence contract.

The completed work should support a narrowly scoped AGF 0.8.1 patch release without
changing calculated astrology, epistemic classifications, or existing evidence
meaning.

## Current evidence and assumptions

- Published AGF 0.8.0 emits bounded uncertainty evidence contract
  `agf.bounded_uncertainty_evidence.v1.0.0`.
- The standalone schema enumerates `available`, `disabled_by_configuration`,
  `unsupported_provider_field`, `missing_provider_field`,
  `nonfinite_provider_value`, and `provider_failure`.
- Current producers additionally emit `disabled`, `unsupported_profile`,
  `prerequisite_unavailable`, and `prerequisite_variable_or_unavailable`.
- `bounded_natal_dataset_v1.schema.json` treats major evidence-bearing containers
  as generic objects. It records the evidence-contract version but does not apply
  `bounded_uncertainty_evidence_v1.schema.json` to every registry record.
- Existing standalone-schema coverage proves one ordinary record. It does not prove
  that every supported producer token or every emitted evidence family validates.
- SPC found the mismatch during its bounded-consumer audit. Its safe interim policy
  is to treat `classification` as epistemic state, preserve `availability` and
  `status_reason` verbatim, validate only consumed evidence families, and retain
  the mismatch for upstream reconciliation.
- The extra tokens carry useful released distinctions. The initial recommendation
  is additive schema reconciliation, not collapsing or silently rewriting 0.8.0
  artifacts. This remains a gate decision until the full producer inventory is
  complete.

## Contract model to preserve

- `classification` answers what AGF proved across the interval: `invariant`,
  `conditional`, `variable`, `unavailable`, or `inconclusive`.
- `availability` explains the state of the feature's inputs or configured
  calculation path. It does not replace or override `classification`.
- `status_reason` is human- and operator-readable explanatory detail. It remains an
  open non-empty string rather than a closed semantic vocabulary.
- Downstream consumers must be able to preserve unknown future explanation fields
  safely, but AGF's own declared contract must validate every value AGF emits.

## Scope

- inventory all statically and dynamically emitted availability values;
- identify aliases, propagated provider values, and cross-family distinctions;
- decide and document the canonical availability vocabulary;
- reconcile implementation and standalone evidence schema without changing
  epistemic classification semantics;
- strengthen whole-package and registry validation for every evidence-bearing
  bounded-Natal family;
- add producer-to-schema, malformed-record, serialization, and installed-resource
  regression tests;
- verify representative exact, bounded, optional-feature, prerequisite-failure,
  and provider-failure cases;
- qualify SPC's bounded consumer against the corrected candidate contract; and
- close documentation, versioning, migration, and 0.8.1 release recommendation.

## Non-goals

- changing interval sampling, astrology calculations, invariant-promotion rules,
  or canonical graph contents;
- redesigning SPC's bounded projection behavior;
- converting free-form `status_reason` prose into an enum;
- weakening `additionalProperties: false` merely to make drift invisible;
- retroactively changing the immutable AGF 0.8.0 release;
- modifying SPC without separate approval; or
- tagging, publishing, or using release credentials during this sprint.

## Slice 1 — Producer and Validation-Path Audit

Enumerate every availability token produced directly, conditionally, or by
provider-field propagation. Map each token to feature families, classification
combinations, prerequisites, tests, and representative artifact paths. Trace every
place bounded evidence appears in `bounded_natal`, `uncertainty_assessment`, the
canonical graph, structural evidence, compact views, and registries. Establish
which records the standalone schema accepts and which containing schemas actually
validate.

**Gate 1:** Retain a machine-readable token/family matrix and validation-path map;
prove the 0.8.0 mismatch with minimal fixtures; distinguish schema omissions from
invalid implementation states; run focused audit tests and `git diff --check`;
update LOG and Slice 1 result; stop for approval.

## Slice 2 — Canonical Vocabulary and Standalone Contract

Decide whether released `disabled` becomes canonical or aliases
`disabled_by_configuration`, whether `unsupported_profile` remains distinct from
provider-field absence, and how prerequisite failures distinguish absent from
variable inputs. Centralize emitted tokens as named constants or a typed vocabulary
where that reduces drift. Update the standalone schema and normative documentation.
Avoid changing artifact values unless the approved vocabulary decision explicitly
requires a versioned migration.

**Gate 2:** Every supported producer token validates against the standalone schema;
unknown tokens fail; classification/availability combinations have regression
coverage; schema version compatibility and any migration rule are explicit; focused
tests, full relevant tests, `git diff --check`, log/result review, and approval.

## Slice 3 — Whole-Artifact Evidence Validation

Compose the evidence schema into containing bounded-Natal contracts where JSON
Schema structure permits. Add an AGF-owned recursive evidence validator for paths
that cannot be expressed safely without changing package shape. Ensure validation
covers all registries and embedded evidence families, reports precise feature paths,
and rejects malformed records rather than accepting them through generic objects.

**Gate 3:** Representative complete bounded artifacts validate; mutations at every
evidence-bearing family fail with actionable paths; no exact-Natal schema changes;
installed packaged schemas resolve correctly; focused/full tests,
`git diff --check`, log/result review, and approval.

## Slice 4 — SPC Compatibility, Documentation, and Release Closure

Run a read-only or external-harness compatibility check against SPC's bounded
consumer branch/candidate. Confirm it preserves the corrected vocabulary, treats
classification as epistemic authority, and does not reinterpret status reasons.
Update AGF consumer handoff, compatibility, release notes, and sprint evidence.
Choose the final package/schema version and prepare—but do not publish—the 0.8.1
candidate boundary.

**Gate 4:** AGF artifact and installed-wheel tests pass; SPC compatibility evidence
passes or records an explicit blocker; all schemas/resources are packaged; full
suite and Markdown/JSON validation pass; `git diff --check` and worktree review are
clean; LOG and result are complete; human approval precedes commits or publication.

## Controls and safety rules

- Begin from clean `main`; preserve unrelated user changes.
- Treat AGF 0.8.0 and its tag/artifacts as immutable evidence.
- Do not use a permissive schema escape hatch to conceal producer drift.
- Do not infer epistemic state from `availability`; classification remains
  authoritative.
- Preserve unrecognized consumer-facing reason strings byte-for-byte.
- Prefer generated inventory evidence over a hand-maintained token list alone.
- Test schema resources from an installed wheel outside the checkout before closure.
- Cross-repository SPC inspection is read-only unless explicitly authorized.
- At every gate: proportionate tests, full relevant tests for broad contract changes,
  `git diff --check`, actual diff review, append-only LOG, slice result, findings,
  human approval, then commit.
- Do not tag, push a release, or publish without explicit approval.
- Retain compact evidence and hashes; clean temporary environments and artifacts.

## Dependencies

- immutable AGF 0.8.0 release and bounded evidence contract;
- current SPC bounded-consumer audit and its family-by-family preservation policy;
- JSON Schema Draft 2020-12 reference-resolution behavior;
- representative Linux/Moshier bounded artifacts, including optional-feature and
  prerequisite-unavailable paths; and
- product-owner decisions at vocabulary and release gates.

## Exit criteria

- One documented canonical availability vocabulary exists.
- Every availability value AGF can emit is covered by code constants, schema, and
  tests.
- Unsupported values fail standalone and whole-artifact validation.
- Every bounded-Natal evidence family is validated or explicitly documented with an
  equivalent recursive validation control.
- Classification, availability, and status reason remain distinct and documented.
- Existing 0.8.0 artifact meaning is preserved or an explicit versioned migration
  exists.
- Installed-wheel schema/resource validation passes outside the source checkout.
- SPC bounded-consumer compatibility is demonstrated or a precise blocker is
  recorded.
- Package and evidence/schema version implications are explicit; expected outcome
  is AGF 0.8.1 if reconciliation remains additive.
- Full relevant tests, JSON/Markdown validation, and `git diff --check` pass.
- Approved commits end at a clean named boundary.

## Deferred work

- broader evidence-contract redesign beyond the discovered mismatch;
- new uncertainty classifications or projection semantics;
- transit and Synastry bounded-time calculation support;
- generic forward-compatible extension namespaces unless the audit demonstrates a
  concrete need; and
- AGF 0.8.1 publication until separately approved.
