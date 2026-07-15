# Foundry 0.5.0 — Housekeeping and Practical Package Improvements

## Scope

This pass combined low-risk repository housekeeping with bounded package improvements that had clear Foundry ownership.

## Implemented

- Replaced the mixed historical/future ideas file with a current Foundry-only backlog and archived the original.
- Added `astro-package doctor` with human-readable and JSON output.
- Added an explicit long-window eclipse/lunation helper script and Windows batch wrapper.
- Added additive, projection-neutral eclipse-season classification fields.
- Reused provider-compiled Natal semantic graphs.
- Reused provider-owned `GraphCompiler` instances when compatible.
- Added a compact factual Solar Return analysis view and schema.
- Updated user-facing documentation around package ownership, installation, diagnostics, long-window lunations, and compact Solar Return output.

## Architectural boundaries

The Foundry continues to own calculated facts, canonical source graphs, structural evidence, package materialization, and source-contract exports.

Projection semantics remain in Semantic Projection Core. Claims, reports, and publishing remain downstream.

## Deferred

No new progression, solar-arc, report-view, game-index, context-reference, or exact-event temporal architecture was introduced in this pass.
