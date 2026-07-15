# Legacy Note: Transit Period Dataset

The public pipeline has been unified and renamed to `transit`.

Use:

```bat
python -m astro_analysis_sdk.cli transit --provider live --target-dataset alex_natal_dataset.json --start 2026-01-01 --end 2027-07-01 --ephe-path C:\dev\swisseph --out alex_transit.json
```

For a single day:

```bat
python -m astro_analysis_sdk.cli transit --provider live --target-dataset alex_natal_dataset.json --date 2026-01-01 --ephe-path C:\dev\swisseph --out alex_2026-01-01_transit.json
```

Internally, the implementation may still reuse the historic `transit_period` module, but CLI users and downstream consumers should refer to the package as `transit`.

## TransitableChart target contract

The unified transit pipeline no longer accepts `--natal-dataset`. Use `--target-dataset` with a natal, composite, or Davison package. Output candidates and arcs use generic target fields rather than natal-only names. See `transitable_chart.md`.
