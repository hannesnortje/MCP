# MCP Memory Server - Agent Initialization Examples

This document provides comprehensive examples for initializing agents with the MCP Memory Server, covering both **prompts-only mode** and **tools-only mode** approaches.

## 🚀 Server Modes for Optimal Client Compatibility

### Tools-Only Mode (Recommended)

The MCP Memory Server supports a **tools-only mode** that provides complete functionality through tools, including comprehensive guidance tools for memory management best practices.

**Benefits of Tools-Only Mode:**
- ✅ All 10 guidance tools available for memory management best practices  
- ✅ Policy loading works correctly through `initialize_new_agent` tool
- ✅ Full memory management functionality through dedicated tools
- ✅ Clean separation of concerns with specialized tools
- ✅ Better error handling and validation

**How to Start Tools-Only Server:**
```bash
# Option 1: Using command line flag
python memory_server.py --tools-only

# Option 2: Using environment variable  
TOOLS_ONLY=1 python memory_server.py

# Option 3: Using Poetry
poetry run python memory_server.py --tools-only
```

### Prompts-Only Mode (Excellent for Cursor)

The MCP Memory Server also supports a **prompts-only mode** that works excellently with Cursor and other interactive MCP clients.

**Benefits of Prompts-Only Mode:**
- ✅ **Perfect Cursor compatibility**: "Call agent_startup" works flawlessly  
- ✅ **Complete policy loading**: Loads policies + 75 rules correctly
- ✅ **Full memory management**: All memory layers (global, learned, agent) work
- ✅ **Interactive workflow**: Natural prompt-based conversation pattern

**How to Start Prompts-Only Server:**
```bash
# Option 1: Using command line flag
python memory_server.py --prompts-only

# Option 2: Using environment variable
PROMPTS_ONLY=1 python memory_server.py

# Option 3: Using convenience script
./scripts/run-prompts-only.sh

# Option 4: Using Poetry script
poetry run mcp-memory-prompts
```

### Full Mode (Tools + Prompts)

For complete functionality including both tools and prompts:
```bash
# Default mode
python memory_server.py

# Or explicit full mode
./scripts/run-full.sh
```

## ✅ **BOTH METHODS WORK PERFECTLY**

Your screenshot confirms that `Call agent_startup` works excellently! Here's what you achieved:

**✅ Successful Policy Loading:**
- Policy version 'latest' loaded
- 75 rules loaded from 4 policy files  
- Policy hash: `be021bc2ccfc...`

**✅ Complete Memory Configuration:**
- Memory Layers: global, learned, agent ✅
- All layers properly configured and accessible

**✅ Agent Registration:**
- Agent ID: `dev-550e8400-e29b-41d4-a716-446655440002` ✅
- Role: developer ✅  
- System Status: 3 agents active ✅

## Choose Your Preferred Method

### Method 1: Prompts-Only Mode (Perfect for Cursor Users)

Use the `initialize_new_agent` tool for agent initialization with full policy loading and validation.

#### Tool: initialize_new_agent

#### Tool: initialize_new_agent

The `initialize_new_agent` tool is the recommended way to initialize agents with complete configuration including memory layers, role assignment, and policy binding.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | No | auto-generated UUID | Unique identifier for the agent |
| `agent_role` | string | No | "general" | Agent role (developer, analyst, admin, etc.) |
| `memory_layers` | string | No | "global,learned" | Comma-separated memory layer access |
| `policy_version` | string | No | "latest" | Policy version for compliance tracking |
| `policy_hash` | string | No | auto-generated | Policy hash for integrity verification |

### Method 2: Prompts-Only Mode (Legacy)

Use the `agent_startup` prompt for legacy client compatibility.

#### Prompt: agent_startup

The `agent_startup` prompt provides the same functionality through the prompts interface.

### Parameters (Both Methods)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_id` | string | No | auto-generated UUID | Unique identifier for the agent |
| `agent_role` | string | No | "general" | Agent role (developer, analyst, admin, etc.) |
| `memory_layers` | string | No | "global,learned" | Comma-separated memory layer access |
| `policy_version` | string | No | "latest" | Policy version for compliance tracking |
| `policy_hash` | string | No | auto-generated | Policy hash for integrity verification |

### Memory Layers

- **global**: Shared knowledge accessible to all agents
- **learned**: Insights and patterns learned from interactions  
- **agent**: Agent-specific private memory

## Complete Examples

### Tools-Only Mode Examples (Recommended)

#### 1. Full Admin Agent (All Parameters)
```json
{
  "agent_id": "admin-550e8400-e29b-41d4-a716-446655440001",
  "agent_role": "admin", 
  "memory_layers": "global,learned,agent",
  "policy_version": "latest",
  "policy_hash": "9a1c73025cc9ffb9ab9a8dd4a4fc6e552945136d7e868719dc07b9f781774cd9"
}
```

**Tool Call:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "initialize_new_agent", "arguments": {"agent_id": "admin-550e8400-e29b-41d4-a716-446655440001", "agent_role": "admin", "memory_layers": "global,learned,agent", "policy_version": "latest", "policy_hash": "9a1c73025cc9ffb9ab9a8dd4a4fc6e552945136d7e868719dc07b9f781774cd9"}}}' | poetry run python memory_server.py --tools-only
```

#### 2. Developer Agent
```json
{
  "agent_id": "dev-550e8400-e29b-41d4-a716-446655440002",
  "agent_role": "developer",
  "memory_layers": "global,learned,agent"
}
```

**Tool Call:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 2, "params": {"name": "initialize_new_agent", "arguments": {"agent_id": "dev-550e8400-e29b-41d4-a716-446655440002", "agent_role": "developer", "memory_layers": "global,learned,agent"}}}' | poetry run python memory_server.py --tools-only
```

### Prompts-Only Mode Examples (Legacy)
#### 1. Full Admin Agent (All Parameters)
```json
{
  "agent_id": "admin-550e8400-e29b-41d4-a716-446655440001",
  "agent_role": "admin", 
  "memory_layers": "global,learned,agent",
  "policy_version": "latest",
  "policy_hash": "9a1c73025cc9ffb9ab9a8dd4a4fc6e552945136d7e868719dc07b9f781774cd9"
}
```

**Usage in Cursor:**
```
Call agent_startup {"agent_id": "admin-550e8400-e29b-41d4-a716-446655440001", "agent_role": "admin", "memory_layers": "global,learned,agent", "policy_version": "latest", "policy_hash": "9a1c73025cc9ffb9ab9a8dd4a4fc6e552945136d7e868719dc07b9f781774cd9"}
```

#### 2. Developer Agent
```json
{
  "agent_id": "dev-550e8400-e29b-41d4-a716-446655440002",
  "agent_role": "developer",
  "memory_layers": "global,learned,agent"
}
```

**Your screenshot confirms:**
```
Call agent_startup {"agent_id": "dev-550e8400-e29b-41d4-a716-446655440002", "agent_role": "developer", "memory_layers": "global,learned,agent"}
```
✅ **Results in successful agent initialization with:**
- Policy version 'latest' loaded 
- 75 rules loaded from 4 policy files
- All memory layers configured correctly
- Agent registered successfully

> **💡 Cursor Pro Tip:** For prompts-only mode, start the server with:
> ```bash
> python memory_server.py --prompts-only
> ```
> This prevents Cursor from auto-selecting tools instead of your prompt calls.

## Available Guidance Tools (Tools-Only Mode)

The tools-only server provides comprehensive guidance through 10 specialized tools:

### Core Guidance Tools
- **get_memory_usage_guidance**: Best practices for memory storage and retrieval
- **get_context_preservation_guidance**: Strategies for maintaining context across sessions
- **get_query_optimization_guidance**: Optimizing memory queries for better results
- **get_markdown_optimization_guidance**: Processing and storing markdown content effectively

### Advanced Tools  
- **get_duplicate_detection_guidance**: Detecting and handling duplicate content
- **get_directory_processing_guidance**: Batch processing directories efficiently
- **get_memory_type_selection_guidance**: Choosing appropriate memory types
- **get_memory_type_suggestion_guidance**: AI-powered memory type suggestions

### Policy Tools
- **get_policy_compliance_guidance**: Following policy compliance requirements
- **get_policy_violation_recovery_guidance**: Recovering from policy violations

**Example Guidance Tool Usage:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "get_memory_usage_guidance", "arguments": {}}}' | poetry run python memory_server.py --tools-only
```

### 3. Analyst Agent (Limited Memory Access)
```json
{
  "agent_role": "analyst",
  "memory_layers": "global,learned",
  "policy_version": "v2.1"
}
```

**Usage in Cursor:**
```
Call agent_startup {"agent_role": "analyst", "memory_layers": "global,learned", "policy_version": "v2.1"}
```

### 4. Minimal Agent (Auto-Generated)
```json
{}
```

**Usage in Cursor:**
```
Call agent_startup {}
```

### 5. Testing Agent
```json
{
  "agent_role": "tester",
  "memory_layers": "global,learned"
}
```

**Usage in Cursor:**
```
Call agent_startup {"agent_role": "tester", "memory_layers": "global,learned"}
```

### 6. Content Processor Agent
```json
{
  "agent_role": "content_processor",
  "memory_layers": "global,agent"
}
```

**Usage in Cursor:**
```
Call agent_startup {"agent_role": "content_processor", "memory_layers": "global,agent"}
```

## Agent ID Formats

The system supports various agent ID formats:

### Supported Formats
- **Pure UUID**: `550e8400-e29b-41d4-a716-446655440000`
- **Role-prefixed UUID**: `admin-550e8400-e29b-41d4-a716-446655440001`
- **Custom strings**: `my-agent-123`, `qa-bot-001`
- **Auto-generated**: Leave empty for system to generate

### Examples by Format
```json
// Pure UUID
{"agent_id": "550e8400-e29b-41d4-a716-446655440000"}

// Admin prefix
{"agent_id": "admin-550e8400-e29b-41d4-a716-446655440001"}

// Developer prefix  
{"agent_id": "dev-550e8400-e29b-41d4-a716-446655440002"}

// QA prefix
{"agent_id": "qa-550e8400-e29b-41d4-a716-446655440003"}

// Custom naming
{"agent_id": "content-processor-001"}
{"agent_id": "data-analyst-main"}
{"agent_id": "support-bot-v2"}
```

## Agent Roles

### Pre-defined Roles
- **admin**: Full system access, all memory layers
- **developer**: Development-focused, full memory access
- **analyst**: Analysis-focused, read-heavy operations
- **tester**: Testing and QA operations
- **content_processor**: Content analysis and processing
- **general**: Default role with standard permissions

### Role Examples
```json
// Admin with full access
{"agent_role": "admin", "memory_layers": "global,learned,agent"}

// Developer with project focus
{"agent_role": "developer", "memory_layers": "global,learned,agent"}

// Analyst with read focus
{"agent_role": "analyst", "memory_layers": "global,learned"}

// Content processor with specific access
{"agent_role": "content_processor", "memory_layers": "global,agent"}

// Custom role
{"agent_role": "custom_specialist", "memory_layers": "global"}
```

## Memory Layer Configurations

### Access Patterns
```json
// Full access (admin/developer)
{"memory_layers": "global,learned,agent"}

// Collaborative access (analyst/tester)
{"memory_layers": "global,learned"}

// Isolated access (specialized agents)
{"memory_layers": "global,agent"}

// Read-only global (external integrations)
{"memory_layers": "global"}
```

## Policy Configuration

### Policy Version Examples
```json
// Latest policy
{"policy_version": "latest"}

// Specific version
{"policy_version": "v2.1"}
{"policy_version": "2024-09-22"}
{"policy_version": "production"}

// Development policy
{"policy_version": "dev"}
{"policy_version": "testing"}
```

### Policy Hash
The policy hash is automatically calculated when policies are loaded. You can:
- **Omit it**: System will calculate automatically
- **Provide it**: For integrity verification
- **Use specific hash**: For exact policy version matching

```json
// Auto-calculated
{"policy_version": "latest"}

// Specific hash verification
{
  "policy_version": "latest",
  "policy_hash": "9a1c73025cc9ffb9ab9a8dd4a4fc6e552945136d7e868719dc07b9f781774cd9"
}
```

## Quick Reference

### Most Common Patterns

#### Tools-Only Mode (Recommended)

**1. Simple Developer Setup:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "initialize_new_agent", "arguments": {"agent_role": "developer", "memory_layers": "global,learned,agent"}}}' | poetry run python memory_server.py --tools-only
```

**2. Admin with Verification:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "initialize_new_agent", "arguments": {"agent_id": "admin-001", "agent_role": "admin", "memory_layers": "global,learned,agent", "policy_version": "latest"}}}' | poetry run python memory_server.py --tools-only
```

**3. Analyst for Data Work:**
```bash
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "initialize_new_agent", "arguments": {"agent_role": "analyst", "memory_layers": "global,learned"}}}' | poetry run python memory_server.py --tools-only
```

#### Prompts-Only Mode (Legacy)

**1. Simple Developer Setup:**
```
Call agent_startup {"agent_role": "developer", "memory_layers": "global,learned,agent"}
```

**2. Admin with Verification:**
```
Call agent_startup {"agent_id": "admin-001", "agent_role": "admin", "memory_layers": "global,learned,agent", "policy_version": "latest"}
```

**3. Analyst for Data Work:**
```
Call agent_startup {"agent_role": "analyst", "memory_layers": "global,learned"}
```

## Response Format

Successful agent initialization returns:
```
# Agent Startup SUCCESS

## Agent Identity
- **Agent ID:** `[generated-or-provided-id]`
- **Role:** `[specified-role]`
- **Initialization Time:** [timestamp]

## Initialization Results
✅ Agent '[agent-id]' registered successfully
✅ Policy version '[version]' loaded
📁 Files processed: [count]
📝 Rules loaded: [count]

## Configuration
- **Memory Layers:** [layers]
- **Policy Version:** `[version]`
- **Policy Hash:** `[hash]...`

✅ Agent initialization success
📊 System Status: [count] agents active
```

## Error Handling

Common errors and solutions:

### Invalid Agent ID Format
❌ **Error**: Agent ID validation failed  
✅ **Solution**: Use supported formats (UUID, prefixed-UUID, or custom strings)

### Memory Layer Access Denied
❌ **Error**: Insufficient permissions for memory layer  
✅ **Solution**: Adjust role or memory layer configuration

### Policy Loading Failed
❌ **Error**: No policy files found  
✅ **Solution**: Ensure policy files exist and server has proper working directory

## Cursor Troubleshooting

### Problem: "Call agent_startup" Executes Tools Instead of Prompts

**Symptoms:**
- You type `Call agent_startup {...}` but see tool calls like `initialize_new_agent`
- Policy loading doesn't happen during agent creation
- Get tool-based workflow instead of prompt-based

**Solution:**
1. **Start server in prompts-only mode:**
   ```bash
   python memory_server.py --prompts-only
   ```

2. **Alternative Cursor Syntax to Try:**
   - `Use MCP prompt agent_startup {...}`
   - `Call prompts/get agent_startup {...}`
   - Use Cursor's command palette: Search for "MCP prompt"

3. **Verify Server Mode:**
   Check server logs for: `Starting Memory MCP Server in PROMPTS-ONLY mode...`

### Problem: Policies Not Loading in Agent Creation

**Symptoms:**
- Agent creation succeeds but no policy rules are loaded
- Missing "Policy version 'latest' loaded" message
- No policy count in startup response

**Solutions:**
1. **Use prompts-only server mode** (ensures `agent_startup` prompt is called directly)
2. **Verify policy files exist** in `./policy/` directory
3. **Check server logs** for policy loading messages

## Best Practices

1. **Use tools-only mode for new projects**: Better functionality with guidance tools
2. **Use descriptive agent IDs**: `admin-main`, `dev-backend`, `qa-frontend`
3. **Match memory layers to role**: Admins get full access, analysts get read-heavy
4. **Leverage guidance tools**: Use the 10 guidance tools for best practices
5. **Specify policy version**: For production environments
6. **Include policy hash**: For strict compliance requirements
7. **Use consistent naming**: Follow organizational conventions
8. **Use prompts-only mode for Cursor**: If you prefer prompt-based interaction

---

*Generated for MCP Memory Server - Agent Initialization System*