"""
File metadata management for the MCP Memory Server.

This module handles file processing metadata and duplicate file checking,
extracted from the monolithic memory_manager.py for better separation
of concerns.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from ..config import Config

logger = logging.getLogger(__name__)


class FileMetadataManager:
    """Manager for file metadata and processing tracking."""
    
    def __init__(self, client: QdrantClient, embedding_service):
        """Initialize file metadata manager."""
        self.client = client
        self.embedding_service = embedding_service
    
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
        try:
            if additional_metadata is None:
                additional_metadata = {}
                
            metadata = {
                "file_path": file_path,
                "file_hash": file_hash,
                "file_size": file_size,
                "processing_status": processing_status,
                "chunks_created": chunks_created,
                "processing_time": processing_time,
                "processed_at": datetime.now().isoformat(),
                **additional_metadata
            }

            # Create searchable text for embedding
            search_text = f"File {file_path} processed status {processing_status}"
            embedding = self.embedding_service.embed_text(search_text)

            # Use file hash as point ID for easy retrieval
            point = PointStruct(
                id=file_hash,
                vector=embedding,
                payload=metadata
            )

            self.client.upsert(
                collection_name=Config.FILE_METADATA_COLLECTION,
                points=[point]
            )

            logger.info(f"📄 Added metadata for file: {file_path}")
            return {
                "success": True,
                "file_path": file_path,
                "file_hash": file_hash
            }

        except Exception as e:
            logger.error(f"❌ Failed to add file metadata: {e}")
            return {"success": False, "error": str(e)}

    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by file path."""
        try:
            # Search by file path in metadata
            search_text = f"File {file_path}"
            query_embedding = self.embedding_service.embed_text(search_text)
            
            results = self.client.search(
                collection_name=Config.FILE_METADATA_COLLECTION,
                query_vector=query_embedding,
                limit=10,
                with_payload=True
            )

            # Find exact match by file path
            for result in results:
                if result.payload.get("file_path") == file_path:
                    return result.payload

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get file metadata: {e}")
            return None

    def check_file_processed(self, file_path: str, file_hash: str) -> bool:
        """Check if file has been processed based on path and hash."""
        try:
            # First try direct lookup by hash
            result = self.client.retrieve(
                collection_name=Config.FILE_METADATA_COLLECTION,
                ids=[file_hash]
            )
            
            if result:
                return True
                
            # Fallback to metadata lookup
            metadata = self.get_file_metadata(file_path)
            return metadata is not None and metadata.get("file_hash") == file_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to check file processed status: {e}")
            return False

    def update_file_status(
        self,
        file_hash: str,
        status: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update file processing status."""
        try:
            # Get current metadata
            current_result = self.client.retrieve(
                collection_name=Config.FILE_METADATA_COLLECTION,
                ids=[file_hash]
            )
            
            if not current_result:
                return {"success": False, "error": "File metadata not found"}
            
            # Update metadata
            metadata = current_result[0].payload
            metadata["processing_status"] = status
            metadata["updated_at"] = datetime.now().isoformat()
            
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Create updated embedding
            search_text = f"File {metadata['file_path']} processed status {status}"
            embedding = self.embedding_service.embed_text(search_text)
            
            # Update point
            point = PointStruct(
                id=file_hash,
                vector=embedding,
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=Config.FILE_METADATA_COLLECTION,
                points=[point]
            )
            
            logger.info(f"📄 Updated status for file hash {file_hash}: {status}")
            return {
                "success": True,
                "file_hash": file_hash,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update file status: {e}")
            return {"success": False, "error": str(e)}

    def list_processed_files(
        self,
        status_filter: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List processed files with optional status filter."""
        try:
            result = self.client.scroll(
                collection_name=Config.FILE_METADATA_COLLECTION,
                limit=limit,
                with_payload=True
            )
            
            files = []
            if result[0]:  # result is a tuple (points, next_page_offset)
                for point in result[0]:
                    metadata = point.payload
                    if status_filter is None or metadata.get("processing_status") == status_filter:
                        files.append(metadata)
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list processed files: {e}")
            return {"success": False, "error": str(e)}

    def delete_file_metadata(self, file_hash: str) -> Dict[str, Any]:
        """Delete file metadata by hash."""
        try:
            self.client.delete(
                collection_name=Config.FILE_METADATA_COLLECTION,
                points_selector=[file_hash]
            )
            
            logger.info(f"🗑️ Deleted metadata for file hash: {file_hash}")
            return {
                "success": True,
                "deleted_hash": file_hash
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete file metadata: {e}")
            return {"success": False, "error": str(e)}