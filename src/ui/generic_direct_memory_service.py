"""
Generic Direct Memory Service for UI Integration

Updated service that uses the new GenericMemoryService for flexible collections
instead of rigid global/learned/agent memory types.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal

# Import new generic memory service
from ..generic_memory_service import GenericMemoryService

logger = logging.getLogger(__name__)


class GenericDirectMemoryService(QObject):
    """
    Memory service that directly uses GenericMemoryService for flexible
    collections.
    
    Replaces the rigid global/learned/agent system with user-defined
    collections.
    """

    # Signals for UI updates
    search_completed = Signal(list)
    stats_completed = Signal(dict)
    collections_completed = Signal(list)
    error_occurred = Signal(str)
    initialization_completed = Signal(bool)
    collection_created = Signal(dict)
    collection_updated = Signal(dict)
    collection_deleted = Signal(str)

    def __init__(self, server_url: str = "generic"):
        """Initialize with optional server_url for compatibility."""
        super().__init__()
        self.server_url = server_url  # For compatibility
        self.memory_service: Optional[GenericMemoryService] = None
        self._initialized = False
        self.current_user = "ui-user"  # Default user context

    async def initialize(self, local_mode: bool = True) -> bool:
        """Initialize the generic memory service."""
        try:
            logger.info("Initializing Generic Direct Memory Service...")
            
            # Initialize generic memory service
            self.memory_service = GenericMemoryService()
            result = await self.memory_service.initialize()
            
            if not result.get("success"):
                logger.error(f"Failed to initialize: {result.get('error')}")
                self.initialization_completed.emit(False)
                return False
            
            # Set user context
            self.memory_service.set_user_context(self.current_user)
            
            self._initialized = True
            logger.info(
                "✅ Generic Direct Memory Service initialized successfully"
            )
            self.initialization_completed.emit(True)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize generic memory service: {e}")
            self.initialization_completed.emit(False)
            return False

    def set_user_context(self, user_id: str) -> None:
        """Set current user context."""
        self.current_user = user_id
        if self.memory_service:
            self.memory_service.set_user_context(user_id)

    # Collection Management API (NEW)
    
    async def create_collection(
        self,
        name: str,
        description: str = "",
        tags: List[str] = None,
        category: str = None,
        project: str = None,
        permissions: Dict[str, List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new memory collection."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            result = await self.memory_service.create_collection(
                name=name,
                description=description,
                tags=tags,
                category=category,
                project=project,
                permissions=permissions
            )
            
            if result.get("success"):
                self.collection_created.emit(result)
                logger.info(f"✅ Created collection: {name}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create collection: {e}")
            return {"success": False, "error": str(e)}

    async def get_collections(self) -> List[Dict[str, Any]]:
        """Get available memory collections."""
        if not self._ensure_initialized():
            return []
            
        try:
            result = await self.memory_service.list_collections()
            
            if result.get("success"):
                collections = result.get("collections", [])
                logger.info(f"Found {len(collections)} memory collections")
                
                # Convert to format expected by UI
                formatted_collections = []
                for col in collections:
                    formatted_collections.append({
                        "name": col["name"],
                        "type": col.get("metadata", {}).get(
                            "category", "custom"
                        ),
                        "description": col.get("description", ""),
                        "tags": col.get("tags", []),
                        "documents": col.get("stats", {}).get(
                            "document_count", 0
                        ),
                        "vectors": col.get("stats", {}).get(
                            "vectors_count", 0
                        ),
                        "status": "active",
                        "metadata": col.get("metadata", {})
                    })
                
                return formatted_collections
            else:
                logger.error(f"Failed to get collections: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get collections: {e}")
            return []

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
            
        try:
            result = await self.memory_service.update_collection(
                name=name,
                description=description,
                tags=tags,
                category=category,
                project=project
            )
            
            if result.get("success"):
                self.collection_updated.emit(result)
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to update collection: {e}")
            return {"success": False, "error": str(e)}

    async def delete_collection(
        self, name: str, confirm: bool = False
    ) -> Dict[str, Any]:
        """Delete a collection."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            result = await self.memory_service.delete_collection(
                name=name, confirm=confirm
            )
            
            if result.get("success"):
                self.collection_deleted.emit(name)
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to delete collection: {e}")
            return {"success": False, "error": str(e)}

    # Memory Content API

    async def add_memory(
        self,
        collection: str,
        content: str,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Add content to a collection."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            result = await self.memory_service.add_memory(
                collection=collection,
                content=content,
                metadata=metadata,
                tags=tags
            )
            
            if result.get("success"):
                logger.info(
                    f"✅ Added memory to collection '{collection}'"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to add memory: {e}")
            return {"success": False, "error": str(e)}

    async def search_memory(
        self,
        query: str,
        collections: List[str] = None,
        limit: int = 10,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for memories across collections."""
        if not self._ensure_initialized():
            return []
            
        try:
            result = await self.memory_service.search_memory(
                query=query,
                collections=collections,
                limit=limit,
                min_score=min_score
            )
            
            if result.get("success"):
                results = result.get("results", [])
                logger.info(f"Search returned {len(results)} results")
                return results
            else:
                logger.error(f"Search failed: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to search memory: {e}")
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics across all collections."""
        if not self._ensure_initialized():
            return {"error": "Service not initialized"}
            
        try:
            # Get all collections
            collections = await self.get_collections()
            
            # Calculate aggregate stats
            total_documents = 0
            total_vectors = 0
            collection_count = len(collections)
            
            collection_stats = {}
            
            for col in collections:
                col_name = col["name"]
                docs = col.get("documents", 0) or 0
                vecs = col.get("vectors", 0) or 0
                
                total_documents += docs
                total_vectors += vecs
                
                collection_stats[col_name] = {
                    "documents": docs,
                    "vectors": vecs,
                    "category": col.get("metadata", {}).get("category", "custom"),
                    "tags": col.get("tags", [])
                }
            
            stats = {
                "status": "healthy" if self._initialized else "error",
                "total_documents": total_documents,
                "total_vectors": total_vectors,
                "total_collections": collection_count,
                "collections_ready": collection_count,
                "collections": collection_stats,
                "message": f"Managing {collection_count} collections",
                "last_updated": datetime.now().isoformat()
            }
            
            logger.info("Successfully retrieved memory stats")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_documents": 0,
                "total_collections": 0
            }

    # Migration Support

    async def migrate_legacy_collections(self) -> Dict[str, Any]:
        """Migrate from old global/learned/agent system."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            result = await self.memory_service.migrate_legacy_collections()
            return result
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {"success": False, "error": str(e)}

    # Collection Templates & Suggestions (NEW)
    
    def get_collection_templates(self) -> List[Dict[str, Any]]:
        """Get predefined collection templates for quick setup."""
        return [
            {
                "name": "project-notes",
                "description": "Project development notes and documentation",
                "tags": ["project", "development", "notes"],
                "category": "project",
                "icon": "📋"
            },
            {
                "name": "meeting-notes",
                "description": "Meeting notes and action items",
                "tags": ["meetings", "notes", "collaboration"],
                "category": "documentation",
                "icon": "🤝"
            },
            {
                "name": "code-snippets",
                "description": "Useful code snippets and examples",
                "tags": ["code", "snippets", "examples"],
                "category": "code",
                "icon": "💻"
            },
            {
                "name": "research",
                "description": "Research findings and references",
                "tags": ["research", "findings", "references"],
                "category": "knowledge",
                "icon": "🔬"
            },
            {
                "name": "troubleshooting",
                "description": "Issue reports and solutions",
                "tags": ["issues", "solutions", "debugging"],
                "category": "support",
                "icon": "🔧"
            },
            {
                "name": "learning-notes",
                "description": "Personal learning notes and insights",
                "tags": ["learning", "insights", "personal"],
                "category": "knowledge",
                "icon": "📚"
            }
        ]

    def suggest_collection_for_content(self, content: str) -> str:
        """Suggest appropriate collection based on content analysis."""
        content_lower = content.lower()
        
        # Simple keyword-based suggestions
        if any(word in content_lower for word in ["bug", "issue", "error", "fix"]):
            return "troubleshooting"
        elif any(word in content_lower for word in ["meeting", "discussed", "agenda"]):
            return "meeting-notes"
        elif any(word in content_lower for word in ["def ", "function", "class", "import"]):
            return "code-snippets"
        elif any(word in content_lower for word in ["research", "study", "analysis"]):
            return "research"
        elif any(word in content_lower for word in ["learn", "understand", "insight"]):
            return "learning-notes"
        else:
            return "project-notes"  # Default suggestion

    async def delete_memory(
        self, memory_id: str, collection: str
    ) -> Dict[str, Any]:
        """Delete a specific memory document."""
        if not self._ensure_initialized():
            return {"success": False, "error": "Service not initialized"}
            
        try:
            result = await self.memory_service.delete_memory(
                memory_id=memory_id, collection=collection
            )
            
            if result.get("success"):
                logger.info(f"✅ Deleted memory {memory_id} from {collection}")
            else:
                logger.error(f"❌ Failed to delete memory: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to delete memory: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods
    
    def _ensure_initialized(self) -> bool:
        """Ensure service is initialized."""
        return self._initialized and self.memory_service is not None

    # Legacy compatibility methods (for existing UI)
    
    async def get_collection_info(
        self, collection_name: str
    ) -> Dict[str, Any]:
        """Get info about specific collection (legacy compatibility)."""
        if not self._ensure_initialized():
            return {"error": "Service not initialized"}
            
        try:
            result = await self.memory_service.get_collection(collection_name)
            if result.get("success"):
                col = result["collection"]
                return {
                    "name": col["name"],
                    "documents_count": col.get("stats", {}).get("document_count", 0),
                    "vectors_count": col.get("stats", {}).get("vectors_count", 0),
                    "status": "active"
                }
            else:
                return {"error": result.get("error", "Collection not found")}
                
        except Exception as e:
            logger.error(f"❌ Failed to get collection info: {e}")
            return {"error": str(e)}