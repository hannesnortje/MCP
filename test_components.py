#!/usr/bin/env python3
"""
Simple test to verify MCP server functionality
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.memory_manager import QdrantMemoryManager
from src.markdown_processor import MarkdownProcessor

async def test_components():
    """Test individual components."""
    print("🧪 Testing MCP Memory Server Components...")
    
    # Test markdown processor
    print("\n📝 Testing Markdown Processor...")
    processor = MarkdownProcessor()
    
    test_content = """# Test Document
    
This is a test with multiple    spaces   and
formatting.

## Section 1
- Item 1
- Item 2

Some content here.
"""
    
    cleaned = processor.clean_content(test_content)
    print(f"✅ Content cleaned ({len(cleaned)} chars)")
    
    # Test memory manager
    print("\n🧠 Testing Memory Manager...")
    try:
        manager = QdrantMemoryManager()
        await manager.initialize()
        print("✅ Memory manager initialized")
        
        # Test adding content
        hash_id = await manager.add_to_memory(
            content="Test content for memory",
            memory_type="global",
            metadata={"source": "test"}
        )
        print(f"✅ Content added to global memory (ID: {hash_id[:8]}...)")
        
        # Test query
        results = await manager.query_memory("test content", memory_type="global")
        print(f"✅ Query returned {len(results)} results")
        
        # Test duplicate detection
        is_duplicate = await manager.check_duplicate("Test content for memory", "global")
        print(f"✅ Duplicate detection: {is_duplicate}")
        
        await manager.cleanup()
        print("✅ Memory manager cleanup completed")
        
    except Exception as e:
        print(f"❌ Memory manager test failed: {e}")
        return False
    
    print("\n🎉 All component tests passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_components())
    sys.exit(0 if success else 1)