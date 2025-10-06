# Configuration Management Package
"""
Configuration management for the autonomous TDD system.

Provides configuration loading, validation, environment overrides,
and schema management with multiple source support.
"""

from .configuration_manager import ConfigurationManager, ConfigValue, ConfigSchema
from .default_config import get_default_configuration

__all__ = [
    'ConfigurationManager',
    'ConfigValue', 
    'ConfigSchema',
    'get_default_configuration'
]