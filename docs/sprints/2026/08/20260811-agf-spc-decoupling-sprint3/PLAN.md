# AGF/SPC Runtime and Ownership Decoupling Sprint Plan

**Status:** Proposed; sequenced after the time-frame bounded-Natal sprint

**Repository:** `astrology-graph-foundry`

**Sequence:** Third planned AGF sprint in the current bounded-Natal development arc

## Outcome

Make Astrology Graph Foundry independently installable and executable without
Semantic Projection Core while preserving the serialized source contracts that SPC
consumes. Projection execution, contexts, profiles, target ontologies, diagnostics,
and projected materializations leave AGF's runtime ownership. Cross-system
compatibility remains proven through independently installed immutable artifacts.

## Current evidence and assumptions

- Published AGF 0.7.0 is the immutable pre-decoupling baseline.
- `semantic-projection-core>=0.10.0,<0.11` is currently a mandatory AGF dependency.
- Coupling also exists through package-root exports, primary CLI imports and the
  `project` command, doctor projection readiness, `projection_adapter.py`, Synastry
  analysis materialization, scripts, and tests.
- AGF-owned canonical graphs, structural evidence, registries, temporal activation
  graphs, and temporal source bundles are projection-neutral wire contracts and do
  not inherently require SPC.
- The temporal source adapter emits a serialized handoff without importing SPC and
  should not be removed merely because its consumer is SPC.
- Public projection exports, CLI behavior, and Synastry view shape make a clean
  decoupling a likely AGF 0.8.0 change even if canonical graph versions are stable.

## Scope

- complete runtime/import/dependency ownership audit;
- removal of mandatory and optional AGF-to-SPC distribution dependencies;
- migration or removal of AGF-owned projection execution APIs and CLI routes;
- projection-neutral Synastry source/analysis replacement or explicit migration;
- doctor and capability semantics after projection execution leaves AGF;
- classification and relocation of projection-specific tests and scripts;
- clean installed AGF saved/live qualification with SPC absent;
- independent exact-wheel AGF-to-SPC wire-compatibility qualification; and
- versioning, migration, release, and downstream handoff recommendations.

## Non-goals

- changing astrology calculation or canonical source semantics merely to ease
  projection;
- implementing target-domain projection inside AGF under another name;
- modifying SPC, SBE, API, project, or frontend repositories without separate
  approval;
- silently restoring legacy theme inference in place of projected semantics;
- changing the frozen temporal source wire contract without evidence; or
- publishing, tagging, or using credentials without explicit approval.

## Slice 1 — AGF/SPC Runtime and Ownership Decoupling

Audit and remove SPC from AGF's distribution and runtime dependency graph across
`pyproject.toml`, package-root exports, primary CLI imports and the `project`
subcommand, `projection_adapter.py`, Synastry analysis materialization, doctor,
scripts, tests, schemas, and documentation.

Retain projection-neutral canonical and temporal source artifacts. Define explicit
migration for public `astrology_graph_foundry.project_dataset` and related exports,
`astro-package project`, the projection doctor mode, and the currently SPC-derived
Synastry compact analysis view. Prefer a source-factual Synastry handoff over a
plausible but semantically different fallback.

Keep compatibility proof outside both core runtimes: install exact AGF and SPC
wheels independently, exchange serialized packages, and verify identity, evidence,
registry, and contract-version preservation. Any SPC-owned implementation or
release work is a separate sprint in that repository.

**Gate 1:** Clean AGF base and live wheels install with SPC absent; package import,
all owned calculation CLIs, saved-package workflows, schemas, and doctor succeed;
no `semantic_projection` import remains in installed AGF runtime code; public
projection/API/CLI/Synastry migrations are documented and versioned; projection-
neutral temporal exports remain intact; exact AGF and SPC wheels pass an external
wire-compatibility harness; focused and full tests, package metadata inspection,
`git diff --check`, diff/log/result review, and human approval.

## Controls and safety rules

- Begin from a clean named boundary after Sprint 2 completion.
- Preserve published AGF 0.7.0 as the immutable compatibility reference.
- Do not retain SPC as an AGF extra merely to make dependency metadata look
  optional while AGF still owns projection execution.
- Do not remove projection-neutral source data or evidence required by consumers.
- Treat public API/CLI/view removal as a versioned migration, not cleanup trivia.
- Cross-repository checks are read-only unless separately authorized.
- Installed no-SPC tests must run outside the source checkout.
- At the gate: focused and full tests, `git diff --check`, actual diff review,
  append-only LOG, slice result, human approval, then commit.
- Clean temporary environments, wheels, caches, and generated artifacts.

## Dependencies

- published AGF 0.7.0 release and artifact hashes;
- completed and committed time-frame bounded-Natal Sprint 2;
- current SPC public wire contracts and independently published wheel;
- accepted ownership rule that AGF produces canonical source artifacts while SPC
  owns semantic projection; and
- explicit product-owner review of public API and Synastry migration decisions.

## Exit criteria

- AGF has no SPC distribution dependency or installed runtime import.
- AGF saved and live modes operate from a clean wheel with SPC absent.
- Projection execution APIs, CLI routes, doctor modes, and Synastry views have a
  documented, tested, versioned disposition.
- Projection-neutral canonical and temporal source contracts remain available.
- Independent exact-wheel compatibility preserves identity and evidence across the
  AGF-to-SPC wire boundary.
- Package/version recommendation and downstream migration guidance are explicit.
- Full relevant tests and documentation validation pass at an approved commit.

## Deferred work

- SPC-owned adapter or convenience-command implementation;
- bounded graph projection support;
- SBE/API/frontend migrations;
- neutral bridge-package design unless later justified; and
- immutable AGF 0.8.0 qualification and publication unless separately approved.
