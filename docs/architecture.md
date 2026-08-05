# Architecture

Ephemeris JSONL -> analysis packages -> report/infographic/story/game generators.

## Compiler layer

Long-range transit packages should not repeatedly traverse the full natal semantic graph for every date. The `GraphCompiler` layer turns the rich natal semantic graph into a compact runtime view containing:

- transit targets,
- target type counts,
- natal house cusps,
- precomputed activated-relationship summaries per target.

The full graph remains canonical. The compiled graph is a performance and consumer-interface layer, not a replacement for the canonical semantic graph.

## Unified transit public API

The public CLI command is `transit`. A single date uses `--date`; a range uses `--start` and `--end`. Internally this still reuses the mature date-range transit engine, but downstream consumers should treat `transit` as the stable public pipeline name.

## Timing/return pipeline layer

First-pass implementations now exist for annual profections, solar returns, lunar returns, Davison charts, and eclipse/lunation calendars. These packages follow the same principles as natal/transit packages: deterministic computed facts first, semantic/report materials second, and room for compact/full views as the pipelines mature.


# Planned Evolution

The current architecture compiles deterministic semantic graphs from astrological computations.

Long-term, these graphs become inputs to an Evidence Integration Layer which produces a Meta Semantic Graph synthesizing convergent and divergent evidence across independent pipelines.

This allows downstream consumers to consume integrated evidence rather than isolated pipeline outputs while preserving provenance and auditability.

See also: Multi-Pipeline Semantic Synthesis.


## Forward Direction: Evidence Integration and Meta Semantic Graphs

The SDK's current production architecture centers on individual semantic packages: natal, transit, synastry, composite, Davison, returns, profections, and lunations. Each package is useful on its own.

The longer-term architecture treats these packages as evidence-producing semantic observers. A future Evidence Integration Layer may combine evidence from multiple package types into a Meta Semantic Graph.

Current:

```text
Pipeline
↓
Semantic Graph
↓
Consumer
```

Future:

```text
Pipeline
↓
Semantic Graph
↓
Evidence Objects
↓
Evidence Integration Layer
↓
Meta Semantic Graph
↓
Consumer
```

This direction is documented in `Multi-Pipeline Semantic Synthesis.md`.

## Ecosystem-Level Architecture

The SDK is increasingly best understood as the semantic kernel of a larger astrology ecosystem.

```text
Astronomical calculation
↓
Astrology Graph Foundry
↓
Canonical semantic packages
↓
Evidence / narrative units
↓
Projection layer
↓
Publishing / games / reports / dashboards / research
```

This does not mean the SDK should absorb every downstream responsibility. It means SDK output design should remain aware that many downstream systems depend on its stability and expressiveness.

See `Astrology Ecosystem Architecture.md`.

## Projection, report blueprints, and publication

Three downstream layers should remain conceptually separate:

1. **Report blueprint / report view**: assembles packages into report-ready evidence structures.
2. **Projection layer**: translates domain-neutral semantic structures into a target context such as romance, workplace collaboration, parent-child dynamics, game mechanics, or park/trail/ecosystem modeling.
3. **Publishing layer**: renders projected/report-ready content into Markdown, PDF, web, dashboards, books, or visual layouts.

A magazine-style report should not be generated directly from raw chart facts. It should consume structured report material produced from semantic packages.

See `Report Blueprint Specification.md`, `Semantic Projection Integration.md`, and the current Semantic Projection Core documentation.

## Pass 2: downstream architecture and ecosystem boundary

The SDK is now documented as the canonical semantic kernel for a larger ecosystem. The core architecture remains package-centered, but the downstream boundary is clearer:

```text
SDK semantic packages
↓
evidence / narrative units
↓
report blueprints / report views
↓
projection layer
↓
publication, games, dashboards, research, NCS/MPAS, CFANFF
```

The following companion documents define those downstream-facing boundaries:

- `Astrology Ecosystem Architecture.md`
- `Semantic Graph Philosophy.md`
- `Semantic Projection Integration.md`
- `Report Blueprint Specification.md`
- `Multi-Pipeline Semantic Synthesis.md`
- `Consumer Cookbook.md`

The important architectural principle is that the SDK should emit stable, provenance-rich, domain-neutral semantic packages. It should not overfit outputs to one downstream use case such as romantic reports or PDF publishing.

## TransitableChart abstraction

Transit calculation now consumes a shared `TransitableChart` interface rather than a natal-only dataset contract. Natal, composite, and Davison packages preserve their distinct package types and provenance while exposing a common chart substrate for transit targeting.

The transit engine is therefore organized as:

```text
package-specific chart builder
↓
TransitableChart adapter
↓
GraphCompiler
↓
transit calculation / compact views
```

The transit pipeline does not branch on natal vs. composite vs. Davison calculation rules. Chart-type-aware interpretation is preserved in target metadata and remains available to report and future relationship-climate synthesis layers.

See `transitable_chart.md`.


## Generic relationship-entity timing

Natal, Composite, and Davison packages share the `TransitableChart` interface. Transit, solar-return, and eclipse/lunation pipelines consume that interface rather than branching on natal-specific package shapes.

This supports three related but distinct timing lenses:

- natal target: individual climate;
- composite target: relationship-pattern climate;
- Davison target: relationship-lifecycle climate.

Composite annual returns use a synthetic midpoint reference event as a recurrence anchor. Davison annual returns use the real midpoint event. Output metadata preserves the target chart type and semantic scope so downstream synthesis can compare the lenses without conflating them.


## Range-based lunar-return packages and experimental entity profections

The common timing interface now extends beyond transits and solar returns. Lunar-return packages expose every return in a requested range, while annual profections can target Natal, Composite, or Davison charts. Relationship-entity profections are intentionally marked experimental and preserve their reference-event method in metadata.

Compact analysis and streaming/indexed outputs also have dedicated schemas, strengthening their status as stable consumer contracts rather than incidental projections of full packages.

## Historical architecture milestones

The following sections summarize completed migration milestones. They explain why the current boundary exists but are not a forward implementation plan. Detailed records live under `docs/history/`.

### Chunk 1 semantic-boundary architecture

The SDK now exposes:

```text
canonical_astrology_graph
        ↓
structural_evidence_graph
        ↓
projection_views
        └── orthodox_astrology.v1
```

The first two layers are pre-projection. The orthodox view is explicit projected interpretation. Legacy semantic fields are dual-written for one generated-output inspection cycle.

Calculation pipelines may import the semantic-boundary finalizer, but they must not import future projected reasoning, claim synthesis, report planning, or publishing modules.

## Chunk 1.1 lineage model

Canonical relationships now inherit evidence lineage from their endpoints. A direct aspect between harmonic or antiscia objects remains direct geometry but is classified as a direct relationship between derived objects.

The structural layer separately counts serialized record groups and collapsed root-owner evidence families. Future confidence and synthesis work must use evidence-family and sensor independence rather than raw record volume.

## Chunk 1.2 identity boundary

Canonical and structural graphs now distinguish the chart under observation from the pipeline instance observing it. Evidence-family grouping remains sensor-specific, while `source_chart_family_group` supports cross-technique de-duplication for evidence derived from the same chart.

## Chunk 1.3 synthetic graph identity

Package-level synthetic graphs must receive the same source-chart identity as graph-backed packages. The boundary finalizer now passes `source_chart_ids` through object and relationship annotation for Synastry and timing-event graphs. Historical internal Transit labels normalize to the public Transit sensor identity contract.

## Chunk 1.4 final package materialization

The temporary dual-write layer has been removed. Full packages use canonical source graphs and explicit projection views as the authoritative semantic representation.

Analysis and streaming outputs are separate materializations, not partial copies of a legacy package:

```text
full
→ canonical graph + structural graph + projection views

analysis
→ graph summaries + structural summaries + selected projection material

streaming
→ registries / references / indexes + compact semantic summaries
```

Pipelines consuming another SDK package must prefer `canonical_astrology_graph` over legacy nested graph fields.

## Chunk 1.5 report-facing row projection

Canonical rows are never used directly as though they were orthodox report rows. Compact report-facing views pass selected rows through the orthodox row adapter, preserving the architectural sequence:

```text
canonical source row
→ orthodox projection annotation
→ analysis/report-facing extract
```

## Chunk 2.1 projection-contract boundary

The repository now contains an extraction-ready `astrology_graph_foundry.projection` package. Its contracts accept canonical and structural plain-data inputs and have no dependency on chart pipelines or ephemeris providers. Projection semantics and engine execution remain downstream work.

## Chunk 2.2 executable projection boundary

Projection is now executable through a generic profile protocol and registry. Dependency direction remains:

```text
canonical/structural plain data
→ generic projection engine
→ domain profile
→ projected semantic graph
```

The generic engine does not import astrology calculation pipelines. Profile drafts carry mapping intent; the engine materializes deterministic IDs, source and rule provenance, audit coverage, unmapped diagnostics, and stable indexes.

## Chunk 2.3 orthodox profile foundation

The repository now demonstrates the full path:

```text
canonical astrology graph
→ generic projection engine
→ orthodox_astrology.v1
→ projected semantic graph
```

This is structured target-domain semantics rather than report prose or claim synthesis.

## Chunk 2.4 relationship projection

The SDK now contains a narrow `projection_adapter` that translates saved Synastry packages into generic projection requests. Compact Synastry analysis rows derive from one batch orthodox projection rather than hidden row-level theme reconstruction.

## Chunk 2.5 saved-dataset projection

The CLI now exposes `project`, allowing an existing canonical package to be reprojected under another context without recalculating the chart. Full and compact summary projected outputs are supported.

## Chunk 2.6 cross-profile execution

Saved Natal packages can now be projected through either orthodox astrology or the cognitive architecture demo without recalculation. Shared source graph hashes and source identities make cross-profile comparison auditable.

## Chunk 2.6.woof cross-domain proof

The same saved Natal package can now produce orthodox, cognitive, and Woofmapped semantic graphs. Woofmapped astrology uses Doghouses and species-specific behavioral media while retaining canonical source identity, aspect geometry, mapping provenance, and deterministic output.

## Canonical temporal source boundary

Foundry timing packages now have an explicit projection-neutral export path:

```text
Transit package
→ canonical_temporal_activation_graph.v1
→ temporal_projection_source_bundle.v1
→ Semantic Projection Core temporal_projection_request.v1
→ projected_temporal_activation_graph.v1
```

The canonical temporal graph is arc-first and directional. It preserves sampled observations, orb, motion, target identity, repeated-pass segmentation, and provenance without adding target-domain meaning.

Static projection of a Transit package remains rejected. The supported path is temporal-source export followed by Semantic Projection Core's production temporal projection route.
