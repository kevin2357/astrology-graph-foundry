# Timing Pipelines

## Shared target model

The following timing pipelines consume `--target-dataset` and therefore accept Natal, Composite, or Davison packages implementing `TransitableChart`:

- `transit`
- `solar-return`
- `lunar-return`
- `eclipse-lunation`
- `annual-profections`

Each output records target chart type, subject scope, and semantic scope.

## Semantic scopes

| Target | Transit | Solar return | Lunar return | Lunation | Profection |
|---|---|---|---|---|---|
| Natal | individual climate | individual annual climate | individual monthly climate | individual lunation climate | individual annual profection |
| Composite | relationship-pattern climate | relationship-pattern annual climate | relationship-pattern monthly climate | relationship-pattern lunation climate | relationship-pattern annual profection |
| Davison | relationship-lifecycle climate | relationship-lifecycle annual climate | relationship-lifecycle monthly climate | relationship-lifecycle lunation climate | relationship-lifecycle annual profection |

## Return-location policy

Solar and Lunar Returns require an explicit policy choice:

- `target_reference`: cast houses/angles for the TransitableChart reference location;
- `explicit`: require timezone, latitude, longitude, and label.

There is no silent default. This prevents a synthetic Composite midpoint location or a historical birth location from being used accidentally in a report intended to describe a relationship/person currently living somewhere else.

The resolved policy and coordinates are preserved in `return_location` and `metadata.return_location_policy`.

## Solar returns

Solar returns use the target Sun longitude and the target reference event as the annual recurrence anchor.

- Natal: birth event.
- Davison: real midpoint event.
- Composite: explicitly labeled synthetic midpoint reference event.

The exact return is to the target Sun longitude. Return-chart houses depend on the selected return location.

## Lunar returns

Lunar returns are range-based. A single package contains every exact Moon return between `--start` and `--end`.

Because an 18-month package contains roughly twenty charts, lunar returns use the `core_semantic_v1` return-chart profile: planets, angles, houses, core aspects, dignity/sect data, and a compact semantic graph are preserved, while expanded harmonic/antiscia material is omitted from each monthly chart.

## Eclipse/lunation

The pipeline emits all new/full moons, eclipse-season window classification, activation windows, total target-contact counts, retained top-contact counts, theme summaries, and indexes.

`total_activation_count` is the number of all qualifying contacts. `retained_activation_count` describes the compact top-contact array stored in `target_aspects`.

## Annual profections

Natal profections are the traditional/default use.

Composite and Davison profections are experimental relationship-entity techniques. Completed years are counted from the target reference event, and the package carries an explicit experimental flag and interpretation note.

## Validation

Use the full-package schemas for timing packages:

- `solar_return_dataset_v1.schema.json`
- `lunar_return_dataset_v1.schema.json`
- `eclipse_lunation_dataset_v1.schema.json`
- `annual_profections_dataset_v1.schema.json`

Compact Natal, Transit, and Synastry views have separate public schemas documented in `package_types.md`.

## Canonical temporal activation graph

Full and streaming Transit packages can be exported as:

```text
canonical_temporal_activation_graph.v1
```

This contract uses activation arcs as primary units and nests sampled states beneath them. It preserves activator/target directionality and distinguishes sampled exactness from solved exact-event timing.

Analysis views are rejected as temporal-source inputs because their ranked arc subset may be incomplete.

See `Canonical Temporal Activation Graph.md`.
