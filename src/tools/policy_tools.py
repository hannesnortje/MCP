"""
Policy management tool definitions for MCP Memory Server.

This module contains tool definitions for policy enforcement,
violation tracking, and compliance management operations.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class PolicyTools:
    """Policy management and compliance tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get policy management tool definitions."""
        return [
            {
                "name": "enforce_policy",
                "description": "Enforce policy rules and check compliance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to check against policies"
                        },
                        "policy_type": {
                            "type": "string",
                            "description": "Type of policy to enforce"
                        }
                    },
                    "required": ["content"]
                }
            }
            # Additional policy tools would be extracted here
        ]
