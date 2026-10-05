param([string]$Python = '', [switch]$Production, [switch]$SetupOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
function Assert-PortAvailable([int]$Port) {
    $portProbe = [System.Net.Sockets.TcpClient]::new()
    try { $portProbe.Connect('127.0.0.1', $Port); throw "Port $Port is already in use. Stop the previous GreenCost server or the app using that port." }
    catch [System.Net.Sockets.SocketException] { }
    finally { $portProbe.Dispose() }
}
if (-not $SetupOnly) { foreach ($port in @(8000, 3000)) { Assert-PortAvailable $port } }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Install Node.js 22 LTS from nodejs.org, then reopen PowerShell.' }
$nodeMajor = [int]((& node.exe --version).TrimStart('v').Split('.')[0])
if ($nodeMajor -lt 22) { throw 'Install Node.js 22 LTS or newer from nodejs.org.' }
if (-not $Python) {
    $availablePython = Get-Command python -ErrorAction SilentlyContinue
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if ($availablePython) { $Python = $availablePython.Source }
    elseif (Test-Path -LiteralPath $bundledPython) { $Python = $bundledPython }
    else { throw 'Install Python 3.12+, or use -Python with its executable path.' }
}
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
}
& '.\.venv\Scripts\python.exe' -c 'import sys; assert sys.version_info >= (3,12), "Python 3.12+ is required"'
if ($LASTEXITCODE -ne 0) { throw 'Use Python 3.12+ to create .venv.' }
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
$dependencyHash = (Get-FileHash -LiteralPath 'requirements-lock.txt' -Algorithm SHA256).Hash
$stampPath = '.venv\greencost-requirements.sha256'
if (-not (Test-Path -LiteralPath $stampPath) -or (Get-Content -LiteralPath $stampPath -Raw).Trim() -ne $dependencyHash) {
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed. Check your internet connection.' }
    Set-Content -LiteralPath $stampPath -Value $dependencyHash
}
$frontendHash = (Get-FileHash -LiteralPath 'frontend\package-lock.json' -Algorithm SHA256).Hash
$frontendStamp = 'frontend\node_modules\.greencost-lock.sha256'
if (-not (Test-Path -LiteralPath $frontendStamp) -or (Get-Content -LiteralPath $frontendStamp -Raw).Trim() -ne $frontendHash) {
    Assert-PortAvailable 3000
    Push-Location frontend
    try { npm.cmd ci; if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' } } finally { Pop-Location }
    Set-Content -LiteralPath $frontendStamp -Value $frontendHash
}
& '.\.venv\Scripts\python.exe' scripts\ingest_knowledge.py
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the research library.' }
if ($SetupOnly) { Write-Host 'Setup complete. Run this script again without -SetupOnly to start GreenCost.'; exit 0 }
if ($Production) {
    Push-Location frontend
    try { npm.cmd run build; if ($LASTEXITCODE -ne 0) { throw 'Production build failed.' } } finally { Pop-Location }
}
$backendProcess = Start-Process -FilePath (Join-Path $projectRoot '.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot 'backend.log') -RedirectStandardError (Join-Path $projectRoot 'backend-error.log')
try {
    $ready = $false
    for ($attempt=0; $attempt -lt 30; $attempt++) {
        if ($backendProcess.HasExited) { throw 'Backend did not start. Read backend-error.log for details.' }
        try { $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2; if ($health.status -eq 'ok') { $ready=$true; break } } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $ready) { throw 'Backend did not become ready. Read backend-error.log.' }
    Write-Host 'Open http://127.0.0.1:3000 in your browser. Press Ctrl+C here to stop GreenCost.'
    Set-Location -LiteralPath (Join-Path $projectRoot 'frontend')
    if ($Production) { npm.cmd run start } else { npm.cmd run dev }
    if ($LASTEXITCODE -ne 0) { throw 'Frontend stopped with an error.' }
} finally { Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue; Set-Location -LiteralPath $projectRoot }
