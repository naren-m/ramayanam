#!/bin/bash

# Development Setup Script for Ramayanam
# One-time setup for development environment

set -e

echo "🛠️  Ramayanam Development Setup"
echo "=============================="

# Check requirements
echo "🔍 Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

echo "✅ System requirements met"

# Setup Python environment
echo ""
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Setup Node.js environment
echo ""
echo "📦 Setting up Node.js environment..."
cd ui
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "✅ Node.js dependencies already installed"
fi
cd ..

# Create .gitignore entries
echo ""
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Development
venv/
.env
.vscode/
.idea/

# UI Build
dist/
ui/node_modules/
ui/dist/

# Logs
*.log
logs/

EOF

echo "✅ .gitignore updated"

echo ""
echo "🎉 Development setup completed!"
echo ""
echo "🚀 Next steps:"
echo "  1. Start development: ./scripts/dev-start.sh"
echo "  2. Build for production: ./scripts/build-ui.sh"
echo "  3. Build Docker image: ./scripts/build-docker.sh"
echo ""
echo "📚 Documentation: README.md"