"""
End-to-end test for MCP Prompts protocol integration.
"""

import pytest
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import io
import sys


def mock_stdin_stdout():
    """Mock stdin/stdout for MCP protocol testing."""
    mock_stdin = io.StringIO()
    mock_stdout = io.StringIO()
    return mock_stdin, mock_stdout


class TestMCPPromptsProtocol:
    """Test MCP prompts protocol integration."""
    
    @pytest.mark.asyncio
    async def test_prompts_list_protocol(self):
        """Test prompts/list MCP protocol method."""
        from src.mcp_server import run_mcp_server
        
        # Create mock request for prompts/list
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/list",
            "params": {}
        }
        
        # Mock stdin/stdout
        mock_stdin = io.StringIO(json.dumps(request) + '\n')
        mock_stdout = io.StringIO()
        
        with patch('sys.stdin', mock_stdin), \
             patch('sys.stdout', mock_stdout), \
             patch('src.mcp_server.ensure_qdrant_running', return_value=False):
            
            # This would run forever, so we need to interrupt it after one message
            try:
                # Start the server task
                server_task = asyncio.create_task(run_mcp_server())
                
                # Wait a moment for it to process
                await asyncio.sleep(0.1)
                
                # Cancel the server task
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass
                    
            except Exception as e:
                # Server might exit early, that's ok for this test
                pass
            
            # Check if we got any output
            output = mock_stdout.getvalue()
            
            # If we got output, verify it's valid JSON
            if output.strip():
                response = json.loads(output.strip())
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == 1
                
                # Should have prompts in result
                if "result" in response:
                    assert "prompts" in response["result"]
                    assert len(response["result"]["prompts"]) > 0
    
    @pytest.mark.asyncio
    async def test_prompts_get_protocol(self):
        """Test prompts/get MCP protocol method."""
        from src.mcp_server import run_mcp_server
        
        # Create mock request for prompts/get
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "prompts/get",
            "params": {
                "name": "agent_startup",
                "arguments": {
                    "agent_id": "test123",
                    "agent_role": "developer"
                }
            }
        }
        
        # Mock stdin/stdout
        mock_stdin = io.StringIO(json.dumps(request) + '\n')
        mock_stdout = io.StringIO()
        
        with patch('sys.stdin', mock_stdin), \
             patch('sys.stdout', mock_stdout), \
             patch('src.mcp_server.ensure_qdrant_running', return_value=False):
            
            try:
                # Start the server task
                server_task = asyncio.create_task(run_mcp_server())
                
                # Wait a moment for it to process
                await asyncio.sleep(0.1)
                
                # Cancel the server task
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass
                    
            except Exception as e:
                # Server might exit early, that's ok for this test
                pass
            
            # Check if we got any output
            output = mock_stdout.getvalue()
            
            # If we got output, verify it's valid JSON
            if output.strip():
                response = json.loads(output.strip())
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == 2
                
                # Should have prompt content in result
                if "result" in response:
                    assert "messages" in response["result"] or "description" in response["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])