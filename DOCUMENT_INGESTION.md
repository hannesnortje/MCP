# MCP Document Ingestion Guide

This guide explains how to correctly load documents into the MCP (Memory Context Protocol) database.

## Understanding the Issue

The original `process_markdown_directory` tool had an issue where it would analyze markdown files but not actually store their content in the database. This issue has now been fixed - the tool now delegates to `batch_process_directory` which properly stores content in the database.

## Solutions

### Option 1: Use Directory Processing Tools

You can use either `process_markdown_directory` or `batch_process_directory` tools, as both now properly store content. These can be accessed via the MCP API or UI:

```json
{
  "tool": "batch_process_directory",
  "arguments": {
    "directory": "/path/to/your/documents",
    "memory_type": "global",
    "recursive": true
  }
}
```

Or:

```json
{
  "tool": "process_markdown_directory",
  "arguments": {
    "directory": "/path/to/your/documents",
    "memory_type": "global",
    "recursive": true
  }
}
```

### Option 2: Use the Ingestion Script

For command-line usage, we've created a dedicated document ingestion script:

```bash
# Navigate to the MCP directory
cd /path/to/mcp

# Run the script with default settings (processes ./docs directory)
poetry run python ingest_documents.py

# Specify a different directory
poetry run python ingest_documents.py /path/to/documents

# Control recursion
poetry run python ingest_documents.py /path/to/documents --recursive
```

**Note:** Using Poetry is essential as it ensures the correct dependencies and Python environment are used.

## Understanding How Document Storage Works

1. The system reads each markdown file
2. Content is cleaned and optimized
3. Documents are split into chunks for better search results
4. Each chunk is stored in the vector database (Qdrant)
5. Metadata is added to link chunks to their source documents

## Verifying Document Storage

After ingestion, you can verify that documents were stored properly:

1. Use the `query_memory` tool with a query relevant to your documents
2. Check the Qdrant database directly using Poetry:
   ```bash
   poetry run python -c "from src.memory_manager import QdrantMemoryManager; mm = QdrantMemoryManager(); points = mm.client.scroll('global_memory', limit=50, with_payload=True); [print(point.payload.get('source_file', 'No source')) for point in points[0]]"
   ```

3. Or run a test query to check specific content:
   ```bash
   poetry run python -c "from src.tool_handlers import ToolHandlers; from src.memory_manager import QdrantMemoryManager; import asyncio; async def test(): mm = QdrantMemoryManager(); handlers = ToolHandlers(mm); result = handlers.handle_query_memory({'query': 'your search term', 'memory_types': ['global']}); print(result['content'][0]['text']); asyncio.run(test())"
   ```

## Troubleshooting

If documents still don't appear in search results:

1. Check that the database is running (Qdrant)
2. Verify the file paths and permissions
3. Look for errors in the logs
4. Try querying with different terms or lower similarity thresholds
5. Check if the documents are in valid markdown format

## Environment Setup

MCP uses Poetry for dependency management and environment isolation:

```bash
# Install dependencies (if not already installed)
poetry install

# Activate the virtual environment
poetry shell

# Run commands in the poetry environment without activating shell
poetry run python your_script.py
```

Make sure Qdrant is running (check the `docker-compose.yml` file for configuration).

## Additional Information

For more details on MCP's document processing pipeline, see:
- `src/markdown_processor.py` - Handles document processing and chunking
- `src/memory_manager.py` - Manages database operations
- `src/tool_handlers.py` - Implements the API tools
- `pyproject.toml` - Poetry configuration and dependencies