# LifeOS Auto-Update Script (Windows PowerShell)
# Usage: Right-click → Run with PowerShell
# Or:   powershell -ExecutionPolicy Bypass -File .\scripts\update.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LifeOS Auto-Update" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Docker is running
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker Desktop is not running. Open Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "      Docker is running." -ForegroundColor Green

# 2. Pull latest code
Write-Host "[2/5] Pulling latest code from GitHub..." -ForegroundColor Yellow
git pull origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: git pull failed. Continuing with local code." -ForegroundColor Yellow
} else {
    Write-Host "      Code updated." -ForegroundColor Green
}

# 3. Stop existing containers
Write-Host "[3/5] Stopping current containers..." -ForegroundColor Yellow
docker compose down 2>$null
Write-Host "      Stopped." -ForegroundColor Green

# 4. Rebuild and start
Write-Host "[4/5] Rebuilding and starting LifeOS (this may take a few minutes)..." -ForegroundColor Yellow
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: docker compose failed. Check the output above." -ForegroundColor Red
    exit 1
}
Write-Host "      Containers started." -ForegroundColor Green

# 5. Wait for health
Write-Host "[5/5] Waiting for backend to become healthy..." -ForegroundColor Yellow
$max = 60
$ok = $false
for ($i = 1; $i -le $max; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) {
            $ok = $true
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
}
if ($ok) {
    Write-Host "      Backend is healthy!" -ForegroundColor Green
} else {
    Write-Host "      Backend not responding yet. It may still be loading models." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LifeOS is ready" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Chat UI   : http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs  : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health    : http://localhost:8000/health" -ForegroundColor White
Write-Host ""

# Open browser
Start-Process "http://localhost:5173"
Write-Host "Browser opened. Enjoy LifeOS!" -ForegroundColor Green
Write-Host ""
