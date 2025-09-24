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
        # Note: This is a placeholder - the actual tools would be extracted
        # from the original file. For brevity, showing structure only.
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
                            "description": "Path to markdown file to process"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["global", "learned", "agent"],
                            "description": "Target memory type"
                        }
                    },
                    "required": ["path"]
                }
            }
            # Additional batch tools would be extracted here
        ]