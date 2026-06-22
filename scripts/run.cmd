@echo off
REM Run viz-rag with project venv (no PowerShell activate needed).
REM Usage: scripts\run.cmd -m rag.ingest

set "ROOT=%~dp0.."
set "PY=%ROOT%\.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo .venv not found. Run:
  echo   python -m venv .venv
  echo   .venv\Scripts\python.exe -m pip install -e .
  exit /b 1
)

"%PY%" %*
exit /b %ERRORLEVEL%
