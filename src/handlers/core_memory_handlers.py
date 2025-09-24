"""
Core memory operation handlers for MCP Memory Server.
Handles fundamental memory operations across global, learned, and agent memory layers.
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

logger = get_logger("core-memory-handlers")


class CoreMemoryHandlers:
    """Handles core memory operations for all memory layers."""
    
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
        
        if result.get("success"):
            message = result.get("message", "Content added successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Added to global memory: {message}"
                    }
                ]
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to add to global memory: {error}"
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
        
        if result.get("success"):
            message = result.get("message", "Pattern added successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Added to learned memory: {message}"
                    }
                ]
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to add to learned memory: {error}"
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
        
        if result.get("success"):
            message = result.get("message", "Content added successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Added to agent memory: {message}"
                    }
                ]
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to add to agent memory: {error}"
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
        
        # Add debugging information
        logger.info(
            f"🔍 Query: '{query}', Types: {memory_types}, "
            f"Limit: {limit}, Min score: {min_score}"
        )
        
        results = self.memory_manager.query_memory(
            query, memory_types, limit, min_score
        )
        
        logger.info(
            f"📊 Query results: success={results.get('success')}, "
            f"total_results={results.get('total_results', 0)}"
        )
        
        if results.get("success", False):
            memories = results.get("results", [])
            response_text = (
                f"Found {len(memories)} relevant memories:\n\n"
            )
            
            if len(memories) == 0:
                response_text += "🔍 **Search Help:**\n"
                response_text += "- Try broader terms or lower min_score\n"
                response_text += "- Check memory_types parameter\n"
                response_text += "- Use different keywords\n\n"
                response_text += "💡 **Query Tips:**\n"
                response_text += f"- Current query: '{query}'\n"
                response_text += f"- Memory types searched: {memory_types}\n"
                response_text += f"- Minimum score: {min_score}\n"
                response_text += f"- Result limit: {limit}\n\n"
                response_text += "Try adjusting these parameters or using different search terms."
            else:
                for i, memory in enumerate(memories, 1):
                    score = memory.get('score', 0)
                    content = memory.get('content', 'No content')
                    memory_type = memory.get('memory_type', 'unknown')
                    category = memory.get('category', 'general')
                    
                    response_text += f"**{i}. [{memory_type.title()}] {category.title()}** (Score: {score:.3f})\n"
                    response_text += f"{content[:200]}{'...' if len(content) > 200 else ''}\n\n"
                
        else:
            error_msg = results.get('error', 'Unknown error')
            response_text = f"Query failed: {error_msg}\n\n"
            response_text += "🔧 Debug Info:\n"
            response_text += f"- Query: '{query}'\n"
            response_text += f"- Memory types: {memory_types}\n"
            response_text += f"- Error details: {error_msg}\n"
        
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
            patterns = results.get("results", [])
            response_text = (
                f"Found {len(patterns)} similar learned patterns:\n\n"
            )
            
            for i, pattern in enumerate(patterns, 1):
                score = pattern.get('score', 0)
                content = pattern.get('content', 'No content')
                pattern_type = pattern.get('pattern_type', 'unknown')
                confidence = pattern.get('confidence', 0)
                
                response_text += f"**{i}. {pattern_type.title()}** (Score: {score:.3f}, Confidence: {confidence:.2f})\n"
                response_text += f"{content[:150]}{'...' if len(content) > 150 else ''}\n\n"
                
        else:
            error_msg = results.get('error', 'Unknown error')
            response_text = f"Comparison failed: {error_msg}"
        
        return {
            "content": [{"type": "text", "text": response_text}]
        }