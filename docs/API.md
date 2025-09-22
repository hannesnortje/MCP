# MCP Memory Server - API Documentation

## Overview

The MCP Memory Server implements the Model Context Protocol (MCP) to provide intelligent memory management capabilities. This document describes all available tools, resources, and prompts.

## Table of Contents

1. [Tools API](#tools-api)
2. [Resources API](#resources-api)
3. [Prompts API](#prompts-api)
4. [Configuration API](#configuration-api)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

## Tools API

### Core Memory Management Tools

#### `set_agent_context`

Set the current agent's context for memory operations.

**Schema**:
```json
{
  "name": "set_agent_context",
  "description": "Set the current agent's context for memory operations",
  "inputSchema": {
    "type": "object",
    "properties": {
      "agent_id": {
        "type": "string",
        "description": "Unique identifier for the agent"
      },
      "context_type": {
        "type": "string", 
        "description": "Type of context (e.g., 'task', 'conversation', 'project')"
      },
      "description": {
        "type": "string",
        "description": "Human-readable description of the context"
      }
    },
    "required": ["agent_id", "context_type", "description"]
  }
}
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Agent context set for {agent_id}: {description}"
    }
  ]
}
```

#### `add_to_global_memory`

Add information to global memory accessible by all agents.

**Schema**:
```json
{
  "name": "add_to_global_memory",
  "description": "Add information to global memory accessible by all agents",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Information to store in global memory"
      },
      "category": {
        "type": "string",
        "description": "Category for organizing the memory (optional)"
      },
      "importance": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Importance score (0.0 to 1.0, default: 0.5)"
      }
    },
    "required": ["content"]
  }
}
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Successfully added to global memory\nContent: {content}\nHash: {hash}"
    }
  ]
}
```

#### `add_to_learned_memory`

Store lessons learned to avoid repeated mistakes.

**Schema**:
```json
{
  "name": "add_to_learned_memory", 
  "description": "Store lessons learned to avoid repeated mistakes",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Lesson or insight to store"
      },
      "pattern_type": {
        "type": "string",
        "description": "Type of pattern (e.g., 'mistake', 'best_practice', 'insight')"
      },
      "confidence": {
        "type": "number", 
        "minimum": 0,
        "maximum": 1,
        "description": "Confidence in the lesson (0.0 to 1.0, default: 0.7)"
      }
    },
    "required": ["content"]
  }
}
```

#### `add_to_agent_memory`

Add content to agent-specific memory.

**Schema**:
```json
{
  "name": "add_to_agent_memory",
  "description": "Add content to agent-specific memory", 
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Information to store in agent memory"
      },
      "agent_id": {
        "type": "string",
        "description": "Target agent ID (optional if context is set)"
      },
      "memory_type": {
        "type": "string",
        "description": "Type of memory entry (default: 'general')"
      }
    },
    "required": ["content"]
  }
}
```

#### `query_memory`

Search memory collections for relevant content.

**Schema**:
```json
{
  "name": "query_memory",
  "description": "Search memory collections for relevant content",
  "inputSchema": {
    "type": "object", 
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query text"
      },
      "memory_types": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["global", "learned", "agent", "all"]
        },
        "description": "Types of memory to search (default: ['all'])"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "Maximum number of results (default: 10)"
      },
      "min_score": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Minimum similarity score (default: 0.3)"
      }
    },
    "required": ["query"]
  }
}
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "Found {count} relevant memories:\n\n**Global Memory:**\n- Content: {content}\n  Score: {score}\n  Category: {category}"
    }
  ]
}
```

#### `compare_against_learned_memory`

Check proposed actions against past lessons learned.

**Schema**:
```json
{
  "name": "compare_against_learned_memory",
  "description": "Check proposed actions against past lessons learned",
  "inputSchema": {
    "type": "object",
    "properties": {
      "situation": {
        "type": "string", 
        "description": "Current situation or proposed action to evaluate"
      },
      "comparison_type": {
        "type": "string",
        "enum": ["pattern_match", "anti_pattern", "best_practice"],
        "description": "Type of comparison to perform (default: 'pattern_match')"
      },
      "limit": {
        "type": "integer",
        "minimum": 1, 
        "maximum": 20,
        "description": "Maximum number of lessons to compare (default: 5)"
      }
    },
    "required": ["situation"]
  }
}
```

### Markdown Processing Tools

#### `scan_workspace_markdown`

Scan workspace for markdown files and provide overview.

**Schema**:
```json
{
  "name": "scan_workspace_markdown",
  "description": "Scan workspace for markdown files and provide overview",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Directory path to scan (default: current directory)"
      },
      "recursive": {
        "type": "boolean", 
        "description": "Scan subdirectories recursively (default: true)"
      },
      "include_hidden": {
        "type": "boolean",
        "description": "Include hidden files/directories (default: false)"
      }
    }
  }
}
```

#### `analyze_markdown_content`

Analyze markdown content for structure and metadata.

**Schema**:
```json
{
  "name": "analyze_markdown_content",
  "description": "Analyze markdown content for structure and metadata",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Path to markdown file to analyze"
      },
      "include_ai_analysis": {
        "type": "boolean",
        "description": "Whether to apply AI enhancements (default: true)"
      },
      "extract_metadata": {
        "type": "boolean", 
        "description": "Extract YAML frontmatter and metadata (default: true)"
      }
    },
    "required": ["file_path"]
  }
}
```

#### `optimize_content_for_storage`

Optimize markdown content for efficient vector storage.

**Schema**:
```json
{
  "name": "optimize_content_for_storage", 
  "description": "Optimize markdown content for efficient vector storage",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Path to markdown file"
      },
      "target_memory_type": {
        "type": "string",
        "enum": ["global", "learned", "agent"],
        "description": "Target memory type for optimization"
      },
      "ai_optimization": {
        "type": "boolean",
        "description": "Whether to apply AI optimizations (default: true)"
      },
      "suggested_memory_type": {
        "type": "string", 
        "description": "Originally suggested memory type for comparison"
      }
    },
    "required": ["file_path", "target_memory_type"]
  }
}
```

#### `process_markdown_directory`

Process entire directory of markdown files.

**Schema**:
```json
{
  "name": "process_markdown_directory",
  "description": "Process entire directory of markdown files",
  "inputSchema": {
    "type": "object",
    "properties": {
      "directory": {
        "type": "string", 
        "description": "Directory to process (default: current directory)"
      },
      "recursive": {
        "type": "boolean",
        "description": "Process subdirectories recursively (default: true)"
      },
      "ai_enhancement": {
        "type": "boolean",
        "description": "Whether to apply AI enhancements (default: true)"
      },
      "memory_type": {
        "type": "string",
        "enum": ["global", "learned", "agent", "auto"],
        "description": "Target memory type (default: 'auto')"
      },
      "batch_size": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "Files to process per batch (default: 10)"
      }
    }
  }
}
```

### Advanced Agent Management Tools

#### `initialize_new_agent`

Initialize a new agent with default configuration.

**Schema**:
```json
{
  "name": "initialize_new_agent",
  "description": "Initialize a new agent with default configuration",
  "inputSchema": {
    "type": "object",
    "properties": {
      "agent_id": {
        "type": "string",
        "description": "Unique identifier for the new agent"
      },
      "agent_role": {
        "type": "string",
        "description": "Primary role or function of the agent"
      },
      "capabilities": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of agent capabilities"
      },
      "initial_context": {
        "type": "object",
        "description": "Initial context and configuration"
      }
    },
    "required": ["agent_id", "agent_role"]
  }
}
```

#### `system_health`

Check system health and get diagnostic information.

**Schema**:
```json
{
  "name": "system_health", 
  "description": "Check system health and get diagnostic information about all components",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "additionalProperties": false
  }
}
```

**Response**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "# System Health Report\n\n**Status:** ✅ All systems operational\n**Timestamp:** 2025-01-20T10:30:45.123456\n\n## Component Status\n\n### Memory Manager\n- **Available:** ✅\n- **Initialized:** ✅\n\n### Components\n- **Qdrant:** ✅ healthy\n- **Embedding Model:** ✅ healthy"
    }
  ]
}
```

## Resources API

### Available Resources

#### Memory Status Resource

**URI**: `memory://status`  
**Description**: Get current memory system status and statistics

**Response**:
```json
{
  "uri": "memory://status",
  "name": "Memory System Status", 
  "description": "Current status and statistics of the memory system",
  "mimeType": "application/json",
  "text": "{\"collections\": {...}, \"stats\": {...}}"
}
```

#### Agent Registry Resource

**URI**: `agent://registry`  
**Description**: List all registered agents and their configurations

#### Global Memory Overview

**URI**: `memory://global/overview`  
**Description**: Overview of global memory content and categories

#### Learned Memory Patterns

**URI**: `memory://learned/patterns`  
**Description**: Summary of learned patterns and lessons

## Prompts API

### Available Prompts

#### Agent Startup Prompt

**Name**: `agent_startup`  
**Description**: Guide for initializing agents with proper memory context

**Arguments**:
- `agent_id` (required): Agent identifier
- `agent_role` (required): Agent role/function
- `memory_layers` (optional): Memory layers to access

#### Memory Query Optimization

**Name**: `memory_query_optimization`  
**Description**: Best practices for optimizing memory queries

**Usage**: No arguments required - provides guidance on query optimization techniques.

#### Content Processing Guidelines

**Name**: `content_processing_guidelines`  
**Description**: Guidelines for processing and organizing content

#### Error Handling Guidelines

**Name**: `error_handling_guidelines`  
**Description**: Best practices for handling errors and recovery

## Configuration API

### YAML Configuration Schema

```yaml
server:
  name: string          # Server name
  version: string       # Server version
  description: string   # Server description

logging:
  level: string        # DEBUG|INFO|WARNING|ERROR|CRITICAL
  format: string       # Log message format
  file: string?        # Optional log file path

qdrant:
  mode: string         # local|remote|cloud
  host: string         # Qdrant host
  port: integer        # Qdrant port
  api_key: string?     # Optional API key
  timeout: integer     # Connection timeout

embedding:
  model_name: string   # HuggingFace model name
  dimension: integer   # Vector dimension
  device: string       # cpu|cuda|mps
  cache_folder: string? # Optional cache directory

markdown:
  chunk_size: integer           # Max tokens per chunk
  chunk_overlap: integer        # Overlap between chunks
  recursive_processing: boolean # Process subdirectories
  ai_enhancement_enabled: boolean
  ai_analysis_depth: string     # basic|standard|deep
  ai_content_optimization: boolean

deduplication:
  similarity_threshold: number  # 0.0-1.0
  near_miss_threshold: number   # 0.0-1.0
  logging_enabled: boolean
  diagnostics_enabled: boolean

error_handling:
  retry_attempts: integer       # Max retry attempts
  base_delay: number           # Base delay in seconds
  max_delay: number            # Maximum delay in seconds
  exponential_base: number     # Exponential backoff base
  jitter_enabled: boolean      # Add random jitter
```

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_SERVER_NAME` | string | memory-server | Server name |
| `LOG_LEVEL` | string | INFO | Logging level |
| `LOG_FILE` | string | - | Log file path |
| `QDRANT_HOST` | string | localhost | Qdrant host |
| `QDRANT_PORT` | integer | 6333 | Qdrant port |
| `QDRANT_API_KEY` | string | - | Qdrant API key |
| `EMBEDDING_MODEL` | string | all-MiniLM-L6-v2 | Model name |
| `EMBEDDING_DEVICE` | string | cpu | Compute device |

## Error Handling

### Standard Error Response

```json
{
  "isError": true,
  "content": [
    {
      "type": "text", 
      "text": "Error message describing what went wrong"
    }
  ]
}
```

### Error Categories

1. **Validation Errors** (`400`): Invalid input parameters
2. **Resource Not Found** (`404`): Requested resource doesn't exist  
3. **Server Errors** (`500`): Internal processing errors
4. **Network Errors** (`503`): Connectivity issues with external services

### Retry Behavior

The system automatically retries failed operations with exponential backoff:

- **Qdrant operations**: Up to 3 retries, 1-30 second delays
- **Embedding operations**: Up to 3 retries, 2-60 second delays  
- **Network operations**: Up to 5 retries, 0.5-10 second delays

## Examples

### Basic Memory Operations

```json
// Set agent context
{
  "tool": "set_agent_context",
  "arguments": {
    "agent_id": "dev_assistant",
    "context_type": "development", 
    "description": "Python development assistant"
  }
}

// Add to global memory
{
  "tool": "add_to_global_memory",
  "arguments": {
    "content": "Always use type hints in Python functions",
    "category": "coding_standards",
    "importance": 0.9
  }
}

// Query memory
{
  "tool": "query_memory",
  "arguments": {
    "query": "Python type hints best practices",
    "memory_types": ["global", "learned"],
    "limit": 5,
    "min_score": 0.7
  }
}
```

### Markdown Processing

```json
// Analyze markdown file
{
  "tool": "analyze_markdown_content",
  "arguments": {
    "file_path": "./docs/api_guide.md",
    "include_ai_analysis": true,
    "extract_metadata": true
  }
}

// Process directory
{
  "tool": "process_markdown_directory", 
  "arguments": {
    "directory": "./documentation",
    "recursive": true,
    "memory_type": "global",
    "batch_size": 5
  }
}
```

### System Monitoring

```json
// Check system health
{
  "tool": "system_health",
  "arguments": {}
}

// Read memory status resource  
{
  "method": "resources/read",
  "params": {
    "uri": "memory://status"
  }
}
```

### Using Prompts

```json
// Get memory optimization guidance
{
  "method": "prompts/get",
  "params": {
    "name": "memory_query_optimization"
  }
}

// Get agent startup guidance
{
  "method": "prompts/get",
  "params": {
    "name": "agent_startup",
    "arguments": {
      "agent_id": "new_agent",
      "agent_role": "code_reviewer"
    }
  }
}
```

## Rate Limits and Quotas

### Default Limits

- **Query operations**: 100 requests/minute per agent
- **Write operations**: 50 requests/minute per agent
- **Batch operations**: 10 requests/minute per agent
- **System operations**: 5 requests/minute per agent

### Resource Limits

- **Maximum query results**: 100 per request
- **Maximum content size**: 1MB per memory entry
- **Maximum batch size**: 100 files per batch operation
- **Collection size**: Limited by available storage and RAM

### Optimizing Performance

1. **Use specific memory types** instead of querying all types
2. **Set appropriate similarity thresholds** to limit results
3. **Process files in batches** for large operations  
4. **Cache frequent queries** when possible
5. **Monitor system health** regularly to identify bottlenecks

## Versioning

The API follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to tool schemas or behavior
- **MINOR**: New tools, resources, or backward-compatible enhancements  
- **PATCH**: Bug fixes and minor improvements

Current API version: `1.0.0`

## Support and Feedback

For API questions and issues:
1. Check the [Troubleshooting Guide](./TROUBLESHOOTING.md)
2. Review the [examples](#examples) section
3. Use the `system_health` tool to diagnose issues
4. Create an issue with your API usage details