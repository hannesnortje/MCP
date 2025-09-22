# Guidance Tools Content

This file contains the comprehensive guidance content for all memory management guidance tools. Each section corresponds to a specific guidance tool.

## Memory Usage Guidance

### Agent Memory Usage Patterns

#### Core Principles
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

#### Best Practices
##### Before Storing
- ✅ Verify content isn't already stored
- ✅ Choose appropriate memory type
- ✅ Add relevant metadata and tags
- ✅ Structure content for searchability

##### When Querying
- ✅ Start with specific terms
- ✅ Use memory type filters when appropriate
- ✅ Adjust similarity thresholds based on needs
- ✅ Review results for relevance

##### Maintenance
- ✅ Regular deduplication checks
- ✅ Update outdated information
- ✅ Clean up temporary or obsolete content
- ✅ Monitor memory usage metrics

#### Common Patterns
1. **Context Preservation:** Store conversation context before major transitions
2. **Progressive Learning:** Build on previous memories for better outcomes
3. **Collaborative Memory:** Share insights in global/learned layers appropriately
4. **Efficient Retrieval:** Use targeted queries with appropriate similarity thresholds

---
**This guidance helps you optimize your memory usage for better performance and organization.**

## Context Preservation Guidance

### Context Preservation Strategy

#### Why Context Preservation Matters
Maintaining context across sessions ensures continuity, reduces redundant work, and enables agents to build on previous interactions effectively.

#### Context Storage Strategies

##### 1. Session Checkpoints
- Store key decisions and outcomes at natural breakpoints
- Include reasoning behind important choices
- Tag with session identifiers for easy retrieval

##### 2. Progressive Context Building
- Start sessions by retrieving relevant previous context
- Layer new context on top of existing knowledge
- Update context summaries periodically

##### 3. Context Categorization
- **Immediate Context:** Current task and immediate decisions
- **Session Context:** Broader goals and multi-step processes
- **Historical Context:** Long-term patterns and learnings

#### Implementation Guidelines

##### Before Session End
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

##### Session Startup
1. **Query Previous Context**
   - Search for recent session summaries
   - Look for unfinished tasks
   - Retrieve relevant background information

2. **Rebuild Context**
   - Review what was being worked on
   - Understand current state
   - Identify next steps

#### Context Preservation Patterns

##### Task Continuity
```
Session End: "Completed API design for user auth. Next: implement JWT middleware"
Session Start: Query "user auth API JWT middleware" → Continue implementation
```

##### Decision History
```
Store: "Chose PostgreSQL over MongoDB because of ACID requirements for financial data"
Later: Reference when making related database decisions
```

##### Learning Accumulation
```
Pattern: Store insights about what works/doesn't work
Benefit: Avoid repeating mistakes, build on successful approaches
```

---
**This guidance ensures smooth continuity between work sessions and builds institutional knowledge over time.**

## Query Optimization Guidance

### Memory Query Optimization Best Practices

#### Query Strategy Fundamentals

##### 1. Specificity Over Breadth
- **Good:** "React component error handling patterns"
- **Poor:** "React help"
- **Better:** "React useEffect cleanup memory leaks"

##### 2. Context-Aware Queries
- Include relevant technical terms
- Reference specific frameworks/technologies
- Add domain context when applicable

##### 3. Memory Type Targeting
```
Global: Documentation, standards, shared knowledge
Learned: Patterns, insights, lessons learned  
Agent: Personal notes, task-specific context
```

#### Advanced Query Techniques

##### Similarity Threshold Guidelines
- **0.9-1.0:** Exact matches, specific lookups
- **0.8-0.9:** Related content, similar contexts
- **0.7-0.8:** Broader exploration, discovery
- **0.6-0.7:** Very broad, experimental searches

##### Query Enhancement Strategies

###### Layer Progressive Queries
1. Start specific, broaden if needed
2. Try different keyword combinations
3. Adjust similarity thresholds
4. Filter by memory type if too broad

###### Keyword Optimization
- **Technical terms:** Use exact technology names
- **Action words:** "implement", "debug", "optimize"  
- **Context markers:** "error", "solution", "pattern"
- **Domain terms:** Business/project specific language

#### Performance Optimization

##### Query Construction
✅ **Effective Queries:**
- "Django REST API authentication middleware implementation"
- "Python asyncio exception handling best practices"
- "React state management Redux vs Context performance"

❌ **Ineffective Queries:**
- "help"
- "code"
- "how to"

##### Memory Type Selection
- **Broad exploration:** Don't specify memory type
- **Specific context:** Filter by appropriate memory type
- **Performance critical:** Use most specific type possible

##### Result Processing
1. **Review Relevance:** Check if results match intent
2. **Adjust Strategy:** Modify query if results aren't useful
3. **Combine Results:** Synthesize information from multiple queries
4. **Cache Insights:** Store useful query patterns

#### Common Query Patterns

##### Problem-Solution Queries
```
"[Technology] [Specific Problem] [Context]"
Example: "Next.js hydration error React components"
```

##### Pattern Discovery
```
"[Domain] [Type] patterns best practices"
Example: "microservices communication patterns reliability"
```

##### Historical Context
```
"[Project/Feature] decisions reasoning background"
Example: "user authentication JWT implementation decisions"
```

---
**This guidance helps you craft more effective queries that return relevant, actionable results quickly.**

## Markdown Optimization Guidance

### Markdown Optimization Rules

#### Content Processing Guidelines

##### 1. Structure Preservation
- ✅ Maintain heading hierarchy for navigation
- ✅ Preserve code blocks with language specifications
- ✅ Keep table structures intact
- ✅ Retain link references and relationships

##### 2. Metadata Extraction
- **Headers:** Extract as navigation markers
- **Tags:** Identify from content and frontmatter  
- **Categories:** Infer from structure and content
- **Relationships:** Track internal and external links

##### 3. Content Optimization
```markdown
Before: ## Some Random Heading
After: ## API Authentication Methods

Before: Code without context
After: ```javascript
// JWT token validation middleware
```

##### 4. Memory Type Selection
- **Global:** Documentation, specifications, references
- **Learned:** Patterns, examples, best practices extracted from docs
- **Agent:** Personal notes, customizations, task-specific content

#### Processing Best Practices

##### Pre-Processing
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

##### Content Chunking Strategy
- **Header-Based:** Split at major headings (H1, H2)
- **Size-Based:** Target 900 tokens with 200 overlap
- **Context-Aware:** Keep related content together
- **Code-Preserving:** Don't split code blocks

##### Tag Generation
- **From Headings:** Extract key terms from section titles
- **From Content:** Identify technical terms and concepts
- **From Context:** Add domain and category tags
- **From Structure:** Include document type tags

#### Quality Assurance

##### Content Validation
- [ ] Markdown syntax is valid and renders correctly
- [ ] Code blocks have proper language annotations
- [ ] Links are functional or marked as internal references
- [ ] Tables are properly formatted
- [ ] Images have alt text and valid paths

##### Processing Validation
- [ ] Content chunked at appropriate boundaries
- [ ] Metadata accurately extracted
- [ ] Tags are relevant and useful
- [ ] Memory type suggestion is appropriate
- [ ] Deduplication check completed

#### Markdown Processing Checklist
- [ ] Source content validated and cleaned
- [ ] Structure preserved during processing
- [ ] Metadata extracted comprehensively
- [ ] Appropriate chunking strategy applied
- [ ] Tags generated from multiple sources
- [ ] Memory type suggested based on content
- [ ] Quality validation completed

---
**Proper markdown processing ensures maximum searchability and utility.**

## Duplicate Detection Guidance

### Duplicate Detection Strategy

#### Detection Methods

##### 1. Cosine Similarity Analysis
- **High Similarity (0.95+):** Likely exact duplicates
- **Medium Similarity (0.85-0.95):** Near-duplicates requiring review
- **Lower Similarity (0.80-0.85):** Potentially related content

##### 2. Content Hash Comparison
- **Exact Matches:** Identical content with different metadata
- **Normalized Matches:** Same content after whitespace/formatting normalization
- **Partial Matches:** Significant content overlap

##### 3. Metadata-Based Detection
- **Same Source File:** Multiple ingestions of same document
- **Similar Titles:** Documents with nearly identical titles
- **Timestamp Clustering:** Multiple entries from same processing batch

#### Deduplication Workflow

##### 1. Pre-Storage Validation
```
1. Calculate content hash
2. Check for exact hash matches
3. Run similarity search (threshold: 0.85)
4. Flag potential duplicates for review
5. Prompt for human decision if ambiguous
```

##### 2. Post-Storage Analysis
```
1. Periodic similarity scans across memory types
2. Identify clusters of related content
3. Review near-duplicates (0.85-0.95 range)
4. Merge or consolidate where appropriate
```

##### 3. Handling Strategies

###### For Exact Duplicates (0.95+)
- **Action:** Skip storage or replace existing
- **Preserve:** Most recent or most complete version
- **Log:** Deduplication event for audit trail

###### For Near-Duplicates (0.85-0.95)
- **Action:** Flag for human review
- **Options:** Merge, keep both, or choose one
- **Consider:** Different perspectives or contexts

###### For Related Content (0.80-0.85)
- **Action:** Log relationship but keep both
- **Enhancement:** Add cross-references
- **Monitor:** For future consolidation opportunities

#### Advanced Strategies

##### Content Versioning
- Track content evolution over time
- Maintain version history for important documents
- Allow rollback to previous versions when needed

##### Semantic Deduplication
- Focus on meaning rather than exact text matches
- Use embedding similarity for semantic comparison
- Consider context and intent, not just words

##### Batch Processing Optimization
- Process similar documents together for better comparison
- Use clustering to identify potential duplicate groups
- Implement progressive deduplication during ingestion

---
**Effective duplicate detection maintains clean, organized memory while preserving unique insights.**

## Directory Processing Guidance

### Directory Processing Best Practices

#### Planning Phase

##### 1. Directory Assessment
- **Size Analysis:** Count files and estimate processing time
- **File Type Distribution:** Identify markdown vs. other files
- **Structure Analysis:** Understand directory organization
- **Priority Assessment:** Identify high-value directories first

##### 2. Processing Strategy
- **Batch Size:** Optimal number of files per batch (recommended: 10-50)
- **Parallel Processing:** Balance speed vs. resource usage
- **Error Handling:** Strategy for failed file processing
- **Progress Tracking:** Monitor completion and identify bottlenecks

#### Execution Best Practices

##### 1. Pre-Processing Validation
```
Directory Checklist:
- [ ] Directory exists and is accessible
- [ ] Sufficient disk space for processing
- [ ] Network connectivity to vector database
- [ ] Required permissions for file access
- [ ] Backup strategy in place
```

##### 2. File Processing Order
- **Prioritize by importance:** Documentation before examples
- **Size considerations:** Large files processed during low-usage times
- **Dependency handling:** Process referenced files first when possible
- **Update detection:** Skip unchanged files when appropriate

##### 3. Error Recovery
- **Graceful Degradation:** Continue processing other files on individual failures
- **Retry Logic:** Attempt failed files with exponential backoff
- **Error Logging:** Detailed logging for post-processing analysis
- **Manual Review:** Queue problematic files for human intervention

#### Memory Management

##### 1. Content Distribution
- **Global Memory:** Shared documentation and standards
- **Learned Memory:** Extracted patterns and best practices
- **Agent Memory:** Processing logs and personal notes

##### 2. Metadata Preservation
- **File Paths:** Maintain directory structure in metadata
- **Processing Time:** Track when content was processed
- **Source Information:** Link back to original files
- **Batch Information:** Group related processed files

#### Performance Optimization

##### 1. Resource Management
```python
# Recommended settings for directory processing
batch_size = 25  # Files per batch
max_workers = 4  # Parallel processing threads  
chunk_size = 900  # Tokens per chunk
chunk_overlap = 200  # Token overlap
similarity_threshold = 0.85  # Duplicate detection
```

##### 2. Progress Monitoring
- **File-level progress:** Track individual file completion
- **Batch-level progress:** Monitor batch completion rates
- **Overall progress:** Directory completion percentage
- **Performance metrics:** Files per minute, errors per batch

##### 3. Quality Assurance
- **Content validation:** Verify processed content matches source
- **Metadata accuracy:** Ensure file paths and timestamps are correct
- **Deduplication:** Check for and handle duplicate content
- **Search testing:** Validate that processed content is searchable

#### Directory Structure Handling

##### Hierarchical Organization
- Preserve folder structure in metadata tags
- Use path segments as automatic tag categories
- Maintain parent-child relationships in content

##### Bulk Operations
- Process related files in logical groups
- Maintain consistency across similar documents
- Apply consistent tagging and categorization

---
**Systematic directory processing ensures comprehensive, organized knowledge capture.**

## Memory Type Selection Guidance

### Memory Type Selection Criteria

#### Memory Type Overview

##### Global Memory
**Purpose:** Shared knowledge accessible to all agents
**Best For:**
- Documentation and specifications
- Reference materials and guides
- Shared standards and policies
- Common knowledge and facts

##### Learned Memory  
**Purpose:** Accumulated insights and patterns
**Best For:**
- Best practices and methodologies
- Patterns and solutions that worked
- Lessons learned from experience
- Consolidated knowledge from multiple sources

##### Agent Memory
**Purpose:** Personal, agent-specific context
**Best For:**
- Individual agent's working context
- Task-specific temporary information
- Personal preferences and configurations
- Session-specific data

#### Selection Decision Tree

##### Ask: "Who needs this information?"
- **Everyone:** → Global Memory
- **Future agents learning:** → Learned Memory
- **Just this agent:** → Agent Memory

##### Ask: "How long should this persist?"
- **Permanently:** → Global or Learned Memory
- **This session only:** → Agent Memory
- **Until task complete:** → Agent Memory

##### Ask: "What type of content is this?"
- **Documentation/Reference:** → Global Memory
- **Insights/Patterns:** → Learned Memory
- **Working notes:** → Agent Memory

#### Content Examples by Type

##### Global Memory Examples
```
✅ API documentation
✅ Company policies
✅ Technical specifications
✅ Shared procedures
✅ Reference materials
```

##### Learned Memory Examples
```
✅ "React hooks patterns that work well"
✅ "Common database optimization techniques"
✅ "Debugging strategies for async issues"
✅ "Effective code review practices"
```

##### Agent Memory Examples
```
✅ "Current task: implementing user auth"
✅ "Next: add JWT validation middleware"
✅ "Personal preference: using TypeScript strict mode"
✅ "Session context: working on payment system"
```

---
**Choose memory types based on audience, persistence, and content nature.**

## Memory Type Suggestion Guidance

### Memory Type Suggestion Guidelines

#### AI-Powered Memory Type Detection

##### Content Analysis Factors
1. **Scope Indicators**
   - Personal pronouns (I, my, this session) → Agent
   - Universal language (all, everyone, standard) → Global
   - Learning language (discovered, found, pattern) → Learned

2. **Temporal Indicators**
   - "Currently working on" → Agent
   - "Always remember" → Global
   - "Learned that" → Learned

3. **Content Type Patterns**
   - Documentation format → Global
   - Insight/pattern format → Learned
   - Task/context format → Agent

#### Suggestion Algorithm

##### Step 1: Content Classification
```python
def classify_content(text):
    # Check for documentation patterns
    if has_structured_docs(text):
        return "global"
    
    # Check for learning/insight patterns
    if has_insight_language(text):
        return "learned"
    
    # Check for task/session patterns
    if has_task_language(text):
        return "agent"
    
    # Default fallback
    return suggest_based_on_context()
```

##### Step 2: Confidence Scoring
- **High confidence (0.8+):** Auto-suggest with explanation
- **Medium confidence (0.6-0.8):** Suggest with alternatives
- **Low confidence (<0.6):** Present options with guidance

##### Step 3: Context Consideration
- Current agent activity
- Recent memory usage patterns
- Content similarity to existing memories
- User preferences and overrides

#### Suggestion Patterns

##### Global Memory Indicators
```
✅ "This is the official API documentation"
✅ "Company policy states that..."
✅ "Standard procedure for..."
✅ "Reference guide for..."
```

##### Learned Memory Indicators
```
✅ "I've found that this pattern works well..."
✅ "Best practice discovered..."
✅ "This approach typically results in..."
✅ "Pattern observed across multiple projects..."
```

##### Agent Memory Indicators
```
✅ "Currently working on implementing..."
✅ "Next step in this task..."
✅ "My preference for this project..."
✅ "Session context: debugging issue with..."
```

#### Implementation Guidelines

##### For Tool Integration
1. **Analyze content semantically**
2. **Consider context clues**
3. **Provide confidence scores**
4. **Allow user overrides**
5. **Learn from corrections**

##### For User Experience
1. **Show suggestion reasoning**
2. **Provide alternative options**
3. **Allow quick acceptance**
4. **Remember user preferences**
5. **Improve over time**

---
**AI-powered suggestions should be helpful, transparent, and continuously improving.**

## Policy Compliance Guidance

### Policy Compliance Guide

#### Understanding Policy Framework

##### Policy Structure
- **Principles:** Core values and guidelines
- **Forbidden Actions:** Absolute restrictions
- **Required Sections:** Mandatory content elements
- **Style Guide:** Formatting and presentation standards

##### Compliance Levels
1. **Critical:** Must never be violated (security, safety)
2. **Important:** Should be followed with rare exceptions
3. **Recommended:** Best practices that improve quality
4. **Stylistic:** Consistency and presentation guidelines

#### Compliance Workflow

##### Pre-Action Check
1. **Review relevant policies**
   - Identify applicable policy sections
   - Check for recent policy updates
   - Understand exception criteria

2. **Assess compliance impact**
   - Will this action violate any policies?
   - Are there compliance alternatives?
   - What are the risk levels?

3. **Document compliance reasoning**
   - Why is this action compliant?
   - What policies were considered?
   - Are there any edge cases?

##### During Action
1. **Monitor for policy conflicts**
2. **Adjust approach if needed**
3. **Document decisions made**

##### Post-Action Review
1. **Verify compliance was maintained**
2. **Log any policy questions that arose**
3. **Update procedures if needed**

#### Common Compliance Scenarios

##### Content Creation
- ✅ Include required sections
- ✅ Follow style guidelines
- ✅ Respect content restrictions
- ✅ Maintain quality standards

##### Decision Making
- ✅ Consider policy implications
- ✅ Document reasoning
- ✅ Seek guidance when uncertain
- ✅ Prioritize safety and security

##### Collaboration
- ✅ Share policy-compliant information
- ✅ Respect confidentiality rules
- ✅ Follow communication standards
- ✅ Maintain professional boundaries

#### Policy Violation Prevention

##### Early Warning Signs
- Uncertainty about policy application
- Pressure to bypass normal procedures
- Novel situations without clear precedent
- Conflicting policy requirements

##### Mitigation Strategies
- ✅ When in doubt, ask for guidance
- ✅ Document all policy-related decisions
- ✅ Regular policy training and updates
- ✅ Create clear escalation procedures

---
**Proactive compliance prevents violations and maintains organizational integrity.**

## Policy Violation Recovery Guidance

### Policy Violation Recovery

#### Immediate Response Protocol

##### Step 1: Stop and Assess
1. **Halt the violating action immediately**
2. **Identify the specific policy violated**
3. **Assess the scope and impact**
4. **Determine if harm has occurred**

##### Step 2: Document Everything
1. **What policy was violated?**
2. **When did the violation occur?**
3. **What was the intended action?**
4. **What actually happened?**
5. **What was the impact?**

##### Step 3: Immediate Containment
1. **Prevent further violations**
2. **Secure any compromised systems**
3. **Notify affected parties if needed**
4. **Preserve evidence for investigation**

#### Recovery Process

##### Severity Assessment
**Critical Violations:**
- Security breaches
- Safety incidents
- Data protection violations
- Legal/regulatory violations

**Major Violations:**
- Process bypasses
- Quality standard violations
- Communication policy breaches

**Minor Violations:**
- Style guide deviations
- Documentation omissions
- Procedural oversights

##### Recovery Actions by Severity

###### Critical Violations
1. **Immediate escalation to leadership**
2. **Full incident investigation**
3. **External notifications if required**
4. **Complete remediation plan**
5. **Policy updates if needed**

###### Major Violations
1. **Supervisor notification**
2. **Impact assessment**
3. **Correction of immediate issues**
4. **Process review and improvement**

###### Minor Violations
1. **Self-correction**
2. **Documentation update**
3. **Learning reinforcement**
4. **Prevention measures**

#### Learning and Prevention

##### Post-Violation Analysis
1. **Why did the violation occur?**
   - Knowledge gap?
   - Process failure?
   - System limitation?
   - Time pressure?

2. **How can we prevent recurrence?**
   - Additional training?
   - Process improvements?
   - System changes?
   - Policy clarification?

##### Improvement Actions
- ✅ Update relevant procedures
- ✅ Enhance training materials
- ✅ Improve system safeguards
- ✅ Clarify policy language
- ✅ Share lessons learned

#### Recovery Communication

##### Internal Communication
- **What:** Clear, factual description
- **When:** Timely reporting
- **Why:** Context and contributing factors
- **How:** Corrective actions taken
- **Prevention:** Future prevention measures

##### External Communication (if required)
- **Follow legal/regulatory requirements**
- **Coordinate with legal/compliance teams**
- **Maintain transparency while protecting interests**
- **Document all communications**

---
**Effective recovery turns violations into learning opportunities and stronger compliance.**