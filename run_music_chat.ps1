$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Create the virtual environment and install dependencies as described in README.md.'
}
Push-Location $PSScriptRoot
try {
    & $python gemini_host.py --server mcp_server_music.py --ask-key --chat
} finally {
    Pop-Location
}
