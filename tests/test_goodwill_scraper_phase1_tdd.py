"""
Phase 1 TDD Tests for Goodwill Scraper
Written BEFORE implementation following TDD principles.
These tests define the Phase 1 requirements and WILL FAIL initially.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPhase1CoreRequirements:
    """
    Phase 1 Core Requirements:
    1. Scrape 100+ listings from Goodwill
    2. Parse item details (title, current bid, end time)
    3. Handle pagination
    4. Implement rate limiting (120 seconds per robots.txt)
    """
    
    def test_scraper_class_exists(self):
        """Test that GoodwillScraper class can be imported"""
        try:
            from src.scrapers.goodwill_scraper import GoodwillScraper
            scraper = GoodwillScraper()
            assert scraper is not None
        except ImportError:
            pytest.fail("GoodwillScraper class does not exist yet")
    
    def test_scraper_has_required_attributes(self):
        """Test that scraper has required configuration attributes"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        # Required attributes
        assert hasattr(scraper, 'BASE_URL')
        assert scraper.BASE_URL == "https://shopgoodwill.com"
        
        assert hasattr(scraper, 'CRAWL_DELAY')
        assert scraper.CRAWL_DELAY == 120  # robots.txt requirement
        
        assert hasattr(scraper, 'HEADERS')
        assert 'User-Agent' in scraper.HEADERS
    
    @pytest.mark.asyncio
    async def test_fetch_listings_method_exists(self):
        """Test that fetch_listings method exists and is async"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper(respect_delay=False)
        
        assert hasattr(scraper, 'fetch_listings')
        assert callable(scraper.fetch_listings)
        
        # Method should be async
        import inspect
        assert inspect.iscoroutinefunction(scraper.fetch_listings)
    
    @pytest.mark.asyncio
    async def test_fetch_100_plus_listings(self):
        """Test fetching 100+ listings - Core Requirement #1"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper(respect_delay=False)
        
        with patch.object(scraper, '_make_request') as mock_request:
            # Mock response with 120 items
            mock_request.return_value = Mock(
                text=self._generate_mock_listings_html(120),
                status_code=200
            )
            
            listings = await scraper.fetch_listings(limit=120)
            
            assert isinstance(listings, list)
            assert len(listings) >= 100, f"Expected 100+ listings, got {len(listings)}"
    
    def test_parse_item_details_method_exists(self):
        """Test that parse_item_details method exists"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        assert hasattr(scraper, 'parse_item_details')
        assert callable(scraper.parse_item_details)
    
    def test_parse_item_title(self):
        """Test parsing item title - Core Requirement #2"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        html = '''
        <div class="item-title">
            <h3>Vintage Sony Walkman WM-D6C Professional</h3>
        </div>
        '''
        
        result = scraper.parse_item_details(html)
        assert 'title' in result
        assert result['title'] == "Vintage Sony Walkman WM-D6C Professional"
    
    def test_parse_current_bid(self):
        """Test parsing current bid - Core Requirement #2"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        html = '''
        <div class="current-price">
            <span class="bid-amount">$125.50</span>
        </div>
        '''
        
        result = scraper.parse_item_details(html)
        assert 'current_bid' in result
        assert result['current_bid'] == 125.50
        assert isinstance(result['current_bid'], float)
    
    def test_parse_end_time(self):
        """Test parsing auction end time - Core Requirement #2"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        future_time = (datetime.now() + timedelta(days=2)).isoformat()
        html = f'''
        <div class="auction-timer" data-endtime="{future_time}">
            <span>2 days left</span>
        </div>
        '''
        
        result = scraper.parse_item_details(html)
        assert 'end_time' in result
        assert isinstance(result['end_time'], datetime)
        assert result['end_time'] > datetime.now()
    
    @pytest.mark.asyncio
    async def test_handle_pagination(self):
        """Test pagination handling - Core Requirement #3"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper(respect_delay=False)
        
        with patch.object(scraper, '_make_request') as mock_request:
            # Mock 3 pages with 40 items each
            mock_request.side_effect = [
                Mock(text=self._generate_mock_page(1, 40), status_code=200),
                Mock(text=self._generate_mock_page(2, 40), status_code=200),
                Mock(text=self._generate_mock_page(3, 40), status_code=200),
            ]
            
            listings = await scraper.fetch_listings(pages=3)
            
            assert len(listings) == 120  # 3 pages * 40 items
            # Check that items have unique IDs (from different pages)
            ids = [item['id'] for item in listings]
            assert len(set(ids)) == len(ids), "Items should have unique IDs"
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration - Core Requirement #4"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        
        # With rate limiting
        scraper_with_delay = GoodwillScraper(respect_delay=True)
        assert scraper_with_delay.respect_delay == True
        assert scraper_with_delay.CRAWL_DELAY == 120
        
        # Without rate limiting (for testing)
        scraper_no_delay = GoodwillScraper(respect_delay=False)
        assert scraper_no_delay.respect_delay == False
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced - Core Requirement #4"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper(respect_delay=True)
        
        with patch('time.sleep') as mock_sleep:
            with patch.object(scraper, 'session') as mock_session:
                mock_session.get.return_value.status_code = 200
                mock_session.get.return_value.text = "test"
                
                # Make two requests
                scraper._make_request("https://shopgoodwill.com/page1")
                scraper._make_request("https://shopgoodwill.com/page2")
                
                # Check that sleep was called with 120 seconds
                assert mock_sleep.called
                sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
                assert any(call >= 120 for call in sleep_calls), \
                    "Rate limit delay should be at least 120 seconds"
    
    def _generate_mock_listings_html(self, count):
        """Helper to generate mock HTML with listings"""
        items = []
        for i in range(count):
            items.append(f'''
                <div class="item" data-item-id="item_{i}">
                    <div class="item-title">
                        <h3>Test Item {i}</h3>
                    </div>
                    <div class="current-price">
                        <span class="bid-amount">${25 + i}.00</span>
                    </div>
                    <div class="auction-timer" data-endtime="2025-09-25T15:30:00">
                        <span>1 day left</span>
                    </div>
                </div>
            ''')
        return '<div class="listings">' + ''.join(items) + '</div>'
    
    def _generate_mock_page(self, page_num, items_per_page):
        """Helper to generate mock HTML for a specific page"""
        start_idx = (page_num - 1) * items_per_page
        items = []
        for i in range(start_idx, start_idx + items_per_page):
            items.append(f'''
                <div class="item" data-item-id="item_{page_num}_{i}">
                    <div class="item-title">
                        <h3>Page {page_num} Item {i}</h3>
                    </div>
                    <div class="current-price">
                        <span class="bid-amount">${25 + i}.00</span>
                    </div>
                </div>
            ''')
        
        next_link = f'<a href="?page={page_num + 1}">Next</a>' if page_num < 3 else ''
        return f'''
            <div class="listings">{''.join(items)}</div>
            <div class="pagination">{next_link}</div>
        '''


class TestPhase1ErrorHandling:
    """Tests for basic error handling"""
    
    @pytest.mark.asyncio
    async def test_handle_connection_error(self):
        """Test handling of connection errors"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper(respect_delay=False)
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_request.side_effect = ConnectionError("Network error")
            
            # Should not crash, return empty list
            listings = await scraper.fetch_listings(limit=10)
            assert listings == []
    
    def test_handle_invalid_html(self):
        """Test parsing of invalid/malformed HTML"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        invalid_html = "<<<broken>>>html<//>"
        
        # Should not crash
        result = scraper.parse_item_details(invalid_html)
        assert isinstance(result, dict)
    
    def test_handle_missing_fields(self):
        """Test handling when expected fields are missing"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper()
        
        html = '<div>Empty item</div>'
        
        result = scraper.parse_item_details(html)
        assert isinstance(result, dict)
        # Should provide defaults for missing fields
        assert 'title' in result
        assert 'current_bid' in result
        assert 'end_time' in result


class TestPhase1DataStructure:
    """Tests for data structure and format"""
    
    @pytest.mark.asyncio
    async def test_listing_data_structure(self):
        """Test that listings have the required data structure"""
        from src.scrapers.goodwill_scraper import GoodwillScraper
        scraper = GoodwillScraper(respect_delay=False)
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_request.return_value = Mock(
                text=self._generate_sample_html(),
                status_code=200
            )
            
            listings = await scraper.fetch_listings(limit=1)
            
            assert len(listings) > 0
            item = listings[0]
            
            # Required fields
            assert 'id' in item
            assert 'title' in item
            assert 'current_bid' in item
            assert 'end_time' in item
            assert 'url' in item
            
            # Correct types
            assert isinstance(item['id'], str)
            assert isinstance(item['title'], str)
            assert isinstance(item['current_bid'], (int, float))
            assert isinstance(item['end_time'], datetime)
            assert isinstance(item['url'], str)
    
    def _generate_sample_html(self):
        """Generate sample HTML for testing"""
        return '''
        <div class="listings">
            <div class="item" data-item-id="test_123">
                <a href="/item/test_123">
                    <div class="item-title">
                        <h3>Test Item Title</h3>
                    </div>
                    <div class="current-price">
                        <span class="bid-amount">$99.99</span>
                    </div>
                    <div class="auction-timer" data-endtime="2025-09-25T15:30:00">
                        <span>1 day left</span>
                    </div>
                </a>
            </div>
        </div>
        '''


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 1 TDD TEST SUITE FOR GOODWILL SCRAPER")
    print("Following TDD principles: Write tests first, then implementation")
    print("=" * 70)
    print("\nPhase 1 Requirements:")
    print("1. ✓ Scrape 100+ listings from Goodwill")
    print("2. ✓ Parse item details (title, current bid, end time)")
    print("3. ✓ Handle pagination to fetch multiple pages")
    print("4. ✓ Respect robots.txt rate limiting (120 seconds)")
    print("\nRunning tests...")
    print("-" * 70)
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])