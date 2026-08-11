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

Semantic Projection Core is maintained separately and consumes AGF's serialized
canonical and temporal source contracts. AGF does not import or execute SPC.

## Installation health check

After installation, run:

```bat
astro-package doctor
```

For machine-readable diagnostics:

```bat
astro-package doctor --json
```

The command distinguishes the dependency-light saved-package runtime from optional
live Swiss Ephemeris calculation support. Projection readiness is diagnosed by SPC
or by the orchestration environment that installs it.

Inspect the installed schema/resource inventory and its SHA-256 identities with:

```bat
astro-package runtime-manifest
```

Use `--out runtime-package-manifest.json` to retain the machine-readable report.
The command reads package resources through the installed distribution and does
not depend on a source-checkout path.

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

### Published immutable release

AGF 0.7.0 is available from the
[GitHub release](https://github.com/kevin2357/astrology-graph-foundry/releases/tag/astrology-graph-foundry-v0.7.0).
The wheel SHA-256 is
`fca6c153b14cd88f56ca9e151baf8d048cde4d3ac41a14af9912e3176fa52f53`.
Environments that also execute projection must independently pin the exact SPC
artifact. Live calculation must pin the qualified provider stack described in
[`docs/compatibility.md`](docs/compatibility.md).

### Graph, package, and projection development

```bat
python -m pip install -e .[dev]
```

The `dev` extra intentionally excludes Swiss Ephemeris so saved-package, graph, and schema work does not require a native C build.

### Live chart calculation

```bat
python -m pip install -e .[live]
```

Or install the complete development surface:

```bat
python -m pip install -e .[full]
```

On Windows, wheel availability depends on Python and `pyswisseph` versions. See `docs/ideas_and_improvements.md` for the open packaging compatibility work.

Semantic Projection Core is an independent downstream consumer and is not an AGF
runtime dependency. Install it only in an orchestration or compatibility-test
environment that owns projection execution.

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

Production Natal generation should supply an opaque, caller-owned chart identity:

```bat
astro-package natal ^
  --name Fido ^
  --birth-local 2020-05-17T14:30:00 ^
  --birth-timezone America/Denver ^
  --birth-lat 39.7392 ^
  --birth-lon -104.9903 ^
  --source-chart-id astrowoof:chart:01HX... ^
  --out fido.natal.json
```

`source_chart_id` is stable chart identity, not display metadata, a calculation
fingerprint, or projection context. Omitting it retains a deterministic
name-derived compatibility fallback that is unsuitable for durable production
joins. See `docs/Canonical Identity and Projection Context Ownership.md`.

For a known date with unknown birth time, the 0.7.0 release candidate can produce a
separate uncertainty-aware bounded artifact:

```bat
astro-package natal ^
  --provider live ^
  --name Fido ^
  --birth-time-unknown ^
  --birth-date 2020-05-17 ^
  --birth-timezone America/Denver ^
  --birth-lat 39.7392 ^
  --birth-lon -104.9903 ^
  --source-chart-id astrowoof:chart:01HX... ^
  --ephemeris-mode moshier ^
  --out fido.bounded-natal.json
```

Use `--birth-local-earliest` and `--birth-local-latest` instead when a narrower
interval is known. Bounded output intentionally omits exact longitudes, houses,
angles, sect, and dependent lots from its canonical graph. Current SPC/SBE and
timing consumers require follow-on compatibility work; see
[`docs/Bounded Birth-Time Natal Calculation.md`](docs/Bounded%20Birth-Time%20Natal%20Calculation.md).

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
