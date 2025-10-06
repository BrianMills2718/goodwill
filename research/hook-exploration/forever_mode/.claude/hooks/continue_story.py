#!/usr/bin/env python3
import os
import sys

# Get the project root directory from the environment variable provided by Claude Code
# This ensures the script can find the .claude directory reliably.
project_root = os.environ.get('CLAUDE_PROJECT_DIR')
if not project_root:
    print("Error: CLAUDE_PROJECT_DIR environment variable not set. Cannot determine project root.", file=sys.stderr)
    sys.exit(1) # Exit with error

state_file_path = os.path.join(project_root, '.claude', 'story_state.txt')

def get_current_chapter():
    """Reads the current chapter number from the state file."""
    if os.path.exists(state_file_path):
        with open(state_file_path, 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0 # Default if file content is invalid
    return 0 # Default if file doesn't exist

def set_current_chapter(chapter_num):
    """Writes the new chapter number to the state file."""
    with open(state_file_path, 'w') as f:
        f.write(str(chapter_num))

def main():
    current_chapter = get_current_chapter()
    next_chapter = current_chapter + 1

    # Update the state file with the new chapter number
    set_current_chapter(next_chapter)

    # Construct the prompt for Claude Code
    prompt = (
        f"Continue the story. Write Chapter {next_chapter} to `chapter_{next_chapter}.txt`. "
        f"Ensure the content flows naturally from the previous chapter. "
        f"If `chapter_{current_chapter}.txt` exists, read it to maintain continuity."
    )

    # For Stop hooks, we need to output JSON with decision: "block" and reason
    # to prevent Claude from stopping and provide the next instruction
    import json
    output = {
        "decision": "block",
        "reason": prompt
    }
    
    # Print JSON output to stdout
    print(json.dumps(output))

    # Exit with code 0 to indicate success

if __name__ == "__main__":
    main()