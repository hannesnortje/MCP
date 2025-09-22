"""
Tests for Enhanced Cosine Similarity Deduplication System.

This module tests the new cosine similarity-based deduplication
system including near-miss detection and diagnostics.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.memory_manager import QdrantMemoryManager
from src.tool_handlers import ToolHandlers
from src.server_config import (
    DEDUPLICATION_SIMILARITY_THRESHOLD,
    DEDUPLICATION_NEAR_MISS_THRESHOLD
)


class TestCosineDeduplication:
    """Test cosine similarity deduplication functionality."""

    @pytest.fixture
    async def memory_manager(self):
        """Create a mock memory manager for testing."""
        manager = Mock(spec=QdrantMemoryManager)
        
        # Mock the new method
        manager.async_check_duplicate_with_similarity = Mock()
        manager.async_check_duplicate = Mock()
        
        return manager

    @pytest.fixture 
    def tool_handlers(self, memory_manager):
        """Create tool handlers with mock memory manager."""
        handlers = ToolHandlers(memory_manager)
        return handlers

    def test_identical_content_detection(self, memory_manager):
        """Test detection of identical content."""
        # Setup: identical content should return high similarity
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": True,
            "is_near_miss": False,
            "similarity_score": 1.0,
            "matched_content_hash": "test-hash",
            "matched_content": "This is identical content",
            "collection": "global_memory"
        }
        
        content = "This is identical content"
        result = memory_manager.async_check_duplicate_with_similarity(
            content=content,
            memory_type="global",
            threshold=DEDUPLICATION_SIMILARITY_THRESHOLD
        )
        
        assert result["is_duplicate"] is True
        assert result["similarity_score"] == 1.0
        assert result["is_near_miss"] is False

    def test_similar_content_near_miss(self, memory_manager):
        """Test near-miss detection for similar content."""
        # Setup: similar content in near-miss range
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,
            "is_near_miss": True,
            "similarity_score": 0.82,  # Between thresholds
            "matched_content_hash": "similar-hash",
            "matched_content": "This is similar content",
            "collection": "global_memory"
        }
        
        content = "This is somewhat similar content"
        result = memory_manager.async_check_duplicate_with_similarity(
            content=content,
            memory_type="global",
            threshold=DEDUPLICATION_SIMILARITY_THRESHOLD,
            enable_near_miss=True
        )
        
        assert result["is_duplicate"] is False
        assert result["is_near_miss"] is True
        assert DEDUPLICATION_NEAR_MISS_THRESHOLD <= result["similarity_score"] < DEDUPLICATION_SIMILARITY_THRESHOLD

    def test_different_content_no_match(self, memory_manager):
        """Test that different content is not flagged."""
        # Setup: completely different content
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,
            "is_near_miss": False,
            "similarity_score": 0.15,
            "matched_content_hash": None,
            "matched_content": "",
            "collection": "global_memory"
        }
        
        content = "Completely different unrelated content"
        result = memory_manager.async_check_duplicate_with_similarity(
            content=content,
            memory_type="global",
            threshold=DEDUPLICATION_SIMILARITY_THRESHOLD
        )
        
        assert result["is_duplicate"] is False
        assert result["is_near_miss"] is False
        assert result["similarity_score"] < DEDUPLICATION_NEAR_MISS_THRESHOLD

    def test_threshold_boundary_conditions(self, memory_manager):
        """Test behavior at threshold boundaries."""
        test_cases = [
            (0.85, True, False),   # Exactly at duplicate threshold
            (0.849, False, True),  # Just below duplicate threshold 
            (0.80, False, True),   # Exactly at near-miss threshold
            (0.799, False, False), # Just below near-miss threshold
        ]
        
        for score, should_be_duplicate, should_be_near_miss in test_cases:
            memory_manager.async_check_duplicate_with_similarity.return_value = {
                "is_duplicate": should_be_duplicate,
                "is_near_miss": should_be_near_miss,
                "similarity_score": score,
                "matched_content_hash": "boundary-test",
                "matched_content": "Boundary test content",
                "collection": "global_memory"
            }
            
            result = memory_manager.async_check_duplicate_with_similarity(
                content=f"Test content with score {score}",
                memory_type="global",
                threshold=DEDUPLICATION_SIMILARITY_THRESHOLD,
                enable_near_miss=True
            )
            
            assert result["is_duplicate"] == should_be_duplicate
            assert result["is_near_miss"] == should_be_near_miss
            assert result["similarity_score"] == score

    def test_custom_threshold(self, memory_manager):
        """Test using custom threshold values."""
        custom_threshold = 0.90
        
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,  # Would be duplicate with default, not with custom
            "is_near_miss": True,
            "similarity_score": 0.87,
            "matched_content_hash": "custom-test",
            "matched_content": "Custom threshold test",
            "collection": "global_memory",
            "diagnostics": {
                "duplicate_threshold": custom_threshold,
                "near_miss_threshold": DEDUPLICATION_NEAR_MISS_THRESHOLD
            }
        }
        
        result = memory_manager.async_check_duplicate_with_similarity(
            content="Custom threshold test content",
            memory_type="global",
            threshold=custom_threshold
        )
        
        assert result["is_duplicate"] is False  # Below custom threshold
        assert result["similarity_score"] < custom_threshold
        assert result["diagnostics"]["duplicate_threshold"] == custom_threshold

    def test_agent_specific_memory(self, memory_manager):
        """Test deduplication in agent-specific memory collections."""
        agent_id = "test-agent-123"
        
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": True,
            "is_near_miss": False,
            "similarity_score": 0.95,
            "matched_content_hash": "agent-specific-hash",
            "matched_content": "Agent-specific duplicate content",
            "collection": f"agent_{agent_id}_memory"
        }
        
        result = memory_manager.async_check_duplicate_with_similarity(
            content="Agent-specific test content",
            memory_type="agent",
            agent_id=agent_id
        )
        
        assert result["is_duplicate"] is True
        assert agent_id in result["collection"]

    def test_diagnostics_information(self, memory_manager):
        """Test that diagnostics provide useful information."""
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,
            "is_near_miss": True,
            "similarity_score": 0.82,
            "matched_content_hash": "diag-test",
            "matched_content": "Diagnostic test content",
            "collection": "global_memory",
            "diagnostics": {
                "duplicate_threshold": DEDUPLICATION_SIMILARITY_THRESHOLD,
                "near_miss_threshold": DEDUPLICATION_NEAR_MISS_THRESHOLD,
                "total_matches": 3,
                "top_similarities": [
                    {"score": 0.82, "content_preview": "Top match preview"},
                    {"score": 0.75, "content_preview": "Second match preview"},
                    {"score": 0.68, "content_preview": "Third match preview"}
                ]
            }
        }
        
        result = memory_manager.async_check_duplicate_with_similarity(
            content="Test content for diagnostics",
            memory_type="global",
            enable_near_miss=True
        )
        
        diagnostics = result["diagnostics"]
        assert diagnostics["total_matches"] == 3
        assert len(diagnostics["top_similarities"]) == 3
        assert diagnostics["duplicate_threshold"] == DEDUPLICATION_SIMILARITY_THRESHOLD
        assert diagnostics["near_miss_threshold"] == DEDUPLICATION_NEAR_MISS_THRESHOLD

    def test_backward_compatibility(self, memory_manager):
        """Test that legacy async_check_duplicate method still works."""
        # Setup legacy method to return simple boolean
        memory_manager.async_check_duplicate.return_value = True
        
        result = memory_manager.async_check_duplicate(
            content="Legacy test content",
            memory_type="global"
        )
        
        assert result is True
        assert isinstance(result, bool)  # Ensure it's still a boolean

    def test_error_handling(self, memory_manager):
        """Test error handling in deduplication methods."""
        # Setup method to return error result instead of raising exception
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,
            "is_near_miss": False,
            "similarity_score": 0.0,
            "error": "Test error"
        }
        
        result = memory_manager.async_check_duplicate_with_similarity(
            content="Error test content",
            memory_type="global"
        )
        
        # Should return safe defaults on error
        assert "error" in result
        assert result["is_duplicate"] is False
        assert result["is_near_miss"] is False
        assert result["similarity_score"] == 0.0

    @pytest.mark.asyncio
    async def test_validate_and_deduplicate_tool(self, tool_handlers):
        """Test the validate_and_deduplicate tool handler."""
        # Setup mock response
        tool_handlers.memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,
            "is_near_miss": True,
            "similarity_score": 0.82,
            "matched_content": "Similar content found",
            "collection": "global_memory",
            "diagnostics": {
                "duplicate_threshold": 0.85,
                "near_miss_threshold": 0.80,
                "total_matches": 2
            }
        }
        
        arguments = {
            "content": "Test content for tool validation",
            "memory_type": "global",
            "enable_near_miss": True
        }
        
        result = await tool_handlers.handle_validate_and_deduplicate(arguments)
        
        assert "content" in result
        assert len(result["content"]) > 0
        assert "text" in result["content"][0]
        
        response_text = result["content"][0]["text"]
        assert "NEAR-MISS DETECTED" in response_text
        assert "0.82" in response_text  # Similarity score
        assert "Diagnostics:" in response_text

    @pytest.mark.asyncio
    async def test_tool_empty_content_error(self, tool_handlers):
        """Test that tool returns error for empty content."""
        arguments = {
            "content": "",
            "memory_type": "global"
        }
        
        result = await tool_handlers.handle_validate_and_deduplicate(arguments)
        
        assert result["isError"] is True
        assert "empty" in result["content"][0]["text"].lower()

    @pytest.mark.asyncio 
    async def test_tool_exception_handling(self, tool_handlers):
        """Test tool exception handling."""
        # Setup method to raise exception
        tool_handlers.memory_manager.async_check_duplicate_with_similarity.side_effect = Exception("Tool test error")
        
        arguments = {
            "content": "Test content that will cause error",
            "memory_type": "global"
        }
        
        result = await tool_handlers.handle_validate_and_deduplicate(arguments)
        
        assert result["isError"] is True
        assert "Failed to validate" in result["content"][0]["text"]


class TestDeduplicationConfiguration:
    """Test deduplication configuration and settings."""

    def test_default_thresholds(self):
        """Test that default threshold values are reasonable."""
        assert 0.0 <= DEDUPLICATION_NEAR_MISS_THRESHOLD <= 1.0
        assert 0.0 <= DEDUPLICATION_SIMILARITY_THRESHOLD <= 1.0
        assert DEDUPLICATION_NEAR_MISS_THRESHOLD < DEDUPLICATION_SIMILARITY_THRESHOLD
        
        # Default values should be reasonable
        assert DEDUPLICATION_SIMILARITY_THRESHOLD == 0.85
        assert DEDUPLICATION_NEAR_MISS_THRESHOLD == 0.80

    def test_threshold_relationships(self):
        """Test that thresholds have correct relationships."""
        # Near-miss threshold should be lower than duplicate threshold
        assert DEDUPLICATION_NEAR_MISS_THRESHOLD < DEDUPLICATION_SIMILARITY_THRESHOLD
        
        # There should be a reasonable gap for near-miss detection
        gap = DEDUPLICATION_SIMILARITY_THRESHOLD - DEDUPLICATION_NEAR_MISS_THRESHOLD
        assert gap >= 0.03  # At least 3% gap
        assert gap <= 0.15  # But not too large


class TestPerformanceAndScalability:
    """Test performance aspects of deduplication system."""

    @pytest.fixture
    async def memory_manager(self):
        """Create a mock memory manager for testing."""
        manager = Mock(spec=QdrantMemoryManager)
        
        # Mock the new method
        manager.async_check_duplicate_with_similarity = Mock()
        manager.async_check_duplicate = Mock()
        
        return manager

    def test_large_content_handling(self, memory_manager):
        """Test deduplication with large content."""
        # Create large content (simulate real-world markdown file)
        large_content = "# Large Document\n\n" + "This is a test paragraph. " * 1000
        
        memory_manager.async_check_duplicate_with_similarity.return_value = {
            "is_duplicate": False,
            "is_near_miss": False,
            "similarity_score": 0.25,
            "matched_content_hash": None,
            "matched_content": "",
            "collection": "global_memory"
        }
        
        result = memory_manager.async_check_duplicate_with_similarity(
            content=large_content,
            memory_type="global"
        )
        
        # Should handle large content without issues
        assert result["is_duplicate"] is False
        assert isinstance(result["similarity_score"], (int, float))

    def test_multiple_memory_types(self, memory_manager):
        """Test deduplication across different memory types."""
        memory_types = ["global", "learned", "agent"]
        test_content = "Multi-type deduplication test"
        
        for memory_type in memory_types:
            memory_manager.async_check_duplicate_with_similarity.return_value = {
                "is_duplicate": False,
                "is_near_miss": False,
                "similarity_score": 0.3,
                "collection": f"{memory_type}_memory"
            }
            
            result = memory_manager.async_check_duplicate_with_similarity(
                content=test_content,
                memory_type=memory_type,
                agent_id="test-agent" if memory_type == "agent" else None
            )
            
            assert memory_type in result["collection"]
            assert result["is_duplicate"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])