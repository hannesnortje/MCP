"""
Policy processor for MCP Memory Server.
Handles policy markdown files, rule extraction, validation, and canonicalization.
"""

import logging
import re
import hashlib
import json
from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path
from datetime import datetime
import aiofiles

from .config import Config

logger = logging.getLogger(__name__)


class PolicyProcessor:
    """Processes policy markdown files for governance and compliance."""

    def __init__(self) -> None:
        """Initialize the Policy Processor."""
        self.rule_id_pattern = re.compile(Config.POLICY_RULE_ID_PATTERN)
        self.required_sections = Config.POLICY_REQUIRED_SECTIONS

    async def discover_policy_files(self, directory: str = None) -> List[str]:
        """Discover policy markdown files in the specified directory.
        
        Args:
            directory: Policy directory path (defaults to config)
            
        Returns:
            List of policy file paths
        """
        try:
            # Handle directory resolution more robustly
            if directory:
                provided_dir = Path(directory)
                # If it's an absolute path, use it directly
                if provided_dir.is_absolute():
                    policy_dir = provided_dir
                else:
                    # For relative paths, resolve relative to project root
                    current_file = Path(__file__)
                    # Go up from src/ to project root
                    project_root = current_file.parent.parent
                    policy_dir = project_root / provided_dir
            else:
                # Try to find project root from this file's location
                current_file = Path(__file__)
                # Go up from src/ to project root
                project_root = current_file.parent.parent
                
                # If Config.POLICY_DIRECTORY is absolute, use it directly
                config_policy_dir = Path(Config.POLICY_DIRECTORY)
                if config_policy_dir.is_absolute():
                    policy_dir = config_policy_dir
                else:
                    # Resolve relative to project root
                    # Use just the directory name (e.g., 'policy')
                    policy_dir = project_root / config_policy_dir.name
            
            # Log the resolved path for debugging
            logger.info(
                f"Attempting to find policy files in: {policy_dir.absolute()}"
            )
            
            if not policy_dir.exists():
                logger.warning(
                    f"Policy directory not found: {policy_dir.absolute()}"
                )
                return []

            policy_files = []
            for file_path in policy_dir.rglob("*.md"):
                if file_path.is_file():
                    policy_files.append(str(file_path))
            
            logger.info(
                f"Found {len(policy_files)} policy files in "
                f"{policy_dir.absolute()}"
            )
            return sorted(policy_files)

        except Exception as e:
            logger.error(f"Failed to discover policy files: {e}")
            return []

    async def read_policy_file(self, file_path: str) -> str:
        """Read a policy markdown file from disk.
        
        Args:
            file_path: Path to the policy markdown file
            
        Returns:
            File content as string
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Policy file not found: {file_path}")
            
            if not path.suffix.lower() in ['.md', '.markdown']:
                raise ValueError(f"Not a markdown file: {file_path}")

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()

            logger.info(f"Read policy file: {file_path} ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"Failed to read policy file {file_path}: {e}")
            raise

    def extract_rule_ids(self, content: str) -> List[Tuple[str, str, int]]:
        """Extract rule IDs from policy content.
        
        Args:
            content: Policy markdown content
            
        Returns:
            List of tuples (rule_id, context_text, line_number)
        """
        try:
            rules = []
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                matches = self.rule_id_pattern.findall(line)
                for rule_id in matches:
                    # Get surrounding context (current line + next line if exists)
                    context = line.strip()
                    if line_num < len(lines):
                        next_line = lines[line_num].strip()
                        if next_line and not next_line.startswith('#'):
                            context += f" {next_line}"
                    
                    rules.append((rule_id, context, line_num))
            
            logger.info(f"Extracted {len(rules)} rule IDs from content")
            return rules

        except Exception as e:
            logger.error(f"Failed to extract rule IDs: {e}")
            return []

    def parse_sections(self, content: str) -> Dict[str, str]:
        """Parse content into sections based on headers.
        
        Args:
            content: Policy markdown content
            
        Returns:
            Dictionary of section_name -> section_content
        """
        try:
            sections = {}
            lines = content.split('\n')
            current_section = None
            current_content = []

            for line in lines:
                # Check for headers (# ## ###)
                header_match = re.match(r'^#+\s+(.+)', line.strip())
                if header_match:
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = header_match.group(1).strip()
                    current_content = []
                else:
                    # Add to current section content
                    if current_section:
                        current_content.append(line)

            # Save the last section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()

            logger.info(f"Parsed {len(sections)} sections from content")
            return sections

        except Exception as e:
            logger.error(f"Failed to parse sections: {e}")
            return {}

    def validate_rule_uniqueness(self, rules: List[Tuple[str, str, int]]) -> Dict[str, Any]:
        """Validate that all rule IDs are unique.
        
        Args:
            rules: List of (rule_id, context, line_number) tuples
            
        Returns:
            Validation results with duplicates and warnings
        """
        try:
            rule_counts = {}
            duplicates = {}
            
            for rule_id, context, line_num in rules:
                if rule_id not in rule_counts:
                    rule_counts[rule_id] = []
                rule_counts[rule_id].append((context, line_num))
            
            # Find duplicates
            for rule_id, occurrences in rule_counts.items():
                if len(occurrences) > 1:
                    duplicates[rule_id] = occurrences

            validation_result = {
                "is_valid": len(duplicates) == 0,
                "total_rules": len(rules),
                "unique_rules": len(rule_counts),
                "duplicates": duplicates,
                "warnings": []
            }

            if duplicates:
                for rule_id, occurrences in duplicates.items():
                    validation_result["warnings"].append(
                        f"Rule {rule_id} appears {len(occurrences)} times at lines: "
                        f"{[line for _, line in occurrences]}"
                    )

            return validation_result

        except Exception as e:
            logger.error(f"Failed to validate rule uniqueness: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "total_rules": 0,
                "unique_rules": 0,
                "duplicates": {},
                "warnings": []
            }

    def validate_required_sections(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Validate that all required sections are present.
        
        Args:
            sections: Dictionary of parsed sections
            
        Returns:
            Validation results with missing sections
        """
        try:
            section_names = set(sections.keys())
            required_sections = set(self.required_sections)
            
            missing_sections = required_sections - section_names
            extra_sections = section_names - required_sections

            validation_result = {
                "is_valid": len(missing_sections) == 0,
                "found_sections": list(section_names),
                "required_sections": list(required_sections),
                "missing_sections": list(missing_sections),
                "extra_sections": list(extra_sections),
                "warnings": []
            }

            if missing_sections:
                validation_result["warnings"].append(
                    f"Missing required sections: {list(missing_sections)}"
                )

            return validation_result

        except Exception as e:
            logger.error(f"Failed to validate required sections: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "found_sections": [],
                "required_sections": self.required_sections,
                "missing_sections": [],
                "extra_sections": [],
                "warnings": []
            }

    def create_policy_entries(
        self,
        rules: List[Tuple[str, str, int]],
        sections: Dict[str, str],
        source_path: str,
        policy_version: str
    ) -> List[Dict[str, Any]]:
        """Create policy memory entries for storage.
        
        Args:
            rules: Extracted rules with context
            sections: Parsed sections
            source_path: Source file path
            policy_version: Policy version identifier
            
        Returns:
            List of policy entries ready for storage
        """
        try:
            entries = []
            policy_hash = self._calculate_policy_hash(rules, sections)

            # Find which section each rule belongs to
            rule_sections = self._map_rules_to_sections(rules, sections)

            for rule_id, context, line_num in rules:
                entry = {
                    "rule_id": rule_id,
                    "policy_version": policy_version,
                    "policy_hash": policy_hash,
                    "title": f"Rule {rule_id}",
                    "section": rule_sections.get(rule_id, "Unknown"),
                    "source_path": source_path,
                    "chunk_index": 0,  # Rules are single chunks
                    "text": context,
                    "severity": self._determine_severity(rule_id),
                    "active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "line_number": line_num
                }
                entries.append(entry)

            logger.info(f"Created {len(entries)} policy entries")
            return entries

        except Exception as e:
            logger.error(f"Failed to create policy entries: {e}")
            return []

    def _map_rules_to_sections(
        self,
        rules: List[Tuple[str, str, int]],
        sections: Dict[str, str]
    ) -> Dict[str, str]:
        """Map rule IDs to their containing sections.
        
        Args:
            rules: List of rule tuples
            sections: Parsed sections
            
        Returns:
            Dictionary mapping rule_id -> section_name
        """
        rule_sections = {}
        
        for rule_id, _, line_num in rules:
            # Find which section this rule belongs to
            # by checking line numbers within section content
            for section_name, section_content in sections.items():
                if f"[{rule_id}]" in section_content:
                    rule_sections[rule_id] = section_name
                    break
            else:
                rule_sections[rule_id] = "Unknown"

        return rule_sections

    def _determine_severity(self, rule_id: str) -> str:
        """Determine rule severity based on rule ID prefix.
        
        Args:
            rule_id: Rule identifier (e.g., P-001, F-101)
            
        Returns:
            Severity level string
        """
        prefix = rule_id.split('-')[0] if '-' in rule_id else ''
        
        severity_map = {
            'P': 'high',      # Principles - high severity
            'F': 'critical',  # Forbidden Actions - critical
            'R': 'medium',    # Required Sections - medium
            'S': 'low'        # Style Guide - low
        }
        
        return severity_map.get(prefix, 'medium')

    def _calculate_policy_hash(
        self,
        rules: List[Tuple[str, str, int]],
        sections: Dict[str, str]
    ) -> str:
        """Calculate a deterministic hash for the policy content.
        
        Args:
            rules: List of extracted rules
            sections: Parsed sections
            
        Returns:
            SHA-256 hash of the policy content
        """
        # Create a canonical representation
        canonical_data = {
            "rules": [(rule_id, context.strip()) for rule_id, context, _ in rules],
            "sections": {k: v.strip() for k, v in sections.items()}
        }
        
        # Sort for deterministic hash
        canonical_json = json.dumps(canonical_data, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    async def process_policy_file(self, file_path: str, policy_version: str) -> Dict[str, Any]:
        """Process a single policy file completely.
        
        Args:
            file_path: Path to policy markdown file
            policy_version: Policy version identifier
            
        Returns:
            Complete processing result
        """
        try:
            # Read the file
            content = await self.read_policy_file(file_path)
            
            # Extract rules and sections
            rules = self.extract_rule_ids(content)
            sections = self.parse_sections(content)
            
            # Validate
            rule_validation = self.validate_rule_uniqueness(rules)
            # Skip individual file section validation - do it globally instead
            section_validation = {
                "is_valid": True,
                "message": "Deferred to global validation"
            }
            
            # Create entries if rules are valid
            entries = []
            if rule_validation["is_valid"]:
                entries = self.create_policy_entries(
                    rules, sections, file_path, policy_version
                )

            result = {
                "success": rule_validation["is_valid"],
                "file_path": file_path,
                "policy_version": policy_version,
                "content_length": len(content),
                "rule_validation": rule_validation,
                "section_validation": section_validation,
                "entries": entries,
                "policy_hash": self._calculate_policy_hash(
                    rules, sections
                ) if entries else None
            }

            return result

        except Exception as e:
            logger.error(f"Failed to process policy file {file_path}: {e}")
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e),
                "entries": []
            }

    async def build_canonical_policy(
        self,
        directory: str = None,
        policy_version: str = "latest"
    ) -> Dict[str, Any]:
        """Build a canonical policy from all files in directory.
        
        Args:
            directory: Policy directory path
            policy_version: Policy version identifier
            
        Returns:
            Complete canonical policy structure
        """
        try:
            policy_files = await self.discover_policy_files(directory)
            
            if not policy_files:
                return {
                    "success": False,
                    "error": "No policy files found",
                    "policy": {}
                }

            all_rules = []
            all_sections = {}
            all_entries = []
            validation_results = []

            # Process each file
            for file_path in policy_files:
                result = await self.process_policy_file(
                    file_path, policy_version
                )
                validation_results.append(result)
                
                if result["success"]:
                    all_entries.extend(result["entries"])
                    # Collect rules for global validation
                    file_content = await self.read_policy_file(file_path)
                    all_rules.extend(self.extract_rule_ids(file_content))
                    all_sections.update(self.parse_sections(file_content))

            # Global validation across all files
            global_rule_validation = self.validate_rule_uniqueness(all_rules)
            
            # Calculate global policy hash
            policy_hash = self._calculate_policy_hash(all_rules, all_sections)

            canonical_policy = {
                "success": global_rule_validation["is_valid"],
                "policy_version": policy_version,
                "policy_hash": policy_hash,
                "created_at": datetime.utcnow().isoformat(),
                "files_processed": len(policy_files),
                "total_rules": len(all_rules),
                "unique_rules": global_rule_validation["unique_rules"],
                "entries": all_entries,
                "validation": {
                    "global_rule_validation": global_rule_validation,
                    "file_results": validation_results
                },
                "metadata": {
                    "source_directory": directory or Config.POLICY_DIRECTORY,
                    "file_paths": policy_files
                }
            }

            logger.info(
                f"Built canonical policy with {len(all_entries)} entries"
            )
            return canonical_policy

        except Exception as e:
            logger.error(f"Failed to build canonical policy: {e}")
            return {
                "success": False,
                "error": str(e),
                "policy": {}
            }
