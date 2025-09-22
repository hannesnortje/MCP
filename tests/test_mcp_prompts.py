"""
Tests for MCP Prompts functionality in the memory server.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.mcp_server import MemoryMCPServer
from src.prompt_handlers import PromptHandlers
from src.memory_manager import QdrantMemoryManager


class TestPromptHandlers:
    """Test the PromptHandlers class directly."""
    
    @pytest.fixture
    def memory_manager(self):
        """Mock memory manager for testing."""
        manager = MagicMock(spec=QdrantMemoryManager)
        manager.get_recent_memories = AsyncMock(return_value=[])
        manager.search_memories = AsyncMock(return_value=[])
        manager.get_memory_stats = AsyncMock(
            return_value={"total": 0, "recent": 0}
        )
        return manager
    
    @pytest.fixture
    def prompt_handlers(self, memory_manager):
        """Create PromptHandlers instance for testing."""
        return PromptHandlers(memory_manager)
    
    def test_get_available_prompts(self, prompt_handlers):
        """Test that all expected prompts are available."""
        prompts = prompt_handlers.list_prompts()
        
        assert len(prompts) == 13
        
        # Check core prompt
        agent_startup = next(p for p in prompts if p["name"] == "agent_startup")
        assert agent_startup["description"] == "Comprehensive agent startup prompt with memory context and task guidelines"
        assert len(agent_startup["arguments"]) == 3
        
        # Check alias prompts
        alias_names = {p["name"] for p in prompts if "alias" in p["description"].lower() or "shortcut" in p["description"].lower()}
        assert "dev" in alias_names
        assert "test" in alias_names
        
        # Check guidance prompts
        guidance_prompts = [p for p in prompts if p["name"] not in ["agent_startup", "dev", "test"]]
        assert len(guidance_prompts) == 10
    
    @pytest.mark.asyncio
    async def test_agent_startup_prompt_minimal(self, prompt_handlers):
        """Test agent startup prompt with minimal arguments."""
        result = await prompt_handlers.agent_startup()
        
        assert "role" in result
        assert "content" in result
        assert result["role"] == "system"
        assert "specialized AI agent" in result["content"]
        assert "Memory Status: No active memories" in result["content"]
    
    @pytest.mark.asyncio
    async def test_agent_startup_prompt_with_arguments(self, prompt_handlers, memory_manager):
        """Test agent startup prompt with all arguments."""
        # Mock memory data
        memory_manager.get_memory_stats.return_value = {"total": 5, "recent": 2}
        memory_manager.get_recent_memories.return_value = [
            {"content": "Recent task", "timestamp": "2024-01-01T00:00:00Z"},
            {"content": "Another task", "timestamp": "2024-01-02T00:00:00Z"}
        ]
        
        result = await prompt_handlers.agent_startup(
            task_context="Code review",
            priority_level="high",
            memory_scope="recent"
        )
        
        assert result["role"] == "system"
        assert "Code review" in result["content"]
        assert "Priority: HIGH" in result["content"]
        assert "Memory Scope: recent" in result["content"]
        assert "Total memories: 5" in result["content"]
    
    @pytest.mark.asyncio
    async def test_dev_alias_prompt(self, prompt_handlers):
        """Test development alias prompt."""
        result = await prompt_handlers.dev()
        
        assert result["role"] == "system"
        assert "development mode" in result["content"]
        assert "debugging" in result["content"]
        assert "testing" in result["content"]
    
    @pytest.mark.asyncio
    async def test_test_alias_prompt(self, prompt_handlers):
        """Test testing alias prompt."""
        result = await prompt_handlers.test()
        
        assert result["role"] == "system"
        assert "testing mode" in result["content"]
        assert "validation" in result["content"]
        assert "quality assurance" in result["content"]
    
    @pytest.mark.asyncio
    async def test_memory_guidance_prompts(self, prompt_handlers):
        """Test all memory guidance prompts."""
        guidance_methods = [
            "memory_search_guidance",
            "memory_storage_guidance", 
            "memory_retrieval_guidance",
            "context_optimization_guidance",
            "task_decomposition_guidance",
            "error_handling_guidance",
            "performance_optimization_guidance",
            "security_compliance_guidance",
            "documentation_guidance",
            "collaboration_guidance"
        ]
        
        for method_name in guidance_methods:
            method = getattr(prompt_handlers, method_name)
            result = await method()
            
            assert result["role"] == "system"
            assert len(result["content"]) > 100  # Ensure substantial content
            assert "guidance" in result["content"].lower()
    
    @pytest.mark.asyncio
    async def test_get_prompt_invalid_name(self, prompt_handlers):
        """Test getting a non-existent prompt."""
        result = await prompt_handlers.get_prompt("nonexistent_prompt")
        
        assert "error" in result
        assert result["error"]["code"] == -32602
        assert "not found" in result["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_prompt_agent_startup_with_args(self, prompt_handlers, memory_manager):
        """Test getting agent_startup prompt through get_prompt method."""
        memory_manager.get_memory_stats.return_value = {"total": 3, "recent": 1}
        
        result = await prompt_handlers.get_prompt("agent_startup", {
            "task_context": "Testing",
            "priority_level": "medium"
        })
        
        assert "role" in result
        assert "content" in result
        assert "Testing" in result["content"]
        assert "Priority: MEDIUM" in result["content"]


class TestMCPServerPrompts:
    """Test MCP server prompt functionality."""
    
    @pytest.fixture
    def memory_manager(self):
        """Mock memory manager."""
        manager = MagicMock(spec=QdrantMemoryManager)
        manager.get_recent_memories = AsyncMock(return_value=[])
        manager.search_memories = AsyncMock(return_value=[])
        manager.get_memory_stats = AsyncMock(
            return_value={"total": 0, "recent": 0}
        )
        return manager
    
    @pytest.fixture
    def qdrant_manager(self):
        """Mock Qdrant manager."""
        return MagicMock()
    
    @pytest.fixture
    def mcp_server(self, memory_manager, qdrant_manager):
        """Create MCP server for testing."""
        return MemoryMCPServer(memory_manager, qdrant_manager)
    
    def test_server_has_prompt_handlers(self, mcp_server):
        """Test that server initializes with prompt handlers."""
        assert hasattr(mcp_server, 'prompt_handlers')
        assert isinstance(mcp_server.prompt_handlers, PromptHandlers)
    
    def test_get_available_prompts(self, mcp_server):
        """Test server's get_available_prompts method."""
        prompts = mcp_server.get_available_prompts()
        
        assert isinstance(prompts, list)
        assert len(prompts) == 13
        
        # Verify MCP format
        for prompt in prompts:
            assert "name" in prompt
            assert "description" in prompt
            assert "arguments" in prompt
    
    @pytest.mark.asyncio
    async def test_handle_prompt_get_valid(self, mcp_server):
        """Test handling valid prompt requests."""
        result = await mcp_server.handle_prompt_get("dev", {})
        
        assert "role" in result
        assert "content" in result
        assert result["role"] == "system"
    
    @pytest.mark.asyncio
    async def test_handle_prompt_get_with_arguments(self, mcp_server):
        """Test handling prompt requests with arguments."""
        arguments = {
            "task_context": "Unit testing",
            "priority_level": "high"
        }
        result = await mcp_server.handle_prompt_get("agent_startup", arguments)
        
        assert "role" in result
        assert "content" in result
        assert "Unit testing" in result["content"]
        assert "Priority: HIGH" in result["content"]
    
    @pytest.mark.asyncio
    async def test_handle_prompt_get_invalid(self, mcp_server):
        """Test handling invalid prompt requests."""
        result = await mcp_server.handle_prompt_get("invalid_prompt", {})
        
        assert "error" in result
        assert result["error"]["code"] == -32602


class TestMCPPromptIntegration:
    """Integration tests for MCP prompt protocol."""
    
    def test_prompt_list_response_format(self):
        """Test that prompt list responses match MCP specification."""
        memory_manager = MagicMock(spec=QdrantMemoryManager)
        memory_manager.get_recent_memories = AsyncMock(return_value=[])
        memory_manager.search_memories = AsyncMock(return_value=[])
        memory_manager.get_memory_stats = AsyncMock(
            return_value={"total": 0, "recent": 0}
        )
        
        qdrant_manager = MagicMock()
        server = MemoryMCPServer(memory_manager, qdrant_manager)
        
        prompts = server.get_available_prompts()
        
        # Verify each prompt has required MCP fields
        for prompt in prompts:
            assert isinstance(prompt, dict)
            assert "name" in prompt
            assert "description" in prompt
            assert "arguments" in prompt
            
            # Verify arguments structure
            for arg in prompt["arguments"]:
                assert "name" in arg
                assert "description" in arg
                assert "required" in arg
    
    @pytest.mark.asyncio
    async def test_prompt_get_response_format(self):
        """Test that prompt get responses are properly formatted."""
        memory_manager = MagicMock(spec=QdrantMemoryManager)
        memory_manager.get_recent_memories = AsyncMock(return_value=[])
        memory_manager.search_memories = AsyncMock(return_value=[])
        memory_manager.get_memory_stats = AsyncMock(
            return_value={"total": 0, "recent": 0}
        )
        
        qdrant_manager = MagicMock()
        server = MemoryMCPServer(memory_manager, qdrant_manager)
        
        result = await server.handle_prompt_get("dev", {})
        
        # Should return a proper prompt response
        assert "role" in result
        assert "content" in result
        assert isinstance(result["role"], str)
        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0
    
    def test_prompt_argument_validation(self):
        """Test that prompt arguments are properly validated."""
        memory_manager = MagicMock(spec=QdrantMemoryManager)
        memory_manager.get_recent_memories = AsyncMock(return_value=[])
        memory_manager.search_memories = AsyncMock(return_value=[])
        memory_manager.get_memory_stats = AsyncMock(
            return_value={"total": 0, "recent": 0}
        )
        
        prompt_handlers = PromptHandlers(memory_manager)
        prompts = prompt_handlers.list_prompts()
        
        # Find agent_startup prompt and verify its arguments
        agent_startup = next(p for p in prompts if p["name"] == "agent_startup")
        
        expected_args = {"task_context", "priority_level", "memory_scope"}
        actual_args = {arg["name"] for arg in agent_startup["arguments"]}
        
        assert expected_args == actual_args
        
        # Verify all arguments are optional (as per our implementation)
        for arg in agent_startup["arguments"]:
            assert not arg["required"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
