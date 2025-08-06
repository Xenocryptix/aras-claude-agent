# Aras MCP Docker Deployment Guide

This document provides comprehensive instructions for deploying the Aras MCP Streamable HTTP server using Docker on Ubuntu.

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Install Docker Compose (if not included)
sudo apt install docker-compose-plugin
```

### 2. Deploy with Script

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy the server
./deploy.sh deploy

# Or deploy with nginx reverse proxy
./deploy.sh deploy-nginx
```

### 3. Manual Deployment

```bash
# 1. Configure environment
cp docker-config/env.example docker-config/.env
nano docker-config/.env  # Edit with your Aras settings

# 2. Build and deploy
docker-compose up -d

# 3. Check health
curl http://localhost:8123/health
```

## 📋 Configuration

### Environment Variables

Edit `docker-config/.env` with your settings:

```env
# Required Aras settings
API_URL=http://your-aras-server/Server
API_USERNAME=your_username
API_PASSWORD=your_password
ARAS_DATABASE=InnovatorSolutions

# Optional AI integration
ANTHROPIC_API_KEY=your_anthropic_key
```

### Docker Compose Options

The `docker-compose.yml` includes:

- **Basic deployment**: MCP server only
- **With nginx**: Reverse proxy with SSL/rate limiting
- **Resource limits**: CPU and memory constraints
- **Health checks**: Automatic service monitoring
- **Logging**: Persistent log storage

## 🏗️ Architecture

### Basic Deployment
```
Internet → Docker Host:8123 → MCP Server Container
```

### With Nginx
```
Internet → Docker Host:80/443 → Nginx Container → MCP Server Container
```

## 🔧 Management Commands

### Using Deploy Script

```bash
# Build image only
./deploy.sh build

# Deploy basic server
./deploy.sh deploy

# Deploy with nginx
./deploy.sh deploy-nginx

# Check service health
./deploy.sh health

# View logs
./deploy.sh logs

# Stop services
./deploy.sh stop

# Clean up everything
./deploy.sh cleanup
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# Start with nginx
docker-compose --profile nginx up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Scale service (if needed)
docker-compose up -d --scale aras-mcp-server=2
```

### Using Docker Commands

```bash
# Build image
docker build -t aras-mcp-server:latest .

# Run container
docker run -d \
  --name aras-mcp-server \
  -p 8123:8123 \
  --env-file docker-config/.env \
  aras-mcp-server:latest

# View logs
docker logs -f aras-mcp-server

# Execute commands in container
docker exec -it aras-mcp-server bash

# Stop and remove
docker stop aras-mcp-server
docker rm aras-mcp-server
```

## 🔍 Monitoring and Troubleshooting

### Health Checks

```bash
# Check service health
curl http://localhost:8123/health

# Get detailed status
curl http://localhost:8123/status | jq

# Test MCP endpoint
curl -X POST http://localhost:8123/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

### Log Analysis

```bash
# View real-time logs
docker logs -f aras-mcp-server

# View specific number of log lines
docker logs --tail 100 aras-mcp-server

# Search logs
docker logs aras-mcp-server 2>&1 | grep ERROR

# Export logs
docker logs aras-mcp-server > mcp-server.log
```

### Common Issues

#### 1. Authentication Failures
```bash
# Check Aras connectivity from container
docker exec aras-mcp-server curl -v http://your-aras-server/Server

# Verify credentials
docker exec aras-mcp-server env | grep ARAS_
```

#### 2. Port Conflicts
```bash
# Check what's using port 8123
sudo netstat -tlnp | grep :8123

# Use different port
docker-compose up -d --env PORT=8124
```

#### 3. Memory Issues
```bash
# Check container resource usage
docker stats aras-mcp-server

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS**: Configure SSL certificates
2. **Set resource limits**: Prevent resource exhaustion
3. **Use secrets**: Don't store passwords in environment files
4. **Network isolation**: Use Docker networks
5. **Regular updates**: Keep base images updated

### SSL Configuration

```bash
# Generate self-signed certificate (for testing)
mkdir -p docker-config/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker-config/ssl/key.pem \
  -out docker-config/ssl/cert.pem

# Use with nginx profile
docker-compose --profile nginx up -d
```

### Docker Secrets (Production)

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  aras-mcp-server:
    environment:
      - ARAS_PASSWORD_FILE=/run/secrets/aras_password
    secrets:
      - aras_password

secrets:
  aras_password:
    file: ./secrets/aras_password.txt
```

## 📊 Performance Tuning

### Resource Optimization

```yaml
# Adjust in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Scaling

```bash
# Run multiple instances behind nginx
docker-compose up -d --scale aras-mcp-server=3

# Use external load balancer
# Configure multiple hosts in nginx upstream
```

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or use deploy script
./deploy.sh deploy
```

### Backup Configuration

```bash
# Backup configuration
tar -czf mcp-config-backup.tar.gz docker-config/ logs/

# Restore configuration
tar -xzf mcp-config-backup.tar.gz
```

### Container Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Complete cleanup
docker system prune -a --volumes
```

## 🌐 Network Configuration

### Port Mapping

- `8123` - MCP server (HTTP Streamable)
- `80` - Nginx HTTP (redirects to HTTPS)
- `443` - Nginx HTTPS (when SSL configured)

### Firewall Setup

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow MCP port (if not using nginx)
sudo ufw allow 8123

# Enable firewall
sudo ufw enable
```

## 📈 Monitoring Integration

### Prometheus Metrics (Advanced)

Add to docker-compose.yml:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🆘 Support

### Getting Help

1. **Check logs**: Always start with container logs
2. **Verify configuration**: Ensure all environment variables are set
3. **Test connectivity**: Verify Aras server accessibility
4. **Resource usage**: Check if container has enough resources

### Useful Commands Summary

```bash
# Quick status check
curl -s http://localhost:8123/status | jq '.authentication'

# Restart service
docker-compose restart aras-mcp-server

# View environment
docker exec aras-mcp-server env | grep ARAS_

# Test from inside container
docker exec -it aras-mcp-server python streamable_client.py --non-interactive
```
