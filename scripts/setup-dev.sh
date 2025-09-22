#!/bin/bash
# MCP Memory Server Development Setup Script

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

print_status "🛠️ Setting up MCP Memory Server for development..."

# Check prerequisites
print_status "Checking development prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    print_error "Python 3.11 or later is required. Current version: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION detected"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    print_warning "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry installation failed. Please install manually."
        exit 1
    fi
fi

print_success "Poetry detected"

# Install dependencies
print_status "Installing Python dependencies..."
poetry install

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    poetry shell
fi

# Create development directories
print_status "Creating development directories..."
mkdir -p data logs policy docs/examples tests/fixtures

# Copy example configuration
if [ ! -f "config.yaml" ] && [ -f "config.example.yaml" ]; then
    print_status "Creating development configuration..."
    cp config.example.yaml config.yaml
    print_success "Created config.yaml for development"
fi

# Setup pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    print_status "Setting up pre-commit hooks..."
    pre-commit install || print_warning "Pre-commit setup failed (optional)"
fi

# Check Docker for local Qdrant
print_status "Checking Docker for local Qdrant..."
if command -v docker &> /dev/null; then
    print_status "Starting local Qdrant instance..."
    
    # Stop existing Qdrant container if running
    docker stop qdrant 2>/dev/null || true
    docker rm qdrant 2>/dev/null || true
    
    # Start new Qdrant container
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v $(pwd)/data/qdrant:/qdrant/storage \
        qdrant/qdrant:latest
    
    # Wait for Qdrant to be ready
    print_status "Waiting for Qdrant to be ready..."
    for i in {1..30}; do
        if curl -s -f http://localhost:6333/health > /dev/null 2>&1; then
            print_success "Qdrant is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            print_warning "Qdrant may not be ready. Check manually: http://localhost:6333"
        fi
    done
else
    print_warning "Docker not found. You'll need to install and run Qdrant manually."
fi

# Run tests to verify setup
print_status "Running tests to verify setup..."
poetry run python -m pytest tests/ -v || print_warning "Some tests failed (may be normal for initial setup)"

# Setup IDE configuration (VS Code)
if [ -d ".vscode" ] || command -v code &> /dev/null; then
    print_status "Setting up VS Code configuration..."
    mkdir -p .vscode
    
    # Create launch.json for debugging
    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "MCP Memory Server",
            "type": "python",
            "request": "launch",
            "program": "memory_server.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
EOF

    # Create settings.json
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
EOF

    print_success "VS Code configuration created"
fi

# Create example policy files
print_status "Creating example policy files..."
mkdir -p policy

cat > policy/01-principles.md << 'EOF'
# Core Principles

## [P-001] Data Integrity
All data must be validated before processing and storage.

## [P-002] Security First
Security considerations must be part of every design decision.

## [P-003] Performance Optimization
System performance must be monitored and optimized continuously.
EOF

cat > policy/02-forbidden-actions.md << 'EOF'
# Forbidden Actions

## [F-101] Unauthorized Data Access
Never access data without proper authorization.

## [F-102] Unencrypted Storage
Never store sensitive data without encryption.

## [F-103] Unvalidated Input
Never process input without proper validation.
EOF

print_success "Example policy files created"

# Display development information
print_success "🎉 Development setup completed!"
echo ""
echo "📋 Development Environment Information:"
echo "  • Python Version: $PYTHON_VERSION"
echo "  • Virtual Environment: .venv"
echo "  • Qdrant: http://localhost:6333"
echo "  • Configuration: config.yaml"
echo "  • Logs: ./logs/"
echo "  • Data: ./data/"
echo ""
echo "🔧 Development Commands:"
echo "  • Activate venv: poetry shell"
echo "  • Run server: poetry run python memory_server.py"
echo "  • Run tests: poetry run pytest"
echo "  • Format code: poetry run black ."
echo "  • Lint code: poetry run pylint src/"
echo ""
echo "🐛 Debugging:"
echo "  • Use VS Code launch configurations"
echo "  • Check logs in ./logs/"
echo "  • Monitor Qdrant at http://localhost:6333/dashboard"
echo ""
echo "📚 Next Steps:"
echo "  1. Customize config.yaml for your setup"
echo "  2. Add your policy documents to ./policy/"
echo "  3. Run tests: poetry run pytest tests/"
echo "  4. Start development: poetry run python memory_server.py"

print_success "Happy coding! 🚀"