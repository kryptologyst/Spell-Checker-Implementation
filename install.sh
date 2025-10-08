#!/bin/bash

# Advanced Spell Checker - Installation Script
# This script installs the required dependencies and sets up the project

echo "🔍 Advanced Spell Checker - Installation Script"
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install basic dependencies
echo "📚 Installing basic dependencies..."
pip install flask flask-cors

# Try to install optional dependencies
echo "🔧 Installing optional dependencies..."

# Install Levenshtein (may fail on some systems)
pip install python-Levenshtein || echo "⚠️ python-Levenshtein installation failed, using fallback implementation"

# Install other optional packages
pip install phonetics || echo "⚠️ phonetics installation failed, using fallback implementation"
pip install textdistance || echo "⚠️ textdistance installation failed, using fallback implementation"
pip install pandas numpy || echo "⚠️ pandas/numpy installation failed, using basic implementations"

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install pytest pytest-cov black flake8 isort mypy
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To run the spell checker:"
echo "  source venv/bin/activate"
echo "  python3 0171.py"
echo ""
echo "To run the web interface:"
echo "  source venv/bin/activate"
echo "  python3 app.py"
echo "  Then visit: http://localhost:5000"
echo ""
echo "To run tests:"
echo "  source venv/bin/activate"
echo "  python3 tests/test_spell_checker.py"
echo ""
