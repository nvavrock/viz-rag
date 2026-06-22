# Run viz-rag commands with the project venv (no activate.ps1 needed).
# If this script is blocked by ExecutionPolicy, use run.cmd instead:
#   .\scripts\run.cmd -m rag.ingest
# Or bypass policy for this script only:
#   powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1 -m rag.ingest
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Remaining
)

$Root = Split-Path $PSScriptRoot -Parent
$Py = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Py)) {
    Write-Error @"
.venv not found at $Py

Create and install:
  python -m venv .venv
  .venv\Scripts\python.exe -m pip install -e .
"@
    exit 1
}

& $Py @Remaining
exit $LASTEXITCODE
