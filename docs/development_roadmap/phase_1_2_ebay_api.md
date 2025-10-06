# Phase 1.2: eBay API Setup

## Goal
Establish eBay API integration for market data access and sold listings capability to enable price comparison with Goodwill items.

## Success Criteria

### 1. eBay API Authentication ✅
- [ ] eBay Developer Account created and configured
- [ ] API credentials (App ID, Dev ID, Cert ID) obtained and secured
- [ ] OAuth 2.0 token generation working
- [ ] API authentication test passes

### 2. Sold Listings API Integration ✅  
- [ ] `get_sold_listings(item_title, category=None)` function implemented
- [ ] Returns structured data: price, sold_date, condition, shipping, title
- [ ] Handles eBay API rate limits (5000 calls/day for sandbox, 100k/day production)
- [ ] Error handling for API failures and network issues
- [ ] Test with at least 5 different item searches

### 3. Price Comparison Logic ✅
- [ ] `compare_goodwill_to_ebay(goodwill_item)` function implemented  
- [ ] Matches Goodwill item title to eBay sold listings using fuzzy matching
- [ ] Calculates profit potential (eBay avg - Goodwill price - fees - shipping)
- [ ] Returns confidence score for match quality
- [ ] Filters out listings older than 90 days

### 4. Integration with Existing Scraper ✅
- [ ] Goodwill scraper enhanced to call eBay API for each item
- [ ] Combined data structure with both Goodwill and eBay data
- [ ] Database schema updated to store eBay comparison data
- [ ] End-to-end workflow: scrape → analyze → store working

### 5. Testing & Verification ✅
- [ ] Unit tests for all eBay API functions (8+ tests)
- [ ] Integration tests with real eBay API calls (sandbox mode)
- [ ] Performance test: 100 items processed in <10 minutes
- [ ] Error handling test: graceful degradation when eBay API unavailable
- [ ] Test coverage ≥80%

## Technical Requirements

### API Configuration
- **Environment**: Start with eBay Sandbox, migrate to Production
- **Endpoints**: 
  - Finding API for sold listings: `findCompletedItems`
  - Trading API for detailed item data (if needed)
- **Rate Limits**: Implement exponential backoff for rate limiting
- **Caching**: Cache eBay results for 24 hours to reduce API calls

### Data Structure Enhancement
```python
# Enhanced Goodwill item with eBay analysis
{
    "goodwill": {
        "title": "Vintage Leather Jacket",
        "price": 25.99,
        "url": "https://...",
        "category": "clothing"
    },
    "ebay_analysis": {
        "avg_sold_price": 89.50,
        "match_confidence": 0.85,
        "recent_sales": 12,
        "profit_potential": 53.51,  # After fees
        "last_updated": "2025-09-24T18:00:00Z"
    }
}
```

### Error Handling Strategy
- **API Rate Limits**: Exponential backoff with 2^n second delays
- **Network Failures**: Retry up to 3 times, then mark item as "analysis_failed"
- **No Matches Found**: Store as null analysis with reason
- **Invalid API Response**: Log error, continue with next item

## Test Implementation Plan

### TDD Approach
1. **Write Tests First**: Create failing tests for each success criteria
2. **Implement Minimum**: Build just enough code to make tests pass
3. **Refactor**: Clean up code while keeping tests green
4. **Integration**: Test end-to-end workflow

### Test Files Structure
```
tests/
├── unit/
│   ├── test_ebay_api.py           # eBay API functions
│   ├── test_price_comparison.py   # Price analysis logic
│   └── test_data_integration.py   # Data structure handling
├── integration/
│   ├── test_ebay_sandbox.py       # Real API calls (sandbox)
│   └── test_full_workflow.py      # End-to-end pipeline
└── fixtures/
    ├── ebay_responses.json        # Mock API responses
    └── test_goodwill_items.json   # Sample Goodwill data
```

## Deliverables

1. **`src/ebay/`** - New module with eBay API integration
2. **Enhanced scraper** - Goodwill scraper with eBay analysis  
3. **Test suite** - Comprehensive tests for all functionality
4. **Documentation** - API usage guide and configuration instructions
5. **Database migration** - Schema updates for eBay data storage

## Phase 1.2 Complete When:
- All 24 success criteria checkboxes completed ✅
- Test coverage ≥80% achieved
- End-to-end demonstration: Scrape 10 Goodwill items → Get eBay analysis → Identify top 3 profit opportunities
- Performance benchmark met: 100 items analyzed in <10 minutes
- Code reviewed and committed with proper documentation

## Next Phase: 1.3 Technical Infrastructure
After Phase 1.2 completion, proceed to database design, data persistence, and scraper architecture optimization.