#!/usr/bin/env python3
"""
Simple test hook that should block Claude from stopping
"""
import json

# This should prevent Claude from stopping and give a direct instruction
output = {
    "decision": "block",
    "reason": "TEST: You must continue working. Create a file called test_file.txt with the content 'Hook blocking works!'"
}

print(json.dumps(output))