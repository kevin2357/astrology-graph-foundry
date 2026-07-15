# Astrology Graph Foundry

Astrology Graph Foundry is a Python SDK and CLI for ephemeris-backed calculation and production of canonical astrology graphs, structural evidence, timing source graphs, and saved multi-pipeline packages.

It is the source-data and calculation layer of a larger semantic ecosystem:

```text
Astrology Graph Foundry
        ↓
canonical source graphs and evidence
        ↓
Semantic Projection Core
        ↓
target-domain projected semantic graphs
```

Semantic Projection Core is maintained separately. This repository retains the saved-package adapters and CLI bridges that translate Foundry package structures into generic projection inputs.

## Current capabilities

Implemented pipelines include:

- Natal
- Transit
- Synastry
- Composite
- Davison
- Solar Return
- Lunar Return
- Annual Profections
- Eclipse/Lunation
- Timeline

Natal, Composite, and Davison packages implement the shared `TransitableChart` interface.

Major saved packages expose:

- `canonical_astrology_graph`
- `structural_evidence_graph`
- stable source identity and provenance
- pipeline-specific calculated data
- explicit projection boundaries

## Canonical temporal activation export

Transit packages can now be normalized into the projection-neutral:

```text
canonical_temporal_activation_graph.v1
```

The contract represents one temporal activation process as a directional arc with dated states, orb, motion, pass identity, exactness limitations, and provenance.

```bat
astro-package export-temporal-graph ^
  --source-dataset transit.full.json ^
  --out transit.canonical_temporal.json
```

The Foundry can also build the reserved cross-repository timing handoff:

```bat
astro-package export-temporal-projection-source ^
  --source-dataset transit.full.json ^
  --out transit.temporal_projection_source.json
```

Semantic Projection Core does not yet execute temporal projection. Static projection of Transit packages remains explicitly rejected until `projected_temporal_activation_graph.v1` is implemented downstream.

See:

- `docs/Canonical Temporal Activation Graph.md`
- `docs/Temporal Projection A-B-C Implementation Plan.md`

## Installation

### Graph, package, and projection development

```bat
python -m pip install -e .[dev]
```

The `dev` extra intentionally excludes Swiss Ephemeris so saved-package, graph, schema, adapter, and projection integration work does not require a native C build.

### Live chart calculation

```bat
python -m pip install -e .[live]
```

Or install the complete development surface:

```bat
python -m pip install -e .[full]
```

On Windows, wheel availability depends on Python and `pyswisseph` versions. See `docs/ideas_and_improvements.md` for the open packaging compatibility work.

### Semantic Projection Core sibling install

```bat
python -m pip install -e ..\semantic-projection-core
```

The Python import package remains:

```python
astro_analysis_sdk
```

## CLI

Primary command:

```bat
astro-package --help
```

Legacy module invocation remains available:

```bat
python -m astro_analysis_sdk.cli --help
```

## Documentation

Start with:

- `docs/architecture.md`
- `docs/SDK Developer Manual.md`
- `docs/package_types.md`
- `docs/timing_pipelines.md`
- `docs/Pre-Projection Semantic Boundary.md`
- `docs/Semantic Projection Integration.md`
- `docs/Canonical Temporal Activation Graph.md`

## Logging

Long-running commands write diagnostics through `logging.json`.

See:

```text
docs/logging.md
```
