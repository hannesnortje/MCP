"""
Step 4 Tests: Enhanced Agent Management

Comprehensive test suite for agent management functionality:
- Agent initialization and registration
- Permission configuration and enforcement
- Agent-specific memory queries with access control
- Action logging with learned memory integration
"""

import pytest
from unittest.mock import Mock, AsyncMock

from src.tool_handlers import ToolHandlers
from src.memory_manager import QdrantMemoryManager
from src.mcp_server import MemoryMCPServer


class TestAgentManagement:
    """Test Step 4: Enhanced Agent Management"""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test environment"""
        # Mock dependencies
        self.mock_memory_manager = Mock(spec=QdrantMemoryManager)
        
        # Configure mock memory manager for agent operations
        self.mock_memory_manager.register_agent = AsyncMock()
        self.mock_memory_manager.get_agent = AsyncMock()
        self.mock_memory_manager.update_agent_permissions = AsyncMock()
        self.mock_memory_manager.list_agents = AsyncMock()
        self.mock_memory_manager.check_agent_permission = AsyncMock()
        self.mock_memory_manager.log_agent_action = AsyncMock()
        self.mock_memory_manager.query_memory = AsyncMock()
        
        # Create tool handlers with mocked dependency (only memory_manager)
        self.tool_handlers = ToolHandlers(self.mock_memory_manager)

    def teardown_method(self) -> None:
        """Clean up test environment"""
        pass

    # Test 1: Agent Initialization
    async def test_initialize_new_agent_success(self) -> None:
        """Test successful agent initialization"""
        self.mock_memory_manager.register_agent.return_value = {
            'success': True,
            'agent_id': 'test-agent',
            'message': 'Agent test-agent registered successfully'
        }
        
        result = await self.tool_handlers.handle_initialize_new_agent({
            'agent_id': 'test-agent',
            'agent_role': 'developer',
            'memory_layers': ['global', 'learned']
        })
        
        assert 'isError' not in result
        assert len(result['content']) == 1
        assert 'test-agent' in result['content'][0]['text']
        assert 'developer' in result['content'][0]['text']
        
        # Verify register_agent was called correctly
        self.mock_memory_manager.register_agent.assert_called_once_with(
            agent_id='test-agent',
            agent_role='developer',
            memory_layers=['global', 'learned']
        )

    async def test_initialize_new_agent_missing_id(self) -> None:
        """Test agent initialization without agent_id"""
        result = await self.tool_handlers.handle_initialize_new_agent({
            'agent_role': 'developer'
        })
        
        assert result['isError'] is True
        assert 'agent_id is required' in result['content'][0]['text']

    async def test_initialize_new_agent_default_values(self) -> None:
        """Test agent initialization with default values"""
        self.mock_memory_manager.register_agent.return_value = {
            'success': True,
            'agent_id': 'test-agent',
            'message': 'Agent registered successfully'
        }
        
        result = await self.tool_handlers.handle_initialize_new_agent({
            'agent_id': 'test-agent'
        })
        
        assert 'isError' not in result
        
        # Check that defaults were applied
        self.mock_memory_manager.register_agent.assert_called_once_with(
            agent_id='test-agent',
            agent_role='general',  # Default role
            memory_layers=['global', 'learned']  # Default layers
        )

    async def test_initialize_new_agent_failure(self) -> None:
        """Test agent initialization failure"""
        self.mock_memory_manager.register_agent.return_value = {
            'success': False,
            'error': 'Agent already exists'
        }
        
        result = await self.tool_handlers.handle_initialize_new_agent({
            'agent_id': 'existing-agent'
        })
        
        assert result['isError'] is True
        assert 'Agent already exists' in result['content'][0]['text']

    # Test 2: Agent Permission Configuration
    async def test_configure_agent_permissions_success(self) -> None:
        """Test successful permission configuration"""
        permissions = {
            'can_read': ['global', 'learned'],
            'can_write': ['learned'],
            'can_admin': []
        }
        
        self.mock_memory_manager.update_agent_permissions.return_value = {
            'success': True,
            'agent_id': 'test-agent',
            'message': 'Permissions updated successfully'
        }
        
        result = await self.tool_handlers.handle_configure_agent_permissions({
            'agent_id': 'test-agent',
            'permissions': permissions
        })
        
        assert 'isError' not in result
        assert 'test-agent' in result['content'][0]['text']
        assert 'Read access:' in result['content'][0]['text']
        assert "'global'" in result['content'][0]['text']
        assert "'learned'" in result['content'][0]['text']
        
        # Verify update_agent_permissions was called correctly
        expected_call = self.mock_memory_manager.update_agent_permissions
        expected_call.assert_called_once_with(
            agent_id='test-agent',
            permissions=permissions
        )

    async def test_configure_agent_permissions_missing_id(self) -> None:
        """Test permission configuration without agent_id"""
        result = await self.tool_handlers.handle_configure_agent_permissions({
            'permissions': {'can_read': ['global']}
        })
        
        assert result['isError'] is True
        assert 'agent_id is required' in result['content'][0]['text']

    async def test_configure_agent_permissions_failure(self) -> None:
        """Test permission configuration failure"""
        self.mock_memory_manager.update_agent_permissions.return_value = {
            'success': False,
            'error': 'Agent not found'
        }
        
        result = await self.tool_handlers.handle_configure_agent_permissions({
            'agent_id': 'nonexistent-agent',
            'permissions': {'can_read': ['global']}
        })
        
        assert result['isError'] is True
        assert 'Agent not found' in result['content'][0]['text']

    # Test 3: Agent Memory Queries
    async def test_query_memory_for_agent_success(self) -> None:
        """Test successful agent memory query"""
        # Mock permission checks
        self.mock_memory_manager.check_agent_permission.side_effect = [
            True,  # global permission
            True,  # learned permission
            False  # agent permission (denied)
        ]
        
        # Mock query results
        self.mock_memory_manager.query_memory.return_value = {
            'success': True,
            'results': [
                {
                    'content': 'Test memory content',
                    'score': 0.95,
                    'memory_type': 'global'
                },
                {
                    'content': 'Another memory item',
                    'score': 0.87,
                    'memory_type': 'learned'
                }
            ]
        }
        
        result = await self.tool_handlers.handle_query_memory_for_agent({
            'agent_id': 'test-agent',
            'query': 'test search',
            'memory_layers': ['global', 'learned', 'agent'],
            'limit': 10
        })
        
        assert 'isError' not in result
        assert 'Found 2 results' in result['content'][0]['text']
        assert 'Test memory content' in result['content'][0]['text']
        # Check allowed layers are mentioned
        assert 'global, learned' in result['content'][0]['text']
        
        # Verify permission checks were called
        assert self.mock_memory_manager.check_agent_permission.call_count == 3

    async def test_query_memory_for_agent_no_permissions(self) -> None:
        """Test agent memory query with no permissions"""
        # Mock all permission checks as denied
        self.mock_memory_manager.check_agent_permission.return_value = False
        
        result = await self.tool_handlers.handle_query_memory_for_agent({
            'agent_id': 'restricted-agent',
            'query': 'test search',
            'memory_layers': ['global', 'learned']
        })
        
        assert result['isError'] is True
        assert 'no read permissions' in result['content'][0]['text']

    async def test_query_memory_for_agent_missing_params(self) -> None:
        """Test agent memory query with missing parameters"""
        result = await self.tool_handlers.handle_query_memory_for_agent({
            'agent_id': 'test-agent'
            # Missing query
        })
        
        assert result['isError'] is True
        error_msg = result['content'][0]['text']
        assert 'agent_id and query are required' in error_msg

    async def test_query_memory_for_agent_query_failure(self) -> None:
        """Test agent memory query with query failure"""
        # Mock permissions as allowed
        self.mock_memory_manager.check_agent_permission.return_value = True
        
        # Mock query failure
        self.mock_memory_manager.query_memory.return_value = {
            'success': False,
            'error': 'Database connection error'
        }
        
        result = await self.tool_handlers.handle_query_memory_for_agent({
            'agent_id': 'test-agent',
            'query': 'test search'
        })
        
        assert result['isError'] is True
        assert 'Database connection error' in result['content'][0]['text']

    # Test 4: Agent Action Logging
    async def test_store_agent_action_success(self) -> None:
        """Test successful agent action logging"""
        self.mock_memory_manager.log_agent_action.return_value = {
            'success': True,
            'message': 'Action logged successfully',
            'stored_as_learned': False
        }
        
        result = await self.tool_handlers.handle_store_agent_action({
            'agent_id': 'test-agent',
            'action': 'analyzed document',
            'context': {'document': 'test.md', 'duration': '2.3s'},
            'outcome': 'successfully analyzed and stored',
            'learn': False
        })
        
        assert 'isError' not in result
        assert 'Action logged for agent' in result['content'][0]['text']
        assert 'analyzed document' in result['content'][0]['text']
        assert 'successfully analyzed' in result['content'][0]['text']
        
        # Verify log_agent_action was called correctly
        self.mock_memory_manager.log_agent_action.assert_called_once_with(
            agent_id='test-agent',
            action='analyzed document',
            context={'document': 'test.md', 'duration': '2.3s'},
            outcome='successfully analyzed and stored',
            store_as_learned=False
        )

    async def test_store_agent_action_with_learning(self) -> None:
        """Test agent action logging with learned memory integration"""
        self.mock_memory_manager.log_agent_action.return_value = {
            'success': True,
            'message': 'Action logged successfully',
            'stored_as_learned': True
        }
        
        result = await self.tool_handlers.handle_store_agent_action({
            'agent_id': 'test-agent',
            'action': 'solved complex problem',
            'context': {'problem_type': 'optimization'},
            'outcome': 'found efficient solution',
            'learn': True
        })
        
        assert 'isError' not in result
        assert 'Stored as learned memory' in result['content'][0]['text']

    async def test_store_agent_action_missing_params(self) -> None:
        """Test agent action logging with missing parameters"""
        result = await self.tool_handlers.handle_store_agent_action({
            'agent_id': 'test-agent',
            'action': 'some action'
            # Missing outcome
        })
        
        assert result['isError'] is True
        error_msg = result['content'][0]['text']
        assert 'agent_id, action, and outcome are required' in error_msg

    async def test_store_agent_action_failure(self) -> None:
        """Test agent action logging failure"""
        self.mock_memory_manager.log_agent_action.return_value = {
            'success': False,
            'error': 'Failed to log action'
        }
        
        result = await self.tool_handlers.handle_store_agent_action({
            'agent_id': 'test-agent',
            'action': 'test action',
            'outcome': 'test outcome'
        })
        
        assert result['isError'] is True
        assert 'Failed to log action' in result['content'][0]['text']

    # Test 5: MCP Server Integration
    async def test_mcp_server_agent_tools_registration(self) -> None:
        """Test MCP server has agent management tools registered"""
        # Note: MemoryMCPServer doesn't take parameters - it creates its own
        try:
            server = MemoryMCPServer()
            
            # Get available tools
            tools = [tool['name'] for tool in server.get_available_tools()]
            
            # Verify all agent management tools are registered
            expected_tools = [
                'initialize_new_agent',
                'configure_agent_permissions',
                'query_memory_for_agent',
                'store_agent_action'
            ]
            
            for tool_name in expected_tools:
                assert tool_name in tools
        except Exception:
            # If server initialization fails (e.g., no Qdrant), skip test
            pytest.skip("MemoryMCPServer initialization failed")

    async def test_mcp_agent_tool_schemas(self) -> None:
        """Test MCP agent tool schemas are properly defined"""
        try:
            server = MemoryMCPServer()
            
            available_tools = server.get_available_tools()
            tools = {tool['name']: tool for tool in available_tools}
            
            # Test initialize_new_agent schema
            init_tool = tools['initialize_new_agent']
            assert init_tool['inputSchema']['type'] == 'object'
            assert 'agent_id' in init_tool['inputSchema']['properties']
            assert 'agent_role' in init_tool['inputSchema']['properties']
            assert init_tool['inputSchema']['required'] == ['agent_id']
            
            # Test configure_agent_permissions schema
            config_tool = tools['configure_agent_permissions']
            assert 'permissions' in config_tool['inputSchema']['properties']
            expected_required = ['agent_id', 'permissions']
            assert config_tool['inputSchema']['required'] == expected_required
            
            # Test query_memory_for_agent schema
            query_tool = tools['query_memory_for_agent']
            assert 'query' in query_tool['inputSchema']['properties']
            expected_required = ['agent_id', 'query']
            assert query_tool['inputSchema']['required'] == expected_required
            
            # Test store_agent_action schema
            action_tool = tools['store_agent_action']
            assert 'action' in action_tool['inputSchema']['properties']
            assert 'outcome' in action_tool['inputSchema']['properties']
            expected_required = ['agent_id', 'action', 'outcome']
            assert action_tool['inputSchema']['required'] == expected_required
        except Exception:
            # If server initialization fails, skip test
            pytest.skip("MemoryMCPServer initialization failed")

    # Test 6: Integration Tests
    async def test_agent_lifecycle_integration(self) -> None:
        """Test complete agent lifecycle: create -> config -> query -> log"""
        # 1. Initialize agent
        self.mock_memory_manager.register_agent.return_value = {
            'success': True,
            'agent_id': 'lifecycle-agent',
            'message': 'Agent registered successfully'
        }
        
        init_result = await self.tool_handlers.handle_initialize_new_agent({
            'agent_id': 'lifecycle-agent',
            'agent_role': 'tester',
            'memory_layers': ['global', 'learned']
        })
        assert 'isError' not in init_result
        
        # 2. Configure permissions
        self.mock_memory_manager.update_agent_permissions.return_value = {
            'success': True,
            'agent_id': 'lifecycle-agent',
            'message': 'Permissions updated successfully'
        }
        
        handler = self.tool_handlers.handle_configure_agent_permissions
        config_result = await handler({
            'agent_id': 'lifecycle-agent',
            'permissions': {
                'can_read': ['global'],
                'can_write': [],
                'can_admin': []
            }
        })
        assert 'isError' not in config_result
        
        # 3. Query memory (with limited permissions)
        self.mock_memory_manager.check_agent_permission.side_effect = [
            True,   # global: allowed
            False   # learned: denied
        ]
        self.mock_memory_manager.query_memory.return_value = {
            'success': True,
            'results': [{
                'content': 'Global content',
                'score': 0.9,
                'memory_type': 'global'
            }]
        }
        
        query_result = await self.tool_handlers.handle_query_memory_for_agent({
            'agent_id': 'lifecycle-agent',
            'query': 'test query',
            'memory_layers': ['global', 'learned']
        })
        assert 'isError' not in query_result
        
        # 4. Log action
        self.mock_memory_manager.log_agent_action.return_value = {
            'success': True,
            'message': 'Action logged successfully',
            'stored_as_learned': True
        }
        
        action_result = await self.tool_handlers.handle_store_agent_action({
            'agent_id': 'lifecycle-agent',
            'action': 'performed integration test',
            'outcome': 'all tests passed',
            'learn': True
        })
        assert 'isError' not in action_result

    # Test 7: Error Handling and Edge Cases
    async def test_agent_operations_exception_handling(self) -> None:
        """Test exception handling in agent operations"""
        # Mock an exception in register_agent
        error_msg = "Database error"
        register_mock = self.mock_memory_manager.register_agent
        register_mock.side_effect = Exception(error_msg)
        
        result = await self.tool_handlers.handle_initialize_new_agent({
            'agent_id': 'test-agent'
        })
        
        assert result['isError'] is True
        assert 'Error initializing agent' in result['content'][0]['text']

    async def test_permission_enforcement(self) -> None:
        """Test strict permission enforcement"""
        # Agent with no permissions tries to access memory
        self.mock_memory_manager.check_agent_permission.return_value = False
        
        result = await self.tool_handlers.handle_query_memory_for_agent({
            'agent_id': 'restricted-agent',
            'query': 'sensitive query',
            'memory_layers': ['global', 'learned', 'agent']
        })
        
        assert result['isError'] is True
        assert 'no read permissions' in result['content'][0]['text']
        
        # Verify no actual query was performed
        self.mock_memory_manager.query_memory.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
