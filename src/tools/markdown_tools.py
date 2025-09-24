"""
Markdown processing tool definitions for MCP Memory Server.

This module contains tool definitions for markdown file scanning, content
analysis, and processing workflows with AI enhancement capabilities.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class MarkdownTools:
    """Markdown content processing and analysis tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get markdown processing tool definitions."""
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