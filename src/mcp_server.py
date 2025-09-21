"""
MCP (Model Context Protocol) server implementation for memory management.
Handles the MCP protocol communication and tool orchestration.
"""

import json
import sys
from typing import Dict, Any, List, Optional

from .server_config import get_logger, MCP_PROTOCOL_VERSION, MCP_SERVER_INFO
from .qdrant_manager import ensure_qdrant_running
from .tool_handlers import ToolHandlers

logger = get_logger("mcp-server")

# Import our memory manager
try:
    from .memory_manager import QdrantMemoryManager
    MEMORY_AVAILABLE = True
    logger.info("Memory manager available")
except ImportError as e:
    MEMORY_AVAILABLE = False
    logger.error(f"Memory manager not available: {e}")


class MemoryMCPServer:
    """MCP Server focused solely on memory management using Qdrant."""
    
    def __init__(self):
        logger.info("Starting Memory MCP Server...")
        
        # Ensure Qdrant is running before initializing memory manager
        if not ensure_qdrant_running():
            logger.error(
                "❌ Failed to start Qdrant. "
                "Memory server will not function properly."
            )
        
        if MEMORY_AVAILABLE:
            try:
                self.memory_manager = QdrantMemoryManager()
                logger.info("Memory manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize memory manager: {e}")
                self.memory_manager = None
        else:
            self.memory_manager = None
        
        # Initialize tool handlers
        self.tool_handlers = ToolHandlers(self.memory_manager)
        
        logger.info("Memory MCP Server initialized")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available memory management tools."""
        if not self.memory_manager:
            return []
            
        return [
            {
                "name": "set_agent_context",
                "description": (
                    "Set the current agent's context for memory operations"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Unique identifier for the agent"
                        },
                        "context_type": {
                            "type": "string",
                            "description": (
                                "Type of context "
                                "(e.g., 'task', 'conversation', 'project')"
                            )
                        },
                        "description": {
                            "type": "string",
                            "description": (
                                "Human-readable description of the context"
                            )
                        }
                    },
                    "required": ["agent_id", "context_type", "description"]
                }
            },
            {
                "name": "add_to_global_memory",
                "description": (
                    "Add information to global memory accessible by all agents"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": (
                                "Information to store in global memory"
                            )
                        },
                        "category": {
                            "type": "string",
                            "description": (
                                "Category for organizing the memory (optional)"
                            )
                        },
                        "importance": {
                            "type": "number",
                            "description": (
                                "Importance score 0.0-1.0 "
                                "(optional, default 0.5)"
                            )
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "add_to_learned_memory",
                "description": (
                    "Add learned patterns or insights that should be "
                    "remembered for future tasks"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": (
                                "Learned insight or pattern to remember"
                            )
                        },
                        "pattern_type": {
                            "type": "string",
                            "description": "Type of pattern learned (optional)"
                        },
                        "confidence": {
                            "type": "number",
                            "description": (
                                "Confidence in this learning 0.0-1.0 "
                                "(optional, default 0.7)"
                            )
                        }
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
                        "content": {
                            "type": "string",
                            "description": (
                                "Information to store in agent's memory"
                            )
                        },
                        "agent_id": {
                            "type": "string",
                            "description": (
                                "Agent ID "
                                "(optional, uses current context "
                                "if not provided)"
                            )
                        },
                        "memory_type": {
                            "type": "string",
                            "description": "Type of memory (optional)"
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "query_memory",
                "description": (
                    "Search and retrieve relevant information from memory"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Search query to find relevant memories"
                            )
                        },
                        "memory_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Types of memory to search "
                                "(optional, searches all by default)"
                            )
                        },
                        "limit": {
                            "type": "number",
                            "description": (
                                "Maximum number of results "
                                "(optional, default 10)"
                            )
                        },
                        "min_score": {
                            "type": "number",
                            "description": (
                                "Minimum similarity score 0.0-1.0 "
                                "(optional, default 0.3)"
                            )
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "compare_against_learned_memory",
                "description": (
                    "Compare current situation against "
                    "learned patterns and insights"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": (
                                "Current situation or context to compare"
                            )
                        },
                        "comparison_type": {
                            "type": "string",
                            "description": "Type of comparison (optional)"
                        },
                        "limit": {
                            "type": "number",
                            "description": (
                                "Maximum number of similar patterns to return "
                                "(optional, default 5)"
                            )
                        }
                    },
                    "required": ["situation"]
                }
            }
        ]

    def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a tool call and return the result."""
        return self.tool_handlers.handle_tool_call(tool_name, arguments)


def send_response(
    request_id: Optional[str],
    result: Dict[str, Any] = None,
    error: Dict[str, Any] = None
):
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


def run_mcp_server():
    """Main server loop for MCP protocol handling."""
    logger.info("Memory MCP Server ready, waiting for connections...")
    
    # Create server instance
    server = MemoryMCPServer()
    
    # MCP initialization response
    init_response = {
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "capabilities": {
            "tools": {
                "listChanged": False
            }
        },
        "serverInfo": MCP_SERVER_INFO
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
                send_response(
                    request_id,
                    error={"code": -32603, "message": str(e)}
                )
