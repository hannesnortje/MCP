"""
Tool definitions for MCP Memory Server.
Contains all tool schemas organized by category for better maintainability.
"""

from typing import Dict, Any, List


class MemoryToolDefinitions:
    """Centralized tool definitions for the MCP Memory Server."""

    @staticmethod
    def get_core_memory_tools() -> List[Dict[str, Any]]:
        """Core memory management tools (legacy compatibility)."""
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
            }
        ]

    @staticmethod
    def get_markdown_processing_tools() -> List[Dict[str, Any]]:
        """Markdown content processing and analysis tools."""
        return [
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
            }
        ]

    @staticmethod
    def get_batch_processing_tools() -> List[Dict[str, Any]]:
        """Batch processing and pipeline tools."""
        return [
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
            }
        ]

    @staticmethod
    def get_agent_management_tools() -> List[Dict[str, Any]]:
        """Agent lifecycle and permission management tools."""
        return [
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
            }
        ]

    @staticmethod
    def get_policy_management_tools() -> List[Dict[str, Any]]:
        """Policy enforcement and compliance tools."""
        return [
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
            }
        ]

    @staticmethod
    def get_system_tools() -> List[Dict[str, Any]]:
        """System monitoring and diagnostics tools."""
        return [
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
            }
        ]

    @staticmethod
    def get_guidance_tools() -> List[Dict[str, Any]]:
        """Help and guidance tools for best practices."""
        return [
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
            }
        ]

    @staticmethod
    def get_generic_collection_tools() -> List[Dict[str, Any]]:
        """Generic collection management tools (new flexible system)."""
        return [
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

    @staticmethod
    def get_all_tools() -> List[Dict[str, Any]]:
        """Get all tool definitions combined."""
        tools = []
        tools.extend(MemoryToolDefinitions.get_core_memory_tools())
        tools.extend(MemoryToolDefinitions.get_markdown_processing_tools())
        tools.extend(MemoryToolDefinitions.get_batch_processing_tools())
        tools.extend(MemoryToolDefinitions.get_agent_management_tools())
        tools.extend(MemoryToolDefinitions.get_policy_management_tools())
        tools.extend(MemoryToolDefinitions.get_system_tools())
        tools.extend(MemoryToolDefinitions.get_guidance_tools())
        tools.extend(MemoryToolDefinitions.get_generic_collection_tools())
        return tools