@echo off
setlocal

set EPHE_PATH=%~1
if "%EPHE_PATH%"=="" set EPHE_PATH=C:\dev\swisseph

set OUT_DIR=%~2
if "%OUT_DIR%"=="" set OUT_DIR=outputs\kevin_ashley_game_files
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo Writing test outputs to %OUT_DIR%

python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --out-full "%OUT_DIR%\brandi_bre_synastry_dataset.full.json"

python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --out-full "%OUT_DIR%\bre_brandi_synastry_dataset.full.json"
