"""
System Health Monitor for MCP Memory Server.
Handles health checks and diagnostic information collection.
"""

from datetime import datetime
from typing import Dict, Any

try:
    from .server_config import get_logger
    from .error_handler import retry_qdrant_operation, error_handler
except ImportError:
    from server_config import get_logger
    from error_handler import retry_qdrant_operation, error_handler

logger = get_logger("health-monitor")


class SystemHealthMonitor:
    """Monitors system health and provides diagnostic information."""
    
    def __init__(self, memory_manager=None):
        """Initialize with optional memory manager reference."""
        self.memory_manager = memory_manager
    
    @retry_qdrant_operation(max_attempts=2)
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        health_info = {
            "timestamp": str(datetime.now()),
            "overall_status": "unknown",
            "components": {},
            "error_statistics": error_handler.get_error_stats(),
            "memory_manager": {
                "available": self.memory_manager is not None,
                "collections_initialized": False
            }
        }
        
        try:
            # Check Qdrant connection
            if self.memory_manager and self.memory_manager.client:
                try:
                    collections = self.memory_manager.client.get_collections()
                    health_info["components"]["qdrant"] = {
                        "status": "healthy",
                        "collections_count": len(collections.collections),
                        "collections": [
                            col.name for col in collections.collections
                        ]
                    }
                    health_info["memory_manager"]["collections_initialized"] = True
                except Exception as e:
                    health_info["components"]["qdrant"] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            else:
                health_info["components"]["qdrant"] = {
                    "status": "unavailable",
                    "reason": "Memory manager or client not initialized"
                }
            
            # Check embedding model
            if (self.memory_manager and 
                self.memory_manager.embedding_model):
                try:
                    # Test embedding with simple text
                    test_embedding = self.memory_manager.embedding_model.encode(
                        "health check test"
                    )
                    health_info["components"]["embedding_model"] = {
                        "status": "healthy",
                        "model_name": getattr(
                            self.memory_manager.embedding_model,
                            'model_name',
                            'unknown'
                        ),
                        "embedding_dimensions": len(test_embedding)
                    }
                except Exception as e:
                    health_info["components"]["embedding_model"] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
            else:
                health_info["components"]["embedding_model"] = {
                    "status": "unavailable",
                    "reason": "Embedding model not initialized"
                }
            
            # Determine overall status
            component_statuses = [
                comp.get("status", "unknown") 
                for comp in health_info["components"].values() 
                if isinstance(comp, dict) and "status" in comp
            ]
            
            if all(status == "healthy" for status in component_statuses):
                health_info["overall_status"] = "healthy"
            elif any(status == "unhealthy" for status in component_statuses):
                health_info["overall_status"] = "unhealthy"
            else:
                health_info["overall_status"] = "degraded"
                
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            health_info["overall_status"] = "error"
            health_info["health_check_error"] = str(e)
        
        return health_info

    def check_component_health(
        self, component_name: str
    ) -> Dict[str, Any]:
        """Check health of a specific component."""
        if component_name == "qdrant":
            return self._check_qdrant_health()
        elif component_name == "embedding":
            return self._check_embedding_health()
        elif component_name == "memory_manager":
            return self._check_memory_manager_health()
        else:
            return {
                "status": "unknown",
                "error": f"Unknown component: {component_name}"
            }
    
    def _check_qdrant_health(self) -> Dict[str, Any]:
        """Check Qdrant database health."""
        if not self.memory_manager or not self.memory_manager.client:
            return {
                "status": "unavailable",
                "reason": "Qdrant client not initialized"
            }
        
        try:
            collections = self.memory_manager.client.get_collections()
            return {
                "status": "healthy",
                "collections_count": len(collections.collections),
                "collections": [col.name for col in collections.collections]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _check_embedding_health(self) -> Dict[str, Any]:
        """Check embedding model health."""
        if not self.memory_manager or not self.memory_manager.embedding_model:
            return {
                "status": "unavailable",
                "reason": "Embedding model not initialized"
            }
        
        try:
            test_embedding = self.memory_manager.embedding_model.encode(
                "health check test"
            )
            return {
                "status": "healthy",
                "model_name": getattr(
                    self.memory_manager.embedding_model,
                    'model_name',
                    'unknown'
                ),
                "embedding_dimensions": len(test_embedding)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _check_memory_manager_health(self) -> Dict[str, Any]:
        """Check memory manager health."""
        if not self.memory_manager:
            return {
                "status": "unavailable",
                "reason": "Memory manager not initialized"
            }
        
        try:
            # Check if generic service is available
            has_generic_service = hasattr(
                self.memory_manager, 'generic_service'
            ) and self.memory_manager.generic_service is not None
            
            return {
                "status": "healthy",
                "has_generic_service": has_generic_service,
                "client_available": self.memory_manager.client is not None,
                "embedding_available": (
                    self.memory_manager.embedding_model is not None
                )
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }