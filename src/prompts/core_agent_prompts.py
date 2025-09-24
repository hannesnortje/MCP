"""
Core agent prompt handlers for MCP Memory Server.
Handles agent startup, initialization, and role-specific prompts.
"""

from datetime import datetime
from typing import Dict, Any
import uuid

try:
    from ..server_config import get_logger
except ImportError:
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger("core-agent-prompts")


class CoreAgentPrompts:
    """Handles core agent initialization and startup prompts."""

    def __init__(self, memory_manager=None):
        """Initialize with optional memory manager reference."""
        self.memory_manager = memory_manager
        # Initialize policy processor for agent startup operations
        try:
            from ..policy_processor import PolicyProcessor
            self.policy_processor = PolicyProcessor()
        except ImportError:
            self.policy_processor = None
            logger.warning("PolicyProcessor not available")

    def get_prompt_definitions(self) -> list[dict]:
        """Get definitions for core agent prompts."""
        return [
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
            }
        ]

    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a core agent prompt by name."""
        if name == "agent_startup":
            return await self._get_agent_startup_prompt(arguments)
        elif name == "development_agent_startup":
            return await self._get_development_agent_startup_prompt(arguments)
        elif name == "testing_agent_startup":
            return await self._get_testing_agent_startup_prompt(arguments)
        else:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown core agent prompt: {name}"
                    }
                ]
            }

    async def _get_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive agent startup prompt."""
        try:
            # Extract and validate arguments
            agent_id = arguments.get("agent_id", str(uuid.uuid4())[:8])
            agent_role = arguments.get("agent_role", "general")
            memory_layers = arguments.get("memory_layers", "global,learned,agent")
            policy_version = arguments.get("policy_version", "latest")
            policy_hash = arguments.get("policy_hash", "auto-generated")
            
            # Parse memory layers
            layers = [layer.strip().lower() for layer in memory_layers.split(",")]
            valid_layers = ["global", "learned", "agent"]
            layers = [layer for layer in layers if layer in valid_layers]
            if not layers:
                layers = ["global"]

            # Generate timestamp for session tracking
            session_timestamp = datetime.now().isoformat()

            # Generate comprehensive startup prompt
            startup_content = f"""# 🤖 Agent Initialization Protocol

## Agent Identity
- **Agent ID**: `{agent_id}`
- **Role**: `{agent_role.capitalize()}`
- **Session**: `{session_timestamp}`
- **Policy Version**: `{policy_version}`
- **Policy Hash**: `{policy_hash}`

## Memory System Access Configuration

You now have access to a sophisticated **3-layer memory system**:

### 🌍 Global Memory Layer
- **Purpose**: Shared knowledge base across all agents
- **Content**: Documentation, standards, references, APIs
- **Usage**: Query for established facts, procedures, and universal knowledge
- **Best Practice**: Use for information that benefits all agents

### 🧠 Learned Memory Layer  
- **Purpose**: Accumulated wisdom and lessons learned
- **Content**: Patterns, insights, mistakes, solutions, experiences
- **Usage**: Learn from past experiences and documented lessons
- **Best Practice**: Add new insights and patterns you discover

### 👤 Agent Memory Layer (`{agent_id}`)
- **Purpose**: Your personal workspace and context
- **Content**: Tasks, personal notes, session context, agent-specific data
- **Usage**: Store your working context, tasks, and personal observations
- **Best Practice**: Keep your working state and context here

## Configured Memory Layers
Your active memory layers: **{', '.join(layers)}**

## Core Memory Operations

### Adding Information
```
Use the memory tools to store information:
- add_to_global_memory(content, title, memory_type)
- add_to_learned_memory(content, title, memory_type) 
- add_to_agent_memory(content, title, memory_type)
```

### Querying Information
```
Search across your configured layers:
- query_memory(query, memory_types, limit)
- compare_against_learned_memory(content, similarity_threshold)
```

## Role-Specific Guidelines

### {agent_role.capitalize()} Agent Responsibilities:
"""

            # Add role-specific guidance
            if agent_role.lower() == "developer":
                startup_content += """
- Focus on code quality, architecture, and development patterns
- Store development insights in learned memory
- Track project context in agent memory
- Reference coding standards from global memory
"""
            elif agent_role.lower() == "testing":
                startup_content += """
- Focus on testing strategies, bug patterns, and quality assurance
- Document test insights in learned memory  
- Track test results and coverage in agent memory
- Reference testing frameworks from global memory
"""
            elif agent_role.lower() == "analyst":
                startup_content += """
- Focus on data analysis, insights, and pattern recognition
- Store analytical insights in learned memory
- Track analysis workflows in agent memory
- Reference analytical methods from global memory
"""
            else:
                startup_content += """
- Adapt your focus based on assigned tasks
- Use learned memory for insights and patterns
- Use agent memory for task context and progress
- Use global memory for reference information
"""

            startup_content += f"""

## Policy Compliance Framework

Your operations are governed by the **MCP Memory Server Policy Framework**:
- **Version**: {policy_version}
- **Hash**: {policy_hash}
- **Compliance**: All actions must follow established policies
- **Violations**: Will be logged and require corrective action

## Session Initialization Checklist

- [ ] Agent identity confirmed: `{agent_id}`
- [ ] Memory layers activated: `{', '.join(layers)}`
- [ ] Role-specific guidelines acknowledged: `{agent_role}`
- [ ] Policy framework bound: `{policy_version}`
- [ ] Ready for productive work

## Quick Start Commands

1. **Set your working context**:
   ```
   add_to_agent_memory("Working on: [your current task]", "Current Task", "context")
   ```

2. **Query for relevant background**:
   ```
   query_memory("your task or topic", ["global", "learned"], 5)
   ```

3. **Check for similar past work**:
   ```
   compare_against_learned_memory("your approach or solution", 0.8)
   ```

---

**🎯 You are now initialized and ready to work effectively with the MCP Memory System.**

**Next Step**: Start by setting your current working context in agent memory, then query for relevant background information to inform your work.
"""

            return {
                "content": [
                    {
                        "type": "text", 
                        "text": startup_content
                    }
                ],
                "metadata": {
                    "agent_id": agent_id,
                    "agent_role": agent_role,
                    "memory_layers": layers,
                    "policy_version": policy_version,
                    "session_timestamp": session_timestamp,
                    "prompt_type": "agent_startup"
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate agent startup prompt: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error generating agent startup prompt: {str(e)}"
                    }
                ]
            }

    async def _get_development_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate development agent startup prompt (alias)."""
        # Set development-specific defaults
        dev_arguments = {
            "agent_role": "developer",
            "memory_layers": "global,learned,agent",
            **arguments
        }
        return await self._get_agent_startup_prompt(dev_arguments)

    async def _get_testing_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate testing agent startup prompt (alias)."""
        # Set testing-specific defaults
        test_arguments = {
            "agent_role": "testing",
            "memory_layers": "global,learned,agent", 
            **arguments
        }
        return await self._get_agent_startup_prompt(test_arguments)