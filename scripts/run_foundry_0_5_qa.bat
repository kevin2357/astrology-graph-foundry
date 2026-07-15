@echo off
setlocal
set OUTDIR=scripts\outputs\foundry_0_5_qa
if not exist "%OUTDIR%" mkdir "%OUTDIR%"

echo [1/3] Test suite
python -m pytest -q > "%OUTDIR%\foundry_0_5_pytest.log"
if errorlevel 1 exit /b %ERRORLEVEL%

echo [2/3] Installation doctor
python -m astrology_graph_foundry.cli doctor > "%OUTDIR%\foundry_0_5_doctor.log"
if errorlevel 1 exit /b %ERRORLEVEL%
python -m astrology_graph_foundry.cli doctor --json > "%OUTDIR%\foundry_0_5_doctor.json"
if errorlevel 1 exit /b %ERRORLEVEL%

echo [3/3] Complete
echo Wrote Foundry 0.5 QA artifacts under %OUTDIR%
