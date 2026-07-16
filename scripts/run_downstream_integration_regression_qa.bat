@echo off
setlocal
cd /d "%~dp0.."
if not exist "outputs\fixture_outputs" mkdir "outputs\fixture_outputs"
python scripts\run_downstream_integration_regression_qa.py > "outputs\fixture_outputs\qa_runner.log" 2>&1
exit /b %ERRORLEVEL%
