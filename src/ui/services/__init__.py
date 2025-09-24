"""
Services Package for AutoGen UI

Provides centralized services for real-time communication,
notifications, memory operations, and other cross-widget functionality.
"""

from .session_service import SessionService
# TODO: Implement MCP-compatible memory service
# from .memory_service import MemoryService
from .conversation_service import ConversationService

__all__ = [
    "SessionService",
    "ConversationService"
]  # "MemoryService" removed temporarily
