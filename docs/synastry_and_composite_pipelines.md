# Synastry and Composite Pipelines

The SDK includes real `synastry_relationship_dataset` and `composite_dataset` builders.

## Inputs

Both pipelines accept two standard natal packages as their preferred input. They may also compute both natal packages live from birth data via Swiss Ephemeris. This keeps the relationship layer aligned with the same enriched natal dataset used by natal reports, transit packages, projected-chart generation, and game consumers.

## Synastry CLI outputs

The synastry command now follows the same default-output pattern as `transit`.

```bat
python -m astro_analysis_sdk.cli synastry ^
  --person-a-natal-dataset kevin_natal_dataset.json ^
  --person-b-natal-dataset bre_natal_dataset.json ^
  --out kevin_bre_synastry_dataset.json
```

By default this writes two compact views:

- `kevin_bre_synastry_dataset.analysis.json`
- `kevin_bre_synastry_dataset.streaming_index.json`

The full research matrix is opt-in:

```bat
python -m astro_analysis_sdk.cli synastry ^
  --person-a-natal-dataset kevin_natal_dataset.json ^
  --person-b-natal-dataset bre_natal_dataset.json ^
  --out-full kevin_bre_synastry_dataset.full.json
```

You can also explicitly request individual views:

```bat
python -m astro_analysis_sdk.cli synastry ^
  --person-a-natal-dataset kevin_natal_dataset.json ^
  --person-b-natal-dataset bre_natal_dataset.json ^
  --out-analysis kevin_bre.analysis.json ^
  --out-streaming-index kevin_bre.streaming_index.json
```

## Synastry full package

The full synastry package still contains the complete directional aspect matrices and house overlay matrices, but repeated semantic material is moved into registries:

- `object_registries.person_a` and `object_registries.person_b` store compact graph-object records.
- `natal_context_registries.person_a` and `natal_context_registries.person_b` store natal relationship/context summaries.
- `theme_registry` maps each `theme_key` to its theme tags.
- `operator_registry` maps each `operator_key` to semantic operator hints.
- Synastry rows store object IDs, theme/operator keys, and context refs instead of repeating full objects, operator arrays, and natal context payloads.

This preserves auditability while avoiding the previous large repeated-context payload.

## Synastry analysis view

The analysis view is the report-consumer default. It includes:

- person metadata and semantic graph summaries,
- compact object registries,
- theme and operator registries,
- `natal_context_hints` for report writers,
- top synastry aspects,
- top house overlays,
- relationship metrics,
- evidence claims,
- compact composite summary.

The analysis view contains enough natal context for many relationship reports without separately loading both natal packages, especially when the report mostly interprets synastry/composite dynamics. For a full natal-style individual-context chapter, consumers should still load the two original natal packages because those preserve the complete natal semantic graph and full technical appendices.

## Synastry streaming/index view

The streaming/index view is designed for games, interactive UIs, and lookup-heavy consumers. It contains:

- `contact_registry`: static semantic material for each unique synastry contact,
- `overlay_registry`: static semantic material for each house overlay,
- compact `ranked_contacts` rows with IDs, rank, orb, strength, and weight,
- compact `house_overlay_refs`,
- indexes by direction, aspect, source object, target object, theme, and house,
- object, theme, operator, and natal-context registries for resolving refs.

The Mythos/game engine can load this once and query by object pair, theme, relationship type, direction, house, or aspect without reading a giant full matrix into memory.

## Composite output

The composite pipeline produces a midpoint-longitude composite chart from shared body keys, including midpoint houses when both natal packages contain house cusps. It then builds a semantic graph for the relationship entity and computes composite aspects, theme metrics, balance metrics, evidence claims, and report materials.

The composite chart is intended to support the “relationship as third protagonist/entity” downstream report style.

## Relationship-entity transits

Composite and Davison packages expose the shared `TransitableChart` contract. This allows the ordinary transit engine to calculate activations to relationship-entity chart objects. Davison transit generation is included and validated in the current pass; composite transit target-policy validation is the next step.
