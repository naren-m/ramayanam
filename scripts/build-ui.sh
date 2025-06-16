#!/bin/bash

# Build UI Script for Ramayanam
# Builds the React UI for production

set -e

echo "⚛️  Building React UI for Production"
echo "==================================="

# Check if UI directory exists
if [ ! -d "ui" ]; then
    echo "❌ Error: ui/ directory not found"
    echo "Make sure you're running this from the project root"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "ui/node_modules" ]; then
    echo "📦 Installing UI dependencies..."
    cd ui && npm install && cd ..
fi

# Build the React app
echo "🔨 Building React application..."
cd ui && npm run build && cd ..

# Check if build was successful
if [ -d "dist" ]; then
    echo "✅ UI build completed successfully!"
    echo "📁 Built files are in: ./dist/"
    echo ""
    echo "📊 Build summary:"
    du -sh dist
    echo ""
    echo "🚀 Ready for:"
    echo "  • Docker build: ./scripts/build-docker.sh"
    echo "  • Production test: python run.py (serves from ./dist/)"
else
    echo "❌ Build failed - dist/ directory not created"
    exit 1
fi