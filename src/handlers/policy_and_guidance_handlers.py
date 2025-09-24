"""
Policy and guidance handlers for MCP Memory Server.
Handles policy building, validation, violation logging, and guidance content.
"""

from typing import Dict, Any
import json
from datetime import datetime

try:
    from ..server_config import get_logger
    from ..policy_processor import PolicyProcessor
    from ..error_handler import error_handler
except ImportError:
    # Fallback for standalone usage
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)
    
    class MockPolicyProcessor:
        async def build_canonical_policy(self, *args, **kwargs):
            return {"success": False, "error": "PolicyProcessor not available"}
    
    class MockErrorHandler:
        def get_error_stats(self):
            return {"total_errors": 0}
    
    error_handler = MockErrorHandler()

logger = get_logger("policy-guidance-handlers")


class PolicyAndGuidanceHandlers:
    """Handles policy management and guidance operations."""
    
    def __init__(self, memory_manager, policy_processor=None):
        """Initialize with memory manager and optional policy processor."""
        self.memory_manager = memory_manager
        self.policy_processor = policy_processor or PolicyProcessor()
    
    async def handle_build_policy_from_markdown(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build policy from markdown files in directory."""
        try:
            directory = arguments.get("directory", "./policy")
            policy_version = arguments.get("policy_version", "latest")
            activate = arguments.get("activate", True)

            # Build canonical policy
            result = await self.policy_processor.build_canonical_policy(
                directory=directory,
                policy_version=policy_version
            )

            if not result["success"]:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text", 
                            "text": f"Failed: {result.get('error', 'Unknown error')}"
                        }
                    ]
                }

            # Store policy entries in Qdrant if activate is True
            if activate and result["entries"]:
                storage_results = await self._store_policy_entries(result["entries"])
                
                response_text = (
                    f"✅ Built policy version '{policy_version}'"
                    f"\n📁 Directory: {directory}"
                    f"\n📝 Files processed: {result['files_processed']}"
                    f"\n🔢 Total rules: {result['total_rules']}"
                    f"\n✅ Unique rules: {result['unique_rules']}"
                    f"\n#️⃣ Policy hash: {result['policy_hash'][:12]}..."
                )
                
                if storage_results["success"]:
                    response_text += (
                        f"\n💾 Stored {len(result['entries'])} policy entries"
                    )
                else:
                    response_text += (
                        f"\n⚠️ Storage issues: "
                        f"{storage_results.get('warnings', 0)} warnings"
                    )

                return {
                    "content": [
                        {"type": "text", "text": response_text}
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": (
                                f"✅ Policy built (not activated)"
                                f"\n📊 {result['total_rules']} rules parsed"
                            )
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Error building policy: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error building policy: {str(e)}"}
                ]
            }

    async def handle_get_policy_rulebook(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get the canonical policy rulebook."""
        try:
            version = arguments.get("version", "latest")
            
            # Query policy memory for the specified version
            policy_entries = await self._query_policy_memory(version=version)
            
            if not policy_entries:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text", 
                            "text": f"No policy found for version: {version}"
                        }
                    ]
                }

            # Build canonical rulebook structure
            rulebook = self._build_rulebook_structure(policy_entries)
            
            response_text = (
                f"📋 Policy Rulebook - Version: {version}"
                f"\n🔢 Rules: {len(policy_entries)}"
                f"\n📚 Sections: {len(rulebook['sections'])}"
                f"\n#️⃣ Hash: {rulebook['policy_hash'][:12]}..."
                f"\n\n📖 **Rulebook JSON:**"
                f"\n```json\n{rulebook['json']}\n```"
            )

            return {
                "content": [
                    {"type": "text", "text": response_text}
                ]
            }

        except Exception as e:
            logger.error(f"Error getting policy rulebook: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error getting rulebook: {str(e)}"}
                ]
            }

    async def handle_validate_json_against_schema(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate JSON against policy schema requirements."""
        try:
            schema_name = arguments.get("schema_name")
            candidate_json = arguments.get("candidate_json")
            
            if not schema_name or not candidate_json:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text", 
                            "text": "schema_name and candidate_json are required"
                        }
                    ]
                }

            # Get current policy rules for validation
            policy_entries = await self._query_policy_memory()
            
            # Extract required sections from policy
            required_sections = self._extract_required_sections(policy_entries)
            
            # Validate the JSON structure
            validation_result = self._validate_json_structure(
                candidate_json, 
                schema_name, 
                required_sections
            )

            if validation_result["is_valid"]:
                response_text = (
                    f"✅ JSON validation passed"
                    f"\n📋 Schema: {schema_name}"
                    f"\n📝 Required sections: {len(required_sections)}"
                    f"\n✓ All requirements met"
                )
            else:
                response_text = (
                    f"❌ JSON validation failed"
                    f"\n📋 Schema: {schema_name}"
                    f"\n🚨 Issues found: {len(validation_result['errors'])}"
                    f"\n\n**Validation Errors:**"
                    f"\n{chr(10).join(validation_result['errors'])}"
                )

            return {
                "content": [
                    {"type": "text", "text": response_text}
                ]
            }

        except Exception as e:
            logger.error(f"Error validating JSON: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error validating JSON: {str(e)}"}
                ]
            }

    async def handle_log_policy_violation(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a policy violation for compliance tracking."""
        try:
            agent_id = arguments.get("agent_id")
            rule_id = arguments.get("rule_id")
            context = arguments.get("context", {})
            
            if not agent_id or not rule_id:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id and rule_id are required"}
                    ]
                }

            # Store violation in policy violations collection
            violation_entry = {
                "agent_id": agent_id,
                "rule_id": rule_id,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": await self._get_rule_severity(rule_id)
            }

            # Store in violations collection
            storage_result = await self._store_policy_violation(violation_entry)
            
            if storage_result["success"]:
                response_text = (
                    f"🚨 Policy violation logged"
                    f"\n👤 Agent: {agent_id}"
                    f"\n📋 Rule: {rule_id}"
                    f"\n⚡ Severity: {violation_entry['severity']}"
                    f"\n🕒 Timestamp: {violation_entry['timestamp']}"
                )
                
                # Add context if provided
                if context:
                    response_text += f"\n📄 Context: {context}"

                return {
                    "content": [
                        {"type": "text", "text": response_text}
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text", 
                            "text": (
                                f"Failed to log violation: "
                                f"{storage_result.get('error', 'Unknown error')}"
                            )
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Error logging policy violation: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error logging violation: {str(e)}"}
                ]
            }

    # Guidance Tools
    def _get_guidance_content(self, guidance_type: str) -> Dict[str, Any]:
        """Get guidance content for a specific type."""
        guidance_map = {
            "memory_usage": (
                "# Memory Usage Best Practices\n\n"
                "## Core Principles\n"
                "• Layer-appropriate storage (Global/Learned/Agent)\n"
                "• Query optimization with specific terms\n"
                "• Well-structured, searchable content\n\n"
                "## Best Practices\n"
                "✅ Before storing: verify uniqueness, choose type, add metadata\n"
                "✅ When querying: start specific, use filters, adjust thresholds\n"
                "✅ Maintenance: deduplicate, update, clean obsolete content\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "context_preservation": (
                "# Context Preservation Strategy\n\n"
                "## Key Strategies\n"
                "• Session checkpoints with key decisions\n"
                "• Progressive context building across sessions\n"
                "• Categorize: immediate/session/historical context\n\n"
                "## Implementation\n"
                "✅ Before session end: summarize outcomes, store context, link memories\n"
                "✅ Session startup: query previous context, rebuild state, identify next steps\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "query_optimization": (
                "# Query Optimization Best Practices\n\n"
                "## Fundamentals\n"
                "• Specificity over breadth\n"
                "• Context-aware queries with technical terms\n"
                "• Memory type targeting (Global/Learned/Agent)\n\n"
                "## Advanced Techniques\n"
                "✅ Similarity thresholds: 0.9+ exact, 0.8-0.9 related, 0.7-0.8 discovery\n"
                "✅ Progressive queries: start specific, broaden if needed\n"
                "✅ Keyword optimization: technical terms, action words, context markers\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "markdown_optimization": (
                "# Markdown Processing Guidelines\n\n"
                "## Processing Principles\n"
                "• Structure preservation (headings, code blocks, tables)\n"
                "• Metadata extraction (headers, tags, categories)\n"
                "• Content optimization for memory storage\n\n"
                "## Best Practices\n"
                "✅ Pre-processing: clean, normalize, extract key info\n"
                "✅ Chunking: header-based, size-based, context-aware\n"
                "✅ Quality assurance: validate syntax, check metadata\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "duplicate_detection": (
                "# Duplicate Detection Strategy\n\n"
                "## Detection Methods\n"
                "• Cosine similarity analysis (0.95+ exact, 0.85-0.95 near-duplicates)\n"
                "• Content hash comparison\n"
                "• Metadata-based detection\n\n"
                "## Workflow\n"
                "✅ Pre-storage: calculate hash, check matches, flag duplicates\n"
                "✅ Post-storage: periodic scans, review near-duplicates\n"
                "✅ Handling: skip/replace exact, review near-duplicates, cross-reference related\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "directory_processing": (
                "# Directory Processing Best Practices\n\n"
                "## Planning Phase\n"
                "• Directory assessment: size, file types, structure\n"
                "• Processing strategy: batch size, parallel processing, error handling\n\n"
                "## Execution\n"
                "✅ Pre-processing validation: check access, space, connectivity\n"
                "✅ File processing order: prioritize importance, handle dependencies\n"
                "✅ Error recovery: graceful degradation, retry logic, logging\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "memory_type_selection": (
                "# Memory Type Selection Criteria\n\n"
                "## Decision Framework\n"
                "• Who needs this? Everyone→Global, Future agents→Learned, Just me→Agent\n"
                "• How long persist? Permanent→Global/Learned, Session→Agent\n"
                "• Content type? Docs→Global, Insights→Learned, Notes→Agent\n\n"
                "## Examples\n"
                "✅ Global: API docs, policies, specifications\n"
                "✅ Learned: patterns, best practices, lessons learned\n"
                "✅ Agent: current tasks, preferences, session context\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "memory_type_suggestion": (
                "# AI Memory Type Suggestions\n\n"
                "## Detection Factors\n"
                "• Scope indicators: personal pronouns→Agent, universal→Global, learning→Learned\n"
                "• Temporal indicators: \"currently\"→Agent, \"always\"→Global, \"learned\"→Learned\n"
                "• Content patterns: documentation→Global, insights→Learned, tasks→Agent\n\n"
                "## Implementation\n"
                "✅ Analyze content semantically, provide confidence scores\n"
                "✅ Consider context clues, allow user overrides\n"
                "✅ Learn from corrections, improve over time\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "policy_compliance": (
                "# Policy Compliance Guide\n\n"
                "## Framework Understanding\n"
                "• Policy structure: principles, forbidden actions, required sections, style guide\n"
                "• Compliance levels: critical, important, recommended, stylistic\n\n"
                "## Workflow\n"
                "✅ Pre-action: review policies, assess impact, document reasoning\n"
                "✅ During action: monitor conflicts, adjust approach, document decisions\n"
                "✅ Post-action: verify compliance, log questions, update procedures\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            ),
            "policy_violation_recovery": (
                "# Policy Violation Recovery\n\n"
                "## Immediate Response\n"
                "• Stop and assess: halt action, identify violation, assess impact\n"
                "• Document everything: what, when, intended vs actual, impact\n"
                "• Immediate containment: prevent further violations, secure systems\n\n"
                "## Recovery Process\n"
                "✅ Severity assessment: critical, major, minor violations\n"
                "✅ Recovery actions: escalation, investigation, remediation\n"
                "✅ Learning: analyze causes, implement improvements, share lessons\n\n"
                "**Full guidance: see docs/GUIDANCE_CONTENT.md**"
            )
        }
        
        content = guidance_map.get(guidance_type, "Guidance content not found.")
        return {
            "content": [
                {"type": "text", "text": content}
            ]
        }

    def handle_get_memory_usage_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on effective memory usage patterns."""
        return self._get_guidance_content("memory_usage")

    def handle_get_context_preservation_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on preserving context across sessions."""
        return self._get_guidance_content("context_preservation")

    def handle_get_query_optimization_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on optimizing memory queries and retrieval."""
        return self._get_guidance_content("query_optimization")

    def handle_get_markdown_optimization_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on processing and storing markdown content."""
        return self._get_guidance_content("markdown_optimization")

    def handle_get_duplicate_detection_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on detecting and handling duplicate content."""
        return self._get_guidance_content("duplicate_detection")

    def handle_get_directory_processing_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on batch processing directories."""
        return self._get_guidance_content("directory_processing")

    def handle_get_memory_type_selection_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance on selecting appropriate memory types."""
        return self._get_guidance_content("memory_type_selection")

    def handle_get_memory_type_suggestion_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance for AI-powered memory type suggestions."""
        return self._get_guidance_content("memory_type_suggestion")

    def handle_get_policy_compliance_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance for following policy compliance."""
        return self._get_guidance_content("policy_compliance")

    def handle_get_policy_violation_recovery_guidance(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide guidance for recovering from policy violations."""
        return self._get_guidance_content("policy_violation_recovery")

    # Policy Helper Methods
    async def _store_policy_entries(self, entries: list) -> Dict[str, Any]:
        """Store policy entries in Qdrant."""
        try:
            from ..config import Config
            import uuid
            
            success_count = 0
            warnings = []

            for entry in entries:
                # Create vector embedding for the rule text
                embedding = self.memory_manager.embedding_model.encode(entry["text"])
                
                # Generate UUID for Qdrant point ID
                point_id = str(uuid.uuid4())
                
                # Create point for storage
                point = {
                    "id": point_id,
                    "vector": embedding.tolist(),
                    "payload": entry
                }

                # Store in policy memory collection
                try:
                    self.memory_manager.client.upsert(
                        collection_name=Config.POLICY_MEMORY_COLLECTION,
                        points=[point]
                    )
                    success_count += 1
                except Exception as e:
                    warnings.append(
                        f"Failed to store {entry['rule_id']}: {str(e)}"
                    )

            return {
                "success": success_count > 0,
                "stored_count": success_count,
                "total_count": len(entries),
                "warnings": warnings
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _query_policy_memory(
        self, version: str = "latest", limit: int = 1000
    ) -> list:
        """Query policy memory collection."""
        try:
            from ..config import Config
            
            # Create a dummy query vector for searching all policies
            query_vector = [0.0] * Config.EMBEDDING_DIMENSION
            
            # Search with filter for version if not "latest"
            filter_condition = None
            if version != "latest":
                filter_condition = {
                    "must": [{"key": "policy_version", "match": {"value": version}}]
                }

            results = self.memory_manager.client.search(
                collection_name=Config.POLICY_MEMORY_COLLECTION,
                query_vector=query_vector,
                query_filter=filter_condition,
                limit=limit,
                with_payload=True
            )

            return [result.payload for result in results]

        except Exception as e:
            logger.error(f"Error querying policy memory: {e}")
            return []

    def _build_rulebook_structure(self, policy_entries: list) -> Dict[str, Any]:
        """Build structured rulebook from policy entries."""
        try:
            # Group by section
            sections: Dict[str, list] = {}
            policy_hash = None
            
            for entry in policy_entries:
                section_name = entry.get("section", "Unknown")
                if section_name not in sections:
                    sections[section_name] = []
                
                sections[section_name].append({
                    "rule_id": entry["rule_id"],
                    "text": entry["text"],
                    "severity": entry["severity"]
                })
                
                # Get policy hash from first entry
                if policy_hash is None:
                    policy_hash = entry.get("policy_hash", "unknown")

            # Create structured rulebook
            rulebook = {
                "policy_version": (
                    policy_entries[0].get("policy_version", "unknown") 
                    if policy_entries else "unknown"
                ),
                "policy_hash": policy_hash,
                "sections": sections,
                "total_rules": len(policy_entries)
            }

            return {
                "policy_hash": policy_hash,
                "sections": sections,
                "json": json.dumps(rulebook, indent=2)
            }

        except Exception as e:
            logger.error(f"Error building rulebook: {e}")
            return {"policy_hash": "unknown", "sections": {}, "json": "{}"}

    def _extract_required_sections(self, policy_entries: list) -> list:
        """Extract required sections from policy entries."""
        # Find rules that specify required sections (R- prefix typically)
        required_sections = []
        for entry in policy_entries:
            if (entry["rule_id"].startswith("R-") 
                and "required" in entry["text"].lower()):
                # Extract section names from rule text
                # This is a simplified extraction - could be enhanced
                required_sections.append(entry["section"])
        
        return list(set(required_sections))

    def _validate_json_structure(
        self, candidate_json: str, schema_name: str, required_sections: list
    ) -> Dict[str, Any]:
        """Validate JSON structure against policy requirements."""
        try:
            # Parse JSON
            try:
                data = json.loads(candidate_json)
            except json.JSONDecodeError as e:
                return {
                    "is_valid": False,
                    "errors": [f"Invalid JSON format: {str(e)}"]
                }

            errors = []
            
            # Check for required sections based on schema
            if isinstance(data, dict):
                data_sections = set(data.keys())
                missing_sections = set(required_sections) - data_sections
                
                if missing_sections:
                    errors.append(
                        f"Missing required sections: {list(missing_sections)}"
                    )
            else:
                errors.append("JSON must be an object with sections")

            return {
                "is_valid": len(errors) == 0,
                "errors": errors
            }

        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }

    async def _get_rule_severity(self, rule_id: str) -> str:
        """Get severity level for a rule ID."""
        try:
            # Query for the specific rule
            policy_entries = await self._query_policy_memory()
            
            for entry in policy_entries:
                if entry["rule_id"] == rule_id:
                    return entry.get("severity", "medium")
            
            # Default severity if rule not found
            return "medium"

        except Exception:
            return "medium"

    async def _store_policy_violation(
        self, violation_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store policy violation in violations collection."""
        try:
            from ..config import Config
            import uuid

            # Create vector embedding for the violation context
            context_text = (
                f"{violation_entry['rule_id']} "
                f"{violation_entry.get('context', '')}"
            )
            embedding = self.memory_manager.embedding_model.encode(context_text)
            
            # Create point for storage
            point = {
                "id": str(uuid.uuid4()),
                "vector": embedding.tolist(),
                "payload": violation_entry
            }

            # Store in violations collection
            self.memory_manager.client.upsert(
                collection_name=Config.POLICY_VIOLATIONS_COLLECTION,
                points=[point]
            )

            return {"success": True}

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }