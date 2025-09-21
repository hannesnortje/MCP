"""
Qdrant lifecycle management for MCP Memory Server.
Handles Docker container startup, health checks, and service management.
"""

import subprocess
import time
from typing import Optional

from .server_config import (
    QDRANT_HEALTH_ENDPOINT,
    QDRANT_DOCKER_IMAGE,
    QDRANT_CONTAINER_NAME,
    QDRANT_DOCKER_PORTS,
    DOCKER_COMMAND_TIMEOUT,
    QDRANT_STARTUP_TIMEOUT,
    HEALTH_CHECK_TIMEOUT,
    get_logger
)

logger = get_logger("qdrant-manager")


def is_qdrant_running() -> bool:
    """Check if Qdrant is running on localhost:6333."""
    try:
        result = subprocess.run(
            ["curl", "-f", QDRANT_HEALTH_ENDPOINT],
            capture_output=True,
            timeout=HEALTH_CHECK_TIMEOUT
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=HEALTH_CHECK_TIMEOUT
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _check_existing_container() -> Optional[str]:
    """Check if Qdrant container exists and return its status."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={QDRANT_CONTAINER_NAME}",
             "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=DOCKER_COMMAND_TIMEOUT
        )
        
        if QDRANT_CONTAINER_NAME in result.stdout:
            return "exists"
        return None
        
    except (subprocess.TimeoutExpired, Exception) as e:
        logger.warning(f"Failed to check existing container: {e}")
        return None


def _start_existing_container() -> bool:
    """Start an existing Qdrant container."""
    logger.info("Found existing Qdrant container, starting it...")
    try:
        start_result = subprocess.run(
            ["docker", "start", QDRANT_CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=DOCKER_COMMAND_TIMEOUT
        )
        
        if start_result.returncode == 0:
            logger.info("✅ Started existing Qdrant container")
            return True
        else:
            logger.warning(
                f"Failed to start existing container: {start_result.stderr}"
            )
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout while starting existing container")
        return False


def _create_new_container() -> bool:
    """Create and run a new Qdrant container."""
    logger.info("Creating new Qdrant container...")
    try:
        # Build the docker run command
        cmd = ["docker", "run", "-d", "--name", QDRANT_CONTAINER_NAME]
        
        # Add port mappings
        for port in QDRANT_DOCKER_PORTS:
            cmd.extend(["-p", port])
            
        # Add image
        cmd.append(QDRANT_DOCKER_IMAGE)
        
        run_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DOCKER_COMMAND_TIMEOUT * 2  # Creation takes longer
        )
        
        if run_result.returncode == 0:
            logger.info("✅ Created and started new Qdrant container")
            return True
        else:
            logger.error(
                f"Failed to create Qdrant container: {run_result.stderr}"
            )
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout while creating new container")
        return False


def _wait_for_qdrant_ready() -> bool:
    """Wait for Qdrant to be ready and responding."""
    logger.info("Waiting for Qdrant to be ready...")
    
    for attempt in range(QDRANT_STARTUP_TIMEOUT):
        time.sleep(1)
        if is_qdrant_running():
            logger.info("✅ Qdrant is ready!")
            return True
            
    logger.error("❌ Qdrant did not become ready in time")
    return False


def start_qdrant_docker() -> bool:
    """Start Qdrant using Docker."""
    logger.info("Starting Qdrant with Docker...")
    
    try:
        # Check if container exists
        container_status = _check_existing_container()
        
        if container_status == "exists":
            # Container exists, try to start it
            if not _start_existing_container():
                return False
        else:
            # No container exists, create new one
            if not _create_new_container():
                return False
        
        # Wait for Qdrant to be ready
        return _wait_for_qdrant_ready()
        
    except Exception as e:
        logger.error(f"❌ Error starting Qdrant: {e}")
        return False


def ensure_qdrant_running() -> bool:
    """Ensure Qdrant is running, start it if necessary."""
    if is_qdrant_running():
        logger.info("✅ Qdrant is already running")
        return True
    
    logger.info("Qdrant not running, attempting to start...")
    
    if not is_docker_available():
        logger.error(
            "❌ Docker is not available. "
            "Please install Docker or start Qdrant manually."
        )
        return False
    
    return start_qdrant_docker()