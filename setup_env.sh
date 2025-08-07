#!/usr/bin/env bash
set -e

VENV_NAME="venv"

# Check Python 3 availability
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 is required but not installed." >&2
  exit 1
fi

PYTHON=${PYTHON:-python3}

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
  echo "✅ Creating virtual environment using $PYTHON..."
  $PYTHON -m venv "$VENV_NAME"
fi

# Activate virtual environment
source "$VENV_NAME/bin/activate"

# Upgrade pip
$PYTHON -m pip install --upgrade pip

# Install dependencies
echo "✅ Installing dependencies..."
pip install flask pandas

# Launch Flask application
echo "🚀 Launching Flask application..."
$PYTHON visualisation.py
