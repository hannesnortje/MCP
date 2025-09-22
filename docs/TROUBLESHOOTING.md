# MCP Memory Server - Troubleshooting Guide

## Table of Contents
1. [Common Issues](#common-issues)
2. [Configuration Problems](#configuration-problems)
3. [Performance Issues](#performance-issues)
4. [Error Handling and Recovery](#error-handling-and-recovery)
5. [Health Monitoring](#health-monitoring)
6. [Debugging Techniques](#debugging-techniques)
7. [FAQ](#faq)

## Common Issues

### Qdrant Connection Issues

**Problem**: Connection refused or timeout errors
```
❌ Failed to initialize Qdrant: ConnectionError: [Errno 111] Connection refused
```

**Solutions**:
1. **Check if Qdrant is running**:
   ```bash
   curl http://localhost:6333/health
   # Should return: {"status":"ok"}
   ```

2. **Start Qdrant with Docker**:
   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage \
     qdrant/qdrant:latest
   ```

3. **Check port availability**:
   ```bash
   netstat -ln | grep 6333
   lsof -i :6333
   ```

4. **Verify configuration**:
   - Check `QDRANT_HOST` and `QDRANT_PORT` environment variables
   - Ensure no firewall blocking the connection
   - For remote Qdrant, verify API key is correct

### Embedding Model Issues

**Problem**: Model download or loading failures
```
❌ Failed to load embedding model: HTTPError 403
```

**Solutions**:
1. **Check internet connection** (required for first download)
2. **Try alternative models**:
   ```bash
   export EMBEDDING_MODEL="all-mpnet-base-v2"
   # Or for faster, smaller model:
   export EMBEDDING_MODEL="all-MiniLM-L6-v2"
   ```
3. **Clear model cache** if corrupted:
   ```bash
   rm -rf ~/.cache/torch/sentence_transformers/
   ```
4. **Check disk space** (models can be 400MB+):
   ```bash
   df -h ~/.cache/
   ```

### Memory/Performance Issues

**Problem**: High memory usage or slow responses
```
⚠️ System running slowly, embeddings taking too long
```

**Solutions**:
1. **Monitor system resources**:
   ```bash
   # Check memory usage
   free -h
   
   # Check CPU usage
   top -p $(pgrep -f memory_server)
   ```

2. **Optimize configuration**:
   ```yaml
   # In config.yaml
   embedding:
     model_name: "all-MiniLM-L6-v2"  # Faster, smaller model
     device: "cpu"  # Use "cuda" if you have GPU
   
   markdown:
     chunk_size: 500  # Reduce for lower memory usage
     chunk_overlap: 100
   
   deduplication:
     similarity_threshold: 0.9  # Higher = fewer comparisons
   ```

3. **Batch processing optimization**:
   ```bash
   # Process files in smaller batches
   export MAX_BATCH_SIZE=10
   ```

## Configuration Problems

### YAML Configuration Issues

**Problem**: Configuration file not loading or invalid format
```
❌ Failed to load config from config.yaml: yaml.scanner.ScannerError
```

**Solutions**:
1. **Validate YAML syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **Check indentation** (use spaces, not tabs):
   ```yaml
   # Correct:
   server:
     name: "memory-server"
     version: "1.0.0"
   
   # Incorrect (mixed tabs/spaces):
   server:
   	name: "memory-server"
       version: "1.0.0"
   ```

3. **Use the example configuration**:
   ```bash
   cp config.example.yaml config.yaml
   # Then edit as needed
   ```

### Environment Variable Issues

**Problem**: Environment variables not being read
```
⚠️ Using default configuration, environment variables not found
```

**Solutions**:
1. **Check variable names** (case sensitive):
   ```bash
   # Correct:
   export QDRANT_HOST=localhost
   
   # Incorrect:
   export qdrant_host=localhost
   ```

2. **Verify variables are set**:
   ```bash
   env | grep QDRANT
   env | grep EMBEDDING
   ```

3. **Use .env file** for development:
   ```bash
   # Create .env file
   echo "QDRANT_HOST=localhost" > .env
   echo "QDRANT_PORT=6333" >> .env
   echo "LOG_LEVEL=DEBUG" >> .env
   ```

## Performance Issues

### Slow Query Performance

**Problem**: Memory queries taking too long

**Diagnostic Steps**:
1. **Check system health**:
   ```json
   {
     "tool": "system_health",
     "arguments": {}
   }
   ```

2. **Monitor query patterns**:
   - Enable debug logging: `LOG_LEVEL=DEBUG`
   - Check for expensive similarity searches
   - Look for large result sets

**Optimization Strategies**:
1. **Tune similarity thresholds**:
   ```yaml
   deduplication:
     similarity_threshold: 0.85  # Higher = faster, fewer results
     near_miss_threshold: 0.80
   ```

2. **Optimize query parameters**:
   ```json
   {
     "tool": "query_memory",
     "arguments": {
       "query": "specific search terms",
       "memory_type": "global",  // Search specific type, not "all"
       "max_results": 5  // Reduce result set size
     }
   }
   ```

3. **Use GPU acceleration** (if available):
   ```yaml
   embedding:
     device: "cuda"  # or "mps" for Apple Silicon
   ```

### Memory Usage Optimization

**Problem**: High RAM usage from embeddings or large documents

**Solutions**:
1. **Reduce chunk size**:
   ```yaml
   markdown:
     chunk_size: 500  # Default is 900
     chunk_overlap: 50  # Default is 200
   ```

2. **Implement document size limits**:
   ```bash
   # Skip very large files (>100KB)
   find . -name "*.md" -size +100k
   ```

3. **Regular collection cleanup**:
   ```bash
   # Remove old or duplicate entries periodically
   # (Implementation depends on your use case)
   ```

## Error Handling and Recovery

### Automatic Recovery Features

The system includes automatic retry logic for common failures:

1. **Qdrant Connection Recovery**:
   - Automatic reconnection attempts with exponential backoff
   - Docker container restart if needed
   - Circuit breaker to prevent cascading failures

2. **Embedding Model Recovery**:
   - Model reinitialization on failures
   - Fallback to CPU if GPU fails
   - Retry logic for transient network errors

3. **Network Error Recovery**:
   - Automatic retries for timeout errors
   - Connection pooling and keepalive
   - Graceful degradation when services unavailable

### Manual Recovery Procedures

**Reset Collections** (destructive - will lose data):
```bash
# Stop the server
pkill -f memory_server

# Remove Qdrant data
rm -rf ./qdrant_storage/*

# Restart Qdrant
docker restart qdrant

# Restart the server
poetry run python memory_server.py
```

**Clear Model Cache**:
```bash
rm -rf ~/.cache/torch/sentence_transformers/
rm -rf ~/.cache/huggingface/
```

**Reset Configuration**:
```bash
# Backup current config
mv config.yaml config.yaml.backup

# Use default configuration
cp config.example.yaml config.yaml
```

## Health Monitoring

### System Health Check

Use the built-in health monitoring tool:

```json
{
  "tool": "system_health",
  "arguments": {}
}
```

**Expected Output**:
```
# System Health Report

**Status:** ✅ All systems operational
**Timestamp:** 2025-01-20T10:30:45.123456

## Component Status

### Memory Manager
- **Available:** ✅
- **Initialized:** ✅

### Components
- **Qdrant:** ✅ healthy
- **Embedding Model:** ✅ healthy
- **Markdown Processor:** ✅

## Error Statistics
- **Total Errors:** 0
- **Recovery Attempts:** 0
- **Successful Recoveries:** 0
```

### Monitoring Metrics

**Key metrics to monitor**:
1. **Response times**: Query latency should be <2s for most operations
2. **Error rates**: Should be <1% for production workloads
3. **Memory usage**: Monitor RAM usage growth over time
4. **Collection sizes**: Track number of vectors per collection

**Alerting thresholds**:
- Response time > 5 seconds: Warning
- Error rate > 5%: Critical
- Memory usage > 80%: Warning
- Disk space < 1GB: Critical

## Debugging Techniques

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
poetry run python memory_server.py
```

### Inspect Qdrant Collections

```bash
# List all collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/global_memory

# Count vectors in collection
curl http://localhost:6333/collections/global_memory/points/count
```

### Test Embeddings

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("test text")
print(f"Embedding dimension: {len(embedding)}")
print(f"Sample values: {embedding[:5]}")
```

### Check MCP Communication

```bash
# Test MCP protocol manually
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | poetry run python memory_server.py
```

## FAQ

### Q: How do I change the embedding model?

A: Update your configuration:
```yaml
embedding:
  model_name: "all-mpnet-base-v2"  # Larger, more accurate
  # or
  model_name: "all-MiniLM-L6-v2"  # Smaller, faster
```

The server will automatically download the new model on first use.

### Q: Can I run multiple instances?

A: Yes, but each instance needs:
- Unique Qdrant port or separate Qdrant instance
- Separate collection names or database
- Different working directories to avoid conflicts

### Q: How do I backup my data?

A: Backup the Qdrant storage directory:
```bash
# Stop the server first
docker stop qdrant

# Backup
tar -czf qdrant_backup_$(date +%Y%m%d).tar.gz qdrant_storage/

# Restart
docker start qdrant
```

### Q: What's the maximum document size?

A: Practical limits:
- Single document: ~1MB markdown file
- Total collection: Limited by available RAM and disk space
- Chunk size: Configurable, default 900 tokens (~3-4KB text)

### Q: How do I migrate to a new server?

A: 1. Backup Qdrant data (see above)
2. Copy configuration files
3. Install dependencies on new server
4. Restore Qdrant data
5. Update MCP client configuration with new server details

### Q: Can I use a different vector database?

A: Currently only Qdrant is supported, but the architecture allows for other backends. The `QdrantMemoryManager` class would need to be replaced with an implementation for your preferred database.

## Getting Help

If you can't resolve the issue:

1. **Check the logs** with debug level enabled
2. **Run system health check** to identify failing components
3. **Search existing issues** in the repository
4. **Create a new issue** with:
   - System health output
   - Configuration files (remove sensitive data)
   - Error logs with debug level
   - Steps to reproduce the problem

## Emergency Procedures

### Complete System Reset

**⚠️ WARNING: This will delete all stored memories**

```bash
# 1. Stop all services
pkill -f memory_server
docker stop qdrant

# 2. Remove all data
rm -rf qdrant_storage/
rm -rf ~/.cache/torch/sentence_transformers/

# 3. Reset configuration
cp config.example.yaml config.yaml

# 4. Restart services
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant:latest &
sleep 10
poetry run python memory_server.py
```

### Recovery from Corruption

```bash
# 1. Backup corrupted data (for analysis)
cp -r qdrant_storage qdrant_storage.corrupted.$(date +%Y%m%d)

# 2. Check for recoverable collections
curl http://localhost:6333/collections

# 3. If partial corruption, export good collections:
curl -X POST http://localhost:6333/collections/global_memory/points/scroll \
  -H "Content-Type: application/json" \
  -d '{"limit": 10000}' > global_memory_backup.json

# 4. Fresh start with selective restore
# (Implementation depends on specific corruption pattern)
```