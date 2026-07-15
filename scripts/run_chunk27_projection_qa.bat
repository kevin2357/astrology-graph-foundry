@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."

call scripts\generate_chunk27_projection_qa.bat
if errorlevel 1 exit /b 1

call scripts\profile_chunk27_projection_outputs.bat
if errorlevel 1 exit /b 1

call scripts\check_chunk27_projection_determinism.bat
if errorlevel 1 exit /b 1

echo Chunk 2.7 projection QA generation, profiling, and determinism check complete.
