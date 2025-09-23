#!/usr/bin/env python3
"""
Memory MCP Server - Entry Point
A Model Context Protocol server for memory management using Qdrant
vector database.

Supports three server modes:
- Full mode: Both prompts and tools (default)
- Prompts-only mode: Only prompts exposed (best for Cursor)
- Tools-only mode: Only tools exposed (best for programmatic use)

Can also launch a UI for memory visualization and management.
"""

import sys
import asyncio
import argparse
import os
import subprocess
import atexit
import signal
import json
import tempfile
from pathlib import Path

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

UI Options:
  --ui              Launch with UI for memory visualization and management
  --ui-only         Launch only the UI without the server (connect to existing)

Examples:
  python memory_server.py                    # Full mode
  python memory_server.py --prompts-only     # Prompts-only mode
  python memory_server.py --tools-only       # Tools-only mode
  python memory_server.py --ui               # Full mode with UI
  python memory_server.py --ui-only          # UI only (no server)
  TOOLS_ONLY=1 python memory_server.py       # Tools-only via env var
  UI=1 python memory_server.py               # UI via env var
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
    
    # UI options
    ui_group = parser.add_mutually_exclusive_group()
    ui_group.add_argument(
        "--ui",
        action="store_true",
        help="Launch with UI for memory visualization and management"
    )
    ui_group.add_argument(
        "--ui-only",
        action="store_true",
        help="Launch only the UI without the server (connect to existing)"
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


def should_launch_ui(args):
    """Determine if UI should be launched based on arguments and env vars."""
    # Check environment variables first
    if os.getenv("UI", "").lower() in ("1", "true", "yes"):
        return True
    if os.getenv("UI_ONLY", "").lower() in ("1", "true", "yes"):
        return "ui-only"
    
    # Check command line arguments
    if args.ui:
        return True
    if args.ui_only:
        return "ui-only"
    
    # Default: no UI
    return False


def launch_ui(server_info=None):
    """Launch the UI as a subprocess.
    
    Args:
        server_info: Optional server connection info for direct connection.
        
    Returns:
        Subprocess object for the UI process.
    """
    logger.info("Launching memory server UI...")
    
    # Create a temporary file with server connection info if provided
    connection_file = None
    if server_info:
        connection_file = tempfile.NamedTemporaryFile(
            mode='w+', suffix='.json', delete=False
        )
        json.dump(server_info, connection_file)
        connection_file.close()
        logger.debug(f"Created connection file at {connection_file.name}")
    
    # Build command to launch UI
    cmd = [sys.executable, "-m", "src.ui.main"]
    if connection_file:
        cmd.extend(["--connection-file", connection_file.name])
    
    # Launch UI subprocess
    try:
        # Get the current directory as the working directory
        working_dir = os.path.abspath(os.path.dirname(__file__))
        
        # When running in Cursor, make sure to pass along environment variables
        env = os.environ.copy()
        
        # Create the subprocess with appropriate settings
        if sys.platform == 'win32':
            # Windows requires different creation flags
            creationflags = subprocess.CREATE_NEW_CONSOLE
            ui_process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                env=env,
                creationflags=creationflags,
            )
        else:
            # Unix/Linux/Mac version
            ui_process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                env=env,
                # Redirect output to devnull to avoid blocking
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                # Start a new process group
                preexec_fn=os.setpgrp
            )
        
        # Log subprocess ID
        logger.info(f"UI process launched with PID {ui_process.pid}")
        
        # Set up cleanup for connection file
        if connection_file:
            def cleanup_connection_file():
                try:
                    os.unlink(connection_file.name)
                    logger.debug(
                        f"Removed connection file {connection_file.name}"
                    )
                except Exception as e:
                    logger.error(f"Failed to remove connection file: {e}")
            
            atexit.register(cleanup_connection_file)
        
        return ui_process
    except Exception as e:
        logger.error(f"Failed to launch UI: {e}")
        if connection_file:
            try:
                os.unlink(connection_file.name)
            except Exception:
                pass
        return None


def main():
    """Main entry point for the Memory MCP Server."""
    ui_process = None
    
    try:
        args = parse_arguments()
        server_mode = determine_server_mode(args)
        ui_option = should_launch_ui(args)
        
        # Handle UI-only mode
        if ui_option == "ui-only":
            logger.info("Starting in UI-only mode (no server)...")
            ui_process = launch_ui()
            
            # Wait for UI process to complete
            if ui_process:
                ui_process.wait()
            return
        
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
        
        # Launch UI if requested
        if ui_option:
            # Create server info for UI
            server_info = {
                "type": "direct",
                "server_mode": server_mode,
                "pid": os.getpid()
            }
            logger.info(
                f"Attempting to launch UI with server info: {server_info}"
            )
            ui_process = launch_ui(server_info)
            
            if ui_process:
                pid = ui_process.pid
                logger.info(
                    f"UI process launched successfully with PID {pid}"
                )
            else:
                logger.error("Failed to launch UI process")
                
                # Provide some troubleshooting info
                logger.error("Troubleshooting information:")
                logger.error(f"  Python executable: {sys.executable}")
                logger.error(f"  Current directory: {os.getcwd()}")
                logger.error(
                    f"  PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}"
                )
                
                ui_path = os.path.join(
                    os.path.dirname(__file__), 'src', 'ui', 'main.py'
                )
                logger.error(f"  UI module exists: {os.path.exists(ui_path)}")
        
        # Define cleanup function for UI process
        def cleanup_ui():
            if ui_process:
                logger.info("Shutting down UI process...")
                try:
                    if sys.platform == 'win32':
                        # Windows requires different termination approach
                        ui_process.terminate()
                    else:
                        # Send SIGTERM on Unix
                        os.kill(ui_process.pid, signal.SIGTERM)
                    
                    # Give it a moment to shut down gracefully
                    ui_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    logger.warning(
                        "UI didn't shut down gracefully, forcing..."
                    )
                    if sys.platform == 'win32':
                        ui_process.kill()
                    else:
                        os.kill(ui_process.pid, signal.SIGKILL)
                except Exception as e:
                    logger.error(f"Error shutting down UI: {e}")
        
        # Register cleanup function
        atexit.register(cleanup_ui)
        
        # Run the MCP server
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
