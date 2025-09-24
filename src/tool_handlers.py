"""
Main tool router for MCP Memory Server.
Lightweight router that delegates to specialized handler modules.
"""

from typing import Dict, Any
import asyncio

try:
    from .server_config import get_logger
    from .handlers.core_memory_handlers import CoreMemoryHandlers
    from .handlers.markdown_processing_handlers import (
        MarkdownProcessingHandlers
    )
    from .handlers.agent_management_handlers import AgentManagementHandlers
    from .handlers.policy_and_guidance_handlers import (
        PolicyAndGuidanceHandlers
    )
    from .handlers.system_and_collections_handlers import (
        SystemAndCollectionsHandlers
    )
    from .markdown_processor import MarkdownProcessor
    from .policy_processor import PolicyProcessor
    from .error_handler import error_handler
except ImportError:
    # Fallback for standalone usage
    import logging

    def get_logger(name: str):
        return logging.getLogger(name)
    
    class MockHandler:
        def __init__(self, *args, **kwargs):
            pass

        async def handle_tool_call(self, tool_name, arguments):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Handler not available for {tool_name}"
                    }
                ]
            }
    
    CoreMemoryHandlers = MockHandler
    MarkdownProcessingHandlers = MockHandler
    AgentManagementHandlers = MockHandler
    PolicyAndGuidanceHandlers = MockHandler
    SystemAndCollectionsHandlers = MockHandler
    
    class MockProcessor:
        pass
    
    MarkdownProcessor = MockProcessor
    PolicyProcessor = MockProcessor
    
    class MockErrorHandler:
        def get_error_stats(self):
            return {"total_errors": 0}
    
    error_handler = MockErrorHandler()

logger = get_logger("tool-handlers-router")


class ToolHandlers:
    """Main tool handler router that delegates to specialized modules."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager instance."""
        self.memory_manager = memory_manager
        
        # Initialize processors
        self.markdown_processor = MarkdownProcessor()
        self.policy_processor = PolicyProcessor()
        
        # Initialize specialized handler modules
        self.core_memory_handlers = CoreMemoryHandlers(memory_manager)
        self.markdown_handlers = MarkdownProcessingHandlers(
            memory_manager, self.markdown_processor
        )
        self.agent_handlers = AgentManagementHandlers(memory_manager)
        self.policy_handlers = PolicyAndGuidanceHandlers(
            memory_manager, self.policy_processor
        )
        self.system_handlers = SystemAndCollectionsHandlers(
            memory_manager, self.markdown_processor
        )
    
    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route tool calls to appropriate specialized handlers."""
        if not self.memory_manager:
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": "Memory manager not available"}
                ]
            }

        try:
            # Route to appropriate handler based on tool category
            core_memory_tools = {
                "set_agent_context",
                "add_to_global_memory",
                "add_to_learned_memory",
                "add_to_agent_memory",
                "query_memory",
                "compare_against_learned_memory"
            }
            
            markdown_tools = {
                "scan_workspace_markdown",
                "analyze_markdown_content",
                "optimize_content_for_storage",
                "process_markdown_directory",
                "validate_and_deduplicate",
                "process_markdown_file",
                "batch_process_markdown_files",
                "batch_process_directory"
            }
            
            agent_tools = {
                "initialize_new_agent",
                "initialize_development_agent",
                "initialize_testing_agent",
                "configure_agent_permissions",
                "query_memory_for_agent",
                "store_agent_action"
            }
            
            policy_and_guidance_tools = {
                "build_policy_from_markdown",
                "get_policy_rulebook",
                "validate_json_against_schema",
                "log_policy_violation",
                "get_memory_usage_guidance",
                "get_context_preservation_guidance",
                "get_query_optimization_guidance",
                "get_markdown_optimization_guidance",
                "get_duplicate_detection_guidance",
                "get_directory_processing_guidance",
                "get_memory_type_selection_guidance",
                "get_memory_type_suggestion_guidance",
                "get_policy_compliance_guidance",
                "get_policy_violation_recovery_guidance"
            }
            
            system_and_collections_tools = {
                "system_health",
                "create_collection",
                "list_collections",
                "add_to_collection",
                "query_collection",
                "delete_collection",
                "get_collection_stats"
            }
            
            # Route to appropriate handler
            if tool_name in core_memory_tools:
                handler_method = getattr(
                    self.core_memory_handlers, f"handle_{tool_name}"
                )
            elif tool_name in markdown_tools:
                handler_method = getattr(
                    self.markdown_handlers, f"handle_{tool_name}"
                )
            elif tool_name in agent_tools:
                handler_method = getattr(
                    self.agent_handlers, f"handle_{tool_name}"
                )
            elif tool_name in policy_and_guidance_tools:
                handler_method = getattr(
                    self.policy_handlers, f"handle_{tool_name}"
                )
            elif tool_name in system_and_collections_tools:
                handler_method = getattr(
                    self.system_handlers, f"handle_{tool_name}"
                )
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Unknown tool: {tool_name}"}
                    ]
                }
            
            # Handle both sync and async methods
            if asyncio.iscoroutinefunction(handler_method):
                return await handler_method(arguments)
            else:
                return handler_method(arguments)

        except AttributeError as e:
            logger.error(f"Handler method not found for {tool_name}: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Handler method not found for "
                            f"{tool_name}: {str(e)}"
                        )
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing {tool_name}: {str(e)}"
                    }
                ]
            }

    # Legacy method compatibility - delegate to specialized handlers
    def handle_set_agent_context(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.core_memory_handlers.handle_set_agent_context(arguments)

    def handle_add_to_global_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.core_memory_handlers.handle_add_to_global_memory(arguments)

    def handle_add_to_learned_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return (
            self.core_memory_handlers.handle_add_to_learned_memory(arguments)
        )

    def handle_add_to_agent_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.core_memory_handlers.handle_add_to_agent_memory(arguments)

    def handle_query_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.core_memory_handlers.handle_query_memory(arguments)

    def handle_compare_against_learned_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return (
            self.core_memory_handlers
            .handle_compare_against_learned_memory(arguments)
        )

    def handle_system_health(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.system_handlers.handle_system_health(arguments)
