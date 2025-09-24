"""
Direct Memory Service for UI Integration

This service provides direct access to the MCP Memory Server's
QdrantMemoryManager without any protocol overhead.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal

# Direct imports from MCP memory server
from ..memory_manager import QdrantMemoryManager
from ..qdrant_manager import ensure_qdrant_running


logger = logging.getLogger(__name__)


class DirectMemoryService(QObject):
    """
    Memory service that directly uses QdrantMemoryManager.
    
    This is much simpler and more efficient than the MCP protocol adapter.
    """

    # Signals for UI updates
    search_completed = Signal(list)
    stats_completed = Signal(dict)
    collections_completed = Signal(list)
    error_occurred = Signal(str)
    initialization_completed = Signal(bool)

    def __init__(self, server_url: str = "direct"):
        """Initialize with optional server_url for compatibility."""
        super().__init__()
        self.server_url = server_url  # For compatibility with old interface
        self.memory_manager: Optional[QdrantMemoryManager] = None
        self._initialized = False

    async def initialize(self, local_mode: bool = True) -> bool:
        """Initialize the direct memory service."""
        try:
            logger.info("Initializing Direct Memory Service...")
            
            # Ensure Qdrant is running
            if not ensure_qdrant_running():
                logger.error("Failed to start Qdrant")
                self.initialization_completed.emit(False)
                return False

            # Initialize the memory manager directly
            self.memory_manager = QdrantMemoryManager()
            
            self._initialized = True
            logger.info("✅ Direct Memory Service initialized successfully")
            self.initialization_completed.emit(True)
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Direct Memory Service: {e}")
            self.error_occurred.emit(f"Initialization failed: {e}")
            self.initialization_completed.emit(False)
            return False

    async def get_collections(self) -> List[Dict[str, Any]]:
        """Get available memory collections."""
        try:
            if not self._initialized or not self.memory_manager:
                await self.initialize()

            # Get collection info from memory manager
            collections = []
            
            # Standard memory types in MCP server
            memory_types = ["global", "learned", "agent"]
            
            for memory_type in memory_types:
                try:
                    # Check if collection exists and get stats
                    # Use the async method available in QdrantMemoryManager
                    if memory_type == "agent":
                        # For agent collections, we need an agent_id
                        # Use default agent to check if collections exist
                        stats = self.memory_manager.async_get_collection_info(
                            memory_type=memory_type,
                            agent_id="default"
                        )
                    else:
                        stats = self.memory_manager.async_get_collection_info(
                            memory_type=memory_type
                        )
                    
                    collections.append({
                        "name": memory_type,
                        "type": memory_type,
                        "status": "active",
                        "documents_count": stats.get("points_count", 0),
                        "vectors_count": stats.get("vectors_count", 0),
                        "indexed_vectors_count": stats.get(
                            "indexed_vectors_count", 0
                        )
                    })
                    
                except Exception as e:
                    logger.debug(
                        f"Collection {memory_type} not available: {e}"
                    )

            logger.info(f"Found {len(collections)} memory collections")
            self.collections_completed.emit(collections)
            return collections

        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            self.error_occurred.emit(f"Collections query failed: {e}")
            return []

    async def search_memory(
        self,
        query: str,
        collection_name: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search memory with the given query."""
        try:
            if not self._initialized or not self.memory_manager:
                await self.initialize()

            # Determine memory types to search
            memory_types = []
            if collection_name:
                memory_types = [collection_name]
            else:
                memory_types = ["global", "learned", "agent"]

            # Perform the search using memory manager directly
            search_results = []
            
            for memory_type in memory_types:
                try:
                    results = self.memory_manager.query_memory(
                        query=query,
                        memory_type=memory_type,
                        limit=limit,
                        min_score=min_score
                    )
                    
                    for result in results:
                        search_results.append({
                            "id": result.get("id", ""),
                            "content": result.get("content", ""),
                            "score": result.get("score", 0.0),
                            "metadata": result.get("metadata", {}),
                            "memory_type": memory_type,
                            "timestamp": result.get("timestamp", ""),
                            "importance": result.get("importance", 0.5)
                        })
                        
                except Exception as e:
                    logger.debug(f"Search in {memory_type} failed: {e}")

            # Sort by score descending
            search_results.sort(key=lambda x: x["score"], reverse=True)
            search_results = search_results[:limit]

            logger.info(f"Search returned {len(search_results)} results")
            self.search_completed.emit(search_results)
            return search_results

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            self.error_occurred.emit(f"Search failed: {e}")
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        try:
            if not self._initialized or not self.memory_manager:
                await self.initialize()

            # Get statistics directly from memory manager
            stats = {
                "status": "healthy",
                "total_documents": 0,
                "total_vectors": 0,
                "collections": {},
                "last_updated": datetime.now().isoformat()
            }

            # Get stats for each collection
            memory_types = ["global", "learned", "agent"]
            
            for memory_type in memory_types:
                try:
                    if memory_type == "agent":
                        collection_stats = (
                            self.memory_manager.async_get_collection_info(
                                memory_type=memory_type,
                                agent_id="default"
                            )
                        )
                    else:
                        collection_stats = (
                            self.memory_manager.async_get_collection_info(
                                memory_type=memory_type
                            )
                        )
                    
                    stats["collections"][memory_type] = {
                        "documents_count": collection_stats.get(
                            "points_count", 0
                        ),
                        "vectors_count": collection_stats.get(
                            "vectors_count", 0
                        ),
                        "indexed_vectors_count": collection_stats.get(
                            "indexed_vectors_count", 0
                        ),
                        "status": "active"
                    }
                    
                    stats["total_documents"] += collection_stats.get(
                        "points_count", 0
                    )
                    stats["total_vectors"] += collection_stats.get(
                        "vectors_count", 0
                    )
                    
                except Exception as e:
                    logger.debug(f"Stats for {memory_type} failed: {e}")
                    stats["collections"][memory_type] = {
                        "documents_count": 0,
                        "vectors_count": 0,
                        "indexed_vectors_count": 0,
                        "status": "error"
                    }

            logger.info("Successfully retrieved memory stats")
            self.stats_completed.emit(stats)
            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            self.error_occurred.emit(f"Stats query failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_documents": 0,
                "total_vectors": 0,
                "collections": {}
            }

    async def add_memory(
        self,
        content: str,
        memory_type: str = "global",
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> Dict[str, Any]:
        """Add content to memory."""
        try:
            if not self._initialized or not self.memory_manager:
                await self.initialize()

            # Add to memory using memory manager directly
            if memory_type == "global":
                category = (
                    metadata.get("category", "general") if metadata
                    else "general"
                )
                result = self.memory_manager.add_to_global_memory(
                    content=content,
                    category=category,
                    importance=importance
                )
            elif memory_type == "learned":
                pattern_type = (
                    metadata.get("pattern_type", "insight") if metadata
                    else "insight"
                )
                confidence = (
                    metadata.get("confidence", 0.7) if metadata
                    else 0.7
                )
                result = self.memory_manager.add_to_learned_memory(
                    content=content,
                    pattern_type=pattern_type,
                    confidence=confidence
                )
            elif memory_type == "agent":
                agent_id = metadata.get("agent_id") if metadata else None
                agent_memory_type = (
                    metadata.get("agent_memory_type", "general") if metadata
                    else "general"
                )
                result = self.memory_manager.add_to_agent_memory(
                    content=content,
                    agent_id=agent_id,
                    memory_type=agent_memory_type
                )
            else:
                raise ValueError(f"Unknown memory type: {memory_type}")

            logger.info(f"Successfully added content to {memory_type} memory")
            return result

        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            self.error_occurred.emit(f"Add memory failed: {e}")
            raise

    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized and self.memory_manager is not None

    async def shutdown(self) -> None:
        """Shutdown the memory service."""
        logger.info("Shutting down Direct Memory Service...")
        self._initialized = False
        self.memory_manager = None
        logger.info("✅ Direct Memory Service shutdown complete")


# Singleton instance for UI use
_direct_memory_service_instance: Optional[DirectMemoryService] = None


def get_direct_memory_service() -> DirectMemoryService:
    """Get the global direct memory service instance."""
    global _direct_memory_service_instance
    if _direct_memory_service_instance is None:
        _direct_memory_service_instance = DirectMemoryService()
    return _direct_memory_service_instance
