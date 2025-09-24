"""
MCP Client Adapter for UI Communication

This module provides a bridge between the PySide6 UI and the MCP Memory Server
using subprocess communication with stdin/stdout JSON-RPC protocol.
"""

import json
import asyncio
import subprocess
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path


logger = logging.getLogger(__name__)


class MCPClientAdapter:
    """
    Handles MCP protocol communication for UI.
    
    This adapter manages a subprocess connection to the MCP Memory Server
    and provides convenient methods for common memory operations.
    """

    def __init__(self) -> None:
        self.server_process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self._initialized = False
        self.project_root = Path(__file__).parent.parent

    async def start_server(self, server_mode: str = "full") -> bool:
        """Start MCP server subprocess."""
        try:
            # Determine server mode arguments
            mode_args = []
            if server_mode == "tools-only":
                mode_args = ["--tools-only"]
            elif server_mode == "prompts-only":
                mode_args = ["--prompts-only"]

            # Use Poetry to run the server with proper environment
            cmd = ["poetry", "run", "python", "memory_server.py"] + mode_args

            logger.info(f"Starting MCP server: {' '.join(cmd)}")

            self.server_process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Give server time to start
            await asyncio.sleep(2)

            if self.server_process.poll() is None:
                self._initialized = True
                logger.info("✅ MCP server started successfully")
                return True
            else:
                logger.error("❌ MCP server failed to start")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            return False

    async def stop_server(self) -> None:
        """Stop the MCP server subprocess."""
        if self.server_process and self.server_process.poll() is None:
            logger.info("Stopping MCP server...")
            self.server_process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_task(
                        asyncio.to_thread(self.server_process.wait)
                    ),
                    timeout=10
                )
                logger.info("✅ MCP server stopped gracefully")
            except asyncio.TimeoutError:
                logger.warning("Force killing MCP server...")
                self.server_process.kill()
            
            self.server_process = None
            self._initialized = False

    async def call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an MCP tool and return the result."""
        if not self._initialized or not self.server_process:
            raise RuntimeError("MCP server not initialized")

        # Prepare the JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        self.request_id += 1

        try:
            # Send request to server stdin
            request_json = json.dumps(request) + '\n'
            if self.server_process.stdin:
                self.server_process.stdin.write(request_json)
                self.server_process.stdin.flush()

            # Read response from server stdout
            if self.server_process.stdout:
                response_line = self.server_process.stdout.readline()
            else:
                raise RuntimeError("Server stdout not available")
                
            if not response_line:
                raise RuntimeError("No response from MCP server")

            response = json.loads(response_line.strip())

            # Check for JSON-RPC errors
            if "error" in response:
                error = response["error"]
                error_msg = f"MCP Error: {error.get('message', 'Unknown')}"
                raise RuntimeError(error_msg)

            result = response.get("result", {})
            return result if isinstance(result, dict) else {}

        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            raise

    async def query_memory(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_score: float = 0.3
    ) -> Dict[str, Any]:
        """Query memory using the MCP query_memory tool."""
        if memory_types is None:
            memory_types = ["global", "learned", "agent"]

        arguments = {
            "query": query,
            "memory_types": memory_types,
            "limit": limit,
            "min_score": min_score
        }

        return await self.call_tool("query_memory", arguments)

    async def add_to_global_memory(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5
    ) -> Dict[str, Any]:
        """Add content to global memory."""
        arguments = {
            "content": content,
            "category": category,
            "importance": importance
        }

        return await self.call_tool("add_to_global_memory", arguments)

    async def add_to_learned_memory(
        self,
        content: str,
        pattern_type: str = "insight",
        confidence: float = 0.7
    ) -> Dict[str, Any]:
        """Add content to learned memory."""
        arguments = {
            "content": content,
            "pattern_type": pattern_type,
            "confidence": confidence
        }

        return await self.call_tool("add_to_learned_memory", arguments)

    async def add_to_agent_memory(
        self,
        content: str,
        agent_id: str,
        memory_type: str = "general"
    ) -> Dict[str, Any]:
        """Add content to agent-specific memory."""
        arguments = {
            "content": content,
            "agent_id": agent_id,
            "memory_type": memory_type
        }

        return await self.call_tool("add_to_agent_memory", arguments)

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        return await self.call_tool("system_health", {})

    async def initialize_new_agent(
        self,
        agent_id: Optional[str] = None,
        agent_role: str = "general",
        memory_layers: str = "global,learned",
        policy_version: str = "latest"
    ) -> Dict[str, Any]:
        """Initialize a new agent."""
        arguments = {
            "agent_role": agent_role,
            "memory_layers": memory_layers,
            "policy_version": policy_version
        }
        
        if agent_id:
            arguments["agent_id"] = agent_id

        return await self.call_tool("initialize_new_agent", arguments)

    def is_initialized(self) -> bool:
        """Check if the MCP server is initialized and running."""
        return (self._initialized and
                self.server_process is not None and
                self.server_process.poll() is None)

    async def __aenter__(self) -> 'MCPClientAdapter':
        """Async context manager entry."""
        await self.start_server()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any]
    ) -> None:
        """Async context manager exit."""
        await self.stop_server()


# Singleton instance for UI use
_mcp_client_instance: Optional[MCPClientAdapter] = None


def get_mcp_client() -> MCPClientAdapter:
    """Get the global MCP client instance."""
    global _mcp_client_instance
    if _mcp_client_instance is None:
        _mcp_client_instance = MCPClientAdapter()
    return _mcp_client_instance


async def ensure_mcp_server_running(server_mode: str = "full") -> bool:
    """Ensure the MCP server is running."""
    client = get_mcp_client()
    if not client.is_initialized():
        return await client.start_server(server_mode)
    return True
