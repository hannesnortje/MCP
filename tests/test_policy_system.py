"""
Test suite for the Policy Memory System (Step 9).
Tests policy processing, validation, storage, and compliance features.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import json

from src.policy_processor import PolicyProcessor
from src.tool_handlers import ToolHandlers
from src.resource_handlers import ResourceHandlers
from src.memory_manager import QdrantMemoryManager
from src.config import Config


class TestPolicyProcessor:
    """Test the PolicyProcessor class functionality."""

    @pytest.fixture
    def processor(self):
        """Create a PolicyProcessor instance."""
        return PolicyProcessor()

    @pytest.fixture
    def temp_policy_dir(self):
        """Create temporary policy directory with sample files."""
        temp_dir = tempfile.mkdtemp()
        policy_dir = Path(temp_dir) / "policy"
        policy_dir.mkdir()

        # Create sample policy files
        principles_content = '''# Principles

## Core Values
- [P-001] Test principle one
- [P-002] Test principle two

## Guidelines  
- [P-003] Test guideline
'''

        forbidden_content = '''# Forbidden Actions

## Prohibited
- [F-101] Test forbidden action one
- [F-102] Test forbidden action two
'''

        (policy_dir / "01-principles.md").write_text(principles_content)
        (policy_dir / "02-forbidden.md").write_text(forbidden_content)

        yield str(policy_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_discover_policy_files(self, processor, temp_policy_dir):
        """Test policy file discovery."""
        files = await processor.discover_policy_files(temp_policy_dir)
        
        assert len(files) == 2
        assert any("01-principles.md" in f for f in files)
        assert any("02-forbidden.md" in f for f in files)

    @pytest.mark.asyncio
    async def test_read_policy_file(self, processor, temp_policy_dir):
        """Test reading policy files."""
        files = await processor.discover_policy_files(temp_policy_dir)
        content = await processor.read_policy_file(files[0])
        
        assert len(content) > 0
        assert "Principles" in content or "Forbidden" in content

    def test_extract_rule_ids(self, processor):
        """Test rule ID extraction from content."""
        content = """
# Test Section
- [P-001] First rule
- [F-101] Forbidden action
- Some text without rule ID
- [R-201] Required section
"""
        
        rules = processor.extract_rule_ids(content)
        
        assert len(rules) == 3
        rule_ids = [rule[0] for rule in rules]
        assert "P-001" in rule_ids
        assert "F-101" in rule_ids
        assert "R-201" in rule_ids

    def test_parse_sections(self, processor):
        """Test section parsing from markdown content."""
        content = """# Section One
Content for section one

## Subsection
More content

# Section Two
Content for section two
"""
        
        sections = processor.parse_sections(content)
        
        assert len(sections) == 3
        assert "Section One" in sections
        assert "Subsection" in sections
        assert "Section Two" in sections

    def test_validate_rule_uniqueness_success(self, processor):
        """Test successful rule uniqueness validation."""
        rules = [
            ("P-001", "First rule", 1),
            ("P-002", "Second rule", 2),
            ("F-101", "Forbidden action", 3)
        ]
        
        result = processor.validate_rule_uniqueness(rules)
        
        assert result["is_valid"] is True
        assert result["total_rules"] == 3
        assert result["unique_rules"] == 3
        assert len(result["duplicates"]) == 0

    def test_validate_rule_uniqueness_duplicates(self, processor):
        """Test rule uniqueness validation with duplicates."""
        rules = [
            ("P-001", "First rule", 1),
            ("P-001", "Duplicate rule", 5),
            ("P-002", "Second rule", 2)
        ]
        
        result = processor.validate_rule_uniqueness(rules)
        
        assert result["is_valid"] is False
        assert result["total_rules"] == 3
        assert result["unique_rules"] == 2
        assert "P-001" in result["duplicates"]
        assert len(result["duplicates"]["P-001"]) == 2

    def test_validate_required_sections_success(self, processor):
        """Test successful required sections validation."""
        sections = {
            "Principles": "Content",
            "Forbidden Actions": "Content",
            "Required Sections": "Content",
            "Style Guide": "Content"
        }
        
        result = processor.validate_required_sections(sections)
        
        assert result["is_valid"] is True
        assert len(result["missing_sections"]) == 0

    def test_validate_required_sections_missing(self, processor):
        """Test required sections validation with missing sections."""
        sections = {
            "Principles": "Content",
            "Extra Section": "Content"
        }
        
        result = processor.validate_required_sections(sections)
        
        assert result["is_valid"] is False
        assert len(result["missing_sections"]) == 3
        assert "Forbidden Actions" in result["missing_sections"]

    def test_create_policy_entries(self, processor):
        """Test creating policy entries for storage."""
        rules = [
            ("P-001", "Test principle", 1),
            ("F-101", "Test forbidden action", 5)
        ]
        sections = {
            "Principles": "Content with [P-001]",
            "Forbidden Actions": "Content with [F-101]"
        }
        
        entries = processor.create_policy_entries(
            rules, sections, "/path/test.md", "v1.0"
        )
        
        assert len(entries) == 2
        
        # Check first entry
        entry = entries[0]
        assert entry["rule_id"] == "P-001"
        assert entry["policy_version"] == "v1.0"
        assert entry["source_path"] == "/path/test.md"
        assert entry["severity"] in ["high", "critical", "medium", "low"]
        assert entry["active"] is True

    @pytest.mark.asyncio
    async def test_process_policy_file(self, processor, temp_policy_dir):
        """Test complete policy file processing."""
        files = await processor.discover_policy_files(temp_policy_dir)
        result = await processor.process_policy_file(files[0], "test-v1")
        
        assert "success" in result
        assert "file_path" in result
        assert "policy_version" in result
        assert "rule_validation" in result
        assert "section_validation" in result
        assert "entries" in result

    @pytest.mark.asyncio
    async def test_build_canonical_policy(self, processor, temp_policy_dir):
        """Test building canonical policy from directory."""
        result = await processor.build_canonical_policy(temp_policy_dir, "test-v1")
        
        assert "success" in result
        assert "policy_version" in result
        assert "policy_hash" in result
        assert "entries" in result
        assert "validation" in result


class TestPolicyTools:
    """Test policy-related tools in ToolHandlers."""

    @pytest.fixture
    def mock_memory_manager(self):
        """Create a mock memory manager."""
        memory_manager = Mock(spec=QdrantMemoryManager)
        memory_manager.client = Mock()
        memory_manager.embedding_model = Mock()
        memory_manager.embedding_model.encode.return_value = Mock()
        memory_manager.embedding_model.encode.return_value.tolist.return_value = [0.1] * 384
        return memory_manager

    @pytest.fixture
    def tool_handlers(self, mock_memory_manager):
        """Create ToolHandlers with mock memory manager."""
        return ToolHandlers(mock_memory_manager)

    @pytest.mark.asyncio
    async def test_handle_build_policy_from_markdown(self, tool_handlers):
        """Test build_policy_from_markdown tool handler."""
        # Mock the policy processor
        tool_handlers.policy_processor.build_canonical_policy = AsyncMock()
        tool_handlers.policy_processor.build_canonical_policy.return_value = {
            "success": True,
            "files_processed": 2,
            "total_rules": 5,
            "unique_rules": 5,
            "policy_hash": "abc123def456",
            "entries": [
                {"rule_id": "P-001", "text": "Test rule", "policy_version": "v1"}
            ]
        }
        
        # Mock storage method
        tool_handlers._store_policy_entries = AsyncMock()
        tool_handlers._store_policy_entries.return_value = {"success": True}
        
        arguments = {
            "directory": "./policy",
            "policy_version": "v1.0",
            "activate": True
        }
        
        result = await tool_handlers.handle_build_policy_from_markdown(arguments)
        
        assert "content" in result
        assert len(result["content"]) > 0
        assert "Built policy version 'v1.0'" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_handle_get_policy_rulebook(self, tool_handlers):
        """Test get_policy_rulebook tool handler."""
        # Mock query method
        tool_handlers._query_policy_memory = AsyncMock()
        tool_handlers._query_policy_memory.return_value = [
            {
                "rule_id": "P-001",
                "text": "Test rule",
                "section": "Principles",
                "severity": "high",
                "policy_hash": "abc123",
                "policy_version": "v1.0"
            }
        ]
        
        arguments = {"version": "v1.0"}
        
        result = await tool_handlers.handle_get_policy_rulebook(arguments)
        
        assert "content" in result
        assert "Policy Rulebook - Version: v1.0" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_handle_validate_json_against_schema(self, tool_handlers):
        """Test validate_json_against_schema tool handler."""
        # Mock policy query
        tool_handlers._query_policy_memory = AsyncMock()
        tool_handlers._query_policy_memory.return_value = []
        
        arguments = {
            "schema_name": "test-schema",
            "candidate_json": '{"test": "valid"}'
        }
        
        result = await tool_handlers.handle_validate_json_against_schema(arguments)
        
        assert "content" in result
        # Should contain validation results

    @pytest.mark.asyncio
    async def test_handle_log_policy_violation(self, tool_handlers):
        """Test log_policy_violation tool handler."""
        # Mock methods
        tool_handlers._get_rule_severity = AsyncMock()
        tool_handlers._get_rule_severity.return_value = "high"
        
        tool_handlers._store_policy_violation = AsyncMock()
        tool_handlers._store_policy_violation.return_value = {"success": True}
        
        arguments = {
            "agent_id": "test-agent",
            "rule_id": "P-001",
            "context": {"action": "test"}
        }
        
        result = await tool_handlers.handle_log_policy_violation(arguments)
        
        assert "content" in result
        assert "Policy violation logged" in result["content"][0]["text"]


class TestPolicyResources:
    """Test policy-related resources in ResourceHandlers."""

    @pytest.fixture
    def mock_memory_manager(self):
        """Create a mock memory manager."""
        memory_manager = Mock(spec=QdrantMemoryManager)
        memory_manager.client = Mock()
        memory_manager.client.search.return_value = []
        return memory_manager

    @pytest.fixture
    def resource_handlers(self, mock_memory_manager):
        """Create ResourceHandlers with mock memory manager."""
        return ResourceHandlers(mock_memory_manager)

    @pytest.mark.asyncio
    async def test_get_policy_violations_log(self, resource_handlers):
        """Test policy violations log resource."""
        # Mock search results
        mock_result = Mock()
        mock_result.id = "violation-1"
        mock_result.payload = {
            "agent_id": "test-agent",
            "rule_id": "P-001",
            "severity": "high",
            "timestamp": "2024-01-01T00:00:00",
            "context": {}
        }
        
        resource_handlers.memory_manager.client.search.return_value = [mock_result]
        
        result = await resource_handlers._get_policy_violations_log()
        
        assert result["status"] == "success"
        assert "violations" in result["data"]
        assert len(result["data"]["violations"]) == 1

    @pytest.mark.asyncio
    async def test_get_policy_rulebook_resource(self, resource_handlers):
        """Test policy rulebook resource."""
        # Mock search results
        mock_result = Mock()
        mock_result.payload = {
            "rule_id": "P-001",
            "text": "Test rule",
            "section": "Principles",
            "severity": "high",
            "policy_hash": "abc123",
            "policy_version": "v1.0"
        }
        
        resource_handlers.memory_manager.client.search.return_value = [mock_result]
        
        result = await resource_handlers._get_policy_rulebook()
        
        assert result["status"] == "success"
        assert "rulebook" in result["data"]
        assert result["data"]["available"] is True


class TestPolicyIntegration:
    """Integration tests for the complete policy system."""

    @pytest.fixture
    def temp_policy_dir(self):
        """Create temporary policy directory."""
        temp_dir = tempfile.mkdtemp()
        policy_dir = Path(temp_dir) / "policy"
        policy_dir.mkdir()

        # Copy actual policy files
        actual_policy_dir = Path("policy")
        if actual_policy_dir.exists():
            for file in actual_policy_dir.glob("*.md"):
                shutil.copy2(file, policy_dir)
        
        yield str(policy_dir)
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_end_to_end_policy_processing(self, temp_policy_dir):
        """Test complete end-to-end policy processing."""
        processor = PolicyProcessor()
        
        # Build canonical policy
        result = await processor.build_canonical_policy(temp_policy_dir, "integration-test")
        
        assert result["success"] is True
        assert result["total_rules"] > 0
        assert result["policy_hash"] is not None
        assert len(result["entries"]) > 0
        
        # Validate specific rule formats
        for entry in result["entries"]:
            assert "rule_id" in entry
            assert entry["rule_id"].count("-") == 1  # Format: X-NNN
            assert "policy_version" in entry
            assert "severity" in entry
            assert entry["severity"] in ["low", "medium", "high", "critical"]

    def test_rule_id_pattern_compliance(self):
        """Test that all rules in actual policy files follow the pattern."""
        policy_dir = Path("policy")
        if not policy_dir.exists():
            pytest.skip("Policy directory not found")
        
        processor = PolicyProcessor()
        rule_pattern = processor.rule_id_pattern
        
        all_rule_ids = []
        for file_path in policy_dir.glob("*.md"):
            with open(file_path, 'r') as f:
                content = f.read()
                rules = processor.extract_rule_ids(content)
                all_rule_ids.extend([rule[0] for rule in rules])
        
        # Verify all rules follow the pattern
        assert len(all_rule_ids) > 0, "No rules found in policy files"
        
        for rule_id in all_rule_ids:
            assert rule_pattern.match(f"[{rule_id}]"), f"Rule ID {rule_id} doesn't match pattern"
        
        # Verify uniqueness
        assert len(all_rule_ids) == len(set(all_rule_ids)), "Duplicate rule IDs found"

    def test_required_sections_present(self):
        """Test that all required sections are present in policy files."""
        policy_dir = Path("policy")
        if not policy_dir.exists():
            pytest.skip("Policy directory not found")
        
        processor = PolicyProcessor()
        
        all_sections = set()
        for file_path in policy_dir.glob("*.md"):
            with open(file_path, 'r') as f:
                content = f.read()
                sections = processor.parse_sections(content)
                all_sections.update(sections.keys())
        
        required_sections = set(Config.POLICY_REQUIRED_SECTIONS)
        missing_sections = required_sections - all_sections
        
        assert len(missing_sections) == 0, f"Missing required sections: {missing_sections}"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])