@echo off
setlocal
python scripts\generate_long_window_lunations.py %*
exit /b %ERRORLEVEL%
