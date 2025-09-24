# Goodwill Site Scraping Analysis

## Date: 2025-09-24
## Task: Phase 1.1 - Scraping Research

## Executive Summary
ShopGoodwill.com is an Angular-based auction platform with both auction and Buy-It-Now listings. The site has moderate anti-scraping measures but is scrapeable with proper rate limiting.

## Site Architecture

### Technology Stack
- **Frontend Framework**: Angular
- **Analytics**: Google Tag Manager, mParticle SDK, Scarab Research
- **Dynamic Content**: Client-side templating with mustache-style syntax

### URL Structure
- Homepage: `https://shopgoodwill.com`
- Categories: `/categories/gallery` (featured), `/categories/new` (newly listed)
- Individual listings: `/categories/listing?item=<itemID>`
- Search parameters: `st=` (search term), `sg=` (category), `c=`, `lp=` (low price), `hp=` (high price)

## Available Data Fields

Each item listing contains:
- **Item ID**: Unique identifier
- **Title**: Product name/description
- **Price**: Current bid or Buy-It-Now price
- **Image URL**: Product photo
- **Auction End Time**: `c_itemendtime` field
- **Number of Bids**: `c_numbids` field
- **Listing Type**: Auction vs Buy-It-Now

## Anti-Scraping Measures

### robots.txt Analysis
- **Crawl-delay**: 120 seconds (MUST respect this)
- **Disallowed paths**:
  - `/shopgoodwill/` (user account areas)
  - `/home-preview/`
  - `/checkout/`
  - `/categories/listing?st=` (search with parameters)
- **Sitemap**: Available at `https://shopgoodwill.com/sitemap-index.xml`

### Other Observations
- No apparent CAPTCHA on initial page loads
- JavaScript-rendered content requires headless browser or API analysis
- Uses tracking/personalization SDKs but no obvious bot detection services

## Scraping Strategy Recommendations

1. **Respect Rate Limits**: Implement 120-second delay between requests minimum
2. **Use Sitemap**: Parse sitemap for systematic crawling
3. **Headless Browser**: Required for JavaScript-rendered content (Playwright/Selenium)
4. **User-Agent Rotation**: Use legitimate browser user agents
5. **Session Management**: May need cookie handling for detailed views

## Next Steps
1. Create initial scraper prototype with rate limiting
2. Test sitemap parsing for item discovery
3. Implement data extraction for key fields
4. Set up database schema for storing scraped data