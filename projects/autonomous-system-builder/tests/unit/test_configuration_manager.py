#!/usr/bin/env python3
"""
Unit tests for Configuration Manager foundation component

LOCKED TESTS: These tests cannot be modified after creation to prevent
anti-fabrication rule violations. Implementation must make these tests pass.

Test Coverage Target: 100% (Foundation component - critical infrastructure)
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.config.configuration_manager import ConfigurationManager
from src.config.configuration_manager import ConfigKeyError, ConfigValidationError

# Alias for test compatibility
ConfigManager = ConfigurationManager
ConfigurationError = ConfigValidationError

class TestConfigManagerInitialization:
    """Test ConfigManager initialization and validation"""
    
    def test_init_with_valid_project_root(self):
        """Test ConfigManager initializes successfully with valid project root"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            
            assert config_manager.project_root == Path(temp_dir)
            assert config_manager.config_dir == Path(temp_dir) / 'config'
            assert config_manager.main_config_file == Path(temp_dir) / 'config' / 'autonomous_config.json'
    
    def test_init_with_empty_project_root_raises_error(self):
        """Test ConfigManager raises error for empty project root"""
        with pytest.raises(ConfigurationError, match="project_root cannot be empty"):
            ConfigManager("")
    
    def test_init_with_nonexistent_project_root_raises_error(self):
        """Test ConfigManager raises error for non-existent project root"""
        non_existent_path = "/tmp/definitely_does_not_exist_12345"
        
        with pytest.raises(ConfigurationError, match="Project root does not exist"):
            ConfigManager(non_existent_path)
    
    def test_init_with_file_as_project_root_raises_error(self):
        """Test ConfigManager raises error when project root is a file"""
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ConfigurationError, match="Project root is not a directory"):
                ConfigManager(temp_file.name)
    
    def test_init_with_read_only_directory_raises_error(self):
        """Test ConfigManager raises error for read-only project root"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Make directory read-only
            os.chmod(temp_dir, 0o444)
            
            try:
                with pytest.raises(ConfigurationError, match="No write permission"):
                    ConfigManager(temp_dir)
            finally:
                # Restore permissions for cleanup
                os.chmod(temp_dir, 0o755)


class TestConfigurationLoading:
    """Test configuration loading with defaults and overrides"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_configuration_with_defaults_only(self):
        """Test loading configuration returns defaults when no config file exists"""
        config = self.config_manager.load_configuration()
        
        # Verify default structure exists
        assert 'autonomous_behavior' in config
        assert 'context_management' in config
        assert 'integration_settings' in config
        assert 'evidence_collection' in config
        assert 'safety_mechanisms' in config
        assert 'logging' in config
        
        # Verify some specific default values
        assert config['autonomous_behavior']['max_hook_iterations'] == 50
        assert config['context_management']['max_context_tokens'] == 150000
        assert config['logging']['log_level'] == 'INFO'
    
    def test_load_configuration_with_main_config_file(self):
        """Test loading configuration merges main config file with defaults"""
        # Create main config file
        main_config = {
            'autonomous_behavior': {
                'max_hook_iterations': 100,  # Override default
                'custom_setting': 'test'     # New setting
            },
            'logging': {
                'log_level': 'DEBUG'         # Override default
            }
        }
        
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        main_config_file = config_dir / 'autonomous_config.json'
        
        with open(main_config_file, 'w') as f:
            json.dump(main_config, f)
        
        config = self.config_manager.load_configuration()
        
        # Verify overrides applied
        assert config['autonomous_behavior']['max_hook_iterations'] == 100
        assert config['autonomous_behavior']['custom_setting'] == 'test'
        assert config['logging']['log_level'] == 'DEBUG'
        
        # Verify defaults preserved
        assert config['context_management']['max_context_tokens'] == 150000
        assert config['evidence_collection']['enable_anti_fabrication'] is True
    
    def test_load_configuration_with_environment_config(self):
        """Test loading configuration includes environment-specific config"""
        # Create main config
        main_config = {'logging': {'log_level': 'INFO'}}
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        
        with open(config_dir / 'autonomous_config.json', 'w') as f:
            json.dump(main_config, f)
        
        # Create environment config
        env_config = {
            'logging': {'log_level': 'DEBUG'},
            'development': {'extra_setting': True}
        }
        
        env_dir = config_dir / 'environments'
        env_dir.mkdir()
        
        with open(env_dir / 'development.json', 'w') as f:
            json.dump(env_config, f)
        
        config = self.config_manager.load_configuration(environment='development')
        
        # Verify environment config overrides main config
        assert config['logging']['log_level'] == 'DEBUG'
        assert config['development']['extra_setting'] is True
    
    def test_load_configuration_with_environment_variables(self):
        """Test loading configuration applies environment variable overrides"""
        env_vars = {
            'AUTONOMOUS_TDD_LOGGING_LOG_LEVEL': 'ERROR',
            'AUTONOMOUS_TDD_AUTONOMOUS_BEHAVIOR_MAX_HOOK_ITERATIONS': '75',
            'AUTONOMOUS_TDD_EVIDENCE_COLLECTION_ENABLE_ANTI_FABRICATION': 'false'
        }
        
        with patch.dict(os.environ, env_vars):
            config = self.config_manager.load_configuration()
        
        # Verify environment variables applied
        assert config['logging']['log_level'] == 'ERROR'
        assert config['autonomous_behavior']['max_hook_iterations'] == 75
        assert config['evidence_collection']['enable_anti_fabrication'] is False
    
    def test_load_configuration_caching(self):
        """Test configuration caching avoids repeated file reads"""
        # First load
        config1 = self.config_manager.load_configuration()
        
        # Second load should use cache
        config2 = self.config_manager.load_configuration()
        
        assert config1 is config2  # Same object, indicating cache hit
    
    def test_load_configuration_cache_invalidation(self):
        """Test configuration cache invalidates when file modified"""
        # Create initial config
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        main_config_file = config_dir / 'autonomous_config.json'
        
        initial_config = {'logging': {'log_level': 'INFO'}}
        with open(main_config_file, 'w') as f:
            json.dump(initial_config, f)
        
        # Load config (creates cache)
        config1 = self.config_manager.load_configuration()
        assert config1['logging']['log_level'] == 'INFO'
        
        # Modify config file
        import time
        time.sleep(0.1)  # Ensure different mtime
        
        updated_config = {'logging': {'log_level': 'DEBUG'}}
        with open(main_config_file, 'w') as f:
            json.dump(updated_config, f)
        
        # Load config again (should reload from file)
        config2 = self.config_manager.load_configuration()
        assert config2['logging']['log_level'] == 'DEBUG'
    
    def test_load_configuration_invalid_main_config_raises_error(self):
        """Test invalid main config file raises ConfigurationError"""
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        main_config_file = config_dir / 'autonomous_config.json'
        
        # Write invalid JSON
        with open(main_config_file, 'w') as f:
            f.write('{ invalid json content')
        
        with pytest.raises(ConfigurationError, match="Failed to load main config"):
            self.config_manager.load_configuration()
    
    def test_load_configuration_invalid_environment_config_raises_error(self):
        """Test invalid environment config file raises ConfigurationError"""
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        
        # Create valid main config
        with open(config_dir / 'autonomous_config.json', 'w') as f:
            json.dump({'logging': {'log_level': 'INFO'}}, f)
        
        # Create invalid environment config
        env_dir = config_dir / 'environments'
        env_dir.mkdir()
        
        with open(env_dir / 'test.json', 'w') as f:
            f.write('{ invalid json content')
        
        with pytest.raises(ConfigurationError, match="Failed to load environment config"):
            self.config_manager.load_configuration(environment='test')


class TestConfigurationSaving:
    """Test configuration saving operations"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_configuration_main_config(self):
        """Test saving configuration to main config file"""
        test_config = {
            'autonomous_behavior': {'max_hook_iterations': 100},
            'logging': {'log_level': 'DEBUG'},
            'context_management': {'max_context_tokens': 200000},
            'integration_settings': {'claude_code_timeout_seconds': 60},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True}
        }
        
        result = self.config_manager.save_configuration(test_config)
        assert result is True
        
        # Verify file was created
        main_config_file = Path(self.temp_dir) / 'config' / 'autonomous_config.json'
        assert main_config_file.exists()
        
        # Verify content is correct
        with open(main_config_file, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == test_config
    
    def test_save_configuration_environment_config(self):
        """Test saving configuration to environment-specific file"""
        test_config = {
            'autonomous_behavior': {'max_hook_iterations': 25},
            'logging': {'log_level': 'DEBUG'},
            'context_management': {'max_context_tokens': 100000},
            'integration_settings': {'claude_code_timeout_seconds': 10},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True}
        }
        
        result = self.config_manager.save_configuration(test_config, environment='testing')
        assert result is True
        
        # Verify file was created in environments directory
        env_config_file = Path(self.temp_dir) / 'config' / 'environments' / 'testing.json'
        assert env_config_file.exists()
        
        # Verify content is correct
        with open(env_config_file, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == test_config
    
    def test_save_configuration_creates_backup(self):
        """Test saving configuration creates backup of existing file"""
        # Create initial config
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        main_config_file = config_dir / 'autonomous_config.json'
        
        initial_config = {'logging': {'log_level': 'INFO'}}
        with open(main_config_file, 'w') as f:
            json.dump(initial_config, f)
        
        # Save new config
        new_config = {
            'autonomous_behavior': {'max_hook_iterations': 50},
            'logging': {'log_level': 'DEBUG'},
            'context_management': {'max_context_tokens': 150000},
            'integration_settings': {'claude_code_timeout_seconds': 30},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True}
        }
        
        result = self.config_manager.save_configuration(new_config)
        assert result is True
        
        # Verify backup was created
        backup_file = config_dir / 'autonomous_config.json.backup'
        assert backup_file.exists()
        
        # Verify backup contains original config
        with open(backup_file, 'r') as f:
            backup_config = json.load(f)
        assert backup_config == initial_config
        
        # Verify main file contains new config
        with open(main_config_file, 'r') as f:
            current_config = json.load(f)
        assert current_config == new_config
    
    def test_save_configuration_atomic_operation(self):
        """Test configuration save is atomic (temp file + rename)"""
        test_config = {
            'autonomous_behavior': {'max_hook_iterations': 50},
            'logging': {'log_level': 'INFO'},
            'context_management': {'max_context_tokens': 150000},
            'integration_settings': {'claude_code_timeout_seconds': 30},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True}
        }
        
        config_dir = Path(self.temp_dir) / 'config'
        main_config_file = config_dir / 'autonomous_config.json'
        temp_file = config_dir / 'autonomous_config.json.tmp'
        
        # Mock to simulate failure during temp file verification
        original_load = json.load
        
        def failing_load(f):
            if '.tmp' in f.name:
                raise json.JSONDecodeError("Simulated validation failure", "", 0)
            return original_load(f)
        
        with patch('json.load', failing_load):
            with pytest.raises(ConfigurationError, match="Failed to save configuration"):
                self.config_manager.save_configuration(test_config)
        
        # Verify main file doesn't exist (atomic operation failed)
        assert not main_config_file.exists()
        
        # Verify temp file was cleaned up
        assert not temp_file.exists()
    
    def test_save_configuration_validation_before_save(self):
        """Test configuration is validated before saving"""
        invalid_config = {
            'autonomous_behavior': {'max_hook_iterations': -1},  # Invalid: negative
            'logging': {'log_level': 'INVALID'},                # Invalid: wrong level
            'context_management': {'max_context_tokens': 500},   # Invalid: too low
            'missing_required_section': True
        }
        
        with pytest.raises(ConfigurationError):
            self.config_manager.save_configuration(invalid_config)
    
    def test_save_configuration_invalidates_cache(self):
        """Test saving configuration invalidates the cache"""
        # Load initial config (creates cache)
        config1 = self.config_manager.load_configuration()
        
        # Save new config
        new_config = {
            'autonomous_behavior': {'max_hook_iterations': 75},
            'logging': {'log_level': 'WARNING'},
            'context_management': {'max_context_tokens': 150000},
            'integration_settings': {'claude_code_timeout_seconds': 30},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True}
        }
        
        self.config_manager.save_configuration(new_config)
        
        # Load config again (should reload from file, not cache)
        config2 = self.config_manager.load_configuration()
        
        assert config1 is not config2  # Different objects, indicating cache invalidation
        assert config2['autonomous_behavior']['max_hook_iterations'] == 75


class TestConfigurationValidation:
    """Test configuration validation logic"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_configuration_missing_required_sections(self):
        """Test validation fails for missing required sections"""
        invalid_config = {
            'autonomous_behavior': {'max_hook_iterations': 50},
            # Missing other required sections
        }
        
        with pytest.raises(ConfigurationError, match="Missing required configuration section"):
            self.config_manager._validate_configuration(invalid_config)
    
    def test_validate_configuration_invalid_section_type(self):
        """Test validation fails for non-dictionary sections"""
        invalid_config = {
            'autonomous_behavior': "not_a_dict",  # Should be dict
            'context_management': {'max_context_tokens': 150000},
            'integration_settings': {'claude_code_timeout_seconds': 30},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True},
            'logging': {'log_level': 'INFO'}
        }
        
        with pytest.raises(ConfigurationError, match="must be a dictionary"):
            self.config_manager._validate_configuration(invalid_config)
    
    def test_validate_configuration_invalid_max_iterations(self):
        """Test validation fails for invalid max_hook_iterations"""
        # Test negative value
        invalid_config = self._get_base_valid_config()
        invalid_config['autonomous_behavior']['max_hook_iterations'] = -1
        
        with pytest.raises(ConfigurationError, match="max_hook_iterations must be positive integer"):
            self.config_manager._validate_configuration(invalid_config)
        
        # Test too high value
        invalid_config['autonomous_behavior']['max_hook_iterations'] = 2000
        
        with pytest.raises(ConfigurationError, match="max_hook_iterations too high"):
            self.config_manager._validate_configuration(invalid_config)
        
        # Test non-integer value
        invalid_config['autonomous_behavior']['max_hook_iterations'] = "fifty"
        
        with pytest.raises(ConfigurationError, match="max_hook_iterations must be positive integer"):
            self.config_manager._validate_configuration(invalid_config)
    
    def test_validate_configuration_invalid_strictness(self):
        """Test validation fails for invalid evidence validation strictness"""
        invalid_config = self._get_base_valid_config()
        invalid_config['autonomous_behavior']['evidence_validation_strictness'] = 'invalid'
        
        with pytest.raises(ConfigurationError, match="evidence_validation_strictness must be strict/moderate/permissive"):
            self.config_manager._validate_configuration(invalid_config)
    
    def test_validate_configuration_invalid_context_tokens(self):
        """Test validation fails for invalid max_context_tokens"""
        # Test too low value
        invalid_config = self._get_base_valid_config()
        invalid_config['context_management']['max_context_tokens'] = 500
        
        with pytest.raises(ConfigurationError, match="max_context_tokens must be integer >= 1000"):
            self.config_manager._validate_configuration(invalid_config)
        
        # Test too high value
        invalid_config['context_management']['max_context_tokens'] = 300000
        
        with pytest.raises(ConfigurationError, match="max_context_tokens too high"):
            self.config_manager._validate_configuration(invalid_config)
    
    def test_validate_configuration_invalid_log_level(self):
        """Test validation fails for invalid log level"""
        invalid_config = self._get_base_valid_config()
        invalid_config['logging']['log_level'] = 'INVALID_LEVEL'
        
        with pytest.raises(ConfigurationError, match="log_level must be DEBUG/INFO/WARNING/ERROR/CRITICAL"):
            self.config_manager._validate_configuration(invalid_config)
    
    def test_validate_configuration_valid_config_passes(self):
        """Test validation passes for valid configuration"""
        valid_config = self._get_base_valid_config()
        
        # Should not raise any exception
        self.config_manager._validate_configuration(valid_config)
    
    def _get_base_valid_config(self):
        """Helper method to get base valid configuration"""
        return {
            'autonomous_behavior': {
                'max_hook_iterations': 50,
                'evidence_validation_strictness': 'strict'
            },
            'context_management': {
                'max_context_tokens': 150000
            },
            'integration_settings': {
                'claude_code_timeout_seconds': 30
            },
            'evidence_collection': {
                'enable_anti_fabrication': True
            },
            'safety_mechanisms': {
                'enable_loop_detection': True
            },
            'logging': {
                'log_level': 'INFO'
            }
        }


class TestConfigurationUtilityMethods:
    """Test configuration utility methods"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_config_value_existing_path(self):
        """Test getting configuration value with valid dot notation path"""
        # Load default config
        config = self.config_manager.load_configuration()
        
        # Test getting nested values
        log_level = self.config_manager.get_config_value('logging.log_level')
        assert log_level == 'INFO'
        
        max_iterations = self.config_manager.get_config_value('autonomous_behavior.max_hook_iterations')
        assert max_iterations == 50
        
        timeout = self.config_manager.get_config_value('integration_settings.claude_code_timeout_seconds')
        assert timeout == 30
    
    def test_get_config_value_nonexistent_path_with_default(self):
        """Test getting nonexistent configuration value returns default"""
        default_value = "test_default"
        
        result = self.config_manager.get_config_value('nonexistent.key.path', default=default_value)
        assert result == default_value
    
    def test_get_config_value_nonexistent_path_no_default(self):
        """Test getting nonexistent configuration value returns None"""
        result = self.config_manager.get_config_value('nonexistent.key.path')
        assert result is None
    
    def test_get_config_value_partial_path_exists(self):
        """Test getting configuration value where partial path exists"""
        # 'logging' exists but 'logging.nonexistent' doesn't
        result = self.config_manager.get_config_value('logging.nonexistent', default='fallback')
        assert result == 'fallback'
    
    def test_convert_env_value_type_boolean(self):
        """Test environment variable type conversion for booleans"""
        assert self.config_manager._convert_env_value_type('true') is True
        assert self.config_manager._convert_env_value_type('True') is True
        assert self.config_manager._convert_env_value_type('TRUE') is True
        assert self.config_manager._convert_env_value_type('yes') is True
        assert self.config_manager._convert_env_value_type('1') is True
        
        assert self.config_manager._convert_env_value_type('false') is False
        assert self.config_manager._convert_env_value_type('False') is False
        assert self.config_manager._convert_env_value_type('FALSE') is False
        assert self.config_manager._convert_env_value_type('no') is False
        assert self.config_manager._convert_env_value_type('0') is False
    
    def test_convert_env_value_type_numeric(self):
        """Test environment variable type conversion for numbers"""
        assert self.config_manager._convert_env_value_type('42') == 42
        assert self.config_manager._convert_env_value_type('-17') == -17
        assert self.config_manager._convert_env_value_type('3.14') == 3.14
        assert self.config_manager._convert_env_value_type('-2.5') == -2.5
    
    def test_convert_env_value_type_string(self):
        """Test environment variable type conversion for strings"""
        assert self.config_manager._convert_env_value_type('hello') == 'hello'
        assert self.config_manager._convert_env_value_type('not_a_number') == 'not_a_number'
        assert self.config_manager._convert_env_value_type('') == ''
    
    def test_set_config_value_dot_notation(self):
        """Test setting configuration values using dot notation"""
        config = {}
        
        self.config_manager._set_config_value(config, 'level1.level2.key', 'test_value')
        
        expected = {
            'level1': {
                'level2': {
                    'key': 'test_value'
                }
            }
        }
        assert config == expected
    
    def test_set_config_value_existing_structure(self):
        """Test setting configuration values in existing structure"""
        config = {
            'existing': {
                'key1': 'value1'
            }
        }
        
        self.config_manager._set_config_value(config, 'existing.key2', 'value2')
        self.config_manager._set_config_value(config, 'existing.nested.deep', 'deep_value')
        
        expected = {
            'existing': {
                'key1': 'value1',
                'key2': 'value2',
                'nested': {
                    'deep': 'deep_value'
                }
            }
        }
        assert config == expected
    
    def test_merge_configurations_basic(self):
        """Test basic configuration merging"""
        base = {
            'section1': {'key1': 'base1', 'key2': 'base2'},
            'section2': {'key3': 'base3'}
        }
        
        override = {
            'section1': {'key2': 'override2', 'key4': 'override4'},
            'section3': {'key5': 'override5'}
        }
        
        result = self.config_manager._merge_configurations(base, override)
        
        expected = {
            'section1': {'key1': 'base1', 'key2': 'override2', 'key4': 'override4'},
            'section2': {'key3': 'base3'},
            'section3': {'key5': 'override5'}
        }
        assert result == expected
    
    def test_merge_configurations_deep_nesting(self):
        """Test configuration merging with deep nesting"""
        base = {
            'level1': {
                'level2': {
                    'level3': {
                        'key1': 'base1',
                        'key2': 'base2'
                    }
                }
            }
        }
        
        override = {
            'level1': {
                'level2': {
                    'level3': {
                        'key2': 'override2',
                        'key3': 'override3'
                    }
                }
            }
        }
        
        result = self.config_manager._merge_configurations(base, override)
        
        expected = {
            'level1': {
                'level2': {
                    'level3': {
                        'key1': 'base1',
                        'key2': 'override2',
                        'key3': 'override3'
                    }
                }
            }
        }
        assert result == expected


class TestEnvironmentVariableOverrides:
    """Test environment variable override functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_environment_variable_override_simple(self):
        """Test simple environment variable override"""
        env_vars = {
            'AUTONOMOUS_TDD_LOGGING_LOG_LEVEL': 'ERROR'
        }
        
        with patch.dict(os.environ, env_vars):
            config = self.config_manager.load_configuration()
        
        assert config['logging']['log_level'] == 'ERROR'
    
    def test_environment_variable_override_nested(self):
        """Test environment variable override for nested configuration"""
        env_vars = {
            'AUTONOMOUS_TDD_AUTONOMOUS_BEHAVIOR_MAX_HOOK_ITERATIONS': '200',
            'AUTONOMOUS_TDD_CONTEXT_MANAGEMENT_MAX_CONTEXT_TOKENS': '100000'
        }
        
        with patch.dict(os.environ, env_vars):
            config = self.config_manager.load_configuration()
        
        assert config['autonomous_behavior']['max_hook_iterations'] == 200
        assert config['context_management']['max_context_tokens'] == 100000
    
    def test_environment_variable_override_boolean(self):
        """Test environment variable override for boolean values"""
        env_vars = {
            'AUTONOMOUS_TDD_EVIDENCE_COLLECTION_ENABLE_ANTI_FABRICATION': 'false',
            'AUTONOMOUS_TDD_SAFETY_MECHANISMS_ENABLE_LOOP_DETECTION': 'true'
        }
        
        with patch.dict(os.environ, env_vars):
            config = self.config_manager.load_configuration()
        
        assert config['evidence_collection']['enable_anti_fabrication'] is False
        assert config['safety_mechanisms']['enable_loop_detection'] is True
    
    def test_environment_variable_override_creates_new_paths(self):
        """Test environment variable override creates new configuration paths"""
        env_vars = {
            'AUTONOMOUS_TDD_NEW_SECTION_NEW_KEY': 'new_value'
        }
        
        with patch.dict(os.environ, env_vars):
            config = self.config_manager.load_configuration()
        
        assert config['new_section']['new_key'] == 'new_value'
    
    def test_environment_variable_non_autonomous_ignored(self):
        """Test non-AUTONOMOUS_TDD environment variables are ignored"""
        env_vars = {
            'OTHER_CONFIG_VALUE': 'should_be_ignored',
            'AUTONOMOUS_TDD_LOGGING_LOG_LEVEL': 'DEBUG'
        }
        
        with patch.dict(os.environ, env_vars):
            config = self.config_manager.load_configuration()
        
        assert 'other_config' not in config
        assert config['logging']['log_level'] == 'DEBUG'


class TestConfigurationErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_json_file_permission_error(self):
        """Test handling of permission errors when loading JSON files"""
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        config_file = config_dir / 'autonomous_config.json'
        
        # Create file and remove read permissions
        with open(config_file, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        os.chmod(config_file, 0o000)
        
        try:
            with pytest.raises(ConfigurationError, match="Cannot read"):
                self.config_manager._load_json_file(config_file)
        finally:
            # Restore permissions for cleanup
            os.chmod(config_file, 0o644)
    
    def test_load_json_file_invalid_syntax(self):
        """Test handling of invalid JSON syntax"""
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        config_file = config_dir / 'autonomous_config.json'
        
        with open(config_file, 'w') as f:
            f.write('{ invalid json syntax')
        
        with pytest.raises(ConfigurationError, match="Invalid JSON"):
            self.config_manager._load_json_file(config_file)
    
    def test_config_cache_validation_file_deletion(self):
        """Test cache validation handles file deletion correctly"""
        # Create config file
        config_dir = Path(self.temp_dir) / 'config'
        config_dir.mkdir()
        config_file = config_dir / 'autonomous_config.json'
        
        with open(config_file, 'w') as f:
            json.dump({'logging': {'log_level': 'INFO'}}, f)
        
        # Load config (creates cache)
        config1 = self.config_manager.load_configuration()
        
        # Delete config file
        config_file.unlink()
        
        # Load config again (cache should still be valid since file doesn't exist)
        config2 = self.config_manager.load_configuration()
        
        # Should be same cached config
        assert config1 is config2