#!/usr/bin/env bash
# CoreClicks 2.0 — Quickstart Launch Script

set -e

echo "======================================================="
echo "⚡ Starting CoreClicks Setup"
echo "======================================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ and retry."
    exit 1
fi

# Create virtual environment if not already present
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install / update dependencies
echo "📥 Checking and installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "======================================================="
echo "🚀 CoreClicks is launching..."
echo "======================================================="

# Launch application runner
python3 run.py
