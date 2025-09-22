#!/bin/bash
# MCP Memory Server Deployment Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
   print_warning "Running as root. Consider using a non-root user for security."
fi

print_status "🚀 Starting MCP Memory Server deployment..."

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Prerequisites check passed"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

# Create necessary directories
print_status "Creating data directories..."
mkdir -p data logs policy docs/examples
chmod 755 data logs policy docs/examples

# Copy example configuration if config doesn't exist
if [ ! -f "config.yaml" ] && [ -f "config.example.yaml" ]; then
    print_status "Creating default configuration from example..."
    cp config.example.yaml config.yaml
    print_success "Created config.yaml from example. Please review and customize as needed."
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down || true

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose pull

# Build the MCP server image
print_status "Building MCP Memory Server image..."
docker-compose build --no-cache mcp-server

# Start services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check Qdrant
if docker-compose ps qdrant | grep -q "Up (healthy)"; then
    print_success "Qdrant is healthy"
else
    print_warning "Qdrant health check pending... waiting 30 seconds"
    sleep 30
    if docker-compose ps qdrant | grep -q "Up (healthy)"; then
        print_success "Qdrant is healthy"
    else
        print_error "Qdrant is not healthy. Check logs: docker-compose logs qdrant"
    fi
fi

# Check MCP Server
if docker-compose ps mcp-server | grep -q "Up"; then
    print_success "MCP Memory Server is running"
else
    print_error "MCP Memory Server failed to start. Check logs: docker-compose logs mcp-server"
fi

# Display status
print_status "Deployment status:"
docker-compose ps

# Display useful information
print_success "🎉 MCP Memory Server deployment completed!"
echo ""
echo "📋 Service Information:"
echo "  • Qdrant Dashboard: http://localhost:6333/dashboard"
echo "  • Qdrant API: http://localhost:6333"
echo "  • Data Directory: ./data"
echo "  • Logs Directory: ./logs"
echo "  • Configuration: ./config.yaml"
echo ""
echo "🔧 Useful Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • Update services: ./scripts/deploy.sh"
echo ""
echo "📚 Next Steps:"
echo "  1. Review and customize config.yaml"
echo "  2. Add policy documents to ./policy directory"
echo "  3. Check service logs for any issues"
echo "  4. Test the MCP server functionality"

# Optional: Run basic health check
read -p "Would you like to run a basic health check? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running basic health check..."
    
    # Test Qdrant connection
    if curl -s -f http://localhost:6333/health > /dev/null; then
        print_success "Qdrant health check passed"
    else
        print_error "Qdrant health check failed"
    fi
    
    # Test MCP Server (check if container is running)
    if docker-compose exec -T mcp-server python -c "import src.server_config; print('MCP Server OK')" 2>/dev/null; then
        print_success "MCP Server health check passed"
    else
        print_error "MCP Server health check failed"
    fi
fi

print_success "Deployment script completed successfully!"