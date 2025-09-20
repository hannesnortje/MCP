#!/usr/bin/env python3
"""
Ultra-minimal test MCP server - just logs connections
"""

import json
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - TEST-MCP - %(message)s")
logger = logging.getLogger("test-mcp")

logger.info("🚀 TEST MCP SERVER STARTED - Waiting for any input...")

try:
    line_count = 0
    for line in sys.stdin:
        line_count += 1
        logger.info(f"📥 Received line {line_count}: {line.strip()}")
        
        try:
            data = json.loads(line.strip())
            logger.info(f"📋 Parsed JSON: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                logger.info("🎯 INITIALIZATION REQUEST RECEIVED!")
                response = {
                    "jsonrpc": "2024-11-05",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "tools": [
                                    {
                                        "name": "test_tool",
                                        "description": "A simple test tool",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {},
                                            "required": []
                                        }
                                    }
                                ]
                            }
                        },
                        "serverInfo": {
                            "name": "test-server",
                            "version": "1.0.0"
                        }
                    }
                }
                print(json.dumps(response), flush=True)
                logger.info("✅ Sent initialization response")
                
            elif method == "tools/call":
                logger.info("🛠️ TOOL CALL RECEIVED!")
                response = {
                    "jsonrpc": "2024-11-05",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": "Test tool executed successfully!"}]
                    }
                }
                print(json.dumps(response), flush=True)
                logger.info("✅ Sent tool response")
                
            else:
                logger.info(f"❓ Unknown method: {method}")
                
        except json.JSONDecodeError:
            logger.info(f"❌ Invalid JSON received")
        except Exception as e:
            logger.info(f"❌ Error processing: {e}")
            
except EOFError:
    logger.info("📡 Client disconnected (EOF)")
except KeyboardInterrupt:
    logger.info("⏹️ Server stopped by user")
except Exception as e:
    logger.info(f"💥 Server error: {e}")

logger.info(f"🏁 TEST MCP SERVER ENDED - Received {line_count} lines total")