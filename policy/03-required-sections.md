# Required Sections

This document defines mandatory sections and data structures that must be present in various system components.

## Memory Entry Requirements

### Global Memory Entries
- [R-201] All global memory entries must include content, category, and importance metadata
- [R-202] Global memory timestamps must be in ISO 8601 format for consistency
- [R-203] Vector embeddings must be present and valid for all memory entries

### Learned Memory Entries
- [R-204] Learned memory entries must specify pattern_type and confidence level
- [R-205] Learning context must be documented for pattern traceability
- [R-206] Confidence scores must be between 0.0 and 1.0 inclusive

### Agent Memory Entries
- [R-207] Agent-specific memories must include agent_id and memory_type classification
- [R-208] Agent memory must respect isolation requirements between different agents
- [R-209] Agent context information must be preserved with memory entries

## System Documentation Requirements

### API Response Format
- [R-210] All tool responses must include success/error status indicators
- [R-211] Error messages must be descriptive and actionable for troubleshooting
- [R-212] Timestamp information must be included in all system responses

### Configuration Schema
- [R-213] System configuration must specify all required Qdrant connection parameters
- [R-214] Embedding model configuration must be explicitly defined
- [R-215] Memory layer permissions must be clearly documented and enforced

## Policy Compliance Requirements

### Rule Documentation
- [R-216] All policy rules must follow the [RULE-ID] format with unique identifiers
- [R-217] Policy documents must be organized by section headers for clarity
- [R-218] Rule severity levels must be assigned based on impact assessment

### Validation Requirements
- [R-219] JSON schema validation must enforce required sections in all submissions
- [R-220] Policy version hashes must be SHA-256 for integrity verification
- [R-221] Agent startup must validate policy binding before operation authorization