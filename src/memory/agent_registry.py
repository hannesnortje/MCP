"""
Agent registry management for the MCP Memory Server.

This module handles agent registration, permissions, and management,
extracted from the monolithic memory_manager.py for better separation
of concerns.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from ..config import Config

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manager for agent registration and permissions."""
    
    def __init__(self, client: QdrantClient, embedding_service):
        """Initialize agent registry with client and embedding service."""
        self.client = client
        self.embedding_service = embedding_service
    
    def _agent_id_to_point_id(self, agent_id: str) -> str:
        """Convert agent ID to valid Qdrant point ID.
        
        Qdrant requires point IDs to be either unsigned integers or UUIDs.
        This function converts any agent ID to a valid UUID using UUID5
        (deterministic namespace-based UUID).
        
        Args:
            agent_id: The original agent ID (may have prefixes like 'dev-')
            
        Returns:
            A valid UUID string that can be used as Qdrant point ID
        """
        # If agent_id is already a valid UUID, use it directly
        try:
            uuid.UUID(agent_id)
            return agent_id  # It's already a valid UUID
        except ValueError:
            pass
        
        # Create a deterministic UUID5 based on the agent_id
        # Using a fixed namespace for consistency
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        return str(uuid.uuid5(namespace, agent_id))
    
    async def register_agent(
        self,
        agent_id: str,
        agent_role: str = "general",
        memory_layers: List[str] = None,
        permissions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Register a new agent in the agent registry."""
        try:
            if memory_layers is None:
                memory_layers = ["global", "learned"]
            
            if permissions is None:
                permissions = {
                    "can_read": memory_layers,
                    "can_write": memory_layers,
                    "can_admin": []
                }

            agent_metadata = {
                "agent_id": agent_id,
                "agent_role": agent_role,
                "memory_layers": memory_layers,
                "permissions": permissions,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }

            # Create embedding for searchability
            search_text = f"Agent {agent_id} role {agent_role}"
            embedding = self.embedding_service.embed_text(search_text)

            # Store in agent registry
            point = PointStruct(
                id=self._agent_id_to_point_id(agent_id),
                vector=embedding,
                payload=agent_metadata
            )

            self.client.upsert(
                collection_name=Config.AGENT_REGISTRY_COLLECTION,
                points=[point]
            )

            logger.info(
                f"✅ Registered agent {agent_id} with role {agent_role}"
            )
            return {
                "success": True,
                "agent_id": agent_id,
                "message": f"Agent {agent_id} registered successfully"
            }

        except Exception as e:
            logger.error(f"❌ Failed to register agent {agent_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to register agent: {str(e)}"
            }

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent information from registry."""
        try:
            result = self.client.retrieve(
                collection_name=Config.AGENT_REGISTRY_COLLECTION,
                ids=[self._agent_id_to_point_id(agent_id)]
            )

            if result:
                agent_data = result[0].payload
                return {
                    "success": True,
                    "agent": agent_data
                }
            else:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found"
                }

        except Exception as e:
            logger.error(f"❌ Failed to get agent {agent_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to get agent: {str(e)}"
            }

    async def update_agent_permissions(
        self,
        agent_id: str,
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update agent permissions."""
        try:
            # Get current agent data
            current_result = await self.get_agent(agent_id)
            if not current_result["success"]:
                return current_result

            # Update permissions
            agent_data = current_result["agent"]
            agent_data["permissions"] = permissions
            agent_data["updated_at"] = datetime.now().isoformat()

            # Create embedding for updated data
            search_text = f"Agent {agent_id} role {agent_data['agent_role']}"
            embedding = self.embedding_service.embed_text(search_text)

            # Update in registry
            point = PointStruct(
                id=self._agent_id_to_point_id(agent_id),
                vector=embedding,
                payload=agent_data
            )

            self.client.upsert(
                collection_name=Config.AGENT_REGISTRY_COLLECTION,
                points=[point]
            )

            logger.info(f"✅ Updated permissions for agent {agent_id}")
            return {
                "success": True,
                "agent_id": agent_id,
                "message": "Permissions updated successfully"
            }

        except Exception as e:
            logger.error(f"❌ Failed to update agent permissions: {e}")
            return {
                "success": False,
                "error": f"Failed to update permissions: {str(e)}"
            }

    async def list_agents(self) -> Dict[str, Any]:
        """List all registered agents."""
        try:
            # Get all points from agent registry
            result = self.client.scroll(
                collection_name=Config.AGENT_REGISTRY_COLLECTION,
                limit=100,  # Adjust as needed
                with_payload=True
            )

            agents = []
            if result[0]:  # result is a tuple (points, next_page_offset)
                for point in result[0]:
                    agents.append(point.payload)

            return {
                "success": True,
                "agents": agents,
                "count": len(agents)
            }

        except Exception as e:
            logger.error(f"❌ Failed to list agents: {e}")
            return {
                "success": False,
                "error": f"Failed to list agents: {str(e)}"
            }

    async def check_agent_permission(
        self,
        agent_id: str,
        action: str,
        memory_type: str
    ) -> bool:
        """Check if agent has permission for a specific action."""
        try:
            agent_result = await self.get_agent(agent_id)
            if not agent_result["success"]:
                return False

            permissions = agent_result["agent"].get("permissions", {})
            allowed_layers = permissions.get(f"can_{action}", [])
            
            return memory_type in allowed_layers

        except Exception as e:
            logger.error(f"❌ Permission check failed for {agent_id}: {e}")
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
        try:
            action_log = {
                "agent_id": agent_id,
                "action": action,
                "context": context,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat()
            }

            # Store as learned memory if requested
            if store_as_learned:
                learned_content = (
                    f"Agent {agent_id} performed {action}. "
                    f"Context: {context}. Outcome: {outcome}"
                )
                
                # Use vector operations to store learned content
                from .vector_operations import VectorOperations
                vector_ops = VectorOperations(
                    self.client, self.embedding_service
                )
                
                await vector_ops.async_add_to_memory(
                    content=learned_content,
                    collection=Config.LEARNED_MEMORY_COLLECTION,
                    metadata={
                        "type": "agent_action",
                        "pattern_type": "behavioral",
                        "agent_id": agent_id,
                        "action": action,
                        **action_log
                    }
                )

            logger.info(f"📝 Logged action for agent {agent_id}: {action}")
            return {
                "success": True,
                "message": "Action logged successfully",
                "stored_as_learned": store_as_learned
            }

        except Exception as e:
            logger.error(f"❌ Failed to log action for {agent_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to log action: {str(e)}"
            }
