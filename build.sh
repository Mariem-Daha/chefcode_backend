#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo "Build completed successfully!"
