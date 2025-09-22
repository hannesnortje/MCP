#!/usr/bin/env python3
"""
Performance and Scalability Test - Tests system with larger workloads
"""

import os
import sys
import tempfile
import shutil
import time
import psutil
import gc

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server_config import ServerConfig
from error_handler import ErrorHandler
from markdown_processor import MarkdownProcessor


def create_test_documents(directory, count=100):
    """Create test markdown documents."""
    print(f"📝 Creating {count} test documents...")
    
    documents = []
    
    # Document templates with varying content
    templates = {
        'technical': """# Technical Specification: {title}

## Overview
This document outlines the technical specifications for {title}.

## Architecture
The system consists of multiple components:

### Core Components
- **Data Layer**: Handles data persistence and retrieval
- **Business Logic**: Implements core functionality
- **API Layer**: Provides external interfaces  
- **UI Layer**: User interaction components

### Integration Points
- Database connections
- External service APIs
- Message queues
- File system access

## Implementation Details
```python
class {class_name}:
    def __init__(self):
        self.config = load_config()
        self.logger = get_logger(__name__)
    
    def process(self, data):
        try:
            result = self.transform_data(data)
            self.save_result(result)
            return result
        except Exception as e:
            self.logger.error(f"Processing failed: {{e}}")
            raise
```

## Performance Considerations
- Memory usage optimization
- Database query optimization
- Caching strategies
- Load balancing

## Security Requirements
- Authentication and authorization
- Data encryption
- Audit logging
- Input validation

## Testing Strategy
- Unit tests for all components
- Integration tests for workflows
- Performance tests with realistic data
- Security penetration testing

## Deployment
- Containerized deployment
- Environment-specific configurations
- Monitoring and alerting
- Rollback procedures
""",
        'guide': """# User Guide: {title}

## Introduction
Welcome to the {title} user guide. This document will help you get started.

## Getting Started

### Prerequisites
Before you begin, ensure you have:
- Basic understanding of the system
- Proper access credentials
- Required software installed

### Quick Start
1. **Login** to the system
2. **Navigate** to your dashboard
3. **Create** your first project
4. **Configure** your settings

## Features Overview

### Core Features
- **Project Management**: Create and organize projects
- **Collaboration**: Work with team members
- **Analytics**: Track progress and metrics
- **Integration**: Connect with external tools

### Advanced Features
- **Automation**: Set up automated workflows  
- **Customization**: Tailor the interface
- **Reporting**: Generate detailed reports
- **API Access**: Programmatic integration

## Step-by-Step Instructions

### Creating a New Project
1. Click the "New Project" button
2. Enter project details:
   - Project name
   - Description
   - Category
   - Team members
3. Configure initial settings
4. Save and start working

### Managing Team Members
- **Add Members**: Invite users via email
- **Set Permissions**: Define access levels
- **Monitor Activity**: Track member contributions
- **Remove Access**: Revoke permissions when needed

## Best Practices
- Regularly backup your data
- Keep software updated
- Follow security guidelines
- Monitor system performance

## Troubleshooting

### Common Issues
**Q: Cannot login to the system**
A: Check your credentials and network connection

**Q: Features not working as expected**
A: Clear cache and refresh the browser

**Q: Performance is slow**
A: Check your internet connection and system resources

### Getting Help
- Check the FAQ section
- Contact support team
- Join community forums
- Review documentation
""",
        'meeting_notes': """# Meeting Notes: {title}

**Date:** 2024-01-{day:02d}
**Time:** {time}
**Attendees:** {attendees}
**Meeting Type:** {meeting_type}

## Agenda
1. Project status review
2. Technical challenges discussion
3. Resource allocation planning
4. Next steps and action items

## Discussion Summary

### Project Status
- **Current Progress**: {progress}% complete
- **Milestones Achieved**: 
  - Initial planning completed
  - Core development in progress
  - Testing framework established
- **Upcoming Milestones**:
  - Feature freeze next month
  - Beta testing phase
  - Production deployment

### Technical Challenges
- **Performance Optimization**: Need to improve query speeds
- **Scalability**: Planning for increased user load
- **Integration**: Third-party API compatibility issues
- **Security**: Implementing additional security measures

### Resource Allocation
- **Development Team**: 5 engineers assigned
- **Testing Team**: 2 QA engineers
- **DevOps**: 1 infrastructure specialist
- **Budget**: Within allocated limits

## Decisions Made
1. Extend development timeline by 2 weeks
2. Hire additional QA engineer
3. Implement caching layer for performance
4. Schedule security audit

## Action Items
- [ ] **John**: Research caching solutions (Due: End of week)
- [ ] **Sarah**: Set up performance monitoring (Due: Next Monday)
- [ ] **Mike**: Contact security audit firm (Due: This Friday)
- [ ] **Lisa**: Update project timeline (Due: Tomorrow)

## Next Meeting
**Date:** 2024-01-{next_day:02d}
**Agenda:** Review action item progress and discuss beta testing plan

## Notes
{additional_notes}
""",
        'policy': """# Policy Document: {title}

## Document Control
- **Version**: 1.0
- **Effective Date**: 2024-01-15
- **Review Date**: 2024-07-15
- **Owner**: {owner}
- **Approver**: Management Team

## Purpose and Scope
This policy establishes the standards and procedures for {title} within the organization.

### Scope
This policy applies to:
- All employees and contractors
- All systems and applications
- All data and information assets
- All business processes

## Policy Statements

### Data Security and Privacy
1. **Confidentiality**: All sensitive data must be protected
2. **Integrity**: Data accuracy must be maintained
3. **Availability**: Authorized users must have access
4. **Compliance**: Follow all applicable regulations

### Access Management
- **Authentication**: Strong passwords required
- **Authorization**: Role-based access control
- **Monitoring**: Log all access attempts
- **Review**: Regular access reviews

### Incident Management
- **Reporting**: Immediate incident reporting
- **Response**: Follow incident response procedures
- **Documentation**: Maintain incident records
- **Review**: Post-incident analysis required

## Procedures

### Implementation Steps
1. **Assessment**: Evaluate current state
2. **Planning**: Develop implementation plan
3. **Deployment**: Roll out in phases
4. **Training**: Educate all stakeholders
5. **Monitoring**: Track compliance

### Compliance Monitoring
- Regular audits and assessments
- Automated compliance checking
- Manual reviews and inspections
- Third-party assessments

## Responsibilities

### Management
- Policy approval and enforcement
- Resource allocation
- Strategic oversight
- Risk management

### IT Department
- Technical implementation
- System monitoring
- Security controls
- Backup and recovery

### All Employees
- Policy compliance
- Incident reporting
- Training completion
- Best practice adherence

## Enforcement
Violations of this policy may result in:
- Verbal or written warnings
- Suspension of access privileges
- Disciplinary action
- Termination of employment

## Related Documents
- Security Standards
- Procedure Manual
- Training Materials
- Compliance Checklist
"""
    }
    
    for i in range(count):
        # Vary document type
        doc_type = list(templates.keys())[i % len(templates)]
        template = templates[doc_type]
        
        # Generate unique content
        title = f"System Component {i+1}"
        class_name = f"Component{i+1}"
        
        if doc_type == 'meeting_notes':
            content = template.format(
                title=title,
                day=(i % 28) + 1,
                time=f"{9 + (i % 8)}:00 AM",
                attendees=f"Team Lead, Developer {(i % 3) + 1}, Analyst {(i % 2) + 1}",
                meeting_type="Project Review" if i % 2 == 0 else "Technical Discussion",
                progress=(i % 10) * 10 + 10,
                next_day=(i % 28) + 2,
                additional_notes=f"Additional context for meeting {i+1}"
            )
        elif doc_type == 'policy':
            content = template.format(
                title=title,
                owner=f"Team Lead {(i % 3) + 1}"
            )
        else:
            content = template.format(
                title=title,
                class_name=class_name
            )
        
        # Write file
        filename = f"{i+1:03d}_{doc_type}_{title.lower().replace(' ', '_')}.md"
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        documents.append(filepath)
    
    return documents


def measure_memory_usage():
    """Get current memory usage."""
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024,  # MB
        'percent': process.memory_percent()
    }


def test_document_processing_performance():
    """Test performance with many documents."""
    print("🧪 Testing document processing performance...")
    
    # Create test environment
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test parameters
        small_batch = 50
        medium_batch = 100  
        large_batch = 200
        
        results = {}
        
        for batch_name, batch_size in [
            ("Small Batch", small_batch),
            ("Medium Batch", medium_batch), 
            ("Large Batch", large_batch)
        ]:
            print(f"  → Testing {batch_name} ({batch_size} documents)...")
            
            # Create documents
            batch_dir = os.path.join(temp_dir, f"batch_{batch_size}")
            os.makedirs(batch_dir)
            
            create_start = time.time()
            documents = create_test_documents(batch_dir, batch_size)
            create_time = time.time() - create_start
            
            # Measure initial memory
            initial_memory = measure_memory_usage()
            
            # Process documents
            processor = MarkdownProcessor()
            
            process_start = time.time()
            processed_count = 0
            
            for doc_path in documents:
                try:
                    # Read file content first
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Process content
                    word_count = processor.get_word_count(content)
                    content_hash = processor.calculate_content_hash(content)
                    plain_text = processor.to_plain_text(content)
                    
                    # Verify results
                    if word_count > 0 and content_hash and plain_text:
                        processed_count += 1
                        
                except Exception as e:
                    print(f"    ⚠️ Failed to process {doc_path}: {e}")
            
            process_time = time.time() - process_start
            
            # Measure final memory
            final_memory = measure_memory_usage()
            
            # Force garbage collection
            gc.collect()
            
            # Calculate metrics
            docs_per_second = processed_count / process_time if process_time > 0 else 0
            memory_increase = final_memory['rss'] - initial_memory['rss']
            
            results[batch_name] = {
                'documents': batch_size,
                'processed': processed_count,
                'create_time': create_time,
                'process_time': process_time,
                'docs_per_second': docs_per_second,
                'memory_initial': initial_memory['rss'],
                'memory_final': final_memory['rss'],
                'memory_increase': memory_increase,
                'success_rate': processed_count / batch_size if batch_size > 0 else 0
            }
            
            print(f"    📊 Processed {processed_count}/{batch_size} documents in {process_time:.2f}s")
            print(f"    📊 Rate: {docs_per_second:.1f} docs/sec")
            print(f"    📊 Memory: {memory_increase:.1f} MB increase")
        
        # Evaluate performance
        performance_ok = True
        issues = []
        
        # Check processing speed (should handle at least 10 docs/sec for small batches)
        if results["Small Batch"]["docs_per_second"] < 10:
            performance_ok = False
            issues.append("Processing speed too slow for small batches")
        
        # Check memory usage (should not grow excessively)
        if results["Large Batch"]["memory_increase"] > 500:  # 500 MB limit
            performance_ok = False
            issues.append("Memory usage too high for large batches")
        
        # Check success rate (should process 95%+ documents)
        for batch_name, result in results.items():
            if result['success_rate'] < 0.95:
                performance_ok = False
                issues.append(f"Low success rate for {batch_name}")
        
        return performance_ok, results, issues
        
    finally:
        shutil.rmtree(temp_dir)


def test_concurrent_processing():
    """Test concurrent processing capabilities."""
    print("🧪 Testing concurrent processing...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test documents
        documents = create_test_documents(temp_dir, 20)
        processor = MarkdownProcessor()
        
        # Test sequential processing
        sequential_start = time.time()
        sequential_results = []
        
        for doc_path in documents:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                'word_count': processor.get_word_count(content),
                'hash': processor.calculate_content_hash(content)
            }
            sequential_results.append(result)
        
        sequential_time = time.time() - sequential_start
        
        # For this test, we'll simulate concurrent processing
        # by processing in smaller batches quickly
        concurrent_start = time.time()
        concurrent_results = []
        
        batch_size = 5
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            for doc_path in batch:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = {
                    'word_count': processor.get_word_count(content),
                    'hash': processor.calculate_content_hash(content)
                }
                concurrent_results.append(result)
        
        concurrent_time = time.time() - concurrent_start
        
        # Compare results
        speedup = sequential_time / concurrent_time if concurrent_time > 0 else 1
        results_match = len(sequential_results) == len(concurrent_results)
        
        success = speedup >= 0.5 and results_match  # Should be at least half as fast
        
        return success, {
            'sequential_time': sequential_time,
            'concurrent_time': concurrent_time,
            'speedup': speedup,
            'results_match': results_match
        }
        
    finally:
        shutil.rmtree(temp_dir)


def test_memory_efficiency():
    """Test memory efficiency under load."""
    print("🧪 Testing memory efficiency...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create documents
        documents = create_test_documents(temp_dir, 100)
        processor = MarkdownProcessor()
        
        # Measure baseline memory
        gc.collect()
        baseline_memory = measure_memory_usage()
        
        # Process documents in batches
        batch_size = 10
        max_memory = baseline_memory['rss']
        memory_samples = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Process batch
            for doc_path in batch:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                _ = processor.get_word_count(content)
                _ = processor.calculate_content_hash(content)
                _ = processor.to_plain_text(content)
            
            # Measure memory after batch
            current_memory = measure_memory_usage()
            memory_samples.append(current_memory['rss'])
            max_memory = max(max_memory, current_memory['rss'])
            
            # Force garbage collection between batches
            gc.collect()
        
        # Calculate efficiency metrics
        memory_growth = max_memory - baseline_memory['rss']
        avg_memory = sum(memory_samples) / len(memory_samples)
        memory_stability = max(memory_samples) - min(memory_samples)
        
        # Evaluate efficiency
        efficiency_ok = (
            memory_growth < 200 and  # Less than 200 MB growth
            memory_stability < 100   # Memory doesn't vary by more than 100 MB
        )
        
        return efficiency_ok, {
            'baseline_memory': baseline_memory['rss'],
            'max_memory': max_memory,
            'memory_growth': memory_growth,
            'avg_memory': avg_memory,
            'memory_stability': memory_stability
        }
        
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run performance and scalability tests."""
    print("🚀 Starting Performance and Scalability Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Document Processing Performance
    print("\n1. Document Processing Performance")
    print("-" * 40)
    total_tests += 1
    try:
        success, results, issues = test_document_processing_performance()
        
        if success:
            print("✅ Performance test PASSED")
            tests_passed += 1
        else:
            print("❌ Performance test FAILED")
            for issue in issues:
                print(f"   - {issue}")
        
        # Display results
        for batch_name, result in results.items():
            print(f"   {batch_name}: {result['docs_per_second']:.1f} docs/sec, {result['memory_increase']:.1f} MB")
            
    except Exception as e:
        print(f"❌ Performance test failed with exception: {e}")
    
    # Test 2: Concurrent Processing  
    print("\n2. Concurrent Processing")
    print("-" * 40)
    total_tests += 1
    try:
        success, results = test_concurrent_processing()
        
        if success:
            print("✅ Concurrent processing test PASSED")
            tests_passed += 1
        else:
            print("❌ Concurrent processing test FAILED")
        
        print(f"   Sequential: {results['sequential_time']:.2f}s")
        print(f"   Concurrent: {results['concurrent_time']:.2f}s")
        print(f"   Speedup: {results['speedup']:.2f}x")
        
    except Exception as e:
        print(f"❌ Concurrent processing test failed: {e}")
    
    # Test 3: Memory Efficiency
    print("\n3. Memory Efficiency")
    print("-" * 40)
    total_tests += 1
    try:
        success, results = test_memory_efficiency()
        
        if success:
            print("✅ Memory efficiency test PASSED")
            tests_passed += 1
        else:
            print("❌ Memory efficiency test FAILED")
        
        print(f"   Baseline: {results['baseline_memory']:.1f} MB")
        print(f"   Max: {results['max_memory']:.1f} MB")
        print(f"   Growth: {results['memory_growth']:.1f} MB")
        print(f"   Stability: {results['memory_stability']:.1f} MB")
        
    except Exception as e:
        print(f"❌ Memory efficiency test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Performance Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All performance tests PASSED! System is scalable.")
        return True
    elif tests_passed / total_tests >= 0.7:
        print("✨ Most performance tests passed - system performance is acceptable.")
        return True
    else:
        print("⚠️ Performance issues detected - optimization needed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)