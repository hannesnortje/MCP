"""
Enhanced Markdown processor for MCP Memory Server.
Handles reading, cleaning, chunking, and optimizing markdown files with AI integration.
"""

import logging
import re
import hashlib
from typing import Optional, List, Dict, Tuple, Union
from pathlib import Path
import aiofiles
from bs4 import BeautifulSoup
import markdown

logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """Processes markdown files for memory storage with AI integration hooks."""

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

            logger.info(f"📖 Read markdown file: {file_path} "
                       f"({len(content)} chars)")
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
        # Replace multiple spaces with single space
        # (except at line start for indentation)
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
        content = re.sub(r'^(#+)\s*(.+)', r'\1 \2', content,
                        flags=re.MULTILINE)
        
        # Fix list formatting
        content = re.sub(r'^(\s*)([*+-])\s*(.+)', r'\1\2 \3', content,
                        flags=re.MULTILINE)
        content = re.sub(r'^(\s*)(\d+\.)\s*(.+)', r'\1\2 \3', content,
                        flags=re.MULTILINE)
        
        # Clean up emphasis
        content = re.sub(r'\*{3,}', '***', content)
        content = re.sub(r'_{3,}', '___', content)
        
        # Fix link formatting
        content = re.sub(r'\[\s*([^\]]+)\s*\]\s*\(\s*([^)]+)\s*\)',
                        r'[\1](\2)', content)
        
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        return content

    def _remove_empty_sections(self, content: str) -> str:
        """Remove empty sections and excessive line breaks."""
        # Remove multiple consecutive empty lines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remove empty sections (headings with no content)
        content = re.sub(r'^(#+\s*.+)\n\s*\n(#+\s*.+)', r'\1\n\n\2',
                        content, flags=re.MULTILINE)
        
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
                logger.warning("⚠️ YAML library not available "
                             "for front matter parsing")
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
                    current_section['content'] = '\n'.join(
                        current_section['content']).strip()
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
            current_section['content'] = '\n'.join(
                current_section['content']).strip()
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

    # New Methods for Step 1 Implementation

    async def scan_directory_for_markdown(
        self, 
        directory: str = "./", 
        recursive: bool = True
    ) -> List[Dict[str, Union[str, int]]]:
        """Scan directory for markdown files.
        
        Args:
            directory: Directory path to scan (default current directory)
            recursive: Whether to scan subdirectories
            
        Returns:
            List of dictionaries containing file info
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
                if (file_path.is_file() and 
                    file_path.suffix.lower() in ['.md', '.markdown']):
                    file_info = {
                        'path': str(file_path),
                        'name': file_path.name,
                        'relative_path': str(
                            file_path.relative_to(directory_path)),
                        'size': file_path.stat().st_size,
                        'directory': str(file_path.parent)
                    }
                    markdown_files.append(file_info)
            
            # Also check for .markdown extension if recursive
            if recursive:
                for file_path in directory_path.glob("**/*.markdown"):
                    if file_path.is_file():
                        # Check if we already have this file
                        if not any(f['path'] == str(file_path) 
                                 for f in markdown_files):
                            file_info = {
                                'path': str(file_path),
                                'name': file_path.name,
                                'relative_path': str(
                                    file_path.relative_to(directory_path)),
                                'size': file_path.stat().st_size,
                                'directory': str(file_path.parent)
                            }
                            markdown_files.append(file_info)
            
            logger.info(
                f"📂 Found {len(markdown_files)} markdown files in "
                f"{directory}" + (" (recursive)" if recursive else "")
            )
            return sorted(markdown_files, key=lambda x: x['path'])
            
        except Exception as e:
            logger.error(f"❌ Failed to scan directory {directory}: {e}")
            raise

    def analyze_content_for_memory_type(
        self, 
        content: str, 
        file_path: Optional[str] = None,
        suggest_memory_type: bool = True
    ) -> Dict[str, Union[str, float, Dict, bool]]:
        """Analyze markdown content and suggest appropriate memory type.
        
        This method provides AI integration hooks for Cursor AI to enhance 
        analysis.
        
        Args:
            content: Markdown content to analyze
            file_path: Optional file path for context
            suggest_memory_type: Whether to suggest memory type
            
        Returns:
            Dictionary containing analysis results and memory type suggestion
        """
        try:
            analysis = {
                'content_length': len(content),
                'word_count': self.get_word_count(content),
                'sections': len(self.extract_sections(content)),
                'has_code_blocks': '```' in content,
                'has_links': '[' in content and '](' in content,
                'has_tables': '|' in content,
                'suggested_memory_type': 'global',  # Default suggestion
                'confidence': 0.7,  # Default confidence
                'reasoning': '',
                'ai_enhanced': False  # Flag for AI enhancement
            }
            
            if suggest_memory_type:
                # Basic heuristic-based suggestion (AI can enhance this)
                suggested_type, confidence, reasoning = (
                    self._suggest_memory_type_heuristic(content, file_path)
                )
                analysis.update({
                    'suggested_memory_type': suggested_type,
                    'confidence': confidence,
                    'reasoning': reasoning
                })
            
            # AI Integration Hook: Cursor AI can enhance this analysis
            # The AI can improve memory type suggestions, reasoning, and 
            # content optimization. This provides a foundation for AI-driven 
            # content categorization
            
            logger.debug(
                f"🧠 Content analysis complete: "
                f"{analysis['suggested_memory_type']} "
                f"(confidence: {analysis['confidence']:.2f})"
            )
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze content: {e}")
            return {
                'suggested_memory_type': 'global',
                'confidence': 0.5,
                'reasoning': 'Analysis failed, defaulting to global',
                'error': str(e)
            }

    def _suggest_memory_type_heuristic(
        self, 
        content: str, 
        file_path: Optional[str] = None
    ) -> Tuple[str, float, str]:
        """Basic heuristic for memory type suggestion (AI can enhance this).
        
        Args:
            content: Content to analyze
            file_path: Optional file path for additional context
            
        Returns:
            Tuple of (suggested_type, confidence, reasoning)
        """
        content_lower = content.lower()
        
        # File path based hints
        if file_path:
            path_lower = file_path.lower()
            if any(term in path_lower for term in 
                  ['readme', 'doc', 'guide', 'manual', 'spec']):
                return ('global', 0.8, 'Documentation or reference material')
            if any(term in path_lower for term in 
                  ['lesson', 'learn', 'pattern', 'best', 'practice']):
                return ('learned', 0.8, 'Lessons learned or best practices')
            if any(term in path_lower for term in 
                  ['personal', 'agent', 'task', 'todo', 'scratch']):
                return ('agent', 0.8, 'Agent-specific or personal content')
        
        # Content-based analysis
        global_indicators = [
            'documentation', 'specification', 'standard', 
            'reference', 'api', 'protocol'
        ]
        learned_indicators = [
            'lesson', 'pattern', 'insight', 'mistake', 
            'experience', 'learned', 'practice'
        ]
        agent_indicators = [
            'todo', 'task', 'personal', 'scratch', 'note', 'draft'
        ]
        
        global_score = sum(1 for term in global_indicators 
                          if term in content_lower)
        learned_score = sum(1 for term in learned_indicators 
                           if term in content_lower)
        agent_score = sum(1 for term in agent_indicators 
                         if term in content_lower)
        
        if learned_score > global_score and learned_score > agent_score:
            return ('learned', 0.7, 
                   f'Contains learning indicators: {learned_score}')
        elif agent_score > global_score and agent_score > learned_score:
            return ('agent', 0.7, 
                   f'Contains agent-specific indicators: {agent_score}')
        else:
            return ('global', 0.6, 'Default to global for reference material')

    def optimize_content_for_storage(
        self, 
        content: str, 
        memory_type: str,
        ai_optimization: bool = True, 
        suggested_type: Optional[str] = None
    ) -> Dict[str, Union[str, bool, int]]:
        """Optimize content for database storage with AI enhancement hooks.
        
        This method provides integration points for Cursor AI to enhance 
        content optimization based on the target memory type.
        
        Args:
            content: Content to optimize
            memory_type: Target memory type (global, learned, agent)
            ai_optimization: Whether to apply AI-driven optimizations
            suggested_type: Originally suggested memory type for comparison
            
        Returns:
            Dictionary with optimized content and metadata
        """
        try:
            # Start with cleaned content
            optimized_content = self.clean_content(content)
            
            # Basic optimization based on memory type
            if memory_type == 'learned':
                # For learned memory, emphasize insights and patterns
                optimized_content = self._optimize_for_learned_memory(
                    optimized_content)
            elif memory_type == 'agent':
                # For agent memory, preserve personal context and tasks
                optimized_content = self._optimize_for_agent_memory(
                    optimized_content)
            else:  # global
                # For global memory, focus on reference and documentation
                optimized_content = self._optimize_for_global_memory(
                    optimized_content)
            
            result = {
                'optimized_content': optimized_content,
                'memory_type': memory_type,
                'original_length': len(content),
                'optimized_length': len(optimized_content),
                'ai_enhanced': ai_optimization,
                'optimization_applied': f'{memory_type}_optimization',
                'suggested_type_override': (
                    suggested_type != memory_type if suggested_type else False
                )
            }
            
            # AI Integration Hook: Cursor AI can enhance content optimization
            # here. The AI can improve content structure, add semantic tags,
            # enhance searchability while preserving the original meaning
            # and context
            
            logger.debug(
                f"🔧 Content optimized for {memory_type} storage "
                f"({len(content)} → {len(optimized_content)} chars)"
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize content: {e}")
            return {
                'optimized_content': content,  # Return original on failure
                'memory_type': memory_type,
                'error': str(e)
            }

    def _optimize_for_learned_memory(self, content: str) -> str:
        """Optimize content for learned memory storage."""
        # Emphasize lessons, insights, and patterns
        # AI can enhance this to better identify and highlight learning points
        return content

    def _optimize_for_agent_memory(self, content: str) -> str:
        """Optimize content for agent-specific memory storage."""
        # Preserve personal context and actionable items
        # AI can enhance this to better identify tasks and personal references
        return content

    def _optimize_for_global_memory(self, content: str) -> str:
        """Optimize content for global memory storage."""
        # Focus on reference value and documentation clarity
        # AI can enhance this to improve searchability and reference utility
        return content

    # Chunking Methods

    def chunk_content(
        self, 
        content: str, 
        preserve_headers: bool = True
    ) -> List[Dict[str, Union[str, int]]]:
        """Chunk content into smaller pieces with AI-optimized boundaries.
        
        Args:
            content: Content to chunk
            preserve_headers: Whether to preserve header context in chunks
            
        Returns:
            List of chunk dictionaries with content, index, and metadata
        """
        try:
            chunks = []
            
            # Handle empty content
            if not content or not content.strip():
                return [{
                    'content': '',
                    'chunk_index': 0,
                    'token_count': 0
                }]
            
            if preserve_headers:
                # Header-aware chunking
                sections = self.extract_sections(content)
                
                for section in sections:
                    section_content = f"# {section['title']}\n\n{section['content']}"
                    section_chunks = self._split_text_by_tokens(section_content)
                    
                    for i, chunk_text in enumerate(section_chunks):
                        chunks.append({
                            'content': chunk_text,
                            'chunk_index': len(chunks),
                            'section_title': section['title'],
                            'section_level': section['level'],
                            'section_chunk_index': i,
                            'token_count': self._estimate_tokens(chunk_text)
                        })
            else:
                # Simple text chunking
                chunk_texts = self._split_text_by_tokens(content)
                
                for i, chunk_text in enumerate(chunk_texts):
                    chunks.append({
                        'content': chunk_text,
                        'chunk_index': i,
                        'token_count': self._estimate_tokens(chunk_text)
                    })
            
            logger.debug(f"📄 Created {len(chunks)} chunks from content")
            return chunks
            
        except Exception as e:
            logger.error(f"❌ Failed to chunk content: {e}")
            # Return single chunk on failure
            return [{
                'content': content,
                'chunk_index': 0,
                'token_count': self._estimate_tokens(content),
                'error': str(e)
            }]

    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count (approximately 4 chars per token)."""
        return len(text) // 4

    def _split_text_by_tokens(self, text: str) -> List[str]:
        """Split text into chunks based on estimated token count."""
        estimated_tokens = self._estimate_tokens(text)
        
        if estimated_tokens <= self.chunk_size:
            return [text]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            
            if (current_tokens + sentence_tokens > self.chunk_size and 
                current_chunk):
                # Add current chunk and start new one with overlap
                chunks.append(current_chunk.strip())
                
                # Create overlap by keeping last part of current chunk
                overlap_text = self._get_overlap_text(
                    current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + " " + sentence
                current_tokens = self._estimate_tokens(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def _get_overlap_text(self, text: str, max_overlap_tokens: int) -> str:
        """Get overlap text from the end of a chunk."""
        overlap_chars = max_overlap_tokens * 4  # Rough estimation
        
        if len(text) <= overlap_chars:
            return text
        
        # Find good break point from the end
        overlap_text = text[-overlap_chars:]
        first_space = overlap_text.find(' ')
        
        if first_space > 0:
            return overlap_text[first_space:].strip()
        
        return overlap_text.strip()

    # Policy Processing Methods

    async def scan_policy_directory(
        self, 
        directory: str = "./policy"
    ) -> List[Dict[str, Union[str, int, List[str], bool]]]:
        """Scan policy directory for markdown files with rule validation.
        
        Args:
            directory: Policy directory path (default ./policy)
            
        Returns:
            List of policy file information with rule counts
        """
        try:
            policy_files = await self.scan_directory_for_markdown(
                directory, recursive=False)
            
            for file_info in policy_files:
                # Add policy-specific metadata
                content = await self.read_markdown_file(file_info['path'])
                rules = self.extract_policy_rules(content)
                file_info.update({
                    'rule_count': len(rules),
                    'rule_ids': [rule['rule_id'] for rule in rules],
                    'is_policy_file': True
                })
            
            logger.info(f"📋 Found {len(policy_files)} policy files with rules")
            return policy_files
            
        except Exception as e:
            logger.error(f"❌ Failed to scan policy directory {directory}: {e}")
            raise

    def extract_policy_rules(self, content: str) -> List[Dict[str, str]]:
        """Extract rule IDs and content from policy markdown.
        
        Args:
            content: Policy markdown content
            
        Returns:
            List of rules with IDs, sections, and content
        """
        try:
            rules = []
            sections = self.extract_sections(content)
            
            # Rule ID pattern: [ANY-FORMAT] to capture all potential rules
            rule_pattern = r'\[([A-Z]+(?:-\d+)?[^\]]*)\]\s*(.+?)(?=\n|$)'
            
            for section in sections:
                section_rules = re.finditer(
                    rule_pattern, section['content'], re.MULTILINE)
                
                for match in section_rules:
                    rule_id = match.group(1)
                    rule_text = match.group(2).strip()
                    
                    # Extract full rule context
                    full_content = self._extract_rule_context(
                        section['content'], match.start())
                    
                    rules.append({
                        'rule_id': rule_id,
                        'section': section['title'],
                        'section_level': section['level'],
                        'rule_text': rule_text,
                        'full_content': full_content,
                        'position': len(rules)
                    })
            
            logger.debug(f"📋 Extracted {len(rules)} policy rules")
            return rules
            
        except Exception as e:
            logger.error(f"❌ Failed to extract policy rules: {e}")
            return []

    def _extract_rule_context(self, content: str, rule_start_pos: int) -> str:
        """Extract full context for a policy rule."""
        lines = content[rule_start_pos:].split('\n')
        context_lines = []
        
        for line in lines:
            # Stop at next rule or empty lines that might indicate section break
            if (len(context_lines) > 0 and 
                (re.match(r'\[([A-Z]+-\d+)\]', line) or 
                 (line.strip() == '' and len(context_lines) > 3))):
                break
            context_lines.append(line)
        
        return '\n'.join(context_lines).strip()

    def validate_policy_rules(
        self, 
        rules: List[Dict[str, str]], 
        policy_version: Optional[str] = None
    ) -> Dict[str, Union[bool, List[str], int, str]]:
        """Validate policy rules for uniqueness and format compliance.
        
        Args:
            rules: List of extracted rules
            policy_version: Optional policy version for tracking
            
        Returns:
            Validation results with success status and any errors
        """
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'rule_count': len(rules),
                'unique_rules': len(set(rule['rule_id'] for rule in rules)),
                'policy_version': policy_version
            }
            
            # Check for duplicate rule IDs
            rule_ids = [rule['rule_id'] for rule in rules]
            duplicates = [rule_id for rule_id in set(rule_ids) 
                         if rule_ids.count(rule_id) > 1]
            
            if duplicates:
                validation_result['valid'] = False
                validation_result['errors'].append(
                    f"Duplicate rule IDs found: {duplicates}")
            
            # Check rule ID format (P-001, F-101, R-201, etc.)
            valid_pattern = re.compile(r'^[A-Z]+-\d+$')
            invalid_ids = [rule['rule_id'] for rule in rules 
                          if not valid_pattern.match(rule['rule_id'])]
            
            if invalid_ids:
                validation_result['valid'] = False
                validation_result['errors'].append(
                    f"Invalid rule ID format: {invalid_ids}")
            
            # Check for empty rules
            empty_rules = [rule['rule_id'] for rule in rules 
                          if not rule['rule_text'].strip()]
            
            if empty_rules:
                validation_result['warnings'].append(
                    f"Empty rules found: {empty_rules}")
            
            logger.debug(
                f"📋 Policy validation: "
                f"{validation_result['unique_rules']}/"
                f"{validation_result['rule_count']} unique rules"
            )
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Failed to validate policy rules: {e}")
            return {
                'valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'rule_count': len(rules) if rules else 0
            }

    def generate_policy_hash(
        self, 
        rules: List[Dict[str, str]], 
        policy_version: str
    ) -> str:
        """Generate SHA-256 hash for policy version.
        
        Args:
            rules: List of policy rules
            policy_version: Version identifier
            
        Returns:
            SHA-256 hash of policy content
        """
        try:
            # Create deterministic string from rules
            rule_strings = []
            for rule in sorted(rules, key=lambda x: x['rule_id']):
                rule_string = (f"{rule['rule_id']}:{rule['section']}:"
                             f"{rule['rule_text']}")
                rule_strings.append(rule_string)
            
            combined_content = f"{policy_version}:{'|'.join(rule_strings)}"
            policy_hash = hashlib.sha256(
                combined_content.encode('utf-8')).hexdigest()
            
            logger.debug(
                f"📋 Generated policy hash: {policy_hash[:8]}... "
                f"for {len(rules)} rules"
            )
            return policy_hash
            
        except Exception as e:
            logger.error(f"❌ Failed to generate policy hash: {e}")
            return ""

    # Batch Processing Methods

    async def process_directory_batch(
        self, 
        directory: str = "./",
        memory_type: Optional[str] = None,
        auto_suggest: bool = True,
        ai_enhance: bool = True,
        recursive: bool = True
    ) -> Dict[str, Union[List[Dict], int, str, Dict[str, int], bool]]:
        """Process entire directory with batch AI-enhanced analysis.
        
        Args:
            directory: Directory to process
            memory_type: Fixed memory type (None for auto-suggestion)
            auto_suggest: Whether to auto-suggest memory types
            ai_enhance: Whether to apply AI enhancements
            recursive: Whether to scan subdirectories
            
        Returns:
            Dictionary with processing results and file analysis
        """
        try:
            # Scan directory for files
            files = await self.scan_directory_for_markdown(directory, recursive)
            
            processing_results = {
                'total_files': len(files),
                'processed_files': [],
                'failed_files': [],
                'memory_type_suggestions': {},
                'directory': directory,
                'recursive': recursive,
                'ai_enhanced': ai_enhance
            }
            
            for file_info in files:
                try:
                    # Read and analyze file
                    content = await self.read_markdown_file(file_info['path'])
                    analysis = self.analyze_content_for_memory_type(
                        content, file_info['path'], auto_suggest
                    )
                    
                    # Use fixed memory type or suggested type
                    final_memory_type = (memory_type or 
                                       analysis.get('suggested_memory_type', 
                                                   'global'))
                    
                    # Optimize content for storage
                    optimization = self.optimize_content_for_storage(
                        content, final_memory_type, ai_enhance, 
                        analysis.get('suggested_memory_type')
                    )
                    
                    # Create file processing result
                    file_result = {
                        **file_info,
                        'analysis': analysis,
                        'optimization': optimization,
                        'final_memory_type': final_memory_type,
                        'processing_status': 'success'
                    }
                    
                    processing_results['processed_files'].append(file_result)
                    
                    # Track memory type suggestions
                    suggested_type = analysis.get('suggested_memory_type', 
                                                 'global')
                    if suggested_type not in processing_results['memory_type_suggestions']:
                        processing_results['memory_type_suggestions'][suggested_type] = 0
                    processing_results['memory_type_suggestions'][suggested_type] += 1
                    
                except Exception as file_error:
                    logger.error(
                        f"❌ Failed to process file {file_info['path']}: "
                        f"{file_error}"
                    )
                    processing_results['failed_files'].append({
                        **file_info,
                        'error': str(file_error),
                        'processing_status': 'failed'
                    })
            
            success_count = len(processing_results['processed_files'])
            logger.info(
                f"📁 Batch processing complete: {success_count}/"
                f"{len(files)} files processed"
            )
            
            return processing_results
            
        except Exception as e:
            logger.error(f"❌ Failed to process directory batch {directory}: {e}")
            return {
                'total_files': 0,
                'processed_files': [],
                'failed_files': [],
                'error': str(e)
            }

    # Utility Methods

    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_file_metadata(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Union[str, int, Optional[float]]]:
        """Generate comprehensive file metadata.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Dictionary with file metadata
        """
        try:
            path = Path(file_path)
            
            metadata = {
                'file_path': str(path.resolve()),
                'file_name': path.name,
                'file_size': len(content.encode('utf-8')),
                'content_hash': self.calculate_content_hash(content),
                'word_count': self.get_word_count(content),
                'section_count': len(self.extract_sections(content)),
                'last_modified': path.stat().st_mtime if path.exists() else None,
                'file_extension': path.suffix,
                'directory': str(path.parent)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to generate file metadata: {e}")
            return {
                'file_path': file_path,
                'error': str(e)
            }