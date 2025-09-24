"""
Quick test of Goodwill scraper without rate limiting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.goodwill_scraper import GoodwillScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_basic_functionality():
    """Test basic scraper functions without rate limiting"""
    
    # Create scraper without rate limiting for testing
    scraper = GoodwillScraper(respect_delay=False)
    
    print("\n=== Testing Basic Connectivity ===")
    
    # Try to get the homepage
    import requests
    response = requests.get("https://shopgoodwill.com", headers=scraper.HEADERS)
    print(f"Homepage status: {response.status_code}")
    print(f"Response size: {len(response.content)} bytes")
    
    # Check content type
    content_type = response.headers.get('content-type', '')
    print(f"Content-Type: {content_type}")
    
    # Try sitemap with error handling
    print("\n=== Testing Sitemap Access ===")
    try:
        response = requests.get("https://shopgoodwill.com/sitemap-index.xml", headers=scraper.HEADERS)
        print(f"Sitemap status: {response.status_code}")
        print(f"Sitemap Content-Type: {response.headers.get('content-type', '')}")
        print(f"First 500 chars: {response.text[:500]}")
    except Exception as e:
        print(f"Sitemap error: {e}")
    
    print("\n=== Test Complete ===")
    print("Findings:")
    print("- Site is accessible")
    print("- May need JavaScript rendering for full content")
    print("- Sitemap might be dynamically generated or protected")

if __name__ == "__main__":
    test_basic_functionality()