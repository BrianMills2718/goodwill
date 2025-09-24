"""
TDD Tests for Goodwill Scraper
These tests are written BEFORE implementation following TDD principles.
They will fail initially and guide our implementation.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.goodwill_scraper import GoodwillScraper


class TestGoodwillScraperCore:
    """Core functionality tests for the scraper"""
    
    def test_scraper_initialization(self):
        """Test that scraper initializes with correct settings"""
        scraper = GoodwillScraper(respect_delay=True)
        assert scraper.respect_delay == True
        assert scraper.CRAWL_DELAY == 120
        assert scraper.BASE_URL == "https://shopgoodwill.com"
        assert 'User-Agent' in scraper.HEADERS
    
    def test_scraper_without_rate_limit(self):
        """Test that scraper can be initialized without rate limiting for testing"""
        scraper = GoodwillScraper(respect_delay=False)
        assert scraper.respect_delay == False


class TestItemFetching:
    """Tests for fetching and parsing item listings"""
    
    @pytest.mark.asyncio
    async def test_fetch_100_plus_listings(self):
        """Test that scraper can fetch 100+ listings from Goodwill"""
        scraper = GoodwillScraper(respect_delay=False)
        
        # This should fetch at least 100 listings
        listings = await scraper.fetch_listings(limit=150)
        
        assert len(listings) >= 100, f"Expected at least 100 listings, got {len(listings)}"
        
        # Each listing should have required fields
        for listing in listings[:10]:  # Check first 10
            assert 'id' in listing
            assert 'title' in listing
            assert 'current_bid' in listing
            assert 'end_time' in listing
            assert 'url' in listing
    
    def test_parse_item_title(self):
        """Test parsing of item titles from listing HTML"""
        scraper = GoodwillScraper(respect_delay=False)
        
        # Mock HTML content
        mock_html = '''
        <div class="item-title">
            <h3>Vintage Canon AE-1 Camera with 50mm Lens</h3>
        </div>
        '''
        
        item_data = scraper.parse_item_details(mock_html)
        assert item_data['title'] == "Vintage Canon AE-1 Camera with 50mm Lens"
    
    def test_parse_current_bid(self):
        """Test parsing of current bid/price from listing"""
        scraper = GoodwillScraper(respect_delay=False)
        
        mock_html = '''
        <div class="current-price">
            <span class="bid-amount">$45.00</span>
        </div>
        '''
        
        item_data = scraper.parse_item_details(mock_html)
        assert item_data['current_bid'] == 45.00
        assert isinstance(item_data['current_bid'], float)
    
    def test_parse_end_time(self):
        """Test parsing of auction end time"""
        scraper = GoodwillScraper(respect_delay=False)
        
        mock_html = '''
        <div class="auction-timer" data-endtime="2025-09-25T15:30:00">
            <span>1d 5h 30m</span>
        </div>
        '''
        
        item_data = scraper.parse_item_details(mock_html)
        assert 'end_time' in item_data
        assert isinstance(item_data['end_time'], datetime)
        assert item_data['end_time'] > datetime.now()


class TestPagination:
    """Tests for handling pagination of listings"""
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_pages(self):
        """Test that scraper can handle pagination to fetch multiple pages"""
        scraper = GoodwillScraper(respect_delay=False)
        
        # Fetch 3 pages of results (assuming ~40 items per page)
        listings = await scraper.fetch_listings(pages=3)
        
        assert len(listings) >= 100, "Should fetch at least 100 items from 3 pages"
        
        # Check that we have items from different pages (IDs should be different)
        item_ids = [item['id'] for item in listings]
        assert len(set(item_ids)) == len(item_ids), "All items should have unique IDs"
    
    def test_get_next_page_url(self):
        """Test extraction of next page URL from current page"""
        scraper = GoodwillScraper(respect_delay=False)
        
        mock_html = '''
        <div class="pagination">
            <a href="/categories/listing?page=2" class="next-page">Next</a>
        </div>
        '''
        
        next_url = scraper.extract_next_page_url(mock_html, current_page=1)
        assert next_url == "https://shopgoodwill.com/categories/listing?page=2"
    
    def test_detect_last_page(self):
        """Test detection when we've reached the last page"""
        scraper = GoodwillScraper(respect_delay=False)
        
        mock_html_last_page = '''
        <div class="pagination">
            <span class="current-page">Page 10 of 10</span>
        </div>
        '''
        
        has_next = scraper.has_next_page(mock_html_last_page)
        assert has_next == False


class TestRateLimiting:
    """Tests for rate limiting functionality"""
    
    def test_rate_limit_enforced(self):
        """Test that rate limiting is enforced when enabled"""
        scraper = GoodwillScraper(respect_delay=True)
        
        # Record time before first request
        start_time = time.time()
        
        # Make two requests
        with patch.object(scraper.session, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"test"
            
            scraper._make_request("https://shopgoodwill.com/test1")
            scraper._make_request("https://shopgoodwill.com/test2")
        
        # Check that appropriate delay was applied
        elapsed = time.time() - start_time
        assert elapsed >= 120, f"Rate limit not enforced, only {elapsed}s elapsed"
    
    def test_rate_limit_disabled_for_testing(self):
        """Test that rate limiting can be disabled for testing"""
        scraper = GoodwillScraper(respect_delay=False)
        
        start_time = time.time()
        
        with patch.object(scraper.session, 'get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"test"
            
            scraper._make_request("https://shopgoodwill.com/test1")
            scraper._make_request("https://shopgoodwill.com/test2")
        
        elapsed = time.time() - start_time
        assert elapsed < 5, "Requests should be fast when rate limiting is disabled"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])