#!/usr/bin/env python3
"""Test tool calls on the raw MCP server"""

import json
import subprocess

def test_tool_call():
    """Test a tool call on the server"""
    proc = subprocess.Popen(
        ["poetry", "run", "python", "server_raw.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialization request
        init_request = {
            "jsonrpc": "2024-11-05",
            "id": 1,
            "method": "initialize", 
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            }
        }
        
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read initialization response
        init_response = proc.stdout.readline()
        print("Init Response:", json.loads(init_response))
        
        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2024-11-05",
            "method": "notifications/initialized",
            "params": {}
        }
        
        proc.stdin.write(json.dumps(initialized_notif) + "\n")
        proc.stdin.flush()
        
        # Test set_agent_context tool
        tool_request = {
            "jsonrpc": "2024-11-05", 
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "set_agent_context",
                "arguments": {
                    "agent_name": "TestAgent"
                }
            }
        }
        
        proc.stdin.write(json.dumps(tool_request) + "\n")
        proc.stdin.flush()
        
        # Read tool response
        tool_response = proc.stdout.readline()
        if tool_response:
            response = json.loads(tool_response)
            print("✅ Tool Response:")
            print(json.dumps(response, indent=2))
        else:
            print("❌ No tool response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_tool_call()