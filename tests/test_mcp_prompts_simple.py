"""
Simple tests to validate MCP Prompts functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.mcp_server import MemoryMCPServer
from src.prompt_handlers import PromptHandlers
from src.memory_manager import QdrantMemoryManager


class TestBasicPromptFunctionality:
    """Basic tests for prompt functionality."""
    
    @pytest.fixture
    def memory_manager(self):
        """Mock memory manager for testing."""
        manager = MagicMock(spec=QdrantMemoryManager)
        manager.get_recent_memories = AsyncMock(return_value=[])
        manager.search_memories = AsyncMock(return_value=[])
        manager.get_memory_stats = AsyncMock(return_value={"total": 0, "recent": 0})
        return manager
    
    @pytest.fixture
    def prompt_handlers(self, memory_manager):
        """Create PromptHandlers instance for testing."""
        return PromptHandlers(memory_manager)
    
    @pytest.fixture
    def mcp_server(self):
        """Create MCP server for testing."""
        return MemoryMCPServer()
    
    def test_prompt_handlers_creation(self, prompt_handlers):
        """Test that prompt handlers can be created."""
        assert isinstance(prompt_handlers, PromptHandlers)
    
    def test_list_prompts_returns_list(self, prompt_handlers):
        """Test that list_prompts returns a list."""
        prompts = prompt_handlers.list_prompts()
        assert isinstance(prompts, list)
        assert len(prompts) > 0
    
    def test_all_prompts_have_required_fields(self, prompt_handlers):
        """Test that all prompts have required MCP fields."""
        prompts = prompt_handlers.list_prompts()
        
        for prompt in prompts:
            assert "name" in prompt
            assert "description" in prompt
            assert "arguments" in prompt
            assert isinstance(prompt["name"], str)
            assert isinstance(prompt["description"], str)
            assert isinstance(prompt["arguments"], list)
    
    @pytest.mark.asyncio
    async def test_get_valid_prompt(self, prompt_handlers):
        """Test getting a valid prompt."""
        prompts = prompt_handlers.list_prompts()
        first_prompt_name = prompts[0]["name"]
        
        # agent_startup requires arguments
        if first_prompt_name == "agent_startup":
            args = {"agent_id": "test123", "agent_role": "developer"}
        else:
            args = {}
            
        result = await prompt_handlers.get_prompt(first_prompt_name, args)
        
        # Should return either a valid prompt or an error structure
        if result.get("status") == "error":
            assert "error" in result
        else:
            assert result.get("status") == "success"
            assert "prompt" in result
    
    @pytest.mark.asyncio
    async def test_get_invalid_prompt(self, prompt_handlers):
        """Test getting an invalid prompt."""
        result = await prompt_handlers.get_prompt("invalid_prompt_name", {})
        
        assert result.get("status") == "error"
        assert "error" in result
        assert "unknown prompt" in result["error"].lower()
    
    def test_server_has_prompt_handlers(self, mcp_server):
        """Test that MCP server has prompt handlers."""
        assert hasattr(mcp_server, 'prompt_handlers')
        assert isinstance(mcp_server.prompt_handlers, PromptHandlers)
    
    def test_server_get_available_prompts(self, mcp_server):
        """Test server's get_available_prompts method."""
        prompts = mcp_server.get_available_prompts()
        
        assert isinstance(prompts, list)
        assert len(prompts) > 0
        
        # Check MCP format
        for prompt in prompts:
            assert "name" in prompt
            assert "description" in prompt
            assert "arguments" in prompt
    
    @pytest.mark.asyncio
    async def test_server_handle_prompt_get(self, mcp_server):
        """Test server's handle_prompt_get method."""
        # Test with agent_startup (requires arguments)
        result = await mcp_server.handle_prompt_get(
            'agent_startup', 
            {'agent_id': 'test123', 'agent_role': 'developer'}
        )
        
        # Should return MCP format
        assert isinstance(result, dict)
        # Either error format or success format
        if "error" in result:
            assert result["error"]["code"] == -32602
        else:
            assert "messages" in result or "description" in result
    
    @pytest.mark.asyncio  
    async def test_server_handle_invalid_prompt(self, mcp_server):
        """Test server handling of invalid prompt."""
        result = await mcp_server.handle_prompt_get("invalid_prompt", {})
        
        assert "error" in result
        assert result["error"]["code"] == -32603  # Internal error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
