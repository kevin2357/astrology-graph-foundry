@echo off
setlocal
cd /d "%~dp0.."
python scripts\run_streaming_profiles_qa.py
exit /b %ERRORLEVEL%
