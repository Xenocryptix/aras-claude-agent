#!/bin/bash

# Aras MCP Docker Deployment Script
# This script helps deploy the Aras MCP server using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Create configuration file
create_config() {
    print_status "Setting up configuration..."
    
    if [ ! -f "docker-config/.env" ]; then
        cp docker-config/env.example docker-config/.env
        print_warning "Created docker-config/.env from template"
        print_warning "Please edit docker-config/.env with your Aras server settings"
        echo ""
        echo "Required settings:"
        echo "  - API_URL: Your Aras Innovator server URL"
        echo "  - API_USERNAME: Aras username"
        echo "  - API_PASSWORD: Aras password"
        echo "  - ARAS_DATABASE: Aras database name"
        echo ""
        read -p "Press Enter to continue after editing the configuration..."
    else
        print_success "Configuration file already exists"
    fi
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t aras-mcp-server:latest .
    print_success "Docker image built successfully"
}

# Deploy services
deploy() {
    print_status "Deploying services..."
    
    # Create logs directory
    mkdir -p logs
    
    # Start services
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "Services deployed successfully"
}

# Deploy with nginx (optional)
deploy_with_nginx() {
    print_status "Deploying services with nginx reverse proxy..."
    
    # Create logs directory
    mkdir -p logs
    
    # Start services with nginx profile
    if command -v docker-compose &> /dev/null; then
        docker-compose --profile nginx up -d
    else
        docker compose --profile nginx up -d
    fi
    
    print_success "Services with nginx deployed successfully"
}

# Check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for service to start
    sleep 10
    
    # Check health endpoint
    if curl -f http://localhost:8123/health &> /dev/null; then
        print_success "Service is healthy"
        
        # Get status
        print_status "Service status:"
        curl -s http://localhost:8123/status | python3 -m json.tool
    else
        print_error "Service health check failed"
        print_status "Checking logs..."
        docker logs aras-mcp-server
        return 1
    fi
}

# Show logs
show_logs() {
    print_status "Showing service logs..."
    docker logs -f aras-mcp-server
}

# Stop services
stop() {
    print_status "Stopping services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    print_success "Services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up..."
    if command -v docker-compose &> /dev/null; then
        docker-compose down -v --rmi local
    else
        docker compose down -v --rmi local
    fi
    print_success "Cleanup completed"
}

# Show usage
show_usage() {
    echo "Aras MCP Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy          Deploy the MCP server"
    echo "  deploy-nginx    Deploy with nginx reverse proxy"
    echo "  build           Build Docker image only"
    echo "  health          Check service health"
    echo "  logs            Show service logs"
    echo "  stop            Stop services"
    echo "  cleanup         Stop services and clean up"
    echo "  help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 deploy           # Deploy basic server"
    echo "  $0 deploy-nginx     # Deploy with nginx reverse proxy"
    echo "  $0 health           # Check if service is healthy"
    echo "  $0 logs             # Follow service logs"
}

# Main script
main() {
    case "${1:-help}" in
        "deploy")
            check_docker
            create_config
            build_image
            deploy
            check_health
            ;;
        "deploy-nginx")
            check_docker
            create_config
            build_image
            deploy_with_nginx
            check_health
            ;;
        "build")
            check_docker
            build_image
            ;;
        "health")
            check_health
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function
main "$@"
