"""
Test script for MCP Memory Server functionality.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory_manager import QdrantMemoryManager
from markdown_processor import MarkdownProcessor
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_memory_manager():
    """Test the QdrantMemoryManager."""
    logger.info("🧪 Testing QdrantMemoryManager...")
    
    try:
        # Initialize manager
        manager = QdrantMemoryManager()
        await manager.initialize()
        
        # Test content
        test_content = """# Test Document

This is a test document for the memory system.

## Key Points

- Point 1: This is important
- Point 2: This is also important
- Point 3: Remember this lesson

## Conclusion

This concludes the test document.
"""
        
        # Test adding to global memory
        logger.info("📝 Testing add to global memory...")
        hash1 = manager.async_add_to_memory(
            content=test_content,
            memory_type="global",
            metadata={"source": "test", "type": "documentation"}
        )
        
        # Test adding to learned memory
        logger.info("📝 Testing add to learned memory...")
        hash2 = manager.async_add_to_memory(
            content="Never deploy on Friday afternoons. Things go wrong.",
            memory_type="learned",
            metadata={"lesson_type": "deployment", "severity": "high"}
        )
        
        # Test adding to agent memory
        logger.info("📝 Testing add to agent memory...")
        hash3 = manager.async_add_to_memory(
            content="Agent context: I am a helpful coding assistant.",
            memory_type="agent",
            agent_id="test_agent",
            metadata={"type": "context", "role": "assistant"}
        )
        
        # Test queries
        logger.info("🔍 Testing memory queries...")
        
        # Query all memories
        results = manager.async_query_memory("test document", memory_type="all")
        logger.info(f"Found {len(results)} results for 'test document'")
        
        # Query learned memory
        results = manager.async_query_memory("deploy", memory_type="learned")
        logger.info(f"Found {len(results)} results for 'deploy' in learned memory")
        
        # Test duplicate detection
        logger.info("🔍 Testing duplicate detection...")
        is_duplicate = manager.async_check_duplicate(
            content=test_content,
            memory_type="global"
        )
        logger.info(f"Duplicate check result: {is_duplicate}")
        
        # Test collection info
        logger.info("📊 Testing collection info...")
        info = await manager.get_collection_info("global")
        logger.info(f"Global collection info: {info}")
        
        # Cleanup
        await manager.cleanup()
        logger.info("✅ QdrantMemoryManager tests completed successfully")
        
    except Exception as e:
        logger.error(f"❌ QdrantMemoryManager test failed: {e}")
        raise


async def test_markdown_processor():
    """Test the MarkdownProcessor."""
    logger.info("🧪 Testing MarkdownProcessor...")
    
    try:
        processor = MarkdownProcessor()
        
        # Test content
        messy_content = """# Test Document   

This  is   a  test   document    with  messy    formatting.



## Section 1

-  Item  1  
*  Item  2
+   Item  3

### Subsection


Some    content   here.

```python
def test():
    pass
```

More   content.


## Section 2

[Link  ](  https://example.com  )

**bold**   text  and  ***emphasized***   text.

"""
        
        # Test content cleaning
        logger.info("🧹 Testing content cleaning...")
        cleaned = processor.clean_content(messy_content)
        logger.info(f"Original: {len(messy_content)} chars")
        logger.info(f"Cleaned: {len(cleaned)} chars")
        
        # Test section extraction
        logger.info("📄 Testing section extraction...")
        sections = processor.extract_sections(cleaned)
        logger.info(f"Extracted {len(sections)} sections:")
        for section in sections:
            logger.info(f"  - Level {section['level']}: {section['title']}")
        
        # Test plain text conversion
        logger.info("📝 Testing plain text conversion...")
        plain = processor.to_plain_text(cleaned)
        logger.info(f"Plain text: {len(plain)} chars")
        
        # Test word count
        word_count = processor.get_word_count(cleaned)
        logger.info(f"Word count: {word_count}")
        
        # Test summary
        summary = processor.get_summary(cleaned, max_length=100)
        logger.info(f"Summary: {summary}")
        
        logger.info("✅ MarkdownProcessor tests completed successfully")
        
    except Exception as e:
        logger.error(f"❌ MarkdownProcessor test failed: {e}")
        raise


async def main():
    """Main test function."""
    logger.info("🚀 Starting MCP Memory Server tests...")
    
    try:
        await test_markdown_processor()
        logger.info("---")
        await test_memory_manager()
        
        logger.info("🎉 All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())