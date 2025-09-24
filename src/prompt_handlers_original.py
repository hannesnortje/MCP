"""
Step 6: MCP Prompts Implementation

Comprehensive prompt handler system providing:
- Core agent startup prompt with policy binding
- Alias prompts for common scenarios
- Guidance prompts for best practices
- Policy compliance prompts
- Input validation and error handling
- MCP protocol compliance
"""

from datetime import datetime
from typing import Dict, Any, List
import uuid
from .server_config import get_logger

logger = get_logger("prompt-handlers")


class PromptHandlers:
    """
    Handles MCP prompts for agent guidance and startup templates.

    Provides 13 prompts:
    - 1 Core prompt: agent_startup
    - 2 Alias prompts: development_agent_startup, testing_agent_startup
    - 10 Guidance prompts: memory usage, optimization, policy compliance
    """

    def __init__(self, memory_manager: Any = None) -> None:
        """Initialize prompt handlers with optional memory manager."""
        self.memory_manager = memory_manager
        # Initialize policy processor for agent startup operations
        from .policy_processor import PolicyProcessor
        self.policy_processor = PolicyProcessor()
        logger.info("PromptHandlers initialized")
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompts with metadata.

        Returns:
            List of prompt metadata dictionaries with name, description,
            arguments
        """
        return [
            # Core Prompt
            {
                "name": "agent_startup",
                "description": (
                    "Comprehensive agent initialization prompt with memory "
                    "layer configuration, role assignment, and policy binding"
                ),
                "arguments": [
                    {
                        "name": "agent_id",
                        "description": (
                            "Unique identifier for the agent "
                            "(auto-generated if not provided)"
                        ),
                        "required": False
                    },
                    {
                        "name": "agent_role",
                        "description": (
                            "Agent role (developer, analyst, admin) - "
                            "defaults to 'general'"
                        ),
                        "required": False
                    },
                    {
                        "name": "memory_layers",
                        "description": (
                            "Comma-separated list of memory layers "
                            "(global,learned,agent)"
                        ),
                        "required": False
                    },
                    {
                        "name": "policy_version",
                        "description": (
                            "Policy version for compliance tracking"
                        ),
                        "required": False
                    },
                    {
                        "name": "policy_hash",
                        "description": (
                            "Policy hash for integrity verification"
                        ),
                        "required": False
                    }
                ]
            },
            
            # Alias Prompts
            {
                "name": "development_agent_startup",
                "description": (
                    "Alias for agent_startup optimized for development agents"
                ),
                "arguments": [
                    {
                        "name": "agent_id",
                        "description": (
                            "Unique identifier for the development agent"
                        ),
                        "required": True
                    }
                ]
            },
            {
                "name": "testing_agent_startup",
                "description": (
                    "Alias for agent_startup optimized for testing agents"
                ),
                "arguments": [
                    {
                        "name": "agent_id",
                        "description": (
                            "Unique identifier for the testing agent"
                        ),
                        "required": True
                    }
                ]
            },
            
            # Guidance Prompts (no arguments)
            {
                "name": "agent_memory_usage_patterns",
                "description": (
                    "Best practices for agents using the memory system"
                ),
                "arguments": []
            },
            {
                "name": "context_preservation_strategy",
                "description": (
                    "Strategies for maintaining context across sessions"
                ),
                "arguments": []
            },
            {
                "name": "memory_query_optimization",
                "description": (
                    "Techniques for optimizing memory queries and retrieval"
                ),
                "arguments": []
            },
            {
                "name": "markdown_optimization_rules",
                "description": (
                    "Guidelines for processing and storing markdown content"
                ),
                "arguments": []
            },
            {
                "name": "memory_type_selection_criteria",
                "description": (
                    "Criteria for selecting appropriate memory types"
                ),
                "arguments": []
            },
            {
                "name": "duplicate_detection_strategy",
                "description": (
                    "Strategies for detecting and handling duplicate content"
                ),
                "arguments": []
            },
            {
                "name": "directory_processing_best_practices",
                "description": (
                    "Best practices for batch processing directories"
                ),
                "arguments": []
            },
            {
                "name": "memory_type_suggestion_guidelines",
                "description": (
                    "Guidelines for AI-powered memory type suggestions"
                ),
                "arguments": []
            },
            
            # Policy Prompts
            {
                "name": "final_checklist",
                "description": (
                    "Pre-finalization policy compliance checklist"
                ),
                "arguments": []
            },
            {
                "name": "policy_compliance_guide",
                "description": (
                    "Comprehensive guide for following the policy rulebook"
                ),
                "arguments": []
            },
            {
                "name": "policy_violation_recovery",
                "description": (
                    "Recovery procedures when policy conflicts arise"
                ),
                "arguments": []
            }
        ]
    
    async def get_prompt(
        self, name: str, arguments: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Get a specific prompt with argument substitution.
        
        Args:
            name: The prompt name
            arguments: Dictionary of argument values
            
        Returns:
            Dictionary with prompt content and metadata
        """
        if arguments is None:
            arguments = {}
        
        try:
            # Validate prompt exists
            available_prompts = {p["name"]: p for p in self.list_prompts()}
            if name not in available_prompts:
                return {
                    "status": "error",
                    "error": f"Unknown prompt: {name}"
                }
            
            prompt_meta = available_prompts[name]
            
            # Validate required arguments
            for arg_spec in prompt_meta["arguments"]:
                if arg_spec["required"] and arg_spec["name"] not in arguments:
                    return {
                        "status": "error",
                        "error": (
                            f"Missing required argument: {arg_spec['name']}"
                        )
                    }
            
            # Route to appropriate handler
            if name == "agent_startup":
                return await self._get_agent_startup_prompt(arguments)
            elif name == "development_agent_startup":
                return await self._get_development_agent_startup_prompt(
                    arguments
                )
            elif name == "testing_agent_startup":
                return await self._get_testing_agent_startup_prompt(arguments)
            elif name == "agent_memory_usage_patterns":
                return self._get_agent_memory_usage_patterns_prompt()
            elif name == "context_preservation_strategy":
                return self._get_context_preservation_strategy_prompt()
            elif name == "memory_query_optimization":
                return self._get_memory_query_optimization_prompt()
            elif name == "markdown_optimization_rules":
                return self._get_markdown_optimization_rules_prompt()
            elif name == "memory_type_selection_criteria":
                return self._get_memory_type_selection_criteria_prompt()
            elif name == "duplicate_detection_strategy":
                return self._get_duplicate_detection_strategy_prompt()
            elif name == "directory_processing_best_practices":
                return self._get_directory_processing_best_practices_prompt()
            elif name == "memory_type_suggestion_guidelines":
                return self._get_memory_type_suggestion_guidelines_prompt()
            elif name == "final_checklist":
                return self._get_final_checklist_prompt()
            elif name == "policy_compliance_guide":
                return self._get_policy_compliance_guide_prompt()
            elif name == "policy_violation_recovery":
                return self._get_policy_violation_recovery_prompt()
            else:
                return {
                    "status": "error",
                    "error": f"Handler not implemented for prompt: {name}"
                }
                
        except Exception as e:
            logger.error(f"Error getting prompt {name}: {e}")
            return {
                "status": "error",
                "error": f"Failed to get prompt: {str(e)}"
            }
    
    async def _get_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Core agent startup prompt with full configuration and initialization.
        """
        agent_id = arguments.get("agent_id")
        agent_role = arguments.get("agent_role")
        memory_layers = arguments.get("memory_layers", "global,learned")
        policy_version = arguments.get("policy_version", "latest")
        policy_hash = arguments.get("policy_hash", "")
        
        # Auto-generate agent_id if not provided
        if not agent_id:
            # Generate a proper UUID for Qdrant compatibility
            agent_id = str(uuid.uuid4())
        
        # Auto-generate agent_role if not provided
        if not agent_role:
            agent_role = "general"
        
        # Parse memory layers
        if isinstance(memory_layers, str):
            layer_list = [layer.strip() for layer in memory_layers.split(",")]
        else:
            layer_list = memory_layers or ["global", "learned"]

        initialization_messages = []
        errors = []

        # Step 1: Register the agent
        try:
            if self.memory_manager:
                agent_result = await self.memory_manager.register_agent(
                    agent_id=agent_id,
                    agent_role=agent_role,
                    memory_layers=layer_list
                )
                
                if agent_result["success"]:
                    initialization_messages.append(
                        f"✅ Agent '{agent_id}' registered successfully"
                    )
                else:
                    errors.append(
                        f"❌ Agent registration failed: "
                        f"{agent_result.get('error', 'Unknown error')}"
                    )
            else:
                errors.append("❌ Memory manager not available")
        except Exception as e:
            errors.append(f"❌ Agent registration error: {str(e)}")

        # Step 2: Load and bind policies
        try:
            if self.policy_processor:
                policy_result = await \
                    self.policy_processor.build_canonical_policy(
                        directory=None,  # Use default policy directory
                        policy_version=policy_version
                    )
                
                if policy_result["success"]:
                    initialization_messages.append(
                        f"✅ Policy version '{policy_version}' loaded"
                    )
                    initialization_messages.append(
                        f"📁 Files processed: "
                        f"{policy_result.get('files_processed', 0)}"
                    )
                    initialization_messages.append(
                        f"📝 Rules loaded: "
                        f"{policy_result.get('unique_rules', 0)}"
                    )
                    
                    # Update policy hash if we got one from policy load
                    if policy_result.get('policy_hash') and not policy_hash:
                        policy_hash = policy_result['policy_hash']
                        
                else:
                    errors.append(
                        f"❌ Policy loading failed: "
                        f"{policy_result.get('error', 'Unknown error')}"
                    )
            else:
                errors.append("❌ Policy processor not available")
        except Exception as e:
            errors.append(f"❌ Policy loading error: {str(e)}")

        # Get system info
        system_info = ""
        try:
            if self.memory_manager:
                agents_result = await self.memory_manager.list_agents()
                agent_count = len(agents_result) if agents_result else 0
                system_info = f"\n📊 System Status: {agent_count} agents active"
        except Exception as e:
            system_info = f"\n⚠️ System Status: Unable to fetch ({str(e)})"

        # Determine overall status
        if errors:
            status = "error"
            status_icon = "❌"
            status_text = "FAILED"
        else:
            status = "success"
            status_icon = "✅"
            status_text = "SUCCESS"

        # Build response content
        response_lines = [
            f"# Agent Startup {status_text}",
            "",
            "## Agent Identity",
            f"- **Agent ID:** `{agent_id}`",
            f"- **Role:** `{agent_role}`",
            f"- **Initialization Time:** {datetime.now().isoformat()}",
            "",
            "## Initialization Results"
        ]
        
        # Add success messages
        if initialization_messages:
            response_lines.extend(initialization_messages)
            
        # Add error messages
        if errors:
            response_lines.append("")
            response_lines.append("### Errors:")
            response_lines.extend(errors)

        # Calculate policy hash display
        policy_hash_display = (
            policy_hash[:12] + '...' if policy_hash
            else 'Not available'
        )

        response_lines.extend([
            "",
            "## Configuration",
            f"- **Memory Layers:** {', '.join(layer_list)}",
            f"- **Policy Version:** `{policy_version}`",
            f"- **Policy Hash:** `{policy_hash_display}`",
            "",
            f"{status_icon} Agent initialization {status_text.lower()}",
            system_info
        ])

        prompt_content = "\n".join(response_lines)
        
        return {
            "status": status,
            "prompt": {
                "name": "agent_startup",
                "content": prompt_content,
                "arguments_used": arguments,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "agent_id": agent_id,
                    "agent_role": agent_role,
                    "memory_layers": layer_list,
                    "policy_version": policy_version,
                    "policy_hash": policy_hash,
                    "initialization_success": len(errors) == 0,
                    "errors": errors
                }
            }
        }
    
    async def _get_development_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Alias prompt optimized for development agents."""
        # Use agent_startup with development defaults
        dev_arguments = {
            "agent_id": arguments.get("agent_id"),
            "agent_role": "developer",
            "memory_layers": "global,learned,agent",
            "policy_version": "latest",
            "policy_hash": ""
        }
        
        result = await self._get_agent_startup_prompt(dev_arguments)
        if result["status"] == "success":
            result["prompt"]["name"] = "development_agent_startup"
            result["prompt"]["content"] = (
                "# 🚀 Development Agent Startup\n\n" +
                result["prompt"]["content"]
            )
        
        return result
    
    async def _get_testing_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Alias prompt optimized for testing agents."""
        # Use agent_startup with testing defaults
        test_arguments = {
            "agent_id": arguments.get("agent_id"),
            "agent_role": "testing",
            "memory_layers": "global,learned",
            "policy_version": "latest",
            "policy_hash": ""
        }
        
        result = await self._get_agent_startup_prompt(test_arguments)
        if result["status"] == "success":
            result["prompt"]["name"] = "testing_agent_startup"
            result["prompt"]["content"] = (
                "# 🧪 Testing Agent Startup\n\n" +
                result["prompt"]["content"]
            )
        
        return result
    
    def _get_agent_memory_usage_patterns_prompt(self) -> Dict[str, Any]:
        """Guidance on effective memory usage patterns."""
        content = """# Agent Memory Usage Patterns

## Core Principles
1. **Layer-Appropriate Storage**
   - Global: Shared knowledge and documentation
   - Learned: Patterns, insights, and accumulated wisdom
   - Agent: Personal context and task-specific information

2. **Query Optimization**
   - Use specific, targeted queries over broad searches
   - Include relevant context keywords
   - Leverage similarity search effectively

3. **Content Structure**
   - Store well-structured, searchable content
   - Use descriptive metadata and tags
   - Maintain consistent formatting

## Best Practices
### Before Storing
- ✅ Verify content isn't already stored
- ✅ Choose appropriate memory type
- ✅ Add relevant metadata and tags
- ✅ Structure content for searchability

### When Querying
- ✅ Start with specific terms
- ✅ Use memory type filters when appropriate
- ✅ Adjust similarity thresholds based on needs
- ✅ Review results for relevance

### Maintenance
- ✅ Regular deduplication checks
- ✅ Update outdated information
- ✅ Clean up temporary or obsolete content
- ✅ Monitor memory usage metrics

## Common Patterns
1. **Context Preservation:** Store conversation context before major 
   transitions
2. **Progressive Learning:** Build on previous memories for better outcomes
3. **Collaborative Memory:** Share insights in global/learned layers 
   appropriately
4. **Efficient Retrieval:** Use targeted queries with appropriate 
   similarity thresholds

---
*Follow these patterns for optimal memory system utilization*"""

        return {
            "status": "success",
            "prompt": {
                "name": "agent_memory_usage_patterns",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_context_preservation_strategy_prompt(self) -> Dict[str, Any]:
        """Guidance on preserving context across sessions."""
        content = """# Context Preservation Strategy

## Why Context Preservation Matters
Maintaining context across sessions ensures continuity, reduces redundant 
work, and enables agents to build on previous interactions effectively.

## Context Storage Strategies

### 1. Session Checkpoints
- Store key decisions and outcomes at natural breakpoints
- Include reasoning behind important choices
- Tag with session identifiers for easy retrieval

### 2. Progressive Context Building
- Start sessions by retrieving relevant previous context
- Layer new context on top of existing knowledge
- Update context summaries periodically

### 3. Context Categorization
- **Immediate Context:** Current task and immediate decisions
- **Session Context:** Broader goals and multi-step processes
- **Historical Context:** Long-term patterns and learnings

## Implementation Guidelines

### Before Session End
1. **Summarize Key Outcomes**
   - What was accomplished?
   - What decisions were made?
   - What should continue next time?

2. **Store Critical Context**
   ```
   Memory Type: learned or agent (depending on scope)
   Tags: session_id, context_preservation, [task_type]
   Content: Structured summary with key points
   ```

3. **Link Related Memories**
   - Reference previous related work
   - Include continuation instructions
   - Note any dependencies or prerequisites

### Session Startup
1. **Query for Previous Context**
   - Search for session_id or task-related context
   - Review recent decisions and outcomes
   - Identify where to continue

2. **Validate Context Currency**
   - Check if previous context is still relevant
   - Update any changed assumptions
   - Merge with new requirements

## Context Preservation Checklist
- [ ] Key decisions documented with reasoning
- [ ] Session outcomes clearly summarized
- [ ] Next steps explicitly defined
- [ ] Related memories properly linked
- [ ] Context tagged for easy retrieval
- [ ] Session startup routine established

---
*Effective context preservation enables seamless continuity across sessions*"""

        return {
            "status": "success", 
            "prompt": {
                "name": "context_preservation_strategy",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_memory_query_optimization_prompt(self) -> Dict[str, Any]:
        """Guidance on optimizing memory queries."""
        content = """**GUIDANCE: Memory Query Optimization Best Practices**

This is guidance content to help you optimize memory queries. This is not an instruction to take action.

## Query Performance Principles

### 1. Specificity Over Breadth
- ✅ Use specific terms and phrases
- ✅ Include domain-specific keywords  
- ✅ Target exact concepts when possible
- ❌ Avoid overly generic queries

### 2. Strategic Memory Type Filtering
- **Global Memory:** For shared knowledge and documentation
- **Learned Memory:** For patterns, insights, and best practices
- **Agent Memory:** For personal context and task-specific info

### 3. Similarity Threshold Optimization
- **High (0.9-1.0):** Exact matches and near-duplicates
- **Medium (0.7-0.9):** Related content and concepts
- **Low (0.5-0.7):** Broader context and associations

## Advanced Query Techniques

### Multi-Stage Queries
1. **Broad Discovery:** Lower threshold to find relevant areas
2. **Focused Retrieval:** Higher threshold for specific content
3. **Context Expansion:** Medium threshold for related concepts

### Query Refinement Patterns
```
Initial Query: "API documentation"
Refined Query: "REST API endpoints authentication middleware"
Specific Query: "Express.js JWT authentication implementation"
```

### Metadata-Enhanced Queries
- Include relevant tags in query text
- Reference source files or authors when known
- Use temporal indicators (recent, latest, updated)

## Performance Optimization

### Query Construction
- **Keywords First:** Start with most important terms
- **Context Second:** Add domain and scope indicators
- **Modifiers Last:** Include qualifiers and constraints

### Result Processing
- **Relevance Scoring:** Check similarity scores match expectations
- **Content Validation:** Verify results address the actual query
- **Iterative Refinement:** Adjust queries based on result quality

### Batch Query Strategies
- Group related queries to minimize API calls
- Use query results to inform subsequent queries
- Cache frequently accessed content locally

## Query Optimization Checklist
- [ ] Query terms are specific and targeted
- [ ] Appropriate memory type selected
- [ ] Similarity threshold matches intent
- [ ] Metadata and tags utilized effectively
- [ ] Results validated for relevance
- [ ] Query refined based on outcomes

## Common Anti-Patterns
- ❌ Single-word generic queries
- ❌ Ignoring memory type advantages
- ❌ Using inappropriate similarity thresholds
- ❌ Not iterating on poor results
- ❌ Overlooking metadata opportunities

---
*Optimized queries lead to better results and improved system performance*"""

        return {
            "status": "success",
            "prompt": {
                "name": "memory_query_optimization", 
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_markdown_optimization_rules_prompt(self) -> Dict[str, Any]:
        """Guidelines for processing markdown content."""
        content = """# Markdown Optimization Rules

## Content Processing Guidelines

### 1. Structure Preservation
- ✅ Maintain heading hierarchy for navigation
- ✅ Preserve code blocks with language specifications
- ✅ Keep table structures intact
- ✅ Retain link references and relationships

### 2. Metadata Extraction
- **Headers:** Extract as navigation markers
- **Tags:** Identify from content and frontmatter  
- **Categories:** Infer from structure and content
- **Relationships:** Track internal and external links

### 3. Content Optimization
```markdown
Before: ## Some Random Heading
After: ## API Authentication Methods

Before: Code without context
After: ```javascript
// JWT token validation middleware
```

### 4. Memory Type Selection
- **Global:** Documentation, specifications, references
- **Learned:** Patterns, examples, best practices extracted from docs
- **Agent:** Personal notes, customizations, task-specific content

## Processing Best Practices

### Pre-Processing
1. **Clean and Normalize**
   - Remove excessive whitespace
   - Standardize heading styles
   - Fix broken markdown syntax

2. **Extract Key Information**
   - Document title and description
   - Section headings for navigation
   - Code examples and their contexts
   - Links and references

3. **Add Processing Metadata**
   - Source file path
   - Processing timestamp  
   - Content hash for deduplication
   - Suggested memory type

### Content Chunking Strategy
- **Header-Based:** Split at major headings (H1, H2)
- **Size-Based:** Target 900 tokens with 200 overlap
- **Context-Aware:** Keep related content together
- **Code-Preserving:** Don't split code blocks

### Tag Generation
- **From Headings:** Extract key terms from section titles
- **From Content:** Identify technical terms and concepts
- **From Context:** Add domain and category tags
- **From Structure:** Include document type tags

## Quality Assurance

### Content Validation
- [ ] Markdown syntax is valid and renders correctly
- [ ] Code blocks have proper language annotations
- [ ] Links are functional or marked as internal references
- [ ] Tables are properly formatted
- [ ] Images have alt text and valid paths

### Processing Validation
- [ ] Content chunked at appropriate boundaries
- [ ] Metadata accurately extracted
- [ ] Tags are relevant and useful
- [ ] Memory type suggestion is appropriate
- [ ] Deduplication check completed

## Markdown Processing Checklist
- [ ] Source content validated and cleaned
- [ ] Structure preserved during processing
- [ ] Metadata extracted comprehensively
- [ ] Appropriate chunking strategy applied
- [ ] Tags generated from multiple sources
- [ ] Memory type suggested based on content
- [ ] Quality validation completed

---
*Proper markdown processing ensures maximum searchability and utility*"""

        return {
            "status": "success",
            "prompt": {
                "name": "markdown_optimization_rules",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_memory_type_selection_criteria_prompt(self) -> Dict[str, Any]:
        """Criteria for selecting appropriate memory types."""
        content = """# Memory Type Selection Criteria

## Memory Type Overview

### Global Memory
**Purpose:** Shared knowledge accessible to all agents
**Best For:**
- Documentation and specifications
- Reference materials and guides
- Shared standards and policies
- Common knowledge and facts

### Learned Memory  
**Purpose:** Accumulated insights and patterns
**Best For:**
- Best practices and methodologies
- Patterns and solutions that worked
- Lessons learned from experience
- Generalized insights and wisdom

### Agent Memory
**Purpose:** Personal context and task-specific information
**Best For:**
- Personal notes and customizations
- Task-specific context and progress
- Individual preferences and settings
- Temporary working information

## Selection Decision Matrix

### Content Characteristics
| Characteristic | Global | Learned | Agent |
|---------------|--------|---------|-------|
| **Audience** | All agents | Multiple agents | Single agent |
| **Longevity** | Permanent | Long-term | Variable |
| **Specificity** | General | Pattern-based | Highly specific |
| **Authority** | Official | Experiential | Personal |

### Use Case Examples

#### Global Memory ✅
- API documentation
- Company policies  
- Technical specifications
- Reference architectures
- Shared vocabulary/glossaries

#### Learned Memory ✅
- "When X happens, try Y approach"
- Code patterns that solved problems
- Architecture decisions and their outcomes
- Debugging strategies that worked
- Performance optimization techniques

#### Agent Memory ✅
- Current task progress and context
- Personal code preferences
- Individual learning notes
- Session-specific information
- Customized workflows

## AI-Powered Suggestions

### Content Analysis Indicators
1. **Scope Indicators**
   - Global: "standard", "official", "documentation"
   - Learned: "pattern", "best practice", "lesson"
   - Agent: "my", "current", "working on"

2. **Audience Indicators**
   - Global: "everyone should", "all developers"
   - Learned: "teams have found", "experience shows"
   - Agent: "I need", "my task", "personal note"

3. **Temporal Indicators**
   - Global: Timeless, reference material
   - Learned: Historical patterns, evolving wisdom
   - Agent: Current, temporary, session-based

### Suggestion Confidence Levels
- **High (90%+):** Clear indicators point to one type
- **Medium (70-89%):** Strong indicators with some ambiguity
- **Low (<70%):** Unclear, human judgment recommended

## Decision Flowchart
```
1. Is this official documentation or policy?
   YES → Global Memory
   NO → Continue

2. Is this a pattern/insight from experience?
   YES → Learned Memory  
   NO → Continue

3. Is this personal or task-specific?
   YES → Agent Memory
   NO → Review criteria again
```

## Memory Type Selection Checklist
- [ ] Content purpose and audience identified
- [ ] Longevity and permanence assessed
- [ ] Specificity and scope evaluated
- [ ] AI suggestions reviewed and validated
- [ ] Decision documented with reasoning
- [ ] Alternative memory types considered

## Common Selection Mistakes
- ❌ Storing personal notes in global memory
- ❌ Putting official docs in learned memory
- ❌ Using agent memory for sharable patterns
- ❌ Ignoring audience and scope considerations
- ❌ Not leveraging AI suggestion system

---
*Proper memory type selection ensures content reaches the right audience*"""

        return {
            "status": "success",
            "prompt": {
                "name": "memory_type_selection_criteria",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_duplicate_detection_strategy_prompt(self) -> Dict[str, Any]:
        """Strategies for detecting and handling duplicates."""
        content = """# Duplicate Detection Strategy

## Detection Methods

### 1. Cosine Similarity Analysis
- **High Similarity (0.95+):** Likely exact duplicates
- **Medium Similarity (0.85-0.95):** Near-duplicates requiring review
- **Lower Similarity (0.80-0.85):** Potentially related content

### 2. Content Hash Comparison
- **Exact Matches:** Identical content with different metadata
- **Normalized Matches:** Same content after whitespace/formatting normalization
- **Partial Matches:** Significant content overlap

### 3. Metadata-Based Detection
- **Same Source File:** Multiple ingestions of same document
- **Similar Titles:** Documents with nearly identical titles
- **Timestamp Clustering:** Multiple entries from same processing batch

## Deduplication Workflow

### 1. Pre-Storage Validation
```
1. Calculate content hash
2. Check for exact hash matches
3. Run similarity search (threshold: 0.85)
4. Flag potential duplicates for review
5. Prompt for human decision if ambiguous
```

### 2. Post-Storage Analysis
```
1. Periodic similarity scans across memory types
2. Identify clusters of related content
3. Review near-duplicates (0.85-0.95 range)
4. Merge or consolidate where appropriate
```

### 3. Handling Strategies

#### For Exact Duplicates (0.95+)
- **Action:** Skip storage or replace existing
- **Preserve:** Most recent or most complete version
- **Log:** Deduplication event for audit trail

#### For Near-Duplicates (0.85-0.95)
- **Action:** Flag for human review
- **Options:** Merge, keep both, or choose one
- **Consider:** Different perspectives or contexts

#### For Related Content (0.80-0.85)
- **Action:** Log relationship but keep both
- **Enhancement:** Add cross-references
- **Monitor:** For future consolidation opportunities

## Advanced Strategies

### Content Versioning
- Track content evolution over time
- Maintain version history for important documents
- Handle updates vs. true duplicates differently

### Context-Aware Deduplication
- Consider memory type in similarity decisions
- Allow duplicates across different memory layers when justified
- Factor in agent ownership for agent memory

### Batch Processing Optimization
- Process similar documents together
- Use clustering to identify potential duplicate groups
- Optimize similarity calculations for large batches

## Quality Metrics

### Detection Accuracy
- **Precision:** Percentage of flagged items that are actual duplicates
- **Recall:** Percentage of actual duplicates that are detected
- **F1 Score:** Harmonic mean of precision and recall

### Processing Efficiency
- Time per document for duplicate detection
- Memory usage during similarity calculations
- Throughput for large document batches

## Deduplication Checklist
- [ ] Similarity thresholds configured appropriately
- [ ] Pre-storage validation implemented
- [ ] Human review process for near-duplicates
- [ ] Logging and audit trail maintained
- [ ] Performance metrics tracked
- [ ] Periodic system-wide deduplication scheduled

## Configuration Guidelines
```yaml
deduplication:
  exact_match_threshold: 0.95
  near_duplicate_threshold: 0.85
  related_content_threshold: 0.80
  require_human_review: true
  preserve_version_history: true
  max_similarity_results: 10
```

---
*Effective duplicate detection maintains content quality while preventing redundancy*"""

        return {
            "status": "success",
            "prompt": {
                "name": "duplicate_detection_strategy",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_directory_processing_best_practices_prompt(self) -> Dict[str, Any]:
        """Best practices for batch processing directories."""
        content = """# Directory Processing Best Practices

## Planning Phase

### 1. Directory Assessment
- **Size Analysis:** Count files and estimate processing time
- **File Type Distribution:** Identify markdown vs. other files
- **Structure Analysis:** Understand directory organization
- **Priority Assessment:** Identify high-value directories first

### 2. Processing Strategy
- **Batch Size:** Optimal number of files per batch (recommended: 10-50)
- **Parallel Processing:** Balance speed vs. resource usage
- **Error Handling:** Strategy for failed file processing
- **Progress Tracking:** Monitor completion and identify bottlenecks

## Execution Best Practices

### 1. Pre-Processing Validation
```
Directory Checklist:
- [ ] Directory exists and is accessible
- [ ] Sufficient disk space for processing
- [ ] Network connectivity to vector database
- [ ] Required permissions for file access
- [ ] Backup strategy in place
```

### 2. File Processing Order
- **Prioritize by importance:** Documentation before examples
- **Size considerations:** Large files processed during low-usage times
- **Dependency handling:** Process referenced files first when possible
- **Update detection:** Skip unchanged files when appropriate

### 3. Error Recovery
- **Graceful Degradation:** Continue processing other files on individual failures
- **Retry Logic:** Attempt failed files with exponential backoff
- **Error Logging:** Detailed logging for post-processing analysis
- **Manual Review:** Queue problematic files for human intervention

## Memory Management

### 1. Content Distribution
- **Global Memory:** Shared documentation and standards
- **Learned Memory:** Extracted patterns and best practices
- **Agent Memory:** Processing logs and personal notes

### 2. Metadata Preservation
- **File Paths:** Maintain directory structure in metadata
- **Processing Time:** Track when content was processed
- **Source Information:** Link back to original files
- **Batch Information:** Group related processed files

## Performance Optimization

### 1. Resource Management
```python
# Recommended settings for directory processing
batch_size = 25  # Files per batch
max_workers = 4  # Parallel processing threads  
chunk_size = 900  # Tokens per chunk
chunk_overlap = 200  # Token overlap
similarity_threshold = 0.85  # Duplicate detection
```

### 2. Progress Monitoring
- **File-level progress:** Track individual file completion
- **Batch-level progress:** Monitor batch completion rates
- **Overall progress:** Directory completion percentage
- **Performance metrics:** Files per minute, errors per batch

### 3. Quality Assurance
- **Content validation:** Verify processed content matches source
- **Metadata accuracy:** Ensure file paths and timestamps are correct
- **Deduplication:** Check for and handle duplicate content
- **Search testing:** Validate that processed content is searchable

## Directory Structure Handling

### 1. Nested Directories
- **Recursive Processing:** Handle subdirectories appropriately
- **Path Preservation:** Maintain full path information
- **Structure Metadata:** Store directory hierarchy information
- **Selective Processing:** Allow inclusion/exclusion patterns

### 2. Special Files
- **README Files:** Process with high priority and global memory
- **Configuration Files:** Extract settings and store as learned memory
- **Example Files:** Tag appropriately and store with context
- **Legacy Files:** Handle deprecated content appropriately

## Post-Processing Activities

### 1. Validation and Verification
- **Completeness Check:** Verify all expected files were processed
- **Content Integrity:** Random sampling to verify accuracy
- **Search Functionality:** Test queries against processed content
- **Performance Baseline:** Establish metrics for future processing

### 2. Documentation and Reporting
- **Processing Summary:** Files processed, errors encountered, time taken
- **Content Distribution:** How content was categorized across memory types
- **Quality Metrics:** Duplicate detection results, content validation
- **Lessons Learned:** Issues encountered and solutions applied

## Directory Processing Checklist
- [ ] Directory assessment completed
- [ ] Processing strategy defined
- [ ] Resource requirements met
- [ ] Error handling configured
- [ ] Progress monitoring setup
- [ ] Quality assurance plan ready
- [ ] Post-processing validation defined

---
*Systematic directory processing ensures comprehensive and reliable content ingestion*"""

        return {
            "status": "success",
            "prompt": {
                "name": "directory_processing_best_practices",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_memory_type_suggestion_guidelines_prompt(self) -> Dict[str, Any]:
        """Guidelines for AI-powered memory type suggestions."""
        content = """# Memory Type Suggestion Guidelines

## AI Suggestion System Overview

The memory type suggestion system analyzes content characteristics to recommend the most appropriate memory type (Global, Learned, or Agent) for storing information.

## Content Analysis Framework

### 1. Linguistic Indicators

#### Global Memory Indicators
- **Authority Language:** "specification", "standard", "official"
- **Universal Scope:** "all users", "everyone", "system-wide"
- **Reference Nature:** "documentation", "reference", "guide"
- **Policy Language:** "must", "required", "mandatory"

#### Learned Memory Indicators  
- **Experience Language:** "learned", "discovered", "found that"
- **Pattern Language:** "best practice", "approach", "strategy"
- **Wisdom Language:** "experience shows", "typically", "usually"
- **Solution Language:** "solved by", "works well", "effective method"

#### Agent Memory Indicators
- **Personal Language:** "my", "I need", "working on", "current"
- **Specific Context:** "this task", "my project", "personal note"
- **Temporary Nature:** "TODO", "reminder", "in progress"
- **Individual Preference:** "prefer", "customize", "personal"

### 2. Content Structure Analysis

#### Document Type Classification
```
Documentation Types → Global Memory:
- API references, user manuals, specifications
- Policy documents, guidelines, standards  
- Shared knowledge bases, wikis

Experience Types → Learned Memory:
- Case studies, lessons learned, retrospectives
- Best practice collections, pattern libraries
- Solution databases, troubleshooting guides

Personal Types → Agent Memory:
- Meeting notes, personal TODO lists
- Individual project progress, working documents
- Custom configurations, personal preferences
```

### 3. Contextual Factors

#### Audience Analysis
- **Broad Audience (Global):** Content valuable to many users
- **Community Audience (Learned):** Content valuable to multiple agents
- **Individual Audience (Agent):** Content specific to one user

#### Temporal Characteristics
- **Timeless (Global):** Stable reference information
- **Evolving (Learned):** Growing knowledge and patterns
- **Current (Agent):** Immediate, time-sensitive information

## Suggestion Confidence Scoring

### High Confidence (90%+)
- Clear linguistic indicators present
- Content structure matches type pattern
- Context strongly supports classification
- No conflicting indicators found

### Medium Confidence (70-89%)
- Some strong indicators present
- Minor conflicting signals
- Structure generally supports classification
- Context is supportive but not definitive

### Low Confidence (<70%)
- Mixed or weak indicators
- Conflicting signals present
- Unclear content structure
- Ambiguous context

## AI Model Training Data

### Positive Examples by Type

#### Global Memory Examples
```
"The API authentication requires JWT tokens..."
"Company policy mandates that all code..."
"This technical specification defines..."
"Reference guide for system administrators..."
```

#### Learned Memory Examples  
```
"We discovered that this pattern works well..."
"Best practice for handling errors is to..."
"Experience shows that users prefer..."
"This approach solved similar problems..."
```

#### Agent Memory Examples
```
"My current project requires..."
"Personal reminder to check..."
"Working notes for today's task..."
"I prefer this configuration because..."
```

## Suggestion Enhancement Strategies

### 1. Context Integration
- **File Path Analysis:** Use directory structure as context
- **Related Content:** Consider similar content classifications
- **User History:** Learn from past user decisions
- **Metadata Context:** Use existing tags and categories

### 2. Multi-Signal Fusion
```python
def calculate_suggestion_confidence(content):
    linguistic_score = analyze_linguistic_indicators(content)
    structural_score = analyze_content_structure(content) 
    contextual_score = analyze_context(content)
    
    # Weighted combination
    confidence = (
        0.4 * linguistic_score + 
        0.3 * structural_score + 
        0.3 * contextual_score
    )
    
    return confidence, suggested_type
```

### 3. Continuous Learning
- **Feedback Loop:** Learn from user corrections
- **Pattern Recognition:** Identify new classification patterns
- **Performance Monitoring:** Track suggestion accuracy
- **Model Updates:** Regular retraining with new data

## Quality Assurance

### Validation Metrics
- **Accuracy:** Percentage of suggestions that users accept
- **Coverage:** Percentage of content that receives suggestions
- **Confidence Calibration:** How well confidence scores match accuracy
- **User Satisfaction:** Feedback on suggestion helpfulness

### Error Analysis
- **False Positives:** Incorrect suggestions with high confidence
- **False Negatives:** Missed opportunities for helpful suggestions
- **Edge Cases:** Content that doesn't fit standard patterns
- **Bias Detection:** Systematic errors in certain content types

## Implementation Guidelines

### Suggestion Presentation
```json
{
  "suggested_memory_type": "learned",
  "confidence": 0.87,
  "reasoning": [
    "Contains best practice language",
    "Describes solution pattern",
    "Has community knowledge indicators"
  ],
  "alternative_types": {
    "global": 0.23,
    "agent": 0.15
  }
}
```

### User Interaction
- **Clear Suggestions:** Present primary recommendation prominently
- **Explanation:** Provide reasoning for transparency
- **Easy Override:** Allow quick selection of alternative types
- **Feedback Collection:** Capture user corrections for learning

---
*AI-powered suggestions enhance efficiency while maintaining user control over memory type selection*"""

        return {
            "status": "success", 
            "prompt": {
                "name": "memory_type_suggestion_guidelines",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_final_checklist_prompt(self) -> Dict[str, Any]:
        """Pre-finalization policy compliance checklist."""
        content = """# Final Checklist - Policy Compliance

## Pre-Finalization Verification

### 1. Data Integrity Checks
- [ ] **Content Validation**
  - All stored content is accurate and complete
  - No corrupted or malformed data detected
  - Content metadata is properly populated
  - File references and links are valid

- [ ] **Deduplication Verification**
  - Duplicate content scan completed
  - Near-duplicates reviewed and resolved
  - Content consolidation performed where appropriate
  - Deduplication logs reviewed and approved

### 2. Memory Type Compliance
- [ ] **Global Memory Validation**
  - Only shared, authoritative content stored
  - All global content follows documentation standards
  - No personal or temporary information present
  - Content is accessible to all authorized agents

- [ ] **Learned Memory Validation**
  - Contains patterns, insights, and best practices
  - No raw data or personal information
  - Knowledge is properly abstracted and generalized
  - Content represents validated learning outcomes

- [ ] **Agent Memory Validation**  
  - Personal and task-specific content appropriately segregated
  - No sensitive information stored without encryption
  - Agent-specific content properly isolated
  - Temporary information tagged for cleanup

### 3. Access Control Verification
- [ ] **Permission Matrix Review**
  - Agent roles properly configured
  - Memory layer access rights validated
  - No unauthorized access permissions granted
  - Admin access properly restricted and logged

- [ ] **Security Compliance**
  - Sensitive data handling follows policy
  - Encryption applied where required
  - Access logs properly maintained
  - Authentication mechanisms validated

### 4. Quality Assurance
- [ ] **Content Quality Standards**
  - All content meets minimum quality thresholds
  - Metadata is comprehensive and accurate
  - Tagging is consistent and meaningful
  - Search functionality works as expected

- [ ] **System Performance**
  - Query response times within acceptable limits
  - Memory usage within operational parameters
  - No performance bottlenecks identified
  - System health metrics all green

### 5. Documentation and Audit Trail
- [ ] **Process Documentation**
  - All processing steps documented
  - Decision rationales recorded
  - Exception handling properly documented
  - Change history maintained

- [ ] **Compliance Evidence**
  - Policy adherence demonstrated
  - Audit trail complete and verifiable
  - Review checkpoints documented
  - Sign-off processes completed

## Policy Specific Checks

### Data Governance
- [ ] Data classification completed and accurate
- [ ] Retention policies properly applied
- [ ] Privacy requirements satisfied
- [ ] Regulatory compliance verified

### Operational Excellence
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery procedures validated
- [ ] Disaster recovery plans updated
- [ ] Performance baselines established

### Security Requirements
- [ ] Security controls implemented and tested
- [ ] Vulnerability assessments completed
- [ ] Incident response procedures updated
- [ ] Security training requirements met

## Final Approval Process

### Technical Review
- [ ] System architecture reviewed by technical lead
- [ ] Code quality standards met
- [ ] Security review completed
- [ ] Performance testing passed

### Business Review  
- [ ] Business requirements fully satisfied
- [ ] Stakeholder acceptance obtained
- [ ] User acceptance testing completed
- [ ] Training materials prepared

### Governance Review
- [ ] Policy compliance verified by governance team
- [ ] Risk assessment completed and approved
- [ ] Change management process followed
- [ ] Final approval from authorized signatory

## Post-Finalization Requirements

### Deployment Readiness
- [ ] Production environment prepared
- [ ] Deployment procedures tested
- [ ] Rollback procedures validated
- [ ] Support team notified and trained

### Ongoing Monitoring
- [ ] Monitoring dashboards configured
- [ ] Alerting thresholds set appropriately
- [ ] Regular review schedule established
- [ ] Continuous improvement process defined

## Checklist Completion

**Final Verification:**
- [ ] All checklist items completed
- [ ] No outstanding issues or exceptions
- [ ] Required approvals obtained
- [ ] System ready for production deployment

**Sign-off Required:**
- Technical Lead: _________________ Date: _______
- Security Officer: ________________ Date: _______
- Governance Lead: ________________ Date: _______
- Project Manager: ________________ Date: _______

---
*This checklist ensures comprehensive policy compliance before system finalization*"""

        return {
            "status": "success",
            "prompt": {
                "name": "final_checklist",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_policy_compliance_guide_prompt(self) -> Dict[str, Any]:
        """Comprehensive guide for following the policy rulebook."""
        content = """# Policy Compliance Guide

## Understanding the Policy Framework

### Policy Hierarchy
1. **Core Policies:** Fundamental rules that cannot be violated
2. **Operational Policies:** Guidelines for day-to-day operations  
3. **Best Practice Policies:** Recommended approaches and methods
4. **Context-Specific Policies:** Rules for specific situations or domains

### Policy Application Principles
- **Mandatory Compliance:** Core policies must always be followed
- **Justified Exceptions:** Operational policy exceptions require documentation
- **Continuous Improvement:** Best practices evolve based on experience
- **Context Awareness:** Apply appropriate policies for each situation

## Memory System Policy Compliance

### 1. Data Classification and Storage
```
Policy: Store data in appropriate memory types based on classification

Implementation:
✅ Global: Shared, authoritative, reference material
✅ Learned: Patterns, insights, validated knowledge
✅ Agent: Personal, task-specific, temporary information

Validation:
- Review content classification before storage
- Verify memory type selection rationale
- Document any exceptions or edge cases
```

### 2. Access Control and Permissions
```
Policy: Ensure appropriate access controls for each memory layer

Implementation:
✅ Role-based access control (RBAC) implemented
✅ Principle of least privilege applied
✅ Regular access review and validation
✅ Admin access properly restricted and logged

Validation:
- Audit agent permissions quarterly
- Review access logs for anomalies
- Test access controls regularly
- Document access decisions
```

### 3. Data Quality and Integrity
```
Policy: Maintain high data quality and prevent corruption

Implementation:
✅ Content validation before storage
✅ Deduplication processes active
✅ Metadata accuracy verification
✅ Regular integrity checks

Validation:
- Monitor data quality metrics
- Perform random content audits
- Validate search functionality
- Review error logs regularly
```

## Operational Compliance Procedures

### Daily Operations
1. **Morning Checklist**
   - [ ] System health check completed
   - [ ] Security alerts reviewed
   - [ ] Performance metrics within normal ranges
   - [ ] Backup status verified

2. **Content Processing**
   - [ ] Memory type selection follows policy guidelines
   - [ ] Deduplication checks performed
   - [ ] Quality validation completed
   - [ ] Metadata properly populated

3. **Evening Review**
   - [ ] Processing logs reviewed
   - [ ] Any exceptions documented
   - [ ] Performance issues addressed
   - [ ] Next-day priorities set

### Weekly Reviews
- **Policy Adherence Review:** Assess week's compliance
- **Exception Analysis:** Review and categorize policy exceptions
- **Performance Analysis:** Check system performance trends
- **Security Review:** Validate security controls and logs

### Monthly Audits
- **Comprehensive Compliance Audit:** Full policy adherence review
- **Access Rights Review:** Validate all agent permissions
- **Data Quality Assessment:** Comprehensive quality metrics review
- **Policy Update Review:** Assess need for policy updates

## Exception Handling

### When Exceptions Are Acceptable
- **Technical Limitations:** Current technology cannot support policy
- **Business Critical Need:** Immediate business need overrides policy
- **Temporary Workaround:** Short-term solution while permanent fix developed
- **Emergency Situation:** Policy compliance would prevent crisis response

### Exception Documentation Process
```
Exception Request:
1. Identify specific policy being violated
2. Provide detailed justification
3. Assess risk and impact
4. Define mitigation measures
5. Set review and expiration dates
6. Obtain required approvals
7. Document in exception register
```

### Exception Monitoring
- **Regular Review:** All exceptions reviewed monthly
- **Risk Assessment:** Ongoing risk evaluation for active exceptions
- **Remediation Tracking:** Progress toward policy compliance
- **Exception Closure:** Formal closure when compliance achieved

## Compliance Monitoring

### Key Performance Indicators (KPIs)
- **Policy Adherence Rate:** Percentage of operations in compliance
- **Exception Rate:** Number of active policy exceptions
- **Resolution Time:** Time to resolve compliance issues
- **Training Completion:** Staff policy training completion rate

### Monitoring Tools
- **Automated Checks:** System-automated compliance monitoring
- **Manual Audits:** Regular manual verification processes
- **User Reporting:** Mechanism for users to report compliance issues
- **Third-Party Assessment:** External compliance verification

## Training and Awareness

### Required Training
- **New User Orientation:** Policy overview for all new users
- **Role-Specific Training:** Specialized training for different roles
- **Annual Refresher:** Yearly policy update and refresher training
- **Exception Handling:** Training on proper exception procedures

### Awareness Programs
- **Policy Updates:** Communication of policy changes
- **Best Practice Sharing:** Sharing compliance success stories
- **Issue Awareness:** Communication about compliance challenges
- **Recognition Programs:** Acknowledging good compliance behavior

## Continuous Improvement

### Policy Evolution
- **Regular Review:** Policies reviewed annually or as needed
- **Stakeholder Input:** Feedback from users and stakeholders
- **Industry Changes:** Updates based on industry best practices
- **Lessons Learned:** Improvements based on compliance experience

### Implementation Improvement
- **Process Optimization:** Streamlining compliance procedures
- **Tool Enhancement:** Improving compliance monitoring tools
- **Training Enhancement:** Improving training effectiveness
- **Communication Improvement:** Better compliance communication

---
*Effective policy compliance requires understanding, commitment, and continuous attention to both letter and spirit of policies*"""

        return {
            "status": "success",
            "prompt": {
                "name": "policy_compliance_guide", 
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_policy_violation_recovery_prompt(self) -> Dict[str, Any]:
        """Recovery procedures when policy conflicts arise."""
        content = """# Policy Violation Recovery Procedures

## Immediate Response Protocol

### 1. Stop and Assess (STOP)
- **Halt Current Operations:** Immediately cease any activities that may worsen the violation
- **Secure the System:** Prevent further unauthorized access or data exposure
- **Document Initial State:** Capture current system state for analysis
- **Notify Stakeholders:** Alert relevant parties per escalation matrix

### 2. Identify and Classify (CLASSIFY)
```
Violation Severity Levels:

🔴 CRITICAL (Level 1):
- Security breach or data exposure
- System compromise or unauthorized access  
- Regulatory compliance violation
- Safety risk to personnel or systems

🟡 HIGH (Level 2): 
- Policy deviation with business impact
- Data quality or integrity issues
- Access control problems
- Performance degradation

🟢 MEDIUM (Level 3):
- Process deviation without immediate impact
- Documentation or reporting issues
- Minor configuration problems
- Training or awareness gaps
```

### 3. Immediate Containment (CONTAIN)
- **Isolate Affected Systems:** Limit scope of potential damage
- **Preserve Evidence:** Maintain logs and forensic information
- **Implement Temporary Controls:** Apply immediate protective measures
- **Communication Management:** Control information flow to prevent panic

## Recovery Procedures by Violation Type

### Security Violations

#### Unauthorized Access
```
Recovery Steps:
1. Disable compromised accounts immediately
2. Change all potentially affected passwords
3. Review access logs for full scope assessment
4. Implement additional authentication controls
5. Conduct security assessment of affected systems
6. Report to security team and management
```

#### Data Exposure
```
Recovery Steps:
1. Identify what data was exposed and to whom
2. Secure exposed data and prevent further access
3. Assess regulatory reporting requirements
4. Notify affected parties per legal requirements
5. Implement additional data protection measures
6. Conduct thorough security review
```

### Data Quality Violations

#### Content Corruption
```
Recovery Steps:
1. Identify extent of corrupted data
2. Restore from last known good backup
3. Validate restored data integrity
4. Analyze root cause of corruption
5. Implement preventive measures
6. Update data validation procedures
```

#### Classification Errors
```
Recovery Steps:
1. Identify misclassified content
2. Assess impact of misclassification
3. Reclassify content to appropriate memory types
4. Review and update classification procedures
5. Provide additional training if needed
6. Monitor for similar issues
```

### Access Control Violations

#### Permission Escalation
```
Recovery Steps:
1. Revoke inappropriate permissions immediately
2. Review all recent access grants
3. Audit affected accounts and resources
4. Implement principle of least privilege
5. Review permission granting procedures
6. Provide additional training to administrators
```

#### Role Boundary Violations
```
Recovery Steps:
1. Identify scope of boundary violations
2. Restore proper role boundaries
3. Review all role assignments
4. Update role definitions if necessary
5. Implement better role enforcement
6. Monitor for compliance going forward
```

## Investigation and Root Cause Analysis

### Evidence Collection
- **System Logs:** Collect all relevant system and application logs
- **User Actions:** Document all user actions leading to violation
- **Timeline Reconstruction:** Create detailed timeline of events
- **Impact Assessment:** Assess full scope and impact of violation

### Root Cause Categories
1. **Human Error:** Mistakes in judgment, process, or execution
2. **System Failure:** Technical system or infrastructure failure
3. **Process Gap:** Inadequate or unclear procedures
4. **Training Deficit:** Insufficient knowledge or awareness
5. **Design Flaw:** Fundamental issue with system design
6. **External Factor:** Outside influence or attack

### Analysis Framework
```
5 Why Analysis:
1. Why did the violation occur?
2. Why did the underlying cause exist?
3. Why was this cause not prevented?
4. Why were controls inadequate?
5. Why was the risk not identified?

Result: Root cause identification and corrective action plan
```

## Corrective Action Planning

### Short-term Actions (24-48 hours)
- **Immediate Fixes:** Address urgent safety and security issues
- **Temporary Controls:** Implement interim risk mitigation
- **Communication:** Stakeholder notification and updates
- **Monitoring:** Enhanced monitoring of affected systems

### Medium-term Actions (1-4 weeks)
- **Process Updates:** Revise procedures based on lessons learned
- **Training Programs:** Additional training for affected personnel
- **System Enhancements:** Implement technical improvements
- **Policy Updates:** Update policies if gaps identified

### Long-term Actions (1-6 months)
- **Systematic Improvements:** Address underlying systemic issues
- **Culture Change:** Address cultural or behavioral root causes
- **Technology Upgrades:** Implement long-term technical solutions
- **Program Enhancements:** Improve overall compliance programs

## Recovery Validation

### Verification Checklist
- [ ] **Root Cause Addressed:** Underlying issue resolved
- [ ] **Controls Effective:** New controls working as intended
- [ ] **Training Complete:** Relevant personnel trained
- [ ] **Monitoring Active:** Enhanced monitoring in place
- [ ] **Documentation Updated:** All procedures and policies updated
- [ ] **Stakeholders Informed:** All parties notified of resolution

### Success Metrics
- **No Recurrence:** Similar violations do not occur
- **Improved Detection:** Better ability to identify issues early
- **Faster Response:** Reduced time to detect and respond
- **Enhanced Controls:** Stronger preventive measures in place

## Prevention and Continuous Improvement

### Preventive Measures
- **Regular Training:** Ongoing policy and procedure training
- **System Monitoring:** Continuous monitoring for compliance
- **Regular Audits:** Periodic compliance assessments
- **Culture Building:** Promote compliance-focused culture

### Learning Integration
- **Lesson Documentation:** Capture lessons learned from incidents
- **Knowledge Sharing:** Share insights across teams
- **Process Improvement:** Continuously improve based on experience
- **Best Practice Development:** Develop best practices from recovery experience

## Recovery Team Structure

### Incident Commander
- **Role:** Overall coordination and decision making
- **Authority:** Full authority to direct recovery efforts
- **Accountability:** Responsible for successful resolution

### Technical Team
- **Role:** Technical analysis and system recovery
- **Expertise:** Deep technical knowledge of affected systems
- **Responsibility:** Implement technical recovery measures

### Communication Team
- **Role:** Stakeholder communication and coordination
- **Skills:** Communication and coordination expertise
- **Responsibility:** Manage all internal and external communication

### Legal/Compliance Team
- **Role:** Legal and regulatory compliance guidance
- **Expertise:** Legal and regulatory knowledge
- **Responsibility:** Ensure proper legal and regulatory response

---
*Effective policy violation recovery requires immediate action, thorough analysis, and systematic improvement to prevent recurrence*"""

        return {
            "status": "success",
            "prompt": {
                "name": "policy_violation_recovery",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }