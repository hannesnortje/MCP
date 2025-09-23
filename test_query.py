#!/usr/bin/env python3
"""
Test script to verify document ingestion and query functionality.
"""

import asyncio
from src.tool_handlers import ToolHandlers
from src.memory_manager import QdrantMemoryManager

async def test_query():
    """Test querying for specific content."""
    # Initialize components
    mm = QdrantMemoryManager()
    handlers = ToolHandlers(mm)
    
    # Query for a relevant term
    query_result = handlers.handle_query_memory({
        'query': 'What is the difference between CMM3 and CMM4',
        'memory_types': ['global'],
        'limit': 3,
        'min_score': 0.1
    })
    
    print("\n--- Query Results ---")
    if query_result and 'content' in query_result and query_result['content']:
        for i, result in enumerate(query_result['content']):
            print(f"\nResult {i+1} (score: {result.get('score', 'unknown')}):")
            print(f"{result.get('text', '')[:200]}...\n")
    else:
        print("No results found or error in query")
    
    # Check total points in global memory
    try:
        points_count = mm.client.get_collection('global_memory').points_count
        print(f'\nTotal points in global memory: {points_count}')
    except Exception as e:
        print(f"Error getting collection info: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_query())