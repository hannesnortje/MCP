# Document Ingestion for MCP Memory Server

This document explains how to properly ingest markdown documents into the MCP Memory Server database.

## Identified Issue

When using the built-in tools `process_markdown_directory` or `batch_process_directory`, the server analyzes the content but **doesn't actually store it in the database**. This happens because the `MarkdownProcessor.process_directory_batch` method only performs analysis without storage, while the `handle_batch_process_directory` function has a bug with the response structure from `scan_directory_for_markdown`.

## Solution: Use the Document Ingestion Script

We've created a dedicated document ingestion script (`ingest_documents.py`) that properly processes markdown files and stores them in the database.

### Usage

```bash
# Basic usage (processes ./docs directory by default)
poetry run python ingest_documents.py

# Process a specific directory
poetry run python ingest_documents.py /path/to/your/docs

# Process a directory without recursion
poetry run python ingest_documents.py /path/to/your/docs --no-recursive
```

### What the Script Does

1. Scans the specified directory for markdown files
2. Reads and cleans each markdown file
3. Chunks the content appropriately for vector storage
4. Stores each chunk in the global memory collection
5. Provides detailed logging of the process

### Advantages Over Built-in Tools

- Correctly stores content in the database rather than just analyzing it
- Provides detailed logging and progress information
- Optimized for batch processing of multiple files
- More robust error handling and reporting

## Testing Your Ingestion

After running the script, you can verify that your documents were properly ingested with this simple test:

```python
# Quick test script
from src.tool_handlers import ToolHandlers
from src.memory_manager import QdrantMemoryManager

# Initialize components
mm = QdrantMemoryManager()
handlers = ToolHandlers(mm)

# Query for a relevant term from your documents
query_result = handlers.handle_query_memory({
    'query': 'your search term here',
    'memory_types': ['global'],
    'limit': 3,
    'min_score': 0.1
})

print(query_result['content'][0]['text'])

# Check total points in global memory
points_count = mm.client.get_collection('global_memory').points_count
print(f'\nTotal points in global memory: {points_count}')
```

## Future Improvements

A future update to the MCP Memory Server should fix these issues in the built-in tools:

1. The `handle_batch_process_directory` function needs to correctly handle the response from `scan_directory_for_markdown`
2. The `process_directory_batch` method should have an option to store content in the database
3. Error handling in the processing pipeline should be improved

Until these improvements are implemented, use the provided `ingest_documents.py` script for reliable document ingestion.