# Ideas and Improvements — Astrology Graph Foundry

> Projection-profile, projected-term-registry, deterministic-rendering, and temporal-projection work is now tracked in Semantic Projection Core. This document should contain calculation, source-graph, evidence, package, and pipeline work only.

# Running Ideas and Improvements

This file is a parking lot for ideas that are approved as worth preserving but not yet selected for the current implementation chunk.

## Transit target profiles

Add configurable transit target profiles so downstream consumers can choose how much of the expanded semantic graph participates in transit matching.

Possible initial profiles:

- `core`: traditional planets, luminaries, angles, and major calculated points.
- `rich`: core targets plus lots, antiscia/contra-antiscia points, harmonics, and selected fixed stars.
- `experimental`: all available first-class graph targets.
- `game`: targets useful for interactive/game engines, probably emphasizing stable identifiers and lightweight scoring.

This should wait until we have more real downstream use across reports, CFANFF reverse reads, Mythos Star Game, infographics, OMTA/projected-chart generation, and timeline consumers.

## Compact natal analysis view

The standard natal package intentionally preserves the full semantic graph for research, report generation, projected-chart generation, and auditability. For lightweight consumers, add a future `natal.analysis.json` view that contains the most commonly used natal facts, graph summary, major themes, evidence claims, and top relationships without requiring consumers to load the full semantic graph.

## Full transit natal-context inclusion options

Full transit packages currently include substantial natal context because they are intended as audit-grade artifacts. Add a future option such as `--full-include-natal full|summary|ref` so long-range full outputs can choose between embedding the complete natal package, embedding a compact natal summary, or referencing an external natal package path/checksum.

## Full-package context inclusion modes

Add full-package include modes for large research-grade outputs so consumers can choose how much upstream context is embedded versus referenced. Candidate options include `full`, `summary`, and `ref` for natal context in full transit, synastry, composite, and future timeline packages. This preserves auditability while avoiding unnecessary file-size growth when the source natal packages are already available.

## Expanded how-to / user guide

Create a much richer `How to Use Astrology Graph Foundry.md` or companion guide that functions as the project handbook. It should cover project philosophy, standards, style, package design goals, output descriptions, pipeline descriptions, output types (`analysis`, `streaming_index`, `full`), schema-reading guidance, file-reading guidance, and small toy reference implementations for reading schemas/files.

The guide should include examples for calling each pipeline and output type using fictional people and locations in all supported invocation styles: non-installed CLI via `python -m`, installed CLI, and Python import usage from another project that imports or submodules this SDK.


## Finish secondary progressions and solar arc directions

Secondary progressions and solar arc directions are currently scaffolded because they need more design decisions than the simpler return/profection/lunation pipelines.

For secondary progressions, decide and document the default symbolic timing convention, progressed angle policy, house policy, and output views. A first full implementation should include progressed planet positions, progressed Moon sign/house/phase, progressed-to-natal aspects, evidence claims, and report materials.

For solar arc directions, decide the default solar-arc source and orb policy, then implement directed natal points, directed-to-natal aspects, relationship/context registries, and compact analysis/full views.

## Ultra-light synastry game index view

The current synastry `streaming_index` is structurally useful for game engines, but still larger than ideal because it preserves a fairly rich `contact_registry`, ranked-contact metadata, and multiple lookup indexes. Add a future even-smaller `game_index` view that favors runtime lookup and scoring over interpretive richness.

Candidate design goals:

- Use compact numeric/contact IDs and short keys where practical.
- Store only object refs, aspect type, orb, weight/relevance, direction, house overlay refs, and compact theme/operator refs.
- Omit prose-oriented report fields, context hints, and expanded ranking details unless explicitly requested.
- Optimize lookup by player pair, object pair, theme, house, and relationship type.
- Keep richer narrative/semantic payloads in `analysis` and `full`; keep `game_index` focused on fast mechanics.

This should be considered when Mythos Star Game or another interactive consumer starts using relationship chemistry, affinity, challenge, or team/NPC mechanics.


## Report-oriented intermediate view

Introduce an optional report_view artifact between analysis packages and natural-language reports. Candidate contents include headline claims, supporting/contradicting evidence bundles, chapter candidates, timeline highlights, and confidence summaries.

## Documentation evolution

Gradually split documentation into:
- Philosophy
- Developer Handbook
- Pipeline Reference
- Schema Reference
- Consumer Cookbook
while retaining the current handbook as the primary entry point.

## Evidence Integration readiness

As Multi-Pipeline Semantic Synthesis matures, ensure every pipeline preserves provenance, stable identifiers, and confidence metadata suitable for future Meta Semantic Graph synthesis.


## Report-oriented intermediate views

Add optional `report_view` outputs for major pipelines or synthesis packages. These would not be prose; they would be structured report-generation inputs containing headline claims, supporting evidence, conflicting evidence, chapter candidates, timeline highlights, and confidence summaries.

Usefulness: high for LLM report writers and CFANFF-style workflows.

Effort: medium. The SDK already emits report materials, but a report view would require a more standardized contract.

Risk: if implemented too early, report views may freeze immature assumptions. Better to prototype after more generated reports are evaluated.

## Evidence-integration readiness

Review all pipelines for future Multi-Pipeline Semantic Synthesis compatibility. Each pipeline should preserve provenance, stable concept IDs where possible, evidence claim shapes, and enough source references to support eventual cross-pipeline corroboration/divergence analysis.

Usefulness: high long-term.

Effort: medium-high over time.

Risk: over-engineering before the synthesis layer exists. Mitigation: keep additions lightweight and provenance-focused.

## Documentation structure evolution

The documentation set should eventually split into a quick-start guide, SDK Developer Manual, architecture reference, pipeline reference, schema/output reference, consumer cookbook, and research/design documents.

Usefulness: high as the project becomes more than a small utility.

Effort: medium editorial work.

Risk: too much documentation overhead. Mitigation: update docs alongside code changes and keep quick-start concise.

## Ecosystem and downstream architecture ideas

### Projection Layer project

Create a future projection-layer project that consumes SDK semantic packages and produces target-domain models. Inputs would include source graph, projection context, primitive mappings, and target-domain schema. This would support romance, professional collaboration, parent-child dynamics, Mythos Star Game mechanics, NCS/MPAS terrain, and Human Operating System publication models.

Usefulness: very high. This appears to unify projected chart generation, report styling, NCS/MPAS, Mythos, and non-romantic relationship interpretation.

Effort: medium-high. Requires schema design and careful operator-preservation tests.

Risk: premature abstraction if built before several concrete examples exist.

### Publishing Layer project

Create a separate publishing/layout project that consumes report views or projected models and renders final artifacts such as PDFs, books, web pages, and visual dashboards. This keeps visual production separate from SDK semantics.

### Report Blueprint compiler

Define standard report blueprints and a compiler that converts SDK packages into `report_view.json`. Candidate report types: natal baseline, daily transit, monthly integrated, yearly integrated, synastry, relationship entity, full relationship synthesis, professional relationship, and game mechanics relationship model.

### Report View JSON

Add a structured intermediate output optimized for report writers and LLMs. It should include headline claims, evidence bundles, support/contradiction, section candidates, timeline highlights, and confidence notes.

### Narrative Unit layer

Explore narrative units as the bridge between semantic packages and publication. A narrative unit packages a topic, evidence, importance, suggested diagrams, suggested report sections, and possible pull quotes.

### Context objects

Introduce context objects to guide projection/interpretation without changing source semantics. Context may include age band, relationship type, report purpose, target domain, audience, tone, and application.

### Generalized non-romantic relationship interpretation

Ensure synastry/composite/Davison semantics remain useful outside romance. Relationship packages should expose domain-neutral traits: communication, activation, friction, trust, pacing, responsibility, morale, values alignment, novelty, and repair.

### Multi-person relationship graphs

Explore pairwise synastry plus group composite/centroid methods for families, teams, parties, and game groups.

### Group composites

Investigate N-person midpoint composites as a group entity chart. Combine with pairwise synastry and shared-theme aggregation.

### Long-window eclipse/lunation support

Generate eclipse/lunation packages for the same window as long transit packages by default or via helper scripts. Yearly reports need year-scale lunation context, not only Q1 samples.

### Eclipse candidate refinement

Replace or supplement "eclipse candidate" terminology with finalized event classification where possible: lunation, solar eclipse, lunar eclipse, partial/total/penumbral where available, and relevance to natal/composite targets.

### Standard report catalog

Maintain a documented catalog of common report formats and required/optional package sets. This helps downstream consumers understand how to assemble outputs.

### Future documentation split

Eventually split docs into quick start, SDK Developer Manual, architecture reference, pipeline reference, schema/output reference, consumer cookbook, projection architecture, publishing architecture, and research/design documents. Do not implement immediately; keep as future work.

### Game index / mechanic-oriented views

For game engines, consider ultra-compact indexes beyond current streaming views. These should use numeric/stable IDs, compact trait vectors, mechanic-ready relationship scores, and minimal prose.

### Relationship Synthesis package

Future package that consumes synastry, composite, Davison, relevant transits, and later progressions/returns/lunations to produce consensus themes, divergence notes, confidence weighting, evidence graph, report materials, story materials, and timeline materials.

## Pass 2 documentation and architecture roadmap additions

### Report blueprint/reference catalog implementation

Add versioned blueprint JSON files for the standard report catalog described in `Report Blueprint Specification.md`. Start with `yearly_integrated.v1`, `monthly_integrated.v1`, and `full_relationship_analysis.v1`.

### Report view schema

Create a `report_view.schema.json` with headline claims, evidence bundles, contradictions, section materials, timeline highlights, projection hints, publisher hints, and source package refs.

### Timing synthesis prototype

Prototype a timing synthesis compiler that consumes natal, profection, solar return, lunar return(s), transit range, and eclipse/lunation range to produce `report_view.json`.

### Relationship synthesis prototype

Prototype a relationship synthesis compiler that consumes natal A/B, synastry, composite, and Davison to produce consensus themes, divergence notes, and evidence bundles.

### Long-window lunation generation

Update scripts/examples so eclipse-lunation packages can be generated over the same window as long transit packages. This will make annual and monthly reports more useful.

### Context object schema

Create a small context-object schema for projection/report interpretation: relationship_type, age_band, target_domain, audience, tone, constraints, and output_intent.

### Projection examples

Build small examples for synastry -> professional relationship, synastry/composite -> Mythos game mechanics, natal -> Human OS publication model, and natal -> NCS/MPAS terrain model.

### Publishing layer extraction

When ready, move publication/layout concerns into a dedicated downstream project. The SDK should provide report views and semantic/publisher hints, not final layout.

### Documentation split later

The current documentation set is transitional. Eventually split quick-start, developer manual, architecture, pipeline reference, schema reference, consumer cookbook, projection architecture, publishing architecture, and research docs.

## Relationship climate implementation follow-up

### Composite transit validation and target policy

Composite packages now expose `TransitableChart`, but a dedicated validation pass should decide which composite objects should be first-class transit targets. Begin conservatively with core planets, angles, nodes, and houses; evaluate whether lots, antiscia, harmonic points, and other expanded objects add signal or noise.

### Relationship climate synthesis

After individual, composite, and Davison transit outputs have been validated, add a higher-level relationship-climate synthesis package. It should distinguish:

- Person A individual weather;
- Person B individual weather;
- relationship-pattern activation from composite transits;
- relationship-lifecycle weather from Davison transits;
- convergent themes;
- asymmetric pressure;
- model divergence;
- key timeline windows.

This should remain a synthesis layer above the generic transit engine.


## Recently implemented infrastructure

### Stable semantic IDs and deterministic ordering — implemented

Semantic relationship IDs are now content-derived rather than generation-order-derived. Semantic objects, relationships, compiled targets, transit candidates, and transit arcs use deterministic ordering and stable tie-breakers. This improves fixture comparison, reproducibility, streaming-index stability, and future evidence integration.

### Generic timing targets — implemented

Transit, solar-return, and eclipse/lunation pipelines now consume `TransitableChart` targets. Natal, Composite, and Davison packages can therefore act as individual, relationship-pattern, or relationship-lifecycle timing targets.

### Eclipse/lunation utility pass — implemented

The pipeline now supports arbitrary explicit ranges, generic target contacts, eclipse-season window terminology, activation windows, target activation counts, theme summaries, indexes, and high-activation report materials.


## Range-based lunar-return packages and experimental entity profections

The common timing interface now extends beyond transits and solar returns. Lunar-return packages expose every return in a requested range, while annual profections can target Natal, Composite, or Davison charts. Relationship-entity profections are intentionally marked experimental and preserve their reference-event method in metadata.

Compact analysis and streaming/indexed outputs also have dedicated schemas, strengthening their status as stable consumer contracts rather than incidental projections of full packages.


## Next development chunk: standard report provider

The next planned development chunk remains focused on standard report infrastructure:

1. Implement a standard report provider/compiler pipeline.
2. Define versioned standard report blueprint JSON objects.
3. Define the compiled `report_view` JSON object and schema.
4. Add initial reference report types:
   - integrated yearly;
   - integrated monthly;
   - full relationship analysis;
   - relationship-climate synthesis.
5. Add schemas, docs, examples, tests, and batch-script fixtures for report blueprints and compiled report views.

Return-location policy and Composite profection time-lord fallback were completed before this chunk and are no longer pending.

## Projection-boundary roadmap

### Chunk 1 — canonical boundary and orthodox namespacing

Implemented in the current development pass:

- `canonical_astrology_graph`;
- `structural_evidence_graph`;
- `orthodox_astrology.v1` projection view;
- evidence tier, derivation family, owner lineage, sensor ID, and independence groups;
- structural strength distinct from orthodox relevance;
- legacy confidence demoted to weighted-support metadata in the new view;
- temporary dual-write migration fields;
- schemas, docs, and tests.

### Chunk 2 — projection-profile framework

Planned:

- projection profile schema and registry;
- mapping-rule versioning;
- projected object and relationship schemas;
- source-to-projection audit path;
- declarative/semi-declarative `orthodox_astrology.v1` implementation;
- conservative structural synthesis improvements;
- a small non-orthodox proof profile, likely `cognitive_architecture_demo.v0`.

### Chunk 3 — reasoning and report infrastructure

Planned:

- reasoning profiles;
- evidence extractors;
- projected claim graph;
- calibrated confidence components;
- concept units;
- narrative units;
- standard report provider/compiler;
- versioned report blueprints;
- compiled `report_view` schema;
- integrated yearly, integrated monthly, full relationship, and relationship-climate report types;
- evidence presentation policies: hidden, footnote, appendix, expandable, companion research view.

## Deferred optimization and output work

These ideas remain worthwhile but are lower priority than the semantic architecture:

- compact Solar Return analysis view;
- smaller streaming indexes;
- ultra-light `game` / `game_index` output;
- configurable streaming retention policies;
- output-size profiling and registry compaction;
- standard report JSON fixtures after the reasoning layer exists.

## Chunk 1.1 — evidence-lineage correction

Implemented:

- relationship evidence tiers inherit endpoint derivation;
- direct relations between derived objects are represented explicitly;
- root-owner lineage is resolved before relationship grouping;
- record-level and evidence-family independence groups are separated;
- Synastry operator registries are resolved into canonical relationships;
- Synastry object registries preserve owner lineage and source operator hints;
- nested Lunar Return charts expose canonical graph registries;
- compact-view inspection distinguishes summary materialization from absence;
- Synastry relationship metrics feed the explicit orthodox projection view;
- schemas and tests cover harmonic, antiscia, registry, and nested-chart cases.

## Deferred engineering improvements discovered during boundary inspection

### Eliminate duplicate natal graph construction

The live Natal workflow currently builds/normalizes the same semantic graph in the provider and again in the Natal pipeline. Reuse the provider-compiled graph where possible.

Usefulness: medium-high for repeated batch generation.  
Risk: low if graph ownership/mutation is made explicit.

### Eliminate duplicate transit target compilation

Transit generation currently compiles the target graph during provider initialization and again inside the Transit pipeline.

Reuse a compiled target/GraphCompiler instance or pass a compiled descriptor through the provider boundary.

Usefulness: medium, especially for many short transit calls.  
Risk: medium because mutable compiler state and serialization boundaries need care.

### Remove temporary semantic dual-write inflation

The Chunk 1/1.1 inspection cycle intentionally repeats legacy, canonical, and projected structures. After the corrected output fixture is approved, remove deprecated duplication and choose one canonical materialization policy per output view.

Potential approaches:

- full package: canonical graph plus projection views;
- analysis: summaries plus selected projected material;
- streaming: references/registries only;
- optional legacy migration exporter rather than permanent duplicate fields.

Usefulness: very high for file size.  
Timing: after the next generated-output review, before or alongside Chunk 2.

### Nested canonical registry compaction

Lunar Return packages now preserve canonical graphs for each nested chart. Profile file size and consider registry deduplication or reference-based storage if the full 18-month output becomes excessive.

Usefulness: medium-high.  
Risk: avoid losing chart-level auditability.

## Chunk 1.2 — boundary stabilization

Implemented:

- globally stable `source_chart_id` and `source_chart_ids`;
- technique/time-window-specific `sensor_instance_id`;
- `source_chart_family_group` for cross-sensor dependence tracking;
- identity propagation into full and compact views;
- recursive nested-graph inspection;
- sensor-collision reporting;
- compact-summary `metric_source_field` preservation;
- identity and collision tests.

After the Chunk 1.2 output review, end the temporary dual-write cycle and choose final full/analysis/streaming materialization policies before beginning the generic projection-profile framework.

## Chunk 1.3 — synthetic identity completion

Implemented:

- source-chart identity propagation into all synthetic canonical rows;
- real source-chart family groups for Synastry, profections, lunations, and Lunar Return sequence graphs;
- normalization of legacy `transit_period_dataset` identity to the public Transit sensor contract;
- current-version refresh of generated canonical, structural, and boundary fields;
- focused tests for synthetic row identity and full/compact Transit sensor consistency.

After generated-output review, the remaining planned boundary task is removal of temporary dual-write duplication and selection of final materialization policies before Chunk 2.

## Chunk 1.4 — final materialization and dual-write removal

Implemented:

- removed temporary legacy semantic aliases from generated full packages;
- made canonical graphs the sole serialized source-graph layer;
- made `orthodox_astrology.v1` the sole home for orthodox metrics, claim candidates, and report materials;
- defined full, analysis, and streaming materialization policies;
- updated package-consuming pipelines to prefer canonical graphs;
- updated compact views, schemas, tests, and developer documentation;
- retained legacy input fallback only for raw/unfinalized package compatibility during internal transition.

Chunk 1 is now complete. The next architectural development round is Chunk 2: projection-profile framework and projected semantic graph machinery.

## Chunk 1.5 — final materialization corrections

Implemented:

- Solar Return canonical graph promotion before legacy nested-graph removal;
- orthodox row-level annotation for Natal, Transit, and Synastry report-facing views;
- compact analysis policy without full projection-view duplication;
- namespace-aware inspector legacy-alias checks;
- explicit inspector validation that all full packages materialize canonical boundaries.

Chunk 1 is considered complete after the generated fixture review confirms these conditions.

## Chunk 2.1 complete — contracts and extraction-ready skeleton

Implemented the generic projection contracts, deterministic IDs, JSON schemas, validation, audit/diagnostic scaffolding, tiny fixtures, and dependency inspection. No profile semantics or engine behavior were intentionally added.

## Chunk 2.2 — generic projection engine

Implemented:

- extraction-ready profile protocol;
- exact-version profile registry;
- optional entry-point discovery boundary;
- deterministic object and relationship projection;
- compatible projected-object merging;
- unmapped source policies;
- mapping execution audit records;
- mapped/unmapped coverage;
- deterministic indexes and output validation;
- a domain-neutral demonstration profile and concrete example.

Orthodox and cognitive semantics remain explicitly deferred to their planned rounds.

## Chunk 2.3 — orthodox profile foundation

Implemented:

- explicit `ProjectionOptions`, separate from semantic context;
- generic merge handling that preserves `source_names` arrays;
- `orthodox_astrology.v1` manifest and ontology;
- core planet/luminary/angle mappings;
- major-aspect mappings;
- profile-specific relevance with auditable components;
- concrete orthodox projection example and golden-style tests.

Deferred to Chunk 2.4:

- complete Synastry registry resolution;
- house overlays;
- general versus professional relationship contexts;
- replacement of provisional SDK orthodox row adapters with batch profile output.

## Chunk 2.4 — registry-aware relationship projection

Implemented:

- package registry adapter for Synastry;
- complete `theme_key` resolution through `theme_registry`;
- operator-registry resolution;
- theme-origin audit records;
- general and professional relationship contexts;
- explicit context vocabulary transformations;
- directional house-overlay projection;
- reverse projected-relationship source index;
- batch-projected Synastry analysis rows.

Deferred:

- standalone projection CLI/API for arbitrary saved datasets (Chunk 2.5);
- migration of remaining Natal-context compatibility hints;
- richer context ontology beyond the two proof contexts.

## Chunk 2.4.1 — real-fixture selection correction

Implemented:

- supported-first representative Synastry row selection;
- preservation of relative source order within supported and expanded groups;
- explicit available/selected/projected coverage counts;
- compact unmapped-family summaries with sample refs;
- retention of expanded rows when the requested limit has remaining capacity.

No orthodox ontology expansion or generic-engine policy change was introduced.

## Chunk 2.4.2 — canonical endpoint namespace correction

Implemented:

- support detection through shared canonical relationship IDs;
- canonical endpoint resolution for representative selection;
- canonical subset reuse for unmapped-family summaries;
- explicit unresolved relationship-ID count;
- regression coverage for compact versus canonical endpoint namespaces.

This completes the real-fixture overlay-selection correction without expanding profile semantics.

## Chunk 2.5 — standalone projection API and CLI

Implemented:

- `project_dataset()` SDK convenience API;
- generic saved-package extraction into `ProjectionRequest`;
- standalone `project` CLI command;
- context file and minimal inline context support;
- exact profile/version selection;
- full and summary output modes;
- audit and diagnostic materialization flags;
- unmapped policy and fraction threshold;
- example general and professional context files;
- compact projected-summary schema.

The generic projection core remains free of SDK adapter imports.

## Chunk 2.6 — cognitive architecture demo

Implemented:

- `cognitive_architecture_demo.v0`;
- ten core cognitive-process primitives;
- five major interaction mappings;
- projection-first Mars-square-Venus proof;
- explicit experimental/non-clinical/non-diagnostic guardrails;
- profile-aware default context;
- built-in registry support;
- cross-profile fixture and tests;
- saved-dataset CLI compatibility.

## Projection materialization and coverage follow-ups for Chunk 2.7

Real Chunk 2.5 fixtures exposed several useful stabilization targets:

- add standard compact full-projection materialization with grouped unmapped families and bounded samples;
- preserve exhaustive forensic audit/diagnostics as an optional mode or companion artifact;
- avoid repeating every unmapped source through both audit refs and informational diagnostic rows;
- consider external full-audit artifacts for very large source graphs;
- add profile-declared eligibility coverage distinct from total canonical-source coverage;
- distinguish object, relationship, supported-endpoint, declared-scope, and required-family thresholds;
- reconsider `--fail-on-unmapped-threshold` defaults once eligibility denominators exist;
- document or tighten output filenames so source person ordering matches package identity;
- profile runtime and serialization cost on full Synastry and large timing packages.

These are stabilization/materialization concerns, not blockers for the second reference profile.

## Chunk 2.6.woof — expanded profiles and projection-domain catalog

Implemented:

- cognitive architecture demo v0.2;
- sign-derived cognitive modes;
- house-derived cognitive domains;
- angle/interface mappings;
- quincunx and semisextile cognitive relations;
- `woofmapped_astrology.v0`;
- canine operator mappings;
- twelve canine sign modes;
- twelve Doghouse domains;
- canine angle interfaces;
- all seven SDK aspect mappings;
- three-profile cross-ontology examples and leakage tests.

### Candidate future projection families

Potential target ontologies now explicitly include:

- orthodox astrology;
- cognitive architecture;
- organizational systems and organizational psychology;
- narrative structure;
- economic systems;
- software architecture;
- learning theory;
- control theory;
- distributed systems;
- ecology;
- political institutions;
- game mechanics;
- Tarot;
- symbolic landscapes and national parks;
- Woofmapped astrology.

These are research directions, not commitments to implement every profile in this SDK.

### Chunk 2.7 coverage semantics

Real fixtures and the richer profiles reinforce that:

```text
unsupported by declared profile scope
is not the same as
eligible but unexpectedly unmapped
```

Chunk 2.7 should add:

- explicit profile eligibility declarations;
- outside-scope versus mapping-failure diagnostics;
- declared-scope coverage;
- eligible object and relationship coverage;
- supported-endpoint coverage;
- required-family thresholds;
- clearer `--fail-on-unmapped-threshold` semantics.

### Woofmapped future extensions

The supplied research artifacts contain mature ideas for:

- dog transits and daily horoscope weather;
- human-dog Synastry;
- dog-dog Synastry;
- pack models;
- lunar-weighted forecasts;
- handler-facing activities.

These are deliberately deferred. Chunk 2.6.woof implements Natal projection only.

## Chunk 2.6.woof.1 — semantic stabilization

Implemented:

- typed projected term registry contract and schema;
- profile-owned registries for orthodox, cognitive, and Woofmapped profiles;
- composition-oriented output guidance;
- used-term subset materialization;
- stable graph term/mode/domain/relation refs;
- True Node preference over Mean Node;
- Part of Fortune preference over Fortune alias;
- explicit policy-exclusion coverage;
- eligible versus outside-scope versus eligible-but-unmapped coverage;
- mandatory Woofmapped house policy with `doghouse` as the sole executable policy.

Chunk 2.7 should build materialization, threshold, large-fixture, and extraction policies on these foundations rather than redefining them.

## Deterministic projected-term rendering experiment

Implemented a bounded renderer proof with:

- projected-term resolution;
- natural and technical object-composition sentences;
- relationship sentences;
- preselected local-neighborhood paragraphs;
- stable template IDs and source-term provenance;
- cognitive and Woofmapped side-by-side showcase artifacts.

Deliberately deferred:

- automatic cluster discovery;
- claim generation;
- report planning;
- whole-report publishing;
- mature style packs;
- deterministic inference of processing sequences.

Future work may use canonical deterministic sentences as a semantic handoff to LLM styling: the machine establishes meaning; the language model makes it elegant.

## Post-2.6 renderer and registry follow-ups

Future work, deliberately deferred beyond Chunk 2.7:

- term-specific active clauses and lexical realization hints;
- article, pluralization, and grammatical-number metadata;
- collocation rules and lexical-collision avoidance;
- pronoun/reference management in deterministic paragraphs;
- grouping repeated relationships before prose realization;
- canonical-English versus style/voice realization packs;
- structured distinction between semantic claims and illustrative examples;
- claim evidence, inference depth, and confidence metadata;
- deterministic cluster detection, relationship ranking, and section planning;
- report-depth policies derived from one reasoning artifact;
- multilingual lexicons without changing target ontology;
- cross-profile semantic-facet queries and comparison tools.

The first renderer should remain a canonical semantic realization tool, not absorb claim discovery or publishing responsibilities.

## First post-extraction priority — temporal activation projection

Implement the design in `Projected Timing and Temporal Activation Design.md`:

- canonical activation arcs rather than duplicated daily rows;
- explicit activator/target directionality;
- transient object identity plus dated state;
- applying/exact/separating phases;
- repeated-pass grouping;
- individual, Composite, and Davison targets;
- arc, event, daily, monthly, and streaming materializations.

Current static projection intentionally rejects Transit packages so they cannot silently degrade to Natal-only output.

## Foundry packaging and Swiss Ephemeris installation

Chunk 2.8 Windows QA exposed that `pyswisseph` may lack a compatible binary wheel for Python 3.12, causing `pip` to attempt a local C build that requires Microsoft Visual C++ Build Tools.

Implemented:

- `dev` no longer pulls `pyswisseph`;
- `live` owns the native ephemeris dependency;
- `full` installs both development and live-calculation dependencies.

Future work:

- identify recommended Python / `pyswisseph` wheel combinations, including whether Python 3.11 should be the preferred Windows live-calculation environment;
- test newer `pyswisseph` releases for CPython 3.12 Windows wheels;
- document a Python/OS/wheel compatibility matrix;
- consider a preflight command that explains live-provider dependency status;
- determine whether CI should test graph-only and live-calculation environments separately.

## Canonical temporal graph follow-ups

- replace conservative observation-gap pass segmentation with solved exact-event grouping;
- represent station boundaries and direction changes explicitly;
- add canonical timing contracts for ingresses, stations, return events, eclipses, and lunations;
- support compact external observation-state registries for very long ranges;
- add a canonical temporal graph profiler and determinism inspector;
- preserve exact-event calculation as a Foundry responsibility rather than a projection concern.
