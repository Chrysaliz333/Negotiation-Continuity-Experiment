#!/bin/bash
# Simple wrapper script that uses python3 and activates venv

# Activate virtual environment
source venv/bin/activate

# Run the command with python3
python3 "$@"
