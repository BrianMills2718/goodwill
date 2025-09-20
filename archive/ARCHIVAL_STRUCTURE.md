# Archive Directory Structure

## Purpose
The `archive/` directory maintains a mirror structure of the entire codebase for archiving files with provenance and decision records.

## Structure
```
archive/
├── ARCHIVAL_STRUCTURE.md           # This file - explains archive organization
├── docs/                           # Archived documentation
│   ├── behavior/
│   ├── architecture/
│   └── development_roadmap/
├── src/                            # Archived source code
│   ├── scrapers/
│   ├── analysis/
│   └── apis/
├── investigations/                 # Archived technical research
│   ├── scraping/
│   ├── apis/
│   ├── analysis/
│   └── errors/
├── research/                       # Archived domain research
│   ├── markets/
│   ├── strategies/
│   └── competitors/
├── tests/                          # Archived test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── tools/                          # Archived utility scripts
├── config/                         # Archived configuration files
├── data/                          # Archived data files
│   ├── raw/
│   └── processed/
├── output/                        # Archived deliverables
│   └── suggestions/
└── logs/                          # Archived log files
    ├── errors/
    └── debug/
```

## Archival Naming Convention
When archiving files, rename them with the archive date prefix:
- Original: `goodwill_scraper.py`
- Archived: `20250920_goodwill_scraper.py`

## Archival Decision Records
Each archive directory should contain an `ARCHIVAL_REASON.md` file documenting:
- **Date archived**
- **Files archived in this directory**
- **Reason for archival**
- **Context and background**
- **References to replacement files/approaches**

## Example Archival Decision Record
```markdown
# Archival Decision Record - src/scrapers/

## Archive Date: 2025-01-20

## Files Archived:
- `20250120_old_scraper.py` - Original scraping approach
- `20250120_legacy_parser.py` - BeautifulSoup-based parser

## Reason for Archival:
Replaced with new Playwright-based scraping approach that handles JavaScript-rendered content.

## Context:
The original BeautifulSoup approach failed when Goodwill updated their site to use dynamic loading. New approach is more robust but uses different architecture.

## Replacement:
- New file: `src/scrapers/playwright_scraper.py`
- Architecture change documented in: `docs/architecture/scraping_update.md`

## Decision Maker: Claude Code Session 2025-01-20
```

## Usage Guidelines
1. **Mirror structure**: Always archive to the same relative path as the original file
2. **Date prefix**: Add YYYYMMDD_ prefix to archived filename
3. **Decision record**: Create or update ARCHIVAL_REASON.md in each directory used
4. **Clean archival**: Remove original file only after successful archival
5. **Reference maintenance**: Update any cross-references to point to replacement files