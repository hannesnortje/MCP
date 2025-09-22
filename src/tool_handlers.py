"""
Tool implementation handlers for MCP Memory Server.
Contains the actual logic for each tool, separated from MCP protocol handling.
Enhanced with health monitoring and diagnostic capabilities.
"""

from typing import Dict, Any
import asyncio
from datetime import datetime

from .server_config import get_logger
from .markdown_processor import MarkdownProcessor
from .policy_processor import PolicyProcessor
from .error_handler import error_handler

logger = get_logger("tool-handlers")


class ToolHandlers:
    """Handles the implementation of all memory management tools."""
    
    def __init__(self, memory_manager):
        """Initialize with a memory manager instance."""
        self.memory_manager = memory_manager
        self.markdown_processor = MarkdownProcessor()
        self.policy_processor = PolicyProcessor()
    
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

    # Agent Management Tools

    async def handle_initialize_new_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a new agent with role and memory layer configuration."""
        try:
            agent_id = arguments.get("agent_id")
            agent_role = arguments.get("agent_role", "general")
            memory_layers = arguments.get("memory_layers", ["global", "learned"])
            
            if not agent_id:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id is required"}
                    ]
                }

            # Register the agent
            result = await self.memory_manager.register_agent(
                agent_id=agent_id,
                agent_role=agent_role,
                memory_layers=memory_layers
            )

            if result["success"]:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"✅ Agent '{agent_id}' initialized successfully"
                                f"\nRole: {agent_role}"
                                f"\nMemory layers: {', '.join(memory_layers)}"
                            )
                        }
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error initializing agent: {str(e)}"}
                ]
            }

    async def handle_configure_agent_permissions(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure agent permissions for memory layer access."""
        try:
            agent_id = arguments.get("agent_id")
            permissions = arguments.get("permissions", {})
            
            if not agent_id:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id is required"}
                    ]
                }

            # Update agent permissions
            result = await self.memory_manager.update_agent_permissions(
                agent_id=agent_id,
                permissions=permissions
            )

            if result["success"]:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"✅ Permissions updated for agent '{agent_id}'"
                                f"\nRead access: {permissions.get('can_read', [])}"
                                f"\nWrite access: {permissions.get('can_write', [])}"
                                f"\nAdmin access: {permissions.get('can_admin', [])}"
                            )
                        }
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error configuring agent permissions: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error configuring permissions: {str(e)}"
                    }
                ]
            }

    async def handle_query_memory_for_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query memory for an agent with permission-based access control."""
        try:
            agent_id = arguments.get("agent_id")
            query = arguments.get("query")
            memory_layers = arguments.get("memory_layers", ["global", "learned"])
            limit = arguments.get("limit", 10)
            
            if not agent_id or not query:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id and query are required"}
                    ]
                }

            # Check agent permissions for each memory layer
            allowed_layers = []
            for memory_type in memory_layers:
                has_permission = await self.memory_manager.check_agent_permission(
                    agent_id=agent_id,
                    action="read",
                    memory_type=memory_type
                )
                if has_permission:
                    allowed_layers.append(memory_type)

            if not allowed_layers:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Agent {agent_id} has no read permissions "
                                f"for requested memory layers"
                            )
                        }
                    ]
                }

            # Query memory with allowed layers
            result = await self.memory_manager.query_memory(
                query=query,
                memory_types=allowed_layers,
                limit=limit,
                agent_id=agent_id
            )

            if result["success"]:
                results_text = []
                for i, memory_result in enumerate(result["results"], 1):
                    results_text.append(
                        f"**Result {i}** (Score: {memory_result['score']:.3f}, "
                        f"Type: {memory_result['memory_type']})\n"
                        f"{memory_result['content']}\n"
                    )
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"🔍 Found {len(result['results'])} results "
                                f"for agent '{agent_id}'"
                                f"\nAllowed memory layers: "
                                f"{', '.join(allowed_layers)}\n\n"
                                + "\n".join(results_text)
                            )
                        }
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Query failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error querying memory for agent: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error querying memory: {str(e)}"
                    }
                ]
            }

    async def handle_store_agent_action(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store an agent action with optional learned memory integration."""
        try:
            agent_id = arguments.get("agent_id")
            action = arguments.get("action")
            context = arguments.get("context", {})
            outcome = arguments.get("outcome")
            learn = arguments.get("learn", False)
            
            if not agent_id or not action or not outcome:
                return {
                    "isError": True,
                    "content": [
                        {
                            "type": "text",
                            "text": "agent_id, action, and outcome are required"
                        }
                    ]
                }

            # Log the action
            result = await self.memory_manager.log_agent_action(
                agent_id=agent_id,
                action=action,
                context=context,
                outcome=outcome,
                store_as_learned=learn
            )

            if result["success"]:
                response_text = (
                    f"✅ Action logged for agent '{agent_id}'"
                    f"\nAction: {action}"
                    f"\nOutcome: {outcome}"
                )
                
                if result["stored_as_learned"]:
                    response_text += (
                        "\n📚 Stored as learned memory for future reference"
                    )
                
                return {
                    "content": [
                        {"type": "text", "text": response_text}
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed: {result['error']}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error storing agent action: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error storing action: {str(e)}"
                    }
                ]
            }
    
    def handle_system_health(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system health check tool call."""
        try:
            # Get health information
            health_info = {
                "timestamp": str(datetime.now()),
                "memory_manager": {
                    "available": self.memory_manager is not None,
                    "initialized": (
                        self.memory_manager is not None and 
                        getattr(self.memory_manager, 'collections_initialized', False)
                    )
                },
                "error_statistics": error_handler.get_error_stats(),
                "components": {
                    "markdown_processor": self.markdown_processor is not None
                }
            }
            
            # Test basic connectivity if memory manager is available
            if self.memory_manager:
                try:
                    if hasattr(self.memory_manager, 'client') and self.memory_manager.client:
                        collections = self.memory_manager.client.get_collections()
                        health_info["components"]["qdrant"] = {
                            "status": "healthy",
                            "collections_count": len(collections.collections)
                        }
                    else:
                        health_info["components"]["qdrant"] = {
                            "status": "unavailable",
                            "error": "No Qdrant client"
                        }
                        
                    if hasattr(self.memory_manager, 'embedding_model') and self.memory_manager.embedding_model:
                        health_info["components"]["embedding_model"] = {
                            "status": "healthy",
                            "model": str(self.memory_manager.embedding_model)
                        }
                    else:
                        health_info["components"]["embedding_model"] = {
                            "status": "unavailable"
                        }
                        
                except Exception as e:
                    health_info["components"]["qdrant"] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            # Determine overall health status
            component_issues = []
            for component, info in health_info["components"].items():
                if isinstance(info, dict) and info.get("status") in ["unavailable", "error"]:
                    component_issues.append(component)
            
            if not component_issues:
                overall_status = "healthy"
                status_text = "✅ All systems operational"
            elif len(component_issues) == len(health_info["components"]):
                overall_status = "critical"
                status_text = f"❌ Critical: All components have issues: {', '.join(component_issues)}"
            else:
                overall_status = "degraded"
                status_text = f"⚠️ Degraded: Issues with: {', '.join(component_issues)}"
            
            health_info["overall_status"] = overall_status
            
            # Format health info for display
            health_text = f"""# System Health Report

**Status:** {status_text}  
**Timestamp:** {health_info['timestamp']}

## Component Status

### Memory Manager
- **Available:** {'✅' if health_info['memory_manager']['available'] else '❌'}
- **Initialized:** {'✅' if health_info['memory_manager']['initialized'] else '❌'}

### Components
"""
            
            for component, info in health_info["components"].items():
                if isinstance(info, dict):
                    status = info.get("status", "unknown")
                    if status == "healthy":
                        status_icon = "✅"
                    elif status == "unavailable":
                        status_icon = "⚠️"
                    else:
                        status_icon = "❌"
                    
                    health_text += f"- **{component.replace('_', ' ').title()}:** {status_icon} {status}\n"
                    
                    if "error" in info:
                        health_text += f"  - Error: {info['error']}\n"
                else:
                    health_text += f"- **{component.replace('_', ' ').title()}:** {'✅' if info else '❌'}\n"
            
            # Add error statistics if available
            error_stats = health_info.get("error_statistics", {})
            if error_stats.get("total_errors", 0) > 0:
                health_text += f"""
## Error Statistics
- **Total Errors:** {error_stats.get('total_errors', 0)}
- **Recovery Attempts:** {error_stats.get('recovery_attempts', 0)}
- **Successful Recoveries:** {error_stats.get('successful_recoveries', 0)}
"""
                
                if error_stats.get("errors_by_category"):
                    health_text += "\n### Errors by Category\n"
                    for category, count in error_stats["errors_by_category"].items():
                        health_text += f"- **{category.title()}:** {count}\n"
            
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": health_text
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in system health check: {e}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Health check failed: {str(e)}"
                    }
                ]
            }

    # Policy Tools
    async def handle_build_policy_from_markdown(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build policy from markdown files in directory."""
        try:
            directory = arguments.get("directory", "./policy")
            policy_version = arguments.get("policy_version", "latest")
            activate = arguments.get("activate", True)

            # Build canonical policy
            result = await self.policy_processor.build_canonical_policy(
                directory=directory,
                policy_version=policy_version
            )

            if not result["success"]:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed: {result.get('error', 'Unknown error')}"}
                    ]
                }

            # Store policy entries in Qdrant if activate is True
            if activate and result["entries"]:
                storage_results = await self._store_policy_entries(result["entries"])
                
                response_text = (
                    f"✅ Built policy version '{policy_version}'"
                    f"\n📁 Directory: {directory}"
                    f"\n📝 Files processed: {result['files_processed']}"
                    f"\n🔢 Total rules: {result['total_rules']}"
                    f"\n✅ Unique rules: {result['unique_rules']}"
                    f"\n#️⃣ Policy hash: {result['policy_hash'][:12]}..."
                )
                
                if storage_results["success"]:
                    response_text += f"\n💾 Stored {len(result['entries'])} policy entries"
                else:
                    response_text += f"\n⚠️ Storage issues: {storage_results.get('warnings', 0)} warnings"

                return {
                    "content": [
                        {"type": "text", "text": response_text}
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"✅ Policy built (not activated)\n📊 {result['total_rules']} rules parsed"
                        }
                    ]
                }

        except Exception as e:
            logger.error(f"Error building policy: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error building policy: {str(e)}"}
                ]
            }

    async def handle_get_policy_rulebook(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get the canonical policy rulebook."""
        try:
            version = arguments.get("version", "latest")
            
            # Query policy memory for the specified version
            policy_entries = await self._query_policy_memory(version=version)
            
            if not policy_entries:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"No policy found for version: {version}"}
                    ]
                }

            # Build canonical rulebook structure
            rulebook = self._build_rulebook_structure(policy_entries)
            
            response_text = (
                f"📋 Policy Rulebook - Version: {version}"
                f"\n🔢 Rules: {len(policy_entries)}"
                f"\n📚 Sections: {len(rulebook['sections'])}"
                f"\n#️⃣ Hash: {rulebook['policy_hash'][:12]}..."
                f"\n\n📖 **Rulebook JSON:**\n```json\n{rulebook['json']}\n```"
            )

            return {
                "content": [
                    {"type": "text", "text": response_text}
                ]
            }

        except Exception as e:
            logger.error(f"Error getting policy rulebook: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error getting rulebook: {str(e)}"}
                ]
            }

    async def handle_validate_json_against_schema(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate JSON against policy schema requirements."""
        try:
            schema_name = arguments.get("schema_name")
            candidate_json = arguments.get("candidate_json")
            
            if not schema_name or not candidate_json:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "schema_name and candidate_json are required"}
                    ]
                }

            # Get current policy rules for validation
            policy_entries = await self._query_policy_memory()
            
            # Extract required sections from policy
            required_sections = self._extract_required_sections(policy_entries)
            
            # Validate the JSON structure
            validation_result = self._validate_json_structure(
                candidate_json, 
                schema_name, 
                required_sections
            )

            if validation_result["is_valid"]:
                response_text = (
                    f"✅ JSON validation passed"
                    f"\n📋 Schema: {schema_name}"
                    f"\n📝 Required sections: {len(required_sections)}"
                    f"\n✓ All requirements met"
                )
            else:
                response_text = (
                    f"❌ JSON validation failed"
                    f"\n📋 Schema: {schema_name}"
                    f"\n🚨 Issues found: {len(validation_result['errors'])}"
                    f"\n\n**Validation Errors:**\n{chr(10).join(validation_result['errors'])}"
                )

            return {
                "content": [
                    {"type": "text", "text": response_text}
                ]
            }

        except Exception as e:
            logger.error(f"Error validating JSON: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error validating JSON: {str(e)}"}
                ]
            }

    async def handle_log_policy_violation(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a policy violation for compliance tracking."""
        try:
            agent_id = arguments.get("agent_id")
            rule_id = arguments.get("rule_id")
            context = arguments.get("context", {})
            
            if not agent_id or not rule_id:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "agent_id and rule_id are required"}
                    ]
                }

            # Store violation in policy violations collection
            violation_entry = {
                "agent_id": agent_id,
                "rule_id": rule_id,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": await self._get_rule_severity(rule_id)
            }

            # Store in violations collection
            storage_result = await self._store_policy_violation(violation_entry)
            
            if storage_result["success"]:
                response_text = (
                    f"🚨 Policy violation logged"
                    f"\n👤 Agent: {agent_id}"
                    f"\n📋 Rule: {rule_id}"
                    f"\n⚡ Severity: {violation_entry['severity']}"
                    f"\n🕒 Timestamp: {violation_entry['timestamp']}"
                )
                
                # Add context if provided
                if context:
                    response_text += f"\n📄 Context: {context}"

                return {
                    "content": [
                        {"type": "text", "text": response_text}
                    ]
                }
            else:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Failed to log violation: {storage_result.get('error', 'Unknown error')}"}
                    ]
                }

        except Exception as e:
            logger.error(f"Error logging policy violation: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error logging violation: {str(e)}"}
                ]
            }

    # Policy Helper Methods
    async def _store_policy_entries(self, entries: list) -> Dict[str, Any]:
        """Store policy entries in Qdrant."""
        try:
            from .config import Config
            
            success_count = 0
            warnings = []

            for entry in entries:
                # Create vector embedding for the rule text
                embedding = self.memory_manager.embedding_model.encode(entry["text"])
                
                # Create point for storage
                point = {
                    "id": f"policy_{entry['rule_id']}_{entry['policy_version']}",
                    "vector": embedding.tolist(),
                    "payload": entry
                }

                # Store in policy memory collection
                try:
                    self.memory_manager.client.upsert(
                        collection_name=Config.POLICY_MEMORY_COLLECTION,
                        points=[point]
                    )
                    success_count += 1
                except Exception as e:
                    warnings.append(f"Failed to store {entry['rule_id']}: {str(e)}")

            return {
                "success": success_count > 0,
                "stored_count": success_count,
                "total_count": len(entries),
                "warnings": warnings
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _query_policy_memory(self, version: str = "latest", limit: int = 1000) -> list:
        """Query policy memory collection."""
        try:
            from .config import Config
            
            # Create a dummy query vector for searching all policies
            query_vector = [0.0] * Config.EMBEDDING_DIMENSION
            
            # Search with filter for version if not "latest"
            filter_condition = None
            if version != "latest":
                filter_condition = {
                    "must": [{"key": "policy_version", "match": {"value": version}}]
                }

            results = self.memory_manager.client.search(
                collection_name=Config.POLICY_MEMORY_COLLECTION,
                query_vector=query_vector,
                query_filter=filter_condition,
                limit=limit,
                with_payload=True
            )

            return [result.payload for result in results]

        except Exception as e:
            logger.error(f"Error querying policy memory: {e}")
            return []

    def _build_rulebook_structure(self, policy_entries: list) -> Dict[str, Any]:
        """Build structured rulebook from policy entries."""
        try:
            import json
            
            # Group by section
            sections = {}
            policy_hash = None
            
            for entry in policy_entries:
                section_name = entry.get("section", "Unknown")
                if section_name not in sections:
                    sections[section_name] = []
                
                sections[section_name].append({
                    "rule_id": entry["rule_id"],
                    "text": entry["text"],
                    "severity": entry["severity"]
                })
                
                # Get policy hash from first entry
                if policy_hash is None:
                    policy_hash = entry.get("policy_hash", "unknown")

            # Create structured rulebook
            rulebook = {
                "policy_version": policy_entries[0].get("policy_version", "unknown") if policy_entries else "unknown",
                "policy_hash": policy_hash,
                "sections": sections,
                "total_rules": len(policy_entries)
            }

            return {
                "policy_hash": policy_hash,
                "sections": sections,
                "json": json.dumps(rulebook, indent=2)
            }

        except Exception as e:
            logger.error(f"Error building rulebook: {e}")
            return {"policy_hash": "unknown", "sections": {}, "json": "{}"}

    def _extract_required_sections(self, policy_entries: list) -> list:
        """Extract required sections from policy entries."""
        # Find rules that specify required sections (R- prefix typically)
        required_sections = []
        for entry in policy_entries:
            if entry["rule_id"].startswith("R-") and "required" in entry["text"].lower():
                # Extract section names from rule text
                # This is a simplified extraction - could be enhanced
                required_sections.append(entry["section"])
        
        return list(set(required_sections))

    def _validate_json_structure(self, candidate_json: str, schema_name: str, required_sections: list) -> Dict[str, Any]:
        """Validate JSON structure against policy requirements."""
        try:
            import json as json_module
            
            # Parse JSON
            try:
                data = json_module.loads(candidate_json)
            except json_module.JSONDecodeError as e:
                return {
                    "is_valid": False,
                    "errors": [f"Invalid JSON format: {str(e)}"]
                }

            errors = []
            
            # Check for required sections based on schema
            if isinstance(data, dict):
                data_sections = set(data.keys())
                missing_sections = set(required_sections) - data_sections
                
                if missing_sections:
                    errors.append(f"Missing required sections: {list(missing_sections)}")
            else:
                errors.append("JSON must be an object with sections")

            return {
                "is_valid": len(errors) == 0,
                "errors": errors
            }

        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }

    async def _get_rule_severity(self, rule_id: str) -> str:
        """Get severity level for a rule ID."""
        try:
            # Query for the specific rule
            policy_entries = await self._query_policy_memory()
            
            for entry in policy_entries:
                if entry["rule_id"] == rule_id:
                    return entry.get("severity", "medium")
            
            # Default severity if rule not found
            return "medium"

        except Exception:
            return "medium"

    async def _store_policy_violation(self, violation_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Store policy violation in violations collection."""
        try:
            from .config import Config
            import uuid

            # Create vector embedding for the violation context
            context_text = f"{violation_entry['rule_id']} {violation_entry.get('context', '')}"
            embedding = self.memory_manager.embedding_model.encode(context_text)
            
            # Create point for storage
            point = {
                "id": str(uuid.uuid4()),
                "vector": embedding.tolist(),
                "payload": violation_entry
            }

            # Store in violations collection
            self.memory_manager.client.upsert(
                collection_name=Config.POLICY_VIOLATIONS_COLLECTION,
                points=[point]
            )

            return {"success": True}

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
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
                # Agent management tools
                "initialize_new_agent": self.handle_initialize_new_agent,
                "configure_agent_permissions": self.handle_configure_agent_permissions,
                "query_memory_for_agent": self.handle_query_memory_for_agent,
                "store_agent_action": self.handle_store_agent_action,
                # Policy management tools
                "build_policy_from_markdown": self.handle_build_policy_from_markdown,
                "get_policy_rulebook": self.handle_get_policy_rulebook,
                "validate_json_against_schema": self.handle_validate_json_against_schema,
                "log_policy_violation": self.handle_log_policy_violation,
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
