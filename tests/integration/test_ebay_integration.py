"""
Integration tests for eBay API with Goodwill scraper
Tests the complete workflow from scraping to price comparison
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.scrapers.goodwill_scraper import GoodwillScraper
from src.ebay.ebay_api import EbayAPI
from src.ebay.price_comparison import PriceComparator


class TestEbayIntegration:
    """Test eBay integration with Goodwill scraper"""
    
    def test_scraper_initialization_with_ebay(self):
        """Test that scraper initializes correctly with eBay credentials"""
        scraper = GoodwillScraper(
            ebay_app_id="test_app",
            ebay_dev_id="test_dev", 
            ebay_cert_id="test_cert",
            enable_ebay_analysis=True
        )
        
        assert scraper.enable_ebay_analysis == True
        assert scraper.ebay_api is not None
        assert scraper.price_comparator is not None
        assert isinstance(scraper.ebay_api, EbayAPI)
        assert isinstance(scraper.price_comparator, PriceComparator)
    
    def test_scraper_initialization_without_ebay(self):
        """Test that scraper works normally without eBay integration"""
        scraper = GoodwillScraper(enable_ebay_analysis=False)
        
        assert scraper.enable_ebay_analysis == False
        assert scraper.ebay_api is None
        assert scraper.price_comparator is None
    
    @pytest.mark.asyncio
    async def test_fetch_listings_without_ebay_analysis(self):
        """Test fetch_listings_with_ebay_analysis returns normal listings when disabled"""
        scraper = GoodwillScraper(enable_ebay_analysis=False)
        
        # Mock the basic fetch_listings method
        mock_listings = [
            {'title': 'Test Item 1', 'price': 25.99},
            {'title': 'Test Item 2', 'price': 45.50}
        ]
        
        with patch.object(scraper, 'fetch_listings', return_value=mock_listings):
            result = await scraper.fetch_listings_with_ebay_analysis(limit=2)
            
            assert result == mock_listings  # Should return original listings
    
    @pytest.mark.asyncio
    async def test_fetch_listings_with_ebay_analysis_enabled(self):
        """Test fetch_listings_with_ebay_analysis with eBay integration enabled"""
        scraper = GoodwillScraper(
            ebay_app_id="test_app",
            ebay_dev_id="test_dev",
            ebay_cert_id="test_cert", 
            enable_ebay_analysis=True
        )
        
        # Mock Goodwill listings
        mock_goodwill_listings = [
            {'title': 'Canon Camera', 'price': 45.99, 'category': 'cameras'}
        ]
        
        # Mock eBay analysis result
        mock_ebay_analysis = {
            'avg_sold_price': 89.50,
            'match_confidence': 0.85,
            'profit_potential': 33.51,
            'recent_sales': 12
        }
        
        with patch.object(scraper, 'fetch_listings', return_value=mock_goodwill_listings):
            with patch.object(scraper.price_comparator, 'compare_goodwill_to_ebay', return_value=mock_ebay_analysis):
                result = await scraper.fetch_listings_with_ebay_analysis(limit=1)
                
                assert len(result) == 1
                enhanced_item = result[0]
                
                # Check structure
                assert 'goodwill' in enhanced_item
                assert 'ebay_analysis' in enhanced_item
                assert 'combined_data' in enhanced_item
                
                # Check data
                assert enhanced_item['goodwill']['title'] == 'Canon Camera'
                assert enhanced_item['ebay_analysis']['profit_potential'] == 33.51
                assert enhanced_item['combined_data']['recommendation'] == 'recommended'
    
    def test_generate_recommendation_logic(self):
        """Test recommendation generation logic"""
        scraper = GoodwillScraper()
        
        # Test high profit, high confidence -> highly_recommended
        ebay_analysis = {'profit_potential': 60.0, 'match_confidence': 0.8}
        recommendation = scraper._generate_recommendation({}, ebay_analysis)
        assert recommendation == 'highly_recommended'
        
        # Test medium profit, medium confidence -> recommended
        ebay_analysis = {'profit_potential': 30.0, 'match_confidence': 0.6}
        recommendation = scraper._generate_recommendation({}, ebay_analysis)
        assert recommendation == 'recommended'
        
        # Test low profit -> consider
        ebay_analysis = {'profit_potential': 15.0, 'match_confidence': 0.4}
        recommendation = scraper._generate_recommendation({}, ebay_analysis)
        assert recommendation == 'consider'
        
        # Test very low profit -> not_recommended
        ebay_analysis = {'profit_potential': 5.0, 'match_confidence': 0.3}
        recommendation = scraper._generate_recommendation({}, ebay_analysis)
        assert recommendation == 'not_recommended'
        
        # Test no data -> insufficient_data
        recommendation = scraper._generate_recommendation({}, {})
        assert recommendation == 'insufficient_data'
    
    @pytest.mark.asyncio
    async def test_get_top_profit_opportunities(self):
        """Test getting top profit opportunities"""
        scraper = GoodwillScraper(
            ebay_app_id="test_app",
            ebay_dev_id="test_dev",
            ebay_cert_id="test_cert",
            enable_ebay_analysis=True
        )
        
        # Mock enhanced listings with different profit potentials
        mock_enhanced_listings = [
            {
                'goodwill': {'title': 'Low Profit Item', 'price': 10.0},
                'ebay_analysis': {'profit_potential': 8.0},
                'combined_data': {'recommendation': 'not_recommended'}
            },
            {
                'goodwill': {'title': 'High Profit Item', 'price': 25.0},
                'ebay_analysis': {'profit_potential': 45.0},
                'combined_data': {'recommendation': 'recommended'}
            },
            {
                'goodwill': {'title': 'Medium Profit Item', 'price': 15.0},
                'ebay_analysis': {'profit_potential': 20.0},
                'combined_data': {'recommendation': 'consider'}
            }
        ]
        
        with patch.object(scraper, 'fetch_listings_with_ebay_analysis', return_value=mock_enhanced_listings):
            opportunities = await scraper.get_top_profit_opportunities(limit=10, min_profit=15.0)
            
            # Should return 2 items (profit >= 15.0), sorted by profit
            assert len(opportunities) == 2
            assert opportunities[0]['ebay_analysis']['profit_potential'] == 45.0  # Highest first
            assert opportunities[1]['ebay_analysis']['profit_potential'] == 20.0  # Second highest
    
    @pytest.mark.asyncio
    async def test_analyze_single_item(self):
        """Test analyzing a single item with eBay comparison"""
        scraper = GoodwillScraper(
            ebay_app_id="test_app",
            ebay_dev_id="test_dev",
            ebay_cert_id="test_cert",
            enable_ebay_analysis=True
        )
        
        # Mock item data
        mock_item_data = {
            'title': 'Vintage Watch',
            'price': 35.99,
            'category': 'jewelry'
        }
        
        mock_ebay_analysis = {
            'avg_sold_price': 89.50,
            'match_confidence': 0.75,
            'profit_potential': 42.51,
            'recent_sales': 8
        }
        
        with patch.object(scraper, 'get_item_details', return_value=mock_item_data):
            with patch.object(scraper.price_comparator, 'compare_goodwill_to_ebay', return_value=mock_ebay_analysis):
                result = await scraper.analyze_single_item('https://shopgoodwill.com/item/123456')
                
                assert 'goodwill' in result
                assert 'ebay_analysis' in result
                assert 'combined_data' in result
                
                assert result['goodwill']['title'] == 'Vintage Watch'
                assert result['ebay_analysis']['profit_potential'] == 42.51
                assert result['combined_data']['recommendation'] == 'recommended'
    
    @pytest.mark.asyncio
    async def test_error_handling_during_ebay_analysis(self):
        """Test error handling when eBay analysis fails"""
        scraper = GoodwillScraper(
            ebay_app_id="test_app", 
            ebay_dev_id="test_dev",
            ebay_cert_id="test_cert",
            enable_ebay_analysis=True
        )
        
        # Mock Goodwill listings
        mock_goodwill_listings = [
            {'title': 'Problematic Item', 'price': 25.99}
        ]
        
        with patch.object(scraper, 'fetch_listings', return_value=mock_goodwill_listings):
            # Mock eBay analysis to raise an exception
            with patch.object(scraper.price_comparator, 'compare_goodwill_to_ebay', side_effect=Exception("API Error")):
                result = await scraper.fetch_listings_with_ebay_analysis(limit=1)
                
                assert len(result) == 1
                enhanced_item = result[0]
                
                # Should still return item but with failed analysis
                assert enhanced_item['goodwill']['title'] == 'Problematic Item'
                assert enhanced_item['ebay_analysis'] is None
                assert enhanced_item['combined_data']['recommendation'] == 'analysis_failed'
    
    def test_ebay_analysis_disabled_error_handling(self):
        """Test error handling when eBay analysis is required but disabled"""
        scraper = GoodwillScraper(enable_ebay_analysis=False)
        
        # Should raise error for methods that require eBay analysis
        with pytest.raises(ValueError, match="eBay analysis must be enabled"):
            asyncio.run(scraper.get_top_profit_opportunities())
        
        with pytest.raises(ValueError, match="eBay analysis must be enabled"):
            asyncio.run(scraper.analyze_single_item("https://example.com/item/123"))


if __name__ == "__main__":
    print("=" * 60)
    print("EBAY INTEGRATION TEST SUITE")
    print("Testing complete workflow from Goodwill scraping to eBay analysis")
    print("=" * 60)
    
    pytest.main([__file__, "-v"])