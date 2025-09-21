#!/usr/bin/env python3
"""
Classify discoveries and their impact on workflow.
Usage: python3 tools/workflow/discovery_classifier.py [discovery_file]
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

class DiscoveryClassifier:
    def __init__(self):
        self.discovery_dir = Path("investigations")
        self.classifications_file = Path(".claude/discovery_classifications.json")
        
        # Impact scoring system
        self.impact_keywords = {
            "critical": ["breaks", "blocked", "error", "fail", "crash", "security"],
            "major": ["change", "refactor", "redesign", "architecture", "dependency"],
            "minor": ["optimize", "improve", "enhance", "update", "adjust"],
            "informational": ["note", "observation", "finding", "discovered", "learned"]
        }
        
        self.impact_scores = {
            "critical": 10,
            "major": 7,
            "minor": 3,
            "informational": 1
        }
        
        # Thresholds for workflow decisions
        self.MAJOR_THRESHOLD = 7
        self.MINOR_THRESHOLD = 3
        
    def scan_discoveries(self, since_timestamp=None):
        """Scan for new discoveries in investigations directory"""
        discoveries = []
        
        # Find all markdown and json files in investigations
        patterns = ["**/*.md", "**/*.json", "**/*.txt"]
        
        for pattern in patterns:
            for file_path in self.discovery_dir.glob(pattern):
                # Skip certain files
                if any(skip in str(file_path) for skip in [".git", "__pycache__", "node_modules"]):
                    continue
                
                # Check if file is new (modified after timestamp)
                if since_timestamp:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < since_timestamp:
                        continue
                
                discoveries.append(file_path)
        
        return discoveries
    
    def analyze_content(self, file_path):
        """Analyze file content to classify discovery"""
        try:
            content = file_path.read_text(errors='ignore').lower()
        except Exception as e:
            return None
        
        # Count keyword occurrences
        impact_counts = {
            "critical": 0,
            "major": 0,
            "minor": 0,
            "informational": 0
        }
        
        for level, keywords in self.impact_keywords.items():
            for keyword in keywords:
                count = len(re.findall(r'\b' + keyword + r'\b', content))
                impact_counts[level] += count
        
        # Calculate weighted score
        total_score = sum(
            count * self.impact_scores[level] 
            for level, count in impact_counts.items()
        )
        
        # Determine primary classification
        if impact_counts["critical"] > 0:
            primary_level = "critical"
        elif impact_counts["major"] > 2:
            primary_level = "major"
        elif impact_counts["minor"] > 3:
            primary_level = "minor"
        else:
            primary_level = "informational"
        
        return {
            "file": str(file_path),
            "level": primary_level,
            "score": total_score,
            "keyword_counts": impact_counts,
            "timestamp": datetime.now().isoformat()
        }
    
    def classify_discovery(self, discovery_file=None):
        """Classify a specific discovery or scan for new ones"""
        classifications = []
        
        if discovery_file:
            # Classify specific file
            file_path = Path(discovery_file)
            if not file_path.exists():
                print(f"❌ File not found: {discovery_file}")
                return []
            
            classification = self.analyze_content(file_path)
            if classification:
                classifications.append(classification)
        else:
            # Scan for new discoveries
            # Load previous classifications to get last timestamp
            last_timestamp = None
            if self.classifications_file.exists():
                try:
                    previous = json.loads(self.classifications_file.read_text())
                    if previous and isinstance(previous, list) and previous[-1].get("timestamp"):
                        last_timestamp = datetime.fromisoformat(previous[-1]["timestamp"])
                except:
                    pass
            
            discoveries = self.scan_discoveries(since_timestamp=last_timestamp)
            
            print(f"📂 Found {len(discoveries)} discovery files to analyze")
            
            for discovery in discoveries:
                classification = self.analyze_content(discovery)
                if classification:
                    classifications.append(classification)
        
        return classifications
    
    def save_classifications(self, classifications):
        """Save classifications to file"""
        # Load existing classifications
        existing = []
        if self.classifications_file.exists():
            try:
                existing = json.loads(self.classifications_file.read_text())
            except:
                pass
        
        # Add new classifications
        existing.extend(classifications)
        
        # Keep only last 100 classifications
        if len(existing) > 100:
            existing = existing[-100:]
        
        # Save
        self.classifications_file.parent.mkdir(parents=True, exist_ok=True)
        self.classifications_file.write_text(json.dumps(existing, indent=2))
    
    def get_workflow_recommendation(self, classifications):
        """Determine workflow impact from classifications"""
        if not classifications:
            return "continue", "No new discoveries"
        
        # Get highest impact score
        max_score = max(c["score"] for c in classifications)
        critical_count = sum(1 for c in classifications if c["level"] == "critical")
        major_count = sum(1 for c in classifications if c["level"] == "major")
        
        if critical_count > 0:
            return "halt", f"Critical discovery found - requires immediate attention"
        elif max_score >= self.MAJOR_THRESHOLD or major_count >= 2:
            return "review", f"Major discovery - plan update may be needed"
        elif max_score >= self.MINOR_THRESHOLD:
            return "note", f"Minor discovery - continue with awareness"
        else:
            return "continue", f"Informational discoveries only"
    
    def report(self, classifications):
        """Generate human-readable report"""
        if not classifications:
            print("📊 No new discoveries to classify")
            return
        
        print(f"\n📊 Discovery Classification Report")
        print("=" * 60)
        
        # Group by level
        by_level = {}
        for c in classifications:
            level = c["level"]
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(c)
        
        # Report by level
        for level in ["critical", "major", "minor", "informational"]:
            if level in by_level:
                items = by_level[level]
                emoji = {
                    "critical": "🔴",
                    "major": "🟠", 
                    "minor": "🟡",
                    "informational": "🔵"
                }[level]
                
                print(f"\n{emoji} {level.upper()}: {len(items)} discoveries")
                for item in items[:3]:  # Show top 3
                    file_name = Path(item["file"]).name
                    print(f"   - {file_name} (score: {item['score']})")
                
                if len(items) > 3:
                    print(f"   ... and {len(items) - 3} more")
        
        # Workflow recommendation
        action, reason = self.get_workflow_recommendation(classifications)
        
        print(f"\n🎯 Workflow Recommendation: {action.upper()}")
        print(f"   {reason}")
        
        if action == "halt":
            print("\n⚠️  CRITICAL: Review discoveries before continuing")
        elif action == "review":
            print("\n⚠️  IMPORTANT: Consider updating plan based on discoveries")
        
        print("\n" + "=" * 60)

def main():
    """Main entry point"""
    classifier = DiscoveryClassifier()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Discovery Classifier - Analyze and classify discoveries")
            print("\nUsage:")
            print("  python3 discovery_classifier.py              # Scan for new discoveries")
            print("  python3 discovery_classifier.py [file]       # Classify specific file")
            print("  python3 discovery_classifier.py --report     # Show last classification report")
            sys.exit(0)
        elif sys.argv[1] == "--report":
            # Show last report
            if classifier.classifications_file.exists():
                try:
                    classifications = json.loads(classifier.classifications_file.read_text())
                    classifier.report(classifications[-10:])  # Last 10
                except Exception as e:
                    print(f"❌ Failed to load classifications: {e}")
            else:
                print("No classifications found yet")
            sys.exit(0)
        else:
            # Classify specific file
            classifications = classifier.classify_discovery(sys.argv[1])
    else:
        # Scan for new discoveries
        classifications = classifier.classify_discovery()
    
    if classifications:
        # Save and report
        classifier.save_classifications(classifications)
        classifier.report(classifications)
        
        # Exit code based on severity
        action, _ = classifier.get_workflow_recommendation(classifications)
        if action == "halt":
            sys.exit(2)  # Critical
        elif action == "review":
            sys.exit(1)  # Major
    else:
        print("No new discoveries found")

if __name__ == "__main__":
    main()