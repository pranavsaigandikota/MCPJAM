param([switch]$CoreOnly)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable failed with exit code $LASTEXITCODE" }
}

$python = $null
$pythonArgs = @()
function Test-Python {
    param([string]$Candidate, [string[]]$CandidateArgs)
    try {
        & $Candidate @CandidateArgs -c "import sys,tkinter,struct; assert (3,10) <= sys.version_info[:2] <= (3,13); assert struct.calcsize('P') == 8" 2>$null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}
foreach ($version in @('3.13', '3.12', '3.11', '3.10')) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        if (Test-Python 'py' @("-$version")) { $python = 'py'; $pythonArgs = @("-$version"); break }
    }
}
if (-not $python -and (Get-Command python -ErrorAction SilentlyContinue)) {
    if (Test-Python 'python' @()) { $python = 'python' }
}
if (-not $python) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Install 64-bit Python 3.13 with Tk from python.org, then run setup.ps1 again.'
    }
    Invoke-Checked 'winget' @('install', '--id', 'Python.Python.3.13', '--exact', '--scope', 'user', '--silent', '--accept-package-agreements', '--accept-source-agreements')
    $python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'
    if (-not (Test-Path -LiteralPath $python)) { throw 'Python installed. Open a new terminal and run setup.ps1 again.' }
}
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    Invoke-Checked $python ($pythonArgs + @('-m', 'venv', '.venv'))
}
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$requirements = if ($CoreOnly) { 'requirements.txt' } else { 'requirements-audio.txt' }
Invoke-Checked $venvPython @('-m', 'pip', 'install', '--disable-pip-version-check', '-r', $requirements)
if (-not $CoreOnly) { Invoke-Checked $venvPython @('setup_audio.py') }
Invoke-Checked $venvPython @('workshop_preflight.py')
Write-Host 'Setup complete. Run: powershell -ExecutionPolicy Bypass -File .\run_app.ps1'
Write-Host 'Music chat: powershell -ExecutionPolicy Bypass -File .\run_music_chat.ps1'
