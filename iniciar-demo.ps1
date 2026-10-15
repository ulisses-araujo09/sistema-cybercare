param([switch]$PrepararSomente)
$ErrorActionPreference = 'Stop'
$raizCyberCare = $PSScriptRoot
$pythonCyberCare = Join-Path $raizCyberCare '.venv/Scripts/python.exe'
$pythonBundled = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$depsCyberCare = Join-Path $raizCyberCare '.deps'
if (Test-Path (Join-Path $depsCyberCare 'fastapi')) {
    $env:PYTHONPATH = $depsCyberCare
    if (Test-Path $pythonBundled) { $pythonCyberCare = $pythonBundled }
} elseif (-not (Test-Path $pythonCyberCare)) {
    python -m venv (Join-Path $raizCyberCare '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Instale Python 3.12 e tente novamente.' }
}
Push-Location (Join-Path $raizCyberCare 'backend')
try {
    & $pythonCyberCare -c 'import fastapi, sqlalchemy, alembic, argon2'
    if ($LASTEXITCODE -ne 0) {
        & $pythonCyberCare -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Falha na instalação das dependências Python.' }
    }
    & $pythonCyberCare -m app.bootstrap_demo
    if ($LASTEXITCODE -ne 0) { throw 'Confira a configuração de backend/.env.' }
    & $pythonCyberCare -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao aplicar migrações.' }
    & $pythonCyberCare -m app.seed
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao carregar dados fictícios.' }
} finally { Pop-Location }
Push-Location (Join-Path $raizCyberCare 'frontend')
try {
    if (-not (Test-Path 'node_modules')) {
        npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw 'Falha na instalação do frontend. Instale Node.js 22.' }
    }
} finally { Pop-Location }
if ($PrepararSomente) { Write-Host 'Preparação concluída.'; exit }
$logsCyberCare = Join-Path $raizCyberCare 'tmp/demo'
New-Item -ItemType Directory -Force $logsCyberCare | Out-Null
$apiAtiva = $false
$uiAtiva = $false
try { $apiAtiva = (Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2).status -eq 'ok' } catch {}
try { $uiAtiva = (Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -TimeoutSec 2).StatusCode -eq 200 } catch {}
$processosCyberCare = @()
if (-not $apiAtiva) {
    $processosCyberCare += Start-Process -FilePath $pythonCyberCare -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--no-access-log', '--no-proxy-headers') -WorkingDirectory (Join-Path $raizCyberCare 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logsCyberCare 'api.log') -RedirectStandardError (Join-Path $logsCyberCare 'api-erro.log') -PassThru
}
if (-not $uiAtiva) {
    $processosCyberCare += Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', 'npm.cmd run dev -- --strictPort') -WorkingDirectory (Join-Path $raizCyberCare 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logsCyberCare 'frontend.log') -RedirectStandardError (Join-Path $logsCyberCare 'frontend-erro.log') -PassThru
}
$processosCyberCare.Id | Set-Content (Join-Path $logsCyberCare 'processos.txt')
$prontoCyberCare = $false
for ($tentativaCyberCare = 0; $tentativaCyberCare -lt 15; $tentativaCyberCare++) {
    try {
        $apiCyberCare = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2
        $uiCyberCare = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -TimeoutSec 2
        if ($apiCyberCare.status -eq 'ok' -and $uiCyberCare.StatusCode -eq 200) { $prontoCyberCare = $true; break }
    } catch {}
    Start-Sleep -Seconds 1
}
if (-not $prontoCyberCare) { throw 'Serviços não iniciaram. Consulte os logs em tmp/demo.' }
Write-Host 'CyberCare disponível em http://127.0.0.1:5173'
Write-Host 'Contas fictícias: demo-acessos.txt. Use Ctrl+C nos terminais se iniciar manualmente.'
