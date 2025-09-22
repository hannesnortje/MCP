# MCP Memory Server - Deployment Guide

## Overview

This guide provides complete instructions for deploying the MCP Memory Server in production environments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Production Deployment](#production-deployment)
3. [Development Setup](#development-setup)
4. [Configuration](#configuration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Security Considerations](#security-considerations)

## Quick Start

### Prerequisites

- **Docker**: 20.10.0 or later
- **Docker Compose**: 2.0.0 or later
- **System Requirements**:
  - 4GB RAM minimum (8GB recommended)
  - 10GB disk space minimum
  - Linux/macOS/Windows with Docker support

### One-Command Deployment

```bash
# Clone the repository
git clone <repository-url>
cd MCP

# Run deployment script
./scripts/deploy.sh
```

This will:
- Set up all required services
- Create necessary directories
- Start Qdrant and MCP Memory Server
- Perform health checks

## Production Deployment

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

### 2. Service Deployment

```bash
# Clone and setup
git clone <repository-url>
cd MCP

# Configure production settings
cp config.example.yaml config.yaml
# Edit config.yaml for your environment

# Deploy services
./scripts/deploy.sh
```

### 3. Service Verification

```bash
# Check service status
./scripts/maintenance.sh status

# View logs
./scripts/maintenance.sh logs

# Run health check
./scripts/maintenance.sh health
```

## Development Setup

For local development:

```bash
# Run development setup
./scripts/setup-dev.sh

# This will:
# - Install Python dependencies with Poetry
# - Set up virtual environment
# - Start local Qdrant instance
# - Create VS Code configuration
# - Run initial tests
```

## Configuration

### Environment Variables

Key environment variables for production:

```bash
# Server Configuration
MCP_SERVER_NAME=memory-server-prod
LOG_LEVEL=INFO
LOG_FILE=/app/logs/server.log

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_API_KEY=your_api_key_here

# Performance Tuning
MARKDOWN_CHUNK_SIZE=1000
MARKDOWN_CHUNK_OVERLAP=200
MEMORY_DEDUPLICATION_THRESHOLD=0.95
```

### Configuration Files

#### config.yaml

```yaml
server:
  name: "memory-server-prod"
  version: "1.0.0"
  description: "Production MCP Memory Server"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/app/logs/server.log"

qdrant:
  mode: "remote"
  host: "qdrant"
  port: 6333
  timeout: 60

embedding:
  model_name: "all-MiniLM-L6-v2"
  dimension: 384
  device: "cpu"
  cache_folder: "/app/data/embeddings"
```

#### docker-compose.yml Customization

For production, customize the Docker Compose configuration:

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: mcp-qdrant-prod
    volumes:
      - /opt/mcp/data/qdrant:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
    restart: unless-stopped

  mcp-server:
    image: your-registry/mcp-memory-server:latest
    container_name: mcp-server-prod
    volumes:
      - /opt/mcp/config.yaml:/app/config.yaml:ro
      - /opt/mcp/data:/app/data
      - /opt/mcp/logs:/app/logs
      - /opt/mcp/policy:/app/policy:ro
    restart: unless-stopped
```

## Monitoring and Maintenance

### Daily Operations

```bash
# Check system health
./scripts/maintenance.sh health

# View system statistics
./scripts/maintenance.sh stats

# Check logs for errors
./scripts/maintenance.sh logs mcp-server | grep ERROR
```

### Backup and Recovery

```bash
# Create backup
./scripts/maintenance.sh backup

# List backups
ls -la backups/

# Restore from backup
./scripts/maintenance.sh restore backups/mcp-backup-20240115-143022.tar.gz
```

### Regular Maintenance

```bash
# Weekly cleanup
./scripts/maintenance.sh cleanup

# Monthly updates
./scripts/maintenance.sh update

# Log rotation (automated in production)
logrotate /etc/logrotate.d/mcp-memory-server
```

### Performance Monitoring

#### Key Metrics to Monitor

1. **System Resources**:
   - CPU usage < 80%
   - Memory usage < 80%
   - Disk space > 20% free

2. **Service Health**:
   - Qdrant response time < 100ms
   - MCP server memory usage stable
   - No error spikes in logs

3. **Data Quality**:
   - Embedding generation success rate > 99%
   - Memory deduplication efficiency
   - Query response times

#### Monitoring Setup

```bash
# Add to crontab for regular checks
crontab -e

# Add these lines:
# Health check every 15 minutes
*/15 * * * * /opt/mcp/scripts/maintenance.sh health >> /var/log/mcp-health.log 2>&1

# Daily backup at 2 AM
0 2 * * * /opt/mcp/scripts/maintenance.sh backup >> /var/log/mcp-backup.log 2>&1

# Weekly cleanup at 3 AM Sunday
0 3 * * 0 /opt/mcp/scripts/maintenance.sh cleanup >> /var/log/mcp-cleanup.log 2>&1
```

## Troubleshooting

### Common Issues

#### 1. Qdrant Connection Failed

```bash
# Check Qdrant status
docker-compose logs qdrant

# Test connection
curl -f http://localhost:6333/health

# Restart Qdrant
docker-compose restart qdrant
```

#### 2. High Memory Usage

```bash
# Check memory usage
./scripts/maintenance.sh stats

# Restart services to clear memory
./scripts/maintenance.sh restart

# Adjust chunk size in config.yaml
markdown:
  chunk_size: 500  # Reduce from 1000
```

#### 3. Slow Performance

```bash
# Check system resources
top
df -h

# Optimize embedding model
# Switch to smaller model in config.yaml
embedding:
  model_name: "all-MiniLM-L12-v2"  # Smaller model
```

### Log Analysis

```bash
# View recent errors
docker-compose logs --tail=50 mcp-server | grep ERROR

# Monitor real-time logs
docker-compose logs -f

# Search for specific issues
grep -r "embedding failed" logs/
```

### Health Check Commands

```bash
# Quick health check
curl -f http://localhost:6333/health

# Comprehensive system check
./scripts/maintenance.sh health

# Test embedding functionality
docker-compose exec mcp-server python -c "
from src.memory_manager import MemoryManager
manager = MemoryManager()
print('Embedding test:', len(manager.embedding_model.encode('test')) > 0)
"
```

## Security Considerations

### Production Security Checklist

- [ ] Use non-root user in containers
- [ ] Set up proper firewall rules
- [ ] Use TLS for external connections
- [ ] Implement API authentication
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup encryption
- [ ] Network isolation

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 6333  # Qdrant (if external access needed)
sudo ufw deny 6334   # Qdrant GRPC (internal only)
sudo ufw enable
```

### Container Security

```bash
# Scan images for vulnerabilities
docker scan qdrant/qdrant:latest
docker scan mcp-memory-server:latest

# Use specific image versions (not :latest)
image: qdrant/qdrant:v1.7.0
```

## Scaling Considerations

### Horizontal Scaling

For high-load environments:

1. **Multiple MCP Server Instances**:
   ```yaml
   mcp-server:
     deploy:
       replicas: 3
   ```

2. **Load Balancer**:
   ```yaml
   nginx:
     image: nginx:alpine
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
     ports:
       - "80:80"
   ```

3. **Qdrant Cluster**:
   ```yaml
   qdrant-cluster:
     image: qdrant/qdrant:latest
     environment:
       - QDRANT__CLUSTER__ENABLED=true
   ```

### Vertical Scaling

```yaml
# Adjust resource limits
mcp-server:
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: '2.0'
      reservations:
        memory: 2G
        cpus: '1.0'
```

## Support and Documentation

### Additional Resources

- [API Documentation](./docs/API.md)
- [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
- [Configuration Reference](./config.example.yaml)
- [Test Results](./tests/)

### Getting Help

1. Check logs: `./scripts/maintenance.sh logs`
2. Run health check: `./scripts/maintenance.sh health`
3. Review troubleshooting guide: `docs/TROUBLESHOOTING.md`
4. Check system resources: `./scripts/maintenance.sh stats`

### Updates and Maintenance

```bash
# Check for updates
git pull origin master

# Update services
./scripts/maintenance.sh update

# Verify update
./scripts/maintenance.sh health
```

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Compatibility**: Docker 20.10+, Docker Compose 2.0+