#!/bin/bash

# Unified Docker Startup Script for All APIs
# This script starts all backend APIs in Docker containers

set -e

echo "=================================================="
echo "  Starting All APIs with Docker Compose"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available!${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Creating .env file...${NC}"
    cat > .env << EOF
# Email Configuration (Optional - for Task Management API)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Add other environment variables as needed
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo ""
fi

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker compose down
echo ""

# Build images
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker compose build
echo ""

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker compose up -d
echo ""

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check service status
echo ""
echo "=================================================="
echo "  Service Status"
echo "=================================================="
docker compose ps
echo ""

# Display access information
echo ""
echo "=================================================="
echo "  🎉 All Services are now running!"
echo "=================================================="
echo ""
echo -e "${GREEN}🌐 Frontend:${NC}"
echo "  • React App:            http://localhost:3000"
echo ""
echo -e "${GREEN}📡 Backend APIs:${NC}"
echo "  • Blog API:             http://localhost:5000"
echo "  • Customer Support API: http://localhost:5001"
echo "  • Support Ticket API:   http://localhost:5002"
echo "  • Task Management API:  http://localhost:5003"
echo "  • E-Commerce API:       http://localhost:5004"
echo ""
echo -e "${GREEN}🗄️  Shared Services:${NC}"
echo "  • Redis:                localhost:6379"
echo ""
echo -e "${GREEN}📊 Health Checks:${NC}"
echo "  • Blog API:             http://localhost:5000/health"
echo "  • Customer Support API: http://localhost:5001/api/health"
echo "  • Support Ticket API:   http://localhost:5002/api/health"
echo "  • Task Management API:  http://localhost:5003/api/auth/health"
echo "  • E-Commerce API:       http://localhost:5004/api/products"
echo ""
echo -e "${GREEN}📚 Swagger Documentation:${NC}"
echo "  • Task Management API:  http://localhost:5003/apidocs"
echo ""
echo -e "${YELLOW}💡 Useful Commands:${NC}"
echo "  • View logs:            docker compose logs -f"
echo "  • View specific logs:   docker compose logs -f [service-name]"
echo "  • Stop all services:    docker compose down"
echo "  • Restart services:     docker compose restart"
echo "  • Check status:         docker compose ps"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
