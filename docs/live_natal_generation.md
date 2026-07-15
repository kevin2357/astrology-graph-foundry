# Live Natal Generation

The natal builder now supports both cached and live modes.

## Cached mode

Use a precomputed `Name_2026_Ephemeris.jsonl` file:

```bash
astro-package natal --provider cached --person-jsonl reverse_read_ephems\kevin_2026.jsonl --out kevin_natal_dataset.json
```

## Live mode from birth data

Compute the natal chart from scratch using Swiss Ephemeris and output the standard natal dataset directly:

```bash
astro-package natal --provider live --name Kevin --birth-local 1981-10-10T16:15:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path . --out kevin_natal_dataset.json
```

## Live mode with transit climate

Add a date range to include long-running transit climate in the same natal package:

```bash
astro-package natal --provider live --name Kevin --birth-local 1981-10-10T16:15:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path . --out kevin_natal_dataset_with_transit_climate.json
```

## Optional intermediate JSONL

The same live provider can persist a JSONL cache, but this is optional:

```bash
astro-package generate-ephemeris --name Kevin --birth-local 1981-10-10T16:15:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --start 2026-01-01 --end 2027-07-01 --persist-jsonl reverse_read_ephems\kevin_2026_2027_generated.jsonl
```

## Implementation notes

The live natal computation includes:

- planets and points,
- Placidus houses by default,
- ASC/DSC/MC/IC,
- Part of Fortune,
- Vertex when available,
- traditional and modern house rulers,
- natal planet-to-planet aspects,
- natal planet-to-angle aspects,
- natal planet-to-calculated-point aspects.

The output shape is intentionally compatible with cached JSONL natal records and the standard `natal_dataset`.
