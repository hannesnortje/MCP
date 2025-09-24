"""
Markdown processing handlers for MCP Memory Server.
Handles markdown file scanning, analysis, optimization, and batch processing.
"""

from typing import Dict, Any
from datetime import datetime

try:
    from ..server_config import get_logger
    from ..markdown_processor import MarkdownProcessor
    from ..error_handler import error_handler
except ImportError:
    # Fallback for standalone usage
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)
    
    class MockMarkdownProcessor:
        async def scan_directory_for_markdown(self, directory, recursive=True):
            return []
        def analyze_content_for_memory_type(self, content, *args, **kwargs):
            return {"suggested_memory_type": "global", "confidence": 0.5}
        def optimize_content_for_storage(self, content, *args, **kwargs):
            return {"memory_type": "global", "optimized_length": len(content)}
        def chunk_content(self, content):
            return [{"text": content}]
    
    class MockErrorHandler:
        def get_error_stats(self):
            return {"total_errors": 0}
    
    error_handler = MockErrorHandler()

logger = get_logger("markdown-processing-handlers")


class MarkdownProcessingHandlers:
    """Handles all markdown processing operations."""
    
    def __init__(self, memory_manager, markdown_processor=None):
        """Initialize with memory manager and optional markdown processor."""
        self.memory_manager = memory_manager
        self.markdown_processor = markdown_processor or MarkdownProcessor()
    
    async def handle_scan_workspace_markdown(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle scan_workspace_markdown tool call."""
        try:
            directory = arguments.get("directory", "./")
            recursive = arguments.get("recursive", True)
            
            files = await self.markdown_processor.scan_directory_for_markdown(
                directory, recursive
            )
            
            response_text = (
                f"Found {len(files)} markdown files in {directory}"
                + (" (recursive)" if recursive else "") + ":\n\n"
            )
            
            for file_info in files:
                response_text += (
                    f"• {file_info['name']} "
                    f"({file_info['size']} bytes) - {file_info['relative_path']}\n"
                )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in scan_workspace_markdown: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to scan directory: {str(e)}"}
                ]
            }

    async def handle_analyze_markdown_content(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle analyze_markdown_content tool call."""
        try:
            content = arguments.get("content", "")
            if not content:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Content parameter is required"}
                    ]
                }
            
            suggest_memory_type = arguments.get("suggest_memory_type", True)
            ai_enhance = arguments.get("ai_enhance", True)
            
            analysis = self.markdown_processor.analyze_content_for_memory_type(
                content, None, suggest_memory_type
            )
            
            response_text = (
                f"Content Analysis Results:\n\n"
                f"• Length: {analysis['content_length']} characters\n"
                f"• Words: {analysis['word_count']}\n"
                f"• Sections: {analysis['sections']}\n"
                f"• Has code blocks: {analysis['has_code_blocks']}\n"
                f"• Has links: {analysis['has_links']}\n"
                f"• Has tables: {analysis['has_tables']}\n"
            )
            
            if suggest_memory_type:
                response_text += (
                    f"\nMemory Type Suggestion:\n"
                    f"• Type: {analysis['suggested_memory_type']}\n"
                    f"• Confidence: {analysis['confidence']:.2f}\n"
                    f"• Reasoning: {analysis['reasoning']}\n"
                )
            
            if ai_enhance:
                response_text += (
                    f"\nAI Enhancement: Ready for integration"
                )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_markdown_content: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to analyze content: {str(e)}"}
                ]
            }

    async def handle_optimize_content_for_storage(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle optimize_content_for_storage tool call."""
        try:
            content = arguments.get("content", "")
            memory_type = arguments.get("memory_type", "global")
            ai_optimization = arguments.get("ai_optimization", True)
            suggested_type = arguments.get("suggested_type")
            
            if not content:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Content parameter is required"}
                    ]
                }
            
            optimization = self.markdown_processor.optimize_content_for_storage(
                content, memory_type, ai_optimization, suggested_type
            )
            
            response_text = (
                f"Content Optimization Results:\n\n"
                f"• Target memory type: {optimization['memory_type']}\n"
                f"• Original length: {optimization['original_length']}\n"
                f"• Optimized length: {optimization['optimized_length']}\n"
                f"• Optimization applied: {optimization['optimization_applied']}\n"
                f"• AI enhanced: {optimization['ai_enhanced']}\n"
            )
            
            if optimization.get('suggested_type_override'):
                response_text += (
                    f"• Note: User override of suggested type\n"
                )
            
            response_text += (
                f"\nOptimized content ready for storage in "
                f"{memory_type} memory layer."
            )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in optimize_content_for_storage: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to optimize content: {str(e)}"}
                ]
            }

    async def handle_process_markdown_directory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle process_markdown_directory tool call.
        
        Note: This function is maintained for backward compatibility.
        It delegates to batch_process_directory which properly stores content.
        """
        try:
            # Delegate to the batch_process_directory handler
            logger.info(
                f"Redirecting process_markdown_directory to "
                f"batch_process_directory: {arguments}"
            )
            return await self.handle_batch_process_directory(arguments)
        except Exception as e:
            logger.error(f"Error in process_markdown_directory: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to process directory: {str(e)}"}
                ]
            }
        
    async def handle_validate_and_deduplicate(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle validate_and_deduplicate tool call."""
        try:
            content = arguments.get("content", "")
            memory_type = arguments.get("memory_type", "global")
            agent_id = arguments.get("agent_id")
            threshold = arguments.get("threshold")
            enable_near_miss = arguments.get("enable_near_miss", True)
            
            if not content.strip():
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Content cannot be empty"}
                    ]
                }
            
            # Check for duplicates using enhanced similarity detection
            result = self.memory_manager.async_check_duplicate_with_similarity(
                content=content,
                memory_type=memory_type,
                agent_id=agent_id,
                threshold=threshold,
                enable_near_miss=enable_near_miss
            )
            
            # Format response
            response_text = "Deduplication Analysis:\n\n"
            response_text += (
                f"Content: {content[:100]}"
                f"{'...' if len(content) > 100 else ''}\n"
            )
            response_text += f"Memory Type: {memory_type}\n"
            if agent_id:
                response_text += f"Agent ID: {agent_id}\n"
            response_text += f"Collection: {result.get('collection', 'unknown')}\n\n"
            
            if result.get('is_duplicate'):
                response_text += f"🔍 DUPLICATE DETECTED\n"
                response_text += (
                    f"Similarity Score: "
                    f"{result.get('similarity_score', 0):.3f}\n"
                )
                response_text += (
                    f"Matched Content: "
                    f"{result.get('matched_content', 'N/A')}\n"
                )
                response_text += (
                    f"Recommendation: Content already exists, "
                    f"consider skipping.\n"
                )
            elif result.get('is_near_miss'):
                response_text += f"⚠️ NEAR-MISS DETECTED\n"
                response_text += (
                    f"Similarity Score: "
                    f"{result.get('similarity_score', 0):.3f}\n"
                )
                response_text += (
                    f"Matched Content: "
                    f"{result.get('matched_content', 'N/A')}\n"
                )
                response_text += (
                    f"Recommendation: Review for potential similarity "
                    f"before adding.\n"
                )
            else:
                response_text += f"✅ NO DUPLICATE FOUND\n"
                response_text += (
                    f"Similarity Score: "
                    f"{result.get('similarity_score', 0):.3f}\n"
                )
                response_text += (
                    f"Recommendation: Safe to add to memory.\n"
                )
            
            # Add diagnostics if available
            if result.get('diagnostics') and enable_near_miss:
                diag = result['diagnostics']
                response_text += f"\nDiagnostics:\n"
                response_text += (
                    f"• Duplicate threshold: "
                    f"{diag.get('duplicate_threshold', 'N/A')}\n"
                )
                response_text += (
                    f"• Near-miss threshold: "
                    f"{diag.get('near_miss_threshold', 'N/A')}\n"
                )
                response_text += (
                    f"• Total matches found: "
                    f"{diag.get('total_matches', 0)}\n"
                )
                
                if diag.get('top_similarities'):
                    response_text += f"• Top similarities:\n"
                    for i, sim in enumerate(diag['top_similarities'][:3]):
                        response_text += (
                            f"  {i+1}. Score: {sim.get('score', 0):.3f} - "
                            f"{sim.get('content_preview', 'N/A')}\n"
                        )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in validate_and_deduplicate: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to validate and deduplicate: {str(e)}"}
                ]
            }

    async def handle_process_markdown_file(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle process_markdown_file tool call - complete end-to-end pipeline."""
        try:
            file_path = arguments.get("path", "")
            memory_type = arguments.get("memory_type")
            auto_suggest = arguments.get("auto_suggest", True)
            agent_id = arguments.get("agent_id")
            
            if not file_path.strip():
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "File path cannot be empty"}
                    ]
                }
            
            # Step 1: Read and validate file
            try:
                content = await self.markdown_processor.read_file(file_path)
                if not content.strip():
                    return {
                        "isError": True,
                        "content": [
                            {"type": "text", "text": f"File is empty: {file_path}"}
                        ]
                    }
            except FileNotFoundError:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"File not found: {file_path}"}
                    ]
                }
            
            # Step 2: Check if already processed (skip if identical)
            file_hash = self.markdown_processor.calculate_content_hash(content)
            if self.memory_manager.check_file_processed(file_path, file_hash):
                return {
                    "content": [
                        {"type": "text", 
                         "text": (
                            f"File already processed: {file_path} "
                            f"(hash: {file_hash[:8]}...)"
                        )}
                    ]
                }
            
            # Step 3: Analyze content and determine memory type
            if auto_suggest and not memory_type:
                analysis = await self.markdown_processor.analyze_content_for_memory_type(
                    content, suggest_memory_type=True, ai_enhance=True
                )
                memory_type = analysis["suggested_memory_type"]
                suggestion_reason = analysis["suggestion_reasoning"]
            else:
                suggestion_reason = ("User specified" if memory_type 
                                  else "Default to global")
                memory_type = memory_type or "global"
            
            # Step 4: Optimize content for storage
            optimized_content = await self.markdown_processor.optimize_content_for_storage(
                content, memory_type, ai_optimization=True
            )
            
            # Step 5: Chunk content
            chunks = self.markdown_processor.chunk_content(optimized_content)
            
            # Step 6: Process chunks with deduplication and storage
            chunk_results = []
            stored_chunks = []
            
            for i, chunk in enumerate(chunks):
                chunk_text = chunk["text"]
                
                # Check for duplicates
                duplicate_check = self.memory_manager.async_check_duplicate_with_similarity(
                    content=chunk_text,
                    memory_type=memory_type,
                    agent_id=agent_id,
                    enable_near_miss=True
                )
                
                if duplicate_check["is_duplicate"]:
                    chunk_results.append({
                        "chunk_index": i,
                        "action": "skipped_duplicate",
                        "similarity_score": duplicate_check["similarity_score"],
                        "reason": "Content already exists in memory"
                    })
                    continue
                elif duplicate_check["is_near_miss"]:
                    chunk_results.append({
                        "chunk_index": i,
                        "action": "stored_near_miss",
                        "similarity_score": duplicate_check["similarity_score"],
                        "reason": "Similar content exists but stored anyway"
                    })
                
                # Store chunk in memory
                chunk_hash = self.memory_manager.async_add_to_memory(
                    content=chunk_text,
                    memory_type=memory_type,
                    agent_id=agent_id,
                    metadata={
                        "source_file": file_path,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_hash": file_hash,
                        "processing_timestamp": datetime.now().isoformat()
                    }
                )
                
                stored_chunks.append(chunk_hash)
                chunk_results.append({
                    "chunk_index": i,
                    "action": "stored",
                    "chunk_hash": chunk_hash,
                    "reason": "Successfully stored in memory"
                })
            
            # Step 7: Record file metadata
            processing_info = {
                "memory_type": memory_type,
                "suggestion_reason": suggestion_reason,
                "total_chunks": len(chunks),
                "stored_chunks": len(stored_chunks),
                "skipped_chunks": len(chunk_results) - len(stored_chunks),
                "agent_id": agent_id
            }
            
            self.memory_manager.add_file_metadata(
                file_path=file_path,
                file_hash=file_hash,
                chunk_ids=stored_chunks,
                processing_info=processing_info
            )
            
            # Format response
            response_text = (
                f"File Processing Complete: {file_path}\n\n"
                f"📋 Processing Summary:\n"
                f"• Memory Type: {memory_type} ({suggestion_reason})\n"
                f"• File Hash: {file_hash}\n"
                f"• Total Chunks: {len(chunks)}\n"
                f"• Stored Chunks: {len(stored_chunks)}\n"
                f"• Skipped (Duplicates): "
                f"{len(chunk_results) - len(stored_chunks)}\n"
            )
            
            if agent_id:
                response_text += f"• Agent Context: {agent_id}\n"
            
            response_text += f"\n📊 Chunk Processing Details:\n"
            for result in chunk_results:
                action_emoji = {
                    "stored": "✅",
                    "skipped_duplicate": "⏭️",
                    "stored_near_miss": "⚠️"
                }.get(result["action"], "❓")
                
                response_text += (
                    f"{action_emoji} Chunk {result['chunk_index']}: "
                    f"{result['action']}"
                )
                if "similarity_score" in result:
                    response_text += (
                        f" (similarity: {result['similarity_score']:.3f})"
                    )
                response_text += f" - {result['reason']}\n"
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in process_markdown_file: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to process file: {str(e)}"}
                ]
            }

    async def handle_batch_process_markdown_files(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle batch processing of specific markdown files."""
        try:
            file_assignments = arguments.get("file_assignments", [])
            default_memory_type = arguments.get("default_memory_type")
            
            if not file_assignments:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "No file assignments provided"}
                    ]
                }
            
            results = {
                "processed_files": [],
                "failed_files": [],
                "total_files": len(file_assignments),
                "total_chunks_stored": 0,
                "total_chunks_skipped": 0
            }
            
            for assignment in file_assignments:
                file_path = assignment.get("path", "")
                memory_type = assignment.get("memory_type", default_memory_type)
                agent_id = assignment.get("agent_id")
                
                if not file_path:
                    results["failed_files"].append({
                        "path": "unknown",
                        "error": "No file path provided in assignment"
                    })
                    continue
                
                # Process individual file
                try:
                    file_result = await self.handle_process_markdown_file({
                        "path": file_path,
                        "memory_type": memory_type,
                        "auto_suggest": memory_type is None,
                        "agent_id": agent_id
                    })
                    
                    if file_result.get("isError"):
                        results["failed_files"].append({
                            "path": file_path,
                            "error": file_result["content"][0]["text"]
                        })
                    else:
                        # Parse success result to extract metrics
                        response_text = file_result["content"][0]["text"]
                        
                        # Extract stored/skipped counts from response
                        stored_chunks = 0
                        skipped_chunks = 0
                        if "Stored Chunks:" in response_text:
                            lines = response_text.split('\n')
                            for line in lines:
                                if "Stored Chunks:" in line:
                                    stored_chunks = int(line.split(':')[1].strip())
                                elif "Skipped (Duplicates):" in line:
                                    skipped_chunks = int(line.split(':')[1].strip())
                        
                        results["processed_files"].append({
                            "path": file_path,
                            "memory_type": memory_type,
                            "stored_chunks": stored_chunks,
                            "skipped_chunks": skipped_chunks
                        })
                        
                        results["total_chunks_stored"] += stored_chunks
                        results["total_chunks_skipped"] += skipped_chunks
                        
                except Exception as e:
                    results["failed_files"].append({
                        "path": file_path,
                        "error": str(e)
                    })
            
            # Format response
            processed = len(results["processed_files"])
            failed = len(results["failed_files"])
            
            response_text = (
                f"Batch File Processing Complete\n\n"
                f"📋 Summary:\n"
                f"• Total files: {results['total_files']}\n"
                f"• Successfully processed: {processed}\n"
                f"• Failed: {failed}\n"
                f"• Total chunks stored: {results['total_chunks_stored']}\n"
                f"• Total chunks skipped: {results['total_chunks_skipped']}\n\n"
            )
            
            if processed > 0:
                response_text += "✅ Successfully Processed:\n"
                for file_info in results["processed_files"]:
                    response_text += (
                        f"• {file_info['path']} → {file_info['memory_type']} "
                        f"({file_info['stored_chunks']} stored, "
                        f"{file_info['skipped_chunks']} skipped)\n"
                    )
                response_text += "\n"
            
            if failed > 0:
                response_text += "❌ Failed Files:\n"
                for file_info in results["failed_files"]:
                    response_text += (
                        f"• {file_info['path']}: {file_info['error']}\n"
                    )
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
        except Exception as e:
            logger.error(f"Error in batch_process_markdown_files: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to batch process files: {str(e)}"}
                ]
            }

    async def handle_batch_process_directory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle complete directory processing with end-to-end pipeline."""
        try:
            directory = arguments.get("directory", "./")
            memory_type = arguments.get("memory_type", "global")
            recursive = arguments.get("recursive", True)
            agent_id = arguments.get("agent_id")
            
            # Step 1: Discover markdown files
            files = await self.markdown_processor.scan_directory_for_markdown(
                directory, recursive=recursive
            )
            
            if not files:
                return {
                    "content": [
                        {"type": "text", 
                         "text": f"No markdown files found in {directory}"}
                    ]
                }
            
            # Step 2: Process each file directly
            processed_count = 0
            error_count = 0
            stored_chunks_count = 0
            file_results = []
            
            for file_info in files:
                file_path = file_info["path"]
                try:
                    # Read file content
                    content = await self.markdown_processor.read_markdown_file(file_path)
                    
                    # Skip empty files
                    if not content or not content.strip():
                        file_results.append({
                            "path": file_path,
                            "status": "skipped",
                            "reason": "Empty file"
                        })
                        continue
                    
                    # Generate file hash for deduplication
                    import hashlib
                    file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                    
                    # Clean and optimize content
                    cleaned_content = self.markdown_processor.clean_content(content)
                    
                    # Create chunks
                    chunks = self.markdown_processor.chunk_content(cleaned_content)
                    
                    # Store each chunk in memory
                    file_chunks_stored = 0
                    for chunk in chunks:
                        chunk_text = chunk.get('content', '')
                        if not chunk_text:
                            continue
                        
                        # Store in specified memory type
                        try:
                            metadata = {
                                "source_file": file_path,
                                "chunk_index": chunk.get('chunk_index', 0),
                                "file_hash": file_hash
                            }
                            
                            if agent_id:
                                metadata["agent_id"] = agent_id
                            
                            chunk_id = self.memory_manager.async_add_to_memory(
                                content=chunk_text,
                                memory_type=memory_type,
                                agent_id=agent_id,
                                metadata=metadata
                            )
                            file_chunks_stored += 1
                        except Exception as e:
                            logger.error(
                                f"Error storing chunk from {file_path}: {e}"
                            )
                    
                    stored_chunks_count += file_chunks_stored
                    processed_count += 1
                    
                    file_results.append({
                        "path": file_path,
                        "status": "processed",
                        "chunks_stored": file_chunks_stored,
                        "memory_type": memory_type
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    error_count += 1
                    file_results.append({
                        "path": file_path,
                        "status": "error",
                        "error": str(e)
                    })
            
            # Format response
            response_text = (
                f"Directory Processing Complete: {directory}\n\n"
                f"📂 Directory: {directory} "
                f"({'recursive' if recursive else 'non-recursive'})\n"
                f"🔍 Files discovered: {len(files)}\n"
                f"✅ Successfully processed: {processed_count}\n"
                f"❌ Errors: {error_count}\n"
                f"💾 Total chunks stored: {stored_chunks_count}\n"
                f"🧠 Memory type: {memory_type}\n"
            )
            
            if agent_id:
                response_text += f"👤 Agent ID: {agent_id}\n"
            
            response_text += "\n📄 Processed Files:\n"
            for result in file_results:
                status_icon = ("✅" if result["status"] == "processed" 
                             else "❌")
                response_text += f"{status_icon} {result['path']}"
                
                if result["status"] == "processed":
                    response_text += (
                        f" ({result['chunks_stored']} chunks stored)"
                    )
                elif result["status"] == "error":
                    response_text += f" (Error: {result['error']})"
                
                response_text += "\n"
            
            return {
                "content": [
                    {"type": "text", "text": response_text}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in batch_process_directory: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to process directory: {str(e)}"}
                ]
            }