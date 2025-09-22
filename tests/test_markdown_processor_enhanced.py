"""
Tests for enhanced markdown processing functionality in Step 1.
Tests directory scanning, memory type analysis, content optimization, and policy processing.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from src.markdown_processor import MarkdownProcessor


@pytest.fixture
def markdown_processor():
    """Create a MarkdownProcessor instance for testing."""
    return MarkdownProcessor()


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Test Document

This is a sample document for testing markdown processing.

## Features

- Content analysis
- Memory type suggestions
- AI integration hooks

## Code Example

```python
def hello_world():
    print("Hello, World!")
```

## Links and References

See [documentation](https://example.com) for more details.

| Feature | Status |
|---------|--------|
| Analysis | ✅ |
| Optimization | ✅ |
"""


@pytest.fixture
def policy_content():
    """Sample policy content for testing."""
    return """# Project Policies

## Core Principles

[P-001] All code must be documented
[P-002] Tests are required for new features

## Forbidden Actions

[F-101] Never commit directly to main branch
[F-102] Do not hardcode credentials

## Required Sections

[R-201] README must include installation instructions
[R-202] All functions must have type hints
"""


@pytest.fixture
def temp_directory():
    """Create a temporary directory with test markdown files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "readme.md").write_text("# README\nThis is documentation.")
        (temp_path / "lessons.md").write_text("# Lessons\nLearned from experience.")
        (temp_path / "personal.md").write_text("# Personal Notes\nMy TODO list.")
        
        # Create subdirectory
        subdir = temp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.md").write_text("# Nested\nNested documentation.")
        
        yield temp_path


@pytest.fixture
def policy_directory():
    """Create a temporary policy directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create policy files
        (temp_path / "principles.md").write_text("""# Core Principles
[P-001] Code quality is important
[P-002] Documentation is required
""")
        
        (temp_path / "rules.md").write_text("""# Rules
[F-101] No direct commits to main
[R-201] All PRs need review
""")
        
        yield temp_path


class TestMarkdownProcessorEnhanced:
    """Test enhanced markdown processor functionality."""

    @pytest.mark.asyncio
    async def test_scan_directory_for_markdown(self, markdown_processor, temp_directory):
        """Test directory scanning for markdown files."""
        files = await markdown_processor.scan_directory_for_markdown(
            str(temp_directory), recursive=True
        )
        
        assert len(files) == 4  # 3 top-level + 1 nested
        assert all('path' in file for file in files)
        assert all('name' in file for file in files)
        assert all('size' in file for file in files)
        
        # Test non-recursive
        files_non_recursive = await markdown_processor.scan_directory_for_markdown(
            str(temp_directory), recursive=False
        )
        assert len(files_non_recursive) == 3  # Only top-level files

    @pytest.mark.asyncio
    async def test_scan_nonexistent_directory(self, markdown_processor):
        """Test scanning non-existent directory raises error."""
        with pytest.raises(FileNotFoundError):
            await markdown_processor.scan_directory_for_markdown("/nonexistent/path")

    def test_analyze_content_for_memory_type(self, markdown_processor, sample_markdown_content):
        """Test content analysis and memory type suggestions."""
        analysis = markdown_processor.analyze_content_for_memory_type(
            sample_markdown_content, "test_doc.md", suggest_memory_type=True
        )
        
        assert 'content_length' in analysis
        assert 'word_count' in analysis
        assert 'sections' in analysis
        assert 'suggested_memory_type' in analysis
        assert 'confidence' in analysis
        assert 'reasoning' in analysis
        
        assert analysis['content_length'] > 0
        assert analysis['word_count'] > 0
        assert analysis['sections'] > 0
        assert analysis['suggested_memory_type'] in ['global', 'learned', 'agent']
        assert 0 <= analysis['confidence'] <= 1

    def test_memory_type_heuristic_global(self, markdown_processor):
        """Test memory type suggestion for global content."""
        global_content = """# API Documentation
        
This is the complete API reference for our system.
Includes all endpoints, parameters, and examples.
"""
        
        analysis = markdown_processor.analyze_content_for_memory_type(
            global_content, "api_docs.md", suggest_memory_type=True
        )
        
        # Should suggest global for documentation
        assert analysis['suggested_memory_type'] == 'global'

    def test_memory_type_heuristic_learned(self, markdown_processor):
        """Test memory type suggestion for learned content."""
        learned_content = """# Lessons Learned
        
Key insights from our last project:
- Pattern: Always validate input
- Mistake: Not testing edge cases
- Experience: User feedback is crucial
"""
        
        analysis = markdown_processor.analyze_content_for_memory_type(
            learned_content, "lessons.md", suggest_memory_type=True
        )
        
        # Should suggest learned for lessons and insights
        assert analysis['suggested_memory_type'] == 'learned'

    def test_memory_type_heuristic_agent(self, markdown_processor):
        """Test memory type suggestion for agent content."""
        agent_content = """# Personal TODO
        
My tasks for today:
- Draft proposal
- Review PRs
- Personal notes on meeting
"""
        
        analysis = markdown_processor.analyze_content_for_memory_type(
            agent_content, "personal_todo.md", suggest_memory_type=True
        )
        
        # Should suggest agent for personal/task content
        assert analysis['suggested_memory_type'] == 'agent'

    def test_optimize_content_for_storage(self, markdown_processor, sample_markdown_content):
        """Test content optimization for storage."""
        optimization = markdown_processor.optimize_content_for_storage(
            sample_markdown_content, 'global', ai_optimization=True
        )
        
        assert 'optimized_content' in optimization
        assert 'memory_type' in optimization
        assert 'original_length' in optimization
        assert 'optimized_length' in optimization
        assert 'ai_enhanced' in optimization
        
        assert optimization['memory_type'] == 'global'
        assert optimization['ai_enhanced'] is True
        assert len(optimization['optimized_content']) > 0

    def test_chunk_content_with_headers(self, markdown_processor, sample_markdown_content):
        """Test header-aware content chunking."""
        chunks = markdown_processor.chunk_content(
            sample_markdown_content, preserve_headers=True
        )
        
        assert len(chunks) >= 1
        assert all('content' in chunk for chunk in chunks)
        assert all('chunk_index' in chunk for chunk in chunks)
        assert all('token_count' in chunk for chunk in chunks)
        
        # First chunk should have header information
        if len(chunks) > 1:
            assert 'section_title' in chunks[0]
            assert 'section_level' in chunks[0]

    def test_chunk_content_simple(self, markdown_processor):
        """Test simple content chunking without headers."""
        simple_content = "This is a simple text without headers. " * 100
        
        chunks = markdown_processor.chunk_content(
            simple_content, preserve_headers=False
        )
        
        assert len(chunks) >= 1
        assert all('content' in chunk for chunk in chunks)
        assert all('chunk_index' in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_process_directory_batch(self, markdown_processor, temp_directory):
        """Test batch directory processing."""
        results = await markdown_processor.process_directory_batch(
            str(temp_directory), 
            memory_type=None,  # Auto-suggest
            auto_suggest=True,
            ai_enhance=True,
            recursive=True
        )
        
        assert 'total_files' in results
        assert 'processed_files' in results
        assert 'failed_files' in results
        assert 'memory_type_suggestions' in results
        
        assert results['total_files'] > 0
        assert len(results['processed_files']) > 0
        
        # Check that each processed file has required fields
        for file_result in results['processed_files']:
            assert 'analysis' in file_result
            assert 'optimization' in file_result
            assert 'final_memory_type' in file_result
            assert 'processing_status' in file_result
            assert file_result['processing_status'] == 'success'


class TestPolicyProcessing:
    """Test policy processing functionality."""

    @pytest.mark.asyncio
    async def test_scan_policy_directory(self, markdown_processor, policy_directory):
        """Test policy directory scanning."""
        policy_files = await markdown_processor.scan_policy_directory(
            str(policy_directory)
        )
        
        assert len(policy_files) == 2
        assert all('rule_count' in file for file in policy_files)
        assert all('rule_ids' in file for file in policy_files)
        assert all('is_policy_file' in file for file in policy_files)
        
        total_rules = sum(file['rule_count'] for file in policy_files)
        assert total_rules > 0

    def test_extract_policy_rules(self, markdown_processor, policy_content):
        """Test policy rule extraction."""
        rules = markdown_processor.extract_policy_rules(policy_content)
        
        assert len(rules) == 6  # 2 principles + 2 forbidden + 2 required
        
        # Check rule structure
        for rule in rules:
            assert 'rule_id' in rule
            assert 'section' in rule
            assert 'rule_text' in rule
            assert 'full_content' in rule
            
        # Check specific rule IDs
        rule_ids = [rule['rule_id'] for rule in rules]
        assert 'P-001' in rule_ids
        assert 'P-002' in rule_ids
        assert 'F-101' in rule_ids
        assert 'F-102' in rule_ids
        assert 'R-201' in rule_ids
        assert 'R-202' in rule_ids

    def test_validate_policy_rules_valid(self, markdown_processor, policy_content):
        """Test policy rule validation with valid rules."""
        rules = markdown_processor.extract_policy_rules(policy_content)
        validation = markdown_processor.validate_policy_rules(rules, "1.0")
        
        assert validation['valid'] is True
        assert validation['rule_count'] == 6
        assert validation['unique_rules'] == 6
        assert len(validation['errors']) == 0

    def test_validate_policy_rules_duplicate(self, markdown_processor):
        """Test policy rule validation with duplicate rule IDs."""
        duplicate_content = """# Test Policy

[P-001] First rule
[P-001] Duplicate rule ID
"""
        
        rules = markdown_processor.extract_policy_rules(duplicate_content)
        validation = markdown_processor.validate_policy_rules(rules, "1.0")
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        assert 'Duplicate rule IDs' in validation['errors'][0]

    def test_validate_policy_rules_invalid_format(self, markdown_processor):
        """Test policy rule validation with invalid rule ID format."""
        invalid_content = """# Test Policy

[INVALID] Bad format
[P-001] Good format
"""
        
        rules = markdown_processor.extract_policy_rules(invalid_content)
        validation = markdown_processor.validate_policy_rules(rules, "1.0")
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0

    def test_generate_policy_hash(self, markdown_processor, policy_content):
        """Test policy hash generation."""
        rules = markdown_processor.extract_policy_rules(policy_content)
        policy_hash = markdown_processor.generate_policy_hash(rules, "1.0")
        
        assert len(policy_hash) == 64  # SHA-256 hash length
        assert policy_hash.isalnum()  # Hexadecimal string
        
        # Same rules should generate same hash
        hash2 = markdown_processor.generate_policy_hash(rules, "1.0")
        assert policy_hash == hash2
        
        # Different version should generate different hash
        hash3 = markdown_processor.generate_policy_hash(rules, "2.0")
        assert policy_hash != hash3


class TestUtilityMethods:
    """Test utility methods."""

    def test_calculate_content_hash(self, markdown_processor):
        """Test content hash calculation."""
        content = "Test content for hashing"
        hash1 = markdown_processor.calculate_content_hash(content)
        hash2 = markdown_processor.calculate_content_hash(content)
        
        assert hash1 == hash2  # Same content, same hash
        assert len(hash1) == 64  # SHA-256 hash length
        
        # Different content should produce different hash
        hash3 = markdown_processor.calculate_content_hash("Different content")
        assert hash1 != hash3

    def test_get_file_metadata(self, markdown_processor, sample_markdown_content):
        """Test file metadata generation."""
        metadata = markdown_processor.get_file_metadata(
            "test_file.md", sample_markdown_content
        )
        
        assert 'file_path' in metadata
        assert 'file_name' in metadata
        assert 'file_size' in metadata
        assert 'content_hash' in metadata
        assert 'word_count' in metadata
        assert 'section_count' in metadata
        
        assert metadata['file_size'] > 0
        assert metadata['word_count'] > 0
        assert len(metadata['content_hash']) == 64

    def test_token_estimation(self, markdown_processor):
        """Test token count estimation."""
        test_text = "This is a test sentence with multiple words."
        token_count = markdown_processor._estimate_tokens(test_text)
        
        assert token_count > 0
        assert token_count == len(test_text) // 4  # Rough estimation

    def test_text_splitting_by_tokens(self, markdown_processor):
        """Test text splitting by token count."""
        # Create long text that should be split
        long_text = "This is a sentence. " * 200
        
        # Create processor with small chunk size for testing
        processor = MarkdownProcessor(chunk_size=50, chunk_overlap=10)
        chunks = processor._split_text_by_tokens(long_text)
        
        assert len(chunks) > 1  # Should be split into multiple chunks
        
        # Check overlap
        if len(chunks) > 1:
            # There should be some overlap between consecutive chunks
            assert len(chunks[0]) > 0
            assert len(chunks[1]) > 0


class TestErrorHandling:
    """Test error handling in markdown processing."""

    def test_analyze_empty_content(self, markdown_processor):
        """Test analysis of empty content."""
        analysis = markdown_processor.analyze_content_for_memory_type(
            "", suggest_memory_type=True
        )
        
        assert 'suggested_memory_type' in analysis
        assert analysis['content_length'] == 0
        assert analysis['word_count'] == 0

    def test_optimize_empty_content(self, markdown_processor):
        """Test optimization of empty content."""
        optimization = markdown_processor.optimize_content_for_storage(
            "", 'global', ai_optimization=True
        )
        
        assert 'optimized_content' in optimization
        assert 'memory_type' in optimization

    def test_chunk_empty_content(self, markdown_processor):
        """Test chunking empty content."""
        chunks = markdown_processor.chunk_content("", preserve_headers=True)
        
        assert len(chunks) == 1  # Should return single empty chunk
        assert chunks[0]['content'] == ""

    def test_extract_rules_from_empty_content(self, markdown_processor):
        """Test policy rule extraction from empty content."""
        rules = markdown_processor.extract_policy_rules("")
        
        assert isinstance(rules, list)
        assert len(rules) == 0

    @pytest.mark.asyncio
    async def test_process_empty_directory(self, markdown_processor):
        """Test processing empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = await markdown_processor.process_directory_batch(
                temp_dir, recursive=True
            )
            
            assert results['total_files'] == 0
            assert len(results['processed_files']) == 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])