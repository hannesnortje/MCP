#!/usr/bin/env python3
"""
Markdown Document Ingestion Script for MCP Memory Server.

This script correctly processes markdown files and stores them in the database.
Use it to ingest important documents into the global memory layer.

Usage:
  poetry run python ingest_documents.py [directory_path] [--recursive]

Options:
  --recursive   Process files in subdirectories (default: True)

Example:
  poetry run python ingest_documents.py /path/to/docs --recursive
"""

import asyncio
import logging
import hashlib
import argparse
from pathlib import Path

from src.memory_manager import QdrantMemoryManager
from src.markdown_processor import MarkdownProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("document-ingest")


def generate_content_hash(content: str) -> str:
    """Generate a hash for content to use as point ID."""
    # Convert hash to UUID format
    hash_hex = hashlib.sha256(content.encode('utf-8')).hexdigest()
    # Convert to UUID by taking first 32 chars and formatting as UUID
    uuid_str = (f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-"
                f"{hash_hex[16:20]}-{hash_hex[20:32]}")
    return uuid_str


async def process_markdown_file(file_path):
    """Read a markdown file synchronously."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


async def ingest_directory(directory, recursive=True):
    """Process all markdown files in directory and store in database."""
    logger.info(f"Starting ingestion from directory: {directory}")
    
    # Initialize components
    mm = QdrantMemoryManager()
    markdown_processor = MarkdownProcessor()
    
    # Scan directory for markdown files
    try:
        files = await markdown_processor.scan_directory_for_markdown(
            directory=directory, recursive=recursive
        )
        logger.info(f"Found {len(files)} markdown files")
        
        if not files:
            logger.warning(f"No markdown files found in {directory}")
            return
        
        # Process each file
        stored_count = 0
        error_count = 0
        
        for file_info in files:
            file_path = file_info['path']
            logger.info(f"Processing file: {file_path}")
            
            # Read file content
            content = await process_markdown_file(file_path)
            if not content:
                logger.error(f"Failed to read {file_path}")
                error_count += 1
                continue
                
            # Generate file hash
            file_hash = generate_content_hash(content)
            logger.info(f"File hash: {file_hash[:8]}...")
            
            # Clean and optimize content
            cleaned_content = markdown_processor.clean_content(content)
            
            # Create chunks
            chunks = markdown_processor.chunk_content(cleaned_content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Store each chunk in global memory
            file_chunks_stored = 0
            
            for chunk in chunks:
                # Check if we have 'content' key or 'text' key
                chunk_text = chunk.get('content', '')
                if not chunk_text and 'text' in chunk:
                    chunk_text = chunk.get('text', '')
                
                # Skip empty chunks
                if not chunk_text:
                    logger.warning(
                        f"Empty chunk at index "
                        f"{chunk.get('chunk_index', 'unknown')}"
                    )
                    continue
                
                # Store in global memory
                try:
                    # The method is not actually async despite its name
                    chunk_hash = mm.async_add_to_memory(
                        content=chunk_text,
                        memory_type="global",
                        metadata={
                            "source_file": file_path,
                            "chunk_index": chunk.get('chunk_index', 0),
                            "file_hash": file_hash
                        }
                    )
                    file_chunks_stored += 1
                    logger.info(
                        f"Stored chunk {chunk.get('chunk_index', 0)}: "
                        f"{chunk_hash[:8]}..."
                    )
                except Exception as e:
                    logger.error(
                        f"Error storing chunk {chunk.get('chunk_index', 0)}: "
                        f"{str(e)}"
                    )
                    error_count += 1
            
            logger.info(
                f"Successfully stored {file_chunks_stored} chunks "
                f"from {file_path}"
            )
            stored_count += file_chunks_stored
        
        logger.info(
            f"Ingestion complete: {stored_count} chunks stored "
            f"from {len(files)} files"
        )
        logger.info(f"Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Ingest markdown documents into MCP memory.'
    )
    parser.add_argument(
        'directory', nargs='?', default='./docs',
        help='Directory containing markdown files (default: ./docs)'
    )
    parser.add_argument(
        '--recursive', action='store_true', default=True,
        help='Process files in subdirectories (default: True)'
    )
    
    args = parser.parse_args()
    
    # Verify directory exists
    directory_path = Path(args.directory)
    if not directory_path.exists():
        logger.error(f"Directory not found: {args.directory}")
        return 1
    if not directory_path.is_dir():
        logger.error(f"Not a directory: {args.directory}")
        return 1
        
    # Run the async function
    try:
        asyncio.run(ingest_directory(args.directory, args.recursive))
        return 0
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

