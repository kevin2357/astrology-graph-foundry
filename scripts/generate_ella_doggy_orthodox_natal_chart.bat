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
if "%OUT_DIR%"=="" set OUT_DIR=..\outputs\elllabear

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo Writing outputs to %OUT_DIR%
set /a tot_sets=1
set /a curr_set=1

echo [%curr_set%/%tot_sets%] Ella natal
python -m astrology_graph_foundry.cli natal --provider live --name Ella --birth-local 2015-08-26T12:00:00 --birth-timezone America/Denver --birth-lat 38.7422 --birth-lon -108.0690 --birth-location-label "Delta, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\ella_canonical_natal_graph.json" --out-analysis "%OUT_DIR%\ella_canonical_natal_graph.analysis.json"
set /a curr_set+=1

