"""
Google Reviews data extractor using Google Places API and web scraping.
Handles business reviews and ratings extraction.
"""
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from urllib.parse import urlencode, quote_plus

from bs4 import BeautifulSoup
from tqdm import tqdm

from .base_extractor import BaseExtractor, ExtractionError, RateLimitError, AuthenticationError
from ..config import APIConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GoogleReviewsExtractor(BaseExtractor):
    """Google Reviews data extractor"""
    
    def __init__(self, service: str, max_posts: int = 500):
        super().__init__(service, max_posts)
        self.api_key = APIConfig.GOOGLE_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate Google API credentials"""
        if not self.api_key:
            logger.warning("Google API key not configured, will use web scraping only")
        else:
            try:
                # Test API connection
                test_url = f"{self.base_url}/place/textsearch/json"
                params = {
                    'query': 'test',
                    'key': self.api_key
                }
                response = requests.get(test_url, params=params)
                
                if response.status_code == 200:
                    logger.info("Google API authentication successful")
                else:
                    logger.warning(f"Google API test failed: {response.text}")
                    
            except Exception as e:
                logger.error(f"Google API validation failed: {e}")
    
    def extract_posts(self, days: int = 30, **kwargs) -> List[Dict[str, Any]]:
        """Extract Google reviews"""
        logger.info(f"Extracting Google reviews for '{self.service}' from last {days} days")
        
        try:
            # Search for businesses
            businesses = self._search_businesses(self.service)
            
            if not businesses:
                logger.warning(f"No businesses found for service: {self.service}")
                return []
            
            all_reviews = []
            for business in businesses[:5]:  # Limit to top 5 businesses
                business_reviews = self._extract_business_reviews(business['place_id'], days)
                all_reviews.extend(business_reviews)
                
                if len(all_reviews) >= self.max_posts:
                    break
            
            # Limit to max_posts
            reviews = all_reviews[:self.max_posts]
            self.posts_extracted = len(reviews)
            
            logger.info(f"Extracted {len(reviews)} Google reviews")
            return reviews
            
        except Exception as e:
            self._handle_extraction_error(e, "Google reviews extraction")
            return []
    
    def _search_businesses(self, query: str) -> List[Dict[str, Any]]:
        """Search for businesses using Google Places API"""
        businesses = []
        
        if not self.api_key:
            # Fallback to web scraping
            return self._search_businesses_scrape(query)
        
        try:
            search_url = f"{self.base_url}/place/textsearch/json"
            params = {
                'query': query,
                'key': self.api_key,
                'language': 'fr',
                'region': 'fr'
            }
            
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    businesses = data.get('results', [])
                    
                    # Sort by rating and user ratings count
                    businesses.sort(
                        key=lambda x: (x.get('rating', 0), x.get('user_ratings_total', 0)), 
                        reverse=True
                    )
                    
                    logger.info(f"Found {len(businesses)} businesses for query: {query}")
                else:
                    logger.warning(f"Google Places API error: {data.get('status')}")
                    
        except Exception as e:
            logger.error(f"Error searching businesses: {e}")
            # Fallback to scraping
            businesses = self._search_businesses_scrape(query)
        
        return businesses
    
    def _search_businesses_scrape(self, query: str) -> List[Dict[str, Any]]:
        """Fallback business search using web scraping"""
        businesses = []
        
        try:
            # Construct Google search URL
            search_query = f"{query} avis google"
            encoded_query = quote_plus(search_query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract business information from search results
                # This is a simplified extraction - real implementation would need
                # more sophisticated parsing based on Google's HTML structure
                business_elements = soup.find_all('div', class_='BNeawe')
                
                for element in business_elements[:10]:  # Limit results
                    business_name = element.get_text(strip=True)
                    if business_name and len(business_name) > 3:
                        businesses.append({
                            'name': business_name,
                            'place_id': f"scrape_{len(businesses)}",
                            'rating': 0,
                            'user_ratings_total': 0,
                            'formatted_address': 'Unknown',
                            'types': ['local_business']
                        })
                
                logger.info(f"Scraped {len(businesses)} businesses")
            
        except Exception as e:
            logger.error(f"Error scraping businesses: {e}")
        
        return businesses
    
    def _extract_business_reviews(self, place_id: str, days: int) -> List[Dict[str, Any]]:
        """Extract reviews for a specific business"""
        reviews = []
        start_date, end_date = self._calculate_date_range(days)
        
        try:
            if self.api_key and not place_id.startswith('scrape_'):
                # Use Google Places API
                reviews = self._extract_reviews_api(place_id, start_date, end_date)
            else:
                # Use web scraping
                reviews = self._extract_reviews_scrape(place_id, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error extracting reviews for place {place_id}: {e}")
        
        return reviews
    
    def _extract_reviews_api(self, place_id: str, start_date: datetime, 
                           end_date: datetime) -> List[Dict[str, Any]]:
        """Extract reviews using Google Places API"""
        reviews = []
        
        try:
            # First, get place details
            details_url = f"{self.base_url}/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,rating,user_ratings_total,review',
                'key': self.api_key,
                'language': 'fr'
            }
            
            response = requests.get(details_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    place_details = data.get('result', {})
                    
                    # Extract reviews
                    api_reviews = place_details.get('reviews', [])
                    
                    for review in api_reviews:
                        review_date = datetime.fromtimestamp(review['time'])
                        
                        # Check if review is within date range
                        if start_date <= review_date <= end_date:
                            processed_review = self._process_api_review(review, place_details)
                            if processed_review:
                                reviews.append(processed_review)
                                self.posts_extracted += 1
                    
                    logger.info(f"Extracted {len(reviews)} reviews via API for {place_details.get('name', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"Google Places API error: {e}")
        
        return reviews
    
    def _extract_reviews_scrape(self, place_id: str, start_date: datetime, 
                              end_date: datetime) -> List[Dict[str, Any]]:
        """Extract reviews using web scraping"""
        reviews = []
        
        try:
            # Construct Google Maps URL for the business
            # This is a simplified approach - real implementation would need
            # to handle the specific business URL
            maps_url = f"https://www.google.com/maps/place/{quote_plus(self.service)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(maps_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract review elements
                # Note: Google's HTML structure changes frequently
                review_elements = soup.find_all('div', {'data-review-id': True})
                
                for element in review_elements[:20]:  # Limit reviews per business
                    review = self._parse_review_element(element)
                    if review:
                        review_date = datetime.fromisoformat(review['created_at'].replace('Z', '+00:00'))
                        
                        if start_date <= review_date <= end_date:
                            reviews.append(review)
                            self.posts_extracted += 1
                
                logger.info(f"Scraped {len(reviews)} reviews for {self.service}")
            
        except Exception as e:
            logger.error(f"Error scraping reviews: {e}")
        
        return reviews
    
    def _process_api_review(self, review: Dict[str, Any], 
                          place_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process Google API review"""
        try:
            review_data = {
                'review_id': review.get('review_id', review.get('time', '')),
                'text': review.get('text', ''),
                'rating': review.get('rating', 0),
                'created_at': datetime.fromtimestamp(review['time']).isoformat(),
                'author_name': review.get('author_name', 'Anonymous'),
                'author_url': review.get('author_url', ''),
                'profile_photo_url': review.get('profile_photo_url', ''),
                'business_name': place_details.get('name', 'Unknown'),
                'business_rating': place_details.get('rating', 0),
                'total_reviews': place_details.get('user_ratings_total', 0),
                'type': 'google_review'
            }
            
            # Validate and clean
            validated_review = self._validate_and_clean_post(review_data)
            if validated_review:
                return self._normalize_post_structure(validated_review, 'google_reviews')
            
        except Exception as e:
            logger.error(f"Error processing Google API review: {e}")
            self.errors_count += 1
        
        return None
    
    def _parse_review_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse review element from scraped HTML"""
        try:
            # Extract review text
            text_element = element.find('span', class_='wiI7pd')
            text = text_element.get_text(strip=True) if text_element else ''
            
            if not text:
                return None
            
            # Extract rating
            rating_element = element.find('span', class_='kvMYJc')
            rating = 0
            if rating_element:
                # Count star elements
                stars = rating_element.find_all('img')
                rating = len([s for s in stars if 'star' in s.get('src', '')])
            
            # Extract author
            author_element = element.find('div', class_='d4r55')
            author_name = author_element.get_text(strip=True) if author_element else 'Anonymous'
            
            # Extract date
            date_element = element.find('span', class_='rsqaWe')
            date_text = date_element.get_text(strip=True) if date_element else ''
            review_date = self._parse_review_date(date_text)
            
            review_data = {
                'review_id': element.get('data-review-id', ''),
                'text': text,
                'rating': rating,
                'created_at': review_date.isoformat(),
                'author_name': author_name,
                'business_name': self.service,
                'type': 'google_review'
            }
            
            # Validate and clean
            validated_review = self._validate_and_clean_post(review_data)
            if validated_review:
                return self._normalize_post_structure(validated_review, 'google_reviews')
            
        except Exception as e:
            logger.error(f"Error parsing review element: {e}")
            self.errors_count += 1
        
        return None
    
    def _parse_review_date(self, date_text: str) -> datetime:
        """Parse review date from text"""
        try:
            # Handle relative dates like "il y a 2 jours", "2 weeks ago"
            if 'jour' in date_text.lower() or 'day' in date_text.lower():
                days = int(re.search(r'\d+', date_text).group() or 0)
                return datetime.now() - timedelta(days=days)
            elif 'semaine' in date_text.lower() or 'week' in date_text.lower():
                weeks = int(re.search(r'\d+', date_text).group() or 0)
                return datetime.now() - timedelta(weeks=weeks)
            elif 'mois' in date_text.lower() or 'month' in date_text.lower():
                months = int(re.search(r'\d+', date_text).group() or 0)
                return datetime.now() - timedelta(days=months * 30)
            else:
                # Try to parse as date
                return datetime.now() - timedelta(days=30)  # Default fallback
                
        except Exception:
            return datetime.now() - timedelta(days=30)
    
    def search_posts(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for Google reviews"""
        # For Google reviews, we search for businesses and get their reviews
        businesses = self._search_businesses(query)
        reviews = []
        
        for business in businesses[:3]:  # Limit to top 3 businesses
            business_reviews = self._extract_business_reviews(business['place_id'], 30)
            
            # Filter reviews containing the query
            for review in business_reviews:
                if query.lower() in review.get('text', '').lower():
                    reviews.append(review)
                
                if len(reviews) >= max_results:
                    break
            
            if len(reviews) >= max_results:
                break
        
        return reviews[:max_results]
    
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get Google review by ID"""
        # Google reviews don't have a simple ID-based retrieval
        # This would require knowing the business and then searching through reviews
        logger.warning("Google review retrieval by ID not implemented")
        return None