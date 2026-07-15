# Astrology Ecosystem Architecture

**Status:** Pass 2 architecture document.  
**Scope:** The whole project ecosystem around the Astrology Graph Foundry.

## 1. Purpose

This document describes the larger architecture implied by the SDK, publishing experiments, projected chart generation, Mythos Star Game, NCS/MPAS, CFANFF, and Multi-Pipeline Semantic Synthesis.

The SDK is upstream of many projects. Output choices made here affect everything downstream. If the SDK collapses interpretation too early, later projection becomes brittle. If it preserves clean semantic evidence, many applications can reuse the same source packages.

## 2. High-level architecture

```text
Astronomical sources / Swiss Ephemeris
        │
        ▼
Astrology Graph Foundry
        │
        ▼
Canonical semantic packages
        │
        ▼
Evidence / narrative units
        │
        ├───────────────┬────────────────────┬────────────────────┐
        ▼               ▼                    ▼                    ▼
Report blueprints   Projection layer     Synthesis layer      Research/audit
        │               │                    │                    │
        ▼               ▼                    ▼                    ▼
Publication        Domain models        Meta Semantic Graph   Dashboards/logs
        │               │
        ▼               ▼
PDF / web / book   games / parks / teams / family maps
```

## 3. What belongs where

### 3.1 SDK

The SDK computes and compiles deterministic chart facts, semantic graphs, evidence claims, registries/IDs, and consumer-oriented output views.

It should avoid final PDF layout, hard-coded romance-only interpretation, game-specific mechanics, target-domain overfitting, and irreversible prose-only outputs.

### 3.2 Evidence / narrative units

This is the bridge between packages and reports. A narrative unit says what claim is being made, what evidence supports it, what contradicts it, why it matters, which report sections might use it, and what visualizations might express it.

### 3.3 Report blueprint system

Blueprints define standard report products: required packages, optional packages, section order, evidence roles, fallbacks, and output shape.

### 3.4 Projection layer

Projection translates domain-neutral source semantics into target-domain models.

### 3.5 Publishing layer

Publishing turns report views or projected models into finished artifacts.

## 4. Why the SDK is the semantic kernel

The SDK is not necessarily the largest project, but it is the shared upstream source of truth. Reports, games, projection systems, publishers, dashboards, and future synthesis tools all become cleaner if the SDK emits stable semantic packages.

## 5. Example: yearly integrated report

A yearly report can consume natal baseline, annual profection, solar return, long-window transits, eclipse/lunation windows, and monthly lunar returns. The generated yearly report showed why this matters: profection established the foregrounded subsystem, solar return corroborated it, transits supplied pressure, and lunations added punctuation.

## 6. Example: monthly integrated report

A monthly report can consume natal baseline, lunar return, active transits, annual context, and lunation windows. The generated July report showed how lunar return adds subjective container while transits describe active arcs.

## 7. Example: relationship synthesis

A full relationship report can consume natal A/B, synastry, composite, and Davison. Synastry describes interaction mechanics; composite and Davison describe relationship entity. The Kevin/Bre reports showed both activation and entity-level calibration.

## 8. Downstream repositories

Potential future repo boundaries:

- `astrology-graph-foundry`: canonical packages;
- `astro-projection`: projection contexts, primitive mappings, target schemas;
- `astro-report-blueprints`: report schemas and compilers;
- `astro-publishing`: layout/PDF/web rendering;
- `mythos-star-game`: game-specific mechanics consuming SDK/projection outputs;
- archaeology/design-history repo: history, design rationale, research notes.

## 9. Documentation architecture

The docs should eventually split into quick start, developer manual, architecture reference, pipeline reference, schema/output reference, consumer cookbook, projection architecture, publishing architecture, and synthesis/research docs.


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

## Projection-aware semantic kernel

The SDK's semantic kernel is now explicitly pre-projection.

```text
calculation
→ canonical astrology graph
→ structural evidence
→ projection profile
→ projected reasoning
→ synthesis
→ reports / games / parks / cognitive models
```

Orthodox astrology is the first explicit profile, not an implicit universal interpretation. This keeps the same SDK packages usable by future cognitive, game, workplace, family-system, Human OS, and NCS/MPAS projections without requiring prose-level reinterpretation.

## Projection layer implementation begins

Chunk 2.1 introduces the internal extraction-ready projection contract package. It is intentionally located in the SDK only during development; contract ownership transfers to the independent Semantic Projection Layer project in Chunk 2.8.
