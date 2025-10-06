#!/usr/bin/env python3
"""
Unit tests for JSON utilities foundation component

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

from src.utils.json_utilities import JSONUtilities, JSONValidationError

class TestJSONUtilitiesBasicOperations:
    """Test basic JSON loading and saving operations"""
    
    def test_safe_load_json_valid_file(self):
        """Test loading valid JSON file returns correct data"""
        test_data = {"key": "value", "number": 42, "array": [1, 2, 3]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            # JSONUtilities().safe_load_json(temp_path) should return test_data
            json_utils = JSONUtilities()
            result = json_utils.safe_load_json(Path(temp_path))
            assert result.success == True
            assert result.data == test_data
        finally:
            os.unlink(temp_path)
    
    def test_safe_load_json_missing_file_with_default(self):
        """Test loading missing file with default returns default value"""
        non_existent_path = "/tmp/does_not_exist_12345.json"
        default_value = {"default": True}
        
        result = JSONUtilities.safe_load_json(non_existent_path, default=default_value)
        assert result == default_value
    
    def test_safe_load_json_missing_file_no_default_raises_error(self):
        """Test loading missing file without default raises FileNotFoundError"""
        non_existent_path = "/tmp/does_not_exist_12345.json"
        
        with pytest.raises(FileNotFoundError):
            JSONUtilities.safe_load_json(non_existent_path)
    
    def test_safe_load_json_empty_file_with_default(self):
        """Test loading empty file with default returns default value"""
        default_value = {"empty_default": True}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write nothing to create empty file
            temp_path = f.name
        
        try:
            result = JSONUtilities.safe_load_json(temp_path, default=default_value)
            assert result == default_value
        finally:
            os.unlink(temp_path)
    
    def test_safe_load_json_invalid_json_with_default(self):
        """Test loading invalid JSON with default returns default value"""
        default_value = {"invalid_default": True}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_path = f.name
        
        try:
            result = JSONUtilities.safe_load_json(temp_path, default=default_value)
            assert result == default_value
        finally:
            os.unlink(temp_path)
    
    def test_safe_load_json_invalid_json_no_default_raises_error(self):
        """Test loading invalid JSON without default raises JSONValidationError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(JSONValidationError):
                JSONUtilities.safe_load_json(temp_path)
        finally:
            os.unlink(temp_path)


class TestJSONUtilitiesSaveOperations:
    """Test JSON saving operations with safety features"""
    
    def test_safe_save_json_basic_save(self):
        """Test basic JSON save operation creates valid file"""
        test_data = {"save_test": True, "value": 123}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Remove the file so we can test creation
            os.unlink(temp_path)
            
            result = JSONUtilities.safe_save_json(temp_path, test_data)
            assert result is True
            
            # Verify file was created and contains correct data
            assert Path(temp_path).exists()
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)
    
    def test_safe_save_json_creates_parent_directories(self):
        """Test save operation creates parent directories if they don't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "deep" / "test.json"
            test_data = {"nested_save": True}
            
            result = JSONUtilities.safe_save_json(str(nested_path), test_data)
            assert result is True
            
            # Verify directory was created and file saved
            assert nested_path.exists()
            with open(nested_path, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
    
    def test_safe_save_json_with_backup(self):
        """Test save operation creates backup of existing file"""
        test_data_original = {"original": True}
        test_data_new = {"updated": True}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data_original, f)
            temp_path = f.name
        
        try:
            # Save new data with backup enabled
            result = JSONUtilities.safe_save_json(temp_path, test_data_new, backup=True)
            assert result is True
            
            # Verify new data was saved
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data_new
            
            # Verify backup was created (should have timestamp suffix)
            backup_files = list(Path(temp_path).parent.glob(f"{Path(temp_path).stem}.backup_*"))
            assert len(backup_files) >= 1
            
            # Verify backup contains original data
            with open(backup_files[0], 'r') as f:
                backup_data = json.load(f)
            assert backup_data == test_data_original
        finally:
            # Clean up all created files
            if Path(temp_path).exists():
                os.unlink(temp_path)
            for backup_file in Path(temp_path).parent.glob(f"{Path(temp_path).stem}.backup_*"):
                backup_file.unlink()
    
    def test_safe_save_json_atomic_write(self):
        """Test atomic write operation prevents corruption"""
        test_data = {"atomic_test": True, "large_value": "x" * 1000}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            os.unlink(temp_path)  # Remove file for fresh test
            
            # Mock to simulate failure during temp file write
            original_write = Path.write_text
            
            def failing_write(self, *args, **kwargs):
                if '.tmp' in str(self):
                    raise IOError("Simulated write failure")
                return original_write(self, *args, **kwargs)
            
            with patch.object(Path, 'write_text', failing_write):
                with pytest.raises(JSONValidationError):
                    JSONUtilities.safe_save_json(temp_path, test_data, atomic=True)
            
            # Verify original file doesn't exist (atomic operation failed)
            assert not Path(temp_path).exists()
            
            # Verify temp file was cleaned up
            temp_files = list(Path(temp_path).parent.glob(f"{Path(temp_path).stem}.tmp"))
            assert len(temp_files) == 0
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)
    
    def test_safe_save_json_invalid_data_raises_error(self):
        """Test saving non-serializable data raises JSONValidationError"""
        # Use object that can't be JSON serialized
        invalid_data = {"function": lambda x: x}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            os.unlink(temp_path)
            
            with pytest.raises(JSONValidationError):
                JSONUtilities.safe_save_json(temp_path, invalid_data)
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)


class TestJSONSchemaValidation:
    """Test JSON schema validation functionality"""
    
    def test_validate_json_schema_valid_object(self):
        """Test schema validation passes for valid object"""
        data = {
            "name": "test",
            "age": 25,
            "active": True
        }
        
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0},
                "active": {"type": "boolean"}
            }
        }
        
        # Should not raise any exception
        JSONUtilities.validate_json_schema(data, schema)
    
    def test_validate_json_schema_missing_required_field(self):
        """Test schema validation fails for missing required field"""
        data = {
            "name": "test"
            # Missing required "age" field
        }
        
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        with pytest.raises(JSONValidationError, match="Missing required field: age"):
            JSONUtilities.validate_json_schema(data, schema)
    
    def test_validate_json_schema_wrong_type(self):
        """Test schema validation fails for wrong data type"""
        data = {
            "name": "test",
            "age": "twenty-five"  # String instead of number
        }
        
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        with pytest.raises(JSONValidationError, match="Expected number, got str"):
            JSONUtilities.validate_json_schema(data, schema)
    
    def test_validate_json_schema_numeric_constraints(self):
        """Test schema validation for numeric constraints"""
        data = {"value": -5}
        
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": "number", "minimum": 0, "maximum": 100}
            }
        }
        
        with pytest.raises(JSONValidationError, match="Value -5 below minimum 0"):
            JSONUtilities.validate_json_schema(data, schema)
    
    def test_validate_json_schema_string_constraints(self):
        """Test schema validation for string constraints"""
        data = {"name": "hi"}  # Too short
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 3, "maxLength": 50}
            }
        }
        
        with pytest.raises(JSONValidationError, match="String too short"):
            JSONUtilities.validate_json_schema(data, schema)
    
    def test_validate_json_schema_enum_constraint(self):
        """Test schema validation for enum constraint"""
        data = {"status": "invalid"}
        
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "inactive", "pending"]}
            }
        }
        
        with pytest.raises(JSONValidationError, match="Value must be one of"):
            JSONUtilities.validate_json_schema(data, schema)
    
    def test_validate_json_schema_array_validation(self):
        """Test schema validation for array types"""
        data = {"items": [1, 2, "three"]}  # Mixed types
        
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "number"}
                }
            }
        }
        
        with pytest.raises(JSONValidationError, match="Expected number, got str"):
            JSONUtilities.validate_json_schema(data, schema)


class TestJSONUtilityFunctions:
    """Test utility functions for JSON manipulation"""
    
    def test_calculate_json_hash_consistent(self):
        """Test JSON hash calculation is consistent across calls"""
        data = {"test": "data", "number": 42, "array": [1, 2, 3]}
        
        hash1 = JSONUtilities.calculate_json_hash(data)
        hash2 = JSONUtilities.calculate_json_hash(data)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex string length
    
    def test_calculate_json_hash_different_for_different_data(self):
        """Test JSON hash calculation produces different hashes for different data"""
        data1 = {"test": "data1"}
        data2 = {"test": "data2"}
        
        hash1 = JSONUtilities.calculate_json_hash(data1)
        hash2 = JSONUtilities.calculate_json_hash(data2)
        
        assert hash1 != hash2
    
    def test_calculate_json_hash_order_independent(self):
        """Test JSON hash is independent of key order"""
        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"c": 3, "a": 1, "b": 2}
        
        hash1 = JSONUtilities.calculate_json_hash(data1)
        hash2 = JSONUtilities.calculate_json_hash(data2)
        
        assert hash1 == hash2
    
    def test_merge_json_objects_basic(self):
        """Test basic JSON object merging"""
        base = {"a": 1, "b": 2}
        overlay = {"b": 3, "c": 4}
        
        result = JSONUtilities.merge_json_objects(base, overlay)
        
        expected = {"a": 1, "b": 3, "c": 4}
        assert result == expected
    
    def test_merge_json_objects_deep_merge(self):
        """Test deep merging of nested objects"""
        base = {
            "config": {"debug": False, "port": 8080},
            "features": {"auth": True}
        }
        overlay = {
            "config": {"debug": True, "ssl": True},
            "features": {"logging": True}
        }
        
        result = JSONUtilities.merge_json_objects(base, overlay, deep=True)
        
        expected = {
            "config": {"debug": True, "port": 8080, "ssl": True},
            "features": {"auth": True, "logging": True}
        }
        assert result == expected
    
    def test_merge_json_objects_handles_none_inputs(self):
        """Test merging handles None inputs gracefully"""
        base = {"a": 1}
        
        result1 = JSONUtilities.merge_json_objects(None, base)
        result2 = JSONUtilities.merge_json_objects(base, None)
        result3 = JSONUtilities.merge_json_objects(None, None)
        
        assert result1 == base
        assert result2 == base
        assert result3 == {}
    
    def test_flatten_json_object(self):
        """Test flattening nested JSON objects"""
        data = {
            "a": {
                "b": {
                    "c": 1
                },
                "d": 2
            },
            "e": 3
        }
        
        result = JSONUtilities.flatten_json_object(data)
        
        expected = {
            "a.b.c": 1,
            "a.d": 2,
            "e": 3
        }
        assert result == expected
    
    def test_unflatten_json_object(self):
        """Test unflattening dot-notation JSON objects"""
        data = {
            "a.b.c": 1,
            "a.d": 2,
            "e": 3
        }
        
        result = JSONUtilities.unflatten_json_object(data)
        
        expected = {
            "a": {
                "b": {
                    "c": 1
                },
                "d": 2
            },
            "e": 3
        }
        assert result == expected
    
    def test_sanitize_for_json_datetime(self):
        """Test sanitizing datetime objects for JSON"""
        from datetime import datetime
        
        data = {
            "timestamp": datetime(2023, 1, 1, 12, 0, 0),
            "value": 42
        }
        
        result = JSONUtilities.sanitize_for_json(data)
        
        assert isinstance(result["timestamp"], str)
        assert "2023-01-01T12:00:00" in result["timestamp"]
        assert result["value"] == 42
    
    def test_sanitize_for_json_path_objects(self):
        """Test sanitizing Path objects for JSON"""
        from pathlib import Path
        
        data = {
            "file_path": Path("/tmp/test.txt"),
            "name": "test"
        }
        
        result = JSONUtilities.sanitize_for_json(data)
        
        assert result["file_path"] == "/tmp/test.txt"
        assert result["name"] == "test"
    
    def test_sanitize_for_json_sets(self):
        """Test sanitizing sets for JSON"""
        data = {
            "tags": {"python", "json", "test"},
            "count": 3
        }
        
        result = JSONUtilities.sanitize_for_json(data)
        
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) == 3
        assert set(result["tags"]) == {"python", "json", "test"}
        assert result["count"] == 3


class TestJSONUtilitiesErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def test_load_json_permission_denied(self):
        """Test handling of permission denied errors"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
        
        try:
            # Remove read permissions
            os.chmod(temp_path, 0o000)
            
            with pytest.raises(JSONValidationError, match="Cannot read"):
                JSONUtilities.safe_load_json(temp_path)
        finally:
            # Restore permissions and clean up
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)
    
    def test_save_json_permission_denied(self):
        """Test handling of permission denied errors during save"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create read-only directory
            read_only_dir = Path(temp_dir) / "readonly"
            read_only_dir.mkdir()
            os.chmod(read_only_dir, 0o444)
            
            test_file = read_only_dir / "test.json"
            test_data = {"test": "data"}
            
            try:
                with pytest.raises(JSONValidationError, match="Failed to save JSON"):
                    JSONUtilities.safe_save_json(str(test_file), test_data)
            finally:
                # Restore permissions for cleanup
                os.chmod(read_only_dir, 0o755)
    
    def test_schema_validation_with_context(self):
        """Test schema validation includes context in error messages"""
        data = {"user": {"name": "test", "age": "invalid"}}
        
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"}
                    }
                }
            }
        }
        
        with pytest.raises(JSONValidationError, match="user.age"):
            JSONUtilities.validate_json_schema(data, schema, "test_context")


# Additional edge case tests
class TestJSONUtilitiesEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_large_json_file(self):
        """Test handling of very large JSON files"""
        # Create large data structure
        large_data = {"data": ["item"] * 10000}  # Large but manageable for testing
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_data, f)
            temp_path = f.name
        
        try:
            result = JSONUtilities.safe_load_json(temp_path)
            assert len(result["data"]) == 10000
        finally:
            os.unlink(temp_path)
    
    def test_unicode_content(self):
        """Test handling of Unicode content in JSON"""
        unicode_data = {
            "english": "Hello",
            "chinese": "你好",
            "emoji": "🤖",
            "special": "café"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(unicode_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            result = JSONUtilities.safe_load_json(temp_path)
            assert result == unicode_data
        finally:
            os.unlink(temp_path)
    
    def test_concurrent_access_simulation(self):
        """Test behavior under simulated concurrent access"""
        test_data = {"concurrent_test": True, "value": 123}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            os.unlink(temp_path)
            
            # Simulate concurrent save operations
            result1 = JSONUtilities.safe_save_json(temp_path, test_data, atomic=True)
            result2 = JSONUtilities.safe_save_json(temp_path, test_data, atomic=True)
            
            assert result1 is True
            assert result2 is True
            
            # Verify final state is consistent
            final_data = JSONUtilities.safe_load_json(temp_path)
            assert final_data == test_data
        finally:
            if Path(temp_path).exists():
                os.unlink(temp_path)