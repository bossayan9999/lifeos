# LifeOS Start Script (Windows PowerShell)
# Double-click "Start LifeOS.bat" or run:
#   powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Write-Ok($msg)  { Write-Host "  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  WARNING: $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  ERROR: $msg" -ForegroundColor Red }
function Show-Fix($steps) {
    Write-Host ""
    Write-Host "----- How to fix -----" -ForegroundColor Magenta
    foreach ($s in $steps) { Write-Host "  * $s" -ForegroundColor White }
    Write-Host "----------------------" -ForegroundColor Magenta
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting LifeOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Docker check
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
$dockerOk = $false
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerOk = $true }
} catch {}
if (-not $dockerOk) {
    Write-Err "Docker Desktop is not running (or not installed)."
    Show-Fix @(
        "Open Docker Desktop and wait until it says Engine running",
        "Then double-click Start LifeOS.bat again",
        "Install: https://www.docker.com/products/docker-desktop/"
    )
    pause
    exit 1
}
Write-Ok "Docker is running."

# Start
Write-Host "Starting containers..." -ForegroundColor Yellow
docker compose up -d --build 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to start containers."
    Show-Fix @(
        "Run in PowerShell:  docker compose up --build",
        "Look at the red error text and share it if you need help",
        "Port busy? Close apps using port 5173 or 8000",
        "Reset:  docker compose down -v   then try again"
    )
    pause
    exit 1
}
Write-Ok "Containers started."

# Health wait
Write-Host "Waiting for backend..." -ForegroundColor Yellow
$max = 60
$ok = $false
for ($i = 1; $i -le $max; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch {}
    if ($i % 5 -eq 0) { Write-Host "  still waiting... ($i/$max)" -ForegroundColor DarkGray }
    Start-Sleep -Seconds 2
}

if ($ok) {
    Write-Ok "Backend is healthy!"
} else {
    Write-Warn "Backend not ready yet (first start can take longer while models load)."
    Show-Fix @(
        "Wait 1-2 minutes then open http://localhost:8000/health",
        "Check logs:  docker compose logs backend"
    )
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LifeOS is running" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Chat UI  : http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Stop later: docker compose down" -ForegroundColor DarkGray
Write-Host ""

try {
    Start-Process "http://localhost:5173"
    Write-Ok "Browser opened."
} catch {
    Write-Warn "Open http://localhost:5173 in your browser."
}

Write-Host ""
pause
