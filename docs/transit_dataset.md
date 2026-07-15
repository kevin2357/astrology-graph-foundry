# Unified Transit Dataset

The public transit command now covers both single-day and date-range transits.

- `--date YYYY-MM-DD` builds one daily window.
- `--start YYYY-MM-DD --end YYYY-MM-DD` builds a range.

The implementation delegates to the GraphCompiler-backed transit-period engine, but public docs and CLI usage should call the pipeline `transit`.

Default CLI output writes `.analysis.json` and `.streaming_index.json`. Use `--out-full` for audit-grade full output.

## TransitableChart target contract

The public transit command accepts `--target-dataset`. Natal, composite, and Davison packages can expose the common `TransitableChart` interface. Output metadata identifies target chart type and semantic scope; candidate fields use generic `target_*` naming.
