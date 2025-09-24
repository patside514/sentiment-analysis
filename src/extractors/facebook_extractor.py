"""
Facebook data extractor using Facebook Graph API.
Handles page posts and comments extraction.
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import requests

from tqdm import tqdm

from .base_extractor import BaseExtractor, ExtractionError, RateLimitError, AuthenticationError
from ..config import APIConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class FacebookExtractor(BaseExtractor):
    """Facebook data extractor"""
    
    def __init__(self, service: str, max_posts: int = 500):
        super().__init__(service, max_posts)
        self.access_token = APIConfig.FACEBOOK_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v18.0"
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate Facebook API credentials"""
        if not self.access_token:
            raise AuthenticationError("Facebook access token not configured")
        
        try:
            # Test API connection
            test_url = f"{self.base_url}/me"
            params = {'access_token': self.access_token}
            response = requests.get(test_url, params=params)
            
            if response.status_code != 200:
                raise AuthenticationError(f"Facebook API authentication failed: {response.text}")
            
            logger.info("Facebook API authentication successful")
            
        except Exception as e:
            logger.error(f"Facebook API validation failed: {e}")
            raise AuthenticationError(f"Facebook API validation failed: {e}")
    
    def extract_posts(self, days: int = 30, **kwargs) -> List[Dict[str, Any]]:
        """Extract Facebook posts"""
        logger.info(f"Extracting Facebook posts for '{self.service}' from last {days} days")
        
        try:
            # Search for pages related to the service
            pages = self._search_pages(self.service)
            
            if not pages:
                logger.warning(f"No Facebook pages found for service: {self.service}")
                return []
            
            all_posts = []
            for page in pages[:5]:  # Limit to top 5 pages
                page_posts = self._extract_page_posts(page['id'], days)
                all_posts.extend(page_posts)
                
                if len(all_posts) >= self.max_posts:
                    break
            
            # Limit to max_posts
            posts = all_posts[:self.max_posts]
            self.posts_extracted = len(posts)
            
            logger.info(f"Extracted {len(posts)} Facebook posts")
            return posts
            
        except Exception as e:
            self._handle_extraction_error(e, "Facebook extraction")
            return []
    
    def _search_pages(self, query: str) -> List[Dict[str, Any]]:
        """Search Facebook pages"""
        pages = []
        
        try:
            search_url = f"{self.base_url}/search"
            params = {
                'q': query,
                'type': 'page',
                'fields': 'id,name,username,link,fan_count,rating_count',
                'access_token': self.access_token,
                'limit': 10
            }
            
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('data', [])
                
                # Sort by fan count (popularity)
                pages.sort(key=lambda x: x.get('fan_count', 0), reverse=True)
                
                logger.info(f"Found {len(pages)} Facebook pages for query: {query}")
            else:
                logger.error(f"Facebook search error: {response.text}")
                
        except Exception as e:
            logger.error(f"Error searching Facebook pages: {e}")
        
        return pages
    
    def _extract_page_posts(self, page_id: str, days: int) -> List[Dict[str, Any]]:
        """Extract posts from a Facebook page"""
        posts = []
        start_date, end_date = self._calculate_date_range(days)
        
        try:
            posts_url = f"{self.base_url}/{page_id}/posts"
            params = {
                'fields': 'id,message,created_time,likes.summary(true),'
                         'comments.summary(true),shares,permalink_url,'
                         'reactions.summary(true)',
                'access_token': self.access_token,
                'limit': 100,
                'since': start_date.isoformat(),
                'until': end_date.isoformat()
            }
            
            while len(posts) < self.max_posts:
                response = requests.get(posts_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Facebook API error: {response.text}")
                    break
                
                data = response.json()
                page_posts = data.get('data', [])
                
                if not page_posts:
                    break
                
                for post in page_posts:
                    processed_post = self._process_page_post(post)
                    if processed_post:
                        posts.append(processed_post)
                        self.posts_extracted += 1
                    
                    if len(posts) >= self.max_posts:
                        break
                
                # Check for next page
                paging = data.get('paging', {})
                if 'next' in paging:
                    posts_url = paging['next']
                    params = {}  # URL already contains params
                else:
                    break
                
                # Rate limiting
                self._rate_limit_delay(1.0)
                
        except Exception as e:
            logger.error(f"Error extracting page posts: {e}")
        
        return posts
    
    def _process_page_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process Facebook page post"""
        try:
            # Extract metrics
            likes = post.get('likes', {}).get('summary', {}).get('total_count', 0)
            comments = post.get('comments', {}).get('summary', {}).get('total_count', 0)
            shares = post.get('shares', {}).get('count', 0) if post.get('shares') else 0
            reactions = post.get('reactions', {}).get('summary', {}).get('total_count', 0)
            
            post_data = {
                'id': post['id'],
                'text': post.get('message', ''),
                'created_at': post['created_time'],
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'reactions': reactions,
                'permalink_url': post.get('permalink_url', ''),
                'type': 'page_post'
            }
            
            # Validate and clean
            validated_post = self._validate_and_clean_post(post_data)
            if validated_post:
                return self._normalize_post_structure(validated_post, 'facebook')
            
        except Exception as e:
            logger.error(f"Error processing Facebook post: {e}")
            self.errors_count += 1
        
        return None
    
    def extract_page_reviews(self, page_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Extract reviews from a Facebook page"""
        reviews = []
        start_date, end_date = self._calculate_date_range(days)
        
        try:
            reviews_url = f"{self.base_url}/{page_id}/ratings"
            params = {
                'fields': 'review_text,rating,created_time,reviewer',
                'access_token': self.access_token,
                'limit': 100
            }
            
            response = requests.get(reviews_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                page_reviews = data.get('data', [])
                
                for review in page_reviews:
                    processed_review = self._process_review(review)
                    if processed_review:
                        # Check if review is within date range
                        review_date = datetime.fromisoformat(
                            processed_review['created_at'].replace('Z', '+00:00')
                        )
                        
                        if start_date <= review_date <= end_date:
                            reviews.append(processed_review)
                            self.posts_extracted += 1
                
                logger.info(f"Extracted {len(reviews)} reviews from page {page_id}")
            
        except Exception as e:
            logger.error(f"Error extracting page reviews: {e}")
        
        return reviews
    
    def _process_review(self, review: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process Facebook review"""
        try:
            review_data = {
                'id': review['id'],
                'text': review.get('review_text', ''),
                'created_at': review['created_time'],
                'rating': review.get('rating', 0),
                'reviewer': review.get('reviewer', {}),
                'type': 'review'
            }
            
            # Validate and clean
            validated_review = self._validate_and_clean_post(review_data)
            if validated_review:
                return self._normalize_post_structure(validated_review, 'facebook')
            
        except Exception as e:
            logger.error(f"Error processing Facebook review: {e}")
            self.errors_count += 1
        
        return None
    
    def search_posts(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for Facebook posts"""
        posts = []
        
        try:
            # Search for pages first
            pages = self._search_pages(query)
            
            for page in pages[:3]:  # Limit to top 3 pages
                page_posts = self._extract_page_posts(page['id'], 30)  # Last 30 days
                
                # Filter posts containing the query
                for post in page_posts:
                    if query.lower() in post.get('text', '').lower():
                        posts.append(post)
                    
                    if len(posts) >= max_results:
                        break
                
                if len(posts) >= max_results:
                    break
            
        except Exception as e:
            logger.error(f"Facebook search error: {e}")
            self._handle_extraction_error(e, "Facebook search")
        
        return posts[:max_results]
    
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get Facebook post by ID"""
        try:
            post_url = f"{self.base_url}/{post_id}"
            params = {
                'fields': 'id,message,created_time,likes.summary(true),'
                         'comments.summary(true),shares,permalink_url',
                'access_token': self.access_token
            }
            
            response = requests.get(post_url, params=params)
            
            if response.status_code == 200:
                post = response.json()
                return self._process_page_post(post)
            
        except Exception as e:
            logger.error(f"Error getting Facebook post {post_id}: {e}")
            self._handle_extraction_error(e, f"Get Facebook post {post_id}")
        
        return None