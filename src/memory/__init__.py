"""
Memory management modules for the MCP Memory Server.

This package contains specialized modules that handle different aspects
of memory management, extracted from the monolithic memory_manager.py
for better maintainability and separation of concerns.
"""

try:
    from .vector_operations import VectorOperations
    from .agent_registry import AgentRegistry
    from .file_metadata_manager import FileMetadataManager
    from .embedding_service import EmbeddingService
    from .collection_manager import CollectionManager

    __all__ = [
        'VectorOperations',
        'AgentRegistry',
        'FileMetadataManager',
        'EmbeddingService',
        'CollectionManager'
    ]
except ImportError as e:
    # Handle import errors gracefully during development
    import logging
    logging.warning(f"Memory module import error: {e}")
    __all__ = []