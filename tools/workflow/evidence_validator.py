#!/usr/bin/env python3
"""
Validate evidence for phase transitions.
Usage: python3 tools/workflow/evidence_validator.py [phase]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class EvidenceValidator:
    def __init__(self):
        self.evidence_paths = [
            Path("investigations/current_work/evidence.json"),
            Path("investigations/evidence.json"),
            Path(".claude/evidence.json")
        ]
        
        self.evidence_schema = {
            "explore": {
                "required": ["areas_investigated", "key_findings"],
                "optional": ["discovery_count", "uncertainties_identified"]
            },
            "write_tests": {
                "required": ["test_files_created", "test_count"],
                "optional": ["coverage_target", "test_framework"]
            },
            "implement": {
                "required": ["files_modified", "implementation_complete"],
                "optional": ["lines_added", "dependencies_added"]
            },
            "run_tests": {
                "required": ["test_results", "tests_passed"],
                "optional": ["coverage_percentage", "failure_analysis"]
            },
            "doublecheck": {
                "required": ["validation_complete", "edge_cases_tested"],
                "optional": ["performance_checked", "security_reviewed"]
            },
            "commit": {
                "required": ["commit_message", "files_committed"],
                "optional": ["commit_hash", "branch_name"]
            }
        }
    
    def find_evidence_file(self):
        """Find the evidence file"""
        for path in self.evidence_paths:
            if path.exists():
                return path
        return None
    
    def validate(self, phase=None):
        """Validate evidence for given phase"""
        # Find evidence file
        evidence_file = self.find_evidence_file()
        
        if not evidence_file:
            print("❌ No evidence file found")
            print("   Searched locations:")
            for path in self.evidence_paths:
                print(f"   - {path}")
            return False
        
        print(f"📄 Found evidence file: {evidence_file}")
        
        # Load evidence
        try:
            with open(evidence_file) as f:
                evidence = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in evidence file: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to read evidence file: {e}")
            return False
        
        # Determine phase if not provided
        if not phase:
            # Try to get from evidence file
            phase = evidence.get("phase")
            
            # Or from workflow state
            if not phase:
                state_file = Path(".claude/workflow_state.json")
                if state_file.exists():
                    try:
                        state = json.loads(state_file.read_text())
                        command = state.get("current_command", "")
                        phase = command.replace("/", "") if command else None
                    except:
                        pass
        
        if not phase:
            print("⚠️  No phase specified and couldn't determine from context")
            print("   Usage: python3 evidence_validator.py [phase]")
            return True  # Don't block if we can't determine phase
        
        print(f"🎯 Validating evidence for phase: {phase}")
        
        # Check if phase has requirements
        if phase not in self.evidence_schema:
            print(f"✅ No evidence requirements for phase: {phase}")
            return True
        
        # Check required fields
        schema = self.evidence_schema[phase]
        required_fields = schema["required"]
        optional_fields = schema.get("optional", [])
        
        missing_required = []
        missing_optional = []
        present_fields = []
        
        for field in required_fields:
            if field in evidence and evidence[field] is not None:
                present_fields.append(field)
            else:
                missing_required.append(field)
        
        for field in optional_fields:
            if field not in evidence or evidence[field] is None:
                missing_optional.append(field)
            else:
                present_fields.append(field)
        
        # Report results
        print(f"\n📊 Evidence Analysis:")
        print(f"   Required Fields: {len(required_fields)}")
        print(f"   Optional Fields: {len(optional_fields)}")
        print(f"   Present Fields: {len(present_fields)}")
        
        if present_fields:
            print(f"\n✅ Present fields:")
            for field in present_fields:
                value = evidence.get(field)
                if isinstance(value, (list, dict)):
                    print(f"   - {field}: {type(value).__name__} with {len(value)} items")
                else:
                    print(f"   - {field}: {value}")
        
        if missing_required:
            print(f"\n❌ Missing REQUIRED fields:")
            for field in missing_required:
                print(f"   - {field}")
            
        if missing_optional:
            print(f"\n⚠️  Missing optional fields:")
            for field in missing_optional:
                print(f"   - {field}")
        
        # Final validation
        is_valid = len(missing_required) == 0
        
        print(f"\n{'✅ EVIDENCE VALID' if is_valid else '❌ EVIDENCE INVALID'}")
        
        if not is_valid:
            print(f"\nTo fix: Add the missing required fields to {evidence_file}")
        
        return is_valid
    
    def generate_template(self, phase):
        """Generate evidence template for phase"""
        if phase not in self.evidence_schema:
            return {
                "phase": phase,
                "timestamp": datetime.now().isoformat(),
                "status": "in_progress",
                "note": f"No schema defined for phase: {phase}"
            }
        
        schema = self.evidence_schema[phase]
        template = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        # Add required fields
        for field in schema["required"]:
            template[field] = None  # User must fill these
            
        # Add optional fields as comments
        template["_optional_fields"] = schema.get("optional", [])
        
        return template
    
    def create_evidence_file(self, phase):
        """Create a new evidence file with template"""
        template = self.generate_template(phase)
        
        # Use first evidence path
        evidence_file = self.evidence_paths[0]
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(evidence_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"✅ Created evidence template at: {evidence_file}")
        print(f"   Please fill in the required fields")
        
        return evidence_file

def main():
    """Main entry point"""
    validator = EvidenceValidator()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--create" or command == "-c":
            # Create template
            phase = sys.argv[2] if len(sys.argv) > 2 else None
            if not phase:
                print("Usage: evidence_validator.py --create [phase]")
                sys.exit(1)
            validator.create_evidence_file(phase)
        elif command == "--help" or command == "-h":
            print("Evidence Validator - Validate phase transition evidence")
            print("\nUsage:")
            print("  python3 evidence_validator.py          # Validate current evidence")
            print("  python3 evidence_validator.py [phase]  # Validate for specific phase")
            print("  python3 evidence_validator.py --create [phase]  # Create template")
            print("\nPhases: explore, write_tests, implement, run_tests, doublecheck, commit")
        else:
            # Treat as phase name
            is_valid = validator.validate(command)
            sys.exit(0 if is_valid else 1)
    else:
        # No arguments - validate current
        is_valid = validator.validate()
        sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()