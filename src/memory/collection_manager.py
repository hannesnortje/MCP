"""
Collection management for the MCP Memory Server.

This module handles Qdrant collection initialization and management,
extracted from the monolithic memory_manager.py for better separation
of concerns.
"""

import logging
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from ..config import Config

logger = logging.getLogger(__name__)


class CollectionManager:
    """Manager for Qdrant collection operations."""
    
    def __init__(self, client: QdrantClient):
        """Initialize collection manager with Qdrant client."""
        self.client = client
        self.collections_initialized = False
    
    def _ensure_legacy_collections(self) -> None:
        """Ensure legacy collections exist for backward compatibility."""
        try:
            legacy_collections = [
                "global_memory",
                "learned_memory", 
                "agent_registry"
            ]
            
            existing_collections = {
                col.name for col in self.client.get_collections().collections
            }
            
            for collection_name in legacy_collections:
                if collection_name not in existing_collections:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=Config.EMBEDDING_DIMENSION,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"✅ Created legacy collection: {collection_name}")
                else:
                    logger.info(f"📁 Legacy collection exists: {collection_name}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to ensure legacy collections: {e}")
            raise
    
    def _sync_initialize_collections(self) -> None:
        """Initialize all required collections synchronously."""
        try:
            # Define collections to create
            collections_to_create = [
                Config.GLOBAL_MEMORY_COLLECTION,
                Config.LEARNED_MEMORY_COLLECTION,
                Config.AGENT_REGISTRY_COLLECTION,
                Config.FILE_METADATA_COLLECTION
            ]

            existing_collections = {
                col.name for col in self.client.get_collections().collections
            }

            for collection_name in collections_to_create:
                if collection_name not in existing_collections:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=Config.EMBEDDING_DIMENSION,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"✅ Created collection: {collection_name}")
                else:
                    logger.info(f"📁 Collection already exists: {collection_name}")

            self.collections_initialized = True
            logger.info("✅ All collections initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize collections: {e}")
            raise
    
    async def _initialize_collections(self) -> None:
        """Initialize all required collections asynchronously."""
        try:
            # Define collections to create  
            collections_to_create = [
                Config.GLOBAL_MEMORY_COLLECTION,
                Config.LEARNED_MEMORY_COLLECTION,
                Config.AGENT_REGISTRY_COLLECTION,
                Config.FILE_METADATA_COLLECTION
            ]

            existing_collections = {
                col.name for col in self.client.get_collections().collections
            }

            for collection_name in collections_to_create:
                if collection_name not in existing_collections:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=Config.EMBEDDING_DIMENSION,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"✅ Created collection: {collection_name}")
                else:
                    logger.info(f"📁 Collection already exists: {collection_name}")

            self.collections_initialized = True
            logger.info("✅ All collections initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize collections: {e}")
            raise
    
    def _ensure_agent_collection(self, agent_id: str) -> None:
        """Ensure agent-specific collection exists."""
        try:
            collection_name = Config.get_collection_name("agent", agent_id)
            
            existing_collections = {
                col.name for col in self.client.get_collections().collections
            }
            
            if collection_name not in existing_collections:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=Config.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created agent collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to ensure agent collection: {e}")
            raise
    
    def ensure_agent_collection(self, agent_id: str) -> None:
        """Public interface for ensuring agent collection."""
        return self._ensure_agent_collection(agent_id)
    
    async def initialize_collections(self) -> None:
        """Public interface for async collection initialization."""
        await self._initialize_collections()
    
    def sync_initialize_collections(self) -> None:
        """Public interface for sync collection initialization."""
        self._sync_initialize_collections()
    
    def ensure_legacy_collections(self) -> None:
        """Public interface for ensuring legacy collections."""
        self._ensure_legacy_collections()