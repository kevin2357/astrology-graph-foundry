@echo off
setlocal

REM Generate the standard Kevin/Bre Foundry test package suite.
REM Usage:
REM   scripts\generate_kevin_bre_test_packages.bat [EPHE_PATH] [OUTPUT_DIR]
REM Example:
REM   scripts\generate_kevin_bre_test_packages.bat C:\dev\swisseph C:\dev\astro-package-test-outputs

set EPHE_PATH=%~1
if "%EPHE_PATH%"=="" set EPHE_PATH=C:\dev\swisseph

set OUT_DIR=%~2
if "%OUT_DIR%"=="" set OUT_DIR=outputs\kevin_bre_test

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo Writing test outputs to %OUT_DIR%
set /a tot_sets=3
set /a curr_set=1

rem echo [%curr_set%/%tot_sets%] Kevin 18-month transit compact outputs
rem python -m astrology_graph_foundry.cli transit-streaming-view --source-dataset "%OUT_DIR%\kevin_2026-01-01_to_2027-07-01_transit.streaming_index.json" --out "%OUT_DIR%" --streaming-profile game --target-set gameplay
rem set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Ashley temporal projection source from transit package
python -m astrology_graph_foundry.cli export-temporal-projection-source --source-dataset "%OUT_DIR%\ashley_2026-01-01_to_2027-07-01_transit.streaming_index.json" --out "%OUT_DIR%\ashley_temporal_projection_source.json" 
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Ashley temporal projection source from transit package
python -m astrology_graph_foundry.cli export-temporal-graph --source-dataset "%OUT_DIR%\ashley_2026-01-01_to_2027-07-01_transit.streaming_index.json" --out "%OUT_DIR%\ashley_temporal_graph.json" 
set /a curr_set+=1


echo [%curr_set%/%tot_sets%] Kevin temporal projection source from transit package
python -m astrology_graph_foundry.cli export-temporal-projection-source --source-dataset "%OUT_DIR%\kevin_2026-01-01_to_2027-07-01_transit.streaming_index.json" --out "%OUT_DIR%\kevin_temporal_projection_source.json" 
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin temporal projection source from transit package
python -m astrology_graph_foundry.cli export-temporal-graph --source-dataset "%OUT_DIR%\kevin_2026-01-01_to_2027-07-01_transit.streaming_index.json" --out "%OUT_DIR%\kevin_temporal_graph.json" 
set /a curr_set+=1



python -m astrology_graph_foundry.builders.build_transit_dataset --natal-dataset "outputs\kevin_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --streaming-profile game --target-set gameplay --out outputs --temporal-projection-out outputs\temporal_projection_source.json