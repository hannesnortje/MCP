"""
MCP Memory Server UI - Main Window
Main window for the MCP Memory Server UI.
"""

import asyncio
import logging

from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStatusBar,
)
from PySide6.QtCore import QTimer

from src.ui.memory_adapter import MemoryAdapter
from src.ui.widgets.memory_browser import MemoryBrowserWidget


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for the MCP Memory Server UI."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.memory_adapter = None
        self.memory_browser = None
        self.stats_timer = None
        
        # Set up the UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Set window properties
        self.setWindowTitle("MCP Memory Server")
        self.resize(1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create memory browser tab with placeholder
        self.memory_browser = MemoryBrowserWidget()
        self.tab_widget.addTab(self.memory_browser, "Memory")
        
        # Status bar setup
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Initializing...")
        self.status_bar.addWidget(self.status_label)
    
    def initialize_with_adapter(self, adapter: MemoryAdapter):
        """Initialize components with the memory adapter.
        
        Args:
            adapter: The memory adapter to use.
        """
        self.memory_adapter = adapter
        
        # Update memory browser with adapter
        if self.memory_browser:
            self.memory_browser.memory_adapter = adapter
            self.memory_browser.initialize()
        
        # Set up periodic status updates
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_status)
        self.stats_timer.start(10000)  # Update every 10 seconds
        
        # Initial status update
        self.update_status()
    
    def update_status(self):
        """Update the status bar with memory stats."""
        if not self.memory_adapter:
            self.status_label.setText("Memory adapter not initialized")
            return
        
        # Start an async task to update status
        asyncio.create_task(self._do_update_status())
    
    async def _do_update_status(self):
        """Asynchronously update status with memory stats."""
        try:
            # Get stats from memory adapter
            stats = await self.memory_adapter.get_stats()
            
            # Format status message
            status = stats.get("status", "unknown")
            total_docs = stats.get("total_documents", 0)
            total_collections = stats.get("total_collections", 0)
            
            status_text = (
                f"Memory Status: {status.upper()} | "
                f"Collections: {total_collections} | "
                f"Total Documents: {total_docs}"
            )
            
            # Set status with appropriate color
            self.status_label.setText(status_text)
            
            if status == "healthy":
                self.status_label.setStyleSheet("color: green;")
            elif status == "degraded":
                self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setStyleSheet("color: red;")
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            self.status_label.setText("Error fetching memory stats")
            self.status_label.setStyleSheet("color: red;")
