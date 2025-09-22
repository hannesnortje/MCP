"""
Step 5 Tests: MCP Resources Implementation

Comprehensive test suite for MCP resource functionality:
- All 10 resource endpoints with proper URI handling
- Resource listing and metadata validation
- Pagination support and parameter validation
- Error scenarios and MCP protocol compliance
- Integration with memory manager and live data
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.resource_handlers import ResourceHandlers
from src.memory_manager import QdrantMemoryManager
from src.mcp_server import MemoryMCPServer


class TestMCPResources:
    """Test Step 5: MCP Resources Implementation"""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test environment"""
        # Mock memory manager
        self.mock_memory_manager = Mock(spec=QdrantMemoryManager)
        
        # Configure mock methods for resource testing
        self.mock_memory_manager.list_agents = AsyncMock()
        self.mock_memory_manager.get_agent = AsyncMock()
        self.mock_memory_manager.query_memory = AsyncMock()
        
        # Create resource handlers with mocked dependency
        self.resource_handlers = ResourceHandlers(self.mock_memory_manager)

    def teardown_method(self) -> None:
        """Clean up test environment"""
        pass

    # Test 1: Resource Listing
    def test_list_resources(self) -> None:
        """Test resource listing returns all 10 expected resources"""
        resources = self.resource_handlers.list_resources()
        
        expected_resources = [
            'agent_registry',
            'memory_access_matrix',
            'global_memory_catalog',
            'learned_memory_insights',
            'agent_memory_summary',
            'memory_statistics',
            'recent_agent_actions',
            'memory_health_status',
            'system_configuration',
            'policy_catalog'
        ]
        
        assert len(resources) == 10
        resource_names = [r['name'] for r in resources]
        
        for expected_name in expected_resources:
            assert expected_name in resource_names
        
        # Verify resource structure
        for resource in resources:
            assert 'name' in resource
            assert 'description' in resource
            assert 'mimeType' in resource
            assert 'uri' in resource
            assert resource['mimeType'] == 'application/json'
            assert resource['uri'].startswith('memory://')

    # Test 2: Agent Registry Resource
    async def test_agent_registry_resource(self) -> None:
        """Test agent_registry resource returns proper agent data"""
        # Mock agent data
        mock_agents = [
            {
                'agent_id': 'test-agent-1',
                'role': 'developer',
                'memory_layers': ['global', 'learned'],
                'permissions': {
                    'can_read': ['global'],
                    'can_write': [],
                    'can_admin': []
                },
                'active': True
            },
            {
                'agent_id': 'test-agent-2',
                'role': 'analyst',
                'memory_layers': ['global'],
                'permissions': {
                    'can_read': ['global'],
                    'can_write': [],
                    'can_admin': []
                },
                'active': False
            }
        ]
        
        self.mock_memory_manager.list_agents.return_value = mock_agents
        
        result = await self.resource_handlers.read_resource(
            'memory://agent_registry'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'agent_registry'
        assert 'data' in result
        assert 'agents' in result['data']
        assert len(result['data']['agents']) == 2
        assert result['data']['metadata']['total_agents'] == 2
        assert result['data']['metadata']['active_agents'] == 1
        
        # Verify pagination info
        assert 'pagination' in result['data']
        assert result['data']['pagination']['total_count'] == 2
        assert result['data']['pagination']['offset'] == 0
        assert result['data']['pagination']['limit'] == 100

    async def test_agent_registry_with_pagination(self) -> None:
        """Test agent_registry resource with pagination parameters"""
        # Mock large agent list
        mock_agents = [
            {'agent_id': f'agent-{i}', 'role': 'test', 'active': True}
            for i in range(150)
        ]
        
        self.mock_memory_manager.list_agents.return_value = mock_agents
        
        result = await self.resource_handlers.read_resource(
            'memory://agent_registry',
            limit=50,
            offset=25
        )
        
        assert result['status'] == 'success'
        assert len(result['data']['agents']) == 50
        assert result['data']['pagination']['offset'] == 25
        assert result['data']['pagination']['limit'] == 50
        assert result['data']['pagination']['has_more'] is True
        assert result['data']['pagination']['total_count'] == 150

    # Test 3: Memory Access Matrix Resource
    async def test_memory_access_matrix_resource(self) -> None:
        """Test memory_access_matrix resource returns permission mappings"""
        mock_agents = [
            {
                'agent_id': 'admin-agent',
                'role': 'admin',
                'memory_layers': ['global', 'learned', 'agent'],
                'permissions': {
                    'can_read': ['global', 'learned', 'agent'],
                    'can_write': ['learned', 'agent'],
                    'can_admin': ['agent']
                }
            },
            {
                'agent_id': 'read-only-agent',
                'role': 'viewer',
                'memory_layers': ['global'],
                'permissions': {
                    'can_read': ['global'],
                    'can_write': [],
                    'can_admin': []
                }
            }
        ]
        
        self.mock_memory_manager.list_agents.return_value = mock_agents
        
        result = await self.resource_handlers.read_resource(
            'memory://memory_access_matrix'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'memory_access_matrix'
        assert 'access_matrix' in result['data']
        
        matrix = result['data']['access_matrix']
        assert 'admin-agent' in matrix
        assert 'read-only-agent' in matrix
        
        # Verify admin agent permissions
        admin_data = matrix['admin-agent']
        assert admin_data['role'] == 'admin'
        assert len(admin_data['access_summary']['can_read']) == 3
        assert len(admin_data['access_summary']['can_write']) == 2
        assert len(admin_data['access_summary']['can_admin']) == 1
        
        # Verify read-only agent permissions
        readonly_data = matrix['read-only-agent']
        assert readonly_data['role'] == 'viewer'
        assert len(readonly_data['access_summary']['can_read']) == 1
        assert len(readonly_data['access_summary']['can_write']) == 0

    # Test 4: Global Memory Catalog Resource
    async def test_global_memory_catalog_resource(self) -> None:
        """Test global_memory_catalog resource returns memory entries"""
        mock_memory_results = {
            'success': True,
            'results': [
                {
                    'id': 'mem-1',
                    'content': 'Global documentation content',
                    'score': 0.95,
                    'metadata': {'source': 'docs.md', 'type': 'documentation'},
                    'memory_type': 'global',
                    'created_at': '2024-12-19T10:00:00Z',
                    'tags': ['documentation', 'reference']
                },
                {
                    'id': 'mem-2',
                    'content': 'API reference information',
                    'score': 0.87,
                    'metadata': {'source': 'api.md', 'type': 'reference'},
                    'memory_type': 'global',
                    'created_at': '2024-12-19T09:00:00Z',
                    'tags': ['api', 'reference']
                }
            ]
        }
        
        self.mock_memory_manager.query_memory.return_value = (
            mock_memory_results
        )
        
        result = await self.resource_handlers.read_resource(
            'memory://global_memory_catalog',
            limit=10
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'global_memory_catalog'
        assert 'catalog' in result['data']
        assert len(result['data']['catalog']) == 2
        
        # Verify first entry structure
        first_entry = result['data']['catalog'][0]
        assert first_entry['id'] == 'mem-1'
        assert first_entry['content'] == 'Global documentation content'
        assert first_entry['memory_type'] == 'global'
        assert 'documentation' in first_entry['tags']

    # Test 5: Learned Memory Insights Resource
    async def test_learned_memory_insights_resource(self) -> None:
        """Test learned_memory_insights resource categorizes content"""
        mock_learned_results = {
            'success': True,
            'results': [
                {
                    'id': 'insight-1',
                    'content': 'Found a common pattern in error handling',
                    'score': 0.92,
                    'metadata': {'category': 'patterns'},
                    'created_at': '2024-12-19T10:00:00Z',
                    'tags': ['patterns', 'errors']
                },
                {
                    'id': 'insight-2',
                    'content': (
                        'Best practice: always validate input parameters'
                    ),
                    'score': 0.89,
                    'metadata': {'category': 'best_practices'},
                    'created_at': '2024-12-19T09:30:00Z',
                    'tags': ['validation', 'best-practices']
                },
                {
                    'id': 'insight-3',
                    'content': (
                        'Lesson learned: debugging async issues requires '
                        'careful timing'
                    ),
                    'score': 0.85,
                    'metadata': {'category': 'lessons'},
                    'created_at': '2024-12-19T09:00:00Z',
                    'tags': ['debugging', 'async']
                }
            ]
        }
        
        self.mock_memory_manager.query_memory.return_value = (
            mock_learned_results
        )
        
        result = await self.resource_handlers.read_resource(
            'memory://learned_memory_insights'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'learned_memory_insights'
        assert 'insights' in result['data']
        
        insights = result['data']['insights']
        expected_categories = [
            'patterns', 'lessons_learned', 'best_practices',
            'troubleshooting', 'other'
        ]
        
        for category in expected_categories:
            assert category in insights
            assert isinstance(insights[category], list)
        
        # Verify categorization worked (should have at least one item
        # in patterns, lessons, and best_practices)
        assert len(insights['patterns']) >= 1  # "pattern" keyword
        assert len(insights['best_practices']) >= 1  # "best" keyword
        assert len(insights['lessons_learned']) >= 1  # "lesson" keyword

    # Test 6: Agent Memory Summary Resource
    async def test_agent_memory_summary_resource(self) -> None:
        """Test agent_memory_summary resource for specific agent"""
        # Mock agent exists
        mock_agent_result = {
            'success': True,
            'agent': {
                'agent_id': 'test-agent',
                'role': 'developer',
                'memory_layers': ['global', 'learned', 'agent'],
                'permissions': {
                    'can_read': ['global', 'learned'],
                    'can_write': ['learned'],
                    'can_admin': []
                }
            }
        }
        
        # Mock agent-specific memory
        mock_agent_memory = {
            'success': True,
            'results': [
                {
                    'id': 'agent-mem-1',
                    'content': 'Agent specific task',
                    'created_at': '2024-12-19T10:00:00Z'
                }
            ]
        }
        
        # Mock recent actions
        mock_recent_actions = {
            'success': True,
            'results': [
                {
                    'id': 'action-1',
                    'content': 'query: search documentation',
                    'created_at': '2024-12-19T09:30:00Z'
                }
            ]
        }
        
        self.mock_memory_manager.get_agent.return_value = mock_agent_result
        self.mock_memory_manager.query_memory.side_effect = [
            mock_agent_memory, mock_recent_actions
        ]
        
        result = await self.resource_handlers.read_resource(
            'memory://agent_memory_summary/test-agent'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'agent_memory_summary'
        assert result['data']['agent_id'] == 'test-agent'
        assert 'summary' in result['data']
        
        summary = result['data']['summary']
        assert 'agent_info' in summary
        assert 'memory_statistics' in summary
        assert 'recent_memories' in summary
        assert 'recent_actions' in summary
        assert 'activity_summary' in summary
        
        # Verify statistics
        stats = summary['memory_statistics']
        assert stats['total_memories'] == 1
        assert stats['recent_actions'] == 1
        assert 'global' in stats['memory_types_accessible']

    async def test_agent_memory_summary_nonexistent_agent(self) -> None:
        """Test agent_memory_summary resource for nonexistent agent"""
        # Mock agent not found
        mock_agent_result = {
            'success': False,
            'error': 'Agent not found'
        }
        
        self.mock_memory_manager.get_agent.return_value = mock_agent_result
        
        result = await self.resource_handlers.read_resource(
            'memory://agent_memory_summary/nonexistent-agent'
        )
        
        assert result['status'] == 'error'
        assert 'Agent not found' in result['error']

    # Test 7: Memory Statistics Resource
    async def test_memory_statistics_resource(self) -> None:
        """Test memory_statistics resource returns system-wide stats"""
        # Mock memory queries for each type
        mock_global_results = {
            'success': True,
            'results': [
                {
                    'id': f'global-{i}', 'score': 0.9,
                    'created_at': '2024-12-19', 'metadata': {}
                } for i in range(50)
            ]
        }
        mock_learned_results = {
            'success': True,
            'results': [
                {
                    'id': f'learned-{i}', 'score': 0.8,
                    'created_at': '2024-12-19', 'metadata': {}
                } for i in range(30)
            ]
        }
        mock_agent_results = {
            'success': True,
            'results': [
                {
                    'id': f'agent-{i}', 'score': 0.7,
                    'created_at': '2024-12-19', 'metadata': {}
                } for i in range(20)
            ]
        }
        
        self.mock_memory_manager.query_memory.side_effect = [
            mock_global_results, mock_learned_results, mock_agent_results
        ]
        
        # Mock agents for agent statistics
        mock_agents = [
            {'agent_id': 'agent-1', 'role': 'developer', 'active': True},
            {'agent_id': 'agent-2', 'role': 'developer', 'active': True},
            {'agent_id': 'agent-3', 'role': 'analyst', 'active': False}
        ]
        self.mock_memory_manager.list_agents.return_value = mock_agents
        
        result = await self.resource_handlers.read_resource(
            'memory://memory_statistics'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'memory_statistics'
        assert 'memory_collections' in result['data']
        assert 'agent_statistics' in result['data']
        assert 'system_overview' in result['data']
        
        # Verify memory collection stats
        collections = result['data']['memory_collections']
        assert 'global' in collections
        assert 'learned' in collections
        assert 'agent' in collections
        assert collections['global']['total_entries'] == 50
        assert collections['learned']['total_entries'] == 30
        assert collections['agent']['total_entries'] == 20
        
        # Verify agent statistics
        agent_stats = result['data']['agent_statistics']
        assert agent_stats['total_agents'] == 3
        assert agent_stats['active_agents'] == 2
        assert agent_stats['agents_by_role']['developer'] == 2
        assert agent_stats['agents_by_role']['analyst'] == 1
        
        # Verify system overview
        overview = result['data']['system_overview']
        assert overview['total_memories'] == 100  # 50 + 30 + 20

    # Test 8: Recent Agent Actions Resource
    async def test_recent_agent_actions_resource(self) -> None:
        """Test recent_agent_actions resource returns action logs"""
        mock_actions_results = {
            'success': True,
            'results': [
                {
                    'id': 'action-1',
                    'content': 'agent performed memory query action',
                    'score': 0.9,
                    'created_at': '2024-12-19T10:00:00Z',
                    'metadata': {
                        'agent_id': 'test-agent-1',
                        'action_type': 'query'
                    }
                },
                {
                    'id': 'action-2',
                    'content': 'agent stored new memory action',
                    'score': 0.85,
                    'created_at': '2024-12-19T09:30:00Z',
                    'metadata': {
                        'agent_id': 'test-agent-2',
                        'action_type': 'store'
                    }
                }
            ]
        }
        
        self.mock_memory_manager.query_memory.return_value = (
            mock_actions_results
        )
        
        result = await self.resource_handlers.read_resource(
            'memory://recent_agent_actions',
            limit=25
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'recent_agent_actions'
        assert 'actions' in result['data']
        assert len(result['data']['actions']) == 2
        
        # Verify action structure
        first_action = result['data']['actions'][0]
        assert first_action['id'] == 'action-1'
        assert first_action['agent_id'] == 'test-agent-1'
        assert first_action['action_type'] == 'query'
        assert first_action['timestamp'] == '2024-12-19T10:00:00Z'
        
        # Verify pagination
        assert result['data']['pagination']['limit'] == 25
        assert result['data']['pagination']['returned_count'] == 2

    # Test 9: Memory Health Status Resource
    async def test_memory_health_status_resource(self) -> None:
        """Test memory_health_status resource returns system health"""
        # Mock successful queries for all memory types
        mock_successful_query = {'success': True, 'results': []}
        self.mock_memory_manager.query_memory.return_value = (
            mock_successful_query
        )
        
        # Mock successful agent list
        self.mock_memory_manager.list_agents.return_value = [
            {'agent_id': 'test-agent', 'role': 'test'}
        ]
        
        result = await self.resource_handlers.read_resource(
            'memory://memory_health_status'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'memory_health_status'
        assert 'health' in result['data']
        
        health = result['data']['health']
        assert health['overall_status'] == 'healthy'
        assert len(health['issues']) == 0
        assert 'collections' in health
        
        # Verify all collections are checked
        collections = health['collections']
        expected_collections = ['global', 'learned', 'agent', 'agent_registry']
        for collection in expected_collections:
            assert collection in collections
            assert collections[collection]['status'] == 'healthy'
            assert collections[collection]['accessible'] is True

    async def test_memory_health_status_with_failures(self) -> None:
        """Test memory_health_status resource with collection failures"""
        # Mock failures for some collections
        def mock_query_side_effect(*args, **kwargs):
            memory_type = kwargs.get('memory_type', 'unknown')
            if memory_type == 'global':
                return {'success': False, 'error': 'Connection timeout'}
            return {'success': True, 'results': []}
        
        self.mock_memory_manager.query_memory.side_effect = (
            mock_query_side_effect
        )
        self.mock_memory_manager.list_agents.return_value = []
        
        result = await self.resource_handlers.read_resource(
            'memory://memory_health_status'
        )
        
        assert result['status'] == 'success'
        health = result['data']['health']
        assert health['overall_status'] in ['degraded', 'unhealthy']
        assert len(health['issues']) > 0
        
        # Verify failed collection is marked as unhealthy
        assert health['collections']['global']['status'] == 'unhealthy'
        assert health['collections']['global']['accessible'] is False

    # Test 10: System Configuration Resource
    async def test_system_configuration_resource(self) -> None:
        """Test system_configuration resource returns config data"""
        with patch('src.resource_handlers.os.getcwd',
                   return_value='/test/dir'), \
             patch('src.resource_handlers.os.sys.version', '3.12.0'):
            
            result = await self.resource_handlers.read_resource(
                'memory://system_configuration'
            )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'system_configuration'
        assert 'configuration' in result['data']
        
        config = result['data']['configuration']
        assert 'memory_settings' in config
        assert 'collections' in config
        assert 'system_info' in config
        
        # Verify memory settings are present
        memory_settings = config['memory_settings']
        assert 'default_memory_type' in memory_settings
        assert 'chunk_size' in memory_settings
        assert 'chunk_overlap' in memory_settings
        assert 'similarity_threshold' in memory_settings
        
        # Verify collections configuration
        collections = config['collections']
        assert 'global_memory' in collections
        assert 'learned_memory' in collections
        assert 'agent_memory' in collections
        assert 'agent_registry' in collections

    # Test 11: Policy Catalog Resource
    async def test_policy_catalog_resource(self) -> None:
        """Test policy_catalog resource returns policy information"""
        result = await self.resource_handlers.read_resource(
            'memory://policy_catalog'
        )
        
        assert result['status'] == 'success'
        assert result['resource'] == 'policy_catalog'
        assert 'policy_catalog' in result['data']
        
        # This is currently a placeholder, so verify placeholder structure
        policy_data = result['data']['policy_catalog']
        assert 'policies' in policy_data
        assert 'metadata' in policy_data
        assert policy_data['metadata']['policy_system'] == 'placeholder'

    # Test 12: URI Validation and Error Handling
    async def test_invalid_uri_scheme(self) -> None:
        """Test handling of invalid URI schemes"""
        result = await self.resource_handlers.read_resource(
            'invalid://some_resource'
        )
        
        assert result['status'] == 'error'
        assert 'Invalid URI scheme' in result['error']

    async def test_unknown_resource(self) -> None:
        """Test handling of unknown resource paths"""
        result = await self.resource_handlers.read_resource(
            'memory://nonexistent_resource'
        )
        
        assert result['status'] == 'error'
        assert 'Unknown resource' in result['error']

    async def test_resource_exception_handling(self) -> None:
        """Test exception handling in resource operations"""
        # Force an exception in list_agents
        self.mock_memory_manager.list_agents.side_effect = Exception(
            "Database error"
        )
        
        result = await self.resource_handlers.read_resource(
            'memory://agent_registry'
        )
        
        assert result['status'] == 'error'
        assert 'Failed to get agent registry' in result['error']

    # Test 13: MCP Server Integration
    async def test_mcp_server_resource_integration(self) -> None:
        """Test MCP server resource integration"""
        with patch('src.mcp_server.ensure_qdrant_running', return_value=True):
            server = MemoryMCPServer()
            
            # Test get_available_resources
            resources = server.get_available_resources()
            assert len(resources) == 10
            
            # Test handle_resource_read
            with patch.object(
                server.resource_handlers, 'read_resource'
            ) as mock_read:
                mock_read.return_value = {
                    'status': 'success',
                    'data': {'test': 'data'},
                    'resource': 'test_resource'
                }
                
                result = await server.handle_resource_read(
                    'memory://test_resource',
                    {'limit': 50}
                )
                
                assert 'contents' in result
                assert len(result['contents']) == 1
                assert result['contents'][0]['uri'] == 'memory://test_resource'
                assert result['contents'][0]['mimeType'] == 'application/json'
                assert 'test' in result['contents'][0]['text']

    async def test_mcp_server_resource_error_handling(self) -> None:
        """Test MCP server resource error handling"""
        with patch('src.mcp_server.ensure_qdrant_running', return_value=True):
            server = MemoryMCPServer()
            
            # Test error response formatting
            with patch.object(
                server.resource_handlers, 'read_resource'
            ) as mock_read:
                mock_read.return_value = {
                    'status': 'error',
                    'error': 'Test error message'
                }
                
                result = await server.handle_resource_read(
                    'memory://test_resource',
                    {}
                )
                
                assert 'error' in result
                assert result['error']['code'] == -32603
                assert 'Test error message' in result['error']['message']

    # Test 14: Pagination Testing
    async def test_pagination_parameters(self) -> None:
        """Test pagination parameter handling across resources"""
        # Test with large mock dataset
        large_agent_list = [
            {'agent_id': f'agent-{i}', 'role': 'test', 'active': True}
            for i in range(250)
        ]
        
        self.mock_memory_manager.list_agents.return_value = large_agent_list
        
        # Test different pagination scenarios
        test_cases = [
            {
                'limit': 50, 'offset': 0,
                'expected_count': 50, 'has_more': True
            },
            {
                'limit': 50, 'offset': 200,
                'expected_count': 50, 'has_more': False
            },
            {
                'limit': 100, 'offset': 150,
                'expected_count': 100, 'has_more': False
            },
        ]
        
        for case in test_cases:
            result = await self.resource_handlers.read_resource(
                'memory://agent_registry',
                limit=case['limit'],
                offset=case['offset']
            )
            
            assert result['status'] == 'success'
            assert len(result['data']['agents']) == case['expected_count']
            assert result['data']['pagination']['has_more'] == case['has_more']
            assert result['data']['pagination']['offset'] == case['offset']
            assert result['data']['pagination']['limit'] == case['limit']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
