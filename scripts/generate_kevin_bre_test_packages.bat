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
set /a tot_sets=45
set /a curr_set=1

echo [%curr_set%/%tot_sets%] Kevin natal
python -m astrology_graph_foundry.cli natal --provider live --name Kevin --birth-local 1981-10-10T16:15:00 --birth-timezone America/Denver --birth-lat 39.7392 --birth-lon -104.9903 --birth-location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_natal_dataset.json" --out-analysis "%OUT_DIR%\kevin_natal_dataset.analysis.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Bre natal
python -m astrology_graph_foundry.cli natal --provider live --name Bre --birth-local 1979-06-18T01:11:00 --birth-timezone America/Indiana/Indianapolis --birth-lat 39.7684 --birth-lon -86.1581 --birth-location-label "Indianapolis, Indiana" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\bre_natal_dataset.json" --out-analysis "%OUT_DIR%\bre_natal_dataset.analysis.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Brandi natal
python -m astrology_graph_foundry.cli natal --provider live --name Brandi --birth-local 1977-07-29T10:58:00 --birth-timezone America/Denver --birth-lat 39.6478 --birth-lon -104.9878 --birth-location-label "Englewood, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\brandi_natal_dataset.json" --out-analysis "%OUT_DIR%\brandi_natal_dataset.analysis.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Bre 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\bre_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\bre_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Brandi 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\brandi_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\brandi_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin 1-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --start 2026-01-01 --end 2026-02-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_2026-01-01_to_2026-02-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin 1-month full transit output
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --start 2026-01-01 --end 2026-02-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out-full "%OUT_DIR%\kevin_2026-01-01_to_2026-02-01_transit.full.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre synastry compact outputs
python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --out "%OUT_DIR%\kevin_bre_synastry_dataset.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre composite
python -m astrology_graph_foundry.cli composite --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --out "%OUT_DIR%\kevin_bre_composite_dataset.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Bre/Kevin full synastry
python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --out-full "%OUT_DIR%\bre_kevin_synastry_dataset.full.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi synastry compact outputs
python -m astrology_graph_foundry.cli synastry --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --out "%OUT_DIR%\kevin_brandi_synastry_dataset.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi composite
python -m astrology_graph_foundry.cli composite --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --out "%OUT_DIR%\kevin_brandi_composite_dataset.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --target-date 2026-07-07 --out "%OUT_DIR%\kevin_2026_profections.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin 2026 solar return
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Bre 2026 solar return in Denver
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\bre_natal_dataset.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\bre_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Brandi 2026 solar return in Denver
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\brandi_natal_dataset.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\brandi_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre Davison relationship chart
python -m astrology_graph_foundry.cli davison --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\bre_natal_dataset.json" --out "%OUT_DIR%\kevin_bre_davison.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi Davison relationship chart
python -m astrology_graph_foundry.cli davison --person-a-natal-dataset "%OUT_DIR%\kevin_natal_dataset.json" --person-b-natal-dataset "%OUT_DIR%\brandi_natal_dataset.json" --out "%OUT_DIR%\kevin_brandi_davison.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin 18-month eclipse/lunation package
python -m astrology_graph_foundry.cli eclipse-lunation --target-dataset "%OUT_DIR%\kevin_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_2026-01-01_to_2027-07-01_lunations.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre Davison 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_bre_davison.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin+bre+davison+entity_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi Davison 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_brandi_davison.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin+brandi+davison+entity_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1


echo [%curr_set%/%tot_sets%] Kevin/Bre composite 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_bre_composite_dataset.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin+bre+composite+entity_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi composite 18-month transit compact outputs
python -m astrology_graph_foundry.cli transit --provider live --target-dataset "%OUT_DIR%\kevin_brandi_composite_dataset.json" --start 2026-01-01 --end 2027-07-01 --timezone America/Denver --snapshot-time 12:00 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin+brandi+composite+entity_2026-01-01_to_2027-07-01_transit.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre composite 2026 solar return
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\kevin_bre_composite_dataset.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_bre_composite_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre Davison 2026 solar return
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\kevin_bre_davison.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_bre_davison_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi composite 2026 solar return
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\kevin_brandi_composite_dataset.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_brandi_composite_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi Davison 2026 solar return
python -m astrology_graph_foundry.cli solar-return --target-dataset "%OUT_DIR%\kevin_brandi_davison.json" --return-year 2026 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_brandi_davison_2026_solar_return.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre composite 2026 eclipse/lunation package
python -m astrology_graph_foundry.cli eclipse-lunation --target-dataset "%OUT_DIR%\kevin_bre_composite_dataset.json" --start 2026-01-01 --end 2027-07-01 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_bre_composite_2026-01-01_to_2027-07-01_lunations.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre Davison 2026 eclipse/lunation package
python -m astrology_graph_foundry.cli eclipse-lunation --target-dataset "%OUT_DIR%\kevin_bre_davison.json" --start 2026-01-01 --end 2027-07-01 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_bre_davison_2026-01-01_to_2027-07-01_lunations.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi composite 2026 eclipse/lunation package
python -m astrology_graph_foundry.cli eclipse-lunation --target-dataset "%OUT_DIR%\kevin_brandi_composite_dataset.json" --start 2026-01-01 --end 2027-07-01 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_brandi_composite_2026-01-01_to_2027-07-01_lunations.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi Davison 2026 eclipse/lunation package
python -m astrology_graph_foundry.cli eclipse-lunation --target-dataset "%OUT_DIR%\kevin_brandi_davison.json" --start 2026-01-01 --end 2027-07-01 --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_brandi_davison_2026-01-01_to_2027-07-01_lunations.json"
set /a curr_set+=1



echo [%curr_set%/%tot_sets%] Bre 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\bre_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\bre_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Brandi 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\brandi_natal_dataset.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\brandi_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre composite 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\kevin_bre_composite_dataset.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_bre_composite_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre Davison 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\kevin_bre_davison.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_bre_davison_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi composite 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\kevin_brandi_composite_dataset.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_brandi_composite_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi Davison 18-month lunar returns
python -m astrology_graph_foundry.cli lunar-return --target-dataset "%OUT_DIR%\kevin_brandi_davison.json" --start 2026-01-01 --end 2027-07-01 --return-location-policy explicit --location-timezone America/Denver --location-lat 39.7392 --location-lon -104.9903 --location-label "Denver, Colorado" --ephe-path "%EPHE_PATH%" --out "%OUT_DIR%\kevin_brandi_davison_lunar_returns_2026-01-01_to_2027-07-01.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Bre annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\bre_natal_dataset.json" --target-date 2026-07-07 --out "%OUT_DIR%\bre_2026_profections.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Brandi annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\brandi_natal_dataset.json" --target-date 2026-07-07 --out "%OUT_DIR%\brandi_2026_profections.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre composite annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\kevin_bre_composite_dataset.json" --target-date 2026-07-07 --out "%OUT_DIR%\kevin_bre_composite_2026_profections.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Bre Davison annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\kevin_bre_davison.json" --target-date 2026-07-07 --out "%OUT_DIR%\kevin_bre_davison_2026_profections.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi composite annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\kevin_brandi_composite_dataset.json" --target-date 2026-07-07 --out "%OUT_DIR%\kevin_brandi_composite_2026_profections.json"
set /a curr_set+=1

echo [%curr_set%/%tot_sets%] Kevin/Brandi Davison annual profection for 2026-07-07
python -m astrology_graph_foundry.cli annual-profections --target-dataset "%OUT_DIR%\kevin_brandi_davison.json" --target-date 2026-07-07 --out "%OUT_DIR%\kevin_brandi_davison_2026_profections.json"
set /a curr_set+=1


echo Done.
endlocal
