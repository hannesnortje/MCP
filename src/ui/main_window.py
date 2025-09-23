"""
MCP Memory Server UI - Main Window
Main window implementation for the MCP Memory Server UI.
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStatusBar,
    QLabel,
    QTabWidget,
)
from PySide6.QtCore import Qt


logger = logging.getLogger(__name__)


class MemoryMainWindow(QMainWindow):
    """Main window for the MCP Memory Server UI."""
    
    def __init__(self, server_connection: Optional[Dict[str, Any]] = None):
        """Initialize the main window.
        
        Args:
            server_connection: Optional server connection info for direct access.
        """
        super().__init__()
        self.server_connection = server_connection
        
        # Configure window
        self.setWindowTitle("MCP Memory Server")
        self.resize(1024, 768)
        
        # Set up UI components (placeholder)
        self.setup_ui()
        
        # Log initialization
        if server_connection:
            logger.info("Main window initialized with direct server connection")
        else:
            logger.info("Main window initialized in standalone mode")
    
    def setup_ui(self):
        """Set up the UI components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add placeholder tab for memory browser
        placeholder = QWidget()
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.addWidget(
            QLabel(
                "Memory Browser widget will be implemented in a future step."
            )
        )
        self.tab_widget.addTab(placeholder, "Memory")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add status message
        self.status_bar.showMessage("MCP Memory Server UI - Initial Setup")