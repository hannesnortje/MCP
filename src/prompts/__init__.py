"""
Prompt handler modules for MCP Memory Server.

This package contains specialized prompt handler modules that were extracted 
from the original monolithic prompt_handlers.py file for better maintainability
and separation of concerns.

Prompt Handler Modules:
- core_agent_prompts: Agent startup and initialization prompts
- memory_management_prompts: Memory usage, optimization, and content handling
- policy_compliance_prompts: Policy compliance, violations, and checklists

The main prompt_handlers.py module acts as a lightweight router that delegates
to these specialized modules based on prompt category.
"""

from .core_agent_prompts import CoreAgentPrompts
from .memory_management_prompts import MemoryManagementPrompts
from .policy_compliance_prompts import PolicyCompliancePrompts

__all__ = [
    "CoreAgentPrompts",
    "MemoryManagementPrompts", 
    "PolicyCompliancePrompts"
]