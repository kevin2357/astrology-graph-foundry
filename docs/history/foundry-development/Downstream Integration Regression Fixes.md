# Downstream Integration Regression Fixes

This pass fixes two defects exposed by the Astrology Graph Foundry → Semantic Projection Core → Mythos integration.

## Temporal projection source bundles

`export-temporal-projection-source` now requires a complete canonical target graph.

- Full Transit packages may provide the graph inline.
- Compact/standard streaming indexes normally require `--target-dataset` pointing to the authoritative Natal, Composite, or Davison package.
- The exporter rejects missing graphs and target-identity mismatches.
- `--transit-target-set` makes source selection explicit and auditable. `gameplay` includes Sun through Pluto, True Node, and all four angles as targets; Mean Node, lots, harmonics, antiscia, and other expanded targets are excluded.

The bundle records both the target-set policy and whether the static graph came from an embedded full package or an explicit target dataset.

## Streaming-index rematerialization

`transit-streaming-view` can now consume an existing standard streaming index, not only a full Transit package. It hydrates daily candidate references through `candidate_registry`, preserves every requested date (including empty-contact dates), and produces populated compact/game indexes.

Newly generated standard streaming indexes embed compact `daily_sky` records so they can later be rematerialized into a complete game artifact without a full package.

Legacy standard indexes may not contain daily sky positions. For those, pass:

```bat
--full-transit-dataset path\to\transit.full.json
```

The full package is used only to restore daily sky positions; contacts and candidate identity remain sourced from the standard index.

## Authoritative ownership

- Foundry owns source selection, factual geometry, canonical target identity, and daily sky state.
- Semantic Projection Core owns projected temporal meaning.
- Mythos owns final gameplay thresholds and mechanics.

## QA

Run:

```bat
scripts\run_downstream_integration_regression_qa.bat
```

All artifacts and logs are written to `outputs/fixture_outputs`.
