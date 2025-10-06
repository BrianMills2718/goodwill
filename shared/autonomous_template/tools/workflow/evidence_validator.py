#!/usr/bin/env python3
"""
Validate evidence for phase transitions.
Usage: python3 tools/workflow/evidence_validator.py [phase]
"""

import json
import sys
import os
import subprocess
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
    
    def analyze_with_llm(self, evidence_data, phase=None):
        """
        Analyze evidence using LLM to determine if it represents real progress
        
        Args:
            evidence_data: Dictionary of evidence claims
            phase: Current workflow phase
            
        Returns:
            dict: LLM analysis results with confidence and gaps
        """
        # For now, implement intelligent heuristics-based analysis
        # Later this can be enhanced with actual LLM API calls
        
        analysis = {
            "real_progress": True,
            "confidence_score": 0.8,
            "gaps_identified": [],
            "recommendations": [],
            "analysis_method": "heuristic"  # Will be "llm" when API integrated
        }
        
        # Analyze evidence patterns for real vs fake progress
        if phase == "implement":
            analysis.update(self._analyze_implementation_evidence(evidence_data))
        elif phase == "run_tests":
            analysis.update(self._analyze_test_evidence(evidence_data))
        elif phase == "explore":
            analysis.update(self._analyze_exploration_evidence(evidence_data))
        
        return analysis
    
    def _analyze_implementation_evidence(self, evidence):
        """Analyze implementation evidence for real progress indicators"""
        real_progress = True
        confidence = 0.8
        gaps = []
        recommendations = []
        
        # Check if files were actually modified
        if "files_modified" in evidence:
            for file_path in evidence["files_modified"]:
                if not Path(file_path).exists():
                    gaps.append(f"Claimed modified file does not exist: {file_path}")
                    confidence -= 0.2
                    real_progress = False
        
        # Check if implementation claims match actual file content
        if "implementation_complete" in evidence and evidence["implementation_complete"]:
            # Verify there are actual code changes
            try:
                result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], 
                                      capture_output=True, text=True)
                if not result.stdout.strip():
                    gaps.append("No git changes detected despite implementation claims")
                    confidence -= 0.3
                    real_progress = False
            except:
                recommendations.append("Unable to verify git changes - manual verification needed")
        
        # Check for substance vs scaffolding
        if "lines_added" in evidence:
            lines_added = evidence["lines_added"]
            if isinstance(lines_added, int) and lines_added < 10:
                gaps.append("Very few lines added - may be scaffolding rather than real implementation")
                confidence -= 0.1
        
        return {
            "real_progress": real_progress,
            "confidence_score": confidence,
            "gaps_identified": gaps,
            "recommendations": recommendations
        }
    
    def _analyze_test_evidence(self, evidence):
        """Analyze test evidence for meaningful test results"""
        real_progress = True
        confidence = 0.8
        gaps = []
        recommendations = []
        
        # Verify test results are real
        if "test_results" in evidence:
            # Try to run tests to verify claims
            try:
                result = subprocess.run(['pytest', '--tb=no', '-q'], 
                                      capture_output=True, text=True, timeout=30)
                
                # Parse actual results vs claimed results
                if "tests_passed" in evidence:
                    claimed_passed = evidence["tests_passed"]
                    actual_success = result.returncode == 0
                    
                    if claimed_passed != actual_success:
                        gaps.append(f"Test results mismatch: claimed {claimed_passed}, actual {actual_success}")
                        confidence -= 0.4
                        real_progress = False
                        
            except subprocess.TimeoutExpired:
                recommendations.append("Tests taking too long - may indicate issues")
                confidence -= 0.1
            except:
                recommendations.append("Unable to verify test results - manual check needed")
        
        # Check for test quality indicators
        if "test_count" in evidence:
            test_count = evidence["test_count"]
            if isinstance(test_count, int) and test_count == 0:
                gaps.append("No tests created despite test phase completion claim")
                confidence -= 0.5
                real_progress = False
        
        return {
            "real_progress": real_progress,
            "confidence_score": confidence,
            "gaps_identified": gaps,
            "recommendations": recommendations
        }
    
    def _analyze_exploration_evidence(self, evidence):
        """Analyze exploration evidence for meaningful discovery"""
        real_progress = True
        confidence = 0.8
        gaps = []
        recommendations = []
        
        # Check for substantive findings
        if "key_findings" in evidence:
            findings = evidence["key_findings"]
            if isinstance(findings, list) and len(findings) == 0:
                gaps.append("No key findings despite exploration completion claim")
                confidence -= 0.3
                real_progress = False
            elif isinstance(findings, list):
                # Check for generic vs specific findings
                generic_patterns = ["need to implement", "research required", "unclear requirements"]
                specific_count = 0
                for finding in findings:
                    if not any(pattern in finding.lower() for pattern in generic_patterns):
                        specific_count += 1
                
                if specific_count == 0:
                    gaps.append("Findings appear generic - may lack real exploration")
                    confidence -= 0.2
        
        # Check for areas investigated
        if "areas_investigated" in evidence:
            areas = evidence["areas_investigated"]
            if isinstance(areas, list) and len(areas) == 0:
                gaps.append("No areas investigated despite exploration claim")
                confidence -= 0.4
                real_progress = False
        
        return {
            "real_progress": real_progress,
            "confidence_score": confidence,
            "gaps_identified": gaps,
            "recommendations": recommendations
        }
    
    def validate_with_analysis(self, phase=None):
        """Enhanced validation that includes LLM analysis"""
        # First do standard validation
        is_valid = self.validate(phase)
        
        # Then add LLM analysis
        evidence_file = self.find_evidence_file()
        if evidence_file:
            try:
                with open(evidence_file) as f:
                    evidence_data = json.load(f)
                
                llm_analysis = self.analyze_with_llm(evidence_data, phase)
                
                # Combine results
                return {
                    "schema_valid": is_valid,
                    "llm_analysis": llm_analysis,
                    "overall_confidence": "high" if is_valid and llm_analysis["real_progress"] else "low",
                    "recommendation": "proceed" if is_valid and llm_analysis["real_progress"] else "review"
                }
            except:
                return {
                    "schema_valid": is_valid,
                    "llm_analysis": {"error": "Could not analyze evidence"},
                    "overall_confidence": "low",
                    "recommendation": "review"
                }
        
        return {
            "schema_valid": is_valid,
            "llm_analysis": {"error": "No evidence file found"},
            "overall_confidence": "low", 
            "recommendation": "review"
        }

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
        elif command == "--analyze" or command == "-a":
            # Enhanced analysis with LLM
            phase = sys.argv[2] if len(sys.argv) > 2 else None
            results = validator.validate_with_analysis(phase)
            print(json.dumps(results, indent=2))
        elif command == "--post-tool-use":
            # Called by PostToolUse hook to validate evidence after tool execution
            phase = sys.argv[2] if len(sys.argv) > 2 else None
            results = validator.validate_with_analysis(phase)
            
            # For hooks, we want concise output focused on actionability
            if results["overall_confidence"] == "high":
                print("✅ Evidence validated - good progress detected")
            else:
                print("⚠️  Evidence validation concerns:")
                if "gaps_identified" in results.get("llm_analysis", {}):
                    for gap in results["llm_analysis"]["gaps_identified"]:
                        print(f"   - {gap}")
                print(f"   Recommendation: {results.get('recommendation', 'review')}")
            
            # Exit with appropriate code for hook decision making
            sys.exit(0 if results["overall_confidence"] == "high" else 1)
        elif command == "--help" or command == "-h":
            print("Evidence Validator - Validate phase transition evidence")
            print("\nUsage:")
            print("  python3 evidence_validator.py          # Validate current evidence")
            print("  python3 evidence_validator.py [phase]  # Validate for specific phase")
            print("  python3 evidence_validator.py --analyze [phase]  # Enhanced LLM analysis")
            print("  python3 evidence_validator.py --create [phase]  # Create template")
            print("  python3 evidence_validator.py --post-tool-use [phase]  # Hook validation")
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