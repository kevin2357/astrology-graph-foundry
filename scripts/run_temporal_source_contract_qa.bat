@echo off
setlocal

set "SOURCE=scripts\outputs\kevin_bre_test\kevin_2026-01-01_to_2026-02-01_transit.full.json"
set "OUT_DIR=scripts\outputs\temporal_source_contract_qa"

if not exist "%SOURCE%" (
  echo Missing required full Transit package:
  echo   %SOURCE%
  exit /b 1
)

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo [1/4] Export canonical temporal activation graph
python -m astro_analysis_sdk.cli export-temporal-graph ^
  --source-dataset "%SOURCE%" ^
  --out "%OUT_DIR%\kevin_2026-01_canonical_temporal.json"
if errorlevel 1 exit /b 1

echo [2/4] Export temporal projection source bundle
python -m astro_analysis_sdk.cli export-temporal-projection-source ^
  --source-dataset "%SOURCE%" ^
  --out "%OUT_DIR%\kevin_2026-01_temporal_projection_source.json"
if errorlevel 1 exit /b 1

echo [3/4] Inspect canonical temporal graph
python scripts\inspect_temporal_source_contract.py ^
  "%OUT_DIR%\kevin_2026-01_canonical_temporal.json" ^
  --out "%OUT_DIR%\kevin_2026-01_canonical_temporal.inspect.json"
if errorlevel 1 exit /b 1

echo [4/4] Inspect temporal projection source bundle
python scripts\inspect_temporal_source_contract.py ^
  "%OUT_DIR%\kevin_2026-01_temporal_projection_source.json" ^
  --out "%OUT_DIR%\kevin_2026-01_temporal_projection_source.inspect.json"
if errorlevel 1 exit /b 1

echo Temporal source-contract QA complete.
endlocal
