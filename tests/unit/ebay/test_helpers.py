"""
Test helpers for eBay API unit tests
Provides mocking utilities and fixtures
"""

import json
import os
from unittest.mock import AsyncMock, Mock
from pathlib import Path

# Load mock responses
FIXTURES_DIR = Path(__file__).parent.parent.parent / 'fixtures' / 'ebay'
with open(FIXTURES_DIR / 'mock_responses.json', 'r') as f:
    MOCK_RESPONSES = json.load(f)


class MockEbayAPI:
    """Mock eBay API for testing"""
    
    def __init__(self, app_id=None, dev_id=None, cert_id=None, sandbox=True):
        self.app_id = app_id
        self.dev_id = dev_id
        self.cert_id = cert_id
        self.sandbox = sandbox
        self.access_token = None
        self.cache = {}
    
    def validate_configuration(self):
        return True
    
    async def get_access_token(self):
        self.access_token = "mock_token_12345"
        return self.access_token
    
    async def validate_authentication(self):
        return True
    
    def cache_response(self, key, data):
        self.cache[key] = data
    
    def get_cached_response(self, key):
        return self.cache.get(key)
    
    def set_cache_ttl(self, ttl):
        self.cache_ttl = ttl
    
    def parse_ebay_response(self, api_response):
        """Parse mock eBay response"""
        items = []
        
        try:
            response = api_response.get('findCompletedItemsResponse', [{}])[0]
            search_result = response.get('searchResult', [{}])[0]
            raw_items = search_result.get('item', [])
            
            for raw_item in raw_items:
                # Extract title
                title = raw_item.get('title', [''])[0]
                
                # Extract price
                selling_status = raw_item.get('sellingStatus', [{}])[0]
                current_price = selling_status.get('currentPrice', [{}])[0]
                price = float(current_price.get('__value__', '0'))
                
                # Extract sold date
                listing_info = raw_item.get('listingInfo', [{}])[0]
                end_time = listing_info.get('endTime', [''])[0]
                
                # Extract condition
                condition_info = raw_item.get('condition', [{}])[0]
                condition = condition_info.get('conditionDisplayName', ['Unknown'])[0]
                
                # Extract shipping cost
                shipping_info = raw_item.get('shippingInfo', [{}])[0]
                shipping_cost = shipping_info.get('shippingServiceCost', [{}])[0]
                shipping = float(shipping_cost.get('__value__', '0'))
                
                item = {
                    'title': title,
                    'price': price,
                    'sold_date': end_time,
                    'condition': condition,
                    'shipping': shipping
                }
                
                items.append(item)
                
        except (KeyError, IndexError, ValueError, TypeError):
            pass
        
        return items
    
    async def get_sold_listings(self, search_term, category=None, start_date=None, 
                               end_date=None, limit=100, use_cache=True):
        """Mock get_sold_listings that returns test data"""
        
        # Return different mock data based on search term
        if "iPhone" in search_term:
            mock_response = MOCK_RESPONSES['sold_listings_response']
            return self.parse_ebay_response(mock_response)
        elif "Camera" in search_term or "Canon" in search_term:
            # Return just the camera item
            mock_response = MOCK_RESPONSES['sold_listings_response']
            all_items = self.parse_ebay_response(mock_response)
            return [item for item in all_items if 'Canon' in item['title']]
        else:
            # Return empty for unknown items
            return []


def create_mock_aiohttp_response(status=200, json_data=None, text_data=""):
    """Create a mock aiohttp response"""
    mock_response = Mock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=json_data or {})
    mock_response.text = AsyncMock(return_value=text_data)
    return mock_response


def create_mock_session():
    """Create a mock aiohttp session"""
    mock_session = Mock()
    
    # Create context managers for get and post
    mock_get_cm = AsyncMock()
    mock_post_cm = AsyncMock()
    
    mock_session.get.return_value = mock_get_cm
    mock_session.post.return_value = mock_post_cm
    
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    return mock_session