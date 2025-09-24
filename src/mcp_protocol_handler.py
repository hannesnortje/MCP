"""
MCP Protocol Handler for Memory Server.
Handles the Model Context Protocol message processing and communication.
"""

import json
import sys
import asyncio
from typing import Dict, Any, Optional

try:
    from .server_config import get_logger, MCP_PROTOCOL_VERSION, MCP_SERVER_INFO
except ImportError:
    from server_config import get_logger, MCP_PROTOCOL_VERSION, MCP_SERVER_INFO

logger = get_logger("mcp-protocol")


class MCPProtocolHandler:
    """Handles MCP protocol communication and message routing."""
    
    def __init__(self, server_instance):
        """Initialize with a server instance to delegate to."""
        self.server = server_instance
    
    @staticmethod
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

    @staticmethod
    def send_notification(method: str, params: Dict[str, Any] = None):
        """Send a notification to the MCP client."""
        notification = {"jsonrpc": "2.0", "method": method}
        
        if params:
            notification["params"] = params
        
        print(json.dumps(notification), flush=True)

    def get_init_response(self) -> Dict[str, Any]:
        """Build MCP initialization response based on server mode."""
        capabilities = {}
        
        # Always include tools (unless prompts-only mode)
        if self.server.server_mode != "prompts-only":
            capabilities["tools"] = {"listChanged": False}
        
        # Always include resources (unless prompts-only mode)
        if self.server.server_mode != "prompts-only":
            capabilities["resources"] = {"subscribe": False, "listChanged": False}
        
        # Include prompts only in full and prompts-only modes
        if self.server.server_mode in ["full", "prompts-only"]:
            capabilities["prompts"] = {"listChanged": False}
        
        return {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": capabilities,
            "serverInfo": MCP_SERVER_INFO
        }

    async def handle_message(self, data: Dict[str, Any]) -> None:
        """Handle a single MCP protocol message."""
        method = data.get("method")
        request_id = data.get("id")
        
        try:
            if method == "initialize":
                init_response = self.get_init_response()
                self.send_response(request_id, init_response)
                logger.info("Memory server initialization response sent")
                
            elif method == "notifications/initialized":
                logger.info("Memory server initialized successfully")
                
            elif method == "tools/list":
                tools_response = {"tools": self.server.get_available_tools()}
                self.send_response(request_id, tools_response)
                
            elif method == "resources/list":
                resources = self.server.get_available_resources()
                resources_response = {"resources": resources}
                self.send_response(request_id, resources_response)
                
            elif method == "resources/read":
                uri = data.get("params", {}).get("uri")
                if not uri:
                    error_response = {
                        "error": {
                            "code": -32602,
                            "message": "URI parameter required"
                        }
                    }
                    self.send_response(request_id, error_response)
                else:
                    params = data.get("params", {})
                    # Remove uri from params to avoid duplicate
                    params_clean = {k: v for k, v in params.items() if k != 'uri'}
                    result = await self.server.handle_resource_read(uri, params_clean)
                    self.send_response(request_id, result)
                
            elif method == "prompts/list":
                prompts = self.server.get_available_prompts()
                prompts_response = {"prompts": prompts}
                self.send_response(request_id, prompts_response)
                
            elif method == "prompts/get":
                name = data.get("params", {}).get("name")
                if not name:
                    error_response = {
                        "error": {
                            "code": -32602,
                            "message": "Prompt name parameter required"
                        }
                    }
                    self.send_response(request_id, error_response)
                else:
                    arguments = data.get("params", {}).get("arguments", {})
                    result = await self.server.handle_prompt_get(name, arguments)
                    self.send_response(request_id, result)
                
            elif method == "tools/call":
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                result = await self.server.handle_tool_call(tool_name, arguments)
                self.send_response(request_id, result)
                
            else:
                logger.info(f"Unhandled method: {method}")
                
        except Exception as e:
            logger.error(f"Error handling method {method}: {e}")
            if request_id:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                self.send_response(request_id, error_response)

    async def run_protocol_loop(self) -> None:
        """Main server loop for MCP protocol handling."""
        logger.info("Memory MCP Server ready, waiting for connections...")
        
        # Process MCP protocol messages
        for line in sys.stdin:
            try:
                data = json.loads(line.strip())
                logger.info(f"Received: {data}")
                
                await self.handle_message(data)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {line} - {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")