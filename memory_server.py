#!/usr/bin/env python3
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("memory-mcp-server")

# Import our memory manager
try:
    from src.memory_manager import QdrantMemoryManager
    MEMORY_AVAILABLE = True
    logger.info("Memory manager available")
except ImportError as e:
    MEMORY_AVAILABLE = False
    logger.error(f"Memory manager not available: {e}")
    sys.exit(1)


class MemoryMCPServer:
    """MCP Server focused solely on memory management using Qdrant."""
    
    def __init__(self):
        logger.info("Starting Memory MCP Server...")
        
        if MEMORY_AVAILABLE:
            try:
                self.memory_manager = QdrantMemoryManager()
                logger.info("Memory manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize memory manager: {e}")
                self.memory_manager = None
        else:
            self.memory_manager = None
        
        logger.info("Memory MCP Server initialized")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available memory management tools."""
        if not self.memory_manager:
            return []
            
        return [
            {
                "name": "set_agent_context",
                "description": "Set the current agent's context for memory operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Unique identifier for the agent"},
                        "context_type": {"type": "string", "description": "Type of context (e.g., 'task', 'conversation', 'project')"},
                        "description": {"type": "string", "description": "Human-readable description of the context"}
                    },
                    "required": ["agent_id", "context_type", "description"]
                }
            },
            {
                "name": "add_to_global_memory",
                "description": "Add information to global memory accessible by all agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Information to store in global memory"},
                        "category": {"type": "string", "description": "Category for organizing the memory (optional)"},
                        "importance": {"type": "number", "description": "Importance score 0.0-1.0 (optional, default 0.5)"}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "add_to_learned_memory",
                "description": "Add learned patterns or insights that should be remembered for future tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Learned insight or pattern to remember"},
                        "pattern_type": {"type": "string", "description": "Type of pattern learned (optional)"},
                        "confidence": {"type": "number", "description": "Confidence in this learning 0.0-1.0 (optional, default 0.7)"}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "add_to_agent_memory",
                "description": "Add information to specific agent's memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Information to store in agent's memory"},
                        "agent_id": {"type": "string", "description": "Agent ID (optional, uses current context if not provided)"},
                        "memory_type": {"type": "string", "description": "Type of memory (optional)"}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "query_memory",
                "description": "Search and retrieve relevant information from memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query to find relevant memories"},
                        "memory_types": {"type": "array", "items": {"type": "string"}, "description": "Types of memory to search (optional, searches all by default)"},
                        "limit": {"type": "number", "description": "Maximum number of results (optional, default 10)"},
                        "min_score": {"type": "number", "description": "Minimum similarity score 0.0-1.0 (optional, default 0.3)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "compare_against_learned_memory",
                "description": "Compare current situation against learned patterns and insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "situation": {"type": "string", "description": "Current situation or context to compare"},
                        "comparison_type": {"type": "string", "description": "Type of comparison (optional)"},
                        "limit": {"type": "number", "description": "Maximum number of similar patterns to return (optional, default 5)"}
                    },
                    "required": ["situation"]
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call and return the result."""
        if not self.memory_manager:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Memory manager not available"}]
            }

        try:
            if tool_name == "set_agent_context":
                agent_id = arguments.get("agent_id")
                context_type = arguments.get("context_type")
                description = arguments.get("description")
                
                self.memory_manager.set_agent_context(agent_id, context_type, description)
                
                return {
                    "content": [{"type": "text", "text": f"Agent context set for {agent_id}: {description}"}]
                }

            elif tool_name == "add_to_global_memory":
                content = arguments.get("content")
                category = arguments.get("category", "general")
                importance = arguments.get("importance", 0.5)
                
                result = self.memory_manager.add_to_global_memory(content, category, importance)
                
                return {
                    "content": [{"type": "text", "text": f"Added to global memory: {result['message']}"}]
                }

            elif tool_name == "add_to_learned_memory":
                content = arguments.get("content")
                pattern_type = arguments.get("pattern_type", "insight")
                confidence = arguments.get("confidence", 0.7)
                
                result = self.memory_manager.add_to_learned_memory(content, pattern_type, confidence)
                
                return {
                    "content": [{"type": "text", "text": f"Added to learned memory: {result['message']}"}]
                }

            elif tool_name == "add_to_agent_memory":
                content = arguments.get("content")
                agent_id = arguments.get("agent_id")
                memory_type = arguments.get("memory_type", "general")
                
                result = self.memory_manager.add_to_agent_memory(content, agent_id, memory_type)
                
                return {
                    "content": [{"type": "text", "text": f"Added to agent memory: {result['message']}"}]
                }

            elif tool_name == "query_memory":
                query = arguments.get("query")
                memory_types = arguments.get("memory_types", ["global", "learned", "agent"])
                limit = arguments.get("limit", 10)
                min_score = arguments.get("min_score", 0.3)
                
                results = self.memory_manager.query_memory(query, memory_types, limit, min_score)
                
                if results.get("success", False):
                    memories = results.get("memories", [])
                    response_text = f"Found {len(memories)} relevant memories:\n\n"
                    
                    for i, memory in enumerate(memories, 1):
                        response_text += f"{i}. {memory.get('content', 'No content')} "
                        response_text += f"(Score: {memory.get('score', 0):.3f}, "
                        response_text += f"Type: {memory.get('memory_type', 'unknown')})\n\n"
                else:
                    response_text = f"Query failed: {results.get('error', 'Unknown error')}"
                
                return {
                    "content": [{"type": "text", "text": response_text}]
                }

            elif tool_name == "compare_against_learned_memory":
                situation = arguments.get("situation")
                comparison_type = arguments.get("comparison_type", "pattern_match")
                limit = arguments.get("limit", 5)
                
                results = self.memory_manager.compare_against_learned_memory(situation, comparison_type, limit)
                
                if results.get("success", False):
                    patterns = results.get("patterns", [])
                    response_text = f"Found {len(patterns)} similar learned patterns:\n\n"
                    
                    for i, pattern in enumerate(patterns, 1):
                        response_text += f"{i}. {pattern.get('content', 'No content')} "
                        response_text += f"(Similarity: {pattern.get('score', 0):.3f})\n\n"
                else:
                    response_text = f"Comparison failed: {results.get('error', 'Unknown error')}"
                
                return {
                    "content": [{"type": "text", "text": response_text}]
                }

            else:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
                }

        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Error executing {tool_name}: {str(e)}"}]
            }


def send_response(request_id: Optional[str], result: Dict[str, Any] = None, error: Dict[str, Any] = None):
    """Send a response back to the MCP client."""
    response = {"jsonrpc": "2.0", "id": request_id}
    
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    print(json.dumps(response), flush=True)


def send_notification(method: str, params: Dict[str, Any] = None):
    """Send a notification to the MCP client."""
    notification = {"jsonrpc": "2.0", "method": method}
    
    if params:
        notification["params"] = params
    
    print(json.dumps(notification), flush=True)


def main():
    """Main server loop."""
    logger.info("Memory MCP Server ready, waiting for connections...")
    
    # Create server instance
    server = MemoryMCPServer()
    
    # MCP initialization response
    init_response = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": False
            }
        },
        "serverInfo": {
            "name": "memory-server",
            "version": "1.0.0",
            "description": "Memory management server for AI agents using Qdrant vector database"
        }
    }
    
    # Process MCP protocol messages
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                send_response(request_id, init_response)
                send_notification("initialized")
                logger.info("Memory server initialized successfully")
                
            elif method == "tools/list":
                tools_response = {"tools": server.get_available_tools()}
                send_response(request_id, tools_response)
                
            elif method == "tools/call":
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                result = server.handle_tool_call(tool_name, arguments)
                send_response(request_id, result)
                
            else:
                logger.info(f"Unhandled method: {method}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {line} - {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            if 'request_id' in locals():
                send_response(request_id, error={"code": -32603, "message": str(e)})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Memory server interrupted")
    except EOFError:
        logger.info("Memory server disconnected")
    except Exception as e:
        logger.error(f"Memory server error: {e}")