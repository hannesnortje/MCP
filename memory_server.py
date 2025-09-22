#!/usr/bin/env python3
"""
Memory MCP Server - Entry Point
A Model Context Protocol server for memory management using Qdrant
vector database.

Supports three server modes:
- Full mode: Both prompts and tools (default)
- Prompts-only mode: Only prompts exposed (best for Cursor)
- Tools-only mode: Only tools exposed (best for programmatic use)
"""

import sys
import asyncio
import argparse
import os

from src.server_config import get_logger
from src.mcp_server import run_mcp_server

logger = get_logger("memory-server")


def parse_arguments():
    """Parse command-line arguments for server mode configuration."""
    parser = argparse.ArgumentParser(
        description=(
            "Memory MCP Server - Vector memory management for AI agents"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Server Modes:
  full (default)    Both prompts and tools available
  prompts-only      Only prompts exposed (best for Cursor)
  tools-only        Only tools exposed (best for programmatic use)

Examples:
  python memory_server.py                    # Full mode
  python memory_server.py --prompts-only    # Prompts-only mode
  python memory_server.py --tools-only      # Tools-only mode
  TOOLS_ONLY=1 python memory_server.py      # Tools-only via env var
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--prompts-only",
        action="store_true",
        help="Run server in prompts-only mode (recommended for Cursor)"
    )
    mode_group.add_argument(
        "--tools-only",
        action="store_true",
        help="Run server in tools-only mode (recommended for programmatic use)"
    )
    mode_group.add_argument(
        "--full",
        action="store_true",
        help="Run server in full mode with both prompts and tools (default)"
    )
    
    return parser.parse_args()


def determine_server_mode(args):
    """Determine server mode from arguments and environment variables."""
    # Check environment variables first
    if os.getenv("PROMPTS_ONLY", "").lower() in ("1", "true", "yes"):
        return "prompts-only"
    if os.getenv("TOOLS_ONLY", "").lower() in ("1", "true", "yes"):
        return "tools-only"
    
    # Check command line arguments
    if args.prompts_only:
        return "prompts-only"
    if args.tools_only:
        return "tools-only"
    if args.full:
        return "full"
    
    # Default mode
    return "full"


def main():
    """Main entry point for the Memory MCP Server."""
    try:
        args = parse_arguments()
        server_mode = determine_server_mode(args)
        
        # Log server mode
        mode_messages = {
            "full": (
                "Starting Memory MCP Server in FULL mode (prompts + tools)..."
            ),
            "prompts-only": (
                "Starting Memory MCP Server in PROMPTS-ONLY mode..."
            ),
            "tools-only": (
                "Starting Memory MCP Server in TOOLS-ONLY mode..."
            )
        }
        logger.info(mode_messages[server_mode])
        
        asyncio.run(run_mcp_server(server_mode))
    except KeyboardInterrupt:
        logger.info("Memory server interrupted")
    except EOFError:
        logger.info("Memory server disconnected")
    except Exception as e:
        logger.error(f"Memory server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
