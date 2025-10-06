# Repository Organization Plan

## 🎯 Current Problem
The `/home/brian/projects/goodwill/` repository contains multiple distinct projects and systems mixed together, making it difficult to work on specific aspects without confusion.

## 📋 Identified Systems/Projects

### **1. Goodwill Arbitrage Project (Original Project)**
**Purpose**: Web scraping and arbitrage system for Goodwill items
**Current Location**: Mixed throughout root directory
**Key Files**:
- `src/scrapers/goodwill_scraper.py`
- `tests/test_goodwill_scraper*.py` 
- `data/`, `export_dir/`
- `demo_goodwill_scraper.py`
- Original docs in `docs/` (system_overview.md, etc.)

### **2. Autonomous TDD System Builder (From Scratch)**
**Purpose**: System that autonomously builds software projects from requirements using 8-phase methodology
**Current Location**: `autonomous_dog_food/` directory
**Key Files**:
- Complete planning methodology and documentation
- Pseudocode for autonomous system
- Tests and implementation structure
- V6 flowchart work

### **3. Autonomous Project Fixer (For Existing Projects)**  
**Purpose**: System that autonomously fixes/improves existing codebases
**Current Location**: Root directory files
**Key Files**:
- `hook_mermaid_diagram_full5_hybrid_intelligence.txt` (and previous versions)
- `claude_code_and_repo_structuring_and_tools_etc_any_projectv4.md` (and previous versions)
- `tools/workflow/` directory

### **4. Hook Exploration and Demos**
**Purpose**: Learning and demonstrating Claude Code hook capabilities
**Current Location**: Various root directories
**Key Files**:
- `forever_mode/` (177 chapters of hook demos)
- `test_hooks/`
- `reference_hooks/`
- Hook documentation files

### **5. Research and Investigations**
**Purpose**: Various explorations and research efforts
**Current Location**: Multiple `investigations/` directories
**Key Files**:
- Root `investigations/`
- `autonomous_dog_food/investigations/`
- `research/`

### **6. Temporary and Archive Files**
**Purpose**: Work-in-progress and historical files
**Current Location**: Root directory
**Key Files**:
- `temp*.txt`
- `CLAUDE_OLD*.md`
- Various planning documents
- `htmlcov/`, `logs/`

## 🏗️ Proposed Organization Structure

```
/home/brian/projects/goodwill/
├── README.md                           # Overview of all projects in repo
├── CLAUDE.md                          # Current autonomous system builder next steps
│
├── projects/
│   ├── goodwill-arbitrage/            # Original Goodwill project
│   │   ├── README.md
│   │   ├── src/scrapers/
│   │   ├── tests/
│   │   ├── data/
│   │   ├── export_dir/
│   │   ├── docs/
│   │   └── requirements.txt
│   │
│   ├── autonomous-system-builder/     # From-scratch autonomous system
│   │   ├── README.md
│   │   ├── docs/                      # 8-phase methodology
│   │   ├── src/                       # Implementation
│   │   ├── pseudo_src/                # Pseudocode
│   │   ├── tests/
│   │   ├── config/
│   │   └── tools/
│   │
│   └── autonomous-project-fixer/      # Fix existing projects system  
│       ├── README.md
│       ├── docs/
│       │   ├── v5-flowchart.md
│       │   └── methodology.md
│       ├── flowcharts/
│       │   ├── hook_mermaid_diagram_full5_hybrid_intelligence.txt
│       │   ├── hook_mermaid_diagram_full4_w_tdd.txt
│       │   └── hook_mermaid_diagram_full2.txt
│       └── tools/workflow/
│
├── research/
│   ├── hook-exploration/              # Hook learning and demos
│   │   ├── forever_mode/
│   │   ├── test_hooks/
│   │   ├── reference_hooks/
│   │   └── claude_code_hooks_*.txt
│   │
│   ├── investigations/                # Research efforts
│   │   ├── automated_workflow_planning/
│   │   ├── phase_1_foundation/
│   │   ├── scraping_research/
│   │   └── tdd_workflow/
│   │
│   └── methodology-evolution/         # Historical methodology development
│       ├── claude_code_and_repo_structuring_v1.md
│       ├── claude_code_and_repo_structuring_v2.md
│       ├── claude_code_and_repo_structuring_v3.md
│       └── claude_code_and_repo_structuring_v4.md
│
├── tools/
│   ├── autonomous_template/           # Project template
│   ├── workflow/                      # Workflow tools
│   └── test/                          # Testing utilities
│
├── archive/
│   ├── temp-files/                    # temp*.txt
│   ├── old-planning/                  # CLAUDE_OLD*.md, planning docs
│   ├── logs/                          # Historical logs
│   └── htmlcov/                       # Coverage reports
│
└── shared/
    ├── config/                        # Shared configuration
    ├── scripts/                       # Shared scripts  
    └── requirements.txt               # Common dependencies
```

## 🎯 Benefits of This Organization

### **Clear Separation of Concerns**
- **Goodwill Arbitrage**: Self-contained project for testing autonomous system
- **Autonomous System Builder**: From-scratch autonomous development system
- **Autonomous Project Fixer**: Existing project improvement system  
- **Research**: Learning and exploration separate from production systems

### **Focused Development**
- Can work on autonomous system builder without confusion from project fixer
- Goodwill project clearly identified as test case for autonomous system
- Hook exploration separated from production system development

### **Preserved Work**
- All flowchart versions preserved and organized
- Methodology evolution documented
- Research and investigations maintained

### **Scalability**
- Easy to add new test projects under `projects/`
- Research can grow without cluttering main projects
- Archive keeps history without cluttering active work

## 🔄 Migration Strategy

### **Phase 1: Create Structure**
1. Create new directory structure
2. Copy/move key files to appropriate locations
3. Update README files for each project

### **Phase 2: Update References** 
1. Update import paths in code
2. Update documentation cross-references
3. Update any scripts or configuration

### **Phase 3: Clean Archive**
1. Move temporary files to archive
2. Organize historical documents
3. Clean up root directory

### **Phase 4: Validation**
1. Test that autonomous system builder still works
2. Verify goodwill project functionality
3. Ensure no broken references

## 🎯 Next Steps

1. **Confirm organization approach** with project owner
2. **Execute migration** following phased approach
3. **Update CLAUDE.md** with new structure references
4. **Continue autonomous system development** in organized structure

This organization preserves all work while creating clear boundaries between the different systems and purposes.