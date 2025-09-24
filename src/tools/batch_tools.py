"""
Batch processing tool definitions for MCP Memory Server.

This module contains tool definitions for file processing pipelines,
batch operations, and directory-level processing workflows.
Extracted from monolithic tool_definitions.py for better maintainability.
"""

from typing import Dict, Any, List


class BatchTools:
    """Batch processing and pipeline tools."""

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get batch processing tool definitions."""
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