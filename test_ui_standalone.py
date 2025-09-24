#!/usr/bin/env python3
"""
Test script to verify the UI can start independently
This helps debug UI startup issues separately from the server
"""

import sys
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_ui_imports():
    """Test if all UI imports work correctly"""
    print("Testing UI imports...")
    
    try:
        from PySide6.QtWidgets import QApplication
        print("✅ PySide6.QtWidgets import successful")
        
        from src.ui.config import load_config
        print("✅ UI config import successful")
        
        from src.ui.main_window import AutoGenMainWindow
        print("✅ Main window import successful")
        
        from src.ui.main import create_application, main
        print("✅ UI main module import successful")
        
        return True
    except Exception as e:
        print(f"❌ UI import failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        from src.ui.config import load_config
        config = load_config()
        print(f"✅ Config loaded: {config.keys()}")
        return config
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return None

def test_ui_creation():
    """Test UI creation without actually showing it"""
    print("\nTesting UI creation...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.ui.config import load_config
        from src.ui.main_window import AutoGenMainWindow
        
        # Create QApplication
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        # Load config
        config = load_config()
        print("✅ Config loaded for UI")
        
        # Try to create main window (but don't show it)
        main_window = AutoGenMainWindow(config)
        print("✅ Main window created successfully")
        
        # Clean up
        main_window.close()
        app.quit()
        
        return True
    except Exception as e:
        print(f"❌ UI creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all UI tests"""
    print("=" * 50)
    print("PySide6 UI Standalone Test")
    print("=" * 50)
    
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    success = True
    
    # Test imports
    if not test_ui_imports():
        success = False
    
    # Test config
    config = test_config_loading()
    if config is None:
        success = False
    
    # Test UI creation
    if not test_ui_creation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! UI should be able to start.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())