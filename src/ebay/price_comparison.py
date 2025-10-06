"""
Price Comparison Logic
Compares Goodwill items with eBay sold listings for profit analysis
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class PriceComparator:
    """Price comparison and profit analysis for Goodwill vs eBay"""
    
    def __init__(self, ebay_api=None):
        """Initialize price comparator
        
        Args:
            ebay_api: EbayAPI instance for fetching sold listings
        """
        self.ebay_api = ebay_api
        
        # eBay fee structure (approximation)
        self.ebay_final_value_fee = 0.10  # 10%
        self.ebay_payment_fee = 0.029  # 2.9%
        self.estimated_shipping_cost = 12.95  # Average shipping
        
        # Confidence scoring weights
        self.title_weight = 0.6
        self.category_weight = 0.3
        self.price_weight = 0.1
    
    async def compare_goodwill_to_ebay(self, goodwill_item: Dict) -> Dict:
        """Compare Goodwill item to eBay sold listings
        
        Args:
            goodwill_item: Goodwill item data with title, price, category
            
        Returns:
            Dictionary with comparison results and profit analysis
        """
        if not self.ebay_api:
            raise ValueError("EbayAPI instance required for comparison")
        
        try:
            # Get eBay sold listings
            listings = await self.ebay_api.get_sold_listings(
                goodwill_item['title'],
                category=goodwill_item.get('category'),
                start_date=datetime.now() - timedelta(days=90),
                limit=50
            )
            
            if not listings:
                return {
                    'avg_sold_price': None,
                    'match_confidence': 0,
                    'recent_sales': 0,
                    'profit_potential': None,
                    'last_updated': datetime.now().isoformat()
                }
            
            # Filter recent listings (90 days)
            recent_listings = self.filter_recent_listings(listings, days=90)
            
            # Find matching listings using fuzzy matching
            matches = self.find_matching_listings(goodwill_item['title'], recent_listings)
            
            if not matches:
                return {
                    'avg_sold_price': None,
                    'match_confidence': 0,
                    'recent_sales': len(recent_listings),
                    'profit_potential': None,
                    'last_updated': datetime.now().isoformat()
                }
            
            # Calculate average price from matches
            match_prices = [match['listing']['price'] for match in matches]
            avg_price = self.calculate_average_price(match_prices, remove_outliers=True)
            
            # Calculate overall match confidence
            avg_confidence = sum(match['confidence'] for match in matches) / len(matches)
            
            # Calculate profit potential
            profit_data = self.calculate_profit_potential(goodwill_item, {'avg_sold_price': avg_price})
            
            return {
                'avg_sold_price': avg_price,
                'match_confidence': round(avg_confidence, 3),
                'recent_sales': len(matches),
                'profit_potential': profit_data['net_profit'],
                'last_updated': datetime.now().isoformat(),
                'detailed_profit': profit_data
            }
            
        except Exception as e:
            logger.error(f"Error comparing Goodwill item to eBay: {e}")
            raise
    
    def find_matching_listings(self, goodwill_title: str, ebay_listings: List[Dict]) -> List[Dict]:
        """Find eBay listings that match Goodwill item using fuzzy matching
        
        Args:
            goodwill_title: Title of Goodwill item
            ebay_listings: List of eBay sold listings
            
        Returns:
            List of matches with confidence scores
        """
        matches = []
        
        for listing in ebay_listings:
            confidence = self.calculate_match_confidence(goodwill_title, listing['title'])
            
            # Only include matches above threshold
            if confidence >= 0.3:  # 30% minimum confidence
                matches.append({
                    'listing': listing,
                    'confidence': confidence
                })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches
    
    def calculate_match_confidence(self, goodwill_title: str, ebay_title: str, 
                                 goodwill_category: str = None, ebay_category: str = None) -> float:
        """Calculate match confidence between two item titles
        
        Args:
            goodwill_title: Goodwill item title
            ebay_title: eBay listing title
            goodwill_category: Goodwill category (optional)
            ebay_category: eBay category (optional)
            
        Returns:
            Confidence score between 0 and 1
        """
        # Normalize titles for comparison
        g_title = self._normalize_title(goodwill_title)
        e_title = self._normalize_title(ebay_title)
        
        # Calculate base similarity using sequence matching
        base_similarity = SequenceMatcher(None, g_title, e_title).ratio()
        
        # Calculate word overlap
        g_words = set(g_title.split())
        e_words = set(e_title.split())
        
        if len(g_words) == 0:
            word_overlap = 0
        else:
            common_words = g_words.intersection(e_words)
            word_overlap = len(common_words) / len(g_words)
        
        # Combine similarities
        title_score = (base_similarity * 0.4) + (word_overlap * 0.6)
        
        # Apply category boost/penalty
        category_score = 0.5  # Neutral if no category info
        if goodwill_category and ebay_category:
            if goodwill_category.lower() == ebay_category.lower():
                category_score = 1.0  # Perfect match
            else:
                category_score = 0.2  # Penalty for different categories
        
        # Final weighted score
        final_score = (title_score * self.title_weight) + (category_score * self.category_weight)
        
        return min(1.0, max(0.0, final_score))
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for better matching"""
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = normalized.split()
        filtered_words = [word for word in words if word not in stopwords]
        
        # Remove special characters but keep spaces
        normalized = ' '.join(filtered_words)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def calculate_profit_potential(self, goodwill_item: Dict, ebay_data: Dict) -> Dict:
        """Calculate profit potential with fees and costs
        
        Args:
            goodwill_item: Goodwill item with price
            ebay_data: eBay data with avg_sold_price
            
        Returns:
            Dictionary with profit breakdown
        """
        goodwill_price = goodwill_item['price']
        ebay_price = ebay_data['avg_sold_price']
        
        if ebay_price is None:
            return {
                'gross_profit': None,
                'net_profit': None,
                'ebay_fees': None,
                'shipping_cost': None,
                'profit_margin': None
            }
        
        # Calculate gross profit
        gross_profit = ebay_price - goodwill_price
        
        # Calculate eBay fees
        final_value_fee = ebay_price * self.ebay_final_value_fee
        payment_fee = ebay_price * self.ebay_payment_fee
        total_fees = final_value_fee + payment_fee
        
        # Calculate net profit (subtract fees and estimated shipping)
        net_profit = gross_profit - total_fees - self.estimated_shipping_cost
        
        # Calculate profit margin
        profit_margin = (net_profit / ebay_price) if ebay_price > 0 else 0
        
        return {
            'gross_profit': round(gross_profit, 2),
            'net_profit': round(net_profit, 2),
            'ebay_fees': round(total_fees, 2),
            'shipping_cost': self.estimated_shipping_cost,
            'profit_margin': round(profit_margin, 3)
        }
    
    def filter_recent_listings(self, listings: List[Dict], days: int = 90) -> List[Dict]:
        """Filter listings to only recent sales
        
        Args:
            listings: List of eBay listings
            days: Number of days to look back
            
        Returns:
            Filtered list of recent listings
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_listings = []
        
        for listing in listings:
            try:
                # Parse eBay date format
                sold_date_str = listing['sold_date'].replace('Z', '+00:00')
                sold_date = datetime.fromisoformat(sold_date_str.replace('+00:00', ''))
                
                if sold_date >= cutoff_date:
                    recent_listings.append(listing)
                    
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing sold date: {e}")
                continue
        
        return recent_listings
    
    def calculate_average_price(self, prices: List[float], remove_outliers: bool = True) -> float:
        """Calculate average price with optional outlier removal
        
        Args:
            prices: List of prices
            remove_outliers: Whether to remove outliers before averaging
            
        Returns:
            Average price
        """
        if not prices:
            return 0.0
        
        if remove_outliers and len(prices) >= 4:
            # Remove outliers using IQR method
            sorted_prices = sorted(prices)
            q1 = sorted_prices[len(sorted_prices) // 4]
            q3 = sorted_prices[3 * len(sorted_prices) // 4]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
            
            if filtered_prices:
                return sum(filtered_prices) / len(filtered_prices)
        
        return sum(prices) / len(prices)
    
    def calculate_demand_score(self, market_data: Dict) -> float:
        """Calculate market demand score
        
        Args:
            market_data: Dictionary with recent_sales, avg_sold_price, price_variance
            
        Returns:
            Demand score between 0 and 1
        """
        recent_sales = market_data.get('recent_sales', 0)
        price_variance = market_data.get('price_variance', 1.0)
        
        # Sales volume score (normalized)
        volume_score = min(1.0, recent_sales / 20)  # 20+ sales = max score
        
        # Price consistency score (lower variance = higher score)
        consistency_score = max(0.0, 1.0 - price_variance)
        
        # Combine scores
        demand_score = (volume_score * 0.7) + (consistency_score * 0.3)
        
        return round(demand_score, 3)
    
    def apply_seasonal_adjustment(self, base_price: float, item_category: str, current_month: int) -> float:
        """Apply seasonal adjustments to price comparison
        
        Args:
            base_price: Base comparison price
            item_category: Category of item
            current_month: Current month (1-12)
            
        Returns:
            Seasonally adjusted price
        """
        # Seasonal multipliers by category and month
        seasonal_factors = {
            'winter_clothing': {
                'winter': 1.2,  # Dec, Jan, Feb
                'summer': 0.7   # Jun, Jul, Aug
            },
            'summer_clothing': {
                'summer': 1.2,
                'winter': 0.8
            },
            'holiday_items': {
                'november': 1.3,  # Pre-holiday
                'december': 1.4,  # Holiday season
                'january': 0.6    # Post-holiday
            }
        }
        
        # Determine season
        if current_month in [12, 1, 2]:
            season = 'winter'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'spring_fall'
        
        # Apply adjustment if category has seasonal factors
        category_factors = seasonal_factors.get(item_category, {})
        
        if current_month == 11:
            adjustment = category_factors.get('november', 1.0)
        elif current_month == 12:
            adjustment = category_factors.get('december', 1.0)
        elif current_month == 1:
            adjustment = category_factors.get('january', 1.0)
        else:
            adjustment = category_factors.get(season, 1.0)
        
        return base_price * adjustment