#!/bin/bash

# Simple API Test Runner for Knowledge Graph

API_URL="${API_URL:-http://localhost:8080}"

echo "🧪 Running Knowledge Graph API Tests..."
echo "API URL: $API_URL"
echo "========================================"

# Install Python dependencies if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install requests
fi

# Run the API tests
python3 tests/test_kg_api.py --url "$API_URL"