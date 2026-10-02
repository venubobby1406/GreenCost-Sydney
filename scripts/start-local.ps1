param([string]$Python = '')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not $Python) {
    $availablePython = Get-Command python -ErrorAction SilentlyContinue
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if ($availablePython) { $Python = $availablePython.Source }
    elseif (Test-Path -LiteralPath $bundledPython) { $Python = $bundledPython }
    else { throw 'Install Python 3.12+, or supply -Python with its executable path.' }
}
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12+ is required.' }
}
$dependencyHash = (Get-FileHash -LiteralPath 'requirements-lock.txt' -Algorithm SHA256).Hash
$stampPath = '.venv\greencost-requirements.sha256'
if (-not (Test-Path -LiteralPath $stampPath) -or (Get-Content -LiteralPath $stampPath -Raw).Trim() -ne $dependencyHash) {
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    Set-Content -LiteralPath $stampPath -Value $dependencyHash
}
if (-not (Test-Path -LiteralPath 'frontend\node_modules')) {
    Push-Location frontend
    try { npm.cmd ci; if ($LASTEXITCODE -ne 0) { throw 'npm install failed.' } } finally { Pop-Location }
}
& '.\.venv\Scripts\python.exe' scripts\ingest_knowledge.py
if ($LASTEXITCODE -ne 0) { throw 'Knowledge ingestion failed.' }
$backendProcess = Start-Process -FilePath (Join-Path $projectRoot '.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot 'backend.log') -RedirectStandardError (Join-Path $projectRoot 'backend-error.log')
Write-Host 'Backend started on http://127.0.0.1:8000. Frontend will start on http://localhost:3000.'
try { Set-Location -LiteralPath (Join-Path $projectRoot 'frontend'); npm.cmd run dev } finally { Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue }
