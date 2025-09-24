"""
Agent management tool definitions for MCP Memory Server.

This module contains tool definitions for agent lifecycle management,
permissions, and configuration operations.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class AgentManagementTools:
    """Agent lifecycle and permission management tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get agent management tool definitions."""
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
                                "Whether to load policies during "
                                "initialization (default: true)"
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