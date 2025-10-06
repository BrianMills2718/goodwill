# Default Configuration Provider
"""
Provides default configuration values for the autonomous TDD system.
Based on configuration schema established in pseudo_src/utils/configuration_manager.py
"""

from typing import Dict, Any
from pathlib import Path

def get_default_configuration() -> Dict[str, Any]:
    """
    Get default configuration for autonomous TDD system
    
    Returns:
        Dictionary with default configuration values
    """
    
    return {
        "system": {
            "project_root": ".",
            "log_level": "INFO",
            "debug_mode": False,
            "max_memory_mb": 2048,
            "timeout_seconds": 300
        },
        "llm": {
            "max_context_tokens": 150000,  # Conservative limit
            "max_response_tokens": 4000,
            "temperature": 0.1,
            "max_retries": 3
        },
        "evidence": {
            "evidence_directory": ".autonomous_state/evidence",
            "max_evidence_files": 1000,
            "compression_enabled": True
        },
        "context": {
            "max_files_loaded": 50,
            "cache_size": 100,
            "cross_reference_depth": 3
        },
        "hooks": {
            "stop_hook_enabled": True,
            "hook_timeout_seconds": 30,
            "max_hook_iterations": 10
        },
        "safety": {
            "max_micro_iterations": 5,
            "max_macro_iterations": 3,
            "emergency_stop_threshold": 15,
            "backup_enabled": True
        }
    }

def get_environment_variable_mapping() -> Dict[str, str]:
    """
    Get mapping of environment variables to configuration keys
    
    Returns:
        Dictionary mapping environment variable names to config keys
    """
    
    return {
        "AUTONOMOUS_TDD_PROJECT_ROOT": "system.project_root",
        "AUTONOMOUS_TDD_LOG_LEVEL": "system.log_level", 
        "AUTONOMOUS_TDD_DEBUG_MODE": "system.debug_mode",
        "AUTONOMOUS_TDD_MAX_MEMORY_MB": "system.max_memory_mb",
        "AUTONOMOUS_TDD_TIMEOUT_SECONDS": "system.timeout_seconds",
        "AUTONOMOUS_TDD_MAX_CONTEXT_TOKENS": "llm.max_context_tokens",
        "AUTONOMOUS_TDD_MAX_RESPONSE_TOKENS": "llm.max_response_tokens",
        "AUTONOMOUS_TDD_TEMPERATURE": "llm.temperature",
        "AUTONOMOUS_TDD_MAX_RETRIES": "llm.max_retries",
        "AUTONOMOUS_TDD_EVIDENCE_DIR": "evidence.evidence_directory",
        "AUTONOMOUS_TDD_MAX_EVIDENCE_FILES": "evidence.max_evidence_files",
        "AUTONOMOUS_TDD_COMPRESSION": "evidence.compression_enabled"
    }