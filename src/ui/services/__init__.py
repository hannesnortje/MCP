"""
Services Package for AutoGen UI

Provides centralized services for real-time communication,
notifications, memory operations, and other cross-widget functionality.
"""

from .session_service import SessionService
from .conversation_service import ConversationService
# Import the new generic memory service (flexible collections)
from ..generic_direct_memory_service import (
    GenericDirectMemoryService as MemoryService
)

__all__ = [
    "SessionService",
    "ConversationService",
    "MemoryService"
]
