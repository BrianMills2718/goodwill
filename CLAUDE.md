# Goodwill Arbitrage Project

## 🚨 ACTIVE ERRORS AND BLOCKERS

### Current Error Status: BLOCKED

### Active Errors:
- **2025-09-20 08:09** REFERENCE_UPDATE_NEEDED: File moved requires reference updates
  - **Impact**: Cross-references pointing to old path may be broken
  - **Log**: `logs/errors/active/error_20250920_080903.log`
  - **Action**: Update all references from old path to new path
  - **Status**: NEEDS_INVESTIGATION
- **2025-09-20 08:07** BROKEN_REFERENCE: Test error injection
  - **Impact**: Testing error injection system
  - **Log**: `logs/errors/active/error_20250920_080759.log`
  - **Action**: Investigate and resolve error
  - **Status**: NEEDS_INVESTIGATION
(None currently)

### Recently Resolved Errors:
(None yet)

### Error Resolution Instructions:
1. Read the detailed log file referenced above
2. Analyze root cause and implement fix
3. Test fix thoroughly with evidence collection
4. Once verified working, remove error entry from this section
5. Move error to "Recently Resolved" with solution summary


## Project Overview
Building an automated system to identify profitable arbitrage opportunities between Goodwill online auctions and eBay resale market.

## Common Commands
*To be populated as we identify frequently used commands*

## Code Style & Patterns
- Use Python for scrapers and analysis
- Follow defensive programming for web scraping (handle failures gracefully)
- Implement comprehensive logging for all external API calls
- Use type hints and docstrings for all functions
- Test scraping logic thoroughly with mock data

## Testing Approach
- Unit tests for individual components (scrapers, analyzers)
- Integration tests for API interactions
- End-to-end tests for complete workflows
- Mock external services for reliable testing

## Workflow Guidelines
- Use "explore, plan, code, commit" pattern for major features
- Leverage subagents for complex investigations
- Document findings in appropriate `investigations/` subdirectories
- Update this CLAUDE.md file with new patterns and commands as they emerge

## Security & Compliance
- NEVER commit API keys or sensitive credentials
- Respect robots.txt and rate limits for all scraped sites
- Implement proper error handling for network failures
- Follow platform terms of service for Goodwill and eBay

## Project Structure
- `docs/behavior/` - What the system should do
- `docs/architecture/` - How to build the system  
- `docs/development_roadmap/` - Current status and implementation plan
- `investigations/` - Research findings and analysis
- `src/` - Implementation code
- `tests/` - Test suites
- `data/` - Raw and processed data
- `config/` - Configuration files