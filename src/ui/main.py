"""
MCP Memory Server UI - Main Entry Point
Main entry point for the MCP Memory Server UI.
"""

import sys
import logging
import asyncio
import signal
import argparse
import json
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QEventLoop

from src.ui.main_window import MainWindow
from src.ui.memory_adapter import MemoryAdapter


# Configure logging with more details
log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
log_file = os.path.join(log_dir, 'ui_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments for UI configuration."""
    parser = argparse.ArgumentParser(
        description=(
            "MCP Memory Server UI - Memory visualization and management"
        )
    )
    
    parser.add_argument(
        "--connection-file",
        help="Path to connection info file for direct server connection"
    )
    
    return parser.parse_args()


def load_connection_info(file_path):
    """Load server connection info from file.
    
    Args:
        file_path: Path to the connection info file.
        
    Returns:
        Dictionary with connection info or None if failed.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Connection file not found: {file_path}")
            return None
        
        with open(file_path, 'r') as f:
            connection_info = json.load(f)
        
        logger.info(f"Loaded connection info from {file_path}")
        return connection_info
    except Exception as e:
        logger.error(f"Failed to load connection info: {e}")
        return None


async def init_memory_adapter(connection_info=None):
    """Initialize the memory adapter.
    
    Args:
        connection_info: Optional connection info for direct connection.
        
    Returns:
        Initialized memory adapter.
    """
    adapter = MemoryAdapter(server_connection=connection_info)
    success = await adapter.initialize()
    if not success:
        logger.warning("Failed to initialize memory adapter.")
    return adapter


async def async_main():
    """Async entry point for the application."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Load connection info if provided
    connection_info = None
    if args.connection_file:
        connection_info = load_connection_info(args.connection_file)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MCP Memory Server")
    
    # Create event loop integration
    loop = asyncio.get_event_loop()
    
    # Handle signal to quit app
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, app.quit)
    
    # Create window first so it appears quickly
    window = MainWindow()
    window.show()
    
    # Initialize memory adapter
    adapter = await init_memory_adapter(connection_info)
    window.initialize_with_adapter(adapter)
    
    # Create timer to process asyncio events
    timer = QTimer()
    timer.setInterval(10)  # 10ms
    
    # Process asyncio events from the Qt event loop
    async def process_asyncio_events():
        await asyncio.sleep(0)
    
    timer.timeout.connect(
        lambda: asyncio.create_task(process_asyncio_events())
    )
    timer.start()
    
    # Create Qt event loop
    qt_loop = QEventLoop()
    app.aboutToQuit.connect(qt_loop.quit)
    
    # Run the Qt event loop
    qt_loop.exec()
    
    # Clean up
    timer.stop()
    return 0


def run_ui():
    """Run the UI application."""
    try:
        logger.info("Starting MCP Memory Server UI...")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Command line arguments: {sys.argv}")
        
        if sys.platform == 'win32':
            # Set event loop policy for Windows
            logger.info("Using Windows event loop policy")
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )
        
        # Create and run the asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async main function
        logger.info("Starting async_main function")
        exit_code = loop.run_until_complete(async_main())
        
        # Clean up and exit
        loop.close()
        logger.info(f"UI exiting with code {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running UI: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_ui()
