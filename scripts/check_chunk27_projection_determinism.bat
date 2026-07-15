@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
python scripts\check_chunk27_projection_determinism.py
