"""
Generic collection tool definitions for MCP Memory Server.

This module contains tool definitions for generic collection operations,
custom memory types, and extensibility features.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class CollectionTools:
    """Generic collection management tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get collection management tool definitions."""
        return [
            {
                "name": "create_collection",
                "description": "Create a new memory collection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to create"
                        },
                        "memory_type": {
                            "type": "string",
                            "description": "Type of memory collection"
                        }
                    },
                    "required": ["collection_name"]
                }
            }
            # Additional collection tools would be extracted here
        ]
