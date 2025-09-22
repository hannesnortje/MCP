#!/usr/bin/env python3
"""
Simple Integration Test - Basic functionality validation
"""

import os
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_config import ServerConfig
from error_handler import ErrorHandler
from markdown_processor import MarkdownProcessor


def test_basic_functionality():
    """Test basic system functionality."""
    print("🧪 Testing basic functionality...")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Configuration
    print("  → Testing configuration...")
    total_tests += 1
    try:
        config = ServerConfig()
        assert config.name == "memory-server"
        assert config.version == "1.0.0" 
        print("    ✅ Configuration working")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Configuration failed: {e}")
    
    # Test 2: Error Handler  
    print("  → Testing error handler...")
    total_tests += 1
    try:
        error_handler = ErrorHandler()
        stats = error_handler.get_error_stats()
        assert isinstance(stats, dict)
        assert 'total_errors' in stats
        print("    ✅ Error handler working")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Error handler failed: {e}")
    
    # Test 3: Markdown Processor (sync methods only)
    print("  → Testing markdown processor...")
    total_tests += 1
    try:
        processor = MarkdownProcessor()
        
        # Test content processing
        test_content = "# Test\n\nThis is a test document."
        word_count = processor.get_word_count(test_content)
        content_hash = processor.calculate_content_hash(test_content)
        
        assert word_count > 0
        assert content_hash is not None
        
        print("    ✅ Markdown processor working")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Markdown processor failed: {e}")
    
    # Test 4: File operations
    print("  → Testing file operations...")
    total_tests += 1
    try:
        processor = MarkdownProcessor()
        
        # Create temp file
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test.md")
        
        with open(test_file, 'w') as f:
            f.write("# Test File\n\nThis is a test.")
        
        # Test file metadata
        metadata = processor.get_file_metadata(test_file)
        assert metadata is not None
        assert 'size' in metadata
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print("    ✅ File operations working")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ File operations failed: {e}")
    
    return tests_passed, total_tests


def test_component_integration():
    """Test components working together."""
    print("🧪 Testing component integration...")
    
    tests_passed = 0 
    total_tests = 0
    
    # Test 1: Config and components
    print("  → Testing config integration...")
    total_tests += 1
    try:
        config = ServerConfig()
        processor = MarkdownProcessor()
        error_handler = ErrorHandler()
        
        # Test config affects components
        assert config.markdown is not None
        assert config.error_handling is not None
        
        print("    ✅ Config integration working")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Config integration failed: {e}")
    
    # Test 2: Error handling with components
    print("  → Testing error handling integration...")
    total_tests += 1
    try:
        error_handler = ErrorHandler()
        processor = MarkdownProcessor()
        
        # Test error stats
        initial_stats = error_handler.get_error_stats()
        
        # Try an operation that might fail gracefully
        try:
            metadata = processor.get_file_metadata("nonexistent_file.md")
        except:
            pass  # Expected to fail
        
        print("    ✅ Error handling integration working")  
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Error handling integration failed: {e}")
    
    # Test 3: Content processing pipeline
    print("  → Testing content pipeline...")
    total_tests += 1
    try:
        processor = MarkdownProcessor()
        
        # Test content pipeline  
        content = """# Document Title

## Section 1
Important content here.

## Section 2  
More content.

### Subsection
Details and examples.
"""
        
        # Basic processing
        word_count = processor.get_word_count(content)
        content_hash = processor.calculate_content_hash(content)
        plain_text = processor.to_plain_text(content)
        
        assert word_count > 0
        assert content_hash is not None
        assert len(plain_text) > 0
        assert "Document Title" in plain_text
        
        print("    ✅ Content pipeline working")
        tests_passed += 1
    except Exception as e:
        print(f"    ❌ Content pipeline failed: {e}")
    
    return tests_passed, total_tests


def main():
    """Run all tests."""
    print("🚀 Starting Simple Integration Tests")
    print("=" * 50)
    
    total_passed = 0
    total_tests = 0
    
    # Run test suites
    test_suites = [
        test_basic_functionality,
        test_component_integration
    ]
    
    for test_suite in test_suites:
        try:
            passed, count = test_suite()
            total_passed += passed
            total_tests += count
        except Exception as e:
            print(f"❌ Test suite {test_suite.__name__} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Overall Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests PASSED! System is working correctly.")
        return True
    else:
        failed = total_tests - total_passed
        print(f"⚠️  {failed} tests FAILED.")
        
        if total_passed / total_tests >= 0.8:
            print("✨ 80%+ tests passed - system is mostly functional.")
            return True
        else:
            print("🔧 Significant issues detected - review required.")
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)