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
        """Get guidance and help tool definitions."""
        return [
            {
                "name": "get_memory_usage_guidance",
                "description": (
                    "Get guidance on effective memory usage patterns "
                    "and best practices"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_context_preservation_guidance",
                "description": (
                    "Get guidance on preserving context across sessions"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_query_optimization_guidance",
                "description": (
                    "Get guidance on optimizing memory queries and retrieval"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_markdown_optimization_guidance",
                "description": (
                    "Get guidance on processing and storing markdown content"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_duplicate_detection_guidance",
                "description": (
                    "Get guidance on detecting and handling duplicate content"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_directory_processing_guidance",
                "description": (
                    "Get guidance on batch processing directories"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_memory_type_selection_guidance",
                "description": (
                    "Get guidance on selecting appropriate memory types"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_memory_type_suggestion_guidance",
                "description": (
                    "Get guidance for AI-powered memory type suggestions"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_policy_compliance_guidance",
                "description": (
                    "Get guidance for following policy compliance"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_policy_violation_recovery_guidance",
                "description": (
                    "Get guidance for recovering from policy violations"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        ]