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

# Markdown Processing Configuration
MARKDOWN_CHUNK_SIZE = 900  # Maximum tokens per chunk
MARKDOWN_CHUNK_OVERLAP = 200  # Token overlap between chunks
MARKDOWN_PROCESSING_RECURSIVE = True  # Default recursive directory scanning

# AI Enhancement Configuration
AI_ENHANCEMENT_ENABLED = True  # Enable AI-driven content optimization
AI_ANALYSIS_DEPTH = "standard"  # Options: "basic", "standard", "deep"
AI_CONTENT_OPTIMIZATION = True  # Enable AI content optimization

# Policy Processing Configuration
POLICY_DIRECTORY_DEFAULT = "./policy"  # Default policy directory
POLICY_RULE_ID_PATTERN = r"^[A-Z]+-\d+$"  # Valid rule ID format
POLICY_VALIDATION_STRICT = True  # Strict policy validation
POLICY_HASH_ALGORITHM = "sha256"  # Hash algorithm for policy versioning

# Memory Type Analysis Configuration
MEMORY_TYPE_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for suggestions
MEMORY_TYPE_SUGGESTION_ENABLED = True  # Enable memory type suggestions

# Deduplication Configuration
DEDUPLICATION_SIMILARITY_THRESHOLD = 0.85  # Duplicate detection threshold
DEDUPLICATION_NEAR_MISS_THRESHOLD = 0.80   # Near-miss detection threshold
DEDUPLICATION_LOGGING_ENABLED = True       # Enable deduplication logging
DEDUPLICATION_DIAGNOSTICS_ENABLED = True   # Enable similarity diagnostics

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
