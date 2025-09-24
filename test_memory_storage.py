#!/usr/bin/env python3
"""
Test script to verify memory storage functionality and diagnose initialization issues
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_memory_storage():
    """Test memory storage functionality directly"""
    print("Testing memory storage functionality...")
    
    try:
        from src.memory_manager import QdrantMemoryManager
        
        # Initialize memory manager
        print("Initializing memory manager...")
        manager = QdrantMemoryManager()
        
        # Give it time to initialize
        await asyncio.sleep(2)
        
        # Test storing to global memory
        print("\nTesting global memory storage...")
        test_content = "42 means four two according to Hannes"
        
        result = manager.add_to_global_memory(
            content=test_content,
            category="user_fact",
            importance=0.8
        )
        
        print(f"Storage result: {result}")
        
        if result.get("success"):
            print("✅ Successfully stored to global memory!")
            
            # Test querying the stored content
            print("\nTesting memory query...")
            query_result = manager.query_memory(
                query="42 means four two",
                memory_types=["global"],
                limit=5
            )
            
            print(f"Query result: {query_result}")
            
            if query_result.get("success") and query_result.get("results"):
                print("✅ Successfully queried stored content!")
                for i, item in enumerate(query_result["results"]):
                    print(f"  Result {i+1}: {item['content'][:100]}")
            else:
                print("❌ Failed to query stored content")
                
        else:
            print("❌ Failed to store to global memory")
            print(f"Error: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Memory storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_collections_status():
    """Test the status of Qdrant collections"""
    print("\nTesting Qdrant collections status...")
    
    try:
        from src.memory_manager import QdrantMemoryManager
        
        manager = QdrantMemoryManager()
        await asyncio.sleep(1)
        
        # Check if collections exist
        if hasattr(manager, 'client') and manager.client:
            collections = manager.client.get_collections()
            print(f"Found {len(collections.collections)} collections:")
            
            for collection in collections.collections:
                info = manager.client.get_collection(collection.name)
                print(f"  - {collection.name}: {info.vectors_count} vectors")
                
            return True
        else:
            print("❌ No Qdrant client available")
            return False
            
    except Exception as e:
        print(f"❌ Collections status test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_service_initialization():
    """Test specific service initialization"""
    print("\nTesting service initialization...")
    
    try:
        from src.memory_manager import QdrantMemoryManager
        
        manager = QdrantMemoryManager()
        await asyncio.sleep(1)
        
        # Check various components
        checks = {
            "client": hasattr(manager, 'client') and manager.client is not None,
            "embedding_model": hasattr(manager, 'embedding_model') and manager.embedding_model is not None,
            "vector_operations": hasattr(manager, 'vector_operations') and manager.vector_operations is not None,
            "agent_registry": hasattr(manager, 'agent_registry') and manager.agent_registry is not None,
            "generic_service": hasattr(manager, 'generic_service') and manager.generic_service is not None,
            "collections_initialized": getattr(manager, 'collections_initialized', False)
        }
        
        print("Service initialization status:")
        all_good = True
        for service, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {service}: {status}")
            if not status:
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all memory tests"""
    print("=" * 60)
    print("Memory Service Diagnostic Test")
    print("=" * 60)
    
    success = True
    
    # Test 1: Service initialization
    if not await test_service_initialization():
        success = False
    
    # Test 2: Collections status  
    if not await test_collections_status():
        success = False
    
    # Test 3: Memory storage
    if not await test_memory_storage():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All memory tests passed! Memory service is working properly.")
    else:
        print("❌ Some memory tests failed. Check the errors above.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))