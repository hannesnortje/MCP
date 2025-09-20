#!/usr/bin/env python3
"""Test the raw MCP server"""

import json
import subprocess
import sys

def test_server():
    # Start the server
    proc = subprocess.Popen(
        ["poetry", "run", "python", "server_raw.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
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
    
    # Read response
    try:
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("✅ Server Response:")
            print(json.dumps(response, indent=2))
            
            # Check if tools are listed
            if "result" in response and "capabilities" in response["result"]:
                tools = response["result"]["capabilities"].get("tools", {}).get("tools", [])
                print(f"\n🔧 Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print("❌ No tools found in response")
        else:
            print("❌ No response from server")
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response: {e}")
        print(f"Raw response: {response_line}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_server()