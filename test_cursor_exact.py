#!/usr/bin/env python3
"""Test script to run MCP server exactly as Cursor would"""

import os
import subprocess
import json
import time
import signal

def test_cursor_mcp_connection():
    # Set up environment exactly as specified in mcp.json
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": "/media/hannesn/storage/Code/MCP",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
        "SIMILARITY_THRESHOLD": "0.8",
        "MAX_RESULTS": "10",
        "LOG_LEVEL": "INFO"
    })
    
    # Command exactly as in mcp.json
    cmd = [
        "/media/hannesn/storage/Code/MCP/.venv/bin/python",
        "/media/hannesn/storage/Code/MCP/server_raw.py"
    ]
    
    cwd = "/media/hannesn/storage/Code/MCP"
    
    print("🚀 Starting MCP server exactly as Cursor would...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {cwd}")
    print(f"Environment vars: {[k for k in env.keys() if k.startswith(('QDRANT_', 'EMBEDDING_', 'SIMILARITY_', 'MAX_', 'LOG_', 'PYTHONPATH'))]}")
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            env=env
        )
        
        print(f"✅ Server started with PID: {proc.pid}")
        
        # Give server time to initialize
        time.sleep(3)
        
        # Test MCP protocol
        init_request = {
            "jsonrpc": "2024-11-05",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cursor",
                    "version": "0.50.5"
                }
            }
        }
        
        print("📤 Sending MCP initialization...")
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response with timeout
        import select
        ready, _, _ = select.select([proc.stdout, proc.stderr], [], [], 10.0)
        
        if proc.stdout in ready:
            response = proc.stdout.readline()
            if response:
                try:
                    resp_data = json.loads(response)
                    print("✅ Server responded successfully!")
                    print(json.dumps(resp_data, indent=2))
                    
                    # Count tools
                    tools = resp_data.get("result", {}).get("capabilities", {}).get("tools", {}).get("tools", [])
                    print(f"\n🔧 {len(tools)} tools detected:")
                    for tool in tools:
                        print(f"  - {tool['name']}")
                        
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    print(f"Raw response: {response}")
                    return False
            else:
                print("❌ Empty response from server")
                return False
                
        elif proc.stderr in ready:
            stderr_output = proc.stderr.read()
            print(f"❌ Server error: {stderr_output}")
            return False
        else:
            print("❌ Server did not respond within 10 seconds")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
        
    finally:
        try:
            if proc and proc.poll() is None:
                print("🛑 Stopping server...")
                proc.terminate()
                proc.wait(timeout=5)
        except:
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    success = test_cursor_mcp_connection()
    if success:
        print("\n✅ MCP server test PASSED - should work with Cursor")
        print("\nNext steps:")
        print("1. Ensure Cursor is closed")
        print("2. Restart Cursor to reload MCP configuration")
        print("3. Check MCP panel in Cursor for 'memory-server'")
    else:
        print("\n❌ MCP server test FAILED - needs debugging")
        print("\nCheck server logs for errors")