#!/usr/bin/env python3
"""
MCP Memory Server Unified Launcher

This script provides unified launching of MCP Memory Server components with
configurable UI launch behavior. Based on AutoGen patterns.

Supports:
- MCP server only (no UI)
- MCP server + automatic UI launch
- UI only (for external server)
- Configuration-driven behavior

Usage:
    python launcher.py                    # Use config file settings
    python launcher.py --server-only     # MCP server without UI
    python launcher.py --ui-only         # UI only (connect to existing server)
    python launcher.py --with-ui         # Force launch both server and UI
"""

import sys
import argparse
import subprocess
import signal
import time
from pathlib import Path
from typing import Optional, Any
import logging

# Add project root to path first, then import
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Now import after path is set
from src.ui_config import (  # noqa: E402
    get_config,
    update_ui_launch_mode,
    UILaunchMode,
    should_launch_ui,
)


class MCPLauncher:
    """Manages launching of MCP Memory Server and UI components."""

    def __init__(self) -> None:
        self.config = get_config()
        self.server_process: Optional[subprocess.Popen] = None
        self.ui_process: Optional[subprocess.Popen] = None
        self.qdrant_started_by_launcher = False
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the launcher."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - MCP-LAUNCHER - %(levelname)s - %(message)s",
        )
        return logging.getLogger(__name__)

    def should_launch_ui_local(
        self, force_ui: bool = False, ui_only: bool = False
    ) -> bool:
        """Determine if UI should be launched based on config and flags."""

        if ui_only:
            return True

        if force_ui:
            return True

        # Use the unified logic from config
        result = should_launch_ui(force_ui)
        return bool(result)

    def start_qdrant(self) -> bool:
        """Start Qdrant server via docker-compose if not already running."""

        self.logger.info("Checking Qdrant server...")

        try:
            # Check if Qdrant is already running
            import requests  # type: ignore

            response = requests.get("http://localhost:6333/", timeout=2)
            if response.status_code == 200:
                self.logger.info("✅ Qdrant server already running")
                return True
        except (requests.ConnectionError, requests.Timeout):
            pass  # Qdrant not running, we'll start it
        except Exception as e:
            self.logger.warning(f"Could not check Qdrant status: {e}")

        # Start Qdrant via docker-compose or start existing container
        self.logger.info("Starting Qdrant server...")

        try:
            # First try to start existing container
            start_result = subprocess.run(
                ["docker", "start", "mcp-qdrant"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if start_result.returncode == 0:
                self.logger.info("✅ Started existing Qdrant container")
                result = start_result
            else:
                # Container doesn't exist, create with docker-compose
                self.logger.info("Creating new Qdrant container...")
                result = subprocess.run(
                    ["docker", "compose", "up", "-d", "qdrant"],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            if result.returncode == 0:
                # Wait for Qdrant to be ready
                self.logger.info("Waiting for Qdrant to be ready...")

                import requests  # type: ignore

                for i in range(10):  # Try for 10 seconds
                    try:
                        response = requests.get(
                            "http://localhost:6333/", timeout=1
                        )
                        if response.status_code == 200:
                            msg = "✅ Qdrant server started successfully"
                            self.logger.info(msg)
                            self.qdrant_started_by_launcher = True
                            return True
                    except (requests.ConnectionError, requests.Timeout):
                        pass

                    time.sleep(1)

                self.logger.error("❌ Qdrant started but not responding")
                return False
            else:
                self.logger.error(f"❌ Failed to start Qdrant: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Qdrant startup timed out")
            return False
        except FileNotFoundError:
            self.logger.error(
                "❌ Docker not found. Please install Docker to use Qdrant."
            )
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to start Qdrant: {e}")
            return False

    def start_server(self, server_mode: str = "full") -> bool:
        """Start the MCP server."""

        # Start Qdrant first
        if not self.start_qdrant():
            self.logger.error("❌ Cannot start MCP server without Qdrant")
            return False

        self.logger.info("Starting MCP Memory Server...")

        try:
            # Determine server mode arguments
            mode_args = []
            if server_mode == "tools-only":
                mode_args = ["--tools-only"]
            elif server_mode == "prompts-only":
                mode_args = ["--prompts-only"]

            # Use Poetry to run the server with proper environment
            cmd = ["poetry", "run", "python", "memory_server.py"] + mode_args

            self.logger.info(f"Server command: {' '.join(cmd)}")

            self.server_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Give server time to start
            time.sleep(3)

            if self.server_process.poll() is None:
                pid = self.server_process.pid
                self.logger.info(f"✅ MCP server started (PID: {pid})")
                self.logger.info(f"   Server mode: {server_mode}")
                return True
            else:
                self.logger.error("❌ MCP server failed to start")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to start MCP server: {e}")
            return False

    def start_ui(self) -> bool:
        """Start the PySide6 UI."""

        self.logger.info("Starting MCP Memory UI...")

        try:
            # Use Poetry to run the UI with proper environment
            cmd = ["poetry", "run", "python", "-m", "src.ui.main"]

            self.logger.info(f"UI command: {' '.join(cmd)}")

            self.ui_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Give UI time to start
            time.sleep(2)

            if self.ui_process.poll() is None:
                pid = self.ui_process.pid
                self.logger.info(f"✅ Desktop UI started (PID: {pid})")
                return True
            else:
                self.logger.error("❌ Desktop UI failed to start")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to start Desktop UI: {e}")
            return False

    def stop_all(self) -> None:
        """Stop all running processes."""

        self.logger.info("Shutting down MCP components...")

        # Stop UI first (graceful)
        if self.ui_process and self.ui_process.poll() is None:
            self.logger.info("Stopping Desktop UI...")
            self.ui_process.terminate()
            try:
                self.ui_process.wait(timeout=5)
                self.logger.info("✅ Desktop UI stopped")
            except subprocess.TimeoutExpired:
                self.logger.warning("Force killing Desktop UI...")
                self.ui_process.kill()

        # Stop server
        if self.server_process and self.server_process.poll() is None:
            self.logger.info("Stopping MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
                self.logger.info("✅ MCP server stopped")
            except subprocess.TimeoutExpired:
                self.logger.warning("Force killing MCP server...")
                self.server_process.kill()

        # Stop Qdrant if we started it
        if self.qdrant_started_by_launcher:
            self.logger.info("Stopping Qdrant server...")
            try:
                result = subprocess.run(
                    ["docker", "compose", "stop", "qdrant"],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode == 0:
                    self.logger.info("✅ Qdrant server stopped")
                else:
                    self.logger.warning("⚠️ Failed to stop Qdrant gracefully")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not stop Qdrant: {e}")

    def launch(
        self,
        server_mode: str = "full",
        server_only: bool = False,
        ui_only: bool = False,
        force_ui: bool = False,
    ) -> int:
        """Main launch logic."""

        self.logger.info("=" * 60)
        self.logger.info("MCP Memory Server Unified Launcher")
        self.logger.info("=" * 60)
        mode_str = (
            self.config.ui.launch_mode.value if self.config.ui else "never"
        )
        self.logger.info(f"Configuration mode: {mode_str}")

        try:
            # Determine what to launch
            launch_server = not ui_only
            launch_ui = self.should_launch_ui_local(force_ui, ui_only)

            if server_only:
                launch_ui = False

            plan = f"Server={launch_server}, UI={launch_ui}"
            self.logger.info(f"Launch plan: {plan}")

            # Start components
            if launch_server:
                if not self.start_server(server_mode):
                    return 1

            if launch_ui:
                if not self.start_ui():
                    if launch_server:
                        self.stop_all()
                    return 1

            if not launch_server and not launch_ui:
                self.logger.warning("Nothing to launch! Check configuration.")
                return 1

            # Set up signal handlers for graceful shutdown
            def signal_handler(signum: int, frame: Any) -> None:
                self.logger.info(f"Received signal {signum}, shutting down...")
                self.stop_all()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Wait for processes
            self.logger.info("✅ MCP components running. Press Ctrl+C to stop.")

            while True:
                time.sleep(1)

                # Check if processes are still running
                server_alive = (
                    self.server_process and self.server_process.poll() is None
                )
                ui_alive = self.ui_process and self.ui_process.poll() is None

                if launch_server and not server_alive:
                    self.logger.error("❌ MCP server stopped unexpectedly")
                    break

                if launch_ui and not ui_alive:
                    self.logger.info("✅ Desktop UI closed by user")
                    break

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Launch error: {e}")
            return 1
        finally:
            self.stop_all()

        return 0


def main() -> int:
    """Main entry point with argument parsing."""

    parser = argparse.ArgumentParser(
        description="MCP Memory Server Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                      # Use config file settings
  python launcher.py --server-only       # MCP server without UI
  python launcher.py --ui-only           # UI only (connect to existing server)
  python launcher.py --with-ui           # Force launch both server and UI
  python launcher.py --config-ui-mode never   # Set UI mode to 'never'

Environment Variables:
  LAUNCH_UI=true               # Force UI launch
  MCP_UI_ENABLED=1            # Enable UI launch
        """,
    )

    # Launch mode options
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--server-only",
        action="store_true",
        help="Launch MCP server only (no UI)",
    )
    group.add_argument(
        "--ui-only",
        action="store_true",
        help="Launch UI only (connect to existing server)",
    )
    group.add_argument(
        "--with-ui",
        action="store_true",
        help="Force launch both server and UI",
    )

    # Server mode options
    parser.add_argument(
        "--mode",
        choices=["full", "tools-only", "prompts-only"],
        default="full",
        help="MCP server mode (default: full)",
    )

    # Configuration options
    parser.add_argument(
        "--config-ui-mode",
        choices=["never", "auto", "on_demand"],
        help="Set UI launch mode in config and exit",
    )

    args = parser.parse_args()

    # Handle config update
    if args.config_ui_mode:
        mode = UILaunchMode(args.config_ui_mode)
        update_ui_launch_mode(mode)
        print(f"✅ UI launch mode updated to: {mode.value}")
        return 0

    # Launch components
    launcher = MCPLauncher()
    return launcher.launch(
        server_mode=args.mode,
        server_only=args.server_only,
        ui_only=args.ui_only,
        force_ui=args.with_ui,
    )


if __name__ == "__main__":
    sys.exit(main())
