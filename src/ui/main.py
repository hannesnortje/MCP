"""
MCP Memory Server UI - Main Entry Point
Main script for launching the MCP Memory Server UI.
"""

import sys
import logging
import argparse
from typing import Optional, Dict, Any

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MemoryMainWindow


def create_application() -> QApplication:
    """Create and configure the Qt application."""
    # Set application attributes
    app_attrs = Qt.ApplicationAttribute
    try:
        QApplication.setAttribute(app_attrs.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(app_attrs.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # These attributes might not exist in newer Qt versions
        pass

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MCP Memory Server")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("MCP")
    app.setOrganizationDomain("mcp.local")

    return app


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP Memory Server UI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--server-connection",
        help="Path to server connection info file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main UI entry point."""
    args = parse_arguments()
    
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Log startup
        logger.info("Starting MCP Memory Server UI...")
        
        # Check if server connection info provided
        server_connection: Optional[Dict[str, Any]] = None
        if args.server_connection:
            import json
            try:
                with open(args.server_connection) as f:
                    server_connection = json.load(f)
                logger.info(f"Loaded server connection info: {args.server_connection}")
            except Exception as e:
                logger.error(f"Failed to load server connection info: {e}")
        
        # Create application
        app = create_application()
        
        # Create main window (placeholder for now)
        main_window = MemoryMainWindow(server_connection)
        main_window.show()
        
        logger.info("MCP Memory Server UI started successfully")
        
        # Run application
        return app.exec()
    
    except Exception as e:
        logger.error(f"Failed to start MCP Memory Server UI: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())