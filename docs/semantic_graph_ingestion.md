# Canonical Graph Ingestion

The supported cross-system source interface is the package-level
`canonical_astrology_graph`. It combines calculated chart facts with normalized,
projection-neutral astrological structure. It is not a reader-facing report and
does not contain a target-domain projection.

The authoritative schema is
[`canonical_astrology_graph_v1.schema.json`](../src/astrology_graph_foundry/schemas/canonical_astrology_graph_v1.schema.json).
The current graph version is `1.3.0`.

## Select the canonical layer

Consumers should read these package layers according to their purpose:

- `canonical_astrology_graph` is the source graph supplied to Semantic
  Projection Core (SPC) and other graph consumers.
- `structural_evidence_graph` is a projection-neutral summary of evidence,
  derivation families, structural strength, and activation groups.
- `projection_views` are optional derived compatibility or consumer views. They
  are not substitutes for the canonical source graph.
- chart-specific nested records preserve calculated detail and compatibility
  data, but downstream systems should not reconstruct a competing canonical
  graph from them.

Older saved packages may expose a nested `semantic_graph`. That is a legacy
compatibility shape, not the current production boundary.

## Identity and references

The graph carries `source_chart_id` and `source_chart_ids`. Object and
relationship IDs are deterministically scoped beneath that chart lineage. The
caller-supplied chart identity is opaque: consumers must preserve it and must
not infer product identity, calculation identity, or projection context from
its text.

Use exact emitted IDs rather than constructing IDs from display names or old
local forms such as `natal:Sun`. For production generation, supply a stable
explicit `source_chart_id`; the name-derived behavior is a compatibility
fallback only.

Relationships reference canonical object IDs through their source and target
fields. Claims, structural evidence, registries, and projection output may also
retain exact canonical references. Preserve those references together when
copying or archiving a graph.

## Objects and relationships

Common object types include planets and points, angles, lots, dignity states,
declination positions, antiscia and contra-antiscia points, harmonic points,
fixed stars, and sect state. Available types depend on the chart type and
calculation configuration.

Branch on emitted type fields and registry definitions rather than prose
labels. Common relationship types include:

- `ASPECT`
- `ANTISCIA` and `CONTRA_ANTISCIA`
- `DECLINATION_PARALLEL` and `DECLINATION_CONTRAPARALLEL`
- `HARMONIC_PROJECTION`
- `HAS_DIGNITY`, `HAS_DECLINATION`, and `HAS_SECT`
- `HAS_ANTISCIA_POINT`, `HAS_CONTRA_ANTISCIA_POINT`, and
  `HAS_HARMONIC_POINT`
- `LOT_DERIVED_FROM`
- `FIXED_STAR_CONJUNCTION`
- temporal activation relationships where present

This list is orientation, not a closed copied schema. Consumers should use the
packaged schema and the artifact's registries when validating exact content.

## Evidence and source semantics

Each canonical object and relationship carries `evidence_metadata` and a
projection-neutral `structural_strength_score`. Rows may also carry
`operator_hints`, which remain source-domain astrological primitives.

The canonicalizer intentionally removes orthodox theme tags, report claims,
consumer report structure, relevance scores, and projection-specific salience.
Do not recompute those presentation concepts inside AGF ingestion. SPC owns
target-domain projection; later systems own selection, synthesis, authorship,
and presentation.

Evidence metadata describes the calculated or derived source lineage of a row.
It is not a probability that the interpretation is true. Preserve evidence,
derivation-family, independence-group, and exact-reference fields through
projection and downstream artifact retention.

## Recommended traversal

1. Validate and load `package["canonical_astrology_graph"]`.
2. Record its graph version, source identity, calculation provenance, and
   artifact provenance before transformation.
3. Traverse `objects` and `relationships`; treat array ordering as deterministic
   output behavior, not as semantic identity.
4. Use `indexes.objects_by_id`, `indexes.objects_by_source_key`, and
   `indexes.relationships_by_object_id` as accelerators when present. The
   arrays and exact IDs remain authoritative.
5. Branch on emitted type fields and preserve `evidence_metadata`, operator
   primitives, endpoints, registries, and exact references.
6. Supply the intact canonical graph to SPC. Filter or summarize only in a
   derived artifact whose lineage still points to the canonical source.

## Compatibility boundary

Nested chart facts remain available for calculation detail and compatibility,
but the canonical graph is the supported projection source. AGF does not embed
Woofmapping, product dog metadata, reader prose, card selection, or projection
context in canonical identity.

For the identity contract and downstream ownership boundary, see
[`Canonical Identity and Projection Context Ownership.md`](Canonical%20Identity%20and%20Projection%20Context%20Ownership.md)
and [`Compatibility Guide`](compatibility.md).
