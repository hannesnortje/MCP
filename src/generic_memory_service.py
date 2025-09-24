"""
Generic Memory Service - Replaces rigid memory types with flexible collections

Provides a modern, flexible memory API that works with any user-defined
collections instead of being locked to global/learned/agent types.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from .collection_manager import CollectionManager, CollectionPermissions

logger = logging.getLogger(__name__)


class GenericMemoryService:
    """
    Generic memory service supporting flexible, user-defined collections.
    
    Replaces the rigid global/learned/agent memory types with dynamic
    collections that users can create and organize as needed.
    """
    
    def __init__(self):
        """Initialize generic memory service."""
        self.client: Optional[QdrantClient] = None
        self.collection_manager: Optional[CollectionManager] = None
        self.embedding_model = None
        self.initialized = False
        self.current_user = "system"  # Current user context
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the memory service and collection manager."""
        try:
            # Initialize Qdrant client (use existing memory manager)
            from .memory_manager import QdrantMemoryManager
            from .config import Config
            
            qdrant_manager = QdrantMemoryManager()
            
            self.client = qdrant_manager.client
            
            # Initialize collection manager
            config = Config()
            self.collection_manager = CollectionManager(
                qdrant_client=self.client,
                embedding_dimension=config.EMBEDDING_DIMENSION
            )
            
            # Initialize embedding model
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.initialized = True
            
            logger.info("✅ Generic memory service initialized successfully")
            return {"success": True, "message": "Memory service initialized"}
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize memory service: {e}")
            return {"success": False, "error": str(e)}
    
    def set_user_context(self, user_id: str) -> None:
        """Set the current user context for operations."""
        self.current_user = user_id
        
    # Collection Management API
    
    async def create_collection(
        self,
        name: str,
        description: str = "",
        tags: List[str] = None,
        category: str = None,
        project: str = None,
        permissions: Dict[str, List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new memory collection.
        
        Args:
            name: Collection name (e.g., "project-alpha", "meeting-notes")
            description: Human-readable description
            tags: List of tags for organization
            category: Collection category (optional)
            project: Associated project (optional)
            permissions: Dict with "read", "write", "admin" keys (optional)
            
        Returns:
            Success/error response
        """
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        # Convert permissions dict to CollectionPermissions object
        perm_obj = None
        if permissions:
            perm_obj = CollectionPermissions(
                read=permissions.get("read", ["*"]),
                write=permissions.get("write", [self.current_user]),
                admin=permissions.get("admin", [self.current_user])
            )
            
        return self.collection_manager.create_collection(
            name=name,
            description=description,
            tags=tags or [],
            category=category,
            project=project,
            permissions=perm_obj,
            created_by=self.current_user
        )
    
    async def list_collections(
        self,
        filter_by_tags: List[str] = None,
        filter_by_category: str = None,
        filter_by_project: str = None,
        include_stats: bool = True
    ) -> Dict[str, Any]:
        """List collections with optional filtering."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        return self.collection_manager.list_collections(
            filter_by_tags=filter_by_tags,
            filter_by_category=filter_by_category,
            filter_by_project=filter_by_project,
            owned_by=None  # Show all accessible collections
        )
    
    async def get_collection(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        return self.collection_manager.get_collection(name)
    
    async def update_collection(
        self,
        name: str,
        description: str = None,
        tags: List[str] = None,
        category: str = None,
        project: str = None
    ) -> Dict[str, Any]:
        """Update collection metadata."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        return self.collection_manager.update_collection(
            name=name,
            description=description,
            tags=tags,
            category=category,
            project=project,
            updated_by=self.current_user
        )
    
    async def delete_collection(
        self, name: str, confirm: bool = False
    ) -> Dict[str, Any]:
        """Delete a collection."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        return self.collection_manager.delete_collection(
            name=name,
            deleted_by=self.current_user,
            confirm=confirm
        )
    
    # Memory Content API
    
    async def add_memory(
        self,
        collection: str,
        content: str,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Add content to a specific collection.
        
        Args:
            collection: Collection name to add to
            content: Content to store
            metadata: Additional metadata (optional)
            tags: Content-specific tags (optional)
            
        Returns:
            Success/error response with memory ID
        """
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            # Check if collection exists and user has write permission
            collection_info = self.collection_manager.get_collection(collection)
            if not collection_info.get("success"):
                return {
                    "success": False,
                    "error": f"Collection '{collection}' not found"
                }
            
            # TODO: Add permission check here
            
            # Generate embedding
            embedding = self._embed_text(content)
            
            # Prepare metadata
            full_metadata = {
                "content": content,
                "collection": collection,
                "added_by": self.current_user,
                "timestamp": datetime.now().isoformat(),
                "tags": tags or [],
                **(metadata or {})
            }
            
            # Generate unique ID
            content_hash = self._generate_content_hash(content)
            
            # Create point
            point = PointStruct(
                id=content_hash,
                vector=embedding,
                payload=full_metadata
            )
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=collection,
                points=[point]
            )
            
            logger.info(f"✅ Added memory to collection '{collection}'")
            return {
                "success": True,
                "memory_id": content_hash,
                "collection": collection,
                "message": "Memory added successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_memory(
        self,
        query: str,
        collections: List[str] = None,
        limit: int = 10,
        min_score: float = 0.3,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Search for memories across one or more collections.
        
        Args:
            query: Search query text
            collections: List of collection names to search (all if None)
            limit: Maximum number of results
            min_score: Minimum similarity score
            filters: Additional filters for metadata
            
        Returns:
            Search results with scores and metadata
        """
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            # If no collections specified, search all accessible collections
            if collections is None:
                all_collections = await self.list_collections()
                if all_collections.get("success"):
                    collections = [
                        col["name"] for col in all_collections["collections"]
                    ]
                else:
                    collections = []
            
            # Generate query embedding
            query_embedding = self._embed_text(query)
            
            all_results = []
            
            # Search each collection
            for collection_name in collections:
                try:
                    # Check if collection exists
                    collection_info = self.collection_manager.get_collection(
                        collection_name
                    )
                    if not collection_info.get("success"):
                        continue
                        
                    # TODO: Add permission check here
                    
                    # Perform search
                    search_results = self.client.search(
                        collection_name=collection_name,
                        query_vector=query_embedding,
                        limit=limit,
                        score_threshold=min_score
                    )
                    
                    # Process results
                    for result in search_results:
                        all_results.append({
                            "id": result.id,
                            "score": result.score,
                            "collection": collection_name,
                            "payload": result.payload
                        })
                        
                except Exception as e:
                    logger.warning(
                        f"Failed to search collection {collection_name}: {e}"
                    )
                    continue
            
            # Sort by score and limit
            all_results.sort(key=lambda x: x["score"], reverse=True)
            all_results = all_results[:limit]
            
            return {
                "success": True,
                "results": all_results,
                "query": query,
                "collections_searched": collections,
                "total_results": len(all_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to search memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_memory(
        self, memory_id: str, collection: str
    ) -> Dict[str, Any]:
        """Get a specific memory by ID."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            result = self.client.retrieve(
                collection_name=collection,
                ids=[memory_id]
            )
            
            if result:
                memory = result[0]
                return {
                    "success": True,
                    "memory": {
                        "id": memory.id,
                        "collection": collection,
                        "payload": memory.payload
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Memory not found"
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_memory(
        self, memory_id: str, collection: str
    ) -> Dict[str, Any]:
        """Delete a specific memory."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            # TODO: Add permission check here
            
            self.client.delete(
                collection_name=collection,
                points_selector=[memory_id]
            )
            
            return {
                "success": True,
                "message": "Memory deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete memory: {e}")
            return {"success": False, "error": str(e)}
    
    # Collection Statistics & Analytics
    
    async def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get detailed statistics for a collection."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            # Get basic collection info
            collection_info = self.collection_manager.get_collection(collection)
            if not collection_info.get("success"):
                return collection_info
                
            # Get additional stats from Qdrant
            info = self.client.get_collection(collection)
            
            # Get recent activity (last 100 memories)
            recent_memories = self.client.scroll(
                collection_name=collection,
                limit=100,
                with_payload=True
            )
            
            # Analyze tags and metadata
            tag_counts = {}
            content_sizes = []
            users = set()
            
            for point in recent_memories[0]:
                payload = point.payload
                
                # Count tags
                for tag in payload.get("tags", []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                    
                # Track content size
                content = payload.get("content", "")
                content_sizes.append(len(content))
                
                # Track users
                users.add(payload.get("added_by", "unknown"))
            
            stats = {
                "success": True,
                "collection": collection,
                "basic_stats": {
                    "total_memories": info.points_count,
                    "vectors_count": info.vectors_count,
                    "status": info.status.value if info.status else "unknown"
                },
                "content_analysis": {
                    "avg_content_size": (
                        sum(content_sizes) / len(content_sizes)
                        if content_sizes else 0
                    ),
                    "total_contributors": len(users),
                    "top_tags": sorted(
                        tag_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                },
                "metadata": collection_info["collection"]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {"success": False, "error": str(e)}
    
    # Migration & Compatibility
    
    async def migrate_legacy_collections(self) -> Dict[str, Any]:
        """
        Migrate from old global/learned/agent system to new flexible system.
        
        Creates equivalent collections with proper metadata and tags.
        """
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            migrations = []
            
            # Define migration mappings
            legacy_collections = [
                {
                    "old_name": "global_memory",
                    "new_name": "shared-knowledge",
                    "description": "Shared knowledge and documentation",
                    "tags": ["global", "shared", "documentation"],
                    "category": "documentation"
                },
                {
                    "old_name": "learned_memory",
                    "new_name": "patterns-insights",
                    "description": "Learned patterns and insights",
                    "tags": ["learned", "patterns", "insights"],
                    "category": "knowledge"
                }
                # Agent collections handled separately due to dynamic names
            ]
            
            for legacy in legacy_collections:
                # Check if old collection exists
                try:
                    old_info = self.client.get_collection(legacy["old_name"])
                    if old_info.points_count > 0:
                        # Create new collection
                        result = await self.create_collection(
                            name=legacy["new_name"],
                            description=legacy["description"],
                            tags=legacy["tags"],
                            category=legacy["category"]
                        )
                        
                        if result["success"]:
                            migrations.append({
                                "from": legacy["old_name"],
                                "to": legacy["new_name"],
                                "status": "created",
                                "documents": old_info.points_count
                            })
                        
                except Exception as e:
                    logger.warning(f"Could not migrate {legacy['old_name']}: {e}")
                    
            return {
                "success": True,
                "migrations": migrations,
                "message": "Legacy collections migration completed"
            }
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods
    
    def _ensure_initialized(self) -> bool:
        """Ensure service is initialized."""
        return (
            self.initialized and
            self.client is not None and
            self.collection_manager is not None and
            self.embedding_model is not None
        )
    
    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        return self.embedding_model.encode(text).tolist()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate unique hash for content."""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]