#!/bin/bash
# Infinity XOS Production Startup Script
# This script starts all agents in production mode

set -e

echo "🚀 Starting Infinity XOS Production Environment"

# Set workspace root
export WORKSPACE_ROOT="/home/ai/repos"
cd "$WORKSPACE_ROOT/infinity-xos"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."
if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command_exists docker; then
    echo "⚠️  Docker not found. Containerized deployment not available."
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt
pip install psutil prometheus_client redis rq

# Install Node.js dependencies for crawlers
echo "📦 Installing Node.js dependencies..."
cd systems/infinity-crawler
npm install
cd ../..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ../mcp/results/compiled
mkdir -p ../mcp/results/indexes
mkdir -p logs
mkdir -p monitoring

# Start services based on deployment method
if [ "$1" = "docker" ] && command_exists docker; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose -f docker-compose.production.yml up -d

    echo "⏳ Waiting for services to be healthy..."
    sleep 30

    # Check service health
    if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
        echo "✅ All services started successfully!"
        echo ""
        echo "🌐 Service URLs:"
        echo "  - Orchestrator: http://localhost:8000"
        echo "  - Agent Communication: http://localhost:8001"
        echo "  - Agent Intelligence: http://localhost:8002"
        echo "  - Grafana: http://localhost:3000 (admin/admin)"
        echo "  - Prometheus: http://localhost:9090"
        echo ""
        echo "📊 View logs with: docker-compose -f docker-compose.production.yml logs -f"
        echo "🛑 Stop with: docker-compose -f docker-compose.production.yml down"
    else
        echo "❌ Some services failed to start. Check logs:"
        docker-compose -f docker-compose.production.yml logs
        exit 1
    fi

elif [ "$1" = "systemd" ]; then
    echo "🔧 Installing systemd service..."
    sudo cp production-orchestrator.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable production-orchestrator
    sudo systemctl start production-orchestrator

    echo "⏳ Waiting for service to start..."
    sleep 10

    if sudo systemctl is-active --quiet production-orchestrator; then
        echo "✅ Production orchestrator started successfully!"
        echo ""
        echo "📊 View status: sudo systemctl status production-orchestrator"
        echo "📋 View logs: sudo journalctl -u production-orchestrator -f"
        echo "🛑 Stop: sudo systemctl stop production-orchestrator"
    else
        echo "❌ Service failed to start. Check logs:"
        sudo journalctl -u production-orchestrator -n 50
        exit 1
    fi

else
    echo "💻 Starting in direct mode..."
    echo "Note: This will run in foreground. Use Ctrl+C to stop."

    # Set environment variables
    export PYTHONPATH="$WORKSPACE_ROOT/infinity-xos:$PYTHONPATH"

    # Start the production orchestrator
    python production_orchestrator.py
fi

echo ""
echo "🎯 Infinity XOS Production Environment Ready!"
echo "All agents are now running autonomously in the background."