#!/usr/bin/env bash
# Simple setup script to install dependencies without using a virtual environment
set -e

echo "Installing Python packages..."
pip install -r requirements.txt

if [ -d "model/deepface" ]; then
    echo "Installing DeepFace in editable mode..."
    pip install -e model/deepface
fi

echo "Creating data directories..."
mkdir -p src/data/uploads src/data/results src/data/images

echo "Setup completed."

