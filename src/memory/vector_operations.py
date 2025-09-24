"""
Core vector database operations for the MCP Memory Server.

This module handles vector storage, retrieval, and similarity operations,
extracted from the monolithic memory_manager.py for better separation
of concerns.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, Range
from ..config import Config

logger = logging.getLogger(__name__)


class VectorOperations:
    """Core vector database operations manager."""
    
    def __init__(self, client: QdrantClient, embedding_service):
        """Initialize vector operations with client and embedding service."""
        self.client = client
        self.embedding_service = embedding_service
    
    def async_add_to_memory(
        self,
        content: str,
        collection: str,
        metadata: Optional[Dict[str, Any]] = None,
        content_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add content to specified memory collection."""
        try:
            if metadata is None:
                metadata = {}
                
            # Generate content hash if not provided
            if content_hash is None:
                content_hash = self.embedding_service.generate_content_hash(content)
            
            # Generate embedding
            embedding = self.embedding_service.embed_text(content)
            
            # Prepare metadata
            full_metadata = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
            
            # Create point
            point = PointStruct(
                id=content_hash,
                vector=embedding,
                payload=full_metadata
            )
            
            # Store in collection
            self.client.upsert(
                collection_name=collection,
                points=[point]
            )
            
            logger.info(f"✅ Added content to {collection}")
            return {
                "success": True,
                "content_hash": content_hash,
                "collection": collection
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add to memory: {e}")
            return {"success": False, "error": str(e)}
    
    def async_query_memory(
        self,
        query: str,
        collection: str,
        limit: int = 10,
        min_score: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query memory collection for relevant content."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)
            
            # Prepare filters if provided
            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, (int, float)):
                        conditions.append(
                            FieldCondition(key=key, range=Range(gte=value))
                        )
                    else:
                        conditions.append(
                            FieldCondition(key=key, match={"value": value})
                        )
                if conditions:
                    qdrant_filter = Filter(must=conditions)
            
            # Search collection
            results = self.client.search(
                collection_name=collection,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=min_score,
                query_filter=qdrant_filter,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.payload.get("content", ""),
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k != "content"}
                })
            
            logger.info(f"🔍 Found {len(formatted_results)} results in {collection}")
            return {
                "success": True,
                "results": formatted_results,
                "query": query,
                "collection": collection
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to query memory: {e}")
            return {"success": False, "error": str(e)}
    
    def async_check_duplicate_with_similarity(
        self,
        content: str,
        collection: str,
        similarity_threshold: float = 0.95,
        metadata_filters: Optional[Dict[str, Any]] = None,
        check_hash_first: bool = True
    ) -> Dict[str, Any]:
        """Check for duplicate content using similarity search."""
        try:
            results = {"is_duplicate": False, "similar_content": []}
            
            # First check by content hash if requested
            if check_hash_first:
                content_hash = self.embedding_service.generate_content_hash(content)
                try:
                    existing = self.client.retrieve(
                        collection_name=collection,
                        ids=[content_hash]
                    )
                    if existing:
                        results["is_duplicate"] = True
                        results["exact_match"] = True
                        results["duplicate_id"] = content_hash
                        return results
                except Exception:
                    pass  # Continue to similarity check
            
            # Generate embedding for similarity search
            query_embedding = self.embedding_service.embed_text(content)
            
            # Prepare filters if provided
            qdrant_filter = None
            if metadata_filters:
                conditions = []
                for key, value in metadata_filters.items():
                    conditions.append(
                        FieldCondition(key=key, match={"value": value})
                    )
                if conditions:
                    qdrant_filter = Filter(must=conditions)
            
            # Search for similar content
            similar_results = self.client.search(
                collection_name=collection,
                query_vector=query_embedding,
                limit=5,
                score_threshold=similarity_threshold,
                query_filter=qdrant_filter,
                with_payload=True
            )
            
            if similar_results:
                results["is_duplicate"] = True
                results["similar_content"] = [
                    {
                        "content": result.payload.get("content", ""),
                        "similarity": result.score,
                        "id": result.id
                    }
                    for result in similar_results
                ]
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Duplicate check failed: {e}")
            return {"is_duplicate": False, "error": str(e)}
    
    def async_check_duplicate(
        self,
        content: str,
        collection: str,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Simple duplicate check by content hash."""
        try:
            content_hash = self.embedding_service.generate_content_hash(content)
            
            existing = self.client.retrieve(
                collection_name=collection,
                ids=[content_hash]
            )
            
            return len(existing) > 0
            
        except Exception as e:
            logger.error(f"❌ Duplicate check failed: {e}")
            return False
    
    def async_delete_content(
        self,
        content_hash: str,
        collection: str
    ) -> Dict[str, Any]:
        """Delete content from collection by hash."""
        try:
            self.client.delete(
                collection_name=collection,
                points_selector=[content_hash]
            )
            
            logger.info(f"🗑️ Deleted content from {collection}")
            return {
                "success": True,
                "deleted_id": content_hash,
                "collection": collection
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete content: {e}")
            return {"success": False, "error": str(e)}
    
    def async_get_collection_info(
        self, 
        collection: str
    ) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection)
            
            return {
                "name": info.config.collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status.value if info.status else "unknown"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection info: {e}")
            return {"error": str(e)}