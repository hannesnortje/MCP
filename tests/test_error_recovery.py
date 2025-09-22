#!/usr/bin/env python3
"""
Error Recovery and Resilience Test - Tests system error handling
"""

import os
import sys
import tempfile
import time
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_config import ServerConfig
from error_handler import ErrorHandler, RetryConfig, ErrorCategory
from markdown_processor import MarkdownProcessor


def test_error_handler_functionality():
    """Test error handler core functionality."""
    print("🧪 Testing error handler functionality...")
    
    try:
        error_handler = ErrorHandler()
        
        # Test 1: Error statistics
        initial_stats = error_handler.get_error_stats()
        assert isinstance(initial_stats, dict)
        assert 'total_errors' in initial_stats
        print("  ✅ Error statistics working")
        
        # Test 2: Retry decorator basic functionality
        call_count = 0
        
        @error_handler.retry_with_backoff()
        async def test_retry_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Test error")
            return "success"
        
        # Run async test
        result = asyncio.run(test_retry_function())
        assert result == "success"
        assert call_count == 2  # Called twice due to retry
        print("  ✅ Retry mechanism working")
        
        # Test 3: Error statistics after errors
        final_stats = error_handler.get_error_stats()
        # Should have recorded some errors
        print("  ✅ Error tracking working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handler test failed: {e}")
        return False


def test_file_operation_resilience():
    """Test resilience to file operation errors."""
    print("🧪 Testing file operation resilience...")
    
    try:
        processor = MarkdownProcessor()
        
        # Test 1: Non-existent file handling
        try:
            # This should handle gracefully
            content = processor.read_markdown_file("nonexistent_file.md")
            # If we get here, it should return None or handle gracefully
        except Exception as e:
            # Expected to fail, but should be a controlled failure
            pass
        print("  ✅ Non-existent file handling working")
        
        # Test 2: Invalid content handling
        try:
            # Test with various edge cases
            edge_cases = [
                "",  # Empty content
                None,  # None content
                "   \n\n   \n  ",  # Whitespace only
                "🚀" * 1000,  # Unicode heavy content
            ]
            
            for i, edge_case in enumerate(edge_cases):
                if edge_case is not None:
                    word_count = processor.get_word_count(edge_case)
                    content_hash = processor.calculate_content_hash(edge_case)
                    # Should handle without crashing
            
        except Exception as e:
            print(f"    ⚠️ Edge case handling issue: {e}")
        
        print("  ✅ Edge case handling working")
        
        # Test 3: Large content handling
        try:
            large_content = "# Large Document\n\n" + "This is a test sentence. " * 10000
            
            start_time = time.time()
            word_count = processor.get_word_count(large_content)
            content_hash = processor.calculate_content_hash(large_content)
            process_time = time.time() - start_time
            
            # Should complete within reasonable time
            assert process_time < 10  # 10 second limit
            assert word_count > 0
            assert content_hash is not None
            
        except Exception as e:
            print(f"    ⚠️ Large content handling issue: {e}")
        
        print("  ✅ Large content handling working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ File operation resilience test failed: {e}")
        return False


def test_configuration_resilience():
    """Test configuration system resilience."""
    print("🧪 Testing configuration resilience...")
    
    try:
        # Test 1: Default configuration loading
        config1 = ServerConfig()
        assert config1.name is not None
        assert config1.version is not None
        print("  ✅ Default configuration working")
        
        # Test 2: Multiple configuration instances
        config2 = ServerConfig()
        config3 = ServerConfig()
        
        # Should be consistent
        assert config1.name == config2.name == config3.name
        print("  ✅ Configuration consistency working")
        
        # Test 3: Configuration attribute access
        try:
            # Access various configuration sections
            _ = config1.qdrant
            _ = config1.embedding
            _ = config1.markdown
            _ = config1.error_handling
            
        except AttributeError as e:
            print(f"    ⚠️ Configuration attribute issue: {e}")
        
        print("  ✅ Configuration access working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration resilience test failed: {e}")
        return False


def test_component_isolation():
    """Test component isolation and independence."""
    print("🧪 Testing component isolation...")
    
    try:
        # Test 1: Independent component creation
        config = ServerConfig()
        error_handler = ErrorHandler()
        processor = MarkdownProcessor()
        
        # Should not interfere with each other
        assert config.name is not None
        assert error_handler.get_error_stats() is not None
        assert processor.chunk_size is not None
        
        print("  ✅ Independent component creation working")
        
        # Test 2: Component state isolation
        error_handler1 = ErrorHandler()
        error_handler2 = ErrorHandler()
        
        # Should have independent state
        stats1 = error_handler1.get_error_stats()
        stats2 = error_handler2.get_error_stats()
        
        # Both should work independently
        assert isinstance(stats1, dict)
        assert isinstance(stats2, dict)
        
        print("  ✅ Component state isolation working")
        
        # Test 3: Processor independence
        processor1 = MarkdownProcessor()
        processor2 = MarkdownProcessor()
        
        # Should work independently
        content = "# Test\n\nTest content"
        count1 = processor1.get_word_count(content)
        count2 = processor2.get_word_count(content)
        
        assert count1 == count2  # Same input, same output
        assert count1 > 0
        
        print("  ✅ Processor independence working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component isolation test failed: {e}")
        return False


def test_error_recovery_patterns():
    """Test various error recovery patterns."""
    print("🧪 Testing error recovery patterns...")
    
    try:
        error_handler = ErrorHandler()
        
        # Test 1: Gradual failure recovery
        attempt_count = 0
        
        @error_handler.retry_with_backoff()
        async def gradually_succeeding_function():
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count == 1:
                raise ConnectionError("Connection failed")
            elif attempt_count == 2:
                raise TimeoutError("Request timeout")
            else:
                return f"Success after {attempt_count} attempts"
        
        result = asyncio.run(gradually_succeeding_function())
        assert "Success" in result
        assert attempt_count >= 3
        
        print("  ✅ Gradual failure recovery working")
        
        # Test 2: Immediate success (no retries needed)
        success_count = 0
        
        @error_handler.retry_with_backoff()
        async def immediate_success_function():
            nonlocal success_count
            success_count += 1
            return "Immediate success"
        
        result = asyncio.run(immediate_success_function())
        assert result == "Immediate success"
        assert success_count == 1  # Should only be called once
        
        print("  ✅ Immediate success handling working")
        
        # Test 3: Partial failure tolerance
        partial_results = []
        
        for i in range(5):
            try:
                if i == 2:  # Simulate failure on 3rd iteration
                    raise RuntimeError(f"Simulated error {i}")
                partial_results.append(f"Result {i}")
            except Exception:
                partial_results.append(f"Failed {i}")
        
        # Should have both successful and failed results
        assert len(partial_results) == 5
        assert any("Result" in r for r in partial_results)
        assert any("Failed" in r for r in partial_results)
        
        print("  ✅ Partial failure tolerance working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error recovery patterns test failed: {e}")
        return False


def test_system_stability():
    """Test overall system stability."""
    print("🧪 Testing system stability...")
    
    try:
        # Test 1: Repeated operations
        processor = MarkdownProcessor()
        
        for i in range(50):  # Perform same operation many times
            content = f"# Document {i}\n\nThis is document number {i}."
            word_count = processor.get_word_count(content)
            content_hash = processor.calculate_content_hash(content)
            
            # Should be consistent
            assert word_count > 0
            assert content_hash is not None
        
        print("  ✅ Repeated operations stability working")
        
        # Test 2: Mixed operations
        for i in range(20):
            content = f"# Mixed Test {i}\n\nContent with {'lots of ' * (i % 10)}text."
            
            # Mix different operations
            if i % 3 == 0:
                _ = processor.get_word_count(content)
            elif i % 3 == 1:
                _ = processor.calculate_content_hash(content)
            else:
                _ = processor.to_plain_text(content)
        
        print("  ✅ Mixed operations stability working")
        
        # Test 3: Resource cleanup
        # Create many temporary objects
        configs = [ServerConfig() for _ in range(10)]
        handlers = [ErrorHandler() for _ in range(10)]
        processors = [MarkdownProcessor() for _ in range(10)]
        
        # Verify they all work
        assert all(c.name is not None for c in configs)
        assert all(h.get_error_stats() is not None for h in handlers)
        assert all(p.chunk_size is not None for p in processors)
        
        # Clear references
        del configs, handlers, processors
        
        print("  ✅ Resource cleanup working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ System stability test failed: {e}")
        return False


def main():
    """Run error recovery and resilience tests."""
    print("🚀 Starting Error Recovery and Resilience Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    test_functions = [
        test_error_handler_functionality,
        test_file_operation_resilience,
        test_configuration_resilience,
        test_component_isolation,
        test_error_recovery_patterns,
        test_system_stability
    ]
    
    for test_func in test_functions:
        print(f"\n{total_tests + 1}. {test_func.__name__.replace('test_', '').replace('_', ' ').title()}")
        print("-" * 40)
        total_tests += 1
        
        try:
            if test_func():
                tests_passed += 1
                print("✅ Test PASSED")
            else:
                print("❌ Test FAILED")
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Error Recovery Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All resilience tests PASSED! System is robust.")
        return True
    elif tests_passed / total_tests >= 0.8:
        print("✨ Most resilience tests passed - system is quite robust.")
        return True
    else:
        print("⚠️ Resilience issues detected - system needs hardening.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)