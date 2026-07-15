# Ideas and Improvements — Astrology Graph Foundry

> This file contains active Foundry-owned work only: calculation, canonical source graphs, structural evidence, package materialization, source registries, pipeline behavior, and source-contract exports.
>
> Projection profiles, projected-term registries, deterministic rendering, and projected temporal semantics are owned by **Semantic Projection Core**. Claim graphs, narrative units, report compilation, and publishing belong to future downstream projects.

## Active near-term improvements

### Installation and environment diagnostics

The initial `astro-package doctor` command now reports the availability of Foundry, Semantic Projection Core, and Swiss Ephemeris. Follow-up work:

- test and document recommended Python / `pyswisseph` wheel combinations on Windows, macOS, and Linux;
- decide whether Python 3.11 should remain the recommended Windows live-calculation environment until dependable CPython 3.12+ wheels exist;
- add graph-only and live-calculation CI jobs;
- expand doctor output with ephemeris-path validation and optional live-provider smoke checks.

### Long-window eclipse/lunation workflows

The pipeline already accepts arbitrary explicit ranges, and the repository now includes `scripts/generate_long_window_lunations.py` plus a `.bat` wrapper. Follow-up work:

- integrate long-window lunation generation into richer fixture/batch helpers;
- align default report-corpus windows with long Transit windows;
- profile year-scale and multi-year package sizes;
- add optional compact views if real consumers need them.

### Eclipse and lunation event classification

Version 0.5.0 distinguishes ordinary lunations from eclipse-season candidates without claiming global eclipse confirmation. Future Foundry work should:

- use Swiss Ephemeris eclipse-search functions or another authoritative calculation path to confirm actual solar/lunar eclipses;
- classify solar eclipses as partial, annular, total, or hybrid where calculable;
- classify lunar eclipses as penumbral, partial, or total;
- preserve global event geometry separately from target-chart relevance and local visibility.

### Calculation and compilation reuse

Version 0.5.0 reuses provider-built Natal graphs and provider-owned `GraphCompiler` instances where possible. Continue profiling:

- graph ownership and mutation boundaries;
- large batch-generation runtime;
- cache lifetime and thread/process safety;
- whether Composite, Davison, Synastry, and return-chart compilation contain similar safe reuse opportunities.

### Compact Solar Return analysis view

Version 0.5.0 adds a factual `solar_return_analysis` view. Follow-up work:

- profile it on Natal, Composite, and Davison targets;
- refine stable object/relationship selection policies from real consumer use;
- add default CLI materialization policy only after the view is validated;
- consider a streaming/index form only if an interactive consumer needs one.

## Designed but deferred package/materialization work

### Full-package context inclusion modes

Design a general `full | summary | ref` policy for upstream package context embedded in Transit, Synastry, Composite/Davison, Lunar Return, and future timing artifacts.

Open questions include reference identity, content hashes, relocation, validation, standardized summaries, and self-contained defaults.

### Compact Natal analysis contract

Natal already exposes an analysis view. Revisit its post-split contract so it remains factual and source-oriented:

- placements, houses, angles, and aspects;
- canonical graph and structural-evidence summaries;
- stable indexes;
- selected high-structural-weight rows;
- no hidden projection or report-claim semantics.

### Streaming and game-oriented indexes

Profile actual consumer access patterns before designing smaller streaming or `game_index` forms. Potential work includes numeric/stable IDs, compact registries, configurable retention, and consumer-specific lookup indexes.

### Transit target policies

Define reusable Foundry source-selection policies such as `core`, `rich`, `experimental`, and possibly `game`. These should govern calculation/export eligibility rather than projected meaning.

Coordinate this with Composite/Davison target validation and document how omitted expanded targets remain auditable.

### Nested Lunar Return registry compaction

Profile long-window Lunar Return packages and investigate hash-addressed shared registries or reference-based storage without losing nested-chart provenance.

### Evidence-integration readiness audits

Periodically audit every pipeline for stable IDs, provenance, evidence tiers, derivation families, root-owner lineage, sensor identity, and structural scores. Cross-pipeline claims and contradiction reasoning remain downstream.

## Major calculation and timing design work

### Secondary progressions

Complete the currently scaffolded pipeline after deciding:

- symbolic timing convention;
- progressed-angle and house policy;
- progressed Moon phase;
- progressed-to-Natal aspect windows;
- exact-event versus snapshot materialization;
- target scope and provenance.

### Solar arc directions

Complete the scaffold after deciding the arc source, angle/house policy, orb policy, exact-event windows, and initial Natal-only versus generic-target scope.

### Exact-event and station-aware temporal geometry

Evolve beyond conservative observation-gap pass segmentation:

- solve exact aspect times;
- emit station events and explicit motion boundaries;
- group direct/retrograde passes from calculated event geometry;
- add canonical timing contracts for ingresses, stations, returns, eclipses, and lunations;
- profile compact external observation registries for multi-year ranges.

### Multi-person and group source graphs

Research N-person midpoint/group charts, pairwise-plus-group evidence, longitude averaging, event/location policies, provenance, and group identity stability.

### Synchronized relationship-climate source bundles

A Foundry-owned artifact may align factual source streams for Person A, Person B, Composite, and Davison across one time window. Consensus themes, model divergence, and narrative synthesis remain downstream.

## Cross-project ownership

### Semantic Projection Core

Owns projection profiles, contexts, projected-term registries, static and temporal projected graphs, profile materialization, and deterministic semantic rendering.

### Future reasoning/synthesis layer

Owns claim graphs, evidence support/contradiction, narrative units, report views, blueprints, relationship synthesis, and timing synthesis.

### Future publication layer

Owns PDF, web, book, dashboard, and visual-layout materialization.

## History

Completed Chunk 1/2 projection-boundary plans and the pre-cleanup parking lot are retained in:

- `docs/history/Ideas and Improvements Archive Through 0.4.2.md`
- dedicated Chunk and extraction-history documents
- Git history

## Streaming/game follow-ups after initial profile implementation

- Profile the `standard`, `compact`, and `game` Transit views against a real 18-month full package when one is available; current rich QA uses the one-month full package because older 18-month fixtures preserve only compact views.
- Let actual Mythos access patterns determine whether a later ultra-packed short-key or chunked/binary materialization is justified. The initial game artifact intentionally favors readable compact keys and one indexed JSON file.
- Consider deriving applying/separating phase directly in game/compact daily contact rows from canonical temporal arcs once the source package exposes an efficient candidate/date phase index.
- Consider optional precomputed mechanics vectors only in a game-owned adapter or explicit Foundry mechanics-export contract; do not hard-code Mythos scoring into the generic Transit package.
- Refine compact-view relationship selection policies across pipelines using derivation-family diversity and direct/core preference, following the Solar Return implementation in this pass.
