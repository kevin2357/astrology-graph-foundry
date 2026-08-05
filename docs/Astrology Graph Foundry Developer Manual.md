# Astrology Graph Foundry Developer Manual

**Status:** Pass 2 developer handbook.  
**Audience:** developers, report writers, game/tool authors, research users, future Foundry maintainers.  
**Relationship to `How to Use Astrology Graph Foundry.md`:** `How to Use Astrology Graph Foundry.md` remains the practical quick-start and command reference. This manual explains how to think about the SDK, how to choose packages, how to consume outputs, and how the SDK fits into the larger project ecosystem.

## 1. Executive orientation

The Astrology Graph Foundry started as a practical engineering layer:

```text
Swiss Ephemeris / PySwissEph
↓
standardized astrology calculations
↓
JSON packages
↓
downstream consumers
```

That remains useful, but it is now too small a description.

The SDK is becoming a **canonical semantic package generator** and, eventually, a substrate for **semantic evidence integration**. It computes chart facts, compiles them into graph-like semantic structures, and exposes them in views that can be consumed by reports, games, visualizations, publication systems, dashboards, and research tools.

The practical rule:

> **Compute once, compile once, consume everywhere.**

The research rule:

> **Treat each pipeline as an evidence sensor. Preserve what it observes. Integrate only after provenance is intact.**

## 2. Separation of concerns

The SDK is most coherent when its responsibilities are kept separate from adjacent layers.

### 2.1 Astronomical calculation

This layer computes positions, returns, aspects, houses, angles, lunations, and other astronomical/astrological facts. It should be deterministic and auditable.

### 2.2 Semantic compilation

This layer turns chart facts into graph objects, relationships, target registries, evidence claims, theme hints, operator hints, and report materials. It is where the package becomes useful to downstream consumers.

### 2.3 Package views

This layer emits output views for different consumers:

- `full`: audit/research detail;
- `analysis`: report/LLM-friendly semantic summary;
- `streaming_index`: lookup/index-friendly runtime format;
- future `report_view`: structured report-ready evidence bundles.

### 2.4 Projection

Projection is not SDK calculation. It translates canonical semantic meaning into a target domain using context and primitive mappings. The same Venus semantics can project into romance, workplace morale, game alliance mechanics, or park terrain.

### 2.5 Publication / application

Publication renders final artifacts: Markdown reports, PDFs, books, web pages, dashboards, images, or game mechanics. It should consume structured material rather than rediscovering astrology.

## 3. Pipelines as semantic observers

A pipeline is not merely a command. It is a semantic observer that answers a specific question.

| Category | Pipeline | Primary question |
|---|---|---|
| Identity | Natal | Who is this person/system? |
| Timing | Transit | What is active now or across this date range? |
| Relationship mechanics | Synastry | How do two people/systems interact? |
| Relationship entity | Composite | What relationship entity emerges as midpoint structure? |
| Relationship entity | Davison | If the relationship were born as a real event, what chart would it have? |
| Year-cycle timing | Solar Return | What story defines the birthday-to-birthday year? |
| Year-cycle timing | Annual Profections | Which life subsystem is foregrounded this year? |
| Month-cycle timing | Lunar Return | What emotional/monthly chapter is active? |
| Activation windows | Eclipse/Lunation | Where are the narrative punctuation points? |
| Developmental timing | Progressions | How is the person/system symbolically evolving? *(scaffolded)* |
| Developmental timing | Solar Arc | What long-term symbolic directions are active? *(scaffolded)* |

Downstream consumers should choose pipelines by the question they need answered.

## 4. Pipeline guide

### 4.1 Natal

Natal is the baseline identity package. It should be treated as the root semantic graph for person-centered work. Other pipelines activate, compare, contextualize, or project from natal structure.

Use natal for personality reports, transit target compilation, synastry inputs, projected chart generation, game character/player modeling, and baseline context in annual/monthly reports.

### 4.2 Transit

Transit is weather. It activates natal structures rather than replacing them. Use transit for daily reads, date-range forecasts, CFANFF reverse reads, long-window timelines, game-state modifiers, and active-arc summaries.

### 4.3 Synastry

Synastry describes interaction mechanics. It is directional and relational: person A's objects contact person B's objects and houses.

Use synastry for relationship dynamics, professional collaboration, parent-child or family-system pair analysis, game/player affinity mechanics, and any question that asks where two systems activate each other.

The semantic layer should remain as domain-neutral as possible. Romance is one projection, not the only interpretation.

### 4.4 Composite

Composite describes an emergent relationship entity through midpoint positions. It asks what third thing appears between two charts. Use composite for relationship-as-system reports, pair/team entity modeling, comparison against Davison, and future relationship synthesis packages.

### 4.5 Davison

Davison casts a real chart for the midpoint in time and space between two births. It is a relationship-entity chart, not a compatibility score.

The Kevin/Bre test case demonstrated why Davison matters: it independently produced a relationship-entity story that dovetailed with composite and synastry while preserving a distinct construction. It emphasized a relationship that enters through softness/atmosphere but stabilizes through practical relational evidence and daily-life calibration.

### 4.6 Annual profections

Profections identify the year's foregrounded house/sign/ruler. They are not a complete report by themselves so much as a yearly spotlight. In the generated yearly demonstration, the profection's 9th-house activation made the year's transits feel less like scattered events and more like activations inside a coherent chapter.

### 4.7 Solar return

Solar return is the birthday-year chart. It can stand alone as a year report or combine with profections/transits. In the yearly demonstration, solar return luminaries in the 9th corroborated the profection's 9th-house emphasis: two independent timing techniques pointing toward the same annual domain.

### 4.8 Lunar return

Lunar return is the month-scale emotional container. In the July demonstration, the lunar return provided information that transits alone would not: Aries rising showed an outer interface of action/self-definition, while Moon in Pisces in the 12th showed private emotional processing.

### 4.9 Eclipse/lunation

Eclipse/lunation packages identify narrative punctuation and activation windows. They are especially useful in long-window reports and should ideally be generated over the same windows as transit packages.

## 5. Output views

### 5.1 Full

Use full packages for audit and research. They are allowed to be large. They preserve provenance and detail.

### 5.2 Analysis

Use analysis packages for report generation and general LLM consumption. They should contain the useful semantic layer without requiring traversal of massive raw matrices.

### 5.3 Streaming/indexed

Use streaming/indexed packages for runtime systems, dashboards, and game engines. They should favor registries, IDs, compact references, and lookup paths over prose.

### 5.4 Report view

A future report view should compile one or more packages through a report blueprint.

Example shape:

```json
{
  "report_type": "yearly_integrated",
  "headline_claims": [],
  "evidence_bundles": [],
  "contradictions": [],
  "timeline_highlights": [],
  "section_materials": [],
  "source_packages": []
}
```

Report views should not be final prose. They are structured reasoning inputs.

## 6. Consumer patterns

### 6.1 Report writer

Start with analysis packages. Use full packages only when auditing or exploring new interpretive logic.

Good input stacks:

- natal baseline report: natal;
- monthly integrated: natal + lunar return + transits + annual context + lunations;
- yearly integrated: natal + solar return + profection + long transits + lunations;
- relationship full: natal A + natal B + synastry + composite + Davison.

### 6.2 LLM report agent

A report agent should receive curated analysis/report-view structures, not giant full outputs unless needed. It should be able to cite evidence bundles internally: "This claim is supported by profection + solar return + transit."

### 6.3 Game engine

The game engine should consume compact indexes and mechanic-ready trait vectors. It should not parse romance prose. It should map semantic traits like harmony, friction, initiative, support, communication, novelty, and responsibility into mechanics.

### 6.4 Publishing engine

The publishing engine should consume report views and layout hints. It should not decide astrological meaning. It should render semantic sections into designed pages/spreads.

### 6.5 Research dashboard

A research dashboard should consume full packages, analysis summaries, and future evidence objects. Its main job is to inspect convergence/divergence across techniques.

## 7. Report blueprints

A report blueprint is a recipe for assembling packages into a structured report view.

Example:

```json
{
  "report_type": "monthly_integrated",
  "required_inputs": ["natal", "lunar_return", "transit.analysis"],
  "optional_inputs": ["annual_profections", "solar_return", "eclipse_lunation"],
  "sections": [
    "executive_summary",
    "monthly_container",
    "active_arcs",
    "corroborating_annual_context",
    "key_windows",
    "practical_guidance"
  ]
}
```

The blueprint defines the report's evidence architecture before prose exists.

See `Report Blueprint Specification.md`.

## 8. Projection contexts

Projection context should be first-class. A relationship package can be read as romantic, professional, parent-child, friendship, family system, game mechanic, or story/NPC chemistry.

The source graph stays stable. Projection changes the target vocabulary.

See `Semantic Projection Integration.md` and the current Semantic Projection Core documentation.

## 9. Evidence integration

The yearly/monthly reports and Kevin/Bre relationship reports manually performed evidence integration before the SDK had a formal layer for it.

Examples:

- Profection and solar return converged on 9th-house/year-of-meaning themes.
- Lunar return and transits separated monthly subjective container from active arcs.
- Synastry, composite, and Davison separated interaction mechanics from relationship-entity identity.
- Composite and Davison convergence suggested that multiple independent constructions can point toward stable relationship themes.

The long-term architecture should formalize this with evidence objects and a Meta Semantic Graph.

See `Multi-Pipeline Semantic Synthesis.md`.

## 10. Documentation map

- `README.md`: authoritative documentation index and status map.
- `compatibility.md`: Foundry/SPC and contract-version expectations.
- `How to Use Astrology Graph Foundry.md`: practical quick-start.
- `Astrology Graph Foundry Developer Manual.md`: this handbook.
- `architecture.md`: SDK-level architecture.
- `Astrology Ecosystem Architecture.md`: whole ecosystem.
- `Semantic Graph Philosophy.md`: why graphs/evidence/provenance matter.
- `Semantic Projection Integration.md`: current Foundry-to-SPC handoff.
- `Report Blueprint Specification.md`: standard report formats and `report_view`.
- `Multi-Pipeline Semantic Synthesis.md`: long-term evidence integration / research layer.
- `Consumer Cookbook.md`: concrete downstream package-combination examples.
- `ideas_and_improvements.md`: roadmap and future work.

## 11. Working principles

1. Keep computation deterministic.
2. Preserve provenance.
3. Use stable IDs.
4. Keep upstream concepts domain-neutral.
5. Emit multiple views for different consumers.
6. Let projection handle context.
7. Let publishing handle layout.
8. Formalize evidence before final prose.
9. Treat convergence and divergence as valuable.
10. Update docs alongside code and design changes.

## TransitableChart and relationship-entity weather

The transit pipeline now accepts any supported package exposing the `TransitableChart` interface. The public CLI flag is `--target-dataset`.

This separates shared transit mathematics from chart-specific meaning:

- natal target -> individual climate;
- composite target -> relationship-pattern climate;
- Davison target -> relationship-lifecycle climate.

Davison is the first relationship-entity target validated in this implementation pass. Because a Davison chart is a real event chart, its chart body can be compiled by the same `GraphCompiler` used for natal charts. Composite packages also expose `TransitableChart`; a subsequent pass will validate conservative composite target policies and report semantics in greater detail.

Transit output fields are generic (`target_id`, `target_type`, `target_house`) rather than natal-specific. Consumers should use `metadata.target_chart_type`, `metadata.target_subject_scope`, and `metadata.semantic_scope` to frame interpretation.

See `transitable_chart.md` for the contract and examples.


## Generic relationship-entity timing

Natal, Composite, and Davison packages share the `TransitableChart` interface. Transit, solar-return, and eclipse/lunation pipelines consume that interface rather than branching on natal-specific package shapes.

This supports three related but distinct timing lenses:

- natal target: individual climate;
- composite target: relationship-pattern climate;
- Davison target: relationship-lifecycle climate.

Composite annual returns use a synthetic midpoint reference event as a recurrence anchor. Davison annual returns use the real midpoint event. Output metadata preserves the target chart type and semantic scope so downstream synthesis can compare the lenses without conflating them.


## Range-based lunar returns and relationship-entity profections

Lunar returns are now generated as a sequence over an explicit date range rather than as a single chart near one date. This makes the package directly usable for monthly timeline construction and integrated 18-month reports.

Annual profections now consume the common `TransitableChart` interface. For natal charts this is the traditional completed-age technique. For Composite and Davison targets, the SDK supports an explicitly experimental relationship-entity interpretation based on completed years from the chart reference event. The package records the method and caveat so synthesis/report consumers cannot silently treat it as conventional natal practice.

## View-specific schemas

Analysis and streaming/indexed outputs are public contracts in their own right. They now have dedicated JSON schemas rather than borrowing full-package schemas whose required fields do not exist in compact views.


See [`timing_pipelines.md`](timing_pipelines.md) for the common timing-target model, semantic scopes, and range-output behavior.


### Mandatory return-location policy

Solar and Lunar Return pipelines require callers to choose a return-location policy. This is a deliberate interpretive safeguard: target longitude determines the exact return instant, while location determines houses, angles, and planet-in-house interpretation. Output packages preserve the resolved policy and coordinates.

## Canonical and projected semantic layers

Developers should no longer treat every field called “semantic” as belonging to the same layer.

Use:

- `canonical_astrology_graph` for projection-ready source structure;
- `structural_evidence_graph` for conservative pre-projection aggregation;
- `projection_views["orthodox_astrology.v1"]` for conventional astrology themes and claim candidates;
- legacy `semantic_graph`, `theme_metrics`, `evidence_graph`, and `report_materials` only when ingesting historical pre-boundary inputs.

Semantic Projection Core consumes the canonical graph and preserves lineage from projected concepts through mapping rules to canonical objects and computed chart facts.

## Evidence-family grouping

Use `record_independence_group` when tracking unique rows and `evidence_family_group` when avoiding correlated-evidence inflation.

Never interpret the number of harmonic, antiscia, daily, or registry-expanded records as independent confirmation without collapsing them by owner/source family.

Synastry canonical graphs resolve compact operator registries but deliberately do not import orthodox theme registries.

## Source-chart and sensor-instance identity

Use `source_chart_id` to identify the chart/entity and `sensor_instance_id` to identify one pipeline result. Do not use analysis type alone as a globally meaningful sensor ID.

For production Natal generation, require the caller to supply the optional
`source_chart_id` input. Foundry preserves a valid value exactly and scopes all
canonical IDs and references beneath it. A display-name change is descriptive
only when explicit identity is stable. The deterministic name-derived fallback
exists for legacy and exploratory compatibility, not durable joins.

Do not silently select among conflicting explicit identity carriers. Use
`rescope_natal_package_source_chart_id` for a deliberate whole-package identity
change; never patch graph IDs or evidence references independently. See
[Canonical Identity and Projection Context Ownership](Canonical%20Identity%20and%20Projection%20Context%20Ownership.md)
and the [migration guide](Canonical%20Identity%20Migration%20Guide.md).

For synthesis across multiple packages, group records first by sensor instance, then use `source_chart_family_group` to detect dependence among techniques sharing the same underlying chart.

## Synthetic canonical graph identity

Do not construct package-level event or relationship graphs without passing the package's source-chart identity into evidence annotation. Every canonical row must have non-empty `source_chart_ids`, and `source_chart_family_group` must never use `source_chart_unknown` when the package identity is known.

## Final semantic materialization contract

As of Chunk 1.4, do not read these legacy aliases from generated packages:

- `semantic_graph`
- `theme_metrics`
- `relationship_metrics`
- `evidence_graph`
- `report_materials`

Use:

- `canonical_astrology_graph`
- `structural_evidence_graph`
- `projection_views["orthodox_astrology.v1"]`

Helper accessors in `common.semantic_layers` expose the canonical graph, orthodox metrics, claim candidates, and report materials.

Input-consuming pipelines are canonical-first. Legacy graph fallback remains only for raw or pre-boundary inputs that have not yet been finalized.

## Reading orthodox row annotations

Use `orthodox_row_annotation()` when a report-facing consumer needs conventional theme tags for a canonical object or relationship. Do not add those tags back to `canonical_astrology_graph`.

Analysis views intentionally expose compact orthodox extracts and projection summaries rather than full duplicated projection views.


## Environment diagnostics

Use `astro-package doctor` or `astro-package doctor --json` to distinguish core Foundry availability, external Semantic Projection Core availability, and optional live Swiss Ephemeris capability. Development and cached-package workflows should not require the native ephemeris dependency.
