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

## Installation health check

After installation, run:

```bat
astro-package doctor
```

For machine-readable diagnostics:

```bat
astro-package doctor --json
```

The command distinguishes saved-package/projection workflows from optional live Swiss Ephemeris calculation support.

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

The contract represents one temporal activation process as a directional arc with dated states, orb, motion, pass identity, exactness limitations, categorical strength labels, and provenance. The Foundry-side A/B temporal source boundary is stabilized as of version 0.4.2 for downstream temporal projection work.

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

Semantic Projection Core 0.10.0 provides the production temporal route from this bundle to `projected_temporal_activation_graph.v1`, including materialization and a deterministic route receipt. Static projection of Transit packages remains explicitly rejected because temporal packages must use that dedicated route.

See:

- `docs/Canonical Temporal Activation Graph.md`
- `docs/compatibility.md`

## Practical compact and long-window helpers

Solar Return can optionally emit a compact factual analysis view:

```bat
astro-package solar-return ... ^
  --out full_solar_return.json ^
  --out-analysis solar_return.analysis.json

REM Or compact an existing saved full package without recalculation:
astro-package solar-return-analysis ^
  --source-dataset full_solar_return.json ^
  --out solar_return.analysis.json
```

Long-window eclipse/lunation generation can mirror an annual or multi-month Transit window:

```bat
scripts\generate_long_window_lunations.bat ^
  --start 2026-01-01 ^
  --end 2027-07-01 ^
  --target-dataset natal.json ^
  --ephe-path C:\dev\swisseph ^
  --out lunations_2026_to_2027.json
```

Eclipse-season classifications remain explicit candidates until a global eclipse calculation confirms subtype and geometry.

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
astrology_graph_foundry
```

## CLI

Primary command:

```bat
astro-package --help
```

Legacy module invocation remains available:

```bat
python -m astrology_graph_foundry.cli --help
```

For guided common workflows with the same underlying CLI behavior, see `tools/README.md`. The `build_natal.py`, `build_transit.py`, `build_synastry.py`, and `build_temporal_source.py` tools support interactive prompting, unattended flags, and command-preview dry runs.

## Documentation

Start with:

- `docs/README.md`
- `docs/architecture.md`
- `docs/Astrology Graph Foundry Developer Manual.md`
- `docs/package_types.md`
- `docs/timing_pipelines.md`
- `docs/Semantic Projection Integration.md`
- `docs/Canonical Temporal Activation Graph.md`

## Logging

Long-running commands write diagnostics through `logging.json`.

See:

```text
docs/logging.md
```

## Transit streaming profiles

Transit streaming/index artifacts support `standard`, `compact`, and `game` retention profiles, optional deterministic gzip transport, and conservative gameplay source/target selection. See `docs/Transit Streaming Profiles and Game Index.md`.

## One-command QA

Place canonical fixtures in `tests/fixtures/qa_inputs` and run `scripts\run_streaming_profiles_qa.bat`. All generated artifacts and logs are written to `outputs/fixture_outputs`.
