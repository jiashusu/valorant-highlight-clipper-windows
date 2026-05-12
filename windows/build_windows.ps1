$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher py was not found. Install Python 3.10 or 3.11 first."
}

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller pytest

$env:PYTHONPATH = Join-Path $ProjectRoot "src"
& ".\.venv\Scripts\python.exe" -m pytest tests
& ".\.venv\Scripts\pyinstaller.exe" --clean --noconfirm "windows\ValorantHighlightClipper-windows.spec"

$ReleaseDir = Join-Path $ProjectRoot "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
Copy-Item "dist\ValorantHighlightClipper.exe" (Join-Path $ReleaseDir "ValorantHighlightClipper.exe") -Force
Copy-Item "README.md" (Join-Path $ReleaseDir "README.md") -Force
Copy-Item "DEVELOPMENT_LOG.md" (Join-Path $ReleaseDir "DEVELOPMENT_LOG.md") -Force
Get-ChildItem -LiteralPath $ProjectRoot -Filter "*.txt" -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $ReleaseDir $_.Name) -Force
}

Write-Host "Build complete: $ReleaseDir\ValorantHighlightClipper.exe"
