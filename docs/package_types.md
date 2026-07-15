# Package Types

Implemented: natal, unified transit, synastry, composite, annual profections, solar return, lunar return, Davison, eclipse/lunation timeline, timeline wrapper.

Scaffolded: secondary progressions, solar arc directions.

Most long or matrix-like packages should expose compact `analysis` and/or `streaming_index` views plus explicit opt-in full output when needed.

## Transitable chart packages

Natal, composite, and Davison packages now expose a `transitable_chart` descriptor. The descriptor identifies the package's chart field, construction method, subject scope, semantic scope, and transit capabilities. Transit consumers should use `--target-dataset` and should not assume the target is natal.


## Public view schemas

Compact public outputs now have dedicated schemas instead of being validated against full-package schemas:

- `natal_analysis_view_v1.schema.json`
- `transit_analysis_view_v1.schema.json`
- `transit_streaming_index_v1.schema.json`
- `synastry_analysis_view_v1.schema.json`
- `synastry_streaming_index_v1.schema.json`

Full package schemas remain separate. Consumers should validate against the schema matching the actual materialized view.

## Semantic-boundary fields

During the Chunk 1 inspection cycle, major packages dual-write:

- `semantic_graph` — legacy graph with orthodox annotations;
- `canonical_astrology_graph` — pre-projection graph;
- `structural_evidence_graph` — conservative aggregation;
- `projection_views.orthodox_astrology.v1` — orthodox themes, claim candidates, and report consumer view;
- `semantic_boundary` — migration metadata.

Compact analysis/index views contain summaries rather than always repeating the full canonical graph.

## Chunk 1.1 lineage fields

Canonical rows now expose:

- `record_independence_group`;
- `evidence_family_group`;
- endpoint evidence tiers;
- root-owner refs;
- direct-versus-direct-between-derived relationship status.

Lunar Return range packages additionally expose nested canonical chart graphs.

## Chunk 1.4 materialization policies

### Full package

```text
full_canonical_projection_v1
```

Contains the authoritative canonical graph, structural evidence, explicit projection views, and pipeline-specific calculated data.

### Analysis view

```text
analysis_projection_summary_v1
```

Contains canonical and structural summaries plus selected orthodox projection material suitable for reports and human-facing analysis.

### Streaming index

```text
streaming_registry_summary_v1
```

Contains compact registries, references, indexes, and semantic summaries. It does not embed full graphs or report-material payloads.
