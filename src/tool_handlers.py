"""
Tool implementation handlers for MCP Memory Server.
Contains the actual logic for each tool, separated from MCP protocol handling.
"""

from typing import Dict, Any
import asyncio

from .server_config import get_logger
from .markdown_processor import MarkdownProcessor

logger = get_logger("tool-handlers")


class ToolHandlers:
    """Handles the implementation of all memory management tools."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager instance."""
        self.memory_manager = memory_manager
        self.markdown_processor = MarkdownProcessor()
    
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

    # New Markdown Processing Tools

    async def handle_scan_workspace_markdown(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle scan_workspace_markdown tool call."""
        try:
            directory = arguments.get("directory", "./")
            recursive = arguments.get("recursive", True)
            
            files = await self.markdown_processor.scan_directory_for_markdown(
                directory, recursive
            )
            
            response_text = (
                f"Found {len(files)} markdown files in {directory}"
                + (" (recursive)" if recursive else "") + ":\n\n"
            )
            
            for file_info in files:
                response_text += (
                    f"• {file_info['name']} "
                    f"({file_info['size']} bytes) - {file_info['relative_path']}\n"
                )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in scan_workspace_markdown: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to scan directory: {str(e)}"}
                ]
            }

    async def handle_analyze_markdown_content(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle analyze_markdown_content tool call."""
        try:
            content = arguments.get("content", "")
            if not content:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Content parameter is required"}
                    ]
                }
            
            suggest_memory_type = arguments.get("suggest_memory_type", True)
            ai_enhance = arguments.get("ai_enhance", True)
            
            analysis = self.markdown_processor.analyze_content_for_memory_type(
                content, None, suggest_memory_type
            )
            
            response_text = (
                f"Content Analysis Results:\n\n"
                f"• Length: {analysis['content_length']} characters\n"
                f"• Words: {analysis['word_count']}\n"
                f"• Sections: {analysis['sections']}\n"
                f"• Has code blocks: {analysis['has_code_blocks']}\n"
                f"• Has links: {analysis['has_links']}\n"
                f"• Has tables: {analysis['has_tables']}\n"
            )
            
            if suggest_memory_type:
                response_text += (
                    f"\nMemory Type Suggestion:\n"
                    f"• Type: {analysis['suggested_memory_type']}\n"
                    f"• Confidence: {analysis['confidence']:.2f}\n"
                    f"• Reasoning: {analysis['reasoning']}\n"
                )
            
            if ai_enhance:
                response_text += (
                    f"\nAI Enhancement: Ready for Cursor AI integration"
                )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_markdown_content: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to analyze content: {str(e)}"}
                ]
            }

    async def handle_optimize_content_for_storage(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle optimize_content_for_storage tool call."""
        try:
            content = arguments.get("content", "")
            memory_type = arguments.get("memory_type", "global")
            ai_optimization = arguments.get("ai_optimization", True)
            suggested_type = arguments.get("suggested_type")
            
            if not content:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Content parameter is required"}
                    ]
                }
            
            optimization = self.markdown_processor.optimize_content_for_storage(
                content, memory_type, ai_optimization, suggested_type
            )
            
            response_text = (
                f"Content Optimization Results:\n\n"
                f"• Target memory type: {optimization['memory_type']}\n"
                f"• Original length: {optimization['original_length']}\n"
                f"• Optimized length: {optimization['optimized_length']}\n"
                f"• Optimization applied: {optimization['optimization_applied']}\n"
                f"• AI enhanced: {optimization['ai_enhanced']}\n"
            )
            
            if optimization.get('suggested_type_override'):
                response_text += (
                    f"• Note: User override of suggested type\n"
                )
            
            response_text += (
                f"\nOptimized content ready for storage in "
                f"{memory_type} memory layer."
            )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in optimize_content_for_storage: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to optimize content: {str(e)}"}
                ]
            }

    async def handle_process_markdown_directory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle process_markdown_directory tool call."""
        try:
            directory = arguments.get("directory", "./")
            memory_type = arguments.get("memory_type")
            auto_suggest = arguments.get("auto_suggest", True)
            ai_enhance = arguments.get("ai_enhance", True)
            recursive = arguments.get("recursive", True)
            
            results = await self.markdown_processor.process_directory_batch(
                directory, memory_type, auto_suggest, ai_enhance, recursive
            )
            
            total_files = results['total_files']
            processed = len(results['processed_files'])
            failed = len(results['failed_files'])
            suggestions = results['memory_type_suggestions']
            
            response_text = (
                f"Directory Processing Results:\n\n"
                f"• Directory: {directory}\n"
                f"• Total files found: {total_files}\n"
                f"• Successfully processed: {processed}\n"
                f"• Failed: {failed}\n"
                f"• AI enhanced: {ai_enhance}\n\n"
            )
            
            if suggestions:
                response_text += "Memory Type Suggestions:\n"
                for mem_type, count in suggestions.items():
                    response_text += f"• {mem_type}: {count} files\n"
                response_text += "\n"
            
            if results['processed_files']:
                response_text += "Processed Files:\n"
                for file_result in results['processed_files'][:10]:  # Show first 10
                    response_text += (
                        f"• {file_result['name']} → "
                        f"{file_result['final_memory_type']}\n"
                    )
                if len(results['processed_files']) > 10:
                    response_text += f"• ... and {len(results['processed_files']) - 10} more\n"
            
            if results['failed_files']:
                response_text += "\nFailed Files:\n"
                for failed_file in results['failed_files']:
                    response_text += f"• {failed_file['name']}: {failed_file['error']}\n"
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in process_markdown_directory: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to process directory: {str(e)}"}
                ]
            }
        
    async def handle_tool_call(
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
                # New markdown processing tools
                "scan_workspace_markdown": self.handle_scan_workspace_markdown,
                "analyze_markdown_content": self.handle_analyze_markdown_content,
                "optimize_content_for_storage": self.handle_optimize_content_for_storage,
                "process_markdown_directory": self.handle_process_markdown_directory,
            }
            
            if tool_name in handler_map:
                handler = handler_map[tool_name]
                # Handle both sync and async methods
                if asyncio.iscoroutinefunction(handler):
                    return await handler(arguments)
                else:
                    return handler(arguments)
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
