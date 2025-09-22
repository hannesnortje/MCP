"""
Enhanced error handling system with retry logic and recovery mechanisms.
Provides robust error handling for production environments.
"""

import asyncio
import logging
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors for different handling strategies."""
    NETWORK = "network"
    EMBEDDING = "embedding"
    QDRANT = "qdrant"
    VALIDATION = "validation"
    SYSTEM = "system"
    MEMORY = "memory"
    TIMEOUT = "timeout"


class ErrorSeverity(Enum):
    """Severity levels for error classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: Tuple[type, ...] = (Exception,)


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: float
    retry_count: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ErrorHandler:
    """Enhanced error handling with retry logic and recovery mechanisms."""

    def __init__(self):
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }
        self.circuit_breakers = {}
        
    def retry_with_backoff(
        self, 
        retry_config: RetryConfig = None,
        error_category: ErrorCategory = ErrorCategory.SYSTEM,
        error_severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ):
        """Decorator for retry logic with exponential backoff."""
        if retry_config is None:
            retry_config = RetryConfig()
            
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                context = ErrorContext(
                    operation=func.__name__,
                    category=error_category,
                    severity=error_severity,
                    timestamp=time.time()
                )
                
                last_exception = None
                
                for attempt in range(retry_config.max_attempts):
                    context.retry_count = attempt
                    
                    try:
                        return await func(*args, **kwargs)
                    except retry_config.retryable_exceptions as e:
                        last_exception = e
                        
                        if attempt == retry_config.max_attempts - 1:
                            # Final attempt failed
                            await self._handle_final_failure(context, e)
                            raise e
                        
                        # Calculate delay with exponential backoff
                        delay = min(
                            retry_config.base_delay * (
                                retry_config.exponential_base ** attempt
                            ),
                            retry_config.max_delay
                        )
                        
                        # Add jitter to prevent thundering herd
                        if retry_config.jitter:
                            import random
                            delay *= (0.5 + 0.5 * random.random())
                        
                        await self._handle_retry_attempt(context, e, delay)
                        await asyncio.sleep(delay)
                
                # This should never be reached, but just in case
                raise last_exception
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                context = ErrorContext(
                    operation=func.__name__,
                    category=error_category,
                    severity=error_severity,
                    timestamp=time.time()
                )
                
                last_exception = None
                
                for attempt in range(retry_config.max_attempts):
                    context.retry_count = attempt
                    
                    try:
                        return func(*args, **kwargs)
                    except retry_config.retryable_exceptions as e:
                        last_exception = e
                        
                        if attempt == retry_config.max_attempts - 1:
                            # Final attempt failed
                            self._handle_final_failure_sync(context, e)
                            raise e
                        
                        # Calculate delay with exponential backoff
                        delay = min(
                            retry_config.base_delay * (
                                retry_config.exponential_base ** attempt
                            ),
                            retry_config.max_delay
                        )
                        
                        # Add jitter
                        if retry_config.jitter:
                            import random
                            delay *= (0.5 + 0.5 * random.random())
                        
                        self._handle_retry_attempt_sync(context, e, delay)
                        time.sleep(delay)
                
                raise last_exception
                
            # Return the appropriate wrapper based on whether the function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator

    async def _handle_retry_attempt(
        self, 
        context: ErrorContext, 
        exception: Exception, 
        delay: float
    ):
        """Handle a retry attempt."""
        self.error_stats["recovery_attempts"] += 1
        
        logger.warning(
            f"Retry attempt {context.retry_count + 1} for {context.operation} "
            f"after {exception.__class__.__name__}: {str(exception)}. "
            f"Waiting {delay:.2f}s before retry."
        )
        
        # Log additional context for debugging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Error context: category={context.category.value}, "
                f"severity={context.severity.value}, "
                f"metadata={context.metadata}"
            )

    def _handle_retry_attempt_sync(
        self, 
        context: ErrorContext, 
        exception: Exception, 
        delay: float
    ):
        """Synchronous version of retry attempt handling."""
        self.error_stats["recovery_attempts"] += 1
        
        logger.warning(
            f"Retry attempt {context.retry_count + 1} for {context.operation} "
            f"after {exception.__class__.__name__}: {str(exception)}. "
            f"Waiting {delay:.2f}s before retry."
        )

    async def _handle_final_failure(
        self, 
        context: ErrorContext, 
        exception: Exception
    ):
        """Handle final failure after all retries exhausted."""
        self._record_error_stats(context)
        
        logger.error(
            f"Operation {context.operation} failed after "
            f"{context.retry_count + 1} attempts. "
            f"Final error: {exception.__class__.__name__}: {str(exception)}"
        )
        
        # Log full traceback for debugging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        # Attempt recovery based on error category
        await self._attempt_recovery(context, exception)

    def _handle_final_failure_sync(
        self, 
        context: ErrorContext, 
        exception: Exception
    ):
        """Synchronous version of final failure handling."""
        self._record_error_stats(context)
        
        logger.error(
            f"Operation {context.operation} failed after "
            f"{context.retry_count + 1} attempts. "
            f"Final error: {exception.__class__.__name__}: {str(exception)}"
        )

    def _record_error_stats(self, context: ErrorContext):
        """Record error statistics for monitoring."""
        self.error_stats["total_errors"] += 1
        
        category_key = context.category.value
        if category_key not in self.error_stats["errors_by_category"]:
            self.error_stats["errors_by_category"][category_key] = 0
        self.error_stats["errors_by_category"][category_key] += 1
        
        severity_key = context.severity.value
        if severity_key not in self.error_stats["errors_by_severity"]:
            self.error_stats["errors_by_severity"][severity_key] = 0
        self.error_stats["errors_by_severity"][severity_key] += 1

    async def _attempt_recovery(
        self, 
        context: ErrorContext, 
        exception: Exception
    ):
        """Attempt recovery based on error category."""
        recovery_attempted = False
        
        try:
            if context.category == ErrorCategory.QDRANT:
                await self._recover_qdrant_connection()
                recovery_attempted = True
            elif context.category == ErrorCategory.EMBEDDING:
                await self._recover_embedding_model()
                recovery_attempted = True
            elif context.category == ErrorCategory.NETWORK:
                await self._recover_network_connection()
                recovery_attempted = True
            
            if recovery_attempted:
                self.error_stats["successful_recoveries"] += 1
                logger.info(
                    f"Recovery attempt completed for {context.operation} "
                    f"({context.category.value})"
                )
                
        except Exception as recovery_error:
            logger.error(
                f"Recovery attempt failed for {context.operation}: "
                f"{recovery_error.__class__.__name__}: {str(recovery_error)}"
            )

    async def _recover_qdrant_connection(self):
        """Attempt to recover Qdrant connection."""
        logger.info("Attempting Qdrant connection recovery...")
        
        # Import here to avoid circular imports
        from .qdrant_manager import ensure_qdrant_running
        
        # Try to restart Qdrant if needed
        if not ensure_qdrant_running():
            raise Exception("Failed to recover Qdrant connection")
        
        # Give Qdrant time to fully start
        await asyncio.sleep(2)

    async def _recover_embedding_model(self):
        """Attempt to recover embedding model."""
        logger.info("Attempting embedding model recovery...")
        
        # This would involve reinitializing the embedding model
        # Implementation depends on the specific model being used
        await asyncio.sleep(1)  # Placeholder for actual recovery logic

    async def _recover_network_connection(self):
        """Attempt to recover network connection."""
        logger.info("Attempting network connection recovery...")
        
        # This would involve network connectivity checks and recovery
        await asyncio.sleep(1)  # Placeholder for actual recovery logic

    def get_error_stats(self) -> Dict[str, Any]:
        """Get current error statistics."""
        return self.error_stats.copy()

    def reset_error_stats(self):
        """Reset error statistics."""
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }


# Global error handler instance
error_handler = ErrorHandler()


# Convenience decorators for common retry patterns
def retry_embedding_operation(max_attempts: int = 3):
    """Decorator for embedding operations with appropriate retry config."""
    return error_handler.retry_with_backoff(
        RetryConfig(
            max_attempts=max_attempts,
            base_delay=2.0,
            max_delay=60.0,
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
                RuntimeError,
                Exception  # Embedding models can throw various exceptions
            )
        ),
        error_category=ErrorCategory.EMBEDDING,
        error_severity=ErrorSeverity.MEDIUM
    )


def retry_qdrant_operation(max_attempts: int = 3):
    """Decorator for Qdrant operations with appropriate retry config."""
    return error_handler.retry_with_backoff(
        RetryConfig(
            max_attempts=max_attempts,
            base_delay=1.0,
            max_delay=30.0,
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
                RuntimeError
            )
        ),
        error_category=ErrorCategory.QDRANT,
        error_severity=ErrorSeverity.HIGH
    )


def retry_network_operation(max_attempts: int = 5):
    """Decorator for network operations with appropriate retry config."""
    return error_handler.retry_with_backoff(
        RetryConfig(
            max_attempts=max_attempts,
            base_delay=0.5,
            max_delay=10.0,
            retryable_exceptions=(
                ConnectionError,
                TimeoutError,
                OSError
            )
        ),
        error_category=ErrorCategory.NETWORK,
        error_severity=ErrorSeverity.MEDIUM
    )