# Infinity XOS Production Startup Script for Windows
# This script starts all agents in production mode

param(
    [string]$Mode = "direct",
    [switch]$InstallService,
    [switch]$UninstallService,
    [switch]$StartService,
    [switch]$StopService
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Infinity XOS Production Environment" -ForegroundColor Green

# Set workspace root
$WorkspaceRoot = $env:WORKSPACE_ROOT
if (-not $WorkspaceRoot) {
    $WorkspaceRoot = "c:\AI\repos"
}
$InfinityXOSPath = Join-Path $WorkspaceRoot "infinity-xos"

Set-Location $InfinityXOSPath

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Service management
if ($InstallService) {
    Write-Host "🔧 Installing Windows service..." -ForegroundColor Yellow
    try {
        python production_orchestrator_service.py install
        Write-Host "✅ Service installed successfully!" -ForegroundColor Green
        Write-Host "Start with: python production_orchestrator_service.py start" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Failed to install service: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

if ($UninstallService) {
    Write-Host "🔧 Uninstalling Windows service..." -ForegroundColor Yellow
    try {
        python production_orchestrator_service.py remove
        Write-Host "✅ Service uninstalled successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to uninstall service: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

if ($StartService) {
    Write-Host "▶️  Starting Windows service..." -ForegroundColor Yellow
    try {
        python production_orchestrator_service.py start
        Write-Host "✅ Service started successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start service: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

if ($StopService) {
    Write-Host "⏹️  Stopping Windows service..." -ForegroundColor Yellow
    try {
        python production_orchestrator_service.py stop
        Write-Host "✅ Service stopped successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to stop service: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

# Check dependencies
Write-Host "📋 Checking dependencies..." -ForegroundColor Yellow
if (-not (Test-Command python)) {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command node)) {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

$DockerAvailable = Test-Command docker

# Install Python dependencies
Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install psutil prometheus_client redis rq

# Install Node.js dependencies for crawlers
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location (Join-Path $InfinityXOSPath "systems\infinity-crawler")
npm install
Set-Location $InfinityXOSPath

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$Directories = @(
    (Join-Path $WorkspaceRoot "mcp\results\compiled"),
    (Join-Path $WorkspaceRoot "mcp\results\indexes"),
    "logs",
    "monitoring"
)

foreach ($Dir in $Directories) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
    }
}

# Start services based on deployment method
if ($Mode -eq "docker" -and $DockerAvailable) {
    Write-Host "🐳 Starting with Docker Compose..." -ForegroundColor Yellow
    docker-compose -f docker-compose.production.yml up -d

    Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
    Start-Sleep 30

    # Check service health
    $ComposeStatus = docker-compose -f docker-compose.production.yml ps
    if ($ComposeStatus -match "Up") {
        Write-Host "✅ All services started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Service URLs:" -ForegroundColor Cyan
        Write-Host "  - Orchestrator: http://localhost:8000" -ForegroundColor White
        Write-Host "  - Agent Communication: http://localhost:8001" -ForegroundColor White
        Write-Host "  - Agent Intelligence: http://localhost:8002" -ForegroundColor White
        Write-Host "  - Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
        Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor White
        Write-Host ""
        Write-Host "📊 View logs with: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Cyan
        Write-Host "🛑 Stop with: docker-compose -f docker-compose.production.yml down" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Some services failed to start. Check logs:" -ForegroundColor Red
        docker-compose -f docker-compose.production.yml logs
        exit 1
    }

} elseif ($Mode -eq "service") {
    Write-Host "🔧 Using Windows service mode..." -ForegroundColor Yellow
    Write-Host "Installing and starting service..." -ForegroundColor Yellow

    # Install and start service
    python production_orchestrator_service.py install
    python production_orchestrator_service.py start

    Write-Host "⏳ Waiting for service to start..." -ForegroundColor Yellow
    Start-Sleep 10

    # Check if service is running
    $Service = Get-Service -Name "InfinityXOSProductionOrchestrator" -ErrorAction SilentlyContinue
    if ($Service -and $Service.Status -eq "Running") {
        Write-Host "✅ Production orchestrator service started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 View status: Get-Service InfinityXOSProductionOrchestrator" -ForegroundColor Cyan
        Write-Host "📋 View logs: Check Windows Event Viewer for 'InfinityXOSProductionOrchestrator'" -ForegroundColor Cyan
        Write-Host "🛑 Stop: python production_orchestrator_service.py stop" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Service failed to start. Check Windows Event Viewer for details." -ForegroundColor Red
        exit 1
    }

} else {
    Write-Host "💻 Starting in direct mode..." -ForegroundColor Yellow
    Write-Host "Note: This will run in foreground. Press Ctrl+C to stop." -ForegroundColor Yellow
    Write-Host ""

    # Set environment variables
    $env:PYTHONPATH = "$InfinityXOSPath;$env:PYTHONPATH"
    $env:WORKSPACE_ROOT = $WorkspaceRoot

    # Start the production orchestrator
    python production_orchestrator.py
}

Write-Host ""
Write-Host "🎯 Infinity XOS Production Environment Ready!" -ForegroundColor Green
Write-Host "All agents are now running autonomously in the background." -ForegroundColor Green