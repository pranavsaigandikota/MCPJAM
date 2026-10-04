$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Create the virtual environment and install dependencies as described in README.md.'
}
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & $python -m MCPJAM
} finally {
    Pop-Location
}
