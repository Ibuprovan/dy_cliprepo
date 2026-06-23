
# Douyin Favorites AI Knowledge Base - PowerShell Launch Script
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Douyin Favorites AI Knowledge Base" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
Write-Host "Current directory: $scriptPath"
Write-Host ""

if (-not (Test-Path "data\logs")) {
    New-Item -ItemType Directory -Path "data\logs" -Force | Out-Null
}

Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Python version: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not installed"
    }
} catch {
    Write-Host "[FAIL] Python not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "[2/6] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Node.js version: $nodeVersion" -ForegroundColor Green
    } else {
        throw "Node.js not installed"
    }
} catch {
    Write-Host "[FAIL] Node.js not installed" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "[3/6] Checking backend environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    Set-Location backend
    python -m venv venv 2>&1 | Out-File -FilePath "..\data\logs\start.log" -Append
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to create virtual environment" -ForegroundColor Red
        Write-Host "Check log: data\logs\start.log" -ForegroundColor Red
        Set-Location ..
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
}
Write-Host "[OK] Virtual environment exists" -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt -q 2>&1 | Out-File -FilePath "..\data\logs\start.log" -Append
Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
Set-Location ..
Write-Host ""

Write-Host "[5/6] Checking frontend environment..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Set-Location frontend
    npm install 2>&1 | Out-File -FilePath "..\data\logs\start.log" -Append
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to install frontend dependencies" -ForegroundColor Red
        Write-Host "Check log: data\logs\start.log" -ForegroundColor Red
        Set-Location ..
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
}
Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Checking authentication..." -ForegroundColor Yellow
if (Test-Path "backend\data\douyin_auth.json") {
    Write-Host "[OK] Authentication file exists" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Authentication file not found" -ForegroundColor Yellow
    Write-Host "Starting login process..." -ForegroundColor Cyan
    Set-Location backend
    & .\venv\Scripts\Activate.ps1
    python login_manual.py
    Set-Location ..
    if (-not (Test-Path "backend\data\douyin_auth.json")) {
        Write-Host "[FAIL] Login failed or cancelled" -ForegroundColor Red
        Write-Host "Please try again or run 'cd backend; python login_manual.py' manually" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Login successful" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting backend service (port 8000)..." -ForegroundColor Cyan
$backendPath = Join-Path $scriptPath "backend"
$backendCommand = "cd /d `"$backendPath`" && venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $backendCommand -WindowStyle Normal

Write-Host "Waiting for backend..." -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Host "Starting frontend service (port 5173)..." -ForegroundColor Cyan
$frontendPath = Join-Path $scriptPath "frontend"
$frontendCommand = "cd /d `"$frontendPath`" && npm run dev"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $frontendCommand -WindowStyle Normal

Write-Host "Waiting for frontend..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend: http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Open http://localhost:5173 to use the application" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Do NOT close this window!" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Start-Process "http://localhost:5173"

Read-Host "Press Enter to exit"
