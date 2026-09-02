# ClipMind AI — Local Development Startup Script
# Run this from the project root: .\start.ps1

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  ClipMind AI — Starting Local Stack' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

# Check prerequisites
$missing = @()
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { $missing += 'Python 3.11+' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $missing += 'Node.js 20+' }
if ($missing.Count -gt 0) {
    Write-Host 'Missing prerequisites:' -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host '[1/3] Starting API server...' -ForegroundColor Yellow
$apiDir = Join-Path $PSScriptRoot 'services\api'

# Create venv if missing
if (-not (Test-Path (Join-Path $apiDir '.venv'))) {
    Write-Host '  Creating Python virtual environment...' -ForegroundColor Gray
    Push-Location $apiDir
    python -m venv .venv
    Pop-Location
}

# Install deps
Push-Location $apiDir
& '.venv\Scripts\activate.ps1'
pip install -r requirements.txt -q 2>$null

# Start API in background
$apiProc = Start-Process -FilePath 'python' -ArgumentList '-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8001' -WorkingDirectory $apiDir -PassThru -NoNewWindow -RedirectStandardOutput "$apiDir\api.log" -RedirectStandardError "$apiDir\api_err.log"
Write-Host "  API started (PID: $($apiProc.Id)) on http://localhost:8001" -ForegroundColor Green
Pop-Location

Write-Host '[2/3] Starting Web server...' -ForegroundColor Yellow
$webDir = Join-Path $PSScriptRoot 'apps\web'

# Install deps if missing
if (-not (Test-Path (Join-Path $webDir 'node_modules'))) {
    Write-Host '  Installing npm packages...' -ForegroundColor Gray
    Push-Location $webDir
    npm install
    Pop-Location
}

# Start Web in background
$webProc = Start-Process -FilePath 'node' -ArgumentList '.\node_modules\next\dist\bin\next', 'dev', '--turbo' -WorkingDirectory $webDir -PassThru -NoNewWindow -RedirectStandardOutput "$webDir\web.log" -RedirectStandardError "$webDir\web_err.log"
Write-Host "  Web started (PID: $($webProc.Id)) on http://localhost:3000" -ForegroundColor Green

Write-Host '[3/3] Waiting for servers...' -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  ClipMind AI is running!' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '  Landing page:  http://localhost:3000' -ForegroundColor White
Write-Host '  Register:       http://localhost:3000/register' -ForegroundColor White
Write-Host '  Login:          http://localhost:3000/login' -ForegroundColor White
Write-Host '  Dashboard:      http://localhost:3000/dashboard' -ForegroundColor White
Write-Host '  API Health:     http://localhost:8000/health' -ForegroundColor White
Write-Host ''
Write-Host 'Press Ctrl+C in this window or run .\stop.ps1 to stop all servers.' -ForegroundColor Gray
Write-Host ''

# Keep script alive
try { Wait-Process -Id $apiProc.Id, $webProc.Id } catch {}
