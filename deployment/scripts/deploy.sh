#!/bin/bash

# Deployment script for the distributed system

echo "Deploying Carrier-Grade Edge-Core-Cloud Distributed System..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Using Docker Compose for deployment..."
    docker-compose up -d
    echo "Deployment complete!"
elif command -v python &> /dev/null; then
    echo "Using Python directly for deployment..."
    python src/gui/main_gui.py
else
    echo "Error: Neither Docker nor Python is available"
    exit 1
fi
