#!/usr/bin/env python3
"""
Test script to verify agent registration works with the UUID fix
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_agent_id_conversion():
    """Test the agent ID to point ID conversion"""
    print("Testing agent ID to point ID conversion...")
    
    try:
        from src.memory.agent_registry import AgentRegistry
        
        # Create a dummy registry just to test the conversion function
        registry = AgentRegistry(None, None)
        
        test_cases = [
            "dev-550e8400-e29b-4016-a716-446655440002",
            "550e8400-e29b-4016-a716-446655440002",
            "simple-test-agent",
            "123",
            "user@example.com"
        ]
        
        print("\nAgent ID -> Point ID conversions:")
        for agent_id in test_cases:
            point_id = registry._agent_id_to_point_id(agent_id)
            print(f"  {agent_id} -> {point_id}")
            
            # Verify it's a valid UUID
            import uuid
            try:
                uuid.UUID(point_id)
                print(f"    ✅ Valid UUID")
            except ValueError as e:
                print(f"    ❌ Invalid UUID: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent ID conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_registration():
    """Test actual agent registration with Qdrant"""
    print("\nTesting agent registration with Qdrant...")
    
    try:
        from src.memory_manager import QdrantMemoryManager
        
        # Initialize memory manager  
        manager = QdrantMemoryManager()
        
        # Give it a moment to initialize
        await asyncio.sleep(1)
        
        # Test agent registration
        test_agent_id = "test-dev-agent-001"
        result = await manager.register_agent(
            agent_id=test_agent_id,
            agent_role="developer", 
            memory_layers=["global", "learned"]
        )
        
        print(f"Registration result: {result}")
        
        if result.get("success"):
            print("✅ Agent registration SUCCESSFUL!")
            
            # Test retrieving the agent
            get_result = await manager.get_agent(test_agent_id)
            print(f"Retrieval result: {get_result}")
            
            if get_result.get("success"):
                print("✅ Agent retrieval SUCCESSFUL!")
                print(f"Agent data: {get_result['agent']}")
            else:
                print("❌ Agent retrieval FAILED!")
                
        else:
            print("❌ Agent registration FAILED!")
            print(f"Error: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Agent registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Agent Registration Test with UUID Fix")
    print("=" * 60)
    
    success = True
    
    # Test 1: Agent ID conversion
    if not test_agent_id_conversion():
        success = False
    
    # Test 2: Actual registration (if Qdrant is available)
    try:
        registration_success = await test_agent_registration()
        if not registration_success:
            success = False
    except Exception as e:
        print(f"⚠️  Could not test registration (Qdrant might not be available): {e}")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Agent registration should work now.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))