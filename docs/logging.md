# Logging

The SDK now uses Python's standard `logging` package.

## Default behavior

When invoked through the CLI, logging is configured automatically. The default config file is `logging.json` at the repository root. It writes DEBUG-and-above messages to:

```text
./astrology_analysis_sdk.log
```

The console handler only emits WARNING-and-above messages so long-running commands remain readable.

## Configuration search order

`astro_analysis_sdk.common.logging_config.configure_logging()` looks for configuration in this order:

1. explicit path passed to `configure_logging(path)`
2. `ASTRO_SDK_LOG_CONFIG`
3. `./logging.json`
4. repository-root `logging.json` in editable `src` layouts
5. built-in fallback writing `./astrology_analysis_sdk.log`

## Diagnosing long-running transit builds

For a command such as:

```cmd
python -m astro_analysis_sdk.cli transit --provider live --target-dataset kevin_natal_dataset.json --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path C:\dev\swisseph --out kevin_transit_period.json
```

watch the log with PowerShell:

```powershell
Get-Content .\astrology_analysis_sdk.log -Wait
```

or in `cmd.exe`:

```cmd
type astrology_analysis_sdk.log
```

The transit pipeline logs provider initialization, semantic graph construction, every tenth daily snapshot, daily-window collection, arc summarization, package-view construction, and JSON write start/finish. With default transit CLI behavior, `--out kevin_transit_period.json` writes `kevin_transit_period.analysis.json` and `kevin_transit_period.streaming_index.json`; full-detail JSON is written only when `--out-full` is provided.
