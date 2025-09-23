"""
MCP Memory Server UI - Main Entry Point
Main entry point for the MCP Memory Server UI.
"""

import sys
import logging
import asyncio
import signal
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QEventLoop

from src.ui.main_window import MainWindow
from src.ui.memory_adapter import MemoryAdapter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def init_memory_adapter():
    """Initialize the memory adapter.
    
    Returns:
        Initialized memory adapter.
    """
    adapter = MemoryAdapter()
    success = await adapter.initialize()
    if not success:
        logger.warning("Failed to initialize memory adapter.")
    return adapter


async def async_main():
    """Async entry point for the application."""
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
    adapter = await init_memory_adapter()
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
        if sys.platform == 'win32':
            # Set event loop policy for Windows
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy()
            )
        
        # Create and run the asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async main function
        exit_code = loop.run_until_complete(async_main())
        
        # Clean up and exit
        loop.close()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_ui()