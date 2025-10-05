#!/bin/bash
# FastMCP Marker - Dual Service Startup Script
# Start zowel MCP server als Gradio web interface tegelijkertijd

set -e

echo "🚀 Starting FastMCP Marker Services..."
echo "=================================="

# Environment setup
export PYTHONPATH=/app
export TORCH_DEVICE=${TORCH_DEVICE:-cuda}

# Verify uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv package manager not found!"
    exit 1
fi

echo "✅ uv package manager detected: $(uv --version)"

# Check CUDA availability
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounits
else
    echo "⚠️  No NVIDIA GPU detected, using CPU mode"
    export TORCH_DEVICE=cpu
fi

# Create necessary directories
mkdir -p /app/data /app/output /app/logs

# Function to handle cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $MCP_PID $GRADIO_PID 2>/dev/null || true
    wait
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start MCP Server in background
echo "🤖 Starting MCP Server on port 8000..."
uv run --frozen mcp_server.py &
MCP_PID=$!

# Wait a moment for MCP server to initialize
sleep 3

# Start Gradio Web Interface in background
echo "🌐 Starting Gradio Web Interface on port 7860..."
uv run --frozen gradio_app_advanced_full.py &
GRADIO_PID=$!

# Wait a moment for Gradio to initialize
sleep 5

# Check if services are running
if kill -0 $MCP_PID 2>/dev/null; then
    echo "✅ MCP Server started successfully (PID: $MCP_PID)"
else
    echo "❌ MCP Server failed to start"
    exit 1
fi

if kill -0 $GRADIO_PID 2>/dev/null; then
    echo "✅ Gradio Web Interface started successfully (PID: $GRADIO_PID)"
else
    echo "❌ Gradio Web Interface failed to start"
    exit 1
fi

echo ""
echo "🎉 Both services are running!"
echo "📡 MCP Server: http://localhost:8000"
echo "🌐 Gradio Web: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait $MCP_PID $GRADIO_PID
