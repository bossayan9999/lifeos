# LifeOS Start Script (Windows PowerShell)
# Double-click or: powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting LifeOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Open Docker Desktop first." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Starting containers..." -ForegroundColor Yellow
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start. Run 'docker compose up --build' to see full logs." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Waiting for backend..." -ForegroundColor Yellow
$max = 45
for ($i = 1; $i -le $max; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { break }
    } catch {}
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "LifeOS is running!" -ForegroundColor Green
Write-Host "  Chat UI  : http://localhost:5173"
Write-Host "  API Docs : http://localhost:8000/docs"
Write-Host ""

Start-Process "http://localhost:5173"
Write-Host "Browser opened." -ForegroundColor Green
Write-Host ""
Write-Host "Tip: To stop LifeOS later, run:  docker compose down" -ForegroundColor DarkGray
Write-Host ""
pause
