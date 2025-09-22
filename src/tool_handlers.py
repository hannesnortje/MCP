"""
Tool implementation handlers for MCP Memory Server.
Contains the actual logic for each tool, separated from MCP protocol handling.
"""

from typing import Dict, Any
import asyncio
from datetime import datetime

from .server_config import get_logger
from .markdown_processor import MarkdownProcessor

logger = get_logger("tool-handlers")


class ToolHandlers:
    """Handles the implementation of all memory management tools."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager instance."""
        self.memory_manager = memory_manager
        self.markdown_processor = MarkdownProcessor()
    
    def handle_set_agent_context(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle set_agent_context tool call."""
        agent_id = arguments.get("agent_id")
        context_type = arguments.get("context_type")
        description = arguments.get("description")
        
        self.memory_manager.set_agent_context(
            agent_id, context_type, description
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Agent context set for {agent_id}: {description}"
                }
            ]
        }

    def handle_add_to_global_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_global_memory tool call."""
        content = arguments.get("content")
        category = arguments.get("category", "general")
        importance = arguments.get("importance", 0.5)
        
        result = self.memory_manager.add_to_global_memory(
            content, category, importance
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Added to global memory: {result['message']}"
                }
            ]
        }

    def handle_add_to_learned_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_learned_memory tool call."""
        content = arguments.get("content")
        pattern_type = arguments.get("pattern_type", "insight")
        confidence = arguments.get("confidence", 0.7)
        
        result = self.memory_manager.add_to_learned_memory(
            content, pattern_type, confidence
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Added to learned memory: {result['message']}"
                }
            ]
        }

    def handle_add_to_agent_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add_to_agent_memory tool call."""
        content = arguments.get("content")
        agent_id = arguments.get("agent_id")
        memory_type = arguments.get("memory_type", "general")
        
        result = self.memory_manager.add_to_agent_memory(
            content, agent_id, memory_type
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Added to agent memory: {result['message']}"
                }
            ]
        }

    def handle_query_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query_memory tool call."""
        query = arguments.get("query")
        memory_types = arguments.get(
            "memory_types", ["global", "learned", "agent"]
        )
        limit = arguments.get("limit", 10)
        min_score = arguments.get("min_score", 0.3)
        
        results = self.memory_manager.query_memory(
            query, memory_types, limit, min_score
        )
        
        if results.get("success", False):
            memories = results.get("memories", [])
            response_text = (
                f"Found {len(memories)} relevant memories:\n\n"
            )
            
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', 'No content')
                score = memory.get('score', 0)
                mem_type = memory.get('memory_type', 'unknown')
                response_text += (
                    f"{i}. {content} "
                    f"(Score: {score:.3f}, Type: {mem_type})\n\n"
                )
        else:
            error_msg = results.get('error', 'Unknown error')
            response_text = f"Query failed: {error_msg}"
        
        return {
            "content": [{"type": "text", "text": response_text}]
        }

    def handle_compare_against_learned_memory(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle compare_against_learned_memory tool call."""
        situation = arguments.get("situation")
        comparison_type = arguments.get("comparison_type", "pattern_match")
        limit = arguments.get("limit", 5)
        
        results = self.memory_manager.compare_against_learned_memory(
            situation, comparison_type, limit
        )
        
        if results.get("success", False):
            patterns = results.get("patterns", [])
            response_text = (
                f"Found {len(patterns)} similar learned patterns:\n\n"
            )
            
            for i, pattern in enumerate(patterns, 1):
                content = pattern.get('content', 'No content')
                score = pattern.get('score', 0)
                response_text += (
                    f"{i}. {content} "
                    f"(Similarity: {score:.3f})\n\n"
                )
        else:
            error_msg = results.get('error', 'Unknown error')
            response_text = f"Comparison failed: {error_msg}"
        
        return {
            "content": [{"type": "text", "text": response_text}]
        }

    # New Markdown Processing Tools

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
                    f"\nAI Enhancement: Ready for Cursor AI integration"
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
        """Handle process_markdown_directory tool call."""
        try:
            directory = arguments.get("directory", "./")
            memory_type = arguments.get("memory_type")
            auto_suggest = arguments.get("auto_suggest", True)
            ai_enhance = arguments.get("ai_enhance", True)
            recursive = arguments.get("recursive", True)
            
            results = await self.markdown_processor.process_directory_batch(
                directory, memory_type, auto_suggest, ai_enhance, recursive
            )
            
            total_files = results['total_files']
            processed = len(results['processed_files'])
            failed = len(results['failed_files'])
            suggestions = results['memory_type_suggestions']
            
            response_text = (
                f"Directory Processing Results:\n\n"
                f"• Directory: {directory}\n"
                f"• Total files found: {total_files}\n"
                f"• Successfully processed: {processed}\n"
                f"• Failed: {failed}\n"
                f"• AI enhanced: {ai_enhance}\n\n"
            )
            
            if suggestions:
                response_text += "Memory Type Suggestions:\n"
                for mem_type, count in suggestions.items():
                    response_text += f"• {mem_type}: {count} files\n"
                response_text += "\n"
            
            if results['processed_files']:
                response_text += "Processed Files:\n"
                for file_result in results['processed_files'][:10]:  # Show first 10
                    response_text += (
                        f"• {file_result['name']} → "
                        f"{file_result['final_memory_type']}\n"
                    )
                if len(results['processed_files']) > 10:
                    response_text += f"• ... and {len(results['processed_files']) - 10} more\n"
            
            if results['failed_files']:
                response_text += "\nFailed Files:\n"
                for failed_file in results['failed_files']:
                    response_text += f"• {failed_file['name']}: {failed_file['error']}\n"
            
            return {
                "content": [{"type": "text", "text": response_text}]
            }
            
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
            response_text += f"Content: {content[:100]}{'...' if len(content) > 100 else ''}\n"
            response_text += f"Memory Type: {memory_type}\n"
            if agent_id:
                response_text += f"Agent ID: {agent_id}\n"
            response_text += f"Collection: {result.get('collection', 'unknown')}\n\n"
            
            if result.get('is_duplicate'):
                response_text += f"🔍 DUPLICATE DETECTED\n"
                response_text += f"Similarity Score: {result.get('similarity_score', 0):.3f}\n"
                response_text += f"Matched Content: {result.get('matched_content', 'N/A')}\n"
                response_text += f"Recommendation: Content already exists, consider skipping.\n"
            elif result.get('is_near_miss'):
                response_text += f"⚠️ NEAR-MISS DETECTED\n"
                response_text += f"Similarity Score: {result.get('similarity_score', 0):.3f}\n"
                response_text += f"Matched Content: {result.get('matched_content', 'N/A')}\n"
                response_text += f"Recommendation: Review for potential similarity before adding.\n"
            else:
                response_text += f"✅ NO DUPLICATE FOUND\n"
                response_text += f"Similarity Score: {result.get('similarity_score', 0):.3f}\n"
                response_text += f"Recommendation: Safe to add to memory.\n"
            
            # Add diagnostics if available
            if result.get('diagnostics') and enable_near_miss:
                diag = result['diagnostics']
                response_text += f"\nDiagnostics:\n"
                response_text += f"• Duplicate threshold: {diag.get('duplicate_threshold', 'N/A')}\n"
                response_text += f"• Near-miss threshold: {diag.get('near_miss_threshold', 'N/A')}\n"
                response_text += f"• Total matches found: {diag.get('total_matches', 0)}\n"
                
                if diag.get('top_similarities'):
                    response_text += f"• Top similarities:\n"
                    for i, sim in enumerate(diag['top_similarities'][:3]):
                        response_text += f"  {i+1}. Score: {sim.get('score', 0):.3f} - {sim.get('content_preview', 'N/A')}\n"
            
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
                         "text": f"File already processed: {file_path} (hash: {file_hash[:8]}...)"}
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
                suggestion_reason = "User specified" if memory_type else "Default to global"
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
                f"• Skipped (Duplicates): {len(chunk_results) - len(stored_chunks)}\n"
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
                
                response_text += f"{action_emoji} Chunk {result['chunk_index']}: {result['action']}"
                if "similarity_score" in result:
                    response_text += f" (similarity: {result['similarity_score']:.3f})"
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
                    response_text += f"• {file_info['path']}: {file_info['error']}\n"
            
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
            memory_type = arguments.get("memory_type")
            recursive = arguments.get("recursive", True)
            agent_id = arguments.get("agent_id")
            
            # Step 1: Discover markdown files
            discovered_files = await self.markdown_processor.scan_directory_for_markdown(
                directory, recursive=recursive
            )
            
            if not discovered_files["files"]:
                return {
                    "content": [
                        {"type": "text", 
                         "text": f"No markdown files found in {directory}"}
                    ]
                }
            
            # Step 2: Process each file through complete pipeline
            file_assignments = []
            for file_info in discovered_files["files"]:
                file_assignments.append({
                    "path": file_info["path"],
                    "memory_type": memory_type,
                    "agent_id": agent_id
                })
            
            # Use batch processing tool
            batch_result = await self.handle_batch_process_markdown_files({
                "file_assignments": file_assignments,
                "default_memory_type": memory_type
            })
            
            # Enhance response with directory context
            if not batch_result.get("isError"):
                original_text = batch_result["content"][0]["text"]
                enhanced_text = (
                    f"Directory Processing Complete: {directory}\n"
                    f"📂 Directory: {directory} ({'recursive' if recursive else 'non-recursive'})\n"
                    f"🔍 Files discovered: {len(discovered_files['files'])}\n\n"
                    f"{original_text}"
                )
                batch_result["content"][0]["text"] = enhanced_text
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Error in batch_process_directory: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", 
                     "text": f"Failed to process directory: {str(e)}"}
                ]
            }

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers."""
        if not self.memory_manager:
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": "Memory manager not available"}
                ]
            }

        try:
            # Route to appropriate handler
            handler_map = {
                "set_agent_context": self.handle_set_agent_context,
                "add_to_global_memory": self.handle_add_to_global_memory,
                "add_to_learned_memory": self.handle_add_to_learned_memory,
                "add_to_agent_memory": self.handle_add_to_agent_memory,
                "query_memory": self.handle_query_memory,
                "compare_against_learned_memory": (
                    self.handle_compare_against_learned_memory
                ),
                # New markdown processing tools
                "scan_workspace_markdown": self.handle_scan_workspace_markdown,
                "analyze_markdown_content": self.handle_analyze_markdown_content,
                "optimize_content_for_storage": self.handle_optimize_content_for_storage,
                "process_markdown_directory": self.handle_process_markdown_directory,
                # Enhanced deduplication tool
                "validate_and_deduplicate": self.handle_validate_and_deduplicate,
                # Complete ingestion pipeline tools
                "process_markdown_file": self.handle_process_markdown_file,
                "batch_process_markdown_files": self.handle_batch_process_markdown_files,
                "batch_process_directory": self.handle_batch_process_directory,
            }
            
            if tool_name in handler_map:
                handler = handler_map[tool_name]
                # Handle both sync and async methods
                if asyncio.iscoroutinefunction(handler):
                    return await handler(arguments)
                else:
                    return handler(arguments)
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Unknown tool: {tool_name}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing {tool_name}: {str(e)}"
                    }
                ]
            }
