#!/bin/bash

# Aras MCP Server Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DEFAULT_ENV_FILE=".env"
DEFAULT_COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env file exists
check_env() {
    if [ ! -f "$DEFAULT_ENV_FILE" ]; then
        print_warning ".env file not found. Copying from .env.example"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Please edit .env file with your Aras Innovator server details"
            return 1
        else
            print_error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
    return 0
}

# Function to start the services
start_services() {
    print_info "Starting Aras MCP Server..."
    check_docker
    
    if check_env; then
        docker-compose up -d aras-mcp-server
        print_info "Server started successfully!"
        print_info "SSE endpoint available at: http://localhost:8080/sse"
    else
        print_error "Please configure .env file before starting the server"
        exit 1
    fi
}

# Function to start services with nginx
start_with_nginx() {
    print_info "Starting Aras MCP Server with Nginx..."
    check_docker
    
    if check_env; then
        docker-compose --profile nginx up -d
        print_info "Server and Nginx started successfully!"
        print_info "Server available at: http://localhost/"
        print_info "Direct SSE endpoint: http://localhost:8080/sse"
    else
        print_error "Please configure .env file before starting the server"
        exit 1
    fi
}

# Function to stop the services
stop_services() {
    print_info "Stopping Aras MCP Server..."
    docker-compose down
    print_info "Services stopped successfully!"
}

# Function to restart services
restart_services() {
    print_info "Restarting Aras MCP Server..."
    stop_services
    start_services
}

# Function to show logs
show_logs() {
    print_info "Showing logs (Press Ctrl+C to exit)..."
    docker-compose logs -f aras-mcp-server
}

# Function to show status
show_status() {
    print_info "Service Status:"
    docker-compose ps
    
    print_info "\nTesting server health..."
    if curl -s -f http://localhost:8080/sse >/dev/null 2>&1; then
        print_info "✅ Server is healthy and responding"
    else
        print_warning "❌ Server is not responding"
    fi
}

# Function to run client
run_client() {
    local server_url=${1:-"http://localhost:8080/sse"}
    print_info "Starting Aras MCP Client connecting to: $server_url"
    python -m src.sse_client "$server_url"
}

# Function to build the image
build_image() {
    print_info "Building Aras MCP Server Docker image..."
    docker-compose build aras-mcp-server
    print_info "Image built successfully!"
}

# Function to show help
show_help() {
    echo "Aras MCP Server Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start         Start the MCP server"
    echo "  start-nginx   Start the MCP server with Nginx reverse proxy"
    echo "  stop          Stop all services"
    echo "  restart       Restart the MCP server"
    echo "  logs          Show server logs"
    echo "  status        Show service status and health"
    echo "  client [URL]  Start the MCP client (default: http://localhost:8080/sse)"
    echo "  build         Build the Docker image"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                                    # Start server"
    echo "  $0 client                                   # Connect client to localhost"
    echo "  $0 client http://remote-server:8080/sse     # Connect to remote server"
    echo "  $0 start-nginx                              # Start with Nginx proxy"
}

# Main script logic
case "${1:-help}" in
    start)
        start_services
        ;;
    start-nginx)
        start_with_nginx
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    client)
        run_client "$2"
        ;;
    build)
        build_image
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
