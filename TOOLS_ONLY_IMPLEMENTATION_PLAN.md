# Tools-Only Server Implementation Plan

## Overview

This document outlines the step-by-step implementation plan for creating a tools-only MCP server variant that preserves all prompt functionality through enhanced tools.

## Current State Analysis

### Existing Architecture
- **13 Prompts** (including main `agent_startup` prompt)
- **23+ Tools** (memory management, markdown processing, agent management, policy handling)
- **Resources** (memory data access)

### Key Finding
The documented `--prompts-only` mode doesn't actually exist in the implementation.

## Implementation Strategy: Option 3 (Hybrid Approach)

### Enhanced Functional Tools
- Merge `agent_startup` functionality into enhanced `initialize_new_agent`
- Keep single-step agent setup with policy loading

### New Documentation/Guidance Tools
- Convert all 10 guidance prompts to equivalent tools
- Return same content but as tool responses
- Allow filtering by section/topic

## Phase 1: Server Mode Infrastructure (Foundation)

### Step 1.1: Add Command-Line Argument Support
**File:** `memory_server.py`
- Add argparse for `--tools-only`, `--prompts-only`, `--full`
- Add environment variable support (`TOOLS_ONLY=1`, etc.)
- Pass server mode to MCP server instance

### Step 1.2: Modify MCP Server Class
**File:** `src/mcp_server.py`
- Add `server_mode` parameter to `MemoryMCPServer.__init__()`
- Conditionally initialize prompt handlers based on mode
- Update MCP capabilities response to exclude prompts in tools-only mode

### Step 1.3: Update Protocol Handlers
**File:** `src/mcp_server.py`
- Make `prompts/list` and `prompts/get` return empty/error in tools-only mode
- Ensure tools and resources work in all modes

## Phase 2: Enhanced Core Functionality (Merge agent_startup into tools)

### Step 2.1: Enhance `initialize_new_agent` Tool
**File:** `src/tool_handlers.py`
- Merge agent_startup prompt logic into existing tool
- Add parameters: `policy_version`, `policy_hash`, `load_policies`
- Return same detailed initialization report as agent_startup prompt
- Include automatic policy loading when `load_policies=true`

### Step 2.2: Add Agent Startup Preset Tools
**File:** `src/tool_handlers.py`
- Add `initialize_development_agent` tool (developer defaults)
- Add `initialize_testing_agent` tool (testing defaults)
- These call enhanced `initialize_new_agent` with preset parameters

## Phase 3: Guidance Tools Implementation (Replace guidance prompts)

### Step 3.1: Create Guidance Tool Handler Class
**File:** `src/guidance_tools.py` (new file)
- Create `GuidanceTools` class with methods for each guidance topic
- Mirror exact content from prompt handlers but as tool responses

### Step 3.2: Add 11 Guidance Tools
Add these tools to the main tool list:
- `get_memory_usage_guide`
- `get_context_preservation_guide`
- `get_query_optimization_guide`
- `get_markdown_processing_guide`
- `get_memory_type_selection_guide`
- `get_duplicate_detection_guide`
- `get_directory_processing_guide`
- `get_type_suggestion_guide`
- `get_completion_checklist`
- `get_policy_compliance_guide`
- `get_violation_recovery_guide`

### Step 3.3: Integrate Guidance Tools
**File:** `src/tool_handlers.py`
- Import and initialize `GuidanceTools`
- Add guidance tool handlers to `handle_tool_call` method
- Update `get_available_tools` in `src/mcp_server.py`

## Phase 4: Testing and Validation

### Step 4.1: Create Tools-Only Test Suite
**File:** `tests/test_tools_only_mode.py`
- Test server mode switching
- Test enhanced initialize_new_agent functionality
- Test all guidance tools return expected content
- Test tools-only server excludes prompts

### Step 4.2: Integration Testing
- Test agent creation workflow with tools-only
- Verify policy loading in enhanced tools
- Compare guidance tool output with original prompts

## Phase 5: Scripts and Documentation

### Step 5.1: Create Startup Scripts
- **File:** `scripts/run-tools-only.sh`
- **File:** `scripts/run-prompts-only.sh` (implement missing one)
- Add Poetry script shortcuts

### Step 5.2: Update Documentation
- **File:** `docs/TOOLS_ONLY_USAGE.md` (new)
- Update `docs/PROMPT_EXAMPLES.md` with tools-only examples
- Update README with server mode explanations

## Detailed Implementation Examples

### Step 1.1: Command-Line Arguments (memory_server.py)

```python
#!/usr/bin/env python3
import argparse
import os

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Memory MCP Server - Vector memory management",
        epilog="Server modes: full (default), prompts-only, tools-only"
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--tools-only", action="store_true")
    mode_group.add_argument("--prompts-only", action="store_true") 
    mode_group.add_argument("--full", action="store_true")
    return parser.parse_args()

def determine_server_mode(args):
    if os.getenv("TOOLS_ONLY") == "1" or args.tools_only:
        return "tools-only"
    elif os.getenv("PROMPTS_ONLY") == "1" or args.prompts_only:
        return "prompts-only"
    return "full"

def main():
    args = parse_arguments()
    server_mode = determine_server_mode(args)
    logger.info(f"Starting Memory MCP Server in {server_mode.upper()} mode...")
    asyncio.run(run_mcp_server(server_mode))
```

### Step 1.2: Server Mode Support (src/mcp_server.py)

```python
class MemoryMCPServer:
    def __init__(self, server_mode="full"):
        self.server_mode = server_mode
        
        # Always initialize tools and resources
        self.tool_handlers = ToolHandlers(self.memory_manager)
        self.resource_handlers = ResourceHandlers(self.memory_manager)
        
        # Conditionally initialize prompts
        if server_mode in ["full", "prompts-only"]:
            self.prompt_handlers = PromptHandlers(self.memory_manager)
        else:
            self.prompt_handlers = None

    def get_available_prompts(self):
        if self.server_mode == "tools-only" or not self.prompt_handlers:
            return []
        return self.prompt_handlers.list_prompts()

async def run_mcp_server(server_mode="full"):
    server = MemoryMCPServer(server_mode)
    
    # Update capabilities based on mode
    capabilities = {"tools": {"listChanged": False}}
    if server_mode != "tools-only":
        capabilities["prompts"] = {"listChanged": False}
    if server_mode != "prompts-only":
        capabilities["resources"] = {"subscribe": False, "listChanged": False}
```

### Step 2.1: Enhanced initialize_new_agent Tool

```python
# In src/tool_handlers.py - enhance existing method
async def _handle_initialize_new_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced agent initialization with policy loading and detailed reporting."""
    agent_id = arguments.get("agent_id", str(uuid.uuid4()))
    agent_role = arguments.get("agent_role", "general")
    memory_layers = arguments.get("memory_layers", ["global", "learned"])
    policy_version = arguments.get("policy_version", "latest")
    load_policies = arguments.get("load_policies", True)
    
    results = []
    errors = []
    
    # Step 1: Register agent (existing logic)
    # Step 2: Load policies if requested (NEW)
    if load_policies:
        try:
            from .policy_processor import PolicyProcessor
            policy_processor = PolicyProcessor()
            policy_result = await policy_processor.build_canonical_policy(
                directory=None, policy_version=policy_version
            )
            if policy_result["success"]:
                results.append(f"✅ Policy version '{policy_version}' loaded")
                results.append(f"📁 Files processed: {policy_result.get('files_processed', 0)}")
            else:
                errors.append(f"❌ Policy loading failed: {policy_result.get('error')}")
        except Exception as e:
            errors.append(f"❌ Policy loading error: {str(e)}")
    
    # Return detailed report (same format as agent_startup prompt)
    return {
        "content": self._format_agent_startup_report(agent_id, agent_role, memory_layers, results, errors),
        "metadata": {
            "agent_id": agent_id,
            "initialization_success": len(errors) == 0
        }
    }
```

### Step 3.1: Guidance Tools Class (new file: src/guidance_tools.py)

```python
"""
Guidance tools providing documentation and best practices.
Replaces guidance prompts in tools-only mode.
"""

class GuidanceTools:
    def __init__(self):
        self.guides = self._load_guidance_content()
    
    def get_memory_usage_guide(self, section="all", format="markdown"):
        """Return memory usage best practices guide."""
        content = self.guides["memory_usage"]
        if section != "all":
            # Return specific section
            content = self._extract_section(content, section)
        return self._format_response(content, format)
    
    def get_context_preservation_guide(self, section="all", format="markdown"):
        """Return context preservation strategies."""
        # Similar implementation for each guide...
    
    def _load_guidance_content(self):
        """Load all guidance content (copied from prompt handlers)."""
        return {
            "memory_usage": """# Agent Memory Usage Patterns...""",
            "context_preservation": """# Context Preservation Strategy...""",
            # ... all other guides
        }
```

### Step 3.2: Integration (src/tool_handlers.py)

```python
from .guidance_tools import GuidanceTools

class ToolHandlers:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.guidance_tools = GuidanceTools()  # NEW
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]):
        # Add guidance tool handlers
        if tool_name == "get_memory_usage_guide":
            return await self._handle_get_memory_usage_guide(arguments)
        elif tool_name == "get_context_preservation_guide":
            return await self._handle_get_context_preservation_guide(arguments)
        # ... handle all guidance tools
```

## Prompt to Tool Mapping

### Functional Prompts → Enhanced Tools

| Current Prompt | What It Does | Enhanced Tool |
|----------------|--------------|---------------|
| `agent_startup` | Registers agent + loads policies | Enhanced `initialize_new_agent` |
| `development_agent_startup` | Same with dev defaults | `initialize_development_agent` |
| `testing_agent_startup` | Same with test defaults | `initialize_testing_agent` |

### Guidance Prompts → New Tools

| Current Prompt | New Tool | Purpose |
|----------------|----------|---------|
| `agent_memory_usage_patterns` | `get_memory_usage_guide` | Best practices guide |
| `context_preservation_strategy` | `get_context_preservation_guide` | Context strategies |
| `memory_query_optimization` | `get_query_optimization_guide` | Query optimization tips |
| `markdown_optimization_rules` | `get_markdown_processing_guide` | Markdown processing rules |
| `memory_type_selection_criteria` | `get_memory_type_selection_guide` | Memory type selection guide |
| `duplicate_detection_strategy` | `get_duplicate_detection_guide` | Deduplication strategies |
| `directory_processing_best_practices` | `get_directory_processing_guide` | Directory processing guide |
| `memory_type_suggestion_guidelines` | `get_type_suggestion_guide` | Type suggestion rules |
| `final_checklist` | `get_completion_checklist` | Completion checklist |
| `policy_compliance_guide` | `get_policy_compliance_guide` | Policy compliance guide |
| `policy_violation_recovery` | `get_violation_recovery_guide` | Violation recovery guide |

## Implementation Order Priority

**High Priority (Core functionality):**
1. Step 1.1-1.3: Server mode infrastructure
2. Step 2.1: Enhanced initialize_new_agent
3. Step 4.1: Basic testing

**Medium Priority (Feature completeness):**
4. Step 3.1-3.3: Guidance tools implementation
5. Step 2.2: Preset agent initialization tools
6. Step 4.2: Integration testing

**Low Priority (Polish):**
7. Step 5.1: Startup scripts
8. Step 5.2: Documentation updates

## Testing Strategy

```bash
# Test tools-only mode
python memory_server.py --tools-only
# Should only expose tools + resources, no prompts

# Test enhanced agent initialization  
initialize_new_agent {
  "agent_id": "test-001",
  "agent_role": "developer", 
  "memory_layers": ["global", "learned", "agent"],
  "load_policies": true
}

# Test guidance tools
get_memory_usage_guide {"section": "best_practices", "format": "markdown"}
```

## Benefits

**✅ Complete Functionality Preservation**
- All prompt capabilities available as tools
- Same underlying functionality, different interface
- No loss of features

**✅ Better API Design**
- Tools have structured inputs/outputs
- Better error handling
- More discoverable parameters

**✅ Cursor Compatibility**
- No prompts for Cursor to auto-select
- Direct tool invocation workflow
- Cleaner separation of concerns

**✅ Enhanced Functionality**
- Could add filtering/sectioning to guidance tools
- Better structured responses
- Composable tool calls

---

This plan provides complete feature parity with the current prompt-based system while offering the clean tools-only interface that Cursor prefers.