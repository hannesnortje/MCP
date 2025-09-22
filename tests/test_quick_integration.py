#!/usr/bin/env python3
"""
Quick Integration Test - Tests core system functionality
"""

import os
import sys
import tempfile
import shutil
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_config import ServerConfig
from error_handler import ErrorHandler
from markdown_processor import MarkdownProcessor


def test_configuration_system():
    """Test configuration management."""
    print("🧪 Testing configuration system...")
    
    try:
        # Test default config
        config = ServerConfig()
        assert hasattr(config, 'server'), "Config should have server section"
        assert hasattr(config, 'logging'), "Config should have logging section"
        
        # Test config dict
        test_config = {
            'server': {'name': 'test-server'},
            'logging': {'level': 'INFO'}
        }
        config2 = ServerConfig(config_dict=test_config)
        assert config2.server['name'] == 'test-server'
        
        print("✅ Configuration system working")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_error_handling():
    """Test error handling system."""
    print("🧪 Testing error handling...")
    
    try:
        error_handler = ErrorHandler()
        
        # Test statistics
        stats = error_handler.get_error_statistics()
        assert isinstance(stats, dict), "Stats should be dict"
        assert 'total_errors' in stats, "Stats should have total_errors"
        
        # Test retry decorator
        retry_count = 0
        
        @error_handler.retry_with_exponential_backoff(max_attempts=2, base_delay=0.1)
        def test_function():
            nonlocal retry_count
            retry_count += 1
            if retry_count == 1:
                raise ValueError("Test error")
            return "success"
        
        result = test_function()
        assert result == "success", "Retry should succeed"
        assert retry_count == 2, "Should retry once"
        
        print("✅ Error handling working")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_markdown_processing():
    """Test markdown processing."""
    print("🧪 Testing markdown processing...")
    
    try:
        processor = MarkdownProcessor()
        
        # Create test file
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test.md")
        
        with open(test_file, 'w') as f:
            f.write("""# Test Document

## Introduction
This is a test markdown document for integration testing.

## Key Points
- Point 1: Important information
- Point 2: Critical details
- Point 3: Essential knowledge

## Code Example
```python
def hello_world():
    print("Hello, World!")
```

## Conclusion
This document demonstrates markdown processing capabilities.
""")
        
        # Test file analysis
        analysis = processor.analyze_file(test_file)
        assert analysis is not None, "Analysis should return results"
        assert analysis['word_count'] > 0, "Should count words"
        
        # Test workspace scanning
        overview = processor.scan_workspace(temp_dir)
        assert len(overview['files']) == 1, "Should find one file"
        
        # Test content optimization
        optimization = processor.optimize_content_for_storage(
            test_file, 
            target_memory_type="global"
        )
        assert optimization is not None, "Optimization should return results"
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print("✅ Markdown processing working")
        return True
        
    except Exception as e:
        print(f"❌ Markdown processing test failed: {e}")
        return False


def test_system_integration():
    """Test system components working together."""
    print("🧪 Testing system integration...")
    
    try:
        # Initialize all components
        config = ServerConfig()
        error_handler = ErrorHandler()
        processor = MarkdownProcessor()
        
        # Test configuration across components
        assert config.server['name'] is not None, "Server should have name"
        
        # Test error handling integration
        stats_before = error_handler.get_error_statistics()
        
        # Create test scenario
        temp_dir = tempfile.mkdtemp()
        test_files = []
        
        # Create multiple test files
        for i in range(5):
            test_file = os.path.join(temp_dir, f"doc_{i}.md")
            with open(test_file, 'w') as f:
                f.write(f"""# Document {i}

This is test document number {i}.

## Content
Important information for document {i}.

## Features
- Feature A
- Feature B  
- Feature C
""")
            test_files.append(test_file)
        
        # Test batch processing
        overview = processor.scan_workspace(temp_dir)
        assert len(overview['files']) == 5, "Should find all 5 files"
        
        # Test individual file processing
        for test_file in test_files[:2]:  # Test first 2 files
            analysis = processor.analyze_file(test_file)
            assert analysis is not None, "Each file should be analyzable"
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print("✅ System integration working")
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Quick Integration Tests")
    print("=" * 50)
    
    start_time = time.time()
    
    tests = [
        test_configuration_system,
        test_error_handling,
        test_markdown_processing,
        test_system_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    duration = time.time() - start_time
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print(f"⏱️  Total time: {duration:.2f} seconds")
    
    if passed == total:
        print("🎉 All tests PASSED! Core system is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests FAILED. Review issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)