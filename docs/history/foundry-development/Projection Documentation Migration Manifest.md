# Projection Documentation Migration Manifest

## Moved to Semantic Projection Core

Projection contracts, engine architecture, profile authoring, context behavior, audit/materialization, projected term registries, deterministic rendering, timing projection design, reference profiles, and Chunk 2 implementation history.

## Retained in Astrology Graph Foundry

Canonical astrology graph, structural evidence, calculation pipelines, providers, saved-package schemas, `TransitableChart`, and SDK adapter/CLI integration.

## Split

- Ecosystem architecture: Foundry owns the upstream calculation/source boundary; Projection Core owns target-domain transformation.
- Ideas and Improvements: calculation/pipeline ideas remain here; projection/profile/rendering/timing-projection ideas moved to Projection Core.
- Developer Manual: Foundry documents source contracts and integration; Profile Authoring and projection internals live in Projection Core.

Duplicated projection documents in this repository have been replaced by migration pointers so there is one authoritative source.


## Foundry 0.5 cleanup

Chunk 2 implementation documents are now stored under `docs/history/projection-extraction/`. Current projection-concept filenames remain as short migration pointers where older links may still refer to them.
