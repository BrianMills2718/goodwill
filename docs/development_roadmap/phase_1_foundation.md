# Phase 1: Foundation (Weeks 1-2)

## Goal
Establish core data collection capabilities and understand the technical landscape.

## Current Status
- [x] Project setup and documentation
- [ ] **Active**: Goodwill scraping investigation
- [ ] **Next**: eBay API research

## Detailed Tasks

### 1.1 Scraping Research
**Owner**: Use Claude Code subagents for parallel investigation

- [ ] **Goodwill Site Analysis**
  - [ ] Visit https://shopgoodwill.com/home and analyze technology stack
  - [ ] Examine search functionality - URL parameters, filters, sorting
  - [ ] Test rate limiting - start with 1 req/sec, increase gradually
  - [ ] Check robots.txt and terms of service for restrictions
  - [ ] Identify JavaScript frameworks and dynamic content loading
  - [ ] Map out search result structure and pagination
  - [ ] Document image availability and quality patterns

- [ ] **Anti-Bot Detection**
  - [ ] Test with different user agents (browser, mobile, bot)
  - [ ] Look for CAPTCHA triggers and IP blocking patterns
  - [ ] Examine session requirements and cookie dependencies
  - [ ] Test from different IP addresses if possible
  - [ ] Document any behavioral detection (mouse movements, timing)

- [ ] **Data Extraction Points**
  - [ ] Item listings - title, description, price, images, seller
  - [ ] Auction details - end time, bid count, shipping info
  - [ ] Search metadata - total results, category info
  - [ ] Historical data availability (if any)

### 1.2 eBay API Research
**Priority**: Start immediately after initial Goodwill analysis

- [ ] **API Access Setup**
  - [ ] Create eBay developer account
  - [ ] Understand API tiers and rate limits
  - [ ] Get sandbox and production keys
  - [ ] Review pricing structure and costs

- [ ] **Sold Listings Capability**
  - [ ] Test Finding API for completed listings
  - [ ] Determine historical data depth (30 days? 90 days?)
  - [ ] Understand search parameters and filters
  - [ ] Test with sample luxury goods queries
  - [ ] Document response format and available fields

- [ ] **Market Intelligence Features**
  - [ ] Price history capabilities
  - [ ] Trending/hot items data
  - [ ] Category-specific insights
  - [ ] Geographical price variations

### 1.3 Technical Infrastructure
**Goal**: Foundation for data collection and analysis

- [ ] **Database Design**
  - [ ] Items table (id, title, description, price, images, source_url, scraped_at)
  - [ ] Auctions table (item_id, end_time, bid_count, current_price, shipping)
  - [ ] Market_data table (item_id, platform, sold_price, sold_date, condition)
  - [ ] Analysis table (item_id, profit_estimate, confidence_score, flags)

- [ ] **Development Environment**
  - [ ] Python virtual environment setup
  - [ ] Required packages: requests, beautifulsoup4, selenium, pandas, sqlite3
  - [ ] Logging configuration for debugging and monitoring
  - [ ] Error handling and retry logic framework

- [ ] **Initial Scraper Architecture**
  - [ ] Modular design for different scraping methods (requests vs browser)
  - [ ] Rate limiting and politeness controls
  - [ ] Data validation and cleaning pipeline
  - [ ] Storage interface for different backends

### 1.4 Target Keywords and Categories
**Focus**: High-value, identifiable items with strong resale markets

- [ ] **Luxury Goods**
  - [ ] Designer handbags: "Louis Vuitton", "Gucci", "Chanel", "Prada", "Hermès"
  - [ ] Luxury watches: "Rolex", "Omega", "Cartier", "Tag Heuer", "Breitling"
  - [ ] Designer clothing: "Versace", "Armani", "Ralph Lauren", "Hugo Boss"
  - [ ] Common misspellings: "Louie Vuiton", "Luis Vuitton", "Rollex", etc.

- [ ] **Electronics**
  - [ ] Apple products: "iPhone", "iPad", "MacBook", "Apple Watch"
  - [ ] Gaming: "PlayStation", "Xbox", "Nintendo Switch", "Steam Deck"
  - [ ] Audio: "Bose", "Sony", "Sennheiser", "Audio-Technica"
  - [ ] Cameras: "Canon", "Nikon", "Sony", "Leica"

- [ ] **High-Value Categories**
  - [ ] Musical instruments: "Gibson", "Fender", "Martin", "Yamaha"
  - [ ] Art and collectibles: "original", "signed", "limited edition"
  - [ ] Vintage items: specific decades, retro brands
  - [ ] Professional tools: "Snap-on", "Mac Tools", high-end equipment

## Success Criteria
- [ ] Successfully scrape 100+ Goodwill listings without being blocked
- [ ] Retrieve eBay sold listings for 10+ test items across different categories
- [ ] Working database with sample data from both sources
- [ ] Documented keyword lists covering 5+ high-value categories
- [ ] Clear understanding of technical limitations and opportunities

## Risk Mitigation
- [ ] Multiple scraping approaches ready (requests + Selenium backup)
- [ ] API rate limiting strategies and error handling
- [ ] Legal compliance review of terms of service
- [ ] Data validation to catch structural changes

## Deliverables
- `investigations/scraping/goodwill_analysis.md` - Complete technical analysis
- `investigations/apis/ebay_research.md` - API capabilities and limitations  
- `src/scrapers/goodwill_scraper.py` - Working prototype scraper
- `src/apis/ebay_client.py` - Basic eBay API integration
- `config/keywords.json` - Organized keyword lists by category
- `data/samples/` - Test data from both sources

## Claude Code Workflow Notes
- Use **subagents extensively** for parallel research on Goodwill and eBay
- **"Think harder"** for complex architecture decisions
- **Multi-Claude approach** if investigations become complex
- **Document everything** in investigations/ for future reference
- **Test iteratively** - don't build everything before testing components