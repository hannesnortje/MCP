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
