@echo off
setlocal EnableExtensions

rem Generate the eight representative Chunk 2.7 projections and all four
rem materializations. Each source package is projected once, then full,
rem standard, summary, and forensic artifacts are derived from that result.
rem
rem Run from the repository root:
rem     scripts\generate_chunk27_projection_qa.bat

cd /d "%~dp0\.."
set "OUT_DIR=scripts\outputs\chunk27_projection_qa"
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

python scripts\generate_chunk27_projection_qa.py > "%OUT_DIR%\chunk27_projection_generation.log" 2>&1
if errorlevel 1 (
  echo Generation failed. See %OUT_DIR%\chunk27_projection_generation.log
  exit /b 1
)

echo Generated Chunk 2.7 projection QA artifacts.
echo Log: %OUT_DIR%\chunk27_projection_generation.log
