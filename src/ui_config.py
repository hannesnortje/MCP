"""
MCP Memory Server UI Configuration System

Based on AutoGen configuration patterns, this module provides centralized
configuration management for both MCP server and UI components, including
launch behavior control.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class UILaunchMode(Enum):
    """UI launch behavior options (AutoGen pattern)."""

    NEVER = "never"          # Never auto-launch UI
    AUTO = "auto"            # Always launch UI with server
    ON_DEMAND = "on_demand"  # Launch via API call or CLI flag


@dataclass
class UIConfig:
    """UI-specific configuration."""

    launch_mode: UILaunchMode = UILaunchMode.NEVER
    theme: str = "system"
    window_geometry: Optional[Dict[str, int]] = None
    auto_connect_server: bool = True
    debug_mode: bool = False

    def __post_init__(self) -> None:
        if self.window_geometry is None:
            self.window_geometry = {"width": 1200, "height": 800}


@dataclass
class ServerConfig:
    """MCP server configuration."""

    host: str = "127.0.0.1"
    port: int = 6333  # Qdrant default port
    log_level: str = "info"
    tools_only: bool = False
    prompts_only: bool = False


@dataclass
class MCPConfig:
    """Main MCP Memory Server configuration."""

    ui: Optional[UIConfig] = None
    server: Optional[ServerConfig] = None
    project_root: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.ui is None:
            self.ui = UIConfig()
        if self.server is None:
            self.server = ServerConfig()
        if self.project_root is None:
            self.project_root = Path(__file__).parent.parent


class ConfigManager:
    """Manages MCP configuration loading and saving (AutoGen pattern)."""

    DEFAULT_CONFIG_FILE = "mcp.config.json"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(self.DEFAULT_CONFIG_FILE)
        self._config: Optional[MCPConfig] = None

    def load_config(self) -> MCPConfig:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                return self._dict_to_config(data)
            except Exception as e:
                config_path = str(self.config_path)
                print(f"Warning: Failed to load config from {config_path}")
                print(f"Error: {e}")
                print("Using default configuration")

        # Return default configuration
        return MCPConfig()

    def save_config(self, config: MCPConfig) -> None:
        """Save configuration to file."""
        try:
            data = self._config_to_dict(config)
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config to {self.config_path}: {e}")

    def _dict_to_config(self, data: Dict) -> MCPConfig:
        """Convert dictionary to configuration object."""
        ui_data = data.get("ui", {})
        server_data = data.get("server", {})

        # Handle UILaunchMode enum
        launch_mode_str = ui_data.get("launch_mode", "never")
        try:
            launch_mode = UILaunchMode(launch_mode_str)
        except ValueError:
            launch_mode = UILaunchMode.NEVER

        ui_config = UIConfig(
            launch_mode=launch_mode,
            theme=ui_data.get("theme", "system"),
            window_geometry=ui_data.get(
                "window_geometry", {"width": 1200, "height": 800}
            ),
            auto_connect_server=ui_data.get("auto_connect_server", True),
            debug_mode=ui_data.get("debug_mode", False)
        )

        server_config = ServerConfig(
            host=server_data.get("host", "127.0.0.1"),
            port=server_data.get("port", 6333),
            log_level=server_data.get("log_level", "info"),
            tools_only=server_data.get("tools_only", False),
            prompts_only=server_data.get("prompts_only", False)
        )

        project_root = data.get("project_root")
        if project_root:
            project_root = Path(project_root)

        return MCPConfig(
            ui=ui_config,
            server=server_config,
            project_root=project_root
        )

    def _config_to_dict(self, config: MCPConfig) -> Dict:
        """Convert configuration object to dictionary."""
        # Ensure config has ui and server (should be set by __post_init__)
        assert config.ui is not None, "UI config should not be None"
        assert config.server is not None, "Server config should not be None"
        
        return {
            "ui": {
                "launch_mode": config.ui.launch_mode.value,
                "theme": config.ui.theme,
                "window_geometry": config.ui.window_geometry,
                "auto_connect_server": config.ui.auto_connect_server,
                "debug_mode": config.ui.debug_mode
            },
            "server": {
                "host": config.server.host,
                "port": config.server.port,
                "log_level": config.server.log_level,
                "tools_only": config.server.tools_only,
                "prompts_only": config.server.prompts_only
            },
            "project_root": (
                str(config.project_root) if config.project_root else None
            )
        }


# Global configuration instance (AutoGen pattern)
_config_manager = ConfigManager()


def get_config() -> MCPConfig:
    """Get the current configuration."""
    return _config_manager.load_config()


def save_config(config: MCPConfig) -> None:
    """Save the configuration."""
    _config_manager.save_config(config)


def update_ui_launch_mode(mode: UILaunchMode) -> None:
    """Update just the UI launch mode and save."""
    config = get_config()
    assert config.ui is not None, "UI config should not be None"
    config.ui.launch_mode = mode
    save_config(config)


def should_launch_ui_from_config() -> bool:
    """Check if UI should be launched based on configuration."""
    config = get_config()
    assert config.ui is not None, "UI config should not be None"
    return config.ui.launch_mode == UILaunchMode.AUTO


def should_launch_ui_from_env() -> bool:
    """Check if UI should be launched based on environment variables."""
    launch_ui = os.getenv("LAUNCH_UI", "").lower()
    mcp_ui_enabled = os.getenv("MCP_UI_ENABLED", "").lower()
    
    return (launch_ui in ("1", "true", "yes") or
            mcp_ui_enabled in ("1", "true", "yes"))


def should_launch_ui(force_ui: bool = False) -> bool:
    """Determine if UI should be launched (unified logic)."""
    if force_ui:
        return True

    # Check environment variables first (highest priority)
    if should_launch_ui_from_env():
        return True

    # Check configuration
    return should_launch_ui_from_config()
