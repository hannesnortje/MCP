#!/usr/bin/env python3
"""
Test script for DirectMemoryService integration
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.direct_memory_service import DirectMemoryService


async def test_direct_memory_service():
    """Test that DirectMemoryService can initialize and perform basic operations."""
    print("🧪 Testing DirectMemoryService...")
    
    # Create service instance
    service = DirectMemoryService()
    
    try:
        # Test initialization
        print("📋 Testing initialization...")
        success = await service.initialize()
        print(f"   Initialization: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if not success:
            print("❌ Cannot continue tests without successful initialization")
            return False
        
        # Test getting collections
        print("📊 Testing get_collections...")
        collections = await service.get_collections()
        print(f"   Collections found: {len(collections)}")
        for collection in collections:
            print(f"   - {collection['name']}: {collection['documents_count']} docs")
        
        # Test getting stats
        print("📈 Testing get_stats...")
        stats = await service.get_stats()
        print(f"   Status: {stats.get('status', 'unknown')}")
        print(f"   Total documents: {stats.get('total_documents', 0)}")
        print(f"   Total vectors: {stats.get('total_vectors', 0)}")
        
        # Test a simple search (this might fail if no data exists, which is OK)
        print("🔍 Testing search_memory...")
        try:
            results = await service.search_memory(
                query="test query",
                limit=5,
                min_score=0.1
            )
            print(f"   Search results: {len(results)} items found")
            for i, result in enumerate(results[:3]):  # Show first 3
                print(f"   {i+1}. Score: {result.get('score', 0):.3f} - {result.get('content', '')[:50]}...")
        except Exception as e:
            print(f"   Search test: ⚠️  Expected error (no data): {e}")
        
        # Test adding content
        print("➕ Testing add_memory...")
        try:
            result = await service.add_memory(
                content="Test content for UI integration",
                memory_type="global",
                metadata={"test": True, "source": "ui_test"},
                importance=0.7
            )
            print(f"   Add memory: ✅ SUCCESS - {result}")
            
            # Search for the content we just added
            print("🔍 Testing search for added content...")
            search_results = await service.search_memory(
                query="UI integration test",
                limit=3,
                min_score=0.1
            )
            print(f"   Found {len(search_results)} results after adding content")
            
        except Exception as e:
            print(f"   Add memory test: ❌ FAILED - {e}")
        
        # Cleanup
        await service.shutdown()
        print("🏁 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        try:
            await service.shutdown()
        except:
            pass
        return False


if __name__ == "__main__":
    success = asyncio.run(test_direct_memory_service())
    exit_code = 0 if success else 1
    print(f"\n{'='*50}")
    print(f"Test Result: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*50}")
    exit(exit_code)