# Foundry workflow tools

The scripts in this directory are human-friendly entry points for common Astrology Graph Foundry workflows. They prompt for missing required values in an interactive terminal and run entirely unattended when all required flags are supplied.

They orchestrate the canonical `astro-package` CLI. They do not implement calculation, graph compilation, materialization, or projection logic.

## Which interface should I use?

| Interface | Use it for |
|---|---|
| `tools/*.py` | Common interactive or readable one-workflow commands |
| `astro-package` | Stable automation, complete option control, integrations |
| `scripts/*` | Repository QA, fixtures, profiling, and project-specific batches |

Every tool supports `--help`, `--dry-run`, and `--non-interactive`. Dry runs validate inputs, create the selected output directory, and print the exact delegated command without calculation. Non-interactive mode fails instead of prompting when a required value is missing.

## Natal

```powershell
python tools/build_natal.py `
  --provider live `
  --name Kevin `
  --source-chart-id example:chart:kevin `
  --birth-local 1981-10-10T16:15:00 `
  --birth-timezone America/Denver `
  --birth-lat 39.7392 `
  --birth-lon -104.9903 `
  --birth-location-label "Denver, Colorado" `
  --ephe-path C:\dev\swisseph `
  --out-dir C:\dev\astro-packages\Kevin `
  --stem kevin_natal `
  --analysis
```

Cached mode uses `--provider cached --person-jsonl FILE`.

## Transit

```powershell
python tools/build_transit.py `
  --target C:\dev\astro-packages\Kevin\kevin_natal.full.json `
  --start 2026-01-01 `
  --end 2027-07-01 `
  --ephe-path C:\dev\swisseph `
  --out-dir C:\dev\astro-packages\Kevin\transits `
  --stem kevin_2026_to_2027 `
  --streaming-profile compact
```

Analysis and streaming outputs are standard. Add `--full` only when the large forensic package is needed.

## Synastry

```powershell
python tools/build_synastry.py `
  --mode saved `
  --person-a-natal person_a.full.json `
  --person-b-natal person_b.full.json `
  --out-dir relationship_outputs `
  --stem person_a_person_b
```

Use `--mode live` and the `--person-a-*` / `--person-b-*` birth flags to calculate both inputs live.

## Temporal source handoff

```powershell
python tools/build_temporal_source.py `
  --source transit.full.json `
  --out-dir temporal_outputs `
  --stem transit_2026
```

This writes both the Foundry canonical temporal graph and the projection-neutral SPC source bundle. It does not execute SPC projection. Use SPC's `tools/project_temporal.py` for the downstream projection route.
