"""
MCP Memory Server UI - Memory Adapter
Adapter for direct communication between UI and MCP Memory Manager.
"""

import logging
import asyncio
import traceback
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from src.memory_manager import QdrantMemoryManager
from src.config import Config


logger = logging.getLogger(__name__)


class MemoryAdapter:
    """Adapter for direct access to the MCP Memory Manager.
    
    This class provides methods that match what the UI expects
    but uses the MCP memory manager directly instead of HTTP calls.
    """
    
    def __init__(self, server_connection: Optional[Dict[str, Any]] = None):
        """Initialize the memory adapter.
        
        Args:
            server_connection: Optional server connection information.
            If provided, will attempt to connect to an existing memory manager.
            If None, will create a new memory manager instance.
        """
        self.server_connection = server_connection
        self.memory_manager: Optional[QdrantMemoryManager] = None
        self._initialized = False
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # Collection name mapping
        self.collection_mapping = {
            "global_memory": "global",
            "learned_memory": "learned",
            "agent_memory": "agent"
        }
        
        # Reverse mapping for UI display
        self.reverse_mapping = {
            v: k for k, v in self.collection_mapping.items()
        }
        
        # Log server connection mode
        if server_connection:
            conn_type = server_connection.get('type', 'unknown')
            server_mode = server_connection.get('server_mode', 'unknown')
            logger.info(
                f"Memory adapter initialized for {conn_type} "
                f"connection to server mode: {server_mode}"
            )
    
    async def initialize(self) -> bool:
        """Initialize the connection to the memory manager.
        
        Returns:
            bool: True if initialization was successful.
        """
        try:
            # Use an executor to run the potentially blocking initialization
            # in a separate thread to avoid blocking the UI
            is_direct = (self.server_connection and
                         self.server_connection.get('type') == 'direct')
            
            if is_direct:
                # Connect to existing memory manager in direct mode
                logger.info("Connecting to existing memory manager...")
                
                # Get the parent process ID
                server_pid = self.server_connection.get('pid')
                if not server_pid:
                    logger.warning("No server PID provided in connection info")
                
                # In direct mode, we create a new memory manager instance
                # that connects to the same Qdrant instance as the server
                loop = asyncio.get_event_loop()
                self.memory_manager = await loop.run_in_executor(
                    self._executor, QdrantMemoryManager
                )
            else:
                # Create a new memory manager
                logger.info("Creating new memory manager instance...")
                loop = asyncio.get_event_loop()
                self.memory_manager = await loop.run_in_executor(
                    self._executor, QdrantMemoryManager
                )
            
            # Check if initialization was successful
            if (self.memory_manager and
                    self.memory_manager.collections_initialized):
                self._initialized = True
                logger.info("Memory adapter initialized successfully")
                return True
            else:
                logger.error("Memory manager initialization failed")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize memory adapter: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _map_collection_name(self, collection: str) -> List[str]:
        """Map UI collection name to memory manager collection type.
        
        Args:
            collection: The collection name from the UI.
            
        Returns:
            List of memory types to search.
        """
        if collection in self.collection_mapping:
            return [self.collection_mapping[collection]]
        # Default to all collections if not found
        return ["global", "learned", "agent"]
    
    def _format_search_results(
        self, search_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format search results to match what the UI expects.
        
        Args:
            search_results: Results from memory_manager.query_memory.
            
        Returns:
            List of formatted search results.
        """
        formatted_results = []
        
        if not search_results.get("success", False):
            return []
        
        for memory in search_results.get("memories", []):
            memory_type = memory.get("memory_type", "unknown")
            # Map memory type back to UI collection name
            collection = self.reverse_mapping.get(memory_type, memory_type)
            
            formatted_result = {
                "score": memory.get("score", 0.0),
                "payload": {
                    "content": memory.get("text", ""),
                    "memory_type": memory_type,
                    "collection": collection,
                    "timestamp": memory.get("timestamp", str(datetime.now())),
                    "metadata": memory.get("metadata", {})
                },
                "id": memory.get("id", "unknown")
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    async def search_memory(
        self, query: str, collection: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memory with the given query.
        
        Args:
            query: The search query.
            collection: The collection to search.
            limit: Maximum number of results to return.
            
        Returns:
            List of search results.
        """
        if not self._initialized or not self.memory_manager:
            logger.warning("Memory adapter not initialized")
            return []
        
        try:
            # Map collection name to memory types
            memory_types = self._map_collection_name(collection)
            
            # Run the query in a separate thread to avoid blocking the UI
            def query_function():
                return self.memory_manager.query_memory(
                    query=query,
                    memory_types=memory_types,
                    limit=limit,
                    min_score=0.3  # Default min score
                )
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor, query_function
            )
            
            # Format results to match what the UI expects
            formatted_results = self._format_search_results(results)
            
            logger.info(f"Search found {len(formatted_results)} results")
            return formatted_results
        except Exception as e:
            logger.error(f"Error during memory search: {e}")
            logger.error(traceback.format_exc())
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Dict containing memory statistics.
        """
        if not self._initialized or not self.memory_manager:
            logger.warning("Memory adapter not initialized")
            return self._get_error_stats()
        
        try:
            # Get health info from memory manager
            if hasattr(self.memory_manager, "get_health_info"):
                def health_function():
                    return self.memory_manager.get_health_info()
                
                loop = asyncio.get_event_loop()
                health_info = await loop.run_in_executor(
                    self._executor, health_function
                )
                return self._format_health_info(health_info)
            
            # Fallback to manual collection stats if health_info
            # method not available
            stats: Dict[str, Any] = {}
            
            # Get collection statistics from Qdrant client
            if self.memory_manager.client:
                def get_collections():
                    return self.memory_manager.client.get_collections()
                
                loop = asyncio.get_event_loop()
                collections = await loop.run_in_executor(
                    self._executor, get_collections
                )
                
                total_points = 0
                collections_ready = 0
                
                for col in collections.collections:
                    # Get collection info
                    collection_name = col.name
                    
                    def get_collection():
                        return self.memory_manager.client.get_collection(
                            collection_name
                        )
                    
                    loop = asyncio.get_event_loop()
                    collection_info = await loop.run_in_executor(
                        self._executor, get_collection
                    )
                    
                    # Extract points count
                    points_count = collection_info.vectors_count
                    total_points += points_count
                    
                    # Check if collection is ready
                    if collection_info.status == "green":
                        collections_ready += 1
                    
                    # Add collection-specific stats
                    ui_name = self.reverse_mapping.get(col.name, col.name)
                    stats[ui_name] = {
                        "documents_count": points_count,
                        "points_count": points_count,
                        "vectors_count": points_count,
                        "indexed_vectors_count": points_count,
                        "status": collection_info.status
                    }
                
                # Add overall stats in the format expected by the UI
                return {
                    "status": ("healthy" if collections_ready ==
                               len(collections.collections) else "degraded"),
                    "total_collections": len(collections.collections),
                    "collections_ready": collections_ready,
                    "total_documents": total_points,
                    "message": (f"{collections_ready}/"
                                f"{len(collections.collections)} "
                                f"collections ready"),
                    **stats
                }
            
            return self._get_error_stats()
        except Exception as e:
            logger.error(f"Error getting memory statistics: {e}")
            logger.error(traceback.format_exc())
            return self._get_error_stats()
    
    def _get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics when normal stats retrieval fails.
        
        Returns:
            Dict containing error statistics.
        """
        return {
            "status": "error",
            "total_collections": 0,
            "collections_ready": 0,
            "total_documents": 0,
            "message": "Failed to retrieve memory statistics"
        }
    
    def _format_health_info(
        self, health_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format health info to match what the UI expects.
        
        Args:
            health_info: Raw health info from memory manager.
            
        Returns:
            Formatted health info.
        """
        # Extract status from components
        components = health_info.get("components", {})
        
        # Map status to UI format
        status_mapping = {
            "healthy": "healthy",
            "unhealthy": "error",
            "unavailable": "error"
        }
        
        # Get collection counts from Qdrant component
        total_collections = 0
        qdrant_comp = components.get("qdrant", {})
        if "collections_count" in qdrant_comp:
            total_collections = qdrant_comp["collections_count"]
        
        # Format collections list for UI
        collections_list = []
        if "qdrant" in components and "collections" in components["qdrant"]:
            collections_list = components["qdrant"]["collections"]
        
        # Count documents if available
        total_documents = 0
        # Future implementation: extract document count
        
        return {
            "status": status_mapping.get(
                health_info.get("overall_status", "unknown"), "unknown"),
            "total_collections": total_collections,
            "collections_ready": total_collections,  # Assuming all ready
            "total_documents": total_documents,
            "message": health_info.get("health_check_error", ""),
            "collections": collections_list
        }
    
    async def get_collections(self) -> List[str]:
        """Get available collections.
        
        Returns:
            List of collection names.
        """
        if not self._initialized or not self.memory_manager:
            logger.warning("Memory adapter not initialized")
            return list(self.reverse_mapping.values())
        
        try:
            # Check if client is available
            if not self.memory_manager.client:
                logger.warning("Qdrant client not available")
                return list(self.reverse_mapping.values())
            
            # Get collections from Qdrant client
            def get_collections():
                return self.memory_manager.client.get_collections()
            
            loop = asyncio.get_event_loop()
            collections_result = await loop.run_in_executor(
                self._executor, get_collections
            )
            
            # Map collection names to UI format
            ui_collections = []
            for col in collections_result.collections:
                # Try to map to a known UI collection name
                ui_name = self.reverse_mapping.get(col.name, col.name)
                ui_collections.append(ui_name)
            
            # If no collections found, return default collections
            if not ui_collections:
                return list(self.reverse_mapping.values())
            
            return ui_collections
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            logger.error(traceback.format_exc())
            return list(self.reverse_mapping.values())
    
    async def delete_memory_point(
        self, collection: str, point_id: str
    ) -> bool:
        """Delete a memory point from a collection.
        
        Args:
            collection: The collection name.
            point_id: The ID of the point to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        if not self._initialized or not self.memory_manager:
            logger.warning("Memory adapter not initialized")
            return False
        
        try:
            # Map collection name to memory type
            memory_types = self._map_collection_name(collection)
            if not memory_types:
                logger.warning(f"Unknown collection: {collection}")
                return False
            
            memory_type = memory_types[0]
            
            # Convert collection name to actual collection name in Qdrant
            if memory_type == "global":
                collection_name = Config.GLOBAL_MEMORY_COLLECTION
            elif memory_type == "learned":
                collection_name = Config.LEARNED_MEMORY_COLLECTION
            elif memory_type == "agent":
                # This is simplified, would need agent ID for actual
                # implementation
                collection_name = Config.get_collection_name(
                    "agent", "default")
            else:
                logger.warning(f"Unknown memory type: {memory_type}")
                return False
            
            # Delete point from collection
            def delete_function():
                return self.memory_manager.client.delete(
                    collection_name=collection_name,
                    points_selector=[point_id]
                )
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor, delete_function
            )
            
            logger.info(f"Deleted point {point_id} from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory point: {e}")
            logger.error(traceback.format_exc())
            return False
            
    async def delete_collection(self, collection: str) -> bool:
        """Delete an entire collection.
        
        Args:
            collection: The UI collection name to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        if not self._initialized or not self.memory_manager:
            logger.warning("Memory adapter not initialized")
            return False
        
        try:
            # Map collection name to memory type
            memory_types = self._map_collection_name(collection)
            if not memory_types:
                logger.warning(f"Unknown collection: {collection}")
                return False
            
            memory_type = memory_types[0]
            
            # Convert collection name to actual collection name in Qdrant
            if memory_type == "global":
                collection_name = Config.GLOBAL_MEMORY_COLLECTION
            elif memory_type == "learned":
                collection_name = Config.LEARNED_MEMORY_COLLECTION
            elif memory_type == "agent":
                # This is simplified, would need agent ID for actual impl
                collection_name = Config.get_collection_name(
                    "agent", "default")
            else:
                logger.warning(f"Unknown memory type: {memory_type}")
                return False
            
            # Delete collection from Qdrant
            def delete_function():
                return self.memory_manager.client.delete_collection(
                    collection_name=collection_name
                )
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor, delete_function
            )
            
            logger.info(f"Deleted collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def upload_document(
        self, collection: str, content: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Upload document content to memory.
        
        Args:
            collection: The UI collection name to upload to.
            content: The document content to upload.
            metadata: Optional metadata for the document.
            
        Returns:
            bool: True if upload was successful.
        """
        if not self._initialized or not self.memory_manager:
            logger.warning("Memory adapter not initialized")
            return False
        
        try:
            # Map collection name to memory type
            memory_types = self._map_collection_name(collection)
            if not memory_types:
                logger.warning(f"Unknown collection: {collection}")
                return False
            
            memory_type = memory_types[0]
            
            # Add document to memory
            memory_id = f"upload_{uuid.uuid4()}"
            
            def add_function():
                return self.memory_manager.add_memory(
                    memory_id=memory_id,
                    text=content,
                    memory_type=memory_type,
                    metadata=metadata or {},
                    timestamp=datetime.now().isoformat()
                )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor, add_function
            )
            
            success = result.get("success", False)
            if success:
                logger.info(f"Uploaded document to {memory_type} memory")
                return True
            else:
                logger.warning(
                    f"Failed to upload document: "
                    f"{result.get('error', 'Unknown error')}"
                )
                return False
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            logger.error(traceback.format_exc())
            return False
