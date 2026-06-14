#!/bin/bash
# Backend setup script for normalization service
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🔧 Setting up Normalization Service..."
echo "📁 Working directory: $SCRIPT_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "✨ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "✅ Normalization service setup complete!"
echo "📝 To activate the environment, run: source venv/bin/activate"
