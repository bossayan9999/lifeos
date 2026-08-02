# LifeOS Auto-Update Script (Windows PowerShell)
# Double-click "Update LifeOS.bat" or run:
#   powershell -ExecutionPolicy Bypass -File .\scripts\update.ps1

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Write-Step($n, $msg) {
    Write-Host "[$n] $msg" -ForegroundColor Yellow
}
function Write-Ok($msg) {
    Write-Host "     $msg" -ForegroundColor Green
}
function Write-Warn($msg) {
    Write-Host "     WARNING: $msg" -ForegroundColor Yellow
}
function Write-Err($msg) {
    Write-Host "     ERROR: $msg" -ForegroundColor Red
}
function Show-Fix($steps) {
    Write-Host ""
    Write-Host "----- How to fix -----" -ForegroundColor Magenta
    foreach ($s in $steps) {
        Write-Host "  * $s" -ForegroundColor White
    }
    Write-Host "----------------------" -ForegroundColor Magenta
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LifeOS Auto-Update" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------- 1. Docker running? ----------
Write-Step "1/6" "Checking Docker Desktop..."
$dockerOk = $false
try {
    $null = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { $dockerOk = $true }
} catch {}
if (-not $dockerOk) {
    Write-Err "Docker Desktop is not running (or not installed)."
    Show-Fix @(
        "Open Docker Desktop and wait until it says 'Engine running'",
        "Then run this script again",
        "If Docker is not installed: https://www.docker.com/products/docker-desktop/"
    )
    pause
    exit 1
}
Write-Ok "Docker is running."

# ---------- 2. Git available? ----------
Write-Step "2/6" "Checking Git..."
$gitOk = $false
try {
    $null = git --version 2>$null
    if ($LASTEXITCODE -eq 0) { $gitOk = $true }
} catch {}
if (-not $gitOk) {
    Write-Warn "Git not found. Skipping code update (will use local files)."
} else {
    Write-Ok "Git found."
}

# ---------- 3. Pull latest code ----------
Write-Step "3/6" "Pulling latest code from GitHub..."
if ($gitOk) {
    git pull origin main 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "Code updated."
    } else {
        Write-Warn "git pull failed (maybe offline or conflicts). Continuing with local code."
        Show-Fix @(
            "Check your internet connection",
            "Or run manually:  git pull origin main",
            "If there are conflicts, resolve them then re-run this script"
        )
    }
} else {
    Write-Warn "Skipped (Git not available)."
}

# ---------- 4. Stop old containers ----------
Write-Step "4/6" "Stopping current containers..."
docker compose down 2>$null
Write-Ok "Stopped."

# ---------- 5. Rebuild & start ----------
Write-Step "5/6" "Rebuilding and starting LifeOS (may take several minutes)..."
docker compose up --build -d 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Err "docker compose failed."
    Show-Fix @(
        "Make sure Docker Desktop is fully started",
        "Run:  docker compose up --build   (to see full error)",
        "If port 5173 or 8000 is in use, close the other app using it",
        "Or reset:  docker compose down -v   then run this script again"
    )
    pause
    exit 1
}
Write-Ok "Containers started."

# ---------- 6. Health check ----------
Write-Step "6/6" "Waiting for backend to become healthy..."
$max = 90
$ok = $false
for ($i = 1; $i -le $max; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) {
            $ok = $true
            break
        }
    } catch {}
    if ($i % 5 -eq 0) {
        Write-Host "     still waiting... ($i/$max)" -ForegroundColor DarkGray
    }
    Start-Sleep -Seconds 2
}

if ($ok) {
    Write-Ok "Backend is healthy!"
} else {
    Write-Warn "Backend not responding yet (models may still be loading)."
    Show-Fix @(
        "Wait 1-2 more minutes then open http://localhost:8000/health",
        "Check logs:  docker compose logs backend",
        "If it keeps failing:  docker compose down -v  then re-run this script"
    )
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
Write-Host "  Stop later: docker compose down" -ForegroundColor DarkGray
Write-Host ""

try {
    Start-Process "http://localhost:5173"
    Write-Ok "Browser opened."
} catch {
    Write-Warn "Could not open browser automatically. Open http://localhost:5173 yourself."
}

Write-Host ""
pause
