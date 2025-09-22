"""Configuration management for MCP Memory Server."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for MCP Memory Server."""

    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")

    # Embedding Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    # Memory Configuration
    DEFAULT_MEMORY_TYPE: str = "global"
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    SIMILARITY_THRESHOLD: float = float(
        os.getenv("SIMILARITY_THRESHOLD", "0.8")
    )
    MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "10"))

    # Collection Names
    GLOBAL_MEMORY_COLLECTION: str = "global_memory"
    LEARNED_MEMORY_COLLECTION: str = "learned_memory"
    AGENT_MEMORY_COLLECTION: str = "agent_specific_memory"
    FILE_METADATA_COLLECTION: str = "file_metadata"
    AGENT_REGISTRY_COLLECTION: str = "agent_registry"
    POLICY_MEMORY_COLLECTION: str = "policy_memory"
    POLICY_VIOLATIONS_COLLECTION: str = "policy_violations"

    # Agent Configuration
    DEFAULT_AGENT_ID: str = os.getenv("DEFAULT_AGENT_ID", "default")

    # Server Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Policy Configuration
    POLICY_DIRECTORY: str = os.getenv("POLICY_DIRECTORY", "./policy")
    POLICY_RULE_ID_PATTERN: str = r"\[([A-Z]-\d+)\]"  # [P-001] format
    POLICY_REQUIRED_SECTIONS: list = [
        "Principles",
        "Forbidden Actions",
        "Required Sections",
        "Style Guide"
    ]

    @classmethod
    def get_collection_name(
        cls, memory_type: str, agent_id: Optional[str] = None
    ) -> str:
        """Get the collection name for a specific memory type and agent."""
        if memory_type == "global":
            return cls.GLOBAL_MEMORY_COLLECTION
        elif memory_type == "learned":
            return cls.LEARNED_MEMORY_COLLECTION
        elif memory_type == "agent" and agent_id:
            return f"{cls.AGENT_MEMORY_COLLECTION}_{agent_id}"
        else:
            raise ValueError(f"Invalid memory type: {memory_type}")


# Module-level constants for backward compatibility and easy import
DEFAULT_MEMORY_TYPE = Config.DEFAULT_MEMORY_TYPE
CHUNK_SIZE = Config.CHUNK_SIZE
CHUNK_OVERLAP = Config.CHUNK_OVERLAP
SIMILARITY_THRESHOLD = Config.SIMILARITY_THRESHOLD
GLOBAL_MEMORY_COLLECTION = Config.GLOBAL_MEMORY_COLLECTION
LEARNED_MEMORY_COLLECTION = Config.LEARNED_MEMORY_COLLECTION
AGENT_MEMORY_COLLECTION = Config.AGENT_MEMORY_COLLECTION
AGENT_REGISTRY_COLLECTION = Config.AGENT_REGISTRY_COLLECTION
FILE_METADATA_COLLECTION = Config.FILE_METADATA_COLLECTION
POLICY_MEMORY_COLLECTION = Config.POLICY_MEMORY_COLLECTION
POLICY_VIOLATIONS_COLLECTION = Config.POLICY_VIOLATIONS_COLLECTION
