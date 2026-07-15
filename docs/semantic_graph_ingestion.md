# Semantic Graph Ingestion

The chart semantic graph is now the preferred project-wide interface for chart facts, semantics, and downstream activation logic.

## Core idea

Consumers should not special-case nested facts like `body.dignity`, `body.antiscia`, or `body.harmonics`. Those facts are still preserved on the original body record, but they are also promoted into first-class graph objects and relationships.

Examples:

- `natal:Sun` object
- `dignity:natal_Sun` object
- `HAS_DIGNITY` relationship from `natal:Sun` to `dignity:natal_Sun`
- `antiscia_point:natal_Sun` object
- `HAS_ANTISCIA_POINT` relationship from `natal:Sun` to the antiscia point
- `harmonic:natal_Sun:5` object
- `HAS_HARMONIC_POINT` relationship from `natal:Sun` to the fifth-harmonic point

## Object classes

Important object types include:

- `planet_or_point`
- `angle`
- `angle_point`
- `calculated_point`
- `lot`
- `fixed_star`
- `dignity_state`
- `declination_position`
- `antiscia_point`
- `contra_antiscia_point`
- `harmonic_point`
- `sect_state`

Objects with longitude and `transit_target=true` can be activated directly by transit builders.

## Canonical relationship types

Relationship types are stable ontology labels. Downstream consumers should branch on `relationship_type`, not on prose labels.

Current canonical types:

- `ASPECT`
- `ANTISCIA`
- `CONTRA_ANTISCIA`
- `DECLINATION_PARALLEL`
- `DECLINATION_CONTRAPARALLEL`
- `HARMONIC_PROJECTION`
- `TRANSIT_ACTIVATION`
- `HAS_DIGNITY`
- `HAS_DECLINATION`
- `HAS_ANTISCIA_POINT`
- `HAS_CONTRA_ANTISCIA_POINT`
- `HAS_HARMONIC_POINT`
- `HAS_SECT`
- `LOT_DERIVED_FROM`
- `FIXED_STAR_CONJUNCTION`
- `ACTIVATES_NATAL_RELATIONSHIP`

## Transit activation behavior

Transit builders now target the semantic graph rather than only the original natal bodies.

That means transits can directly activate:

- planets and angles,
- lots,
- fixed stars,
- antiscia points,
- contra-antiscia points,
- harmonic points.

When a transit activates an object, the candidate also includes `activated_natal_relationships`, a compact list of graph relationships touching the activated target. This lets downstream consumers see that a transit to Venus is also activating Venus's dignity state, declination object, harmonic points, aspects, and other graph context.

## Recommended traversal pattern

1. Load `semantic_graph.objects`.
2. Use `indexes.objects_by_id` or `indexes.objects_by_source_key` to locate a node.
3. Use `indexes.relationships_by_object_id` to retrieve local graph context.
4. Branch on `relationship_type`.
5. Read `theme_tags` and `semantic_operator_hints` from objects and relationships rather than recomputing them.

## Compatibility

Nested facts remain available in the natal body records. The graph is an enriched traversal layer, not a destructive replacement.
