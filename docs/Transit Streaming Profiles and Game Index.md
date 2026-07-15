# Transit Streaming Profiles and Game Index

Astrology Graph Foundry supports three deterministic retention profiles for Transit streaming/index artifacts.

## Profiles

### `standard`

The legacy rich streaming/index materialization. It preserves the full candidate registry, activated-target relationship registry, day summaries, arcs, monthly summaries, and broad lookup metrics.

### `compact`

A general lightweight date-indexed artifact. It retains readable stable identifiers, a reduced candidate registry, a referenced subset of activated-target relationships, compact arcs, and monthly summaries while omitting repeated report-adjacent and forensic payloads.

### `game`

A mechanics-oriented artifact designed for round-by-round game access. It contains:

- one `days_by_date` lookup table;
- every source candidate eligible under the gameplay target/source policy;
- compact mutable daily contact values;
- a compact contact registry;
- a daily sky record containing sign, target-chart house, longitude, speed, and retrograde state;
- no report prose, full canonical graph, expanded relationship registry, or redundant reverse indexes.

The gameplay policy includes transiting Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, and True Node. Eligible targets include those bodies plus all four angles: ASC, DSC, MC, and IC. Lots, Mean Node, harmonics, antiscia/contra-antiscia points, and other research targets are excluded.

Foundry does not impose the final game-mechanics threshold. It retains every contact available in the source Transit package that satisfies the gameplay policy, including raw relevance and orb values. The game owns scoring and final filtering.

## CLI

Generate profiles directly while calculating a Transit package:

```bat
astro-package transit ... ^
  --streaming-profile game ^
  --transit-target-set gameplay ^
  --streaming-compression gzip ^
  --out-streaming-index player_transits.game.json
```

Materialize a profile from an existing full Transit package:

```bat
astro-package transit-streaming-view ^
  --source-dataset transit.full.json ^
  --streaming-profile compact ^
  --transit-target-set all ^
  --compression gzip ^
  --out transit.compact.json
```

Gzip output receives a `.gz` suffix when needed. Compression is deterministic: gzip timestamps and embedded source filenames are suppressed so identical inputs produce byte-identical compressed files.

## Target sets

- `core`: planets/luminaries, True Node, and four angles.
- `expanded`: broad non-harmonic targets.
- `all`: all candidates already present in the source package.
- `gameplay`: conservative game source/target policy described above.

These are Foundry source-selection policies, not Semantic Projection Core profiles.

## File organization

The `game` profile intentionally uses one indexed JSON file per player/window. A consumer can load the artifact once and retrieve the current round with:

```python
round_state = artifact["days_by_date"][current_date]
contacts = round_state["contacts"]
sky = round_state["daily_sky"]
```

## Compression

JSON structure reduction provides the largest semantic-size savings. Optional deterministic gzip transport compression then reduces repeated keys and registry references further. Consumers may use `gzip.open(..., "rt")` or Foundry's `read_json`, which transparently reads `.json.gz` files.
