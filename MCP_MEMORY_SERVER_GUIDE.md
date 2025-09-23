# MCP Memory Server - Comprehensive Guide

This guide provides a detailed overview of the Memory Context Protocol (MCP) server and common operations, troubleshooting, and best practices.

## Table of Contents
1. [Overview](#overview)
2. [Server Modes](#server-modes)
3. [Basic Operations](#basic-operations)
4. [Content Ingestion](#content-ingestion)
5. [Memory Types](#memory-types)
6. [Querying Memory](#querying-memory)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

The MCP Memory Server is a vector database system that stores markdown content in a way that allows AI agents to perform semantic search and recall information. It's designed for:

- Storing reference documentation
- Recording learned insights and patterns
- Maintaining agent-specific context
- Enforcing policies and compliance
- Providing long-term memory for AI agents

The system uses [Qdrant](https://qdrant.tech/) as the vector database backend and [Sentence Transformers](https://www.sbert.net/) for generating embeddings.

## Server Modes

The server can run in three modes:

1. **Full mode** (default) - Both prompts and tools available
2. **Prompts-only mode** - Only prompts exposed (best for Cursor)
3. **Tools-only mode** - Only tools exposed (best for programmatic use)

You can specify the mode when starting the server:

```bash
# Full mode (default)
python memory_server.py

# Prompts-only mode
python memory_server.py --prompts-only
# OR
PROMPTS_ONLY=1 python memory_server.py

# Tools-only mode
python memory_server.py --tools-only
# OR
TOOLS_ONLY=1 python memory_server.py
```

## Basic Operations

### Starting the Server

```bash
# Basic startup
cd /path/to/mcp
poetry run python memory_server.py

# With custom configuration
QDRANT_HOST=localhost QDRANT_PORT=6333 poetry run python memory_server.py
```

### Configuration

The server can be configured using:
- Environment variables
- Config file (`config.yaml`)
- Command-line arguments

Example configuration:

```yaml
# config.yaml
server:
  name: "memory-server-prod"
  version: "1.0.0"
  description: "Production MCP Memory Server"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/app/logs/server.log"

qdrant:
  mode: "remote"
  host: "qdrant"
  port: 6333
  timeout: 60

embedding:
  model_name: "all-MiniLM-L6-v2"
  dimension: 384
  device: "cpu"
  cache_folder: "/app/data/embeddings"
```

## Content Ingestion

The server provides three main ways to ingest markdown content:

### 1. Processing Individual Files

```python
result = memory_tool_handlers.handle_process_markdown_file({
    "path": "/path/to/file.md",
    "memory_type": "global",  # Optional, can auto-suggest
    "auto_suggest": True,     # Whether to auto-suggest memory type
    "agent_id": None          # Optional, for agent-specific memory
})
```

### 2. Batch Processing Multiple Files

```python
result = memory_tool_handlers.handle_batch_process_markdown_files({
    "file_assignments": [
        {"path": "/path/to/file1.md", "memory_type": "global"},
        {"path": "/path/to/file2.md", "memory_type": "learned"},
        {"path": "/path/to/file3.md"}  # Will use default or auto-suggest
    ],
    "default_memory_type": "global"  # Optional default type
})
```

### 3. Processing Entire Directories

```python
result = memory_tool_handlers.handle_batch_process_directory({
    "directory": "/path/to/docs",
    "memory_type": "global",  # Optional, can auto-suggest per file
    "recursive": True,        # Whether to scan subdirectories
    "agent_id": None          # Optional, for agent-specific memory
})
```

## Memory Types

The system supports three main memory types:

1. **Global Memory** (`global`)
   - Documentation, references, specs, standards
   - Shared across all agents
   - Permanent, factual information

2. **Learned Memory** (`learned`)
   - Insights, patterns, lessons learned
   - Shared knowledge that evolves over time
   - Best practices and observations

3. **Agent Memory** (`agent`)
   - Agent-specific context and preferences
   - Personal notes and drafts
   - Session-specific information

The markdown processor can automatically suggest the appropriate memory type based on content analysis.

## Querying Memory

To retrieve information from memory:

```python
result = memory_tool_handlers.handle_query_memory({
    "query": "How to configure Qdrant connection?",
    "memory_types": ["global", "learned", "agent"],  # Types to search
    "limit": 10,              # Maximum results to return
    "min_score": 0.3          # Minimum similarity score (0-1)
})
```

For learned patterns comparison:

```python
result = memory_tool_handlers.handle_compare_against_learned_memory({
    "situation": "The server is failing to connect to Qdrant",
    "comparison_type": "troubleshooting",
    "limit": 5                # Maximum results to return
})
```

## Troubleshooting

### Common Issues

#### Qdrant Connection Problems

**Symptom**: "Failed to initialize Qdrant: ConnectionError"

**Solutions**:
1. Check if Qdrant is running:
   ```bash
   curl http://localhost:6333/health
   ```
2. Verify configuration in `config.yaml` or environment variables:
   ```bash
   export QDRANT_HOST=localhost
   export QDRANT_PORT=6333
   ```
3. Check if the port is open and available:
   ```bash
   netstat -ln | grep 6333
   ```
4. Start Qdrant manually:
   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage \
     qdrant/qdrant:latest
   ```

#### Embedding Model Issues

**Symptom**: "Failed to load embedding model"

**Solutions**:
1. Check internet connection (required for first download)
2. Try alternative models:
   ```bash
   export EMBEDDING_MODEL="all-MiniLM-L6-v2"
   ```
3. Clear model cache if corrupted:
   ```bash
   rm -rf ~/.cache/torch/sentence_transformers/
   ```
4. Check disk space (models can be 400MB+):
   ```bash
   df -h ~/.cache/
   ```

#### High Memory Usage

**Symptom**: System running slowly, high RAM usage

**Solutions**:
1. Monitor system resources:
   ```bash
   free -h
   top -p $(pgrep -f memory_server)
   ```
2. Optimize configuration:
   ```yaml
   embedding:
     model_name: "all-MiniLM-L6-v2"  # Smaller, faster model
     device: "cpu"  # Use "cuda" if you have GPU
   
   markdown:
     chunk_size: 500  # Reduce for lower memory usage
     chunk_overlap: 100
   ```

#### Slow Query Performance

**Solutions**:
1. Tune similarity thresholds:
   ```yaml
   deduplication:
     similarity_threshold: 0.85  # Higher = faster, fewer results
   ```
2. Optimize query parameters:
   ```python
   # Search specific memory types instead of all
   result = memory_tool_handlers.handle_query_memory({
       "query": "specific search terms",
       "memory_types": ["global"],  # Instead of all types
       "limit": 5                   # Reduce result set size
   })
   ```

### System Health Check

You can run a system health check to diagnose issues:

```python
result = memory_tool_handlers.handle_system_health({})
```

This will return a detailed report about the state of all components.

### Reset Collections

If you need to completely reset the database (CAUTION: this will lose all data):

```bash
# Stop the server
pkill -f memory_server

# Remove Qdrant data
rm -rf ./qdrant_storage/*

# Restart Qdrant
docker restart qdrant

# Restart the server
poetry run python memory_server.py
```

## Best Practices

### Memory Usage

1. **Choose the right memory type**:
   - Global: Documentation, specs, APIs, standards
   - Learned: Insights, patterns, lessons, best practices
   - Agent: Personal context, preferences, session state

2. **Optimize query parameters**:
   - Start with specific queries before broadening
   - Use technical terms when possible
   - Filter by memory type to narrow results

3. **Content chunking**:
   - The system automatically chunks long documents
   - Default chunk size is 900 tokens (configurable)
   - Headers are preserved for context

4. **Deduplication**:
   - The system checks for duplicates before storing
   - Similarity threshold is configurable (default 0.9)
   - Near-miss detection flags potential duplicates

### Performance Optimization

1. **Batch processing**:
   - Use batch_process_directory for processing many files
   - Process related files together for context

2. **Query optimization**:
   - Similarity thresholds: 0.9+ exact, 0.8-0.9 related, 0.7-0.8 discovery
   - Progressive queries: start specific, broaden if needed
   - Keyword optimization: technical terms, action words, context markers

3. **Resource usage**:
   - Use smaller embedding models for speed
   - Enable GPU acceleration if available
   - Adjust chunk sizes for memory constraints

### Maintenance

1. **Regular collection cleanup**:
   - Periodically remove outdated or duplicate entries
   - Archive rarely used memories

2. **Monitor system health**:
   - Check error logs and rates
   - Monitor disk usage for Qdrant storage
   - Track response times for queries

3. **Backups**:
   - Backup the Qdrant storage directory regularly
   - Document memory organization and structure