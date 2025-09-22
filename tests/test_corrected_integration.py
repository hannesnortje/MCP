#!/usr/bin/env python3
"""
Corrected Integration Test - Tests actual system functionality
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
        assert hasattr(config, 'name'), "Config should have name"
        assert hasattr(config, 'version'), "Config should have version"
        assert hasattr(config, 'qdrant'), "Config should have qdrant config"
        
        # Test config values
        assert config.name == "memory-server"
        assert config.version == "1.0.0"
        
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
        
        # Test statistics (correct method name)
        stats = error_handler.get_error_stats()
        assert isinstance(stats, dict), "Stats should be dict"
        assert 'total_errors' in stats, "Stats should have total_errors"
        
        # Test retry decorator (correct method name)
        retry_count = 0
        
        @error_handler.retry_with_backoff(max_attempts=2, base_delay=0.1)
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
        
        # Test reading markdown file
        content = processor.read_markdown_file(test_file)
        assert content is not None, "Should read file content"
        
        # Test word count
        word_count = processor.get_word_count(content)
        assert word_count > 0, "Should count words"
        
        # Test content hashing
        hash_value = processor.calculate_content_hash(content)
        assert hash_value is not None, "Should generate hash"
        
        # Test directory scanning
        files = processor.scan_directory_for_markdown(temp_dir)
        assert len(files) == 1, "Should find one file"
        
        # Test content optimization
        optimization = processor.optimize_content_for_storage(
            content, "global", ai_optimization=False  # Disable AI for testing
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
        
        # Test configuration access
        assert config.name is not None, "Server should have name"
        assert config.qdrant is not None, "Should have qdrant config"
        
        # Test error handling integration
        stats_before = error_handler.get_error_stats()
        
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
        files = processor.scan_directory_for_markdown(temp_dir)
        assert len(files) == 5, "Should find all 5 files"
        
        # Test individual file processing
        for test_file in test_files[:2]:  # Test first 2 files
            content = processor.read_markdown_file(test_file)
            assert content is not None, "Each file should be readable"
            
            word_count = processor.get_word_count(content)
            assert word_count > 0, "Each file should have word count"
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print("✅ System integration working")
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        return False


def test_performance_basic():
    """Test basic performance characteristics."""
    print("🧪 Testing performance...")
    
    try:
        processor = MarkdownProcessor()
        
        # Create larger content
        large_content = """# Large Document

## Overview
This is a larger document to test processing performance.

"""
        
        # Add multiple sections
        for i in range(20):
            large_content += f"""## Section {i}

This is section {i} with important content.

"""
        
        # Test processing time
        start_time = time.time()
        
        word_count = processor.get_word_count(large_content)
        content_hash = processor.calculate_content_hash(large_content)
        plain_text = processor.to_plain_text(large_content)
        
        processing_time = time.time() - start_time
        
        assert word_count > 100, "Should count many words"
        assert content_hash is not None, "Should generate hash"
        assert len(plain_text) > 0, "Should convert to plain text"
        assert processing_time < 5, "Should process within 5 seconds"
        
        print(f"✅ Performance test passed ({processing_time:.2f}s)")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Corrected Integration Tests")
    print("=" * 50)
    
    start_time = time.time()
    
    tests = [
        test_configuration_system,
        test_error_handling,
        test_markdown_processing,
        test_system_integration,
        test_performance_basic
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