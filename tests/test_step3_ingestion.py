#!/usr/bin/env python3
"""
Step 3 Tests: Complete Markdown Ingestion Pipeline

Test the three main ingestion tools:
- process_markdown_file: Single file processing
- batch_process_markdown_files: Multi-file processing
- batch_process_directory: Directory processing
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock

from src.tool_handlers import ToolHandlers
from src.memory_manager import QdrantMemoryManager
from src.markdown_processor import MarkdownProcessor
from src.mcp_server import MemoryMCPServer


class TestStep3Ingestion:
    """Test Step 3: Complete Markdown Ingestion Pipeline"""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up test environment"""
        # Create temp directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Mock dependencies
        self.mock_memory_manager = Mock(spec=QdrantMemoryManager)
        self.mock_markdown_processor = Mock(spec=MarkdownProcessor)
        
        # Configure mock memory manager
        self.mock_memory_manager.add_file_metadata = AsyncMock(
            return_value=True
        )
        self.mock_memory_manager.get_file_metadata = AsyncMock(
            return_value=None
        )
        self.mock_memory_manager.check_file_processed = AsyncMock(
            return_value=False
        )
        self.mock_memory_manager.validate_and_deduplicate = AsyncMock(
            return_value={
                'success': True,
                'processed': 5,
                'duplicates_removed': 1,
                'near_misses': 2
            }
        )
        
        # Configure mock markdown processor
        self.mock_markdown_processor.analyze_content = AsyncMock(
            return_value={'memory_type': 'learned', 'confidence': 0.8}
        )
        self.mock_markdown_processor.optimize_content = AsyncMock(
            return_value="Optimized content"
        )
        self.mock_markdown_processor.chunk_content = AsyncMock(
            return_value=["chunk1", "chunk2", "chunk3"]
        )
        self.mock_memory_manager.store_memory = AsyncMock(
            return_value={'success': True, 'stored': 3}
        )
        
        # Create tool handlers with mocked dependencies
        self.tool_handlers = ToolHandlers(
            self.mock_memory_manager,
            self.mock_markdown_processor
        )

    def teardown_method(self) -> None:
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def create_test_file(
        self,
        name: str,
        content: str = "# Test Content\nThis is test content."
    ) -> str:
        """Create a test markdown file"""
        file_path = os.path.join(self.temp_dir, name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files.append(file_path)
        return file_path

    # Test 1: Single File Processing
    async def test_process_markdown_file_success(self) -> None:
        """Test successful single file processing"""
        file_path = self.create_test_file("test.md")
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned',
            'auto_suggest': False
        })
        
        assert result['success'] is True
        assert result['file'] == file_path
        assert result['memory_type'] == 'learned'
        assert 'chunks_stored' in result
        assert 'deduplication_stats' in result
        
        # Verify calls to dependencies
        self.mock_memory_manager.add_file_metadata.assert_called_once()
        self.mock_markdown_processor.optimize_content.assert_called_once()
        self.mock_markdown_processor.chunk_content.assert_called_once()
        self.mock_memory_manager.store_memory.assert_called_once()
        self.mock_memory_manager.validate_and_deduplicate.assert_called_once()

    async def test_process_markdown_file_not_found(self) -> None:
        """Test handling of non-existent files"""
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': '/nonexistent/file.md',
            'memory_type': 'learned'
        })
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    # Test 2: Batch File Processing
    async def test_batch_process_markdown_files_success(self) -> None:
        """Test successful batch file processing"""
        file1 = self.create_test_file("file1.md", "# File 1\nContent 1")
        file2 = self.create_test_file("file2.md", "# File 2\nContent 2")
        
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': [
                {'path': file1, 'memory_type': 'global'},
                {'path': file2, 'memory_type': 'learned'}
            ]
        })
        
        assert result['success'] is True
        assert result['total_files'] == 2
        assert result['processed_files'] == 2
        assert result['failed_files'] == 0
        assert len(result['results']) == 2
        
        # Check individual file results
        file_results = {r['file']: r for r in result['results']}
        assert file_results[file1]['memory_type'] == 'global'
        assert file_results[file2]['memory_type'] == 'learned'

    async def test_batch_process_empty_list(self) -> None:
        """Test batch processing with empty file list"""
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': []
        })
        
        assert result['success'] is True
        assert result['total_files'] == 0
        assert result['processed_files'] == 0

    # Test 3: Directory Processing
    async def test_batch_process_directory_success(self) -> None:
        """Test successful directory processing"""
        # Create test directory structure
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        
        # Create files in root and subdirectory
        self.create_test_file("root_file.md", "# Root File\nRoot content")
        self.create_test_file(
            os.path.join("subdir", "sub_file.md"),
            "# Sub File\nSub content"
        )
        
        # Create non-markdown file (should be ignored)
        non_md_path = os.path.join(self.temp_dir, "text_file.txt")
        with open(non_md_path, 'w') as f:
            f.write("Not markdown")
        
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': self.temp_dir,
            'memory_type': 'global',
            'recursive': True
        })
        
        assert result['success'] is True
        assert result['directory'] == self.temp_dir
        assert result['files_found'] == 2  # Only .md files
        assert result['processed_files'] == 2
        assert result['failed_files'] == 0
        
        # Verify all markdown files were processed
        processed_files = [r['file'] for r in result['results']]
        assert any('root_file.md' in f for f in processed_files)
        assert any('sub_file.md' in f for f in processed_files)

    async def test_batch_process_directory_not_found(self) -> None:
        """Test handling of non-existent directory"""
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': '/nonexistent/directory',
            'memory_type': 'global'
        })
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    # Test 4: MCP Server Integration
    async def test_mcp_server_tool_registration(self) -> None:
        """Test MCP server has ingestion tools registered"""
        mock_handlers = Mock(spec=ToolHandlers)
        server = MemoryMCPServer(mock_handlers)
        
        # Get available tools
        tools = [tool['name'] for tool in server.get_available_tools()]
        
        # Verify all Step 3 tools are registered
        expected_tools = [
            'process_markdown_file',
            'batch_process_markdown_files', 
            'batch_process_directory'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tools

    # Test 5: File Metadata Integration
    async def test_file_metadata_tracking(self) -> None:
        """Test file metadata is properly tracked"""
        file_path = self.create_test_file("test.md")
        
        # Mock metadata responses
        expected_metadata = {
            'path': file_path,
            'hash': 'mock_hash',
            'processed_at': '2024-01-01T00:00:00',
            'memory_type': 'learned',
            'chunks_stored': 3
        }
        self.mock_memory_manager.add_file_metadata.return_value = expected_metadata
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned'
        })
        
        assert result['success'] is True
        
        # Verify metadata was added
        self.mock_memory_manager.add_file_metadata.assert_called_once()
        call_args = self.mock_memory_manager.add_file_metadata.call_args[1]
        assert call_args['path'] == file_path
        assert call_args['memory_type'] == 'learned'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock

from src.tool_handlers import ToolHandlers
from src.memory_manager import MemoryManager
from src.markdown_processor import MarkdownProcessor
from src.mcp_server import MCPServer


class TestStep3Ingestion:
    """Test Step 3: Complete Markdown Ingestion Pipeline"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Set up test environment"""
        # Create temp directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Mock dependencies
        self.mock_memory_manager = Mock(spec=MemoryManager)
        self.mock_markdown_processor = Mock(spec=MarkdownProcessor)
        
        # Configure mock memory manager
        self.mock_memory_manager.add_file_metadata = AsyncMock(
            return_value=True
        )
        self.mock_memory_manager.get_file_metadata = AsyncMock(
            return_value=None
        )
        self.mock_memory_manager.check_file_processed = AsyncMock(
            return_value=False
        )
        self.mock_memory_manager.validate_and_deduplicate = AsyncMock(
            return_value={
                'success': True,
                'processed': 5,
                'duplicates_removed': 1,
                'near_misses': 2
            }
        )
        
        # Configure mock markdown processor
        self.mock_markdown_processor.analyze_content = AsyncMock(
            return_value={'memory_type': 'learned', 'confidence': 0.8}
        )
        self.mock_markdown_processor.optimize_content = AsyncMock(
            return_value="Optimized content"
        )
        self.mock_markdown_processor.chunk_content = AsyncMock(
            return_value=["chunk1", "chunk2", "chunk3"]
        )
        self.mock_memory_manager.store_memory = AsyncMock(
            return_value={'success': True, 'stored': 3}
        )
        
        # Create tool handlers with mocked dependencies
        self.tool_handlers = ToolHandlers(
            self.mock_memory_manager,
            self.mock_markdown_processor
        )
        
        yield
        
        # Cleanup
        shutil.rmtree(self.temp_dir)

    def create_test_file(
        self,
        name: str,
        content: str = "# Test Content\nThis is test content."
    ) -> str:
        """Create a test markdown file"""
        file_path = os.path.join(self.temp_dir, name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files.append(file_path)
        return file_path

    def create_test_directory_structure(self) -> str:
        """Create nested directory with markdown files"""
        # Create subdirectory
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        
        # Create files in root and subdirectory
        self.create_test_file("root_file.md", "# Root File\nRoot content")
        self.create_test_file(
            os.path.join("subdir", "sub_file.md"),
            "# Sub File\nSub content"
        )
        
        # Create non-markdown file (should be ignored)
        non_md_path = os.path.join(self.temp_dir, "text_file.txt")
        with open(non_md_path, 'w') as f:
            f.write("Not markdown")
            
        return self.temp_dir

    # Test 1: Single File Processing
    async def test_process_markdown_file_success(self):
        """Test successful single file processing"""
        file_path = self.create_test_file("test.md")
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned',
            'auto_suggest': False
        })
        
        assert result['success'] is True
        assert result['file'] == file_path
        assert result['memory_type'] == 'learned'
        assert 'chunks_stored' in result
        assert 'deduplication_stats' in result
        
        # Verify calls to dependencies
        self.mock_memory_manager.add_file_metadata.assert_called_once()
        self.mock_markdown_processor.optimize_content.assert_called_once()
        self.mock_markdown_processor.chunk_content.assert_called_once()
        self.mock_memory_manager.store_memory.assert_called_once()
        self.mock_memory_manager.validate_and_deduplicate.assert_called_once()

    async def test_process_markdown_file_auto_suggest(self):
        """Test file processing with auto memory type suggestion"""
        file_path = self.create_test_file("test.md")
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'auto_suggest': True
        })
        
        assert result['success'] is True
        assert result['memory_type'] == 'learned'  # From mock analyzer
        
        # Verify analysis was called
        self.mock_markdown_processor.analyze_content.assert_called_once()

    async def test_process_markdown_file_already_processed(self):
        """Test handling of already processed files"""
        file_path = self.create_test_file("test.md")
        
        # Mock file as already processed
        self.mock_memory_manager.check_file_processed.return_value = True
        self.mock_memory_manager.get_file_metadata.return_value = {
            'processed_at': '2024-01-01T00:00:00',
            'memory_type': 'global'
        }
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned'
        })
        
        assert result['success'] is True
        assert 'already_processed' in result['message']
        assert result['memory_type'] == 'global'  # From existing metadata

    async def test_process_markdown_file_not_found(self):
        """Test handling of non-existent files"""
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': '/nonexistent/file.md',
            'memory_type': 'learned'
        })
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    async def test_process_markdown_file_processing_error(self):
        """Test handling of processing errors"""
        file_path = self.create_test_file("test.md")
        
        # Mock processing error
        self.mock_markdown_processor.optimize_content.side_effect = Exception(
            "Processing failed"
        )
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned'
        })
        
        assert result['success'] is False
        assert 'processing failed' in result['error'].lower()

    # Test 2: Batch File Processing
    async def test_batch_process_markdown_files_success(self):
        """Test successful batch file processing"""
        file1 = self.create_test_file("file1.md", "# File 1\nContent 1")
        file2 = self.create_test_file("file2.md", "# File 2\nContent 2")
        
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': [
                {'path': file1, 'memory_type': 'global'},
                {'path': file2, 'memory_type': 'learned'}
            ],
            'default_memory_type': 'agent'
        })
        
        assert result['success'] is True
        assert result['total_files'] == 2
        assert result['processed_files'] == 2
        assert result['failed_files'] == 0
        assert len(result['results']) == 2
        
        # Check individual file results
        file_results = {r['file']: r for r in result['results']}
        assert file_results[file1]['memory_type'] == 'global'
        assert file_results[file2]['memory_type'] == 'learned'

    async def test_batch_process_mixed_success_failure(self):
        """Test batch processing with some failures"""
        file1 = self.create_test_file("file1.md")
        file2_path = "/nonexistent/file2.md"
        
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': [
                {'path': file1, 'memory_type': 'global'},
                {'path': file2_path, 'memory_type': 'learned'}
            ]
        })
        
        assert result['success'] is True  # Overall success even with failures
        assert result['total_files'] == 2
        assert result['processed_files'] == 1
        assert result['failed_files'] == 1
        
        # Check results
        results = result['results']
        success_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        assert len(success_results) == 1
        assert len(failed_results) == 1
        assert success_results[0]['file'] == file1
        assert failed_results[0]['file'] == file2_path

    async def test_batch_process_with_default_memory_type(self):
        """Test batch processing using default memory type"""
        file1 = self.create_test_file("file1.md")
        file2 = self.create_test_file("file2.md")
        
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': [
                {'path': file1},  # No memory_type specified
                {'path': file2, 'memory_type': 'learned'}
            ],
            'default_memory_type': 'global'
        })
        
        assert result['success'] is True
        
        # Check that first file used default memory type
        file_results = {r['file']: r for r in result['results']}
        assert file_results[file1]['memory_type'] == 'global'  # Default
        assert file_results[file2]['memory_type'] == 'learned'  # Specified

    async def test_batch_process_empty_list(self):
        """Test batch processing with empty file list"""
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': []
        })
        
        assert result['success'] is True
        assert result['total_files'] == 0
        assert result['processed_files'] == 0

    # Test 3: Directory Processing
    async def test_batch_process_directory_success(self):
        """Test successful directory processing"""
        self.create_test_directory_structure()
        
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': self.temp_dir,
            'memory_type': 'global',
            'recursive': True
        })
        
        assert result['success'] is True
        assert result['directory'] == self.temp_dir
        assert result['files_found'] == 2  # Only .md files
        assert result['processed_files'] == 2
        assert result['failed_files'] == 0
        
        # Verify all markdown files were processed
        processed_files = [r['file'] for r in result['results']]
        assert any('root_file.md' in f for f in processed_files)
        assert any('sub_file.md' in f for f in processed_files)

    async def test_batch_process_directory_non_recursive(self):
        """Test directory processing without recursion"""
        self.create_test_directory_structure()
        
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': self.temp_dir,
            'memory_type': 'global',
            'recursive': False
        })
        
        assert result['success'] is True
        assert result['files_found'] == 1  # Only root level .md file
        
        # Verify only root file was processed
        processed_files = [r['file'] for r in result['results']]
        assert any('root_file.md' in f for f in processed_files)
        assert not any('sub_file.md' in f for f in processed_files)

    async def test_batch_process_directory_with_auto_suggest(self):
        """Test directory processing with memory type auto-suggestion"""
        self.create_test_directory_structure()
        
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': self.temp_dir,
            'recursive': True
            # No memory_type specified, should use auto-suggestion
        })
        
        assert result['success'] is True
        
        # Check that files used suggested memory type
        for file_result in result['results']:
            assert file_result['memory_type'] == 'learned'  # From mock

    async def test_batch_process_directory_not_found(self):
        """Test handling of non-existent directory"""
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': '/nonexistent/directory',
            'memory_type': 'global'
        })
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()

    async def test_batch_process_directory_no_markdown_files(self):
        """Test directory with no markdown files"""
        # Create directory with only non-markdown files
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)
        
        with open(os.path.join(empty_dir, "text.txt"), 'w') as f:
            f.write("Not markdown")
        
        result = await self.tool_handlers.handle_batch_process_directory({
            'directory': empty_dir,
            'memory_type': 'global'
        })
        
        assert result['success'] is True
        assert result['files_found'] == 0
        assert len(result['results']) == 0

    # Test 4: File Metadata Integration
    async def test_file_metadata_tracking(self):
        """Test file metadata is properly tracked"""
        file_path = self.create_test_file("test.md")
        
        # Mock metadata responses
        expected_metadata = {
            'path': file_path,
            'hash': 'mock_hash',
            'processed_at': '2024-01-01T00:00:00',
            'memory_type': 'learned',
            'chunks_stored': 3
        }
        self.mock_memory_manager.add_file_metadata.return_value = expected_metadata
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned'
        })
        
        assert result['success'] is True
        
        # Verify metadata was added
        self.mock_memory_manager.add_file_metadata.assert_called_once()
        call_args = self.mock_memory_manager.add_file_metadata.call_args[1]
        assert call_args['path'] == file_path
        assert call_args['memory_type'] == 'learned'

    # Test 5: Progress Tracking and Reporting
    async def test_progress_tracking(self):
        """Test progress tracking in batch operations"""
        files = [
            self.create_test_file(f"file{i}.md", f"# File {i}\nContent {i}")
            for i in range(5)
        ]
        
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': [
                {'path': f, 'memory_type': 'global'} for f in files
            ]
        })
        
        assert result['success'] is True
        assert result['total_files'] == 5
        assert result['processed_files'] == 5
        assert result['failed_files'] == 0
        
        # Verify progress information
        assert 'processing_time' in result
        assert 'average_time_per_file' in result
        assert len(result['results']) == 5

    # Test 6: Error Recovery and Resilience
    async def test_error_recovery_in_batch(self):
        """Test error recovery in batch processing"""
        file1 = self.create_test_file("file1.md")
        file2 = self.create_test_file("file2.md")
        file3 = self.create_test_file("file3.md")
        
        # Mock error for middle file
        original_store = self.mock_memory_manager.store_memory
        def mock_store_with_error(*args, **kwargs):
            if 'file2.md' in str(args) or 'file2.md' in str(kwargs):
                raise Exception("Storage error")
            return original_store(*args, **kwargs)
        
        self.mock_memory_manager.store_memory.side_effect = mock_store_with_error
        
        result = await self.tool_handlers.handle_batch_process_markdown_files({
            'file_assignments': [
                {'path': file1, 'memory_type': 'global'},
                {'path': file2, 'memory_type': 'global'},
                {'path': file3, 'memory_type': 'global'}
            ]
        })
        
        assert result['success'] is True  # Overall success despite one failure
        assert result['total_files'] == 3
        assert result['processed_files'] == 2
        assert result['failed_files'] == 1
        
        # Check specific results
        results = result['results']
        failed_result = next(r for r in results if not r['success'])
        assert 'file2.md' in failed_result['file']
        assert 'storage error' in failed_result['error'].lower()

    # Test 7: Integration with Deduplication
    async def test_deduplication_integration(self):
        """Test integration with deduplication system"""
        file_path = self.create_test_file("test.md")
        
        # Mock deduplication results
        dedup_stats = {
            'success': True,
            'processed': 10,
            'duplicates_removed': 2,
            'near_misses': 3,
            'collection': 'learned_memory'
        }
        self.mock_memory_manager.validate_and_deduplicate.return_value = dedup_stats
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'learned'
        })
        
        assert result['success'] is True
        assert result['deduplication_stats'] == dedup_stats
        
        # Verify deduplication was called with correct collection
        self.mock_memory_manager.validate_and_deduplicate.assert_called_once()
        call_args = self.mock_memory_manager.validate_and_deduplicate.call_args[1]
        assert call_args['collection'] == 'learned_memory'

    # Test 8: MCP Server Integration
    async def test_mcp_server_tool_registration(self):
        """Test MCP server has ingestion tools registered"""
        mock_handlers = Mock(spec=ToolHandlers)
        server = MCPServer(mock_handlers)
        
        # Get available tools
        tools = [tool['name'] for tool in server.get_available_tools()]
        
        # Verify all Step 3 tools are registered
        expected_tools = [
            'process_markdown_file',
            'batch_process_markdown_files', 
            'batch_process_directory'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tools

    async def test_mcp_tool_schemas(self):
        """Test MCP tool schemas are properly defined"""
        mock_handlers = Mock(spec=ToolHandlers)
        server = MCPServer(mock_handlers)
        
        tools = {tool['name']: tool for tool in server.get_available_tools()}
        
        # Test process_markdown_file schema
        pmf_tool = tools['process_markdown_file']
        assert pmf_tool['inputSchema']['type'] == 'object'
        assert 'path' in pmf_tool['inputSchema']['properties']
        assert 'memory_type' in pmf_tool['inputSchema']['properties']
        assert pmf_tool['inputSchema']['required'] == ['path']
        
        # Test batch_process_markdown_files schema
        bpmf_tool = tools['batch_process_markdown_files']
        assert 'file_assignments' in bpmf_tool['inputSchema']['properties']
        assert bpmf_tool['inputSchema']['required'] == ['file_assignments']
        
        # Test batch_process_directory schema
        bpd_tool = tools['batch_process_directory']
        assert 'directory' in bpd_tool['inputSchema']['properties']
        assert bpd_tool['inputSchema']['required'] == []

    # Test 9: Memory Type Handling
    async def test_memory_type_validation(self):
        """Test memory type validation and agent_id handling"""
        file_path = self.create_test_file("test.md")
        
        # Test agent memory type requires agent_id
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'agent',
            'agent_id': 'test_agent'
        })
        
        assert result['success'] is True
        assert result['memory_type'] == 'agent'
        assert result['agent_id'] == 'test_agent'

    async def test_invalid_memory_type_fallback(self):
        """Test handling of invalid memory types"""
        file_path = self.create_test_file("test.md")
        
        # Mock analyzer for fallback suggestion
        self.mock_markdown_processor.analyze_content.return_value = {
            'memory_type': 'global', 
            'confidence': 0.7
        }
        
        result = await self.tool_handlers.handle_process_markdown_file({
            'path': file_path,
            'memory_type': 'invalid_type',  # Invalid type
            'auto_suggest': True
        })
        
        assert result['success'] is True
        assert result['memory_type'] == 'global'  # Fallback from analyzer

if __name__ == '__main__':
    pytest.main([__file__, '-v'])