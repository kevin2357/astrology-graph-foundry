# Temporal Projection A–B–C Implementation Plan

## Status

This is the official cross-repository plan approved after Chunk 2 extraction.

## A — Foundry temporal source contract

**Implemented in Foundry 0.4.0**

Deliverables:

- `canonical_temporal_activation_graph.v1`;
- Python export API;
- JSON Schema;
- deterministic activation and state IDs;
- directional activator/target roles;
- arc-first representation;
- sampled phase and motion preservation;
- explicit exactness limitations.

## B — Foundry Transit normalization adapter

**Implemented in Foundry 0.4.0**

Deliverables:

- full and streaming Transit input support;
- rejection of incomplete analysis views;
- observation lookup by candidate identity;
- conservative repeated-pass segmentation;
- projection-neutral source registries and provenance;
- `temporal_projection_source_bundle.v1`;
- CLI and QA tooling.

## C — Cross-repository projected timing

**Next major Semantic Projection Core feature**

Core should consume the Foundry bundle and implement:

```text
projected_temporal_activation_graph.v1
```

Recommended implementation sequence:

### C1. Temporal request and adapter contract

- define generic Core temporal request;
- ingest static target graph plus temporal source graph;
- validate Foundry contract version;
- preserve source identity and temporal directionality;
- keep static and temporal projection IDs distinct.

### C2. Projected activation arcs

- reuse existing projected object mappings;
- reuse existing aspect/contact mappings;
- map transiting activator and static target roles;
- retain temporal states, exactness, motion, and pass identity;
- support Orthodox, Cognitive, and Woofmapped profiles;
- emit full, standard, summary, and forensic materializations.

### C3. Temporal QA and reinstatement

- Natal target fixture;
- Composite target fixture;
- Davison target fixture;
- direct and retrograde-pass examples;
- context-aware projection tests;
- deterministic repeat runs;
- cross-repository schema tests;
- remove Foundry's static-project Transit rejection only after the new temporal route exists.

## Explicit non-goals for initial C implementation

- narrative transit readings;
- multi-activation claim synthesis;
- monthly weather summaries;
- report planning;
- interpretive meanings for retrograde passes;
- exact-event solving inside Core;
- projection of every timing pipeline at once.

## First post-extraction ergonomic work

The same Core pass should retain the queued ergonomic corrections:

1. Friendly handling for expected CLI exceptions, with traceback only in debug mode.
2. Artifact profiler recognition or exclusion of QA/rejection JSON files.
3. One authoritative profiling invocation in the bundled QA flow.

## Boundary rule

Foundry exports facts.

Core projects those facts.

Neither repository should silently imitate the other's responsibility.
