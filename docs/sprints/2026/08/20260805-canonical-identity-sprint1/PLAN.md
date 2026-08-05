# Canonical Identity Sprint Plan

**Status:** Proposed; planning only

**Planned sequence:** Sprint 1 of 2; the release-engineering sprint may not begin until this sprint is accepted, implemented, tested, documented, and committed.

**Repository:** `astrology-graph-foundry`

## Outcome

Freeze an explicit canonical subject/chart identity contract that works through supported live Natal generation and every retained AGF artifact boundary. A caller-supplied stable identifier must scope canonical object and relationship identity independently of display metadata, while calculation identity and downstream projection context remain separate concepts.

The production-preferred input is provisionally named `source_chart_id`, because that is AGF's existing canonical graph vocabulary and its handoff vocabulary to Semantic Projection Core (SPC). The exact validation grammar, namespace policy, precedence, fallback policy, and version impact are decisions of Slice 1 rather than assumptions embedded in implementation.

## Current Evidence and Assumptions

Evidence observed during planning:

- `BirthData`, `natal.build`, provider helpers, `astro-package`, `generate-daily-ephemeris`, and the repository tools do not expose an explicit chart identifier for ordinary live Natal generation.
- Canonical finalization already recognizes identity in saved artifacts, principally `transitable_chart.chart_identity.chart_id`, then metadata keys including `source_chart_id`, `target_chart_id`, and `chart_id`.
- In the absence of explicit identity, Natal finalization uses `natal:<slug(display name)>`. Canonical object IDs, regenerated relationship IDs, indexes, structural evidence, and exact nested references inherit that scope.
- Existing finalization migrates legacy `natal:*` object IDs, recursively rewrites exact references, rebuilds relationship IDs and indexes, and has idempotence coverage. It has not been qualified as a general migration from one already-scoped explicit identity to another.
- Synastry obtains identities from its component packages. Composite and Davison identities have separate relationship-chart derivations that currently depend in part on participant labels/names. Transit, return, and temporal paths rely on `TransitableChart.chart_id` and validate target identity.
- The projection adapter passes source chart identity and sensor identity to SPC. SPC 0.10.0 hashes source identity into request/projection identity, so changing canonical identity predictably changes downstream artifact identity without making projection context part of AGF identity.
- AstroWoof's API already distinguishes product dog ID, immutable birth-data version, normalized calculation-input hash, subject-calculation hash, and exact AGF-request hash. Its present AGF request has no explicit chart identity. These concepts must not be collapsed.
- The accepted AstroWoof birth contract supports exact-time and date-known/time-unknown birth versions. Identity must not encode time policy, timestamps, filesystem paths, or a calculation fingerprint.

Assumptions to validate at Slice 1's gate:

- `source_chart_id` is an opaque, caller-owned chart identity, not an AstroWoof dog database ID field and not an AGF-generated calculation fingerprint.
- AGF preserves a valid explicit identifier exactly rather than slug-normalizing it.
- Explicit identity wins over the display name. Conflicting explicit identity carriers fail closed rather than being silently prioritized.
- The deterministic name-derived identity may remain as a documented legacy compatibility fallback, but is unsuitable for production persistence or joins.
- This is additive at the invocation surface but semantically material enough to warrant a new identity-policy version and probably a package minor release.

## Scope

- Public and internal identity carriers for live Natal and saved packages.
- Validation, normalization/preservation, precedence, collision behavior, and error reporting.
- Canonical scoping, complete reference migration, indexes, evidence, claims, registries, adapters, serialization, and reload.
- Identity implications for synastry, composite, Davison, transit, returns, and temporal artifacts.
- AGF-to-SPC 0.10.0 compatibility and an AstroWoof API handoff specification.
- Versioned schemas, compatibility fixtures, migration guidance, and AGF/project-facing contract documentation.

## Non-goals

- Product users, dogs, handlers, breeds, pronouns, accounts, persistence, or database semantics.
- Calculation fingerprint design beyond preserving its separation from chart identity.
- Projection context, Woofmapping, authorship, card selection, or UI behavior.
- Release tagging or publication; those belong exclusively to Sprint 2.
- Modifying SPC, SBE, the API, or `astrowoof-project` without separately confirmed execution authority.
- Redesigning relationship-chart identity merely to make it resemble Natal identity.

## Slice 1 — Identity-Path Audit and Contract Decision

Create a complete identity-carrier and identity-consumer matrix covering public entry points, schemas, constructors, saved packages, semantic finalization, relationship packages, temporal adapters, projection adapters, fixtures, and documentation. Decide:

- whether `source_chart_id` is the authoritative input name;
- its semantic relationship to `TransitableChart.chart_id` and saved metadata;
- exact accepted type, length, character grammar, Unicode policy, whitespace/control-character policy, and reserved prefixes;
- byte-for-byte preservation versus normalization;
- explicit-value precedence and conflict detection across duplicate carriers;
- empty and duplicate value behavior;
- whether callers supply a complete namespace-safe ID;
- the legacy fallback and its warning/deprecation status;
- whether source scope must begin with `natal:` and how object IDs are formed for opaque scopes;
- package, graph-schema, birth-schema, and identity-policy version effects; and
- whether relationship-chart derivation belongs in this sprint or becomes a documented follow-up.

Recommended decision for review: accept a nonempty, bounded, namespace-safe ASCII identifier; preserve it exactly; require callers to own stability and uniqueness; use explicit input over the name fallback; reject conflicting explicit values. Do not prescribe AstroWoof's exact UUID namespace in AGF.

**Gate 1:** Produce an evidence-backed decision record, carrier/consumer matrix, before/after examples, schema-impact table, migration threat model, and test matrix. Run existing identity-focused tests and `git diff --check`; review the diff; append to `LOG.md`; write `results/SLICE 1 - Identity Contract Decision.md`; report surprises; stop for approval and commit only after approval.

## Slice 2 — Public Input and Schema Boundary

Implement the accepted field consistently in `BirthData`, Natal constructors/builders, provider-facing APIs, both supported console commands where Natal inputs are accepted, repository helper tools, serialization, and appropriate birth/package schemas. Centralize validation so CLI, Python, saved-package, and adapter paths cannot disagree. Preserve display name as descriptive metadata and provide actionable validation errors.

Define schema optionality deliberately: an optional field plus explicit legacy fallback preserves old callers; making the field required requires a versioned contract break and fixture migration. Ensure installed resource lookup, not source-tree paths, is the supported schema access path.

**Gate 2:** Focused constructor, validation, schema, serialization, and CLI tests; representative accepted/rejected identifiers; compatibility tests for callers omitting the field; full relevant public-boundary tests; `git diff --check`; diff review; log and slice result; stop for approval and commit from a clean named boundary.

## Slice 3 — Natal Canonical Finalization and Migration

Thread the accepted identity through metadata, transitable descriptors, semantic identity, and canonical finalization. Establish one canonical scoping function for objects and relationships. Migrate every exact reference atomically: relationship endpoints and IDs, claims, evidence, structural evidence, operators, source registries, indexes, projection-facing views, and nested exact-key references.

Do not assume the existing legacy migration safely re-scopes an artifact from explicit ID A to explicit ID B. Define whether such mutation is supported. If supported, retain enough prior identity to remove the old scope without prefix stacking; if not, reject it explicitly and require regeneration from unscoped/source facts. Repeated finalization under one identity must be idempotent.

**Gate 3:** Machine-readable migration fixtures proving same-name/different-ID separation, rename stability, predictable explicit-ID change or explicit rejection, zero stale endpoints/references, complete index rebuilding, deterministic fallback, and repeated-finalization idempotence. Run all graph, evidence, schema, saved-package, and adapter tests; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 4 — Relationship and Temporal Compatibility

Audit and test Natal, synastry, composite, Davison, transit, return, and temporal identity as distinct artifact classes. Synastry must distinguish same-named participants when explicit identities differ. Determine whether composite/Davison identity should derive deterministically from ordered/canonical participant chart IDs plus technique/configuration, accept its own caller-provided chart identity, or retain a versioned legacy derivation. Keep target chart identity, sensor instance identity, relationship artifact identity, and calculation/period identity explicit.

No relationship identity rule is changed without its own reviewed contract and migration effect. If a safe decision exceeds this sprint, document the limitation and prevent Natal production guarantees from being falsely generalized.

**Gate 4:** A package-type identity matrix and focused tests for participant order, same names, explicit IDs, temporal target checks, returns/transits, serialization, and deterministic derivation. Run the full package and temporal suites; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 5 — Migration and Downstream Boundary QA

Qualify old saved fixtures and the new explicit-identity fixtures through save, reload, adapters, and projection. Test against the exact qualified SPC 0.10.0 wheel/artifact rather than merely a version range. Confirm source vocabulary, source IDs, sensor identity, evidence, and request/projection determinism survive. Confirm projection context remains downstream-owned.

Produce a compact AstroWoof API handoff describing how an opaque stable value is derived from product-owned identity, without teaching AGF dog/database semantics. Reconcile the accepted project birth and canonical-chart contracts. Any disagreement is recorded as an open question rather than resolved unilaterally.

**Gate 5:** `identity-migration-fixtures.json` and `cross-repository-compatibility.json`; saved/reloaded and AGF-to-SPC projection tests using the exact SPC artifact; legacy-fixture regression; full relevant suite; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 6 — Documentation and Contract Closure

Update AGF's authoritative identity, schema, CLI, migration, and downstream-integration documentation. Update AstroWoof-facing contracts only within approved repository scope. Clearly label implemented guarantees, compatibility fallback, recommended production use, and deferred relationship decisions. Finalize package/schema/identity-policy version recommendations for Sprint 2.

**Gate 6:** Link validation, schema/example validation, complete relevant test suite, `git diff --check`, actual diff and document-status review, clean-worktree review, and a consolidated sprint result. Stop for approval; create the final approved Sprint 1 commit(s). Sprint 2 remains blocked until all accepted Sprint 1 commits form a clean, named boundary.

## Controls and Safety Rules

- Inspect status before every slice and preserve unrelated changes.
- Never use destructive Git operations.
- Keep cross-repository work read-only unless the user explicitly authorizes edits.
- Treat a found defect as successful QA: document, test, fix, rerun the gate, and seek approval.
- Never use display names, timestamps, filesystem paths, calculation hashes, or projection contexts as silent source identity.
- Never silently resolve conflicting explicit identities.
- At every gate: proportionate tests, broad tests for broad contracts, `git diff --check`, diff review, append-only log, slice result, report, approval, then commit.
- Do not tag, push, publish, or access release credentials in this sprint.

## Dependencies

- Current AGF canonical graph/schema behavior (Natal graph 1.3.0 at planning time).
- Accepted AstroWoof birth-data/version lineage contract and API worker handoff model.
- Exact qualified SPC 0.10.0 wheel and its compatibility resource.
- Human decisions at every gate, particularly validation grammar, legacy fallback, relationship identity, and versioning.
- Sprint 2 depends on the exact approved Sprint 1 commit; Sprint 1 does not depend on Sprint 2.

## Exit Criteria

- One documented authoritative identity precedence/conflict rule.
- Explicit stable identity accepted through every supported live Natal path, schema, and CLI/API boundary.
- Display-name changes do not affect canonical IDs when explicit identity is unchanged.
- Same-normalized-name subjects with different explicit IDs cannot collide.
- Changing explicit identity either migrates every scoped ID/reference predictably or is explicitly rejected with a documented regeneration path.
- Finalization is deterministic and idempotent; no stale endpoint, evidence, claim, index, registry, or exact reference remains.
- Explicit identity survives serialization, reload, adapters, and SPC projection.
- Product identity, chart identity, calculation identity, sensor identity, and projection context are not conflated.
- Relationship/temporal implications are implemented and tested or bounded by an explicit reviewed limitation.
- Backward compatibility is demonstrated or a versioned break and migration are approved.
- AGF-to-exact-SPC compatibility passes.
- AGF and authorized AstroWoof contract documentation is current and linked.
- Full relevant tests and formatting/link/schema checks pass.
- All slice gates are approved and committed; worktree is clean.

## Deferred Work

- Release qualification, reproducible wheels, tags, and publication (Sprint 2).
- AstroWoof API database and orchestration implementation of the accepted handoff.
- Product-specific identity namespace selection.
- Broader relationship-chart redesign if Gate 1 determines it cannot safely share this contract change.
- Any projection, authoring, deck, or UI behavior.
