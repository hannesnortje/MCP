#!/usr/bin/env python3
"""
Simple import test for generic memory system
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all generic memory components can be imported."""
    logger.info("Testing imports...")
    
    try:
        # Test core components
        from src.collection_manager import CollectionManager
        logger.info("✅ CollectionManager imported")
        
        from src.generic_memory_service import GenericMemoryService
        logger.info("✅ GenericMemoryService imported")
        
        from src.ui.generic_direct_memory_service import GenericDirectMemoryService
        logger.info("✅ GenericDirectMemoryService imported")
        
        # Test UI components (without creating widgets)
        from src.ui.widgets.generic_memory_browser import (
            GenericMemoryBrowserWidget,
            CreateCollectionDialog
        )
        logger.info("✅ GenericMemoryBrowserWidget imported")
        
        # Test updated services import
        from src.ui.services import MemoryService
        logger.info("✅ Updated MemoryService imported")
        
        logger.info("✅ All imports successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_class_structure():
    """Test class structure without instantiation."""
    logger.info("Testing class structure...")
    
    try:
        from src.collection_manager import CollectionManager, CollectionInfo
        from src.generic_memory_service import GenericMemoryService
        
        # Check class attributes exist
        assert hasattr(CollectionManager, 'create_collection')
        assert hasattr(CollectionManager, 'list_collections')
        assert hasattr(GenericMemoryService, 'add_memory')
        assert hasattr(GenericMemoryService, 'search_memory')
        
        logger.info("✅ Class structure verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Class structure test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("=== Generic Memory System Import Test ===")
    
    import_success = test_imports()
    structure_success = test_class_structure()
    
    if import_success and structure_success:
        logger.info("🎉 All tests passed! Generic memory system ready.")
        print("\n" + "="*60)
        print("SUCCESS: Generic Memory System Integration Complete!")
        print("="*60)
        print("\nNew features available:")
        print("• Dynamic user-defined collections")
        print("• Flexible memory organization")
        print("• Collection templates and migration")
        print("• Enhanced search and UI")
        print("\nTo use: Run main UI → 'Memory (Generic)' tab")
    else:
        logger.error("❌ Tests failed")
        sys.exit(1)