#!/usr/bin/env python3
"""
State Reconciliation - Compare claimed vs actual project state
Detects automation health issues by validating evidence against reality

Usage: python3 tools/workflow/state_reconciliation.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import re

class StateReconciler:
    def __init__(self):
        self.project_root = Path.cwd()
        self.evidence_paths = [
            Path("investigations/current_work/evidence.json"),
            Path("investigations/evidence.json"),
            Path(".claude/evidence.json")
        ]
        
    def check_automation_health(self):
        """
        Detects automation health issues
        
        Returns:
            "good" - Automation is working effectively
            "warning" - Some issues detected but not critical  
            "failing" - Automation is not making meaningful progress
        """
        issues = []
        
        # Check 1: Git activity - are files actually changing?
        git_activity = self._check_git_activity()
        if not git_activity["has_changes"]:
            issues.append("no_git_changes")
            
        # Check 2: Evidence repetition - same claims multiple times?
        evidence_repetition = self._check_evidence_repetition()
        if evidence_repetition["repeated_count"] >= 3:
            issues.append("evidence_repetition")
            
        # Check 3: Test progression - are tests improving?
        test_progression = self._check_test_progression()
        if test_progression["regression_detected"]:
            issues.append("test_regression")
            
        # Check 4: File existence vs claims
        file_validation = self._validate_claimed_files()
        if file_validation["missing_files_count"] > 0:
            issues.append("file_claims_invalid")
        
        # Determine health status
        critical_issues = ["evidence_repetition", "test_regression", "file_claims_invalid"]
        warning_issues = ["no_git_changes"]
        
        if any(issue in critical_issues for issue in issues):
            return "failing"
        elif any(issue in warning_issues for issue in issues):
            return "warning"
        else:
            return "good"
    
    def compare_claimed_vs_actual(self, evidence_file=None):
        """
        Compare claimed evidence against actual project state
        
        Args:
            evidence_file: Path to evidence file (optional)
            
        Returns:
            dict: Validation results with gaps and inconsistencies
        """
        if not evidence_file:
            evidence_file = self._find_evidence_file()
            
        if not evidence_file or not evidence_file.exists():
            return {
                "validation_status": "no_evidence",
                "gaps": ["No evidence file found"],
                "inconsistencies": [],
                "confidence": "low"
            }
        
        # Load evidence
        try:
            with open(evidence_file) as f:
                evidence = json.load(f)
        except Exception as e:
            return {
                "validation_status": "invalid_evidence",
                "gaps": [f"Could not read evidence file: {e}"],
                "inconsistencies": [],
                "confidence": "low"
            }
        
        gaps = []
        inconsistencies = []
        
        # Validate file existence claims
        if "files_created" in evidence:
            for claimed_file in evidence["files_created"]:
                if not Path(claimed_file).exists():
                    gaps.append(f"Claimed file does not exist: {claimed_file}")
        
        # Validate test count claims  
        if "test_count" in evidence:
            actual_tests = self._count_actual_tests()
            claimed_tests = evidence["test_count"]
            if actual_tests != claimed_tests:
                inconsistencies.append(f"Test count mismatch: claimed {claimed_tests}, actual {actual_tests}")
        
        # Validate test results claims
        if "tests_passed" in evidence:
            actual_test_status = self._get_actual_test_status()
            if actual_test_status["status"] != evidence["tests_passed"]:
                inconsistencies.append(f"Test status mismatch: claimed {evidence['tests_passed']}, actual {actual_test_status['status']}")
        
        # Validate commit claims
        if "commit_hash" in evidence:
            if not self._validate_commit_hash(evidence["commit_hash"]):
                gaps.append(f"Claimed commit hash does not exist: {evidence['commit_hash']}")
        
        # Determine validation status
        if len(gaps) == 0 and len(inconsistencies) == 0:
            validation_status = "valid"
            confidence = "high"
        elif len(gaps) > 0:
            validation_status = "incomplete"
            confidence = "low"
        else:
            validation_status = "inconsistent"
            confidence = "medium"
        
        return {
            "validation_status": validation_status,
            "gaps": gaps,
            "inconsistencies": inconsistencies,
            "confidence": confidence,
            "evidence_file": str(evidence_file)
        }
    
    def _check_git_activity(self):
        """Check if git shows meaningful activity"""
        try:
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            has_uncommitted = len(result.stdout.strip()) > 0
            
            # Check for recent commits (last hour)
            result = subprocess.run(['git', 'log', '--since="1 hour ago"', '--oneline'], 
                                  capture_output=True, text=True)
            has_recent_commits = len(result.stdout.strip()) > 0
            
            return {
                "has_changes": has_uncommitted or has_recent_commits,
                "uncommitted_changes": has_uncommitted,
                "recent_commits": has_recent_commits
            }
        except:
            return {"has_changes": False, "error": "git_unavailable"}
    
    def _check_evidence_repetition(self):
        """Check for repeated evidence patterns"""
        # Simple implementation - check if same phase appears multiple times recently
        evidence_files = list(Path("investigations").glob("**/evidence.json"))
        recent_evidence = []
        
        for evidence_file in evidence_files[-5:]:  # Last 5 evidence files
            try:
                with open(evidence_file) as f:
                    data = json.load(f)
                    if "phase" in data:
                        recent_evidence.append(data["phase"])
            except:
                continue
        
        # Count repetitions
        if len(recent_evidence) >= 3:
            most_common = max(set(recent_evidence), key=recent_evidence.count)
            repeated_count = recent_evidence.count(most_common)
            return {
                "repeated_count": repeated_count,
                "repeated_phase": most_common
            }
        
        return {"repeated_count": 0}
    
    def _check_test_progression(self):
        """Check if tests are getting better or worse"""
        try:
            # Run pytest to get current test status
            result = subprocess.run(['pytest', '--tb=no', '-q'], 
                                  capture_output=True, text=True, timeout=30)
            
            # Parse test results
            output = result.stdout + result.stderr
            
            # Look for test counts
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            
            # For now, just flag if we have more failures than passes
            regression_detected = failed > passed and failed > 0
            
            return {
                "regression_detected": regression_detected,
                "passed": passed,
                "failed": failed,
                "total": passed + failed
            }
        except:
            return {"regression_detected": False, "error": "test_check_failed"}
    
    def _validate_claimed_files(self):
        """Validate that claimed files actually exist"""
        evidence_file = self._find_evidence_file()
        if not evidence_file or not evidence_file.exists():
            return {"missing_files_count": 0}
        
        try:
            with open(evidence_file) as f:
                evidence = json.load(f)
        except:
            return {"missing_files_count": 0}
        
        missing_count = 0
        
        # Check common file claim patterns
        file_fields = ["files_created", "files_modified", "test_files_created"]
        
        for field in file_fields:
            if field in evidence and isinstance(evidence[field], list):
                for claimed_file in evidence[field]:
                    if not Path(claimed_file).exists():
                        missing_count += 1
        
        return {"missing_files_count": missing_count}
    
    def _find_evidence_file(self):
        """Find the most recent evidence file"""
        for path in self.evidence_paths:
            if path.exists():
                return path
        return None
    
    def _count_actual_tests(self):
        """Count actual test files in the project"""
        test_files = list(Path("tests").glob("**/test_*.py")) if Path("tests").exists() else []
        return len(test_files)
    
    def _get_actual_test_status(self):
        """Get actual test status by running pytest"""
        try:
            result = subprocess.run(['pytest', '--tb=no', '-q'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {"status": True, "returncode": 0}
            else:
                return {"status": False, "returncode": result.returncode}
        except:
            return {"status": None, "error": "could_not_run_tests"}
    
    def _validate_commit_hash(self, commit_hash):
        """Validate that a commit hash exists"""
        try:
            result = subprocess.run(['git', 'cat-file', '-e', commit_hash], 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def generate_health_report(self):
        """Generate comprehensive automation health report"""
        health_status = self.check_automation_health()
        validation_results = self.compare_claimed_vs_actual()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "automation_health": health_status,
            "validation_results": validation_results,
            "recommendations": self._generate_recommendations(health_status, validation_results)
        }
        
        return report
    
    def _generate_recommendations(self, health_status, validation_results):
        """Generate actionable recommendations"""
        recommendations = []
        
        if health_status == "failing":
            recommendations.append("CRITICAL: Stop autonomous mode - human intervention required")
            recommendations.append("Review evidence claims against actual project state")
        
        if health_status == "warning":
            recommendations.append("Monitor automation closely - issues detected")
            
        if validation_results["validation_status"] == "incomplete":
            recommendations.append("Complete missing implementation before claiming success")
            
        if validation_results["validation_status"] == "inconsistent":
            recommendations.append("Fix inconsistencies between claims and reality")
        
        if len(recommendations) == 0:
            recommendations.append("Automation health good - continue current approach")
        
        return recommendations

def main():
    """Main entry point for standalone execution"""
    reconciler = StateReconciler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        # Generate full health report
        report = reconciler.generate_health_report()
        print(json.dumps(report, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--health":
        # Just return health status
        health = reconciler.check_automation_health()
        print(health)
    else:
        # Default: validation check
        results = reconciler.compare_claimed_vs_actual()
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()