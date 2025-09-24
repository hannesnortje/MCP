"""
Lightweight prompt handler router for MCP Memory Server.
Delegates to specialized prompt modules for better maintainability.
"""

from typing import Dict, Any, List

try:
    from .server_config import get_logger
    from .prompts.core_agent_prompts import CoreAgentPrompts
    from .prompts.memory_management_prompts import MemoryManagementPrompts
    from .prompts.policy_compliance_prompts import PolicyCompliancePrompts
    from .policy_processor import PolicyProcessor
except ImportError:
    # Fallback for standalone usage
    import logging

    def get_logger(name: str):
        return logging.getLogger(name)

    class MockPromptHandler:
        def __init__(self, *args, **kwargs):
            pass

        def get_prompt_definitions(self):
            return []

        async def get_prompt(self, name, arguments):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Prompt handler not available for {name}"
                    }
                ]
            }

        def get_prompt(self, name, arguments):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Prompt handler not available for {name}"
                    }
                ]
            }

    CoreAgentPrompts = MockPromptHandler
    MemoryManagementPrompts = MockPromptHandler
    PolicyCompliancePrompts = MockPromptHandler

    class MockPolicyProcessor:
        pass

    PolicyProcessor = MockPolicyProcessor

logger = get_logger("prompt-handlers-router")


class PromptHandlers:
    """
    Lightweight prompt handler router that delegates to specialized modules.
    
    Provides 13 prompts across 3 categories:
    - Core Agent Prompts (3): startup and initialization
    - Memory Management Prompts (8): usage, optimization, content handling
    - Policy Compliance Prompts (3): compliance, violations, checklists
    """

    def __init__(self, memory_manager: Any = None) -> None:
        """Initialize prompt handlers router with specialized modules."""
        self.memory_manager = memory_manager
        
        # Initialize policy processor for backwards compatibility
        try:
            self.policy_processor = PolicyProcessor()
        except Exception:
            self.policy_processor = None
            logger.warning("PolicyProcessor not available")

        # Initialize specialized prompt handlers
        self.core_agent_prompts = CoreAgentPrompts(memory_manager)
        self.memory_management_prompts = MemoryManagementPrompts()
        self.policy_compliance_prompts = PolicyCompliancePrompts()

        logger.info("PromptHandlers router initialized with specialized modules")

    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompts with metadata from all specialized modules.
        
        Returns:
            List of prompt metadata dictionaries with name, description,
            arguments
        """
        all_prompts = []
        
        # Collect prompts from all specialized modules
        all_prompts.extend(self.core_agent_prompts.get_prompt_definitions())
        all_prompts.extend(
            self.memory_management_prompts.get_prompt_definitions()
        )
        all_prompts.extend(
            self.policy_compliance_prompts.get_prompt_definitions()
        )
        
        return all_prompts

    async def get_prompt(
        self, name: str, arguments: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Get a specific prompt with argument substitution by routing to
        appropriate specialized handler.
        
        Args:
            name: The prompt name
            arguments: Dictionary of argument values
            
        Returns:
            Dictionary with prompt content and metadata
        """
        if arguments is None:
            arguments = {}

        try:
            # Route to appropriate specialized handler based on prompt category
            core_agent_prompts = {
                "agent_startup",
                "development_agent_startup", 
                "testing_agent_startup"
            }

            memory_management_prompts = {
                "agent_memory_usage_patterns",
                "context_preservation_strategy",
                "memory_query_optimization",
                "markdown_optimization_rules",
                "memory_type_selection_criteria",
                "duplicate_detection_strategy",
                "directory_processing_best_practices",
                "memory_type_suggestion_guidelines"
            }

            policy_compliance_prompts = {
                "final_checklist",
                "policy_compliance_guide",
                "policy_violation_recovery"
            }

            # Route to appropriate handler
            if name in core_agent_prompts:
                return await self.core_agent_prompts.get_prompt(name, arguments)
            elif name in memory_management_prompts:
                return self.memory_management_prompts.get_prompt(
                    name, arguments
                )
            elif name in policy_compliance_prompts:
                return self.policy_compliance_prompts.get_prompt(
                    name, arguments
                )
            else:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown prompt: {name}"
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Error getting prompt {name}: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error retrieving prompt {name}: {str(e)}"
                    }
                ]
            }

    # Legacy method compatibility - delegate to specialized handlers
    async def _get_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return await self.core_agent_prompts.get_prompt(
            "agent_startup", arguments
        )

    async def _get_development_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return await self.core_agent_prompts.get_prompt(
            "development_agent_startup", arguments
        )

    async def _get_testing_agent_startup_prompt(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return await self.core_agent_prompts.get_prompt(
            "testing_agent_startup", arguments
        )

    def _get_agent_memory_usage_patterns_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "agent_memory_usage_patterns", {}
        )

    def _get_context_preservation_strategy_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "context_preservation_strategy", {}
        )

    def _get_memory_query_optimization_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "memory_query_optimization", {}
        )

    def _get_markdown_optimization_rules_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "markdown_optimization_rules", {}
        )

    def _get_memory_type_selection_criteria_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "memory_type_selection_criteria", {}
        )

    def _get_duplicate_detection_strategy_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "duplicate_detection_strategy", {}
        )

    def _get_directory_processing_best_practices_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "directory_processing_best_practices", {}
        )

    def _get_memory_type_suggestion_guidelines_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.memory_management_prompts.get_prompt(
            "memory_type_suggestion_guidelines", {}
        )

    def _get_final_checklist_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.policy_compliance_prompts.get_prompt(
            "final_checklist", {}
        )

    def _get_policy_compliance_guide_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.policy_compliance_prompts.get_prompt(
            "policy_compliance_guide", {}
        )

    def _get_policy_violation_recovery_prompt(self) -> Dict[str, Any]:
        """Legacy compatibility method."""
        return self.policy_compliance_prompts.get_prompt(
            "policy_violation_recovery", {}
        )


def calculate_suggestion_confidence(content):
    """
    Legacy compatibility function for suggestion confidence calculation.
    This function was originally at the module level and is preserved for
    backwards compatibility.
    """
    # Basic content analysis for memory type suggestion confidence
    content_lower = content.lower()
    
    # Count indicators for different memory types
    global_indicators = ['documentation', 'specification', 'standard', 
                        'reference', 'api', 'protocol']
    learned_indicators = ['lesson', 'pattern', 'insight', 'mistake', 
                         'experience', 'learned', 'practice']
    agent_indicators = ['todo', 'task', 'personal', 'scratch', 'note', 'draft']
    
    global_score = sum(1 for term in global_indicators if term in content_lower)
    learned_score = sum(1 for term in learned_indicators 
                       if term in content_lower)
    agent_score = sum(1 for term in agent_indicators if term in content_lower)
    
    # Calculate confidence based on score distribution
    total_score = global_score + learned_score + agent_score
    if total_score == 0:
        return 0.5  # Default medium confidence
    
    max_score = max(global_score, learned_score, agent_score)
    confidence = min(0.9, 0.5 + (max_score / total_score) * 0.4)
    
    return confidence