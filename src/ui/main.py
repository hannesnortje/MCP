#!/usr/bin/env python3
"""
AutoGen Desktop UI - Main Entry Point

This module serves as the entry point for the AutoGen desktop application.
It sets up the Qt application, logging, and launches the main window.
"""

import sys
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import AutoGenMainWindow
from .config import load_config


def create_application() -> QApplication:
    """Create and configure the Qt application."""

    # Set application attributes
    app_attrs = Qt.ApplicationAttribute
    # Skip deprecated attributes for newer Qt versions
    try:
        QApplication.setAttribute(app_attrs.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(app_attrs.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # These attributes might not exist in newer Qt versions
        pass

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MCP Memory Server UI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("MCP")
    app.setOrganizationDomain("mcp.local")

    return app


def main() -> int:
    """Main application entry point."""

    try:
        # Load configuration first
        config = load_config()

        # Set up basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger(__name__)

        logger.info("Starting MCP Memory Server UI...")

        # Create Qt application
        app = create_application()

        # Create main window
        main_window = AutoGenMainWindow(config)
        main_window.show()

        logger.info("MCP Memory Server UI started successfully")

        # Run the application
        result = app.exec()

        logger.info("MCP Memory Server UI shutting down...")
        return result

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start MCP Memory Server UI: {e}")
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
