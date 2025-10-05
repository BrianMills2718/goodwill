#!/usr/bin/env python3
"""
JSON UTILITIES - Foundation Component (No Dependencies)
Safe JSON handling with validation and error recovery
"""

# RELATES_TO: ../config/config_manager.py, ../../logs/evidence/

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class JSONValidationError(Exception):
    """Raised when JSON data fails validation"""
    pass

class JSONUtilities:
    """
    Safe JSON operations with defensive programming
    
    FOUNDATION COMPONENT: No dependencies on other system components
    Provides safe JSON loading, saving, and validation for entire system
    """
    
    @staticmethod
    def safe_load_json(file_path: Union[str, Path], 
                      default: Optional[Any] = None,
                      validate_schema: Optional[Dict] = None) -> Any:
        """
        Safely load JSON file with error handling and validation
        
        PARAMETERS:
        - file_path: Path to JSON file
        - default: Default value to return if file doesn't exist or is invalid
        - validate_schema: Optional schema to validate against
        
        RETURNS: Parsed JSON data or default value
        
        DEFENSIVE PROGRAMMING:
        - Handles missing files gracefully
        - Validates JSON syntax
        - Optionally validates against schema
        - Always returns something (never None unless explicitly set)
        """
        
        file_path = Path(file_path)
        
        # Handle missing file
        if not file_path.exists():
            if default is not None:
                return default
            else:
                raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        # Handle empty file
        if file_path.stat().st_size == 0:
            if default is not None:
                return default
            else:
                raise JSONValidationError(f"JSON file is empty: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate against schema if provided
            if validate_schema is not None:
                JSONUtilities.validate_json_schema(data, validate_schema, str(file_path))
            
            return data
            
        except json.JSONDecodeError as e:
            if default is not None:
                return default
            else:
                raise JSONValidationError(f"Invalid JSON in {file_path}: {e}")
        
        except (IOError, OSError) as e:
            if default is not None:
                return default
            else:
                raise JSONValidationError(f"Cannot read {file_path}: {e}")
    
    @staticmethod
    def safe_save_json(file_path: Union[str, Path], 
                      data: Any,
                      backup: bool = True,
                      validate_schema: Optional[Dict] = None,
                      atomic: bool = True) -> bool:
        """
        Safely save JSON data with backup and validation
        
        PARAMETERS:
        - file_path: Path where to save JSON file
        - data: Data to save as JSON
        - backup: Whether to create backup of existing file
        - validate_schema: Optional schema to validate data against
        - atomic: Whether to use atomic write (temp file + rename)
        
        RETURNS: True if save successful, False otherwise
        
        SAFETY FEATURES:
        - Validates data can be serialized to JSON
        - Creates backup of existing file
        - Uses atomic write to prevent corruption
        - Validates written file can be read back
        """
        
        file_path = Path(file_path)
        
        try:
            # Validate data can be serialized
            json_str = json.dumps(data, indent=2, sort_keys=True, default=str)
            
            # Validate against schema if provided
            if validate_schema is not None:
                JSONUtilities.validate_json_schema(data, validate_schema, str(file_path))
            
            # Create parent directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup of existing file
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                backup_path.write_bytes(file_path.read_bytes())
            
            if atomic:
                # Atomic write using temporary file
                temp_path = file_path.with_suffix('.tmp')
                
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                
                # Verify written file is valid
                with open(temp_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Will raise exception if invalid
                
                # Atomic move to final location
                temp_path.replace(file_path)
            
            else:
                # Direct write
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            
            return True
            
        except Exception as e:
            # Clean up temp file if it exists
            if atomic:
                temp_path = file_path.with_suffix('.tmp')
                if temp_path.exists():
                    temp_path.unlink()
            
            raise JSONValidationError(f"Failed to save JSON to {file_path}: {e}")
    
    @staticmethod
    def validate_json_schema(data: Any, schema: Dict, context: str = "") -> None:
        """
        Validate JSON data against a simple schema
        
        PARAMETERS:
        - data: JSON data to validate
        - schema: Schema definition dictionary
        - context: Context string for error messages
        
        SCHEMA FORMAT:
        {
            "type": "object",  # object, array, string, number, boolean
            "required": ["field1", "field2"],  # required fields for objects
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "number", "minimum": 0}
            }
        }
        
        RAISES: JSONValidationError if validation fails
        """
        
        context_prefix = f"{context}: " if context else ""
        
        # Validate type
        expected_type = schema.get("type")
        if expected_type:
            if not JSONUtilities._validate_type(data, expected_type):
                raise JSONValidationError(f"{context_prefix}Expected {expected_type}, got {type(data).__name__}")
        
        # Validate object properties
        if expected_type == "object" and isinstance(data, dict):
            
            # Check required fields
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in data:
                    raise JSONValidationError(f"{context_prefix}Missing required field: {field}")
            
            # Validate properties
            properties = schema.get("properties", {})
            for field_name, field_schema in properties.items():
                if field_name in data:
                    field_context = f"{context}.{field_name}" if context else field_name
                    JSONUtilities.validate_json_schema(data[field_name], field_schema, field_context)
        
        # Validate array items
        elif expected_type == "array" and isinstance(data, list):
            
            items_schema = schema.get("items")
            if items_schema:
                for i, item in enumerate(data):
                    item_context = f"{context}[{i}]" if context else f"[{i}]"
                    JSONUtilities.validate_json_schema(item, items_schema, item_context)
        
        # Validate numeric constraints
        elif expected_type in ["number", "integer"] and isinstance(data, (int, float)):
            
            minimum = schema.get("minimum")
            if minimum is not None and data < minimum:
                raise JSONValidationError(f"{context_prefix}Value {data} below minimum {minimum}")
            
            maximum = schema.get("maximum")
            if maximum is not None and data > maximum:
                raise JSONValidationError(f"{context_prefix}Value {data} above maximum {maximum}")
        
        # Validate string constraints
        elif expected_type == "string" and isinstance(data, str):
            
            min_length = schema.get("minLength")
            if min_length is not None and len(data) < min_length:
                raise JSONValidationError(f"{context_prefix}String too short (min {min_length})")
            
            max_length = schema.get("maxLength")
            if max_length is not None and len(data) > max_length:
                raise JSONValidationError(f"{context_prefix}String too long (max {max_length})")
            
            enum_values = schema.get("enum")
            if enum_values is not None and data not in enum_values:
                raise JSONValidationError(f"{context_prefix}Value must be one of: {enum_values}")
    
    @staticmethod
    def _validate_type(data: Any, expected_type: str) -> bool:
        """
        Check if data matches expected JSON type
        
        PARAMETERS:
        - data: Data to check
        - expected_type: Expected type string
        
        RETURNS: True if type matches, False otherwise
        """
        
        type_mapping = {
            "object": dict,
            "array": list,
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None)
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, assume valid
        
        return isinstance(data, expected_python_type)
    
    @staticmethod
    def calculate_json_hash(data: Any) -> str:
        """
        Calculate SHA-256 hash of JSON data for change detection
        
        PARAMETERS:
        - data: JSON-serializable data
        
        RETURNS: SHA-256 hash string
        
        NOTE: Hash is stable across runs (deterministic JSON serialization)
        """
        
        try:
            # Serialize with consistent formatting
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
        except Exception as e:
            raise JSONValidationError(f"Cannot calculate hash for data: {e}")
    
    @staticmethod
    def merge_json_objects(base: Dict, overlay: Dict, deep: bool = True) -> Dict:
        """
        Merge two JSON objects with overlay taking precedence
        
        PARAMETERS:
        - base: Base object (lower priority)
        - overlay: Overlay object (higher priority)
        - deep: Whether to perform deep merge of nested objects
        
        RETURNS: Merged object
        
        DEFENSIVE PROGRAMMING:
        - Handles None inputs gracefully
        - Deep copies data to avoid mutation
        - Validates inputs are dictionaries
        """
        
        if base is None:
            base = {}
        if overlay is None:
            overlay = {}
        
        if not isinstance(base, dict):
            raise JSONValidationError("Base object must be a dictionary")
        if not isinstance(overlay, dict):
            raise JSONValidationError("Overlay object must be a dictionary")
        
        # Deep copy to avoid modifying originals
        import copy
        result = copy.deepcopy(base)
        
        for key, value in overlay.items():
            if (deep and 
                key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                # Recursively merge nested dictionaries
                result[key] = JSONUtilities.merge_json_objects(result[key], value, deep=True)
            else:
                # Direct override
                result[key] = copy.deepcopy(value)
        
        return result
    
    @staticmethod
    def flatten_json_object(obj: Dict, separator: str = '.', prefix: str = '') -> Dict[str, Any]:
        """
        Flatten nested JSON object into dot-notation dictionary
        
        PARAMETERS:
        - obj: Object to flatten
        - separator: Separator for nested keys (default '.')
        - prefix: Prefix for all keys
        
        RETURNS: Flattened dictionary
        
        EXAMPLE:
        {"a": {"b": {"c": 1}}} → {"a.b.c": 1}
        """
        
        result = {}
        
        for key, value in obj.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                nested = JSONUtilities.flatten_json_object(value, separator, new_key)
                result.update(nested)
            else:
                result[new_key] = value
        
        return result
    
    @staticmethod
    def unflatten_json_object(flat_obj: Dict[str, Any], separator: str = '.') -> Dict:
        """
        Unflatten dot-notation dictionary into nested JSON object
        
        PARAMETERS:
        - flat_obj: Flattened dictionary
        - separator: Separator used in keys
        
        RETURNS: Nested dictionary
        
        EXAMPLE:
        {"a.b.c": 1} → {"a": {"b": {"c": 1}}}
        """
        
        result = {}
        
        for flat_key, value in flat_obj.items():
            keys = flat_key.split(separator)
            current = result
            
            # Navigate to parent of target key
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set final value
            current[keys[-1]] = value
        
        return result
    
    @staticmethod
    def sanitize_for_json(data: Any) -> Any:
        """
        Sanitize data to be JSON-serializable
        
        PARAMETERS:
        - data: Data to sanitize
        
        RETURNS: JSON-serializable version of data
        
        CONVERSIONS:
        - datetime objects → ISO format strings
        - Path objects → string paths
        - Sets → lists
        - Non-serializable objects → string representation
        """
        
        if isinstance(data, dict):
            return {key: JSONUtilities.sanitize_for_json(value) for key, value in data.items()}
        
        elif isinstance(data, (list, tuple)):
            return [JSONUtilities.sanitize_for_json(item) for item in data]
        
        elif isinstance(data, set):
            return list(data)
        
        elif isinstance(data, datetime):
            return data.isoformat()
        
        elif isinstance(data, Path):
            return str(data)
        
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        
        else:
            # Convert unknown types to string
            return str(data)