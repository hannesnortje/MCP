#!/usr/bin/env python3
"""
Memory MCP Server - Entry Point
A Model Context Protocol server for memory management using Qdrant
vector database.
"""

import sys

from src.server_config import get_logger
from src.mcp_server import run_mcp_server

logger = get_logger("memory-server")


def main():
    """Main entry point for the Memory MCP Server."""
    try:
        logger.info("Starting Memory MCP Server...")
        run_mcp_server()
    except KeyboardInterrupt:
        logger.info("Memory server interrupted")
    except EOFError:
        logger.info("Memory server disconnected")
    except Exception as e:
        logger.error(f"Memory server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
