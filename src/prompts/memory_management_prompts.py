"""
Memory management prompt handlers for MCP Memory Server.
Handles memory usage patterns, optimization, querying, and content management.
"""

from datetime import datetime
from typing import Dict, Any

try:
    from ..server_config import get_logger
except ImportError:
    import logging

    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger("memory-management-prompts")


class MemoryManagementPrompts:
    """Handles memory management and optimization guidance prompts."""

    def __init__(self):
        """Initialize memory management prompts handler."""
        pass

    def get_prompt_definitions(self) -> list[dict]:
        """Get definitions for memory management prompts."""
        return [
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
            }
        ]

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a memory management prompt by name."""
        method_map = {
            "agent_memory_usage_patterns": 
                self._get_agent_memory_usage_patterns_prompt,
            "context_preservation_strategy": 
                self._get_context_preservation_strategy_prompt,
            "memory_query_optimization": 
                self._get_memory_query_optimization_prompt,
            "markdown_optimization_rules": 
                self._get_markdown_optimization_rules_prompt,
            "memory_type_selection_criteria": 
                self._get_memory_type_selection_criteria_prompt,
            "duplicate_detection_strategy": 
                self._get_duplicate_detection_strategy_prompt,
            "directory_processing_best_practices": 
                self._get_directory_processing_best_practices_prompt,
            "memory_type_suggestion_guidelines": 
                self._get_memory_type_suggestion_guidelines_prompt
        }

        if name in method_map:
            return method_map[name]()
        else:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown memory management prompt: {name}"
                    }
                ]
            }

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
        content = """# Memory Query Optimization Best Practices

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
- **Normalized Matches:** Same content after whitespace/formatting
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
3. Flag high-similarity pairs for review
4. Batch process deduplication decisions
```

## Handling Strategies

### Exact Duplicates (Hash Match)
- **Action:** Skip storage, reference existing
- **Logging:** Note duplicate attempt with source info
- **Metadata:** Update access patterns and frequency

### Near Duplicates (High Similarity)
- **Review Required:** Human decision on merge vs keep
- **Context Analysis:** Check for meaningful differences
- **Metadata Merge:** Combine tags and references if merging

### Related Content (Medium Similarity)
- **Cross-Reference:** Link related entries
- **Tag Enhancement:** Add shared tags for discoverability
- **Keep Separate:** Maintain distinct entries

## Automation Guidelines

### Auto-Skip Criteria
- Exact hash match from same source
- Similarity > 0.98 with minimal metadata differences
- Known temporary or cache files

### Auto-Merge Criteria
- Same title and author with minor formatting differences
- Version updates of same document
- Duplicate imports from same processing run

### Human Review Required
- Similarity 0.85-0.98 with different sources
- Conflicting metadata or tags
- Uncertain content relationships

## Quality Metrics

### Detection Accuracy
- **True Positives:** Correctly identified duplicates
- **False Positives:** Non-duplicates flagged as duplicates
- **False Negatives:** Missed actual duplicates

### Processing Efficiency
- **Time per Detection:** Processing speed metrics
- **Batch Processing:** Bulk duplicate detection
- **Resource Usage:** Memory and computation costs

## Deduplication Checklist
- [ ] Content hash calculated and checked
- [ ] Similarity analysis completed
- [ ] Metadata comparison performed
- [ ] Human review triggered if needed
- [ ] Decision logged with reasoning
- [ ] Related content properly linked

---
*Effective duplicate detection maintains content quality and system efficiency*"""

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

### 1. Directory Analysis
- **Size Assessment:** Count files and estimate processing time
- **Content Types:** Identify file formats and processing needs
- **Structure Review:** Understand hierarchy and organization
- **Dependency Mapping:** Note file relationships and references

### 2. Processing Strategy
- **Batch Size:** Optimize for memory and performance
- **Priority Order:** Process critical files first
- **Error Handling:** Plan for failures and recovery
- **Progress Tracking:** Monitor and report processing status

## Execution Guidelines

### Pre-Processing
1. **Validation Checks**
   - Verify directory accessibility
   - Check available disk space
   - Validate file permissions
   - Estimate processing requirements

2. **Preparation Steps**
   - Create processing logs
   - Set up progress tracking
   - Initialize error handling
   - Configure parallel processing

### During Processing
1. **File-by-File Processing**
   - Read and validate each file
   - Apply content optimization
   - Run duplicate detection
   - Store with appropriate metadata

2. **Progress Management**
   - Update progress indicators
   - Log processing decisions
   - Handle errors gracefully
   - Maintain processing statistics

### Post-Processing
1. **Quality Assurance**
   - Verify all files processed
   - Check for processing errors
   - Validate storage integrity
   - Review duplicate detection results

2. **Cleanup and Reporting**
   - Archive processing logs
   - Generate summary reports
   - Clean up temporary files
   - Document any issues

## Performance Optimization

### Parallel Processing
- **File-Level Parallelism:** Process multiple files simultaneously
- **Pipeline Processing:** Overlap I/O and computation
- **Resource Management:** Balance CPU, memory, and I/O usage

### Memory Management
- **Streaming Processing:** Handle large files in chunks
- **Garbage Collection:** Clean up processed content
- **Cache Strategy:** Reuse common processing results

### I/O Optimization
- **Batch Operations:** Group database operations
- **Efficient Scanning:** Use optimized directory traversal
- **Caching:** Cache frequently accessed metadata

## Error Handling

### Common Issues
- **File Access Errors:** Permissions, locks, missing files
- **Content Errors:** Malformed, corrupted, or unreadable content
- **Processing Errors:** Memory limits, timeout, system failures
- **Storage Errors:** Database connectivity, capacity limits

### Recovery Strategies
- **Retry Logic:** Automatic retry with exponential backoff
- **Skip and Continue:** Log errors and process remaining files
- **Partial Recovery:** Resume from last successful checkpoint
- **Manual Intervention:** Flag for human review and resolution

## Quality Assurance

### Validation Checks
- [ ] All expected files processed successfully
- [ ] Content integrity maintained during processing
- [ ] Metadata accurately extracted and stored
- [ ] Duplicate detection completed appropriately
- [ ] Error handling functioned as expected

### Performance Metrics
- [ ] Processing time within expected ranges
- [ ] Memory usage remained within limits
- [ ] Error rates below acceptable thresholds
- [ ] Storage efficiency optimized

## Directory Processing Checklist
- [ ] Directory structure analyzed and understood
- [ ] Processing strategy planned and configured
- [ ] Pre-processing validation completed
- [ ] Parallel processing optimized for system
- [ ] Error handling and recovery tested
- [ ] Progress tracking and reporting enabled
- [ ] Post-processing quality assurance planned

---
*Systematic directory processing ensures consistent, reliable content ingestion*"""

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

## AI-Powered Analysis Framework

### Content Classification Indicators

#### Global Memory Indicators
- **Keywords:** "documentation", "specification", "standard", "reference"
- **Structure:** Formal headings, comprehensive coverage, authoritative tone
- **Audience:** Language suggesting broad applicability ("all", "everyone")
- **Examples:** API docs, policies, technical specifications

#### Learned Memory Indicators
- **Keywords:** "pattern", "best practice", "lesson", "experience", "insight"
- **Structure:** Problem-solution format, comparative analysis
- **Audience:** Professional/team context ("we found", "teams discovered")
- **Examples:** Architecture decisions, debugging guides, methodology docs

#### Agent Memory Indicators
- **Keywords:** "my", "current", "working on", "personal", "task"
- **Structure:** Informal notes, task lists, temporary information
- **Audience:** First person or specific individual context
- **Examples:** Task notes, personal preferences, session context

### Confidence Scoring

#### High Confidence (90-100%)
- **Clear Indicators:** Multiple strong signals point to one type
- **Consistent Context:** All analysis dimensions agree
- **Unambiguous Content:** Purpose and audience clearly defined
- **Action:** Auto-suggest with high confidence

#### Medium Confidence (70-89%)
- **Mixed Signals:** Some indicators for multiple types
- **Context Ambiguity:** Purpose somewhat unclear
- **Partial Indicators:** Incomplete information for classification
- **Action:** Suggest with explanation and alternatives

#### Low Confidence (50-69%)
- **Weak Signals:** Few or contradictory indicators
- **Unclear Context:** Purpose and audience not evident
- **Insufficient Information:** Limited content for analysis
- **Action:** Present options with user guidance

### Analysis Methodology

#### Step 1: Content Analysis
```python
def analyze_content(content, file_path=None):
    indicators = {
        'global': count_global_indicators(content),
        'learned': count_learned_indicators(content), 
        'agent': count_agent_indicators(content)
    }
    return indicators
```

#### Step 2: Context Analysis
```python
def analyze_context(file_path, metadata):
    path_signals = extract_path_signals(file_path)
    meta_signals = extract_metadata_signals(metadata)
    return combine_signals(path_signals, meta_signals)
```

#### Step 3: Confidence Calculation
```python
def calculate_confidence(content_indicators, context_indicators):
    max_score = max(content_indicators.values())
    score_difference = calculate_separation(content_indicators)
    context_support = check_context_alignment(indicators, context)
    return compute_confidence(max_score, score_difference, context_support)
```

## Implementation Guidelines

### AI Integration Points
1. **Pre-Processing Analysis**
   - Analyze content before storage decisions
   - Extract semantic features and keywords
   - Identify document structure and patterns

2. **Real-Time Suggestions**  
   - Provide suggestions during content ingestion
   - Update suggestions based on user feedback
   - Learn from user corrections and preferences

3. **Batch Analysis**
   - Analyze large content collections
   - Identify patterns across document sets
   - Suggest bulk categorization strategies

### User Experience Design
1. **Suggestion Presentation**
   - Show primary suggestion with confidence level
   - Provide reasoning for suggestion
   - Offer alternative options when confidence is low

2. **Feedback Integration**
   - Allow users to accept, modify, or reject suggestions
   - Learn from user decisions to improve future suggestions
   - Track suggestion accuracy and user satisfaction

3. **Override Capabilities**
   - Always allow manual memory type selection
   - Explain implications of overriding AI suggestions
   - Learn from override patterns to improve analysis

## Quality Metrics

### Suggestion Accuracy
- **Acceptance Rate:** Percentage of suggestions accepted by users
- **Override Analysis:** Patterns in user overrides
- **Correction Learning:** Improvement from user feedback

### System Performance
- **Processing Speed:** Time to generate suggestions
- **Resource Usage:** Computational requirements
- **Scalability:** Performance with large content volumes

### User Satisfaction
- **Suggestion Relevance:** Quality of suggestions from user perspective
- **Decision Confidence:** User confidence in AI-assisted decisions
- **Workflow Integration:** Seamless integration with user workflows

## Continuous Improvement

### Learning Mechanisms
1. **User Feedback Integration**
   - Track suggestion acceptance/rejection patterns
   - Analyze user override reasoning
   - Update models based on user preferences

2. **Pattern Recognition**
   - Identify new content patterns over time
   - Adapt to changing content types and structures
   - Evolve classification criteria based on usage

3. **Performance Monitoring**
   - Monitor suggestion accuracy metrics
   - Track user satisfaction indicators
   - Adjust confidence thresholds based on outcomes

## AI Suggestion Guidelines Checklist
- [ ] Content analysis indicators clearly defined
- [ ] Confidence scoring methodology implemented
- [ ] User experience optimized for suggestion workflow
- [ ] Feedback mechanisms integrated for learning
- [ ] Quality metrics tracked and monitored
- [ ] Continuous improvement processes established

---
*AI-powered suggestions enhance user productivity while maintaining accuracy*"""

        return {
            "status": "success",
            "prompt": {
                "name": "memory_type_suggestion_guidelines",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }