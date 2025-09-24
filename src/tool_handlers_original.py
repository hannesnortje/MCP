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
        
        if result.get("success"):
            message = result.get("message", "Content added successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Added to global memory: {message}"
                    }
                ]
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to add to global memory: {error}"
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
        
        if result.get("success"):
            message = result.get("message", "Pattern added successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Added to learned memory: {message}"
                    }
                ]
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to add to learned memory: {error}"
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
        
        if result.get("success"):
            message = result.get("message", "Content added successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Added to agent memory: {message}"
                    }
                ]
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to add to agent memory: {error}"
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
        
        # Add debugging information
        logger.info(
            f"🔍 Query: '{query}', Types: {memory_types}, "
            f"Limit: {limit}, Min score: {min_score}"
        )
        
        results = self.memory_manager.query_memory(
            query, memory_types, limit, min_score
        )
        
        logger.info(
            f"📊 Query results: success={results.get('success')}, "
            f"total_results={results.get('total_results', 0)}"
        )
        
        if results.get("success", False):
            memories = results.get("results", [])
            response_text = (
                f"Found {len(memories)} relevant memories:\n\n"
            )
            
            if len(memories) == 0:
                response_text += "No memories found matching the criteria.\n"
                response_text += "\n🔧 Debug Info:\n"
                response_text += f"- Query: '{query}'\n"
                response_text += f"- Memory types searched: {memory_types}\n"
                response_text += f"- Minimum score threshold: {min_score}\n"
                response_text += f"- Result limit: {limit}\n"
                
                # Add collection status
                try:
                    collections = self.memory_manager.client.get_collections()
                    for collection in collections.collections:
                        name_matches = any(
                            collection.name.endswith(mt) or mt in collection.name
                            for mt in memory_types
                        )
                        if name_matches:
                            info = self.memory_manager.client.get_collection(
                                collection.name
                            )
                            response_text += (
                                f"- Collection '{collection.name}': "
                                f"{info.points_count} points\n"
                            )
                except Exception as e:
                    response_text += f"- Collection info error: {e}\n"
            else:
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
            response_text = f"Query failed: {error_msg}\n\n"
            response_text += "🔧 Debug Info:\n"
            response_text += f"- Query: '{query}'\n"
            response_text += f"- Memory types: {memory_types}\n"
            response_text += f"- Error details: {error_msg}\n"
        
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
            patterns = results.get("results", [])
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
        """Handle process_markdown_directory tool call.
        
        Note: This function is maintained for backward compatibility.
        It delegates to batch_process_directory which properly stores content.
        """
        try:
            # Just delegate to the batch_process_directory handler
            # which will properly store content in the database
            logger.info(f"Redirecting process_markdown_directory to batch_process_directory: {arguments}")
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
            
            # Step 2: Process each file directly - don't use markdown_processor.process_directory_batch
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
                        chunk_text = chunk.get('content', '')  # Use 'content' key instead of 'text'
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
                            logger.error(f"Error storing chunk from {file_path}: {e}")
                    
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
                f"📂 Directory: {directory} ({'recursive' if recursive else 'non-recursive'})\n"
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
                status_icon = "✅" if result["status"] == "processed" else "❌"
                response_text += f"{status_icon} {result['path']}"
                
                if result["status"] == "processed":
                    response_text += f" ({result['chunks_stored']} chunks stored)"
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

    # Agent Management Tools

    async def handle_initialize_new_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a new agent with enhanced functionality from agent_startup."""
        try:
            # Extract parameters with defaults matching agent_startup prompt
            agent_id = arguments.get("agent_id")
            agent_role = arguments.get("agent_role")
            memory_layers = arguments.get("memory_layers", ["global", "learned"])
            policy_version = arguments.get("policy_version", "latest")
            policy_hash = arguments.get("policy_hash", "")
            load_policies = arguments.get("load_policies", True)
            
            # Auto-generate agent_id if not provided (like agent_startup)
            if not agent_id:
                import uuid
                agent_id = str(uuid.uuid4())
            
            # Auto-generate agent_role if not provided
            if not agent_role:
                agent_role = "general"
            
            # Convert string memory_layers to list if needed (for compatibility)
            if isinstance(memory_layers, str):
                memory_layers = [layer.strip() for layer in memory_layers.split(",")]
            
            initialization_messages = []
            errors = []
            
            # Step 1: Register the agent
            try:
                if self.memory_manager:
                    agent_result = await self.memory_manager.register_agent(
                        agent_id=agent_id,
                        agent_role=agent_role,
                        memory_layers=memory_layers
                    )
                    
                    if agent_result["success"]:
                        initialization_messages.append(
                            f"✅ Agent '{agent_id}' registered successfully"
                        )
                    else:
                        errors.append(
                            f"❌ Agent registration failed: "
                            f"{agent_result.get('error', 'Unknown error')}"
                        )
                else:
                    errors.append("❌ Memory manager not available")
            except Exception as e:
                errors.append(f"❌ Agent registration error: {str(e)}")
            
            # Step 2: Load and bind policies (if requested)
            if load_policies:
                try:
                    from .policy_processor import PolicyProcessor
                    policy_processor = PolicyProcessor()
                    policy_result = await policy_processor.build_canonical_policy(
                        directory=None,  # Use default policy directory
                        policy_version=policy_version
                    )
                    
                    if policy_result["success"]:
                        initialization_messages.append(
                            f"✅ Policy version '{policy_version}' loaded"
                        )
                        initialization_messages.append(
                            f"📁 Files processed: "
                            f"{policy_result.get('files_processed', 0)}"
                        )
                        initialization_messages.append(
                            f"📝 Rules loaded: "
                            f"{policy_result.get('unique_rules', 0)}"
                        )
                        
                        # Update policy hash if we got one from policy load
                        if policy_result.get('policy_hash') and not policy_hash:
                            policy_hash = policy_result['policy_hash']
                    else:
                        errors.append(
                            f"❌ Policy loading failed: "
                            f"{policy_result.get('error', 'Unknown error')}"
                        )
                except Exception as e:
                    errors.append(f"❌ Policy loading error: {str(e)}")
            
            # Step 3: Get system info
            system_info = ""
            try:
                if self.memory_manager:
                    agents_result = await self.memory_manager.list_agents()
                    agent_count = len(agents_result) if agents_result else 0
                    system_info = f"\n📊 System Status: {agent_count} agents active"
            except Exception as e:
                system_info = f"\n⚠️ System Status: Unable to fetch ({str(e)})"
            
            # Determine overall status
            if errors:
                status = "error"
                status_icon = "❌"
                status_text = "FAILED"
            else:
                status = "success"
                status_icon = "✅"
                status_text = "SUCCESS"
            
            # Build response content (same format as agent_startup)
            response_lines = [
                f"# Agent Startup {status_text}",
                "",
                "## Agent Identity",
                f"- **Agent ID:** `{agent_id}`",
                f"- **Role:** `{agent_role}`",
                f"- **Initialization Time:** {datetime.now().isoformat()}",
                "",
                "## Initialization Results"
            ]
            
            # Add success messages
            if initialization_messages:
                response_lines.extend(initialization_messages)
            
            # Add error messages
            if errors:
                response_lines.append("")
                response_lines.append("### Errors:")
                response_lines.extend(errors)
            
            # Calculate policy hash display
            policy_hash_display = (
                policy_hash[:12] + '...' if policy_hash
                else 'Not available'
            )
            
            response_lines.extend([
                "",
                "## Configuration",
                f"- **Memory Layers:** {', '.join(memory_layers)}",
                f"- **Policy Version:** `{policy_version}`",
                f"- **Policy Hash:** `{policy_hash_display}`",
                "",
                f"{status_icon} Agent initialization {status_text.lower()}",
                system_info
            ])
            
            prompt_content = "\n".join(response_lines)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": prompt_content
                    }
                ],
                "metadata": {
                    "agent_id": agent_id,
                    "agent_role": agent_role,
                    "memory_layers": memory_layers,
                    "policy_version": policy_version,
                    "policy_hash": policy_hash,
                    "initialization_success": len(errors) == 0,
                    "errors": errors
                },
                "isError": len(errors) > 0
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced initialize_new_agent: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Error initializing agent: {str(e)}"}
                ]
            }

    async def handle_initialize_development_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a development agent with developer-optimized defaults."""
        dev_arguments = {
            "agent_id": arguments.get("agent_id"),
            "agent_role": "developer",
            "memory_layers": ["global", "learned", "agent"],
            "policy_version": "latest",
            "load_policies": True
        }
        return await self.handle_initialize_new_agent(dev_arguments)

    async def handle_initialize_testing_agent(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a testing agent with testing-optimized defaults."""
        test_arguments = {
            "agent_id": arguments.get("agent_id"),
            "agent_role": "tester",
            "memory_layers": ["global", "learned"],
            "policy_version": "latest",
            "load_policies": True
        }
        return await self.handle_initialize_new_agent(test_arguments)

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
            import uuid
            
            success_count = 0
            warnings = []

            for entry in entries:
                # Create vector embedding for the rule text
                embedding = self.memory_manager.embedding_model.encode(entry["text"])
                
                # Generate UUID for Qdrant point ID
                point_id = str(uuid.uuid4())
                
                # Create point for storage
                point = {
                    "id": point_id,
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
                    warnings.append(
                        f"Failed to store {entry['rule_id']}: {str(e)}"
                    )

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
            sections: Dict[str, list] = {}
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

    # =============================================================================
    # GUIDANCE TOOLS - Phase 3
    # =============================================================================

    def _get_guidance_content(self, guidance_type: str) -> Dict[str, Any]:
        """Get guidance content for a specific type."""
        guidance_map = {
            "memory_usage": "# Memory Usage Best Practices\n\n## Core Principles\n• Layer-appropriate storage (Global/Learned/Agent)\n• Query optimization with specific terms\n• Well-structured, searchable content\n\n## Best Practices\n✅ Before storing: verify uniqueness, choose type, add metadata\n✅ When querying: start specific, use filters, adjust thresholds\n✅ Maintenance: deduplicate, update, clean obsolete content\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "context_preservation": "# Context Preservation Strategy\n\n## Key Strategies\n• Session checkpoints with key decisions\n• Progressive context building across sessions\n• Categorize: immediate/session/historical context\n\n## Implementation\n✅ Before session end: summarize outcomes, store context, link memories\n✅ Session startup: query previous context, rebuild state, identify next steps\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "query_optimization": "# Query Optimization Best Practices\n\n## Fundamentals\n• Specificity over breadth\n• Context-aware queries with technical terms\n• Memory type targeting (Global/Learned/Agent)\n\n## Advanced Techniques\n✅ Similarity thresholds: 0.9+ exact, 0.8-0.9 related, 0.7-0.8 discovery\n✅ Progressive queries: start specific, broaden if needed\n✅ Keyword optimization: technical terms, action words, context markers\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "markdown_optimization": "# Markdown Processing Guidelines\n\n## Processing Principles\n• Structure preservation (headings, code blocks, tables)\n• Metadata extraction (headers, tags, categories)\n• Content optimization for memory storage\n\n## Best Practices\n✅ Pre-processing: clean, normalize, extract key info\n✅ Chunking: header-based, size-based, context-aware\n✅ Quality assurance: validate syntax, check metadata\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "duplicate_detection": "# Duplicate Detection Strategy\n\n## Detection Methods\n• Cosine similarity analysis (0.95+ exact, 0.85-0.95 near-duplicates)\n• Content hash comparison\n• Metadata-based detection\n\n## Workflow\n✅ Pre-storage: calculate hash, check matches, flag duplicates\n✅ Post-storage: periodic scans, review near-duplicates\n✅ Handling: skip/replace exact, review near-duplicates, cross-reference related\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "directory_processing": "# Directory Processing Best Practices\n\n## Planning Phase\n• Directory assessment: size, file types, structure\n• Processing strategy: batch size, parallel processing, error handling\n\n## Execution\n✅ Pre-processing validation: check access, space, connectivity\n✅ File processing order: prioritize importance, handle dependencies\n✅ Error recovery: graceful degradation, retry logic, logging\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "memory_type_selection": "# Memory Type Selection Criteria\n\n## Decision Framework\n• Who needs this? Everyone→Global, Future agents→Learned, Just me→Agent\n• How long persist? Permanent→Global/Learned, Session→Agent\n• Content type? Docs→Global, Insights→Learned, Notes→Agent\n\n## Examples\n✅ Global: API docs, policies, specifications\n✅ Learned: patterns, best practices, lessons learned\n✅ Agent: current tasks, preferences, session context\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "memory_type_suggestion": "# AI Memory Type Suggestions\n\n## Detection Factors\n• Scope indicators: personal pronouns→Agent, universal→Global, learning→Learned\n• Temporal indicators: \"currently\"→Agent, \"always\"→Global, \"learned\"→Learned\n• Content patterns: documentation→Global, insights→Learned, tasks→Agent\n\n## Implementation\n✅ Analyze content semantically, provide confidence scores\n✅ Consider context clues, allow user overrides\n✅ Learn from corrections, improve over time\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "policy_compliance": "# Policy Compliance Guide\n\n## Framework Understanding\n• Policy structure: principles, forbidden actions, required sections, style guide\n• Compliance levels: critical, important, recommended, stylistic\n\n## Workflow\n✅ Pre-action: review policies, assess impact, document reasoning\n✅ During action: monitor conflicts, adjust approach, document decisions\n✅ Post-action: verify compliance, log questions, update procedures\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**",
            "policy_violation_recovery": "# Policy Violation Recovery\n\n## Immediate Response\n• Stop and assess: halt action, identify violation, assess impact\n• Document everything: what, when, intended vs actual, impact\n• Immediate containment: prevent further violations, secure systems\n\n## Recovery Process\n✅ Severity assessment: critical, major, minor violations\n✅ Recovery actions: escalation, investigation, remediation\n✅ Learning: analyze causes, implement improvements, share lessons\n\n**Full guidance: see docs/GUIDANCE_CONTENT.md**"
        }
        
        content = guidance_map.get(guidance_type, "Guidance content not found.")
        return {
            "content": [
                {"type": "text", "text": content}
            ]
        }

    def handle_get_memory_usage_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on effective memory usage patterns."""
        return self._get_guidance_content("memory_usage")

    def handle_get_context_preservation_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on preserving context across sessions."""
        return self._get_guidance_content("context_preservation")

    def handle_get_query_optimization_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on optimizing memory queries and retrieval."""
        return self._get_guidance_content("query_optimization")

    def handle_get_markdown_optimization_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on processing and storing markdown content."""
        return self._get_guidance_content("markdown_optimization")

    def handle_get_duplicate_detection_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on detecting and handling duplicate content."""
        return self._get_guidance_content("duplicate_detection")

    def handle_get_directory_processing_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on batch processing directories."""
        return self._get_guidance_content("directory_processing")

    def handle_get_memory_type_selection_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on selecting appropriate memory types."""
        return self._get_guidance_content("memory_type_selection")

    def handle_get_memory_type_suggestion_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance for AI-powered memory type suggestions."""
        return self._get_guidance_content("memory_type_suggestion")

    def handle_get_policy_compliance_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance for following policy compliance."""
        return self._get_guidance_content("policy_compliance")

    def handle_get_policy_violation_recovery_guidance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance for recovering from policy violations."""
        return self._get_guidance_content("policy_violation_recovery")

    # Generic Collection Tools
    async def handle_create_collection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_collection tool call."""
        try:
            collection_name = arguments.get("collection_name")
            description = arguments.get("description", "")
            metadata = arguments.get("metadata", {})
            
            if not collection_name:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Collection name is required"}
                    ]
                }
            
            # Use the GenericMemoryService to create the collection
            result = await self.memory_manager.generic_service.create_collection(
                collection_name, description, metadata
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Successfully created collection '{collection_name}'"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Failed to create collection: {str(e)}"}
                ]
            }

    async def handle_list_collections(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_collections tool call."""
        try:
            include_stats = arguments.get("include_stats", True)
            
            # Get collections from GenericMemoryService
            collections = await self.memory_manager.generic_service.list_collections()
            
            result_text = f"Found {len(collections.collections)} collections:\n\n"
            
            for collection in collections.collections:
                result_text += f"**{collection.name}**\n"
                if collection.description:
                    result_text += f"  Description: {collection.description}\n"
                
                if include_stats:
                    stats = await self.memory_manager.generic_service.get_collection_stats(collection.name)
                    result_text += f"  Documents: {stats['document_count']}\n"
                    result_text += f"  Created: {collection.created_at}\n"
                    
                if collection.metadata:
                    result_text += f"  Metadata: {collection.metadata}\n"
                result_text += "\n"
            
            return {
                "content": [
                    {"type": "text", "text": result_text}
                ]
            }
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Failed to list collections: {str(e)}"}
                ]
            }

    async def handle_add_to_collection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_to_collection tool call."""
        try:
            collection_name = arguments.get("collection_name")
            content = arguments.get("content")
            metadata = arguments.get("metadata", {})
            importance = arguments.get("importance", 0.5)
            
            if not collection_name or not content:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Collection name and content are required"}
                    ]
                }
            
            # Use the GenericMemoryService to add content
            memory_id = await self.memory_manager.generic_service.add_to_collection(
                collection_name, content, metadata, importance
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Successfully added content to collection '{collection_name}' with ID: {memory_id}"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error adding to collection: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Failed to add to collection: {str(e)}"}
                ]
            }

    async def handle_query_collection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query_collection tool call."""
        try:
            collection_name = arguments.get("collection_name")
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            min_score = arguments.get("min_score", 0.3)
            include_metadata = arguments.get("include_metadata", True)
            
            if not collection_name or not query:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Collection name and query are required"}
                    ]
                }
            
            # Use the GenericMemoryService to query the collection
            results = await self.memory_manager.generic_service.query_collection(
                collection_name, query, limit, min_score
            )
            
            if not results:
                result_text = f"No results found in collection '{collection_name}' for query: '{query}'"
            else:
                result_text = f"Found {len(results)} results in collection '{collection_name}':\n\n"
                
                for i, result in enumerate(results, 1):
                    result_text += f"**Result {i}** (Score: {result.get('score', 'N/A'):.3f})\n"
                    result_text += f"{result['content']}\n"
                    
                    if include_metadata and result.get('metadata'):
                        result_text += f"Metadata: {result['metadata']}\n"
                    result_text += "\n"
            
            return {
                "content": [
                    {"type": "text", "text": result_text}
                ]
            }
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Failed to query collection: {str(e)}"}
                ]
            }

    async def handle_delete_collection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_collection tool call."""
        try:
            collection_name = arguments.get("collection_name")
            confirm = arguments.get("confirm", False)
            
            if not collection_name:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Collection name is required"}
                    ]
                }
            
            if not confirm:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Confirmation required: set 'confirm' to true to delete the collection"}
                    ]
                }
            
            # Use the GenericMemoryService to delete the collection
            await self.memory_manager.generic_service.delete_collection(collection_name)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Successfully deleted collection '{collection_name}' and all its contents"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Failed to delete collection: {str(e)}"}
                ]
            }

    async def handle_get_collection_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_collection_stats tool call."""
        try:
            collection_name = arguments.get("collection_name")
            
            if not collection_name:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": "Collection name is required"}
                    ]
                }
            
            # Use the GenericMemoryService to get collection stats
            stats = await self.memory_manager.generic_service.get_collection_stats(collection_name)
            
            result_text = f"**Statistics for Collection '{collection_name}'**\n\n"
            result_text += f"Document Count: {stats['document_count']}\n"
            result_text += f"Total Size: {stats.get('total_size', 'Unknown')}\n"
            result_text += f"Last Updated: {stats.get('last_updated', 'Unknown')}\n"
            
            if stats.get('metadata'):
                result_text += f"Metadata: {stats['metadata']}\n"
            
            return {
                "content": [
                    {"type": "text", "text": result_text}
                ]
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Failed to get collection stats: {str(e)}"}
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
                # System health and diagnostics
                "system_health": self.handle_system_health,
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
                "initialize_development_agent": self.handle_initialize_development_agent,
                "initialize_testing_agent": self.handle_initialize_testing_agent,
                "configure_agent_permissions": self.handle_configure_agent_permissions,
                "query_memory_for_agent": self.handle_query_memory_for_agent,
                "store_agent_action": self.handle_store_agent_action,
                # Policy management tools
                "build_policy_from_markdown": self.handle_build_policy_from_markdown,
                "get_policy_rulebook": self.handle_get_policy_rulebook,
                "validate_json_against_schema": self.handle_validate_json_against_schema,
                "log_policy_violation": self.handle_log_policy_violation,
                # Guidance tools - Phase 3
                "get_memory_usage_guidance": self.handle_get_memory_usage_guidance,
                "get_context_preservation_guidance": self.handle_get_context_preservation_guidance,
                "get_query_optimization_guidance": self.handle_get_query_optimization_guidance,
                "get_markdown_optimization_guidance": self.handle_get_markdown_optimization_guidance,
                "get_duplicate_detection_guidance": self.handle_get_duplicate_detection_guidance,
                "get_directory_processing_guidance": self.handle_get_directory_processing_guidance,
                "get_memory_type_selection_guidance": self.handle_get_memory_type_selection_guidance,
                "get_memory_type_suggestion_guidance": self.handle_get_memory_type_suggestion_guidance,
                "get_policy_compliance_guidance": self.handle_get_policy_compliance_guidance,
                "get_policy_violation_recovery_guidance": self.handle_get_policy_violation_recovery_guidance,
                # Generic Collection Tools
                "create_collection": self.handle_create_collection,
                "list_collections": self.handle_list_collections,
                "add_to_collection": self.handle_add_to_collection,
                "query_collection": self.handle_query_collection,
                "delete_collection": self.handle_delete_collection,
                "get_collection_stats": self.handle_get_collection_stats,
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
