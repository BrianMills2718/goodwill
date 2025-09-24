#!/usr/bin/env python3
"""
Autonomous TDD Workflow Hook for Goodwill Project
Based on proven forever_mode pattern
"""
import os
import sys
import json

# Get the project root directory from the environment variable provided by Claude Code
project_root = os.environ.get('CLAUDE_PROJECT_DIR')
if not project_root:
    print("Error: CLAUDE_PROJECT_DIR environment variable not set. Cannot determine project root.", file=sys.stderr)
    sys.exit(1)

state_file_path = os.path.join(project_root, '.claude', 'workflow_state.txt')

def get_current_step():
    """Reads the current workflow step from the state file."""
    if os.path.exists(state_file_path):
        with open(state_file_path, 'r') as f:
            try:
                return f.read().strip()
            except:
                return "load_phase"
    return "load_phase"

def set_current_step(step):
    """Writes the new step to the state file."""
    with open(state_file_path, 'w') as f:
        f.write(step)

def get_next_step(current_step):
    """Determine next TDD step based on current state"""
    # Simple TDD cycle
    workflow = {
        "load_phase": "explore",
        "explore": "write_tests", 
        "write_tests": "implement",
        "implement": "run_tests",
        "run_tests": "doublecheck",
        "doublecheck": "commit",
        "commit": "explore"  # Start new cycle
    }
    
    return workflow.get(current_step, "load_phase")

def get_instruction(step):
    """Generate instruction for each workflow step"""
    instructions = {
        "load_phase": "Read docs/development_roadmap/phases.md and identify the current phase (Phase 1: Foundation). Update the CLAUDE.md file with the phase details including the four tasks: Scraping Research, eBay API Setup, Technical Infrastructure, and Keyword Research.",
        
        "explore": "Explore the codebase for Phase 1 requirements. Read docs/behavior/requirements.md and any existing architecture docs. Visit shopgoodwill.com to understand their auction structure. Create investigations/phase_1_foundation/exploration_notes.md documenting your findings about how to scrape Goodwill listings.",
        
        "write_tests": "Write tests for the Goodwill scraper following TDD principles. Create tests/test_goodwill_scraper.py with pytest tests that verify: fetching 100+ listings, parsing item details (title, current bid, end time), handling pagination, and rate limiting. The tests should fail initially as we haven't implemented the scraper yet.",
        
        "implement": "Implement the Goodwill scraper to pass your tests. Create src/scrapers/goodwill_scraper.py with a GoodwillScraper class. Implement methods to fetch listings, parse HTML with BeautifulSoup, handle pagination, and include rate limiting. Make all tests pass.",
        
        "run_tests": "Run pytest tests/test_goodwill_scraper.py -v and verify all tests pass. Create investigations/phase_1_foundation/test_results.md with the test output showing all tests passing and any coverage metrics.",
        
        "doublecheck": "Verify the scraper meets Phase 1 requirements. Test manually that it can scrape 100+ real Goodwill listings. Check error handling and rate limiting work properly. Create investigations/phase_1_foundation/verification_evidence.md documenting that all success criteria are met.",
        
        "commit": "Commit your implementation with git. Use git add to stage all new files, then git commit with a descriptive message about what was implemented. Create investigations/phase_1_foundation/commit_evidence.md showing the commit was successful."
    }
    
    return instructions.get(step, f"Continue working on {step} to progress the TDD workflow.")

def main():
    current_step = get_current_step()
    next_step = get_next_step(current_step)
    
    # Update the state file with the new step
    set_current_step(next_step)
    
    # Get instruction for the next step
    instruction = get_instruction(next_step)
    
    # For Stop hooks, we need to output JSON with decision: "block" and reason
    # to prevent Claude from stopping and provide the next instruction
    output = {
        "decision": "block",
        "reason": instruction
    }
    
    # Print JSON output to stdout
    print(json.dumps(output))

if __name__ == "__main__":
    main()