#!/bin/bash

# Development Start Script for Ramayanam
# Starts both React dev server and Flask API server

set -e

echo "🚀 Starting Ramayanam Development Environment"
echo "============================================="

# Check if UI dependencies are installed
if [ ! -d "ui/node_modules" ]; then
    echo "📦 Installing UI dependencies..."
    cd ui && npm install && cd ..
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🎯 Starting services..."
echo "├── React Dev Server: http://localhost:5173"
echo "├── Flask API Server: http://localhost:5000"
echo "└── API Proxy: React → Flask (automatic)"

# Start Flask API server in background
echo ""
echo "🔧 Starting Flask API server..."
python run.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start React dev server in background
echo "⚛️  Starting React dev server..."
cd ui && npm run dev &
REACT_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $FLASK_PID 2>/dev/null || true
    kill $REACT_PID 2>/dev/null || true
    exit
}

# Trap SIGINT and SIGTERM to cleanup
trap cleanup SIGINT SIGTERM

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "📱 Open your browser to: http://localhost:5173"
echo "🔍 API endpoints available at: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for processes to complete
wait