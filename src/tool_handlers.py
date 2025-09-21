"""
Tool implementation handlers for MCP Memory Server.
Contains the actual logic for each tool, separated from MCP protocol handling.
"""

from typing import Dict, Any

from .server_config import get_logger

logger = get_logger("tool-handlers")


class ToolHandlers:
    """Handles the implementation of all memory management tools."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager instance."""
        self.memory_manager = memory_manager
    
    def handle_set_agent_context(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle set_agent_context tool call."""
        agent_id = arguments.get("agent_id")
        context_type = arguments.get("context_type")
        description = arguments.get("description")
        
        self.memory_manager.set_agent_context(
            agent_id, context_type, description
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Agent context set for {agent_id}: {description}"
                }
            ]
        }

    def handle_add_to_global_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_global_memory tool call."""
        content = arguments.get("content")
        category = arguments.get("category", "general")
        importance = arguments.get("importance", 0.5)
        
        result = self.memory_manager.add_to_global_memory(
            content, category, importance
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Added to global memory: {result['message']}"
                }
            ]
        }

    def handle_add_to_learned_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_learned_memory tool call."""
        content = arguments.get("content")
        pattern_type = arguments.get("pattern_type", "insight")
        confidence = arguments.get("confidence", 0.7)
        
        result = self.memory_manager.add_to_learned_memory(
            content, pattern_type, confidence
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Added to learned memory: {result['message']}"
                }
            ]
        }

    def handle_add_to_agent_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_agent_memory tool call."""
        content = arguments.get("content")
        agent_id = arguments.get("agent_id")
        memory_type = arguments.get("memory_type", "general")
        
        result = self.memory_manager.add_to_agent_memory(
            content, agent_id, memory_type
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Added to agent memory: {result['message']}"
                }
            ]
        }

    def handle_query_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query_memory tool call."""
        query = arguments.get("query")
        memory_types = arguments.get(
            "memory_types", ["global", "learned", "agent"]
        )
        limit = arguments.get("limit", 10)
        min_score = arguments.get("min_score", 0.3)
        
        results = self.memory_manager.query_memory(
            query, memory_types, limit, min_score
        )
        
        if results.get("success", False):
            memories = results.get("memories", [])
            response_text = (
                f"Found {len(memories)} relevant memories:\n\n"
            )
            
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', 'No content')
                score = memory.get('score', 0)
                mem_type = memory.get('memory_type', 'unknown')
                response_text += (
                    f"{i}. {content} "
                    f"(Score: {score:.3f}, Type: {mem_type})\n\n"
                )
        else:
            error_msg = results.get('error', 'Unknown error')
            response_text = f"Query failed: {error_msg}"
        
        return {
            "content": [{"type": "text", "text": response_text}]
        }

    def handle_compare_against_learned_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle compare_against_learned_memory tool call."""
        situation = arguments.get("situation")
        comparison_type = arguments.get("comparison_type", "pattern_match")
        limit = arguments.get("limit", 5)
        
        results = self.memory_manager.compare_against_learned_memory(
            situation, comparison_type, limit
        )
        
        if results.get("success", False):
            patterns = results.get("patterns", [])
            response_text = (
                f"Found {len(patterns)} similar learned patterns:\n\n"
            )
            
            for i, pattern in enumerate(patterns, 1):
                content = pattern.get('content', 'No content')
                score = pattern.get('score', 0)
                response_text += (
                    f"{i}. {content} "
                    f"(Similarity: {score:.3f})\n\n"
                )
        else:
            error_msg = results.get('error', 'Unknown error')
            response_text = f"Comparison failed: {error_msg}"
        
        return {
            "content": [{"type": "text", "text": response_text}]
        }
        
    def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers."""
        if not self.memory_manager:
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": "Memory manager not available"}
                ]
            }

        try:
            # Route to appropriate handler
            handler_map = {
                "set_agent_context": self.handle_set_agent_context,
                "add_to_global_memory": self.handle_add_to_global_memory,
                "add_to_learned_memory": self.handle_add_to_learned_memory,
                "add_to_agent_memory": self.handle_add_to_agent_memory,
                "query_memory": self.handle_query_memory,
                "compare_against_learned_memory": (
                    self.handle_compare_against_learned_memory
                ),
            }
            
            if tool_name in handler_map:
                return handler_map[tool_name](arguments)
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Unknown tool: {tool_name}"}
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
