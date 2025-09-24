"""
Services Package for AutoGen UI

Provides centralized services for real-time communication,
notifications, memory operations, and other cross-widget functionality.
"""

from .session_service import SessionService
from .conversation_service import ConversationService
# Import the direct memory service (much simpler than MCP protocol)
from ..direct_memory_service import DirectMemoryService as MemoryService

__all__ = [
    "SessionService",
    "ConversationService",
    "MemoryService"
]
