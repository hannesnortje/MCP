#!/usr/bin/env python3
"""Test MCP server connection like Cursor would"""

import subprocess
import json
import os
import signal
import time

def test_cursor_connection():
    """Test the server as Cursor would connect to it"""
    
    # Set environment variables like Cursor would
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
    
    # Start server like Cursor would
    cmd = ["/media/hannesn/storage/Code/MCP/.venv/bin/python", 
           "/media/hannesn/storage/Code/MCP/server_raw.py"]
    
    print(f"🚀 Starting server: {' '.join(cmd)}")
    print(f"📁 Working directory: /media/hannesn/storage/Code/MCP")
    print(f"🌍 Environment variables set: {len([k for k in env.keys() if k.startswith(('QDRANT_', 'EMBEDDING_', 'SIMILARITY_', 'MAX_', 'LOG_'))])} MCP vars")
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            cwd="/media/hannesn/storage/Code/MCP",
            env=env
        )
        
        print(f"✅ Server started with PID: {proc.pid}")
        
        # Give server time to initialize
        time.sleep(2)
        
        # Send MCP initialization
        init_msg = {
            "jsonrpc": "2024-11-05",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cursor",
                    "version": "0.42.3"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        proc.stdin.write(json.dumps(init_msg) + "\n")
        proc.stdin.flush()
        
        # Read response with timeout
        import select
        ready, _, _ = select.select([proc.stdout], [], [], 5.0)
        
        if ready:
            response = proc.stdout.readline()
            if response:
                resp_data = json.loads(response)
                print("📥 Server Response:")
                print(json.dumps(resp_data, indent=2))
                
                # Check for tools
                if "result" in resp_data and "capabilities" in resp_data["result"]:
                    tools = resp_data["result"]["capabilities"].get("tools", {}).get("tools", [])
                    print(f"\n🔧 Tools available: {len(tools)}")
                    for tool in tools[:3]:  # Show first 3
                        print(f"  - {tool['name']}")
                    if len(tools) > 3:
                        print(f"  ... and {len(tools) - 3} more")
                        
                    return True
                else:
                    print("❌ No capabilities found in response")
                    return False
            else:
                print("❌ Empty response from server")
                return False
        else:
            print("❌ Server did not respond within 5 seconds")
            
            # Check if process is still running
            if proc.poll() is None:
                print("🔍 Server is still running, checking stderr...")
                try:
                    stderr_ready, _, _ = select.select([proc.stderr], [], [], 1.0)
                    if stderr_ready:
                        stderr_output = proc.stderr.read()
                        if stderr_output:
                            print(f"🚨 Server stderr: {stderr_output}")
                except:
                    pass
            else:
                print(f"💀 Server exited with code: {proc.returncode}")
                stderr_output = proc.stderr.read()
                if stderr_output:
                    print(f"🚨 Server stderr: {stderr_output}")
                    
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
        
    finally:
        try:
            if proc and proc.poll() is None:
                print("🛑 Terminating server...")
                proc.terminate()
                proc.wait(timeout=3)
        except:
            try:
                proc.kill()
            except:
                pass

if __name__ == "__main__":
    success = test_cursor_connection()
    if success:
        print("\n✅ Server connection test PASSED - should work with Cursor")
    else:
        print("\n❌ Server connection test FAILED - needs debugging")