"""
Handler modules for MCP Memory Server.

This package contains specialized handler modules that were extracted from
the original monolithic tool_handlers.py file for better maintainability
and separation of concerns.

Handler Modules:
- core_memory_handlers: Core memory operations across all memory layers
- markdown_processing_handlers: Markdown processing and optimization
- agent_management_handlers: Agent lifecycle management
- policy_and_guidance_handlers: Policy management and guidance content
- system_and_collections_handlers: System health and generic collections
"""

from .core_memory_handlers import CoreMemoryHandlers
from .markdown_processing_handlers import MarkdownProcessingHandlers
from .agent_management_handlers import AgentManagementHandlers
from .policy_and_guidance_handlers import PolicyAndGuidanceHandlers
from .system_and_collections_handlers import SystemAndCollectionsHandlers

__all__ = [
    "CoreMemoryHandlers",
    "MarkdownProcessingHandlers",
    "AgentManagementHandlers",
    "PolicyAndGuidanceHandlers",
    "SystemAndCollectionsHandlers"
]
