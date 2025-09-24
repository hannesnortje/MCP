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
                    "configuration, and policy loading"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Unique identifier for the agent"
                        },
                        "agent_role": {
                            "type": "string",
                            "description": "Role of the agent (default: general)"
                        },
                        "memory_layers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["global", "learned", "agent"]
                            },
                            "description": "Memory layers agent can access"
                        }
                    },
                    "required": ["agent_id"]
                }
            }
            # Additional agent management tools would be extracted here
        ]