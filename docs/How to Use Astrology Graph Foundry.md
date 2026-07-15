# How to Use the Astrology Graph Foundry

> **Pass 2 documentation map**
>
> This quick-start is intentionally narrow: use it when you want to run commands. For conceptual/developer guidance, see [`Astrology Graph Foundry Developer Manual.md`](Astrology%20Graph%20Foundry%20Developer%20Manual.md). For the system-wide architecture, see [`Astrology Ecosystem Architecture.md`](Astrology%20Ecosystem%20Architecture.md). For downstream domain translation, see [`Projection Layer Architecture.md`](Projection%20Layer%20Architecture.md). For standard report products and `report_view.json`, see [`Report Blueprint Specification.md`](Report%20Blueprint%20Specification.md). For evidence objects and graph philosophy, see [`Semantic Graph Philosophy.md`](Semantic%20Graph%20Philosophy.md). For the long-term synthesis/research layer, see [`Multi-Pipeline Semantic Synthesis.md`](Multi-Pipeline%20Semantic%20Synthesis.md). For concrete package-combination examples, see [`Consumer Cookbook.md`](Consumer%20Cookbook.md).


> **Documentation status note**
>
> This file is the current practical quick-start for the Astrology Graph Foundry. It is intentionally preserved as a stable, command-oriented reference. A new long-form companion document, [`Astrology Graph Foundry Developer Manual.md`](Astrology%20Graph%20Foundry%20Developer%20Manual.md), is being developed as the richer conceptual/developer handbook. Once that manual is mature, it may replace or absorb this guide. Until then, this document remains the concise "how do I run it?" reference.


This SDK is designed around a simple separation of concerns:

1. **Astronomical calculation** — Swiss Ephemeris or cached ephemeris inputs produce deterministic chart facts.
2. **Analysis package compilation** — chart facts are promoted into structured JSON packages with semantic graphs, relationship types, evidence, registries, and report materials.
3. **Downstream consumption** — report writers, CFANFF reverse reads, OMTA/projected-chart generation, infographics, timelines, and game engines read those packages instead of recomputing astrology.

The project standard is: preserve audit-grade facts, use stable IDs, avoid repeated payloads in compact outputs, and make semantic reasoning explicit through graph objects, relationship types, theme tags, operator hints, evidence claims, and report materials.

## Invocation styles

### Non-installed CLI from a repo checkout

```bat
python -m astrology_graph_foundry.cli natal --provider live --name Alex Example --birth-local 1990-04-12T09:30:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path C:\dev\swisseph --out alex_natal_dataset.json
```

### Installed CLI

```bat
astro-package natal --provider live --name Alex Example --birth-local 1990-04-12T09:30:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path C:\dev\swisseph --out alex_natal_dataset.json
```

### Python import from another project

```python
from astrology_graph_foundry.pipelines import natal, transit, synastry

alex = natal.build(
    provider="live",
    name="Alex Example",
    birth_local="1990-04-12T09:30:00",
    birth_timezone="America/Denver",
    birth_lat=39.7392,
    birth_lon=-104.9903,
    birth_location_label="Denver, Colorado",
    ephe_path=r"C:\dev\swisseph",
)

transit_pkg = transit.build(
    start="2026-01-01",
    end="2026-02-01",
    provider="live",
    natal_dataset=alex,
    ephe_path=r"C:\dev\swisseph",
)
analysis = transit.analysis_view(transit_pkg)
```

## Output types

Several pipelines support multiple physicalized output views.

- **Full**: audit/research-grade package. Preserves the richest data, but can be large. Usually opt-in through `--out-full`.
- **Analysis**: compact report-consumer view. Keeps the highest-value facts, metrics, evidence, summaries, and registries.
- **Streaming/indexed**: compact lookup-oriented view for game engines, dashboards, and interactive consumers. Uses registries and ID indexes so callers can resolve contacts/windows without loading a giant repeated matrix.

## Natal packages

Natal is the foundation package. It computes a full chart and promotes the chart into a semantic graph.

```bat
python -m astrology_graph_foundry.cli natal --provider live --name Alex Example --birth-local 1990-04-12T09:30:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path C:\dev\swisseph --out alex_natal_dataset.json
```

Important sections:

- `metadata`: package identity and version.
- `natal`: bodies, houses, angles, aspects, lots, dignities, declinations, antiscia, harmonics, and optional points.
- `semantic_graph`: first-class graph objects and relationships.
- `report_materials`: pre-chewed summary material for downstream prose/report layers.

## Unified transit pipeline

The public command is now **`transit`**. A single-day transit and a date-range transit use the same underlying pipeline.

Single day:

```bat
python -m astrology_graph_foundry.cli transit --provider live --target-dataset alex_natal_dataset.json --date 2026-01-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path C:\dev\swisseph --out alex_2026-01-01_transit.json
```

Date range:

```bat
python -m astrology_graph_foundry.cli transit --provider live --target-dataset alex_natal_dataset.json --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path C:\dev\swisseph --out alex_2026_to_2027_transit.json
```

By default this writes:

```text
alex_2026_to_2027_transit.analysis.json
alex_2026_to_2027_transit.streaming_index.json
```

Full output is opt-in:

```bat
python -m astrology_graph_foundry.cli transit --provider live --target-dataset alex_natal_dataset.json --start 2026-01-01 --end 2026-02-01 --ephe-path C:\dev\swisseph --out-full alex_transit_full.json
```

## Synastry and composite

Synastry compares two natal graphs directionally. Composite creates a midpoint relationship chart.

```bat
python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset alex_natal_dataset.json --person-b-natal-dataset blair_natal_dataset.json --out alex_blair_synastry.json
python -m astrology_graph_foundry.cli composite --person-a-natal-dataset alex_natal_dataset.json --person-b-natal-dataset blair_natal_dataset.json --out alex_blair_composite.json
```

Synastry defaults to:

```text
alex_blair_synastry.analysis.json
alex_blair_synastry.streaming_index.json
```

Use `--out-full` for the full research matrix.

Both commands can also compute the two natal charts live from birth data:

```bat
python -m astrology_graph_foundry.cli synastry ^
  --person-a-provider live --person-a-name Alex Example --person-a-birth-local 1990-04-12T09:30:00 --person-a-birth-timezone America/Denver --person-a-birth-lat 39.7392 --person-a-birth-lon -104.9903 ^
  --person-b-provider live --person-b-name Blair Example --person-b-birth-local 1988-09-03T21:15:00 --person-b-birth-timezone America/New_York --person-b-birth-lat 40.7128 --person-b-birth-lon -74.0060 ^
  --ephe-path C:\dev\swisseph --out alex_blair_synastry.json
```

## Simple timing / relationship pipelines

### Annual profections

```bat
python -m astrology_graph_foundry.cli annual-profections --target-dataset alex_natal_dataset.json --target-date 2026-04-12 --out alex_2026_profections.json
```

Annual profections activate a house by completed age and identify a time lord from the natal house/sign metadata.

### Solar return

```bat
python -m astrology_graph_foundry.cli solar-return --target-dataset alex_natal_dataset.json --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path C:\dev\swisseph --out alex_2026_solar_return.json
```

A solar return chart is cast for the exact moment the transiting Sun returns to the natal Sun longitude.

### Lunar return

```bat
python -m astrology_graph_foundry.cli lunar-return --target-dataset alex_natal_dataset.json --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path C:\dev\swisseph --out alex_lunar_returns_2026-01-01_to_2027-07-01.json
```

A lunar return chart is cast for the nearest moment the transiting Moon returns to the natal Moon longitude.

### Davison relationship chart

```bat
python -m astrology_graph_foundry.cli davison --person-a-natal-dataset alex_natal_dataset.json --person-b-natal-dataset blair_natal_dataset.json --ephe-path C:\dev\swisseph --out alex_blair_davison.json
```

Davison uses the midpoint in birth time and location, then casts a real chart for that synthetic event.

### Eclipse/lunation calendar

```bat
python -m astrology_graph_foundry.cli eclipse-lunation --start 2026-01-01 --end 2026-12-31 --target-dataset alex_natal_dataset.json --ephe-path C:\dev\swisseph --out alex_2026_lunations.json
```

The eclipse/lunation pipeline scans an explicit date range, identifies each new and full moon, classifies node-proximity eclipse-season windows, adds ±3-day activation windows, and records contacts to any natal, composite, or Davison TransitableChart target. The node-distance classification is intentionally described as an eclipse window rather than asserting global visibility or exact eclipse subtype.

## Scaffolded future pipelines

```bat
python -m astrology_graph_foundry.cli progressed --out progressed_scaffold.json
python -m astrology_graph_foundry.cli solar-arc --out solar_arc_scaffold.json
```

These intentionally return scaffold packages until secondary progressions and solar arc directions receive full design/implementation passes.

## How to read a package

```python
import json
from pathlib import Path

pkg = json.loads(Path("alex_blair_synastry.analysis.json").read_text(encoding="utf-8"))
print(pkg["metadata"]["analysis_type"])
for row in pkg.get("top_synastry_aspects", [])[:10]:
    themes = pkg["theme_registry"].get(row.get("theme_key"), [])
    operators = pkg["operator_registry"].get(row.get("operator_key"), [])
    print(row["id"], row.get("aspect"), themes, operators)
```

## How to read a schema

Schemas live in `src/astrology_graph_foundry/schemas`. Start with:

- `metadata.analysis_type`: identifies package kind.
- required top-level sections: minimum contract.
- `additionalProperties: true`: many schemas intentionally permit richer experimental data while stable fields mature.

Toy schema validation:

```python
import json
from pathlib import Path
from jsonschema import validate

pkg = json.loads(Path("alex_2026_to_2027_transit.analysis.json").read_text())
schema = json.loads(Path("src/astrology_graph_foundry/schemas/transit_dataset_v1.schema.json").read_text())
validate(pkg, schema)
```

## Logging

The CLI configures logging automatically. Progress and debug details are written to `astrology_graph_foundry.log` in the current working directory by default. See `docs/logging.md`.

## Batch test script

For the recurring Kevin/Bre smoke-test package suite, use:

```bat
scripts\generate_kevin_bre_test_packages.bat C:\dev\swisseph outputs\kevin_bre_test
```

The script generates Kevin natal, Bre natal, Kevin compact/full transit samples, Kevin/Bre synastry compact outputs, Kevin/Bre composite, and a reversed full synastry package.


# Conceptual Guide: Choosing Pipelines

A useful way to think about the SDK is not as a collection of astrology techniques but as a collection of semantic observers. Each pipeline answers a different question and therefore contributes different evidence.

| Category | Pipeline | Question |
|---|---|---|
| Identity | Natal | Who is this person? |
| Relationship | Synastry | How do these people interact? |
| Relationship | Composite | What relationship entity emerges? |
| Relationship | Davison | If that relationship were a real entity, who would it be? |
| Long-cycle timing | Solar Return | What themes define this year? |
| Mid-cycle timing | Annual Profections | Which life subsystem is foregrounded this year? |
| Mid-cycle timing | Lunar Return | What themes define this month? |
| Short-cycle timing | Transit | What is active now? |
| Short-cycle timing | Eclipse/Lunation | Where are major activation windows? |

Typical consumer combinations:

- Daily reading: Natal + Transit.
- Monthly reading: Natal + Lunar Return + Transit.
- Yearly reading: Natal + Solar Return + Annual Profections + Transit + Eclipse/Lunation.
- Relationship reading: Both Natals + Synastry + Composite + Davison.

Analysis views are the preferred starting point for report writers. Streaming views are intended for interactive consumers. Full views prioritize auditability and research.

See also: Multi-Pipeline Semantic Synthesis.


### Relationship-entity timing

Because Composite and Davison packages implement `TransitableChart`, the same timing pipelines can target them directly:

```bat
python -m astrology_graph_foundry.cli transit --provider live --target-dataset kevin_bre_composite_dataset.json --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --ephe-path C:\dev\swisseph --out kevin_bre_composite_transit.json

python -m astrology_graph_foundry.cli solar-return --target-dataset kevin_bre_davison.json --return-year 2026 --return-location-policy target_reference --ephe-path C:\dev\swisseph --out kevin_bre_davison_solar_return.json

python -m astrology_graph_foundry.cli eclipse-lunation --target-dataset kevin_bre_composite_dataset.json --start 2026-01-01 --end 2027-07-01 --ephe-path C:\dev\swisseph --out kevin_bre_composite_lunations.json
```

The target metadata distinguishes individual climate, relationship-pattern climate, and relationship-lifecycle climate.


### Generic lunar returns and profections

`lunar-return` now accepts a `TransitableChart` target and an explicit date range. It emits every exact Moon return inside the range, with indexes by ID and month. Natal targets produce individual monthly climate; Composite and Davison targets produce relationship-pattern and relationship-lifecycle monthly climate.

`annual-profections` also accepts `--target-dataset`. Natal use is traditional. Relationship-entity profections are explicitly labeled experimental: Davison counts completed years from the real midpoint event, while Composite counts from the synthetic midpoint reference event.

```bat
python -m astrology_graph_foundry.cli lunar-return --target-dataset kevin_bre_davison.json --start 2026-01-01 --end 2027-07-01 --return-location-policy target_reference --ephe-path C:\dev\swisseph --out kevin_bre_davison_lunar_returns.json

python -m astrology_graph_foundry.cli annual-profections --target-dataset kevin_bre_composite_dataset.json --target-date 2026-07-07 --out kevin_bre_composite_profections.json
```


See [`timing_pipelines.md`](timing_pipelines.md) for the common timing-target model, semantic scopes, and range-output behavior.


## Mandatory return-location policy

Solar and Lunar Return commands require `--return-location-policy`. The SDK intentionally does not silently choose a return-chart location because houses and angles depend on that choice.

Use:

```bat
--return-location-policy target_reference
```

for simple testing or when the `TransitableChart.reference_event` location is intentionally desired.

Use:

```bat
--return-location-policy explicit ^
--location-timezone America/Denver ^
--location-lat 39.7392 ^
--location-lon -104.9903 ^
--location-label "Denver, Colorado"
```

when the return should be cast for a lived/event location. All four explicit location fields are required under the `explicit` policy.
