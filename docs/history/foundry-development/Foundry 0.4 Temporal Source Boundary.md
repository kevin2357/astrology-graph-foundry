# Foundry 0.4 Temporal Source Boundary

## Completion summary

Astrology Graph Foundry 0.4 implements the Foundry-owned A and B stages of the official temporal-projection plan.

### A — canonical temporal source contract

Added:

```text
canonical_temporal_activation_graph.v1
```

with:

- directional activator and target references;
- arc-first temporal identity;
- sequence and pass identity;
- dated observation states;
- conservative applying/closest/separating phases;
- sampled exactness policy;
- direct/retrograde motion preservation;
- target chart identity;
- deterministic IDs, ordering, indexes, and diagnostics.

### B — Transit normalization adapter

Added:

```text
temporal_projection_source_bundle.v1
```

The adapter accepts complete full or streaming Transit materializations, normalizes package-specific timing structures, and packages the static source graph, structural evidence, source registries, and temporal graph for future Core consumption.

Analysis views are rejected because ranked/truncated arcs cannot provide a truthful complete temporal source contract.

### C — Semantic Projection Core

Not implemented in this repository.

The next Core pass should ingest the Foundry bundle and create:

```text
projected_temporal_activation_graph.v1
```

Static Transit projection remains rejected until that path exists.

## Additional project polish

- project-facing documentation now consistently uses Astrology Graph Foundry;
- README was rewritten around Foundry ownership;
- `dev` installation no longer requires `pyswisseph`;
- `live` owns Swiss Ephemeris;
- `full` installs both development and live dependencies;
- a real-corpus QA batch and temporal artifact inspector were added.

## Validation

The focused temporal contract tests cover:

- deterministic output;
- source immutability;
- repeated-pass segmentation;
- phase assignment;
- sampled exactness;
- direct/retrograde state;
- full and streaming materializations;
- analysis-view rejection;
- JSON Schema validation;
- Composite target handoff;
- source registry preservation.
