"""
Core memory management tool definitions for MCP Memory Server.

This module contains tool definitions for basic memory operations including
adding content to different memory types and querying stored information.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class CoreMemoryTools:
    """Core memory management tools (legacy compatibility)."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get core memory management tool definitions."""
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