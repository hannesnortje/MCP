"""
System management tool definitions for MCP Memory Server.

This module contains tool definitions for system operations,
status checking, and administrative functions.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class SystemTools:
    """System management and administrative tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get system management tool definitions."""
        return [
            {
                "name": "get_system_status",
                "description": "Get current system status and health",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            # Additional system tools would be extracted here
        ]
