"""
Tool definitions for MCP Memory Server (Refactored Router).

This is now a lightweight router that aggregates specialized tool modules
while maintaining backward compatibility with the existing MCP server interface.
Refactored from monolithic 1,146-line class for better maintainability.
"""

from typing import Dict, Any, List

# Import specialized tool modules
from .tools import (
    CoreMemoryTools,
    MarkdownTools,
    BatchTools,
    AgentManagementTools,
    PolicyTools,
    SystemTools,
    GuidanceTools,
    CollectionTools
)


class MemoryToolDefinitions:
    """
    Lightweight router that aggregates specialized tool definition modules.
    
    Maintains backward compatibility with existing MCP server interface
    while using modular architecture for better maintainability.
    """

    @staticmethod
    def get_core_memory_tools() -> List[Dict[str, Any]]:
        """Core memory management tools (legacy compatibility)."""
        return CoreMemoryTools.get_tools()

    @staticmethod
    def get_markdown_processing_tools() -> List[Dict[str, Any]]:
        """Markdown content processing and analysis tools."""
        return MarkdownTools.get_tools()

    @staticmethod
    def get_batch_processing_tools() -> List[Dict[str, Any]]:
        """Batch processing and pipeline tools."""
        return BatchTools.get_tools()

    @staticmethod
    def get_agent_management_tools() -> List[Dict[str, Any]]:
        """Agent lifecycle and permission management tools."""
        return AgentManagementTools.get_tools()

    @staticmethod
    def get_policy_management_tools() -> List[Dict[str, Any]]:
        """Policy management and compliance tools."""
        return PolicyTools.get_tools()

    @staticmethod
    def get_system_tools() -> List[Dict[str, Any]]:
        """System management and administrative tools."""
        return SystemTools.get_tools()

    @staticmethod
    def get_guidance_tools() -> List[Dict[str, Any]]:
        """Guidance and help tools."""
        return GuidanceTools.get_tools()

    @staticmethod
    def get_generic_collection_tools() -> List[Dict[str, Any]]:
        """Generic collection management tools."""
        return CollectionTools.get_tools()

    @staticmethod
    def get_all_tools() -> List[Dict[str, Any]]:
        """Get all tool definitions combined."""
        tools = []
        tools.extend(MemoryToolDefinitions.get_core_memory_tools())
        tools.extend(MemoryToolDefinitions.get_markdown_processing_tools())
        tools.extend(MemoryToolDefinitions.get_batch_processing_tools())
        tools.extend(MemoryToolDefinitions.get_agent_management_tools())
        tools.extend(MemoryToolDefinitions.get_policy_management_tools())
        tools.extend(MemoryToolDefinitions.get_system_tools())
        tools.extend(MemoryToolDefinitions.get_guidance_tools())
        tools.extend(MemoryToolDefinitions.get_generic_collection_tools())
        return tools