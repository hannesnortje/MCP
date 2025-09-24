"""
Qdrant Memory Manager for MCP Memory Server (Refactored Router).

This is now a lightweight router that delegates to specialized memory modules
while maintaining backward compatibility with the existing MCP server interface.
Refactored from monolithic 1,106-line class for better maintainability.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.config import Config
from .error_handler import retry_qdrant_operation
from .generic_memory_service import GenericMemoryService

# Import specialized memory modules
from .memory import (
    VectorOperations,
    AgentRegistry,
    FileMetadataManager,
    EmbeddingService,
    CollectionManager
)

logger = logging.getLogger(__name__)


class QdrantMemoryManager:
    """
    Lightweight router that delegates to specialized memory modules.
    
    Maintains backward compatibility with existing MCP server interface
    while using modular architecture for better maintainability.
    """

    def __init__(self) -> None:
        """Initialize the Memory Manager Router."""
        # Legacy interface compatibility
        self.client: Optional[QdrantClient] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.collections_initialized = False
        self.current_agent_id = None
        self.current_context = {}
        
        # Generic memory service for backward compatibility
        self.generic_service = GenericMemoryService()
        
        # Specialized modules (initialized after client setup)
        self.embedding_service: Optional[EmbeddingService] = None
        self.collection_manager: Optional[CollectionManager] = None
        self.vector_operations: Optional[VectorOperations] = None
        self.agent_registry: Optional[AgentRegistry] = None
        self.file_metadata_manager: Optional[FileMetadataManager] = None
        
        # Initialize synchronously for MCP server compatibility
        self._sync_initialize()

    def _agent_id_to_point_id(self, agent_id: str) -> str:
        """Convert agent ID to valid Qdrant point ID."""
        try:
            uuid.UUID(agent_id)
            return agent_id  # It's already a valid UUID
        except ValueError:
            pass
        
        # Create a deterministic UUID5 based on the agent_id
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        return str(uuid.uuid5(namespace, agent_id))

    @retry_qdrant_operation(max_attempts=3)
    def _sync_initialize(self) -> None:
        """Synchronous initialization for compatibility."""
        try:
            # Initialize the generic memory service synchronously
            import asyncio
            
            # Check if we can run async operations
            try:
                asyncio.get_running_loop()
                logger.warning(
                    "Already in event loop during sync initialization - "
                    "using fallback sync init"
                )
                # Fall back to old sync initialization
                self._fallback_sync_init()
            except RuntimeError:
                # No event loop, run async initialization
                asyncio.run(self._async_initialize_generic_service())
                logger.info(
                    "✅ QdrantMemoryManager initialized with GenericMemoryService"
                )

        except Exception as e:
            logger.error(f"❌ Failed to initialize QdrantMemoryManager: {e}")
            # Fall back to sync initialization
            try:
                self._fallback_sync_init()
                logger.info("✅ Fallback sync initialization completed")
            except Exception as fallback_error:
                logger.error(
                    f"❌ Fallback initialization also failed: {fallback_error}"
                )
                raise
            
    async def _async_initialize_generic_service(self) -> None:
        """Initialize the generic memory service asynchronously."""
        await self.generic_service.initialize()
        
    def _fallback_sync_init(self) -> None:
        """Fallback to sync initialization with modular services."""
        # Initialize Qdrant client directly
        if Config.QDRANT_API_KEY:
            self.client = QdrantClient(
                host=Config.QDRANT_HOST,
                port=Config.QDRANT_PORT,
                api_key=Config.QDRANT_API_KEY,
                timeout=60
            )
        else:
            self.client = QdrantClient(
                host=Config.QDRANT_HOST,
                port=Config.QDRANT_PORT,
                timeout=60
            )

        # Test connection
        collections = self.client.get_collections()
        logger.info(
            f"✅ Connected to Qdrant at {Config.QDRANT_HOST}:"
            f"{Config.QDRANT_PORT}"
        )
        logger.info(
            f"Found {len(collections.collections)} existing collections"
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        logger.info(f"✅ Loaded embedding model: {Config.EMBEDDING_MODEL}")

        # Initialize specialized modules
        self._initialize_modules()

        # Initialize collections using collection manager
        if self.collection_manager:
            self.collection_manager.sync_initialize_collections()
            self.collections_initialized = True
        
        # Initialize the generic service with the same client and model
        self.generic_service.client = self.client
        self.generic_service.embedding_model = self.embedding_model
        self.generic_service.collection_manager = self.collection_manager
        self.generic_service.initialized = True
    
    def _initialize_modules(self) -> None:
        """Initialize specialized memory modules."""
        try:
            # Initialize embedding service
            self.embedding_service = EmbeddingService()
            # Set embedding model directly (sync initialization)
            self.embedding_service.embedding_model = self.embedding_model
            
            # Initialize collection manager
            self.collection_manager = CollectionManager(self.client)
            
            # Initialize vector operations
            self.vector_operations = VectorOperations(
                self.client,
                self.embedding_service
            )
            
            # Initialize agent registry
            self.agent_registry = AgentRegistry(
                self.client,
                self.embedding_service
            )
            
            # Initialize file metadata manager
            self.file_metadata_manager = FileMetadataManager(
                self.client,
                self.embedding_service
            )
            
            logger.info("✅ Specialized memory modules initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize modules: {e}")
            raise

    # MCP Server Interface Methods

    def set_agent_context(
        self, 
        agent_id: str, 
        context_type: str, 
        description: str
    ) -> None:
        """Set the current agent context for memory operations."""
        self.current_agent_id = agent_id
        self.current_context = {
            "agent_id": agent_id,
            "context_type": context_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"🎯 Set agent context: {agent_id} ({context_type})")

    def add_to_global_memory(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5
    ) -> Dict[str, Any]:
        """Add content to global memory via GenericMemoryService."""
        return self.generic_service.add_to_global_memory(
            content, category, importance
        )

    def add_to_learned_memory(
        self,
        content: str,
        pattern_type: str = "insight",
        confidence: float = 0.7
    ) -> Dict[str, Any]:
        """Add learned patterns to memory via GenericMemoryService."""
        return self.generic_service.add_to_learned_memory(
            content, pattern_type, confidence
        )

    def add_to_agent_memory(
        self, 
        content: str, 
        agent_id: Optional[str] = None, 
        memory_type: str = "general"
    ) -> Dict[str, Any]:
        """Add content to agent-specific memory via vector operations."""
        try:
            target_agent_id = agent_id or self.current_agent_id
            if not target_agent_id:
                return {
                    "success": False, 
                    "error": "No agent ID provided or set in context"
                }

            # Ensure agent collection exists via collection manager
            if self.collection_manager:
                self.collection_manager.ensure_agent_collection(target_agent_id)
            
            # Use vector operations to add content
            collection_name = Config.get_collection_name("agent", target_agent_id)
            if self.vector_operations:
                result = self.vector_operations.async_add_to_memory(
                    content=content,
                    collection=collection_name,
                    metadata={
                        "agent_id": target_agent_id,
                        "memory_type": memory_type
                    }
                )
                
                if result["success"]:
                    result["message"] = (
                        f"Added to agent memory for {target_agent_id}"
                    )
                
                return result
            else:
                return {
                    "success": False, 
                    "error": "Vector operations not initialized"
                }

        except Exception as e:
            logger.error(f"❌ Failed to add to agent memory: {e}")
            return {"success": False, "error": str(e)}

    def query_memory(
        self,
        query: str,
        memory_types: List[str] = None,
        limit: int = 10,
        min_score: float = 0.3
    ) -> Dict[str, Any]:
        """Query memory for relevant content via GenericMemoryService."""
        return self.generic_service.query_memory(
            query, memory_types, limit, min_score
        )

    def compare_against_learned_memory(
        self,
        situation: str,
        comparison_type: str = "pattern_match",
        limit: int = 5
    ) -> Dict[str, Any]:
        """Compare situation against learned patterns via service."""
        return self.generic_service.compare_against_learned_memory(
            situation, comparison_type, limit
        )

    # Async Interface Methods

    async def initialize(self) -> None:
        """Initialize Qdrant client and embedding model."""
        await self.generic_service.initialize()
        
        # Copy initialized components
        self.client = self.generic_service.client
        self.embedding_model = self.generic_service.embedding_model
        self.collections_initialized = True
        
        # Initialize specialized modules
        self._initialize_modules()

    # Vector Operations Delegation

    def async_add_to_memory(
        self,
        content: str,
        collection: str,
        metadata: Optional[Dict[str, Any]] = None,
        content_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add content to specified memory collection."""
        if self.vector_operations:
            return self.vector_operations.async_add_to_memory(
                content, collection, metadata, content_hash
            )
        return {"success": False, "error": "Vector operations not initialized"}

    def async_query_memory(
        self,
        query: str,
        collection: str,
        limit: int = 10,
        min_score: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query memory collection for relevant content."""
        if self.vector_operations:
            return self.vector_operations.async_query_memory(
                query, collection, limit, min_score, filters
            )
        return {"success": False, "error": "Vector operations not initialized"}

    def async_check_duplicate_with_similarity(
        self,
        content: str,
        collection: str,
        similarity_threshold: float = 0.95,
        metadata_filters: Optional[Dict[str, Any]] = None,
        check_hash_first: bool = True
    ) -> Dict[str, Any]:
        """Check for duplicate content using similarity search."""
        if self.vector_operations:
            return self.vector_operations.async_check_duplicate_with_similarity(
                content, collection, similarity_threshold, 
                metadata_filters, check_hash_first
            )
        return {"is_duplicate": False, "error": "Vector operations not initialized"}

    def async_check_duplicate(
        self,
        content: str,
        collection: str,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Simple duplicate check by content hash."""
        if self.vector_operations:
            return self.vector_operations.async_check_duplicate(
                content, collection, metadata_filters
            )
        return False

    def async_delete_content(
        self,
        content_hash: str,
        collection: str
    ) -> Dict[str, Any]:
        """Delete content from collection by hash."""
        if self.vector_operations:
            return self.vector_operations.async_delete_content(
                content_hash, collection
            )
        return {"success": False, "error": "Vector operations not initialized"}

    def async_get_collection_info(
        self, 
        memory_type: str, 
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get information about a collection."""
        collection = (
            Config.get_collection_name(memory_type, agent_id) 
            if agent_id 
            else Config.get_collection_name(memory_type)
        )
        
        if self.vector_operations:
            return self.vector_operations.async_get_collection_info(collection)
        return {"error": "Vector operations not initialized"}

    # Agent Registry Delegation

    async def register_agent(
        self,
        agent_id: str,
        agent_role: str = "general",
        memory_layers: List[str] = None,
        permissions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Register a new agent in the agent registry."""
        if self.agent_registry:
            return await self.agent_registry.register_agent(
                agent_id, agent_role, memory_layers, permissions
            )
        return {"success": False, "error": "Agent registry not initialized"}

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent information from registry."""
        if self.agent_registry:
            return await self.agent_registry.get_agent(agent_id)
        return {"success": False, "error": "Agent registry not initialized"}

    async def update_agent_permissions(
        self,
        agent_id: str,
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update agent permissions."""
        if self.agent_registry:
            return await self.agent_registry.update_agent_permissions(
                agent_id, permissions
            )
        return {"success": False, "error": "Agent registry not initialized"}

    async def list_agents(self) -> Dict[str, Any]:
        """List all registered agents."""
        if self.agent_registry:
            return await self.agent_registry.list_agents()
        return {"success": False, "error": "Agent registry not initialized"}

    async def check_agent_permission(
        self,
        agent_id: str,
        action: str,
        memory_type: str
    ) -> bool:
        """Check if agent has permission for a specific action."""
        if self.agent_registry:
            return await self.agent_registry.check_agent_permission(
                agent_id, action, memory_type
            )
        return False

    async def log_agent_action(
        self,
        agent_id: str,
        action: str,
        context: Dict[str, Any],
        outcome: str,
        store_as_learned: bool = False
    ) -> Dict[str, Any]:
        """Log an agent action and optionally store as learned memory."""
        if self.agent_registry:
            return await self.agent_registry.log_agent_action(
                agent_id, action, context, outcome, store_as_learned
            )
        return {"success": False, "error": "Agent registry not initialized"}

    # File Metadata Management Delegation

    def add_file_metadata(
        self,
        file_path: str,
        file_hash: str,
        file_size: int,
        processing_status: str = "processed",
        chunks_created: int = 0,
        processing_time: float = 0.0,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add file processing metadata to tracking collection."""
        if self.file_metadata_manager:
            return self.file_metadata_manager.add_file_metadata(
                file_path, file_hash, file_size, processing_status,
                chunks_created, processing_time, additional_metadata
            )
        return {"success": False, "error": "File metadata manager not initialized"}

    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by file path."""
        if self.file_metadata_manager:
            return self.file_metadata_manager.get_file_metadata(file_path)
        return None

    def check_file_processed(self, file_path: str, file_hash: str) -> bool:
        """Check if file has been processed based on path and hash."""
        if self.file_metadata_manager:
            return self.file_metadata_manager.check_file_processed(
                file_path, file_hash
            )
        return False

    # Cleanup

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.embedding_service:
                await self.embedding_service.cleanup()
            
            if self.generic_service:
                await self.generic_service.cleanup()
            
            logger.info("🧹 Memory manager cleanup completed")
                
        except Exception as e:
            logger.error(f"⚠️ Error during cleanup: {e}")