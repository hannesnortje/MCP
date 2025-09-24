# MCP Memory Server UI Integration Plan

## 📋 Analysis Summary

Based on the reference AutoGen implementation at `/media/hannesn/storage/Code/autogen/`, I've analyzed how UI integration works with their MCP server. This plan adapts their proven patterns for our MCP Memory Server.

### Key Reference Patterns Identified:
- **Unified Launcher**: Single `launch.py` script manages both server and UI  
- **Configuration-Driven**: JSON config controls UI launch behavior
- **Process Management**: Subprocess handling with graceful shutdown
- **UI Launch Modes**: `never`, `auto`, `on_demand`, `vscode_only`
- **Dependency Management**: Poetry-based PySide6 integration

## Executive Summary

This document outlines a comprehensive plan to integrate the existing PySide6 UI (copied from a previous REST API-based project) with the current MCP Memory Server. The plan adapts proven patterns from the AutoGen reference implementation to create a robust, production-ready solution.

## Current State Analysis

### Existing UI Structure
- **Location**: `/media/hannesn/storage/Code/MCP/src/ui/`
- **Framework**: PySide6 (Qt-based desktop application)
- **Architecture**: Multi-tab interface with Services layer
- **Current Tabs**: Memory, Agents, Sessions, Server status
- **Integration**: Currently designed for REST API (HTTP requests)
- **Missing**: PySide6 not in pyproject.toml dependencies

### Current MCP Server
- **Protocol**: Model Context Protocol (MCP) over stdin/stdout
- **Modes**: Full, Tools-only, Prompts-only
- **Memory Tools**: query_memory, add memory functions, guidance tools
- **Memory Resources**: Statistics, health status, access matrix
- **No UI Integration**: Currently no auto-launch capability

### Reference AutoGen Implementation
- **Launcher**: `launch.py` with unified process management
- **Config System**: JSON-based configuration with UI launch modes
- **UI Control**: `ui_control.py` for managing launch behavior
- **Process Management**: Robust subprocess handling with graceful shutdown

### Integration Challenges

1. **Protocol Mismatch**: UI expects HTTP REST API, MCP server uses stdin/stdout protocol
2. **Missing Dependencies**: PySide6 not in pyproject.toml dependencies
3. **Service Layer**: Current services expect HTTP endpoints
4. **Auto-launch**: No mechanism to start UI when server starts
5. **Memory-only Focus**: Need to disable/grey out non-memory functionality

## 🏗️ Implementation Steps (AutoGen-Inspired)

### **Step 1: Foundation & Dependencies** (Branch: `feature/ui-foundation`)
**Duration**: 1-2 days  
**Focus**: Set up dependencies and basic structure based on AutoGen patterns

#### 1.1 Add PySide6 Dependencies (Following AutoGen pyproject.toml)
```toml
# Add to pyproject.toml [tool.poetry.dependencies]
PySide6 = "^6.6.0"
aiofiles = "^24.1.0"
```

#### 1.2 Create Configuration System (Based on AutoGen Pattern)
```python
# src/ui_config.py
class UILaunchMode(Enum):
    NEVER = "never"
    AUTO = "auto"  
    ON_DEMAND = "on_demand"

@dataclass
class MCPConfig:
    ui: UIConfig
    server: ServerConfig
```

#### 1.3 Create Unified Launcher (Adapted from AutoGen)
```python
# launcher.py - Main entry point
class MCPLauncher:
    def should_launch_ui(self) -> bool
    def start_server(self) -> bool
    def start_ui(self) -> bool
    def stop_all(self) -> None
```

---

### **Step 2: MCP Client Adapter** (Branch: `feature/mcp-client-adapter`)  
**Duration**: 2-3 days  
**Focus**: Create bridge between UI and MCP protocol

#### 2.1 Create MCP Client Adapter
```python
# src/ui/mcp_client.py
class MCPClientAdapter:
    """Bridges PySide6 UI with MCP stdin/stdout protocol"""
    
    def __init__(self, server_process: subprocess.Popen)
    async def call_tool(self, tool_name: str, arguments: dict) -> dict
    async def query_memory(self, query: str, types: list, limit: int) -> dict
    async def get_memory_stats(self) -> dict
    async def list_collections(self) -> list
```

#### 2.2 Replace HTTP Services
Replace existing HTTP-based services:
- `MemoryService` → Use MCP `query_memory` tool
- Collection fetching → Use MCP resource endpoints
- Statistics → Use MCP `system_health` tool

---

### **Step 3: Memory-Only UI** (Branch: `feature/memory-only-ui`)
**Duration**: 1-2 days  
**Focus**: Focus UI on memory functionality only

#### 3.1 Modify Main Window Layout
```python
# src/ui/main_window.py modifications:
- Grey out Agent Manager tab
- Grey out Session Manager tab  
- Keep Memory Browser tab fully functional
- Update status messages for MCP mode
```

#### 3.2 Memory Browser Enhancements
- **Search Tab**: Query memory using MCP tools
- **Upload Tab**: Store files via MCP tools
- **Statistics Tab**: Display memory stats from MCP
- **Collections Tab**: Browse collections via MCP

---

### **Step 4: Auto-Launch Integration** (Branch: `feature/auto-launch`)
**Duration**: 2-3 days  
**Focus**: Integrate UI launch with server startup (AutoGen pattern)

#### 4.1 Update Memory Server Entry Point
```python
# memory_server.py modifications
def main():
    args = parse_arguments()
    server_mode = determine_server_mode(args)
    
    # NEW: Check if UI should be launched
    if should_launch_ui(args):
        launch_with_ui(server_mode)
    else:
        asyncio.run(run_mcp_server(server_mode))
```

#### 4.2 Configuration Integration (AutoGen JSON pattern)
```json
// Add to root: mcp.config.json
{
  "ui": {
    "launch_mode": "auto",
    "window_geometry": {"width": 1200, "height": 800}
  },
  "server": {
    "host": "localhost", 
    "port": 6333,
    "tools_only": false
  }
}
```

#### 4.3 Command Line Options (AutoGen Pattern)
```bash
# New command line options:
python memory_server.py --with-ui          # Force launch UI
python memory_server.py --server-only      # No UI (override config)
python memory_server.py --ui-only          # UI only (connect to existing)
python launcher.py                         # Use unified launcher
```

---

### **Step 5: Polish & Testing** (Branch: `feature/ui-polish`)
**Duration**: 1-2 days  
**Focus**: Final refinements and comprehensive testing

## 🔧 Technical Implementation Details (AutoGen-Inspired)

### Configuration System (AutoGen Pattern)
```python
# src/config.py
class UILaunchMode(Enum):
    NEVER = "never"        # Never auto-launch
    AUTO = "auto"          # Always launch with server  
    ON_DEMAND = "on_demand" # Launch when requested

@dataclass 
class MCPConfig:
    ui: UIConfig
    server: ServerConfig
    
    @classmethod
    def load(cls, path: Path = None) -> 'MCPConfig':
        # Load from mcp.config.json
        
    def save(self, path: Path = None):
        # Save to mcp.config.json
```

### MCP Client Adapter Architecture
```python
# src/ui/services/mcp_client.py
class MCPClient:
    """Handles MCP protocol communication for UI"""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.request_id = 0
        
    async def start_server(self, server_mode: str):
        """Start MCP server subprocess"""
        cmd = ["python", "memory_server.py", f"--{server_mode}"]
        self.server_process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True
        )
        
    async def call_tool(self, name: str, args: dict) -> dict:
        """Call MCP tool and return result"""
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call", 
            "params": {"name": name, "arguments": args}
        }
        self.request_id += 1
        
        # Send to server stdin
        self.server_process.stdin.write(json.dumps(request) + '\n')
        self.server_process.stdin.flush()
        
        # Read response from stdout
        response_line = self.server_process.stdout.readline()
        return json.loads(response_line)
        
    # Memory-specific convenience methods
    async def query_memory(self, query: str, types: list, limit: int):
        return await self.call_tool("query_memory", {
            "query": query, "memory_types": types, "limit": limit
        })
        
    async def get_memory_stats(self):
        return await self.call_tool("system_health", {})
```

### Launcher Integration (AutoGen Pattern)
```python
# launcher.py
class MCPLauncher:
    def __init__(self):
        self.config = MCPConfig.load()
        self.server_process = None
        self.ui_process = None
        
    def should_launch_ui(self, force_ui: bool = False) -> bool:
        if force_ui:
            return True
        return self.config.ui.launch_mode == UILaunchMode.AUTO
        
    async def launch(self, server_mode: str = "full", 
                    server_only: bool = False, 
                    ui_only: bool = False,
                    force_ui: bool = False):
        
        launch_server = not ui_only
        launch_ui = self.should_launch_ui(force_ui) and not server_only
        
        if launch_server:
            await self.start_server(server_mode)
            
        if launch_ui:
            await self.start_ui()
            
        # Wait and monitor processes
        await self.monitor_processes(launch_server, launch_ui)
```

## 🧪 Testing Strategy

### Unit Testing
- Configuration loading/saving
- MCP client communication
- UI component functionality
- Process management

### Integration Testing
- Server + UI launch coordination
- MCP protocol communication
- Configuration changes
- Error scenarios

### End-to-End Testing
- Complete workflow testing
- Multi-session scenarios
- Performance under load
- Recovery from failures
poetry install
poetry run python -c "import PySide6; print('PySide6 OK')"
```

---

### Step 2: MCP Client Integration
**Branch**: `feature/mcp-client-adapter`
**Duration**: 2-3 days

#### Tasks:
1. **Implement MCP Communication**
   - Create subprocess-based MCP server communication
   - Implement MCP tool calling from UI
   - Add response parsing and error handling

2. **Replace Memory Service Backend**
   - Modify `src/ui/services/memory_service.py`
   - Replace HTTP calls with MCP tool calls
   - Map UI memory operations to MCP tools:
     - Search → `query_memory` MCP tool
     - Stats → `system_health` MCP tool
     - Collections → MCP resources

3. **Update Memory Browser Widget**
   - Ensure `memory_browser.py` works with new service backend
   - Test all memory operations through MCP
   - Maintain existing UI behavior

#### Acceptance Criteria:
- [ ] UI can communicate with MCP server via subprocess
- [ ] Memory search works through MCP protocol
- [ ] Memory statistics display correctly
- [ ] All memory browser functionality preserved
- [ ] Error handling for MCP communication failures

#### Technical Implementation:

```python
# src/ui/mcp_client.py
import asyncio
import json
import subprocess
from typing import Dict, Any, Optional

class MCPClient:
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.process: Optional[subprocess.Popen] = None
        
    async def start_server(self):
        """Start MCP server process"""
        self.process = subprocess.Popen(
            ["python", self.server_script_path, "--tools-only"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict:
        """Call MCP tool and return response"""
        # Implement MCP protocol message handling
        pass
```

#### Testing:
```bash
# Test MCP client integration
python -m src.ui.main
# In UI: Search for memory → Should use MCP protocol
# Verify MCP server logs show tool calls from UI
```

---

### Step 3: Memory-Only UI
**Branch**: `feature/memory-only-ui`
**Duration**: 1-2 days

#### Tasks:
1. **Disable Non-Memory Tabs**
   - Grey out Agents, Sessions tabs in main window
   - Add tooltips explaining memory-only focus
   - Disable related functionality

2. **Focus on Memory Functionality**
   - Ensure all 4 memory sub-tabs work correctly:
     - Search Results
     - Upload Files  
     - Statistics
     - Collections
   - Implement complete memory operations through MCP

3. **Update UI Configuration**
   - Update window title to reflect memory focus
   - Modify config to remove non-memory settings
   - Clean up unused service dependencies

#### Acceptance Criteria:
- [ ] Only Memory tab is active and functional
- [ ] Other tabs are visually disabled (greyed out)
- [ ] All memory sub-functionality works correctly
- [ ] Upload, search, stats, collections all operational
- [ ] No functionality regressions in memory features

#### Implementation:
```python
# In src/ui/main_window.py - setupCentralWidget()
# Grey out non-memory tabs
left_widget.setTabEnabled(2, False)  # Agents tab
left_widget.setTabEnabled(3, False)  # Sessions tab
left_widget.setTabText(2, "Agents (Disabled)")
left_widget.setTabText(3, "Sessions (Disabled)")
```

#### Testing:
```bash
# Test memory-only functionality
python -m src.ui.main
# Verify:
# - Memory tab works completely
# - Other tabs are greyed out
# - All memory operations functional
```

---

### Step 4: Auto-Launch Integration
**Branch**: `feature/auto-launch`
**Duration**: 2-3 days

#### Tasks:
1. **Add UI Launch Configuration**
   - Add UI auto-launch options to MCP server config
   - Environment variables for UI control
   - Command-line flags for UI launching

2. **Integrate UI Launch into Server Startup**
   - Modify `memory_server.py` to optionally launch UI
   - Add process management for UI subprocess
   - Handle UI process lifecycle

3. **Cross-Platform Process Management**
   - Linux/Windows compatible UI launching
   - Proper process cleanup on server shutdown
   - Error handling for UI launch failures

#### Acceptance Criteria:
- [ ] MCP server can auto-launch UI on startup
- [ ] Configuration options for enabling/disabling UI
- [ ] UI process properly managed (start/stop with server)
- [ ] Cross-platform compatibility
- [ ] Graceful fallback when UI launch fails

#### Technical Implementation:

```python
# In memory_server.py
import subprocess
import sys
from typing import Optional

def launch_ui_if_configured() -> Optional[subprocess.Popen]:
    """Launch UI if configured to do so"""
    if os.getenv("LAUNCH_UI", "false").lower() in ("1", "true", "yes"):
        try:
            ui_script = Path(__file__).parent / "src" / "ui" / "main.py"
            process = subprocess.Popen([
                sys.executable, "-m", "src.ui.main"
            ], cwd=Path(__file__).parent)
            logger.info("UI launched successfully")
            return process
        except Exception as e:
            logger.error(f"Failed to launch UI: {e}")
    return None

# In main()
async def main():
    ui_process = launch_ui_if_configured()
    try:
        await run_mcp_server(server_mode)
    finally:
        if ui_process:
            ui_process.terminate()
```

#### Configuration Options:
```bash
# Environment variables
LAUNCH_UI=true python memory_server.py
MCP_UI_ENABLED=1 python memory_server.py

# Command line flags
python memory_server.py --launch-ui
python memory_server.py --ui-auto-launch
```

#### Testing:
```bash
# Test auto-launch
LAUNCH_UI=true python memory_server.py
# Verify: UI opens automatically when server starts

# Test without auto-launch  
python memory_server.py
# Verify: Server starts without UI

# Test server shutdown
# Verify: UI closes when server stops
```

---

### Step 5: Polish & Testing
**Branch**: `feature/ui-polish`
**Duration**: 1-2 days

#### Tasks:
1. **UI Polish & Error Handling**
   - Improve error messages and user feedback
   - Add loading indicators for MCP operations
   - Enhance UI responsiveness

2. **Comprehensive Testing**
   - Test all memory operations end-to-end
   - Test error conditions and recovery
   - Test UI auto-launch in different scenarios

3. **Documentation & Configuration**
   - Update README with UI instructions
   - Document configuration options
   - Create user guide for memory UI

#### Acceptance Criteria:
- [ ] All memory operations work smoothly through UI
- [ ] Proper error handling and user feedback
- [ ] Documentation is complete and accurate
- [ ] No regressions in existing MCP server functionality
- [ ] UI provides good user experience

#### Testing Checklist:
- [ ] Memory search through UI
- [ ] File upload to memory through UI  
- [ ] Memory statistics display
- [ ] Collections management
- [ ] UI auto-launch with server
- [ ] Server shutdown properly closes UI
- [ ] Error conditions handled gracefully
- [ ] UI works on target platforms

## 🚨 Risk Management

### High Risk Items
1. **MCP Protocol Stability**: Subprocess communication can be fragile
   - *Mitigation*: Robust error handling, connection recovery
2. **Process Coordination**: Managing multiple processes reliably
   - *Mitigation*: Based on proven AutoGen patterns
3. **PySide6 Dependencies**: GUI framework complexity
   - *Mitigation*: Minimal UI changes, focus on backend integration

### Medium Risk Items
1. **Configuration Compatibility**: Ensuring config system works across environments
2. **Performance**: UI responsiveness with MCP communication
3. **Cross-platform**: Windows/Mac/Linux compatibility

## 📚 Branch Strategy & Workflow

### Branch Naming Convention
- `feature/ui-foundation` → Foundation and dependencies
- `feature/mcp-client-adapter` → MCP protocol integration  
- `feature/memory-only-ui` → UI focusing and cleanup
- `feature/auto-launch` → Server integration
- `feature/ui-polish` → Final polish and testing

### Development Workflow
1. **Create Feature Branch**: From current `feature/copy-ui`
2. **Implement Step**: Follow acceptance criteria
3. **Test Thoroughly**: Unit + integration tests
4. **Create PR**: Request review and approval  
5. **Merge to Master**: After approval
6. **Create Next Branch**: From updated master
7. **Repeat**: Until all steps complete

### Testing Gates
- Each step requires all tests passing
- Integration testing between steps
- User acceptance testing before merge
- Performance benchmarking for final step

## 📖 Usage Examples (AutoGen-Inspired)

### Server with Auto-Launch UI
```bash
# Start server with UI (based on config)
python memory_server.py

# Force UI launch regardless of config  
python memory_server.py --with-ui

# Server only (no UI)
python memory_server.py --server-only
```

### Using Unified Launcher (AutoGen Pattern)
```bash
# Use configuration settings
python launcher.py

# Specific launch modes
python launcher.py --server-only
python launcher.py --ui-only  
python launcher.py --with-ui
```

### Configuration Control
```bash
# Control UI launch behavior
python ui_control.py status                    # Show current config
python ui_control.py set auto                  # Auto-launch UI
python ui_control.py set never                 # Never launch UI
python ui_control.py launch                    # Launch UI now
```

## 🎯 Success Criteria

### Functional Requirements
- ✅ UI integrates natively with MCP server (no REST API)
- ✅ Memory tab fully functional with all 4 sub-tabs
- ✅ Other tabs appropriately disabled/greyed out
- ✅ UI auto-launches with server (configurable)
- ✅ Configuration system manages launch behavior
- ✅ Graceful process management and shutdown

### Technical Requirements  
- ✅ Based on proven AutoGen integration patterns
- ✅ Robust MCP protocol communication
- ✅ Cross-platform compatibility (Windows/Mac/Linux)
- ✅ Proper dependency management with Poetry
- ✅ Comprehensive test coverage
- ✅ Clean, maintainable code architecture

### User Experience Requirements
- ✅ Seamless workflow from server start to UI usage
- ✅ Clear visual feedback for MCP operations
- ✅ Intuitive configuration management
- ✅ Reliable error handling and recovery
- ✅ Responsive UI with good performance

---

## 🚀 Ready to Begin?

This plan is based on the proven AutoGen implementation patterns and provides a clear, step-by-step approach to integrating the UI with your MCP Memory Server.

**Next Steps:**
1. **Review and approve** this plan
2. **Start with Step 1** - Foundation & Dependencies
3. **Create branch**: `feature/ui-foundation` 
4. **Begin implementation** following the detailed acceptance criteria

Each step is designed to be thoroughly tested before moving to the next, ensuring a robust and reliable final implementation.
5. Master branch always deployable

### Branch Progression:
```
master
├── feature/ui-foundation
├── feature/mcp-client-adapter  
├── feature/memory-only-ui
├── feature/auto-launch
└── feature/ui-polish
```

### Testing & Approval Process:
1. **Develop** on feature branch
2. **Test** all functionality thoroughly
3. **Document** any issues or limitations
4. **Request approval** from project maintainer
5. **Merge** to master after approval
6. **Deploy** and verify in master
7. **Create next feature branch**

## Dependencies & Prerequisites

### New Python Dependencies:
```toml
# Add to pyproject.toml [tool.poetry.dependencies]
PySide6 = "^6.6.0"
aiohttp = "^3.9.0"  # For async HTTP if needed as fallback
```

### System Dependencies:
- Qt6 libraries (usually installed via PySide6)
- Display server (X11/Wayland on Linux, automatic on Windows/Mac)

### Development Dependencies:
```toml
# Add to [tool.poetry.group.dev.dependencies]  
pytest-qt = "^4.2.0"  # For UI testing
```

## Risk Assessment & Mitigation

### High Risk:
1. **MCP Protocol Complexity**: MCP stdin/stdout communication from UI
   - **Mitigation**: Implement robust MCP client with proper error handling
   - **Fallback**: Local memory client mode as implemented

2. **UI Process Management**: Managing UI subprocess lifecycle
   - **Mitigation**: Proper process management with cleanup
   - **Fallback**: Manual UI launch if auto-launch fails

### Medium Risk:
1. **Cross-Platform Compatibility**: UI launch on different OS
   - **Mitigation**: Test on target platforms early
   - **Fallback**: Platform-specific launch scripts

2. **Memory Operation Complexity**: Mapping UI operations to MCP tools
   - **Mitigation**: Thorough testing of each memory operation
   - **Fallback**: HTTP API bridge if needed

### Low Risk:
1. **UI Performance**: PySide6 performance with memory operations
   - **Mitigation**: Async operations, progress indicators
   - **Fallback**: Operation optimization

## Configuration Options

### Environment Variables:
```bash
# UI Control
LAUNCH_UI=true|false           # Auto-launch UI with server
MCP_UI_ENABLED=1|0            # Enable UI integration

# UI Behavior  
UI_MEMORY_ONLY=true|false     # Show only memory functionality
UI_AUTO_CONNECT=true|false    # Auto-connect to server

# Server Integration
MCP_SERVER_MODE=tools-only    # Server mode for UI integration
```

### Command Line Options:
```bash
# Server startup
python memory_server.py --launch-ui     # Start server with UI
python memory_server.py --ui-enabled    # Enable UI integration

# UI startup
python -m src.ui.main --memory-only     # Memory-only mode
python -m src.ui.main --auto-connect    # Auto-connect to server
```

## Success Criteria

### Functional Requirements:
- [ ] UI opens automatically when MCP server starts (configurable)
- [ ] Memory tab fully functional with all 4 sub-tabs
- [ ] All memory operations work through MCP protocol
- [ ] Non-memory tabs appropriately disabled
- [ ] Proper error handling and user feedback

### Technical Requirements:
- [ ] No regressions in existing MCP server functionality
- [ ] Proper process management for UI subprocess
- [ ] Cross-platform compatibility (Linux primary)
- [ ] Clean shutdown of UI when server stops

### User Experience Requirements:
- [ ] Intuitive memory management interface
- [ ] Responsive UI with loading indicators
- [ ] Clear feedback on operations and errors
- [ ] Professional appearance with disabled tabs clearly marked

## Timeline Estimate

| Step | Duration | Dependencies |
|------|----------|--------------|
| Step 1: Foundation | 1-2 days | None |
| Step 2: MCP Integration | 2-3 days | Step 1 |
| Step 3: Memory-Only UI | 1-2 days | Step 2 |
| Step 4: Auto-Launch | 2-3 days | Step 3 |
| Step 5: Polish & Testing | 1-2 days | Step 4 |
| **Total** | **7-12 days** | Sequential |

## Next Steps

1. **Review and Approve Plan**: Confirm approach and timeline
2. **Create Feature Branch**: `feature/ui-foundation`
3. **Begin Step 1**: Update dependencies and create MCP client
4. **Iterative Development**: Follow step-by-step approach with testing
5. **Regular Check-ins**: Review progress and adjust plan as needed

---

*This plan provides a structured approach to integrating the existing PySide6 UI with the MCP Memory Server, focusing on memory functionality while ensuring proper process management and user experience.*