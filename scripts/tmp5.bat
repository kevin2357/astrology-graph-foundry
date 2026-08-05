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
set /a tot_sets=4
set /a curr_set=1

echo [%curr_set%/%tot_sets%] Kevin natal
python -m astrology_graph_foundry.cli natal --provider live --name Kevin --birth-local 1981-10-10T16:15:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_natal_dataset.full.json" 
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Bre natal
python -m astrology_graph_foundry.cli natal --provider live --name Bre --birth-local 1979-06-18T01:11:00 --birth-timezone America/Indiana/Indianapolis --birth-lat 39.7684 --birth-lon -86.1581 --birth-location-label "Indianapolis, Indiana" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\bre_natal_dataset.full.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Brandi natal
python -m astrology_graph_foundry.cli natal --provider live --name Brandi --birth-local 1977-07-29T10:58:00 --birth-timezone America/Denver --birth-lat 39.6478 --birth-lon -104.9878 --birth-location-label "Englewood, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\brandi_natal_dataset.full.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Ashley natal
python -m astrology_graph_foundry.cli natal --provider live --name Ashley --birth-local "1979-06-19T18:09:00" --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\ashley_natal_dataset.full.json"
set /a curr_set+=1

echo Done.
endlocal
