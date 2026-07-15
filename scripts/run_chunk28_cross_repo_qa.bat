@echo off
setlocal
python -m pytest -q
if errorlevel 1 exit /b %errorlevel%
python scripts\inspect_projection_extraction_readiness.py > chunk28_extraction_readiness.json
if errorlevel 1 exit /b %errorlevel%
python examples\projection_cross_profile_chunk26.py > chunk28_cross_profile_projection.json
if errorlevel 1 exit /b %errorlevel%
echo Chunk 2.8 Foundry integration QA complete.
