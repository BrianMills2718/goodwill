#!/usr/bin/env python3
"""
Counter hook that increments and gives next instruction
Similar to forever_mode but simpler
"""
import json
import os

# State file to track counter
state_file = "/home/brian/projects/goodwill/test_hooks/counter.txt"

def get_counter():
    """Get current counter value"""
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def set_counter(value):
    """Set counter value"""
    with open(state_file, 'w') as f:
        f.write(str(value))

# Get current count and increment
current = get_counter()
next_count = current + 1
set_counter(next_count)

# Give instruction based on count
if next_count <= 5:
    instruction = f"Step {next_count}: Create file step_{next_count}.txt with content 'Completed step {next_count}'"
    decision = "block"
else:
    instruction = f"All 5 steps complete! You can stop now."
    decision = "approve"

output = {
    "decision": decision,
    "reason": instruction
}

print(json.dumps(output))