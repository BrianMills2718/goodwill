#!/usr/bin/env python3
"""
Planning Process Hook Implementation

Implements the planning process flowchart as a Claude Code hook to autonomously
execute the 8-phase planning methodology.

This hook implements the planning process flowchart from:
hook_mermaid_diagram_planning_process.txt
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class PlanningProcessHook:
    """Implements the planning process flowchart as an autonomous hook"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.planning_state_file = self.project_root / ".autonomous_state" / "planning_state.json"
        self.planning_artifacts_dir = self.project_root / "docs"
        self.current_state = self._load_planning_state()
        
    def _load_planning_state(self) -> Dict[str, Any]:
        """Load current planning state or initialize if not exists"""
        if self.planning_state_file.exists():
            with open(self.planning_state_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize new planning state
            return {
                "current_phase": "phase_1",
                "phase_status": {
                    "phase_1": "pending",
                    "phase_2": "pending", 
                    "phase_3": "pending",
                    "phase_4": "pending",
                    "phase_5": "pending",
                    "phase_6": "pending",
                    "phase_7": "pending"
                },
                "micro_iterations": 0,
                "macro_iterations": 0,
                "last_updated": time.time(),
                "planning_artifacts_locked": False
            }
    
    def _save_planning_state(self):
        """Save current planning state to disk"""
        self.planning_state_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_state["last_updated"] = time.time()
        with open(self.planning_state_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)
    
    def _project_requirements_available(self) -> bool:
        """🤖 Check if project requirements are available"""
        # Check for existing project requirements in docs/
        requirements_files = [
            self.project_root / "CLAUDE.md",
            self.project_root / "README.md",
            self.planning_artifacts_dir / "overview.md"
        ]
        
        for req_file in requirements_files:
            if req_file.exists() and req_file.stat().st_size > 100:  # Has meaningful content
                return True
        return False
    
    def _check_iteration_limits(self) -> Tuple[bool, str]:
        """🤖 Check iteration limits for safety"""
        micro_limit = 5
        macro_limit = 3
        
        if self.current_state["micro_iterations"] >= micro_limit:
            return False, f"Micro-iteration limit exceeded ({micro_limit})"
        
        if self.current_state["macro_iterations"] >= macro_limit:
            return False, f"Macro-iteration limit exceeded ({macro_limit})"
            
        return True, "Within limits"
    
    def _phase_router(self) -> str:
        """🤖 Route to current planning phase"""
        return self.current_state["current_phase"]
    
    def _advance_to_next_phase(self):
        """🤖 Advance to next planning phase"""
        phase_order = ["phase_1", "phase_2", "phase_3", "phase_4", "phase_5", "phase_6", "phase_7"]
        current_idx = phase_order.index(self.current_state["current_phase"])
        
        if current_idx < len(phase_order) - 1:
            # Mark current phase as complete
            self.current_state["phase_status"][self.current_state["current_phase"]] = "complete"
            # Advance to next phase
            self.current_state["current_phase"] = phase_order[current_idx + 1]
            self.current_state["phase_status"][self.current_state["current_phase"]] = "in_progress"
            # Reset micro iterations for new phase
            self.current_state["micro_iterations"] = 0
        else:
            # Planning complete
            self.current_state["current_phase"] = "complete"
            self.current_state["planning_artifacts_locked"] = True
    
    def execute_planning_process(self) -> Dict[str, Any]:
        """Main entry point - execute planning process flowchart"""
        
        # Check if project requirements are available
        if not self._project_requirements_available():
            return {
                "decision": "block",
                "reason": """**REQUEST**: Provide project requirements
                - Problem statement
                - Success criteria  
                - Key constraints
                
                Create or update CLAUDE.md, README.md, or docs/overview.md with project requirements."""
            }
        
        # Check iteration limits
        within_limits, limit_msg = self._check_iteration_limits()
        if not within_limits:
            return {
                "decision": "block", 
                "reason": f"**ESCALATE**: Iteration limits exceeded - {limit_msg}\nHuman intervention required"
            }
        
        # Route to current phase
        current_phase = self._phase_router()
        
        if current_phase == "complete":
            return self._handle_planning_complete()
        
        # Execute current phase
        if current_phase == "phase_1":
            return self._execute_phase_1_overview()
        elif current_phase == "phase_2":
            return self._execute_phase_2_behavior()
        elif current_phase == "phase_3":
            return self._execute_phase_3_architecture()
        elif current_phase == "phase_4":
            return self._execute_phase_4_dependencies()
        elif current_phase == "phase_5":
            return self._execute_phase_5_pseudocode()
        elif current_phase == "phase_6":
            return self._execute_phase_6_implementation()
        elif current_phase == "phase_7":
            return self._execute_phase_7_files()
        else:
            return {
                "decision": "block",
                "reason": f"Unknown planning phase: {current_phase}"
            }
    
    def _execute_phase_1_overview(self) -> Dict[str, Any]:
        """Execute Phase 1: Overview"""
        overview_file = self.planning_artifacts_dir / "overview.md"
        
        # Check if overview exists and has sufficient content
        if overview_file.exists() and overview_file.stat().st_size > 1000:
            # Validate overview quality (simplified - real implementation would use LLM)
            self._advance_to_next_phase()
            self._save_planning_state()
            return {
                "decision": "continue",
                "reason": "Phase 1 Overview complete. Advancing to Phase 2: Behavior + Acceptance Tests"
            }
        else:
            # Request overview creation
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block",
                "reason": """**EXECUTE**: Create comprehensive project overview
                
                Create docs/overview.md with:
                - Project purpose and goals
                - Key stakeholders and constraints  
                - Success criteria and metrics
                - High-level approach
                
                Minimum 1000 characters for sufficient detail."""
            }
    
    def _execute_phase_2_behavior(self) -> Dict[str, Any]:
        """Execute Phase 2: Behavior + Acceptance Tests"""
        behavior_file = self.planning_artifacts_dir / "behavior_decisions.md"
        acceptance_tests_dir = self.project_root / "tests" / "acceptance"
        
        # Check if behavior decisions and acceptance tests exist
        behavior_exists = behavior_file.exists() and behavior_file.stat().st_size > 1000
        tests_exist = acceptance_tests_dir.exists() and len(list(acceptance_tests_dir.glob("*.py"))) > 0
        
        if behavior_exists and tests_exist:
            self._advance_to_next_phase()
            self._save_planning_state()
            return {
                "decision": "continue", 
                "reason": "Phase 2 Behavior + Acceptance Tests complete. Advancing to Phase 3: Architecture"
            }
        else:
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block",
                "reason": """**EXECUTE**: Create behavior decisions and acceptance tests
                
                1. Create docs/behavior_decisions.md with system behavior requirements
                2. Create tests/acceptance/ directory with acceptance test files
                3. Define clear success criteria for system behavior
                
                Both behavior docs and acceptance tests are required to proceed."""
            }
    
    def _execute_phase_3_architecture(self) -> Dict[str, Any]:
        """Execute Phase 3: Architecture + Contract Integration Tests"""  
        arch_file = self.planning_artifacts_dir / "architecture_decisions.md"
        contract_tests_dir = self.project_root / "tests" / "integration" / "test_contracts"
        
        arch_exists = arch_file.exists() and arch_file.stat().st_size > 1000
        contract_tests_exist = contract_tests_dir.exists() and len(list(contract_tests_dir.glob("*.py"))) > 0
        
        if arch_exists and contract_tests_exist:
            self._advance_to_next_phase()
            self._save_planning_state()
            return {
                "decision": "continue",
                "reason": "Phase 3 Architecture + Contract Integration Tests complete. Advancing to Phase 4: Dependencies"
            }
        else:
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block", 
                "reason": """**EXECUTE**: Create architecture decisions and contract integration tests
                
                1. Create docs/architecture_decisions.md with system architecture
                2. Create tests/integration/test_contracts/ with contract integration tests
                3. Define component interfaces and API contracts
                
                Both architecture docs and contract tests are required."""
            }
    
    def _execute_phase_4_dependencies(self) -> Dict[str, Any]:
        """Execute Phase 4: External Dependency Research"""
        deps_file = self.planning_artifacts_dir / "dependencies" / "external_service_integration.md"
        external_tests_dir = self.project_root / "tests" / "integration" / "test_external"
        
        deps_exists = deps_file.exists() and deps_file.stat().st_size > 500
        external_tests_exist = external_tests_dir.exists() and len(list(external_tests_dir.glob("*.py"))) > 0
        
        if deps_exists and external_tests_exist:
            self._advance_to_next_phase()
            self._save_planning_state()
            return {
                "decision": "continue",
                "reason": "Phase 4 External Dependencies complete. Advancing to Phase 5: Pseudocode"
            }
        else:
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block",
                "reason": """**EXECUTE**: Research external dependencies and create external integration tests
                
                1. Create docs/dependencies/external_service_integration.md
                2. Create tests/integration/test_external/ with external dependency tests
                3. Research and validate all external APIs and services
                
                Both dependency research and external tests are required."""
            }
    
    def _execute_phase_5_pseudocode(self) -> Dict[str, Any]:
        """Execute Phase 5: Pseudocode + Architecture Review"""
        pseudocode_files = list((self.planning_artifacts_dir / "architecture").glob("pseudocode_*.md"))
        
        if len(pseudocode_files) >= 3:  # Expect multiple pseudocode files
            self._advance_to_next_phase()
            self._save_planning_state()
            return {
                "decision": "continue",
                "reason": "Phase 5 Pseudocode complete. Advancing to Phase 6: Implementation Plans"
            }
        else:
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block",
                "reason": """**EXECUTE**: Create detailed pseudocode and architecture review
                
                Create docs/architecture/pseudocode_*.md files with:
                - Detailed pseudocode for all major components
                - Architecture consistency review
                - Implementation approach for each component
                
                Minimum 3 pseudocode files required."""
            }
    
    def _execute_phase_6_implementation(self) -> Dict[str, Any]:
        """Execute Phase 6: Implementation Plans + Unit Tests"""
        impl_strategy = self.planning_artifacts_dir / "development_roadmap" / "implementation_strategy.md"
        unit_tests_dir = self.project_root / "tests" / "unit"
        
        impl_exists = impl_strategy.exists() and impl_strategy.stat().st_size > 1000
        unit_tests_exist = unit_tests_dir.exists() and len(list(unit_tests_dir.glob("*.py"))) >= 3
        
        if impl_exists and unit_tests_exist:
            self._advance_to_next_phase()
            self._save_planning_state()
            return {
                "decision": "continue",
                "reason": "Phase 6 Implementation Plans complete. Advancing to Phase 7: Files & Cross-References"
            }
        else:
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block",
                "reason": """**EXECUTE**: Create implementation plans and unit tests
                
                1. Create docs/development_roadmap/implementation_strategy.md
                2. Create comprehensive unit tests in tests/unit/
                3. Create implementation task graph and dependency plans
                
                Both implementation strategy and unit tests are required."""
            }
    
    def _execute_phase_7_files(self) -> Dict[str, Any]:
        """Execute Phase 7: Create Files & Cross-References"""
        src_dir = self.project_root / "src"
        config_files = list(self.project_root.glob("*.json")) + list((self.project_root / "config").glob("*.json"))
        
        src_exists = src_dir.exists() and len(list(src_dir.rglob("*.py"))) >= 5
        config_exists = len(config_files) >= 1
        
        if src_exists and config_exists:
            self._advance_to_next_phase()  # This will mark as complete
            self._save_planning_state()
            return {
                "decision": "continue",
                "reason": "Phase 7 Files & Cross-References complete. Planning process finished!"
            }
        else:
            self.current_state["micro_iterations"] += 1
            self._save_planning_state()
            return {
                "decision": "block",
                "reason": """**EXECUTE**: Create complete file structure and cross-references
                
                1. Create src/ directory with all Python modules
                2. Create configuration files (config/*.json)
                3. Establish cross-reference system between files
                4. Create project packaging (setup.py, requirements.txt)
                
                Complete file structure required to finish planning."""
            }
    
    def _handle_planning_complete(self) -> Dict[str, Any]:
        """Handle planning completion and handoff to implementation"""
        return {
            "decision": "continue",
            "reason": """**HANDOFF**: Planning Complete - Ready for Implementation Phase
            
            All planning artifacts have been created and validated:
            ✅ Phase 1: Overview  
            ✅ Phase 2: Behavior + Acceptance Tests
            ✅ Phase 3: Architecture + Contract Integration Tests
            ✅ Phase 4: External Dependencies + External Integration Tests
            ✅ Phase 5: Pseudocode + Architecture Review
            ✅ Phase 6: Implementation Plans + Unit Tests
            ✅ Phase 7: Files & Cross-References
            
            Planning artifacts are now LOCKED and ready for implementation handoff.
            Switch to implementation process hook."""
        }

def main():
    """Main hook entry point for Claude Code"""
    try:
        # Get input data from Claude Code
        input_data = {}
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        
        # Initialize planning process hook
        project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        hook = PlanningProcessHook(project_dir)
        
        # Execute planning process
        result = hook.execute_planning_process()
        
        # Output result for Claude Code
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        error_result = {
            "decision": "block",
            "reason": f"Planning process hook error: {str(e)}"
        }
        print(json.dumps(error_result))
        return 1

if __name__ == "__main__":
    sys.exit(main())