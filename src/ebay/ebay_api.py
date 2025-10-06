"""
eBay API Integration
Provides eBay marketplace data access and authentication
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import base64
import hashlib
import time
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class EbayAPI:
    """eBay API client for market data and sold listings access"""
    
    def __init__(self, app_id: str = None, dev_id: str = None, cert_id: str = None, sandbox: bool = True):
        """Initialize eBay API client
        
        Args:
            app_id: eBay application ID
            dev_id: eBay developer ID  
            cert_id: eBay certificate ID
            sandbox: Use sandbox environment for testing
        """
        self.app_id = app_id
        self.dev_id = dev_id
        self.cert_id = cert_id
        self.sandbox = sandbox
        self.access_token = None
        self.token_expires_at = None
        
        # API endpoints
        if sandbox:
            self.base_url = "https://api.sandbox.ebay.com"
            self.auth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            self.base_url = "https://api.ebay.com"
            self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        
        # Rate limiting
        self.last_request_time = 0
        self.requests_per_second = 5  # Conservative rate limit
        self.min_request_interval = 1.0 / self.requests_per_second
        
        # Caching for 24 hours
        self.cache = {}
        self.cache_ttl = 24 * 3600  # 24 hours in seconds
    
    def validate_configuration(self) -> bool:
        """Validate API configuration
        
        Returns:
            bool: True if configuration is valid
        """
        required_fields = [self.app_id, self.dev_id, self.cert_id]
        return all(field is not None and field.strip() != "" for field in required_fields)
    
    async def get_access_token(self) -> str:
        """Generate OAuth 2.0 access token
        
        Returns:
            str: Access token for API calls
        """
        if not self.validate_configuration():
            raise ValueError("Invalid API configuration - missing required credentials")
        
        # Check if we have a valid cached token
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at - timedelta(minutes=5)):
            return self.access_token
        
        # Prepare OAuth request
        auth_string = f"{self.app_id}:{self.cert_id}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.auth_url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    
                    # Calculate expiration time
                    expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    logger.info("eBay API token obtained successfully")
                    return self.access_token
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get eBay token: {response.status} - {error_text}")
    
    async def validate_authentication(self) -> bool:
        """Validate API authentication
        
        Returns:
            bool: True if authentication is valid
        """
        try:
            token = await self.get_access_token()
            return token is not None and len(token) > 0
        except Exception as e:
            logger.error(f"Authentication validation failed: {e}")
            return False
    
    async def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, search_term: str, **kwargs) -> str:
        """Generate cache key for request"""
        key_data = f"{search_term}:{json.dumps(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def cache_response(self, key: str, data: Any):
        """Cache API response with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_cached_response(self, key: str) -> Optional[Any]:
        """Get cached response if still valid"""
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        if time.time() - cached_item['timestamp'] > self.cache_ttl:
            del self.cache[key]
            return None
        
        return cached_item['data']
    
    def set_cache_ttl(self, ttl_seconds: int):
        """Set cache time-to-live in seconds"""
        self.cache_ttl = ttl_seconds
    
    def parse_ebay_response(self, api_response: Dict) -> List[Dict]:
        """Parse eBay API response into standardized format
        
        Args:
            api_response: Raw eBay API response
            
        Returns:
            List of parsed item dictionaries
        """
        items = []
        
        try:
            # Navigate eBay's nested response structure
            response = api_response.get('findCompletedItemsResponse', [{}])[0]
            search_result = response.get('searchResult', [{}])[0]
            raw_items = search_result.get('item', [])
            
            for raw_item in raw_items:
                try:
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
                    
                except (KeyError, IndexError, ValueError, TypeError) as e:
                    logger.warning(f"Error parsing eBay item: {e}")
                    continue
                    
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing eBay response structure: {e}")
        
        return items
    
    async def get_sold_listings(self, search_term: str, category: str = None, 
                               start_date: datetime = None, end_date: datetime = None,
                               limit: int = 100, use_cache: bool = True) -> List[Dict]:
        """Get sold listings from eBay
        
        Args:
            search_term: Item title or keywords to search
            category: eBay category ID or name (optional)
            start_date: Filter sold items from this date
            end_date: Filter sold items until this date  
            limit: Maximum number of results
            use_cache: Whether to use cached results
            
        Returns:
            List of sold listing dictionaries
        """
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(
                search_term, category=category, limit=limit,
                start_date=start_date.isoformat() if start_date else None,
                end_date=end_date.isoformat() if end_date else None
            )
            cached_result = self.get_cached_response(cache_key)
            if cached_result is not None:
                logger.info(f"Using cached eBay results for: {search_term}")
                return cached_result
        
        # Get authentication token
        token = await self.get_access_token()
        
        # Apply rate limiting
        await self._rate_limit()
        
        # Build search parameters
        params = {
            'OPERATION-NAME': 'findCompletedItems',
            'SERVICE-VERSION': '1.0.0',
            'SECURITY-APPNAME': self.app_id,
            'RESPONSE-DATA-FORMAT': 'JSON',
            'keywords': search_term,
            'paginationInput.entriesPerPage': min(limit, 100),
            'sortOrder': 'EndTimeSoonest'
        }
        
        # Add date filters if provided
        if start_date or end_date:
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=90)
                
            params['itemFilter(0).name'] = 'EndTimeFrom'
            params['itemFilter(0).value'] = start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            params['itemFilter(1).name'] = 'EndTimeTo'  
            params['itemFilter(1).value'] = end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Add category filter if provided
        if category:
            filter_index = 2 if (start_date or end_date) else 0
            params[f'itemFilter({filter_index}).name'] = 'CategoryName'
            params[f'itemFilter({filter_index}).value'] = category
        
        # Make API request
        url = f"{self.base_url}/services/search/FindingService/v1"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        api_response = await response.json()
                        parsed_items = self.parse_ebay_response(api_response)
                        
                        # Cache the result
                        if use_cache:
                            self.cache_response(cache_key, parsed_items)
                        
                        logger.info(f"Retrieved {len(parsed_items)} sold listings for: {search_term}")
                        return parsed_items
                    else:
                        error_text = await response.text()
                        logger.error(f"eBay API error: {response.status} - {error_text}")
                        raise Exception(f"eBay API request failed: {response.status}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling eBay API: {e}")
            raise Exception(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling eBay API: {e}")
            raise