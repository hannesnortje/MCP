"""
Agent management handlers for MCP Memory Server.
Handles agent lifecycle, permissions, memory queries, and action logging.
"""

from typing import Dict, Any
from datetime import datetime

try:
    from ..server_config import get_logger
    from ..error_handler import error_handler
except ImportError:
    # Fallback for standalone usage
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)
    
    class MockErrorHandler:
        def get_error_stats(self):
            return {"total_errors": 0}
    
    error_handler = MockErrorHandler()

logger = get_logger("agent-management-handlers")


class AgentManagementHandlers:
    """Handles agent lifecycle and management operations."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager instance."""
        self.memory_manager = memory_manager
    
    async def handle_initialize_new_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a new agent with enhanced functionality from agent_startup."""
        try:
            # Extract parameters with defaults matching agent_startup prompt
            agent_id = arguments.get("agent_id")
            agent_role = arguments.get("agent_role")
            memory_layers = arguments.get("memory_layers", ["global", "learned"])
            policy_version = arguments.get("policy_version", "latest")
            policy_hash = arguments.get("policy_hash", "")
            load_policies = arguments.get("load_policies", True)
            
            # Auto-generate agent_id if not provided (like agent_startup)
            if not agent_id:
                import uuid
                agent_id = str(uuid.uuid4())
            
            # Auto-generate agent_role if not provided
            if not agent_role:
                agent_role = "general"
            
            # Convert string memory_layers to list if needed (for compatibility)
            if isinstance(memory_layers, str):
                memory_layers = [
                    layer.strip() for layer in memory_layers.split(",")
                ]
            
            initialization_messages = []
            errors = []
            
            # Step 1: Register the agent
            try:
                if self.memory_manager:
                    agent_result = await self.memory_manager.register_agent(
                        agent_id=agent_id,
                        agent_role=agent_role,
                        memory_layers=memory_layers
                    )
                    
                    if agent_result["success"]:
                        initialization_messages.append(
                            f"✅ Agent '{agent_id}' registered successfully"
                        )
                    else:
                        errors.append(
                            f"❌ Agent registration failed: "
                            f"{agent_result.get('error', 'Unknown error')}"
                        )
                else:
                    errors.append("❌ Memory manager not available")
            except Exception as e:
                errors.append(f"❌ Agent registration error: {str(e)}")
            
            # Step 2: Load and bind policies (if requested)
            if load_policies:
                try:
                    from ..policy_processor import PolicyProcessor
                    policy_processor = PolicyProcessor()
                    policy_result = await policy_processor.build_canonical_policy(
                        directory=None,  # Use default policy directory
                        policy_version=policy_version
                    )
                    
                    if policy_result["success"]:
                        initialization_messages.append(
                            f"✅ Policy version '{policy_version}' loaded"
                        )
                        initialization_messages.append(
                            f"📁 Files processed: "
                            f"{policy_result.get('files_processed', 0)}"
                        )
                        initialization_messages.append(
                            f"📝 Rules loaded: "
                            f"{policy_result.get('unique_rules', 0)}"
                        )
                        
                        # Update policy hash if we got one from policy load
                        if policy_result.get('policy_hash') and not policy_hash:
                            policy_hash = policy_result['policy_hash']
                    else:
                        errors.append(
                            f"❌ Policy loading failed: "
                            f"{policy_result.get('error', 'Unknown error')}"
                        )
                except Exception as e:
                    errors.append(f"❌ Policy loading error: {str(e)}")
            
            # Step 3: Get system info
            system_info = ""
            try:
                if self.memory_manager:
                    agents_result = await self.memory_manager.list_agents()
                    agent_count = len(agents_result) if agents_result else 0
                    system_info = (
                        f"\n📊 System Status: {agent_count} agents active"
                    )
            except Exception as e:
                system_info = (
                    f"\n⚠️ System Status: Unable to fetch ({str(e)})"
                )
            
            # Determine overall status
            if errors:
                status = "error"
                status_icon = "❌"
                status_text = "FAILED"
            else:
                status = "success"
                status_icon = "✅"
                status_text = "SUCCESS"
            
            # Build response content (same format as agent_startup)
            response_lines = [
                f"# Agent Startup {status_text}",
                "",
                "## Agent Identity",
                f"- **Agent ID:** `{agent_id}`",
                f"- **Role:** `{agent_role}`",
                f"- **Initialization Time:** {datetime.now().isoformat()}",
                "",
                "## Initialization Results"
            ]
            
            # Add success messages
            if initialization_messages:
                response_lines.extend(initialization_messages)
            
            # Add error messages
            if errors:
                response_lines.append("")
                response_lines.append("### Errors:")
                response_lines.extend(errors)
            
            # Calculate policy hash display
            policy_hash_display = (
                policy_hash[:12] + '...' if policy_hash
                else 'Not available'
            )
            
            response_lines.extend([
                "",
                "## Configuration",
                f"- **Memory Layers:** {', '.join(memory_layers)}",
                f"- **Policy Version:** `{policy_version}`",
                f"- **Policy Hash:** `{policy_hash_display}`",
                "",
                f"{status_icon} Agent initialization {status_text.lower()}",
                system_info
            ])
            
            prompt_content = "\n".join(response_lines)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": prompt_content
                    }
                ],
                "metadata": {
                    "agent_id": agent_id,
                    "agent_role": agent_role,
                    "memory_layers": memory_layers,
                    "policy_version": policy_version,
                    "policy_hash": policy_hash,
                    "initialization_success": len(errors) == 0,
                    "errors": errors
                },
                "isError": len(errors) > 0
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced initialize_new_agent: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error initializing agent: {str(e)}"}
                ]
            }

    async def handle_initialize_development_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a development agent with developer-optimized defaults."""
        dev_arguments = {
            "agent_id": arguments.get("agent_id"),
            "agent_role": "developer",
            "memory_layers": ["global", "learned", "agent"],
            "policy_version": "latest",
            "load_policies": True
        }
        return await self.handle_initialize_new_agent(dev_arguments)

    async def handle_initialize_testing_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a testing agent with testing-optimized defaults."""
        test_arguments = {
            "agent_id": arguments.get("agent_id"),
            "agent_role": "tester",
            "memory_layers": ["global", "learned"],
            "policy_version": "latest",
            "load_policies": True
        }
        return await self.handle_initialize_new_agent(test_arguments)

    async def handle_configure_agent_permissions(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure agent permissions for memory layer access."""
        try:
            agent_id = arguments.get("agent_id")
            permissions = arguments.get("permissions", {})
            
            if not agent_id:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id is required"}
                    ]
                }

            # Update agent permissions
            result = await self.memory_manager.update_agent_permissions(
                agent_id=agent_id,
                permissions=permissions
            )

            if result["success"]:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"✅ Permissions updated for agent '{agent_id}'"
                                f"\nRead access: {permissions.get('can_read', [])}"
                                f"\nWrite access: {permissions.get('can_write', [])}"
                                f"\nAdmin access: {permissions.get('can_admin', [])}"
                            )
                        }
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error configuring agent permissions: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error configuring permissions: {str(e)}"
                    }
                ]
            }

    async def handle_query_memory_for_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query memory for an agent with permission-based access control."""
        try:
            agent_id = arguments.get("agent_id")
            query = arguments.get("query")
            memory_layers = arguments.get("memory_layers", ["global", "learned"])
            limit = arguments.get("limit", 10)
            
            if not agent_id or not query:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id and query are required"}
                    ]
                }

            # Check agent permissions for each memory layer
            allowed_layers = []
            for memory_type in memory_layers:
                has_permission = await self.memory_manager.check_agent_permission(
                    agent_id=agent_id,
                    action="read",
                    memory_type=memory_type
                )
                if has_permission:
                    allowed_layers.append(memory_type)

            if not allowed_layers:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Agent {agent_id} has no read permissions "
                                f"for requested memory layers"
                            )
                        }
                    ]
                }

            # Query memory with allowed layers
            result = await self.memory_manager.query_memory(
                query=query,
                memory_types=allowed_layers,
                limit=limit,
                agent_id=agent_id
            )

            if result["success"]:
                results_text = []
                for i, memory_result in enumerate(result["results"], 1):
                    results_text.append(
                        f"**Result {i}** (Score: {memory_result['score']:.3f}, "
                        f"Type: {memory_result['memory_type']})\n"
                        f"{memory_result['content']}\n"
                    )
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"🔍 Found {len(result['results'])} results "
                                f"for agent '{agent_id}'"
                                f"\nAllowed memory layers: "
                                f"{', '.join(allowed_layers)}\n\n"
                                + "\n".join(results_text)
                            )
                        }
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Query failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error querying memory for agent: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error querying memory: {str(e)}"
                    }
                ]
            }

    async def handle_store_agent_action(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store an agent action with optional learned memory integration."""
        try:
            agent_id = arguments.get("agent_id")
            action = arguments.get("action")
            context = arguments.get("context", {})
            outcome = arguments.get("outcome")
            learn = arguments.get("learn", False)
            
            if not agent_id or not action or not outcome:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": "agent_id, action, and outcome are required"
                        }
                    ]
                }

            # Log the action
            result = await self.memory_manager.log_agent_action(
                agent_id=agent_id,
                action=action,
                context=context,
                outcome=outcome,
                store_as_learned=learn
            )

            if result["success"]:
                response_text = (
                    f"✅ Action logged for agent '{agent_id}'"
                    f"\nAction: {action}"
                    f"\nOutcome: {outcome}"
                )
                
                if result["stored_as_learned"]:
                    response_text += (
                        "\n📚 Stored as learned memory for future reference"
                    )
                
                return {
                    "content": [
                        {"type": "text", "text": response_text}
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error storing agent action: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error storing action: {str(e)}"
                    }
                ]
            }