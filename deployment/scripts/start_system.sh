#!/bin/bash

# Start script for the distributed system

echo "Starting Carrier-Grade Edge-Core-Cloud Distributed System..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import tkinter" &> /dev/null; then
    echo "Error: tkinter is not available"
    exit 1
fi

# Start the GUI application
echo "Starting GUI application..."
python src/gui/main_gui.py

echo "System started successfully!"
