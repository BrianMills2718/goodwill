# Logging Setup for Autonomous TDD System
"""
Provides structured logging setup for the autonomous TDD system.
Supports different log levels, structured JSON logging, and file/console output.
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class StructuredJSONFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger_name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
        
        # Add autonomous system context if present
        if hasattr(record, 'task_id'):
            log_entry['task_id'] = record.task_id
        if hasattr(record, 'phase'):
            log_entry['phase'] = record.phase
        if hasattr(record, 'iteration_count'):
            log_entry['iteration_count'] = record.iteration_count
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_json_format: bool = False,
    max_file_size_mb: int = 10,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging for the autonomous TDD system
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (if None, no file logging)
        enable_console: Enable console logging
        enable_json_format: Use structured JSON format
        max_file_size_mb: Maximum log file size in MB
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured root logger
    """
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    if enable_json_format:
        formatter = StructuredJSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

def get_logger(name: str, extra_context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get logger with optional autonomous system context
    
    Args:
        name: Logger name (usually __name__)
        extra_context: Extra context to include in all log messages
        
    Returns:
        Logger instance with optional context
    """
    
    logger = logging.getLogger(name)
    
    # Add extra context if provided
    if extra_context:
        logger = ContextualLogger(logger, extra_context)
    
    return logger

class ContextualLogger:
    """Logger wrapper that adds contextual information to all log messages"""
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        self._logger = logger
        self._context = context
    
    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log message with added context"""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # Add contextual information
        kwargs['extra'].update(self._context)
        
        self._logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        kwargs['exc_info'] = True
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)

# Convenience function for autonomous system logging
def log_autonomous_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    task_id: Optional[str] = None,
    phase: Optional[str] = None,
    iteration_count: Optional[int] = None,
    extra_data: Optional[Dict[str, Any]] = None
):
    """
    Log autonomous system event with structured context
    
    Args:
        logger: Logger instance
        event_type: Type of event (task_start, decision_made, error_occurred, etc.)
        message: Log message
        task_id: Current task ID
        phase: Current methodology phase
        iteration_count: Current iteration count
        extra_data: Additional data to include
    """
    
    # Build extra context
    extra = {
        'event_type': event_type
    }
    
    if task_id:
        extra['task_id'] = task_id
    if phase:
        extra['phase'] = phase
    if iteration_count is not None:
        extra['iteration_count'] = iteration_count
    if extra_data:
        extra['extra_data'] = extra_data
    
    logger.info(message, extra=extra)