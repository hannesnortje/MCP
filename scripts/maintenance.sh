#!/bin/bash
# MCP Memory Server Maintenance Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

show_help() {
    echo "MCP Memory Server Maintenance Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status      Show service status"
    echo "  logs        Show service logs"
    echo "  backup      Create backup of data and configuration"
    echo "  restore     Restore from backup"
    echo "  cleanup     Clean up old logs and temporary files"
    echo "  update      Update services to latest versions"
    echo "  restart     Restart all services"
    echo "  health      Run comprehensive health check"
    echo "  stats       Show system statistics"
    echo "  help        Show this help message"
    echo ""
}

show_status() {
    print_status "🔍 Checking service status..."
    echo ""
    docker-compose ps
    echo ""
    
    # Check disk usage
    print_status "💾 Disk Usage:"
    du -sh data logs 2>/dev/null || echo "No data/logs directories found"
    
    # Check memory usage of containers
    print_status "🧠 Container Memory Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" || true
}

show_logs() {
    local service="${2:-}"
    
    if [ -n "$service" ]; then
        print_status "📋 Showing logs for $service..."
        docker-compose logs -f "$service"
    else
        print_status "📋 Showing all service logs..."
        docker-compose logs -f
    fi
}

create_backup() {
    local backup_name="mcp-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_dir="./backups/$backup_name"
    
    print_status "💾 Creating backup: $backup_name"
    
    mkdir -p "$backup_dir"
    
    # Backup configuration
    if [ -f "config.yaml" ]; then
        cp config.yaml "$backup_dir/"
        print_success "Configuration backed up"
    fi
    
    # Backup policy files
    if [ -d "policy" ]; then
        cp -r policy "$backup_dir/"
        print_success "Policy files backed up"
    fi
    
    # Backup Qdrant data (stop service first)
    print_status "Stopping services for data backup..."
    docker-compose stop
    
    if [ -d "data" ]; then
        cp -r data "$backup_dir/"
        print_success "Data files backed up"
    fi
    
    # Create backup manifest
    cat > "$backup_dir/manifest.txt" << EOF
MCP Memory Server Backup
Created: $(date)
Backup Name: $backup_name
Contents:
- Configuration (config.yaml)
- Policy files (policy/)
- Qdrant data (data/)
EOF

    # Restart services
    print_status "Restarting services..."
    docker-compose up -d
    
    # Create compressed backup
    tar -czf "./backups/${backup_name}.tar.gz" -C "./backups" "$backup_name"
    rm -rf "$backup_dir"
    
    print_success "Backup created: ./backups/${backup_name}.tar.gz"
}

restore_backup() {
    local backup_file="${2:-}"
    
    if [ -z "$backup_file" ]; then
        print_error "Please specify backup file: $0 restore <backup-file>"
        echo ""
        echo "Available backups:"
        ls -la backups/*.tar.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_warning "⚠️ This will overwrite current configuration and data!"
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled"
        exit 0
    fi
    
    print_status "🔄 Restoring from backup: $backup_file"
    
    # Stop services
    docker-compose down
    
    # Extract backup
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # Find backup directory
    local backup_dir=$(find "$temp_dir" -name "mcp-backup-*" -type d | head -1)
    
    if [ -z "$backup_dir" ]; then
        print_error "Invalid backup file format"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    # Restore files
    if [ -f "$backup_dir/config.yaml" ]; then
        cp "$backup_dir/config.yaml" .
        print_success "Configuration restored"
    fi
    
    if [ -d "$backup_dir/policy" ]; then
        rm -rf policy
        cp -r "$backup_dir/policy" .
        print_success "Policy files restored"
    fi
    
    if [ -d "$backup_dir/data" ]; then
        rm -rf data
        cp -r "$backup_dir/data" .
        print_success "Data files restored"
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    # Restart services
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "Restore completed successfully"
}

cleanup() {
    print_status "🧹 Cleaning up old files..."
    
    # Clean old logs
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
        print_success "Old log files cleaned"
    fi
    
    # Clean old backups (keep last 5)
    if [ -d "backups" ]; then
        ls -t backups/*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f
        print_success "Old backups cleaned"
    fi
    
    # Docker cleanup
    docker system prune -f --volumes
    print_success "Docker cleanup completed"
}

update_services() {
    print_status "🔄 Updating services..."
    
    # Pull latest images
    docker-compose pull
    
    # Rebuild MCP server
    docker-compose build --no-cache mcp-server
    
    # Restart with new images
    docker-compose up -d
    
    print_success "Services updated successfully"
}

restart_services() {
    print_status "🔄 Restarting services..."
    
    docker-compose restart
    
    print_success "Services restarted"
}

health_check() {
    print_status "🏥 Running comprehensive health check..."
    echo ""
    
    local errors=0
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some services are not running"
        ((errors++))
    else
        print_success "All services are running"
    fi
    
    # Check Qdrant health
    if curl -s -f http://localhost:6333/health > /dev/null; then
        print_success "Qdrant health check passed"
    else
        print_error "Qdrant health check failed"
        ((errors++))
    fi
    
    # Check disk space
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        print_error "Disk usage is above 90%: ${disk_usage}%"
        ((errors++))
    else
        print_success "Disk usage is acceptable: ${disk_usage}%"
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$memory_usage" -gt 90 ]; then
        print_warning "Memory usage is high: ${memory_usage}%"
    else
        print_success "Memory usage is acceptable: ${memory_usage}%"
    fi
    
    # Check log files for errors
    if grep -r "ERROR" logs/ 2>/dev/null | head -5; then
        print_warning "Recent errors found in logs"
    else
        print_success "No recent errors in logs"
    fi
    
    echo ""
    if [ $errors -eq 0 ]; then
        print_success "🎉 All health checks passed!"
    else
        print_error "⚠️ $errors health check(s) failed"
    fi
}

show_stats() {
    print_status "📊 System Statistics"
    echo ""
    
    # Container stats
    print_status "Container Statistics:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
    
    # Disk usage
    print_status "Disk Usage:"
    df -h . | tail -1
    echo ""
    
    # Data directory sizes
    if [ -d "data" ]; then
        print_status "Data Directory Sizes:"
        du -sh data/* 2>/dev/null | sort -hr
        echo ""
    fi
    
    # Recent activity
    print_status "Recent Log Activity (last 10 entries):"
    docker-compose logs --tail=10 mcp-server 2>/dev/null || echo "No recent activity"
}

# Main command processing
case "${1:-help}" in
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup "$@"
        ;;
    cleanup)
        cleanup
        ;;
    update)
        update_services
        ;;
    restart)
        restart_services
        ;;
    health)
        health_check
        ;;
    stats)
        show_stats
        ;;
    help|*)
        show_help
        ;;
esac