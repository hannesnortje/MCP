#!/usr/bin/env python3
"""
Example script showing different ways to delete documents from the MCP memory database.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from generic_memory_service import GenericMemoryService
from qdrant_client import QdrantClient


async def main():
    """Demonstrate document deletion methods."""
    
    # Initialize services
    client = QdrantClient(host="localhost", port=6333)
    memory_service = GenericMemoryService(client)
    
    print("🗑️  Document Deletion Examples")
    print("=" * 50)
    
    # Method 1: Delete by document ID
    print("\n1. Delete by Document ID:")
    print("   memory_service.delete_memory(memory_id='doc-123', collection='my-collection')")
    
    # Method 2: Search and delete
    print("\n2. Search and Delete Pattern:")
    search_result = await memory_service.search_memory(
        query="test", 
        collections=["global_memory"], 
        limit=1
    )
    
    if search_result.get("success") and search_result.get("results"):
        result = search_result["results"][0]
        document_id = result["id"]
        collection = result["collection"]
        content = result["payload"].get("content", "")[:50] + "..."
        
        print(f"   Found document: {content}")
        print(f"   ID: {document_id}")
        print(f"   Collection: {collection}")
        
        # Uncomment to actually delete:
        # delete_result = await memory_service.delete_memory(
        #     memory_id=document_id, 
        #     collection=collection
        # )
        # print(f"   Delete result: {delete_result}")
    else:
        print("   No documents found to demonstrate deletion")
    
    # Method 3: List collections and their document counts
    print("\n3. Collection Document Counts:")
    collections_result = await memory_service.list_collections()
    
    if collections_result.get("success"):
        for collection in collections_result["collections"]:
            name = collection["name"]
            doc_count = collection["stats"]["document_count"]
            print(f"   {name}: {doc_count} documents")
    
    print("\n📋 Available Deletion Methods:")
    print("   • Via UI: Search results have Delete buttons and right-click context menu")
    print("   • Via API: memory_service.delete_memory(memory_id, collection)")
    print("   • Via MCP Tools: Use existing MCP server tools")
    print("   • Direct Qdrant: client.delete() with point selectors or filters")
    
    print("\n⚠️  Important Notes:")
    print("   • Deletion is permanent and cannot be undone")
    print("   • Make sure you have the correct document ID and collection")
    print("   • Consider backing up important data before bulk deletions")


if __name__ == "__main__":
    asyncio.run(main())