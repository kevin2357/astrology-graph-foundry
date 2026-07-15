@echo off
setlocal
set "CORE_DIR=%~dp0..\..\semantic-projection-core"
if not exist "%CORE_DIR%\pyproject.toml" (
  echo ERROR: Expected sibling Semantic Projection Core at "%CORE_DIR%"
  exit /b 1
)
python -m pip install -e "%CORE_DIR%[dev]"
if errorlevel 1 exit /b %errorlevel%
echo Installed Semantic Projection Core from %CORE_DIR%
