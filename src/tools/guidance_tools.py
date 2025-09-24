"""
Guidance and help tool definitions for MCP Memory Server.

This module contains tool definitions for user guidance,
help documentation, and usage instructions.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class GuidanceTools:
    """Guidance and help tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get guidance tool definitions."""
        return [
            {
                "name": "get_help",
                "description": "Get help and usage guidance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Help topic to get guidance on"
                        }
                    },
                    "required": []
                }
            }
            # Additional guidance tools would be extracted here
        ]
