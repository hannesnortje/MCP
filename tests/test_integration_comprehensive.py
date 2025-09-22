#!/usr/bin/env python3
"""
Comprehensive Integration Tests for MCP Memory Server
Tests all features working together in realistic scenarios.
"""

import os
import sys
import asyncio
import tempfile
import shutil
import time
import logging
from typing import List

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after path modification  
from mcp_server import MCPMemoryServer
from server_config import ServerConfig
from error_handler import ErrorHandler
from markdown_processor import MarkdownProcessor


class IntegrationTestSuite:
    """Comprehensive integration test suite."""
    
    def __init__(self):
        self.test_results = []
        self.temp_dirs = []
        self.server = None
        self.logger = logging.getLogger(__name__)
        
        # Test configuration
        self.test_config = {
            'server': {
                'name': 'integration-test-server',
                'version': '1.0.0-test',
                'description': 'Integration test server'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'qdrant': {
                'mode': 'local',
                'host': 'localhost',
                'port': 6333,
                'timeout': 30
            },
            'embedding': {
                'model_name': 'all-MiniLM-L6-v2',
                'dimension': 384,
                'device': 'cpu'
            },
            'markdown': {
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'recursive_processing': True,
                'ai_enhancement_enabled': True,
                'ai_analysis_depth': 'standard',
                'ai_content_optimization': True
            }
        }
        
    async def setup(self):
        """Setup test environment."""
        print("🔧 Setting up integration test environment...")
        
        # Create temporary directories
        self.temp_workspace = tempfile.mkdtemp(prefix="mcp_integration_test_")
        self.temp_dirs.append(self.temp_workspace)
        
        # Initialize server components
        config = ServerConfig(config_dict=self.test_config)
        self.server = MCPMemoryServer(config)
        
        # Wait for Qdrant to be ready
        await self.server.memory_manager.qdrant_manager.ensure_ready()
        await self.server.memory_manager.initialize()
        
        print(f"✅ Test environment ready. Workspace: {self.temp_workspace}")
        
    async def cleanup(self):
        """Cleanup test environment."""
        print("🧹 Cleaning up test environment...")
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        # Stop Qdrant if running
        if hasattr(self.server, 'memory_manager'):
            if hasattr(self.server.memory_manager, 'qdrant_manager'):
                try:
                    self.server.memory_manager.qdrant_manager.stop_qdrant()
                except Exception:
                    pass
        
        print("✅ Cleanup completed")
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'duration': duration
        })
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"   Details: {details}")
            
    def create_test_markdown_files(self, count: int = 20) -> List[str]:
        """Create test markdown files."""
        files = []
        base_dir = os.path.join(self.temp_workspace, "test_docs")
        os.makedirs(base_dir, exist_ok=True)
        
        # Create different types of content
        content_templates = {
            'technical': """# Technical Documentation

## Overview
This document covers technical implementation details for {topic}.

## Key Components
- Component A: Handles data processing
- Component B: Manages user interactions
- Component C: Provides analytics

## Best Practices
1. Always validate input data
2. Implement proper error handling
3. Use logging for debugging
4. Write comprehensive tests

## Code Examples
```python
def process_data(input_data):
    # Validate input
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Process data
    result = transform_data(input_data)
    return result
```

## Troubleshooting
Common issues and solutions:
- Issue 1: Data corruption → Solution: Implement checksums
- Issue 2: Performance degradation → Solution: Add caching
""",
            'guide': """# User Guide: {topic}

## Getting Started
This guide will help you get started with {topic}.

## Prerequisites
- Basic understanding of the system
- Access to required tools
- Proper configuration

## Step-by-Step Instructions
1. **Initial Setup**
   - Configure your environment
   - Install required dependencies
   - Verify installation

2. **Basic Usage**
   - Start the application
   - Navigate the interface
   - Perform basic operations

3. **Advanced Features**
   - Custom configurations
   - Integration options
   - Automation setup

## Tips and Tricks
- Use keyboard shortcuts for efficiency
- Customize your workspace
- Regular backups are important

## Common Questions
**Q: How do I reset my configuration?**
A: Use the reset command in settings.

**Q: Can I import existing data?**
A: Yes, use the import wizard.
""",
            'policy': """# Policy Document: {topic}

## Purpose
This policy defines the standards and procedures for {topic}.

## Scope
This policy applies to all team members and systems.

## Policy Statements
1. **Data Security**
   - All data must be encrypted at rest
   - Access requires proper authentication
   - Regular security audits are mandatory

2. **Quality Standards**
   - Code must pass all automated tests
   - Peer review is required for all changes
   - Documentation must be updated

3. **Compliance**
   - Follow industry standards
   - Regular compliance audits
   - Report violations immediately

## Procedures
### Data Handling
1. Classify data sensitivity
2. Apply appropriate protection
3. Monitor access logs
4. Regular reviews

### Incident Response
1. Immediate containment
2. Impact assessment
3. Stakeholder notification
4. Post-incident review

## Responsibilities
- **Team Lead**: Policy enforcement
- **Developers**: Compliance implementation  
- **Security**: Audit and monitoring
""",
            'meeting_notes': """# Meeting Notes: {topic}

**Date:** 2024-01-15
**Attendees:** Alice, Bob, Charlie, Diana
**Duration:** 60 minutes

## Agenda
1. Project status update
2. Technical challenges
3. Resource allocation
4. Next steps

## Discussion Points

### Project Status
- **Progress**: 75% complete
- **Milestones**: On track for Q1 delivery
- **Blockers**: External API integration pending

### Technical Challenges
- **Performance**: Need optimization for large datasets
- **Security**: Implementing additional auth layers
- **Integration**: Third-party service compatibility

### Decisions Made
1. Extend deadline by 2 weeks for thorough testing
2. Allocate additional developer resources
3. Schedule weekly check-ins

### Action Items
- [ ] Alice: Contact vendor for API documentation
- [ ] Bob: Optimize database queries  
- [ ] Charlie: Set up staging environment
- [ ] Diana: Update project timeline

## Next Meeting
**Date:** 2024-01-22
**Agenda:** Review progress on action items
"""
        }
        
        topics = [
            "Data Processing Pipeline", "User Authentication System", "API Gateway Configuration",
            "Database Optimization", "Security Framework", "Testing Strategy", "Deployment Process",
            "Monitoring Setup", "Error Handling", "Performance Tuning", "Code Review Process",
            "Documentation Standards", "Version Control", "CI/CD Pipeline", "System Architecture",
            "User Interface Design", "Data Migration", "Backup Procedures", "Disaster Recovery",
            "Team Collaboration"
        ]
        
        for i in range(count):
            topic = topics[i % len(topics)]
            content_type = list(content_templates.keys())[i % len(content_templates)]
            
            filename = f"{i+1:02d}_{content_type}_{topic.lower().replace(' ', '_')}.md"
            filepath = os.path.join(base_dir, filename)
            
            content = content_templates[content_type].format(topic=topic)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files.append(filepath)
            
        return files
        
    async def test_basic_memory_operations(self):
        """Test basic memory operations."""
        start_time = time.time()
        
        try:
            # Test agent context setting
            await self.server.memory_manager.set_agent_context(
                "test_agent_1", "integration_test", "Integration test agent"
            )
            
            # Test adding to different memory types
            global_content = "Global knowledge: Always validate input data before processing"
            global_result = await self.server.memory_manager.add_to_global_memory(
                global_content, category="best_practices"
            )
            
            learned_content = "Lesson learned: Retry logic prevents cascading failures"
            learned_result = await self.server.memory_manager.add_to_learned_memory(
                learned_content, pattern_type="best_practice"
            )
            
            agent_content = "Agent-specific note: Use conservative timeout values"
            agent_result = await self.server.memory_manager.add_to_agent_memory(
                agent_content, agent_id="test_agent_1"
            )
            
            # Test memory querying
            query_results = await self.server.memory_manager.query_memory(
                "input validation best practices", memory_types=["global"], limit=5
            )
            
            # Verify results
            success = (
                global_result['success'] and 
                learned_result['success'] and 
                agent_result['success'] and
                len(query_results) > 0
            )
            
            details = f"Added {len([global_result, learned_result, agent_result])} memories, found {len(query_results)} query results"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("Basic Memory Operations", success, details, duration)
        return success
        
    async def test_markdown_processing_pipeline(self):
        """Test complete markdown processing pipeline."""
        start_time = time.time()
        
        try:
            # Create test markdown files
            test_files = self.create_test_markdown_files(10)
            
            # Test individual file processing
            processor = MarkdownProcessor()
            
            # Process a single file
            test_file = test_files[0]
            analysis = await processor.analyze_file(test_file, ai_enhanced=True)
            
            # Test directory processing
            test_dir = os.path.dirname(test_files[0])
            overview = processor.scan_workspace(test_dir, recursive=False)
            
            # Test optimization
            optimization = await processor.optimize_content_for_storage(
                test_file, target_memory_type="global", ai_optimization=True
            )
            
            # Test batch processing
            batch_results = await processor.process_directory(
                test_dir, memory_type="global", batch_size=5
            )
            
            success = (
                analysis is not None and
                len(overview['files']) == 10 and
                optimization is not None and
                len(batch_results) > 0
            )
            
            details = f"Processed {len(test_files)} files, analysis: {bool(analysis)}, optimization: {bool(optimization)}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("Markdown Processing Pipeline", success, details, duration)
        return success
        
    async def test_multi_agent_scenarios(self):
        """Test multi-agent collaboration scenarios."""
        start_time = time.time()
        
        try:
            agents = ["frontend_dev", "backend_dev", "devops_engineer", "qa_tester"]
            
            # Initialize multiple agents
            for agent_id in agents:
                await self.server.memory_manager.set_agent_context(
                    agent_id, "development", f"Role: {agent_id.replace('_', ' ').title()}"
                )
                
                # Add agent-specific knowledge
                agent_knowledge = {
                    "frontend_dev": "React best practices: Use hooks for state management",
                    "backend_dev": "API design: Always implement rate limiting",
                    "devops_engineer": "Deployment: Use blue-green deployment strategy",
                    "qa_tester": "Testing: Automate regression tests for critical paths"
                }
                
                await self.server.memory_manager.add_to_agent_memory(
                    agent_knowledge[agent_id], agent_id=agent_id
                )
            
            # Test cross-agent queries
            query_results = {}
            for agent_id in agents:
                # Switch context to current agent
                await self.server.memory_manager.set_agent_context(
                    agent_id, "development", f"Querying as {agent_id}"
                )
                
                # Query for relevant knowledge
                results = await self.server.memory_manager.query_memory(
                    "best practices deployment testing", 
                    memory_types=["global", "agent"], 
                    limit=10
                )
                query_results[agent_id] = results
            
            # Test memory isolation
            backend_query = await self.server.memory_manager.query_memory(
                "API rate limiting", memory_types=["agent"], limit=5
            )
            
            success = (
                len(query_results) == len(agents) and
                all(len(results) >= 0 for results in query_results.values()) and
                len(backend_query) > 0  # Should find backend dev's knowledge
            )
            
            details = f"Initialized {len(agents)} agents, queries: {[len(r) for r in query_results.values()]}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("Multi-Agent Scenarios", success, details, duration)
        return success
        
    async def test_system_health_monitoring(self):
        """Test system health monitoring capabilities."""
        start_time = time.time()
        
        try:
            # Test system health check
            health = self.server.get_system_health()
            
            # Test component status
            components = ['memory_manager', 'qdrant', 'embedding_model']
            component_status = {}
            
            for component in components:
                if component == 'memory_manager':
                    component_status[component] = hasattr(self.server, 'memory_manager')
                elif component == 'qdrant':
                    component_status[component] = await self.server.memory_manager.qdrant_manager.health_check()
                elif component == 'embedding_model':
                    # Test embedding generation
                    try:
                        embedding = self.server.memory_manager.embedding_model.encode("test")
                        component_status[component] = len(embedding) > 0
                    except:
                        component_status[component] = False
            
            # Test error statistics
            error_handler = ErrorHandler()
            error_stats = error_handler.get_error_statistics()
            
            success = (
                health is not None and
                all(component_status.values()) and
                isinstance(error_stats, dict)
            )
            
            details = f"Health check: {bool(health)}, components: {sum(component_status.values())}/{len(components)}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("System Health Monitoring", success, details, duration)
        return success
        
    async def test_error_recovery_mechanisms(self):
        """Test error handling and recovery mechanisms."""
        start_time = time.time()
        
        try:
            error_handler = ErrorHandler()
            
            # Test retry decorator with controlled failure
            retry_count = 0
            
            @error_handler.retry_with_exponential_backoff(max_attempts=3, base_delay=0.1)
            async def failing_operation():
                nonlocal retry_count
                retry_count += 1
                if retry_count < 3:
                    raise Exception(f"Controlled failure #{retry_count}")
                return "success"
            
            # Test successful retry
            result = await failing_operation()
            retry_success = (result == "success" and retry_count == 3)
            
            # Test connection recovery
            recovery_test = False
            try:
                # Simulate connection issue and recovery
                await self.server.memory_manager.qdrant_manager.ensure_ready()
                recovery_test = True
            except:
                recovery_test = False
            
            # Test error statistics tracking
            stats = error_handler.get_error_statistics()
            stats_test = isinstance(stats, dict) and 'total_errors' in stats
            
            success = retry_success and recovery_test and stats_test
            details = f"Retry: {retry_success}, Recovery: {recovery_test}, Stats: {stats_test}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("Error Recovery Mechanisms", success, details, duration)
        return success
        
    async def test_performance_large_dataset(self):
        """Test performance with larger dataset."""
        start_time = time.time()
        
        try:
            # Create larger dataset
            test_files = self.create_test_markdown_files(50)  # More files for performance test
            
            # Measure processing time
            process_start = time.time()
            
            # Process files in batches
            processor = MarkdownProcessor()
            test_dir = os.path.dirname(test_files[0])
            
            batch_results = await processor.process_directory(
                test_dir, memory_type="global", batch_size=10
            )
            
            process_time = time.time() - process_start
            
            # Test query performance
            query_start = time.time()
            
            # Perform multiple queries
            query_times = []
            for i in range(10):
                query_start_single = time.time()
                results = await self.server.memory_manager.query_memory(
                    f"technical documentation best practices {i}", 
                    limit=5
                )
                query_times.append(time.time() - query_start_single)
            
            avg_query_time = sum(query_times) / len(query_times)
            
            # Performance criteria
            performance_ok = (
                process_time < 120  # Should process 50 files in under 2 minutes
                and avg_query_time < 2  # Average query under 2 seconds
                and len(batch_results) > 0
            )
            
            success = performance_ok
            details = f"Processed {len(test_files)} files in {process_time:.1f}s, avg query: {avg_query_time:.2f}s"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("Performance Large Dataset", success, details, duration)
        return success
        
    async def test_mcp_protocol_compliance(self):
        """Test MCP protocol compliance and tool functionality."""
        start_time = time.time()
        
        try:
            # Test MCP server initialization
            tools = self.server.list_tools()
            resources = self.server.list_resources()
            prompts = self.server.list_prompts()
            
            # Expected tool count (from implementation)
            expected_tools = [
                'set_agent_context', 'add_to_global_memory', 'add_to_learned_memory',
                'add_to_agent_memory', 'query_memory', 'compare_against_learned_memory',
                'scan_workspace_markdown', 'analyze_markdown_content', 
                'optimize_content_for_storage', 'process_markdown_directory',
                'initialize_new_agent', 'system_health'
            ]
            
            tool_names = [tool.name for tool in tools]
            tools_ok = all(tool in tool_names for tool in expected_tools)
            
            # Test resource availability
            expected_resources = ['memory://status']
            resource_uris = [resource.uri for resource in resources]
            resources_ok = all(resource in resource_uris for resource in expected_resources)
            
            # Test prompt availability  
            expected_prompts = ['agent_startup', 'memory_optimization']
            prompt_names = [prompt.name for prompt in prompts]
            prompts_ok = any(prompt in prompt_names for prompt in expected_prompts)
            
            success = tools_ok and resources_ok and prompts_ok
            details = f"Tools: {len(tools)}/{len(expected_tools)}, Resources: {len(resources)}, Prompts: {len(prompts)}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
            
        duration = time.time() - start_time
        self.log_test_result("MCP Protocol Compliance", success, details, duration)
        return success
        
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Comprehensive Integration Tests")
        print("=" * 60)
        
        await self.setup()
        
        # Run all test scenarios
        test_methods = [
            self.test_basic_memory_operations,
            self.test_markdown_processing_pipeline,
            self.test_multi_agent_scenarios, 
            self.test_system_health_monitoring,
            self.test_error_recovery_mechanisms,
            self.test_performance_large_dataset,
            self.test_mcp_protocol_compliance
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL {test_method.__name__}: {str(e)}")
                
        await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Integration Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests PASSED! System is ready for production.")
        else:
            print(f"⚠️ {total - passed} tests FAILED. Review issues before deployment.")
            
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']} ({result['duration']:.2f}s)")
            if result['details']:
                print(f"   {result['details']}")
                
        return passed == total


async def main():
    """Run the integration test suite."""
    suite = IntegrationTestSuite()
    success = await suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())