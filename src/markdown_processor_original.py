"""
Markdown processor for MCP Memory Server.
Handles reading, cleaning, and optimizing markdown files.
"""

import logging
import re
import hashlib
import os
from typing import Optional, List, Dict, Tuple, Union
from pathlib import Path
import aiofiles
from bs4 import BeautifulSoup
import markdown

logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """Processes markdown files for memory storage."""

    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 200) -> None:
        """Initialize the Markdown Processor.
        
        Args:
            chunk_size: Maximum tokens per chunk (default 900)
            chunk_overlap: Token overlap between chunks (default 200)
        """
        self.markdown_processor = markdown.Markdown(
            extensions=['extra', 'codehilite', 'toc'],
            extension_configs={
                'codehilite': {'css_class': 'highlight'},
                'extra': {}
            }
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def read_markdown_file(self, file_path: str) -> str:
        """Read a markdown file from disk."""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not path.suffix.lower() in ['.md', '.markdown']:
                raise ValueError(f"Not a markdown file: {file_path}")

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()

            logger.info(f"📖 Read markdown file: {file_path} ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"❌ Failed to read markdown file {file_path}: {e}")
            raise

    def clean_content(self, content: str) -> str:
        """Clean and optimize markdown content."""
        try:
            # Remove excessive whitespace
            content = self._normalize_whitespace(content)
            
            # Clean up markdown formatting
            content = self._clean_markdown_formatting(content)
            
            # Remove empty sections
            content = self._remove_empty_sections(content)
            
            # Normalize line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # Ensure content ends with single newline
            content = content.rstrip() + '\n'

            logger.debug(f"🧹 Cleaned content ({len(content)} chars)")
            return content

        except Exception as e:
            logger.error(f"❌ Failed to clean content: {e}")
            return content  # Return original content if cleaning fails

    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content."""
        # Replace multiple spaces with single space (except at line start for indentation)
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Preserve leading whitespace for code blocks and lists
            stripped = line.lstrip()
            if stripped.startswith(('```', '    ', '\t', '-', '*', '+')):
                # Keep original line for code blocks and lists
                cleaned_lines.append(line.rstrip())
            else:
                # Normalize spaces in regular text
                leading_spaces = len(line) - len(stripped)
                cleaned_text = re.sub(r' +', ' ', stripped)
                cleaned_lines.append(' ' * leading_spaces + cleaned_text)
        
        return '\n'.join(cleaned_lines)

    def _clean_markdown_formatting(self, content: str) -> str:
        """Clean up markdown formatting issues."""
        # Fix heading spacing
        content = re.sub(r'^(#+)\s*(.+)', r'\1 \2', content, flags=re.MULTILINE)
        
        # Fix list formatting
        content = re.sub(r'^(\s*)([*+-])\s*(.+)', r'\1\2 \3', content, flags=re.MULTILINE)
        content = re.sub(r'^(\s*)(\d+\.)\s*(.+)', r'\1\2 \3', content, flags=re.MULTILINE)
        
        # Clean up emphasis
        content = re.sub(r'\*{3,}', '***', content)  # Triple+ asterisks to triple
        content = re.sub(r'_{3,}', '___', content)   # Triple+ underscores to triple
        
        # Fix link formatting
        content = re.sub(r'\[\s*([^\]]+)\s*\]\s*\(\s*([^)]+)\s*\)', r'[\1](\2)', content)
        
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        return content

    def _remove_empty_sections(self, content: str) -> str:
        """Remove empty sections and excessive line breaks."""
        # Remove multiple consecutive empty lines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remove empty sections (headings with no content)
        content = re.sub(r'^(#+\s*.+)\n\s*\n(#+\s*.+)', r'\1\n\n\2', content, flags=re.MULTILINE)
        
        return content

    def extract_metadata(self, content: str) -> tuple[str, dict]:
        """Extract YAML front matter if present."""
        metadata = {}
        
        # Check for YAML front matter
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(yaml_pattern, content, re.DOTALL)
        
        if match:
            try:
                import yaml
                metadata = yaml.safe_load(match.group(1)) or {}
                content = content[match.end():]
                logger.debug(f"📋 Extracted metadata: {list(metadata.keys())}")
            except ImportError:
                logger.warning("⚠️ YAML library not available for front matter parsing")
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse YAML front matter: {e}")
        
        return content, metadata

    def extract_sections(self, content: str) -> list[dict]:
        """Extract sections from markdown content."""
        sections = []
        
        # Split by headings
        heading_pattern = r'^(#+)\s*(.+)$'
        lines = content.split('\n')
        
        current_section = {
            'level': 0,
            'title': 'Introduction',
            'content': []
        }
        
        for line in lines:
            heading_match = re.match(heading_pattern, line)
            
            if heading_match:
                # Save previous section if it has content
                if current_section['content']:
                    current_section['content'] = '\n'.join(current_section['content']).strip()
                    if current_section['content']:
                        sections.append(current_section.copy())
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                current_section = {
                    'level': level,
                    'title': title,
                    'content': []
                }
            else:
                current_section['content'].append(line)
        
        # Add final section
        if current_section['content']:
            current_section['content'] = '\n'.join(current_section['content']).strip()
            if current_section['content']:
                sections.append(current_section)
        
        logger.debug(f"📄 Extracted {len(sections)} sections")
        return sections

    def to_plain_text(self, content: str) -> str:
        """Convert markdown to plain text."""
        try:
            # Convert markdown to HTML first
            html = self.markdown_processor.convert(content)
            
            # Parse HTML and extract text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove code blocks content (keep structure but simplify)
            for code_block in soup.find_all(['pre', 'code']):
                code_block.string = '[CODE]'
            
            # Get text content
            plain_text = soup.get_text()
            
            # Clean up whitespace
            plain_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', plain_text)
            plain_text = plain_text.strip()
            
            logger.debug(f"📝 Converted to plain text ({len(plain_text)} chars)")
            return plain_text

        except Exception as e:
            logger.error(f"❌ Failed to convert to plain text: {e}")
            # Return cleaned markdown as fallback
            return self.clean_content(content)

    def get_word_count(self, content: str) -> int:
        """Get word count of content."""
        plain_text = self.to_plain_text(content)
        words = re.findall(r'\b\w+\b', plain_text)
        return len(words)

    def get_summary(self, content: str, max_length: int = 200) -> str:
        """Get a summary of the content."""
        plain_text = self.to_plain_text(content)
        
        if len(plain_text) <= max_length:
            return plain_text
        
        # Find good break point (sentence end)
        summary = plain_text[:max_length]
        last_period = summary.rfind('.')
        last_question = summary.rfind('?')
        last_exclamation = summary.rfind('!')
        
        break_point = max(last_period, last_question, last_exclamation)
        
        if break_point > max_length * 0.7:  # If we found a good break point
            summary = summary[:break_point + 1]
        else:
            # Break at word boundary
            summary = summary[:summary.rfind(' ')] + '...'
        
        return summary.strip()
    
    async def scan_directory_for_markdown(
        self, 
        directory: str = "./", 
        recursive: bool = True
    ) -> List[Dict[str, str]]:
        """Scan directory for markdown files.
        
        Args:
            directory: Directory path to scan (default current directory)
            recursive: Whether to scan subdirectories
            
        Returns:
            List of dictionaries containing file info: path, name, size
        """
        try:
            directory_path = Path(directory).resolve()
            if not directory_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            if not directory_path.is_dir():
                raise ValueError(f"Path is not a directory: {directory}")
            
            markdown_files = []
            pattern = "**/*.md" if recursive else "*.md"
            
            for file_path in directory_path.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in ['.md', '.markdown']:
                    file_info = {
                        'path': str(file_path),
                        'name': file_path.name,
                        'relative_path': str(file_path.relative_to(directory_path)),
                        'size': file_path.stat().st_size,
                        'directory': str(file_path.parent)
                    }
                    markdown_files.append(file_info)
            
            # Also check for alternative patterns if recursive
            if recursive:
                for ext in ['.markdown']:
                    pattern = f"**/*{ext}"
                    for file_path in directory_path.glob(pattern):
                        if file_path.is_file():
                            # Check if we already have this file
                            if not any(f['path'] == str(file_path) for f in markdown_files):
                                file_info = {
                                    'path': str(file_path),
                                    'name': file_path.name,
                                    'relative_path': str(file_path.relative_to(directory_path)),
                                    'size': file_path.stat().st_size,
                                    'directory': str(file_path.parent)
                                }
                                markdown_files.append(file_info)
            
            logger.info(
                f"📂 Found {len(markdown_files)} markdown files in {directory}" + 
                (" (recursive)" if recursive else "")
            )
            return sorted(markdown_files, key=lambda x: x['path'])
            
        except Exception as e:
            logger.error(f"❌ Failed to scan directory {directory}: {e}")
            raise