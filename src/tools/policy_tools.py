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
                "name": "build_policy_from_markdown",
                "description": (
                    "Build policy from markdown files in directory "
                    "and optionally activate it"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": (
                                "Policy directory path (default: ./policy)"
                            )
                        },
                        "policy_version": {
                            "type": "string",
                            "description": (
                                "Policy version identifier (default: latest)"
                            )
                        },
                        "activate": {
                            "type": "boolean",
                            "description": (
                                "Store policy in memory for enforcement "
                                "(default: true)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_policy_rulebook",
                "description": (
                    "Get the canonical policy rulebook as JSON"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "version": {
                            "type": "string",
                            "description": (
                                "Policy version to retrieve (default: latest)"
                            )
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "validate_json_against_schema",
                "description": (
                    "Validate JSON structure against "
                    "policy schema requirements"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schema_name": {
                            "type": "string",
                            "description": (
                                "Name of the schema to validate against"
                            )
                        },
                        "candidate_json": {
                            "type": "string",
                            "description": "JSON string to validate"
                        }
                    },
                    "required": ["schema_name", "candidate_json"]
                }
            },
            {
                "name": "log_policy_violation",
                "description": (
                    "Log a policy violation for compliance tracking"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent ID that violated the policy"
                        },
                        "rule_id": {
                            "type": "string",
                            "description": "Policy rule ID that was violated"
                        },
                        "context": {
                            "type": "object",
                            "description": (
                                "Additional context about the violation"
                            )
                        }
                    },
                    "required": ["agent_id", "rule_id"]
                }
            }
        ]
