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
if "%OUT_DIR%"=="" set OUT_DIR=outputs\kevin_ashley_game_files
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo Writing test outputs to %OUT_DIR%
set /a tot_sets=3
set /a curr_set=1

python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\ashley_natal_dataset.json" --out "%OUT_DIR%\kevin_ashley_synastry_dataset.json"

python -m astrology_graph_foundry.cli synastry --person-b-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-a-natal-dataset "%OUT_DIR%\ashley_natal_dataset.json" --out "%OUT_DIR%\ashley_kevin_synastry_dataset.json"

python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --out "%OUT_DIR%\brandi_bre_synastry_dataset.json"

python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --out "%OUT_DIR%\bre_brandi_synastry_dataset.json"
