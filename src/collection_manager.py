"""
Generic Collection Manager for MCP Memory Server

Replaces the rigid global/learned/agent memory types with a flexible,
user-defined collection system.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)

logger = logging.getLogger(__name__)


@dataclass
class CollectionPermissions:
    """Permission settings for a collection"""
    read: List[str]   # Users/agents who can read
    write: List[str]  # Users/agents who can write
    admin: List[str]  # Users/agents who can manage


@dataclass
class CollectionMetadata:
    """Metadata for a memory collection"""
    created_at: str
    created_by: str
    permissions: CollectionPermissions
    category: Optional[str] = None      # "documentation", "code", "notes"
    project: Optional[str] = None       # Associated project/context
    retention_days: Optional[int] = None  # TTL in days (optional)
    last_updated: Optional[str] = None


@dataclass
class CollectionInfo:
    """Complete information about a memory collection"""
    name: str
    description: str
    tags: List[str]
    metadata: CollectionMetadata
    stats: Dict[str, Any]  # document_count, size_bytes, etc.


class CollectionManager:
    """
    Manages dynamic memory collections with flexible organization.
    
    Replaces rigid global/learned/agent types with user-defined collections.
    """
    
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_dimension: int = 384
    ):
        """Initialize collection manager."""
        self.client = qdrant_client
        self.embedding_dimension = embedding_dimension
        self.collections_cache = {}  # Cache for collection metadata
        self._initialize_system_collections()

    def _initialize_system_collections(self) -> None:
        """Initialize system collection for storing collection metadata."""
        try:
            system_collection = "system_collections_metadata"
            
            # Check if system collection exists
            existing_collections = {
                col.name for col in self.client.get_collections().collections
            }
            
            if system_collection not in existing_collections:
                self.client.create_collection(
                    collection_name=system_collection,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("✅ Created system collections metadata store")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize system collections: {e}")
            raise

    def create_collection(
        self,
        name: str,
        description: str = "",
        tags: List[str] = None,
        category: str = None,
        project: str = None,
        permissions: CollectionPermissions = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a new memory collection.
        
        Args:
            name: Collection name (must be unique)
            description: Human-readable description
            tags: List of tags for organization
            category: Collection category (optional)
            project: Associated project (optional)
            permissions: Access permissions (optional)
            created_by: Creator identifier
            
        Returns:
            Success/error response with collection info
        """
        try:
            # Validate collection name
            if not self._is_valid_collection_name(name):
                return {
                    "success": False,
                    "error": (
                        f"Invalid collection name: {name}. "
                        "Use alphanumeric, hyphens, underscores only."
                    )
                }
                
            # Check if collection already exists
            if self._collection_exists(name):
                return {
                    "success": False,
                    "error": f"Collection '{name}' already exists"
                }

            # Set defaults
            if tags is None:
                tags = []
            if permissions is None:
                permissions = CollectionPermissions(
                    read=["*"],  # Everyone can read by default
                    write=[created_by],  # Only creator can write
                    admin=[created_by]   # Only creator is admin
                )

            # Create collection metadata
            metadata = CollectionMetadata(
                created_at=datetime.now().isoformat(),
                created_by=created_by,
                permissions=permissions,
                category=category,
                project=project,
                last_updated=datetime.now().isoformat()
            )
            
            # Create the actual Qdrant collection
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            
            # Save collection metadata
            collection_info = CollectionInfo(
                name=name,
                description=description,
                tags=tags,
                metadata=metadata,
                stats={"document_count": 0, "size_bytes": 0}
            )
            
            self._save_collection_metadata(collection_info)
            
            logger.info(f"✅ Created collection: {name}")
            return {
                "success": True,
                "collection": asdict(collection_info),
                "message": f"Collection '{name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create collection {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to create collection: {str(e)}"
            }

    def list_collections(
        self,
        filter_by_tags: List[str] = None,
        filter_by_category: str = None,
        filter_by_project: str = None,
        owned_by: str = None
    ) -> Dict[str, Any]:
        """
        List all collections with optional filtering.
        
        Args:
            filter_by_tags: Filter by tags (all must match)
            filter_by_category: Filter by category
            filter_by_project: Filter by project
            owned_by: Filter by owner/creator
            
        Returns:
            List of collections matching filters
        """
        try:
            all_collections = self._load_all_collection_metadata()
            filtered_collections = []
            
            for collection in all_collections:
                # Apply filters
                if filter_by_tags and not all(
                    tag in collection.tags for tag in filter_by_tags
                ):
                    continue
                if (
                    filter_by_category and
                    collection.metadata.category != filter_by_category
                ):
                    continue
                if (
                    filter_by_project and
                    collection.metadata.project != filter_by_project
                ):
                    continue
                if owned_by and collection.metadata.created_by != owned_by:
                    continue
                    
                # Update stats
                collection.stats = self._get_collection_stats(collection.name)
                filtered_collections.append(collection)
            
            return {
                "success": True,
                "collections": [asdict(col) for col in filtered_collections],
                "total_count": len(filtered_collections)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list collections: {e}")
            return {
                "success": False,
                "error": f"Failed to list collections: {str(e)}"
            }

    def get_collection(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a specific collection."""
        try:
            collection_info = self._load_collection_metadata(name)
            if not collection_info:
                return {
                    "success": False,
                    "error": f"Collection '{name}' not found"
                }
                
            # Update stats
            collection_info.stats = self._get_collection_stats(name)
            
            return {
                "success": True,
                "collection": asdict(collection_info)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to get collection: {str(e)}"
            }

    def update_collection(
        self,
        name: str,
        description: str = None,
        tags: List[str] = None,
        category: str = None,
        project: str = None,
        updated_by: str = "system"
    ) -> Dict[str, Any]:
        """Update collection metadata."""
        try:
            collection_info = self._load_collection_metadata(name)
            if not collection_info:
                return {
                    "success": False,
                    "error": f"Collection '{name}' not found"
                }
                
            # Check permissions
            if not self._can_admin_collection(collection_info, updated_by):
                return {
                    "success": False,
                    "error": "Insufficient permissions to update collection"
                }
            
            # Update fields if provided
            if description is not None:
                collection_info.description = description
            if tags is not None:
                collection_info.tags = tags
            if category is not None:
                collection_info.metadata.category = category
            if project is not None:
                collection_info.metadata.project = project
                
            collection_info.metadata.last_updated = datetime.now().isoformat()
            
            # Save updated metadata
            self._save_collection_metadata(collection_info)
            
            return {
                "success": True,
                "collection": asdict(collection_info),
                "message": f"Collection '{name}' updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update collection {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to update collection: {str(e)}"
            }

    def delete_collection(
        self,
        name: str,
        deleted_by: str = "system",
        confirm: bool = False
    ) -> Dict[str, Any]:
        """Delete a collection and all its data."""
        try:
            if not confirm:
                return {
                    "success": False,
                    "error": (
                        "Collection deletion requires explicit confirmation"
                    )
                }
                
            collection_info = self._load_collection_metadata(name)
            if not collection_info:
                return {
                    "success": False,
                    "error": f"Collection '{name}' not found"
                }
                
            # Check permissions
            if not self._can_admin_collection(collection_info, deleted_by):
                return {
                    "success": False,
                    "error": "Insufficient permissions to delete collection"
                }
            
            # Delete the Qdrant collection
            self.client.delete_collection(collection_name=name)
            
            # Remove metadata
            self._delete_collection_metadata(name)
            
            logger.info(f"✅ Deleted collection: {name}")
            return {
                "success": True,
                "message": f"Collection '{name}' deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete collection {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to delete collection: {str(e)}"
            }

    # Helper methods
    
    def _is_valid_collection_name(self, name: str) -> bool:
        """Validate collection name format."""
        import re
        # Allow alphanumeric, hyphens, underscores, dots
        pattern = r'^[a-zA-Z0-9_\-\.]+$'
        return bool(re.match(pattern, name)) and len(name) <= 100

    def _collection_exists(self, name: str) -> bool:
        """Check if collection exists in Qdrant."""
        try:
            existing_collections = {
                col.name for col in self.client.get_collections().collections
            }
            return name in existing_collections
        except Exception:
            return False

    def _get_collection_stats(self, name: str) -> Dict[str, Any]:
        """Get current statistics for a collection."""
        try:
            info = self.client.get_collection(name)
            return {
                "document_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status.value if info.status else "unknown",
                "indexed_vectors": info.indexed_vectors_count or 0
            }
        except Exception as e:
            logger.warning(f"Failed to get stats for {name}: {e}")
            return {"document_count": 0, "vectors_count": 0, "status": "unknown"}

    def _save_collection_metadata(
        self, collection_info: CollectionInfo
    ) -> None:
        """Save collection metadata to system collection."""
        try:
            # Convert to point for storage
            metadata_point = PointStruct(
                id=abs(hash(collection_info.name)),  # Use absolute hash as ID
                vector=[0.0] * self.embedding_dimension,  # Dummy vector
                payload={
                    "collection_name": collection_info.name,
                    "metadata": asdict(collection_info),
                    "type": "collection_metadata"
                }
            )
            
            self.client.upsert(
                collection_name="system_collections_metadata",
                points=[metadata_point]
            )
            
            # Update cache
            self.collections_cache[collection_info.name] = collection_info
            
        except Exception as e:
            logger.error(
                f"Failed to save metadata for {collection_info.name}: {e}"
            )
            raise

    def _load_collection_metadata(self, name: str) -> Optional[CollectionInfo]:
        """Load collection metadata from system collection."""
        try:
            # Check cache first
            if name in self.collections_cache:
                return self.collections_cache[name]
                
            # Query system collection
            results = self.client.scroll(
                collection_name="system_collections_metadata",
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="collection_name",
                            match=MatchValue(value=name)
                        )
                    ]
                ),
                limit=1
            )
            
            if results[0]:  # points found
                point = results[0][0]
                metadata_dict = point.payload["metadata"]
                
                # Reconstruct CollectionInfo object
                collection_info = CollectionInfo(
                    name=metadata_dict["name"],
                    description=metadata_dict["description"],
                    tags=metadata_dict["tags"],
                    metadata=CollectionMetadata(**metadata_dict["metadata"]),
                    stats=metadata_dict["stats"]
                )
                
                # Cache it
                self.collections_cache[name] = collection_info
                return collection_info
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to load metadata for {name}: {e}")
            return None

    def _load_all_collection_metadata(self) -> List[CollectionInfo]:
        """Load metadata for all collections."""
        try:
            results = self.client.scroll(
                collection_name="system_collections_metadata",
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="type",
                            match=MatchValue(value="collection_metadata")
                        )
                    ]
                ),
                limit=1000  # Should be enough for most use cases
            )
            
            collections = []
            for point in results[0]:
                metadata_dict = point.payload["metadata"]
                collection_info = CollectionInfo(
                    name=metadata_dict["name"],
                    description=metadata_dict["description"],
                    tags=metadata_dict["tags"],
                    metadata=CollectionMetadata(**metadata_dict["metadata"]),
                    stats=metadata_dict["stats"]
                )
                collections.append(collection_info)
                
                # Update cache
                self.collections_cache[collection_info.name] = collection_info
                
            return collections
            
        except Exception as e:
            logger.error(f"Failed to load all collection metadata: {e}")
            return []

    def _delete_collection_metadata(self, name: str) -> None:
        """Delete collection metadata from system collection."""
        try:
            self.client.delete(
                collection_name="system_collections_metadata",
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="collection_name",
                            match=MatchValue(value=name)
                        )
                    ]
                )
            )
            
            # Remove from cache
            if name in self.collections_cache:
                del self.collections_cache[name]
                
        except Exception as e:
            logger.error(f"Failed to delete metadata for {name}: {e}")
            raise

    def _can_admin_collection(
        self, collection_info: CollectionInfo, user: str
    ) -> bool:
        """Check if user has admin permissions for collection."""
        return (
            user in collection_info.metadata.permissions.admin or
            "*" in collection_info.metadata.permissions.admin or
            user == collection_info.metadata.created_by
        )

    def _can_write_collection(
        self, collection_info: CollectionInfo, user: str
    ) -> bool:
        """Check if user has write permissions for collection."""
        return (
            self._can_admin_collection(collection_info, user) or
            user in collection_info.metadata.permissions.write or
            "*" in collection_info.metadata.permissions.write
        )

    def _can_read_collection(
        self, collection_info: CollectionInfo, user: str
    ) -> bool:
        """Check if user has read permissions for collection."""
        return (
            self._can_write_collection(collection_info, user) or
            user in collection_info.metadata.permissions.read or
            "*" in collection_info.metadata.permissions.read
        )
