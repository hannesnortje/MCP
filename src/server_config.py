"""
Server configuration and constants for MCP Memory Server.
"""

import logging

# Server Metadata
SERVER_NAME = "memory-server"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = (
    "Memory management server for AI agents using Qdrant vector database"
)

# MCP Protocol Version
MCP_PROTOCOL_VERSION = "2024-11-05"

# Logging Configuration
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Qdrant Configuration
QDRANT_DEFAULT_HOST = "localhost"
QDRANT_DEFAULT_PORT = 6333
QDRANT_HEALTH_ENDPOINT = (
    f"http://{QDRANT_DEFAULT_HOST}:{QDRANT_DEFAULT_PORT}/health"
)
QDRANT_COLLECTIONS_ENDPOINT = (
    f"http://{QDRANT_DEFAULT_HOST}:{QDRANT_DEFAULT_PORT}/collections"
)

# Docker Configuration
QDRANT_DOCKER_IMAGE = "qdrant/qdrant:latest"
QDRANT_CONTAINER_NAME = "qdrant"
QDRANT_DOCKER_PORTS = ["6333:6333", "6334:6334"]

# Timeouts (in seconds)
DOCKER_COMMAND_TIMEOUT = 30
QDRANT_STARTUP_TIMEOUT = 15
HEALTH_CHECK_TIMEOUT = 5

# MCP Capabilities
MCP_CAPABILITIES = {
    "tools": {
        "listChanged": False
    }
}

# MCP Server Info
MCP_SERVER_INFO = {
    "name": SERVER_NAME,
    "version": SERVER_VERSION,
    "description": SERVER_DESCRIPTION
}

# MCP Initialization Response
MCP_INIT_RESPONSE = {
    "protocolVersion": MCP_PROTOCOL_VERSION,
    "capabilities": MCP_CAPABILITIES,
    "serverInfo": MCP_SERVER_INFO
}


def setup_logging() -> logging.Logger:
    """Configure logging for the server."""
    logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
    return logging.getLogger("memory-mcp-server")


def get_logger(name: str = "memory-mcp-server") -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)