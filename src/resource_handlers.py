"""
Resource handlers for MCP Resources implementation.
Provides read-only access to system data via MCP protocol.
"""

import os
from typing import Dict, Any, List
from datetime import datetime

from .server_config import get_logger
from .memory_manager import QdrantMemoryManager

logger = get_logger("resource-handlers")


class ResourceHandlers:
    """Handles MCP resource requests for read-only system data access."""
    
    def __init__(self, memory_manager: QdrantMemoryManager):
        """Initialize resource handlers with memory manager."""
        self.memory_manager = memory_manager
        logger.info("Resource handlers initialized")
        
        # Define available resources with their metadata
        self.available_resources = {
            'agent_registry': {
                'name': 'agent_registry',
                'description': (
                    'List of all registered agents with roles '
                    'and memory layers'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://agent_registry'
            },
            'memory_access_matrix': {
                'name': 'memory_access_matrix',
                'description': 'Agent-to-memory access permission mappings',
                'mimeType': 'application/json',
                'uri': 'memory://memory_access_matrix'
            },
            'global_memory_catalog': {
                'name': 'global_memory_catalog',
                'description': (
                    'Indexed global memory entries with metadata and tags'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://global_memory_catalog'
            },
            'learned_memory_insights': {
                'name': 'learned_memory_insights',
                'description': (
                    'Categorized learned memory with insights and patterns'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://learned_memory_insights'
            },
            'agent_memory_summary': {
                'name': 'agent_memory_summary',
                'description': 'Per-agent memory digest and statistics',
                'mimeType': 'application/json',
                'uri': 'memory://agent_memory_summary/{agent_id}'
            },
            'memory_statistics': {
                'name': 'memory_statistics',
                'description': (
                    'System-wide memory collection statistics and metrics'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://memory_statistics'
            },
            'recent_agent_actions': {
                'name': 'recent_agent_actions',
                'description': 'Recent agent actions and activities log',
                'mimeType': 'application/json',
                'uri': 'memory://recent_agent_actions'
            },
            'memory_health_status': {
                'name': 'memory_health_status',
                'description': (
                    'Qdrant collections health status and diagnostics'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://memory_health_status'
            },
            'system_configuration': {
                'name': 'system_configuration',
                'description': 'Current system configuration and settings',
                'mimeType': 'application/json',
                'uri': 'memory://system_configuration'
            },
            'policy_catalog': {
                'name': 'policy_catalog',
                'description': (
                    'Policy rules catalog with versions and compliance status'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://policy_catalog'
            },
            'policy_violations_log': {
                'name': 'policy_violations_log',
                'description': (
                    'Log of policy violations with agent attribution '
                    'and context'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://policy_violations_log'
            },
            'policy_rulebook': {
                'name': 'policy_rulebook',
                'description': (
                    'Complete policy rulebook in canonical JSON format '
                    'with all active rules'
                ),
                'mimeType': 'application/json',
                'uri': 'memory://policy_rulebook'
            }
        }
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """Return list of available resources for MCP resources/list."""
        return list(self.available_resources.values())
    
    async def read_resource(self, uri: str, **kwargs) -> Dict[str, Any]:
        """Read a specific resource by URI."""
        try:
            # Parse URI to extract resource name and parameters
            if not uri.startswith('memory://'):
                return {
                    'error': (
                        f"Invalid URI scheme. Expected 'memory://', got: {uri}"
                    ),
                    'status': 'error'
                }
            
            resource_path = uri[9:]  # Remove 'memory://' prefix
            
            # Route to appropriate handler
            if resource_path == 'agent_registry':
                return await self._get_agent_registry(**kwargs)
            elif resource_path == 'memory_access_matrix':
                return await self._get_memory_access_matrix(**kwargs)
            elif resource_path == 'global_memory_catalog':
                return await self._get_global_memory_catalog(**kwargs)
            elif resource_path == 'learned_memory_insights':
                return await self._get_learned_memory_insights(**kwargs)
            elif resource_path.startswith('agent_memory_summary/'):
                agent_id = resource_path.split('/', 1)[1]
                return await self._get_agent_memory_summary(agent_id, **kwargs)
            elif resource_path == 'memory_statistics':
                return await self._get_memory_statistics(**kwargs)
            elif resource_path == 'recent_agent_actions':
                return await self._get_recent_agent_actions(**kwargs)
            elif resource_path == 'memory_health_status':
                return await self._get_memory_health_status(**kwargs)
            elif resource_path == 'system_configuration':
                return await self._get_system_configuration(**kwargs)
            elif resource_path == 'policy_catalog':
                return await self._get_policy_catalog(**kwargs)
            elif resource_path == 'policy_violations_log':
                return await self._get_policy_violations_log(**kwargs)
            elif resource_path == 'policy_rulebook':
                return await self._get_policy_rulebook(**kwargs)
            else:
                return {
                    'error': f"Unknown resource: {resource_path}",
                    'status': 'error'
                }
                
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return {
                'error': f"Failed to read resource: {str(e)}",
                'status': 'error'
            }
    
    async def _get_agent_registry(
        self, limit: int = 100, offset: int = 0, **kwargs
    ) -> Dict[str, Any]:
        """Get list of all registered agents with roles and memory layers."""
        try:
            agents = await self.memory_manager.list_agents()
            
            # Apply pagination
            total_count = len(agents)
            paginated_agents = agents[offset:offset + limit]
            
            return {
                'resource': 'agent_registry',
                'data': {
                    'agents': paginated_agents,
                    'pagination': {
                        'total_count': total_count,
                        'offset': offset,
                        'limit': limit,
                        'has_more': offset + limit < total_count
                    },
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {
                        'total_agents': total_count,
                        'active_agents': len([
                            a for a in agents if a.get('active', True)
                        ])
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting agent registry: {e}")
            return {
                'error': f"Failed to get agent registry: {str(e)}",
                'status': 'error'
            }
    
    async def _get_memory_access_matrix(self, **kwargs) -> Dict[str, Any]:
        """Get agent-to-memory access permission mappings."""
        try:
            agents = await self.memory_manager.list_agents()
            access_matrix = {}
            
            for agent in agents:
                agent_id = agent.get('agent_id', 'unknown')
                permissions = agent.get('permissions', {})
                access_matrix[agent_id] = {
                    'role': agent.get('role', 'unknown'),
                    'memory_layers': agent.get('memory_layers', []),
                    'permissions': permissions,
                    'access_summary': {
                        'can_read': permissions.get('can_read', []),
                        'can_write': permissions.get('can_write', []),
                        'can_admin': permissions.get('can_admin', [])
                    }
                }
            
            return {
                'resource': 'memory_access_matrix',
                'data': {
                    'access_matrix': access_matrix,
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {
                        'total_agents': len(agents),
                        'memory_layers': ['global', 'learned', 'agent'],
                        'permission_types': [
                            'can_read', 'can_write', 'can_admin'
                        ]
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting memory access matrix: {e}")
            return {
                'error': f"Failed to get memory access matrix: {str(e)}",
                'status': 'error'
            }
    
    async def _get_global_memory_catalog(
        self, limit: int = 100, offset: int = 0, **kwargs
    ) -> Dict[str, Any]:
        """Get indexed global memory entries with metadata and tags."""
        try:
            # Query global memory collection
            query_result = await self.memory_manager.query_memory(
                query="*",
                memory_type="global",
                limit=limit,
                offset=offset
            )
            
            if not query_result.get('success', False):
                return {
                    'error': (
                        f"Failed to query global memory: "
                        f"{query_result.get('error', 'Unknown error')}"
                    ),
                    'status': 'error'
                }
            
            results = query_result.get('results', [])
            
            # Format results with metadata
            catalog_entries = []
            for result in results:
                entry = {
                    'id': result.get('id', 'unknown'),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0),
                    'metadata': result.get('metadata', {}),
                    'memory_type': result.get('memory_type', 'global'),
                    'created_at': result.get('created_at'),
                    'tags': result.get('tags', [])
                }
                catalog_entries.append(entry)
            
            return {
                'resource': 'global_memory_catalog',
                'data': {
                    'catalog': catalog_entries,
                    'pagination': {
                        'offset': offset,
                        'limit': limit,
                        'returned_count': len(catalog_entries),
                        'has_more': len(catalog_entries) == limit
                    },
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {
                        'collection': 'global',
                        'query_type': 'catalog_listing'
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting global memory catalog: {e}")
            return {
                'error': f"Failed to get global memory catalog: {str(e)}",
                'status': 'error'
            }
    
    async def _get_learned_memory_insights(
        self, limit: int = 100, offset: int = 0, **kwargs
    ) -> Dict[str, Any]:
        """Get categorized learned memory with insights and patterns."""
        try:
            # Query learned memory collection
            query_result = await self.memory_manager.query_memory(
                query="*",
                memory_type="learned",
                limit=limit,
                offset=offset
            )
            
            if not query_result.get('success', False):
                return {
                    'error': (
                        f"Failed to query learned memory: "
                        f"{query_result.get('error', 'Unknown error')}"
                    ),
                    'status': 'error'
                }
            
            results = query_result.get('results', [])
            
            # Categorize and analyze insights
            insights = {
                'patterns': [],
                'lessons_learned': [],
                'best_practices': [],
                'troubleshooting': [],
                'other': []
            }
            
            for result in results:
                content = result.get('content', '').lower()
                insight = {
                    'id': result.get('id', 'unknown'),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0),
                    'metadata': result.get('metadata', {}),
                    'created_at': result.get('created_at'),
                    'tags': result.get('tags', [])
                }
                
                # Simple categorization logic
                pattern_words = ['pattern', 'recurring', 'common', 'trend']
                if any(word in content for word in pattern_words):
                    insights['patterns'].append(insight)
                elif any(word in content for word in [
                    'lesson', 'learned', 'mistake', 'experience'
                ]):
                    insights['lessons_learned'].append(insight)
                elif any(word in content for word in [
                    'best', 'practice', 'recommend', 'should'
                ]):
                    insights['best_practices'].append(insight)
                elif any(word in content for word in [
                    'error', 'fix', 'problem', 'solution', 'debug'
                ]):
                    insights['troubleshooting'].append(insight)
                else:
                    insights['other'].append(insight)
            
            return {
                'resource': 'learned_memory_insights',
                'data': {
                    'insights': insights,
                    'pagination': {
                        'offset': offset,
                        'limit': limit,
                        'returned_count': len(results),
                        'has_more': len(results) == limit
                    },
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {
                        'collection': 'learned',
                        'categories': list(insights.keys()),
                        'total_insights': len(results)
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting learned memory insights: {e}")
            return {
                'error': f"Failed to get learned memory insights: {str(e)}",
                'status': 'error'
            }
    
    async def _get_agent_memory_summary(
        self, agent_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Get per-agent memory digest and statistics."""
        try:
            # Check if agent exists
            agent = await self.memory_manager.get_agent(agent_id)
            if not agent.get('success', False):
                return {
                    'error': f"Agent not found: {agent_id}",
                    'status': 'error'
                }
            
            agent_data = agent.get('agent', {})
            
            # Query agent-specific memory
            agent_memory_result = await self.memory_manager.query_memory(
                query="*",
                memory_type="agent",
                agent_id=agent_id,
                limit=1000  # Get more for statistics
            )
            
            agent_memories = (
                agent_memory_result.get('results', [])
                if agent_memory_result.get('success')
                else []
            )
            
            # Get recent actions for this agent
            actions_result = await self.memory_manager.query_memory(
                query=f"agent_id:{agent_id}",
                memory_type="learned",
                limit=50
            )
            
            recent_actions = (
                actions_result.get('results', [])
                if actions_result.get('success')
                else []
            )
            
            # Calculate statistics
            summary = {
                'agent_info': agent_data,
                'memory_statistics': {
                    'total_memories': len(agent_memories),
                    'recent_actions': len(recent_actions),
                    'memory_types_accessible': agent_data.get(
                        'memory_layers', []
                    ),
                    'permissions': agent_data.get('permissions', {})
                },
                'recent_memories': agent_memories[:10],  # Last 10 memories
                'recent_actions': recent_actions[:10],   # Last 10 actions
                'activity_summary': {
                    'last_action': (
                        recent_actions[0].get('created_at')
                        if recent_actions else None
                    ),
                    'total_queries': len([
                        a for a in recent_actions
                        if 'query' in a.get('content', '')
                    ]),
                    'total_stores': len([
                        a for a in recent_actions
                        if 'store' in a.get('content', '')
                    ])
                }
            }
            
            return {
                'resource': 'agent_memory_summary',
                'data': {
                    'agent_id': agent_id,
                    'summary': summary,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'status': 'success'
            }
        except Exception as e:
            error_msg = (
                f"Error getting agent memory summary for {agent_id}: {e}"
            )
            logger.error(error_msg)
            return {
                'error': f"Failed to get agent memory summary: {str(e)}",
                'status': 'error'
            }
    
    async def _get_memory_statistics(self, **kwargs) -> Dict[str, Any]:
        """Get system-wide memory collection statistics and metrics."""
        try:
            # Get statistics for all memory types
            stats = {}
            
            for memory_type in ['global', 'learned', 'agent']:
                query_result = await self.memory_manager.query_memory(
                    query="*",
                    memory_type=memory_type,
                    limit=1000  # Get many for accurate count
                )
                
                results = (
                    query_result.get('results', [])
                    if query_result.get('success')
                    else []
                )
                
                stats[memory_type] = {
                    'total_entries': len(results),
                    'recent_entries': len([
                        r for r in results if r.get('created_at')
                    ]),
                    'avg_score': (
                        sum(r.get('score', 0) for r in results) / len(results)
                        if results else 0
                    ),
                    'has_metadata': len([
                        r for r in results if r.get('metadata')
                    ])
                }
            
            # Get agent statistics
            agents = await self.memory_manager.list_agents()
            agent_stats = {
                'total_agents': len(agents),
                'active_agents': len([
                    a for a in agents if a.get('active', True)
                ]),
                'agents_by_role': {}
            }
            
            # Count agents by role
            for agent in agents:
                role = agent.get('role', 'unknown')
                current_count = agent_stats['agents_by_role'].get(role, 0)
                agent_stats['agents_by_role'][role] = current_count + 1
            
            return {
                'resource': 'memory_statistics',
                'data': {
                    'memory_collections': stats,
                    'agent_statistics': agent_stats,
                    'system_overview': {
                        'total_memories': sum(
                            stats[mt]['total_entries'] for mt in stats
                        ),
                        'collections': list(stats.keys()),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting memory statistics: {e}")
            return {
                'error': f"Failed to get memory statistics: {str(e)}",
                'status': 'error'
            }
    
    async def _get_recent_agent_actions(
        self, limit: int = 50, offset: int = 0, **kwargs
    ) -> Dict[str, Any]:
        """Get recent agent actions and activities log."""
        try:
            # Query learned memory for action logs
            actions_result = await self.memory_manager.query_memory(
                query="action",  # Look for action-related content
                memory_type="learned",
                limit=limit,
                offset=offset
            )
            
            if not actions_result.get('success', False):
                return {
                    'error': (
                        f"Failed to query action logs: "
                        f"{actions_result.get('error', 'Unknown error')}"
                    ),
                    'status': 'error'
                }
            
            actions = actions_result.get('results', [])
            
            # Format actions with agent information
            formatted_actions = []
            for action in actions:
                formatted_action = {
                    'id': action.get('id', 'unknown'),
                    'content': action.get('content', ''),
                    'agent_id': action.get('metadata', {}).get(
                        'agent_id', 'unknown'
                    ),
                    'action_type': action.get('metadata', {}).get(
                        'action_type', 'unknown'
                    ),
                    'timestamp': action.get('created_at'),
                    'score': action.get('score', 0.0),
                    'metadata': action.get('metadata', {})
                }
                formatted_actions.append(formatted_action)
            
            return {
                'resource': 'recent_agent_actions',
                'data': {
                    'actions': formatted_actions,
                    'pagination': {
                        'offset': offset,
                        'limit': limit,
                        'returned_count': len(formatted_actions),
                        'has_more': len(formatted_actions) == limit
                    },
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {
                        'collection': 'learned',
                        'query_type': 'action_logs'
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting recent agent actions: {e}")
            return {
                'error': f"Failed to get recent agent actions: {str(e)}",
                'status': 'error'
            }
    
    async def _get_memory_health_status(self, **kwargs) -> Dict[str, Any]:
        """Get Qdrant collections health status and diagnostics."""
        try:
            # This would typically call Qdrant client directly for health info
            # For now, we'll provide basic status based on successful queries
            
            health_status = {
                'collections': {},
                'overall_status': 'healthy',
                'issues': []
            }
            
            # Test each collection
            for memory_type in ['global', 'learned', 'agent']:
                try:
                    test_result = await self.memory_manager.query_memory(
                        query="test",
                        memory_type=memory_type,
                        limit=1
                    )
                    
                    if test_result.get('success', False):
                        health_status['collections'][memory_type] = {
                            'status': 'healthy',
                            'last_check': datetime.utcnow().isoformat(),
                            'accessible': True
                        }
                    else:
                        health_status['collections'][memory_type] = {
                            'status': 'unhealthy',
                            'last_check': datetime.utcnow().isoformat(),
                            'accessible': False,
                            'error': test_result.get('error', 'Unknown error')
                        }
                        health_status['issues'].append(
                            f"Collection {memory_type} is not accessible"
                        )
                        
                except Exception as e:
                    health_status['collections'][memory_type] = {
                        'status': 'error',
                        'last_check': datetime.utcnow().isoformat(),
                        'accessible': False,
                        'error': str(e)
                    }
                    health_status['issues'].append(
                        f"Collection {memory_type}: {str(e)}"
                    )
            
            # Check agent registry
            try:
                agents = await self.memory_manager.list_agents()
                health_status['collections']['agent_registry'] = {
                    'status': 'healthy',
                    'last_check': datetime.utcnow().isoformat(),
                    'accessible': True,
                    'agent_count': len(agents)
                }
            except Exception as e:
                health_status['collections']['agent_registry'] = {
                    'status': 'error',
                    'last_check': datetime.utcnow().isoformat(),
                    'accessible': False,
                    'error': str(e)
                }
                health_status['issues'].append(f"Agent registry: {str(e)}")
            
            # Update overall status
            if health_status['issues']:
                issue_count = len(health_status['issues'])
                health_status['overall_status'] = (
                    'degraded' if issue_count < 3 else 'unhealthy'
                )
            
            return {
                'resource': 'memory_health_status',
                'data': {
                    'health': health_status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'diagnostics': {
                        'collections_checked': len(
                            health_status['collections']
                        ),
                        'healthy_collections': len([
                            c for c in health_status['collections'].values()
                            if c['status'] == 'healthy'
                        ]),
                        'total_issues': len(health_status['issues'])
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting memory health status: {e}")
            return {
                'error': f"Failed to get memory health status: {str(e)}",
                'status': 'error'
            }
    
    async def _get_system_configuration(self, **kwargs) -> Dict[str, Any]:
        """Get current system configuration and settings."""
        try:
            from .config import (
                DEFAULT_MEMORY_TYPE, CHUNK_SIZE, CHUNK_OVERLAP,
                SIMILARITY_THRESHOLD, GLOBAL_MEMORY_COLLECTION,
                LEARNED_MEMORY_COLLECTION, AGENT_MEMORY_COLLECTION,
                AGENT_REGISTRY_COLLECTION
            )
            
            config_data = {
                'memory_settings': {
                    'default_memory_type': DEFAULT_MEMORY_TYPE,
                    'chunk_size': CHUNK_SIZE,
                    'chunk_overlap': CHUNK_OVERLAP,
                    'similarity_threshold': SIMILARITY_THRESHOLD
                },
                'collections': {
                    'global_memory': GLOBAL_MEMORY_COLLECTION,
                    'learned_memory': LEARNED_MEMORY_COLLECTION,
                    'agent_memory': AGENT_MEMORY_COLLECTION,
                    'agent_registry': AGENT_REGISTRY_COLLECTION
                },
                'system_info': {
                    'python_version': os.sys.version,
                    'working_directory': os.getcwd(),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            return {
                'resource': 'system_configuration',
                'data': {
                    'configuration': config_data,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting system configuration: {e}")
            return {
                'error': f"Failed to get system configuration: {str(e)}",
                'status': 'error'
            }
    
    async def _get_policy_catalog(self, **kwargs) -> Dict[str, Any]:
        """Get policy rules catalog with versions and compliance status."""
        try:
            # For now, return placeholder policy information
            # This would be expanded when policy system is implemented
            
            policy_data = {
                'policies': {
                    'current_version': '1.0.0',
                    'last_updated': datetime.utcnow().isoformat(),
                    'status': 'active',
                    'rules': [],
                    'compliance_status': 'compliant'
                },
                'metadata': {
                    'policy_system': 'placeholder',
                    'note': 'Policy system will be implemented in Step 9'
                }
            }
            
            return {
                'resource': 'policy_catalog',
                'data': {
                    'policy_catalog': policy_data,
                    'timestamp': datetime.utcnow().isoformat(),
                    'metadata': {
                        'implementation_status': 'placeholder',
                        'planned_step': 9
                    }
                },
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error getting policy catalog: {e}")
            return {
                'error': f"Failed to get policy catalog: {str(e)}",
                'status': 'error'
            }

    async def _get_policy_violations_log(self, limit: int = 100, offset: int = 0, **kwargs) -> Dict[str, Any]:
        """Get policy violations log with pagination."""
        try:
            from .config import Config
            
            # Query policy violations collection
            violations_data = []
            
            try:
                # Create dummy query vector for all violations
                query_vector = [0.0] * Config.EMBEDDING_DIMENSION
                
                # Search policy violations collection
                results = self.memory_manager.client.search(
                    collection_name=Config.POLICY_VIOLATIONS_COLLECTION,
                    query_vector=query_vector,
                    limit=min(limit, 1000),
                    offset=offset,
                    with_payload=True
                )
                
                violations_data = [
                    {
                        'violation_id': result.id,
                        'agent_id': result.payload.get('agent_id', 'unknown'),
                        'rule_id': result.payload.get('rule_id', 'unknown'),
                        'severity': result.payload.get('severity', 'medium'),
                        'timestamp': result.payload.get('timestamp', 'unknown'),
                        'context': result.payload.get('context', {})
                    }
                    for result in results
                ]
                
            except Exception as e:
                logger.warning(f"Could not query policy violations: {e}")
                violations_data = []
            
            return {
                'resource': 'policy_violations_log',
                'data': {
                    'violations': violations_data,
                    'total_violations': len(violations_data),
                    'pagination': {
                        'limit': limit,
                        'offset': offset,
                        'has_more': len(violations_data) == limit
                    },
                    'timestamp': datetime.utcnow().isoformat()
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error getting policy violations log: {e}")
            return {
                'error': f"Failed to get policy violations log: {str(e)}",
                'status': 'error'
            }

    async def _get_policy_rulebook(self, version: str = "latest", **kwargs) -> Dict[str, Any]:
        """Get the complete policy rulebook in canonical JSON format."""
        try:
            from .config import Config
            
            policy_entries = []
            
            try:
                # Create dummy query vector for all policies
                query_vector = [0.0] * Config.EMBEDDING_DIMENSION
                
                # Search with filter for version if not "latest"
                filter_condition = None
                if version != "latest":
                    filter_condition = {
                        "must": [{"key": "policy_version", "match": {"value": version}}]
                    }
                
                # Search policy memory collection
                results = self.memory_manager.client.search(
                    collection_name=Config.POLICY_MEMORY_COLLECTION,
                    query_vector=query_vector,
                    query_filter=filter_condition,
                    limit=1000,
                    with_payload=True
                )
                
                policy_entries = [result.payload for result in results]
                
            except Exception as e:
                logger.warning(f"Could not query policy memory: {e}")
                policy_entries = []
            
            if not policy_entries:
                return {
                    'resource': 'policy_rulebook',
                    'data': {
                        'message': f'No policy found for version: {version}',
                        'available': False,
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    'status': 'success'
                }
            
            # Build structured rulebook
            sections = {}
            policy_hash = None
            policy_version_actual = version
            
            for entry in policy_entries:
                section_name = entry.get("section", "Unknown")
                if section_name not in sections:
                    sections[section_name] = []
                
                sections[section_name].append({
                    "rule_id": entry["rule_id"],
                    "text": entry["text"],
                    "severity": entry.get("severity", "medium"),
                    "line_number": entry.get("line_number"),
                    "source_path": entry.get("source_path")
                })
                
                # Get policy hash and version from first entry
                if policy_hash is None:
                    policy_hash = entry.get("policy_hash", "unknown")
                    policy_version_actual = entry.get("policy_version", version)
            
            # Create canonical rulebook
            rulebook = {
                "policy_version": policy_version_actual,
                "policy_hash": policy_hash,
                "sections": sections,
                "total_rules": len(policy_entries),
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                'resource': 'policy_rulebook',
                'data': {
                    'rulebook': rulebook,
                    'available': True,
                    'version': policy_version_actual,
                    'hash': policy_hash,
                    'total_rules': len(policy_entries),
                    'sections_count': len(sections),
                    'timestamp': datetime.utcnow().isoformat()
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error getting policy rulebook: {e}")
            return {
                'error': f"Failed to get policy rulebook: {str(e)}",
                'status': 'error'
            }
