#!/bin/bash

# PDF2PPT Docker Startup Script
# Automatically checks dependencies and starts the service

set -e

echo "🚀 PDF2PPT Docker Startup Script"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found, using 'docker compose' instead${NC}"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Check for port conflicts
PORT=${PORT:-8000}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use${NC}"
    echo "Please set a different PORT in .env file or stop the service using that port"
    read -p "Do you want to use a different port? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter new port number: " NEW_PORT
        export PORT=$NEW_PORT
        echo "PORT=$NEW_PORT" > .env
    else
        exit 1
    fi
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs
echo -e "${GREEN}✅ Directories created${NC}"

# Build and start the service
echo "🔨 Building Docker image..."
$DOCKER_COMPOSE build

echo "🚀 Starting PDF2PPT service..."
$DOCKER_COMPOSE up -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if docker ps | grep -q pdf2ppt; then
    echo -e "${GREEN}✅ PDF2PPT is running!${NC}"
    echo ""
    echo "📊 Service Information:"
    echo "  - Web UI: http://localhost:$PORT"
    echo "  - API Docs: http://localhost:$PORT/docs"
    echo "  - Health Check: http://localhost:$PORT/health"
    echo ""
    echo "📝 Useful Commands:"
    echo "  - View logs: $DOCKER_COMPOSE logs -f"
    echo "  - Stop service: $DOCKER_COMPOSE down"
    echo "  - Restart service: $DOCKER_COMPOSE restart"
    echo ""
    echo "🎉 Ready to convert PDF to PPT!"
else
    echo -e "${RED}❌ Failed to start PDF2PPT${NC}"
    echo "Check logs with: $DOCKER_COMPOSE logs"
    exit 1
fi
