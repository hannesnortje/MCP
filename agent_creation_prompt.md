# Simple Agent Creation Prompt

## Copy This One-Liner:

**For Cursor:** Call the MCP prompt named "agent_startup" (not tools). Use prompts/get method with name="agent_startup" and empty arguments={}.

## Alternative One-Liners:

**Developer Agent:** Use agent_startup with {"agent_role": "developer", "memory_layers": "global,learned,agent"}.

**Content Processor Agent:** Use agent_startup with {"agent_role": "content_processor", "memory_layers": "global,agent"}.

**Testing Agent:** Use agent_startup with {"agent_role": "tester", "memory_layers": "global,learned"}.

**Custom ID Agent:** Use agent_startup with {"agent_id": "550e8400-e29b-41d4-a716-446655440000", "agent_role": "developer"}.

**Admin Agent (Full):** Use agent_startup with {"agent_id": "admin-550e8400-e29b-41d4-a716-446655440001", "agent_role": "admin", "memory_layers": "global,learned,agent", "policy_version": "latest", "policy_hash": "abc123def456"}.

**Analyst Agent:** Use agent_startup with {"agent_role": "analyst", "memory_layers": "global,learned", "policy_version": "v2.1"}.

## Quick Command Reference:
```bash
# Minimal - everything auto-generated:
# No arguments needed! Will create agent with auto-generated ID and "general" role

# With custom role:
agent_role: "developer|tester|admin|content_processor" 

# With custom ID and role:
agent_id: "550e8400-e29b-41d4-a716-446655440000" (UUID format)
agent_role: "developer|tester|admin|content_processor"
memory_layers: "global,learned,agent" (optional)
policy_version: "latest" (optional)
```

## Auto-Generation Features:
✅ **agent_id**: Auto-generates UUID like "550e8400-e29b-41d4-a716-446655440000" for Qdrant compatibility  
✅ **agent_role**: Defaults to "general" if not provided  
✅ **memory_layers**: Defaults to "global,learned"  
✅ **policy_version**: Defaults to "latest"

## Important Note:
🎯 **Use PROMPTS not TOOLS**: agent_startup is a prompt (prompts/get), not a tool (tools/call). Don't use build_policy_from_markdown or other tools - just call the prompt directly.