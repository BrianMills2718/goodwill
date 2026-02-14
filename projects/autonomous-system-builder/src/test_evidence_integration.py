#!/usr/bin/env python3
"""
Test file to trigger evidence validator hook
This should trigger PostToolUse evidence validation
"""

def test_evidence_integration():
    """Test function to verify evidence hook triggers"""
    # Testing PreToolUse validation hook  
    return "Evidence hook integration test - UPDATED"

if __name__ == "__main__":
    print(test_evidence_integration())