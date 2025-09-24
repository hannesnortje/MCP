"""
MCP (Model Context Protocol) server implementation for memory management.
Handles the MCP protocol communication and tool orchestration.
Enhanced with production-grade error handling and monitoring.
"""

import json
from typing import Dict, Any, List, Optional

from .server_config import get_logger
from .qdrant_manager import ensure_qdrant_running
from .tool_handlers import ToolHandlers
from .resource_handlers import ResourceHandlers
from .prompt_handlers import PromptHandlers
from .tool_definitions import MemoryToolDefinitions
from .mcp_protocol_handler import MCPProtocolHandler
from .system_health_monitor import SystemHealthMonitor

logger = get_logger("mcp-server")

# Import our memory manager
try:
    from .memory_manager import QdrantMemoryManager
    MEMORY_AVAILABLE = True
    logger.info("Memory manager available")
except ImportError as e:
    MEMORY_AVAILABLE = False
    logger.error(f"Memory manager not available: {e}")


class MemoryMCPServer:
    """MCP Server focused solely on memory management using Qdrant."""
    
    def __init__(self, server_mode="full"):
        self.server_mode = server_mode
        logger.info(
            f"Starting Memory MCP Server in {server_mode.upper()} mode..."
        )
        
        # Ensure Qdrant is running before initializing memory manager
        if not ensure_qdrant_running():
            logger.error(
                "❌ Failed to start Qdrant. "
                "Memory server will not function properly."
            )
        
        if MEMORY_AVAILABLE:
            try:
                self.memory_manager = QdrantMemoryManager()
                logger.info("Memory manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize memory manager: {e}")
                self.memory_manager = None
        else:
            self.memory_manager = None
        
        # Initialize handlers and monitors
        self.tool_handlers = ToolHandlers(self.memory_manager)
        self.resource_handlers = ResourceHandlers(self.memory_manager)
        self.health_monitor = SystemHealthMonitor(self.memory_manager)
        
        # Conditionally initialize prompt handlers based on server mode
        if server_mode in ["full", "prompts-only"]:
            self.prompt_handlers = PromptHandlers(self.memory_manager)
            logger.info("Prompt handlers initialized")
        else:
            self.prompt_handlers = None
            logger.info("Prompt handlers disabled (tools-only mode)")
        
        logger.info("Memory MCP Server initialized")

    @retry_qdrant_operation(max_attempts=2)
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        health_info = {
            "timestamp": str(datetime.now()),
            "overall_status": "unknown",
            "components": {},
            "error_statistics": error_handler.get_error_stats(),
            "memory_manager": {
                "available": self.memory_manager is not None,
                "collections_initialized": False
            }
        }
        
        try:
            # Check Qdrant connection
            if self.memory_manager and self.memory_manager.client:
                try:
                    collections = self.memory_manager.client.get_collections()
                    health_info["components"]["qdrant"] = {
                        "status": "healthy",
                        "collections_count": len(collections.collections),
                        "collections": [col.name for col in collections.collections]
                    }
                    health_info["memory_manager"]["collections_initialized"] = True
                except Exception as e:
                    health_info["components"]["qdrant"] = {
                        "status": "unhealthy", 
                        "error": str(e)
                    }
            else:
                health_info["components"]["qdrant"] = {
                    "status": "unavailable",
                    "error": "Memory manager not initialized"
                }
            
            # Check embedding model
            if (self.memory_manager and 
                self.memory_manager.embedding_model):
                try:
                    # Test embedding with a simple text
                    test_embedding = self.memory_manager._embed_text("test")
                    health_info["components"]["embedding_model"] = {
                        "status": "healthy",
                        "model_name": str(self.memory_manager.embedding_model),
                        "embedding_dimension": len(test_embedding)
                    }
                except Exception as e:
                    health_info["components"]["embedding_model"] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            else:
                health_info["components"]["embedding_model"] = {
                    "status": "unavailable",
                    "error": "Embedding model not loaded"
                }
            
            # Check handlers
            health_info["components"]["handlers"] = {
                "tool_handlers": self.tool_handlers is not None,
                "resource_handlers": self.resource_handlers is not None,
                "prompt_handlers": self.prompt_handlers is not None
            }
            
            # Determine overall status
            component_statuses = [
                comp.get("status", "unknown") 
                for comp in health_info["components"].values() 
                if isinstance(comp, dict) and "status" in comp
            ]
            
            if all(status == "healthy" for status in component_statuses):
                health_info["overall_status"] = "healthy"
            elif any(status == "unhealthy" for status in component_statuses):
                health_info["overall_status"] = "degraded"
            else:
                health_info["overall_status"] = "unavailable"
                
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            health_info["overall_status"] = "error"
            health_info["health_check_error"] = str(e)
        
        return health_info

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available memory management tools."""
        if not self.memory_manager:
            return []
            
        return [
            {
                "name": "set_agent_context",
                "description": (
                    "Set the current agent's context for memory operations"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Unique identifier for the agent"
                        },
                        "context_type": {
                            "type": "string",
                            "description": (
                                "Type of context "
                                "(e.g., 'task', 'conversation', 'project')"
                            )
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "Human-readable description of the context"
                            )
                        }
                    },
                    "required": ["agent_id", "context_type", "description"]
                }
            },
            {
                "name": "add_to_global_memory",
                "description": (
                    "Add information to global memory accessible by all agents"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": (
                                "Information to store in global memory"
                            )
                        },
                        "category": {
                            "type": "string",
                            "description": (
                                "Category for organizing the memory (optional)"
                            )
                        },
                        "importance": {
                            "type": "number",
                            "description": (
                                "Importance score 0.0-1.0 "
                                "(optional, default 0.5)"
                            )
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "add_to_learned_memory",
                "description": (
                    "Add learned patterns or insights that should be "
                    "remembered for future tasks"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": (
                                "Learned insight or pattern to remember"
                            )
                        },
                        "pattern_type": {
                            "type": "string",
                            "description": "Type of pattern learned (optional)"
                        },
                        "confidence": {
                            "type": "number",
                            "description": (
                                "Confidence in this learning 0.0-1.0 "
                                "(optional, default 0.7)"
                            )
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "add_to_agent_memory",
                "description": "Add information to specific agent's memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": (
                                "Information to store in agent's memory"
                            )
                        },
                        "agent_id": {
                            "type": "string",
                            "description": (
                                "Agent ID "
                                "(optional, uses current context "
                                "if not provided)"
                            )
                        },
                        "memory_type": {
                            "type": "string",
                            "description": "Type of memory (optional)"
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "query_memory",
                "description": (
                    "Search and retrieve relevant information from memory"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Search query to find relevant memories"
                            )
                        },
                        "memory_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Types of memory to search "
                                "(optional, searches all by default)"
                            )
                        },
                        "limit": {
                            "type": "number",
                            "description": (
                                "Maximum number of results "
                                "(optional, default 10)"
                            )
                        },
                        "min_score": {
                            "type": "number",
                            "description": (
                                "Minimum similarity score 0.0-1.0 "
                                "(optional, default 0.3)"
                            )
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "compare_against_learned_memory",
                "description": (
                    "Compare current situation against "
                    "learned patterns and insights"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": (
                                "Current situation or context to compare"
                            )
                        },
                        "comparison_type": {
                            "type": "string",
                            "description": "Type of comparison (optional)"
                        },
                        "limit": {
                            "type": "number",
                            "description": (
                                "Maximum number of similar patterns to return "
                                "(optional, default 5)"
                            )
                        }
                    },
                    "required": ["situation"]
                }
            },
            # New Markdown Processing Tools
            {
                "name": "scan_workspace_markdown",
                "description": (
                    "Scan directory for markdown files with configurable "
                    "recursive search"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": (
                                "Directory path to scan "
                                "(default current directory)"
                            )
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": (
                                "Whether to scan subdirectories "
                                "(default true)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_markdown_content",
                "description": (
                    "Analyze markdown content and suggest appropriate "
                    "memory type with AI integration hooks"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Markdown content to analyze"
                        },
                        "suggest_memory_type": {
                            "type": "boolean",
                            "description": (
                                "Whether to suggest memory type (default true)"
                            )
                        },
                        "ai_enhance": {
                            "type": "boolean",
                            "description": (
                                "Whether to apply AI enhancements (default true)"
                            )
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "optimize_content_for_storage",
                "description": (
                    "Optimize content for database storage based on "
                    "memory type with AI enhancement hooks"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to optimize"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Target memory type (default global)"
                            )
                        },
                        "ai_optimization": {
                            "type": "boolean",
                            "description": (
                                "Whether to apply AI optimizations (default true)"
                            )
                        },
                        "suggested_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Originally suggested memory type for comparison"
                            )
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "process_markdown_directory",
                "description": (
                    "Process entire directory of markdown files with "
                    "batch AI-enhanced analysis and memory type suggestions"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": (
                                "Directory to process (default current directory)"
                            )
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Fixed memory type (null for auto-suggestion)"
                            )
                        },
                        "auto_suggest": {
                            "type": "boolean",
                            "description": (
                                "Whether to auto-suggest memory types "
                                "(default true)"
                            )
                        },
                        "ai_enhance": {
                            "type": "boolean",
                            "description": (
                                "Whether to apply AI enhancements (default true)"
                            )
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": (
                                "Whether to scan subdirectories (default true)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "validate_and_deduplicate",
                "description": (
                    "Validate content for duplicates using enhanced cosine "
                    "similarity detection with near-miss analysis"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to check for duplicates"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Memory type to check against (default global)"
                            )
                        },
                        "agent_id": {
                            "type": "string",
                            "description": (
                                "Agent ID for agent-specific memory checks"
                            )
                        },
                        "threshold": {
                            "type": "number",
                            "description": (
                                "Similarity threshold (0.0-1.0, "
                                "defaults to configured value)"
                            )
                        },
                        "enable_near_miss": {
                            "type": "boolean",
                            "description": (
                                "Enable near-miss detection and logging "
                                "(default true)"
                            )
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "process_markdown_file",
                "description": (
                    "Process single markdown file through complete pipeline: "
                    "analyze, optimize, chunk, deduplicate, and store"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to process"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Memory type (null for auto-suggestion)"
                            )
                        },
                        "auto_suggest": {
                            "type": "boolean",
                            "description": (
                                "Auto-suggest memory type (default true)"
                            )
                        },
                        "agent_id": {
                            "type": "string",
                            "description": (
                                "Agent ID for agent-specific memory"
                            )
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "batch_process_markdown_files",
                "description": (
                    "Process multiple markdown files with specific "
                    "memory type assignments"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_assignments": {
                            "type": "array",
                            "description": (
                                "Array of file processing assignments"
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {
                                        "type": "string",
                                        "description": "File path"
                                    },
                                    "memory_type": {
                                        "type": "string",
                                        "enum": ["global", "learned", "agent"],
                                        "description": (
                                            "Memory type for this file"
                                        )
                                    },
                                    "agent_id": {
                                        "type": "string",
                                        "description": (
                                            "Agent ID if memory_type is agent"
                                        )
                                    }
                                },
                                "required": ["path"]
                            }
                        },
                        "default_memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Default memory type for files "
                                "without assignment"
                            )
                        }
                    },
                    "required": ["file_assignments"]
                }
            },
            {
                "name": "batch_process_directory",
                "description": (
                    "Process entire directory through complete pipeline: "
                    "discover, analyze, optimize, deduplicate, and store"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": (
                                "Directory to process "
                                "(default current directory)"
                            )
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": (
                                "Memory type for all files "
                                "(null for auto-suggestion)"
                            )
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": (
                                "Process subdirectories recursively "
                                "(default true)"
                            )
                        },
                        "agent_id": {
                            "type": "string",
                            "description": (
                                "Agent ID for agent-specific memory"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "initialize_new_agent",
                "description": (
                    "Initialize a new agent with role, memory layer "
                    "configuration, and policy loading (enhanced version "
                    "of agent_startup prompt)"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": (
                                "Unique identifier for the agent "
                                "(auto-generated if not provided)"
                            )
                        },
                        "agent_role": {
                            "type": "string",
                            "description": (
                                "Role of the agent (default: general)"
                            )
                        },
                        "memory_layers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["global", "learned", "agent"]
                            },
                            "description": (
                                "Memory layers agent can access "
                                "(default: ['global', 'learned'])"
                            )
                        },
                        "policy_version": {
                            "type": "string",
                            "description": (
                                "Policy version to load (default: latest)"
                            )
                        },
                        "policy_hash": {
                            "type": "string",
                            "description": (
                                "Expected policy hash for verification"
                            )
                        },
                        "load_policies": {
                            "type": "boolean",
                            "description": (
                                "Whether to load policies during initialization "
                                "(default: true)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "configure_agent_permissions",
                "description": (
                    "Configure memory layer access permissions for an agent"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID to configure"
                        },
                        "permissions": {
                            "type": "object",
                            "description": "Permission configuration",
                            "properties": {
                                "can_read": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["global", "learned", "agent"]
                                    },
                                    "description": (
                                        "Memory layers agent can read from"
                                    )
                                },
                                "can_write": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["global", "learned", "agent"]
                                    },
                                    "description": (
                                        "Memory layers agent can write to"
                                    )
                                },
                                "can_admin": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["global", "learned", "agent"]
                                    },
                                    "description": (
                                        "Memory layers agent can administer"
                                    )
                                }
                            }
                        }
                    },
                    "required": ["agent_id", "permissions"]
                }
            },
            {
                "name": "query_memory_for_agent",
                "description": (
                    "Query memory for an agent with "
                    "permission-based access control"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID performing the query"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query text"
                        },
                        "memory_layers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["global", "learned", "agent"]
                            },
                            "description": (
                                "Memory layers to search "
                                "(subject to permissions)"
                            )
                        },
                        "limit": {
                            "type": "integer",
                            "description": (
                                "Maximum number of results (default: 10)"
                            )
                        }
                    },
                    "required": ["agent_id", "query"]
                }
            },
            {
                "name": "store_agent_action",
                "description": (
                    "Store an agent action with optional "
                    "learned memory integration"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID performing the action"
                        },
                        "action": {
                            "type": "string",
                            "description": "Description of the action taken"
                        },
                        "context": {
                            "type": "object",
                            "description": (
                                "Contextual information about the action"
                            )
                        },
                        "outcome": {
                            "type": "string",
                            "description": "Result or outcome of the action"
                        },
                        "learn": {
                            "type": "boolean",
                            "description": (
                                "Store action as learned memory "
                                "(default: false)"
                            )
                        }
                    },
                    "required": ["agent_id", "action", "outcome"]
                }
            },
            {
                "name": "build_policy_from_markdown",
                "description": (
                    "Build policy from markdown files in directory "
                    "and optionally activate it"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": (
                                "Policy directory path (default: ./policy)"
                            )
                        },
                        "policy_version": {
                            "type": "string",
                            "description": (
                                "Policy version identifier (default: latest)"
                            )
                        },
                        "activate": {
                            "type": "boolean",
                            "description": (
                                "Store policy in memory for enforcement "
                                "(default: true)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_policy_rulebook",
                "description": (
                    "Get the canonical policy rulebook as JSON"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "version": {
                            "type": "string",
                            "description": (
                                "Policy version to retrieve (default: latest)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "validate_json_against_schema",
                "description": (
                    "Validate JSON structure against policy schema requirements"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schema_name": {
                            "type": "string",
                            "description": "Name of the schema to validate against"
                        },
                        "candidate_json": {
                            "type": "string",
                            "description": "JSON string to validate"
                        }
                    },
                    "required": ["schema_name", "candidate_json"]
                }
            },
            {
                "name": "log_policy_violation",
                "description": (
                    "Log a policy violation for compliance tracking"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID that violated the policy"
                        },
                        "rule_id": {
                            "type": "string",
                            "description": "Policy rule ID that was violated"
                        },
                        "context": {
                            "type": "object",
                            "description": (
                                "Additional context about the violation"
                            )
                        }
                    },
                    "required": ["agent_id", "rule_id"]
                }
            },
            {
                "name": "system_health",
                "description": (
                    "Check system health and get diagnostic information "
                    "about all components"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_memory_usage_guidance",
                "description": (
                    "Get guidance on effective memory usage patterns and best practices"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_context_preservation_guidance",
                "description": (
                    "Get guidance on preserving context across sessions"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_query_optimization_guidance",
                "description": (
                    "Get guidance on optimizing memory queries and retrieval"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_markdown_optimization_guidance",
                "description": (
                    "Get guidance on processing and storing markdown content"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_duplicate_detection_guidance",
                "description": (
                    "Get guidance on detecting and handling duplicate content"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_directory_processing_guidance",
                "description": (
                    "Get guidance on batch processing directories"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_memory_type_selection_guidance",
                "description": (
                    "Get guidance on selecting appropriate memory types"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_memory_type_suggestion_guidance",
                "description": (
                    "Get guidance for AI-powered memory type suggestions"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_policy_compliance_guidance",
                "description": (
                    "Get guidance for following policy compliance"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_policy_violation_recovery_guidance",
                "description": (
                    "Get guidance for recovering from policy violations"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            # Generic Collection Tools
            {
                "name": "create_collection",
                "description": (
                    "Create a new generic memory collection with optional "
                    "metadata and permissions"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to create"
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "Description of the collection (optional)"
                            )
                        },
                        "metadata": {
                            "type": "object",
                            "description": (
                                "Additional metadata for the collection "
                                "(optional)"
                            )
                        }
                    },
                    "required": ["collection_name"]
                }
            },
            {
                "name": "list_collections",
                "description": (
                    "List all available memory collections with their "
                    "metadata and statistics"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_stats": {
                            "type": "boolean",
                            "description": (
                                "Include collection statistics "
                                "(default true)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "add_to_collection",
                "description": (
                    "Add content to a specific memory collection with "
                    "optional metadata"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": (
                                "Name of the collection to add content to"
                            )
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to add to the collection"
                        },
                        "metadata": {
                            "type": "object",
                            "description": (
                                "Additional metadata for the content "
                                "(optional)"
                            )
                        },
                        "importance": {
                            "type": "number",
                            "description": (
                                "Importance score 0.0-1.0 "
                                "(optional, default 0.5)"
                            )
                        }
                    },
                    "required": ["collection_name", "content"]
                }
            },
            {
                "name": "query_collection",
                "description": (
                    "Search and retrieve relevant information from a "
                    "specific memory collection"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": (
                                "Name of the collection to query"
                            )
                        },
                        "query": {
                            "type": "string",
                            "description": (
                                "Search query to find relevant memories"
                            )
                        },
                        "limit": {
                            "type": "number",
                            "description": (
                                "Maximum number of results "
                                "(optional, default 10)"
                            )
                        },
                        "min_score": {
                            "type": "number",
                            "description": (
                                "Minimum similarity score 0.0-1.0 "
                                "(optional, default 0.3)"
                            )
                        },
                        "include_metadata": {
                            "type": "boolean",
                            "description": (
                                "Include metadata in results "
                                "(optional, default true)"
                            )
                        }
                    },
                    "required": ["collection_name", "query"]
                }
            },
            {
                "name": "delete_collection",
                "description": (
                    "Delete an entire memory collection and all its contents"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to delete"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": (
                                "Confirmation flag required for deletion "
                                "(must be true)"
                            )
                        }
                    },
                    "required": ["collection_name", "confirm"]
                }
            },
            {
                "name": "get_collection_stats",
                "description": (
                    "Get detailed statistics and information about a "
                    "specific memory collection"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": (
                                "Name of the collection to get stats for"
                            )
                        }
                    },
                    "required": ["collection_name"]
                }
            }
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a tool call and return the result."""
        return await self.tool_handlers.handle_tool_call(tool_name, arguments)

    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources."""
        if not self.memory_manager:
            return []
        return self.resource_handlers.list_resources()

    async def handle_resource_read(
        self, uri: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a resource read request."""
        try:
            # Read the resource with all parameters
            result = await self.resource_handlers.read_resource(uri, **params)
            
            if result.get('status') == 'error':
                return {
                    "error": {
                        "code": -32603,
                        "message": result.get('error', 'Unknown error')
                    }
                }
            
            # Format successful response - MCP requires 'contents' array
            resource_data = result.get('data', {})
            
            # Convert the data to a properly formatted JSON string
            json_text = json.dumps(resource_data, indent=2, ensure_ascii=False)
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json_text
                }]
            }
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Failed to read resource: {str(e)}"
                }
            }

    def get_available_prompts(self) -> List[Dict[str, Any]]:
        """Get list of available prompts."""
        # Return empty list in tools-only mode or if components not available
        if (self.server_mode == "tools-only" or
                not self.memory_manager or
                not self.prompt_handlers):
            return []
        return self.prompt_handlers.list_prompts()

    async def handle_prompt_get(
        self, name: str, arguments: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Handle a prompt get request."""
        # Return error in tools-only mode
        if self.server_mode == "tools-only" or not self.prompt_handlers:
            return {
                "error": {
                    "code": -32601,
                    "message": "Prompts not available in tools-only mode"
                }
            }
            
        try:
            # Get the prompt with arguments
            result = await self.prompt_handlers.get_prompt(name, arguments)
            
            if result.get('status') == 'error':
                return {
                    "error": {
                        "code": -32603,
                        "message": result.get('error', 'Unknown error')
                    }
                }
            
            # Format successful response - trying simple text display approach
            prompt_data = result.get('prompt', {})
            guidance_text = prompt_data.get('content', '')
            
            # Try formatting as pure reference content, not a request
            return {
                "description": prompt_data.get('name', name),
                "messages": [
                    {
                        "role": "assistant",
                        "content": {
                            "type": "text",
                            "text": f"Here is the {name} reference guide:\n\n{guidance_text}\n\n---\nThis is reference information only."
                        }
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting prompt {name}: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Failed to get prompt: {str(e)}"
                }
            }


def send_response(
    request_id: Optional[str],
    result: Dict[str, Any] = None,
    error: Dict[str, Any] = None
):
    """Send a response back to the MCP client."""
    response = {"jsonrpc": "2.0", "id": request_id}
    
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    print(json.dumps(response), flush=True)


def send_notification(method: str, params: Dict[str, Any] = None):
    """Send a notification to the MCP client."""
    notification = {"jsonrpc": "2.0", "method": method}
    
    if params:
        notification["params"] = params
    
    print(json.dumps(notification), flush=True)


async def run_mcp_server(server_mode="full"):
    """Main server loop for MCP protocol handling."""
    logger.info("Memory MCP Server ready, waiting for connections...")
    
    # Create server instance with specified mode
    server = MemoryMCPServer(server_mode)
    
    # Build MCP capabilities based on server mode
    capabilities = {}
    
    # Always include tools (unless prompts-only mode)
    if server_mode != "prompts-only":
        capabilities["tools"] = {"listChanged": False}
    
    # Always include resources (unless prompts-only mode)
    if server_mode != "prompts-only":
        capabilities["resources"] = {"subscribe": False, "listChanged": False}
    
    # Include prompts only in full and prompts-only modes
    if server_mode in ["full", "prompts-only"]:
        capabilities["prompts"] = {"listChanged": False}
    
    # MCP initialization response
    init_response = {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": capabilities,
        "serverInfo": MCP_SERVER_INFO
    }
    
    # Process MCP protocol messages
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                send_response(request_id, init_response)
                # Don't send notification immediately - wait for client's initialized notification
                logger.info("Memory server initialization response sent")
                
            elif method == "notifications/initialized":
                # Client has confirmed initialization is complete
                logger.info("Memory server initialized successfully")
                
            elif method == "tools/list":
                tools_response = {"tools": server.get_available_tools()}
                send_response(request_id, tools_response)
                
            elif method == "resources/list":
                resources = server.get_available_resources()
                resources_response = {"resources": resources}
                send_response(request_id, resources_response)
                
            elif method == "resources/read":
                uri = data.get("params", {}).get("uri")
                if not uri:
                    error_response = {
                        "error": {
                            "code": -32602,
                            "message": "URI parameter required"
                        }
                    }
                    send_response(request_id, error_response)
                else:
                    params = data.get("params", {})
                    # Remove uri from params to avoid duplicate
                    params_clean = {k: v for k, v in params.items() if k != 'uri'}
                    result = await server.handle_resource_read(uri, params_clean)
                    send_response(request_id, result)
                
            elif method == "prompts/list":
                prompts = server.get_available_prompts()
                prompts_response = {"prompts": prompts}
                send_response(request_id, prompts_response)
                
            elif method == "prompts/get":
                name = data.get("params", {}).get("name")
                if not name:
                    error_response = {
                        "error": {
                            "code": -32602,
                            "message": "Prompt name parameter required"
                        }
                    }
                    send_response(request_id, error_response)
                else:
                    arguments = data.get("params", {}).get("arguments", {})
                    result = await server.handle_prompt_get(name, arguments)
                    send_response(request_id, result)
                
            elif method == "tools/call":
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                result = await server.handle_tool_call(tool_name, arguments)
                send_response(request_id, result)
                
            else:
                logger.info(f"Unhandled method: {method}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {line} - {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            if 'request_id' in locals():
                send_response(
                    request_id,
                    error={"code": -32603, "message": str(e)}
                )
