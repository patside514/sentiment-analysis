"""
Base extractor class for social media data extraction.
Provides common functionality and interface for all extractors.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Iterator
import time

from ..utils.logger import get_logger
from ..utils.data_validator import DataValidator
from ..config import APIConfig, AnalysisConfig

logger = get_logger(__name__)

class BaseExtractor(ABC):
    """Abstract base class for social media extractors"""
    
    def __init__(self, service: str, max_posts: int = 500):
        self.service = service
        self.max_posts = max_posts
        self.validator = DataValidator()
        self.posts_extracted = 0
        self.errors_count = 0
        
    @abstractmethod
    def extract_posts(self, days: int = 30, **kwargs) -> List[Dict[str, Any]]:
        """Extract posts from the social media platform"""
        pass
    
    @abstractmethod
    def search_posts(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for specific posts"""
        pass
    
    @abstractmethod
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific post by ID"""
        pass
    
    def _calculate_date_range(self, days: int) -> tuple:
        """Calculate start and end dates for extraction"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    def _rate_limit_delay(self, delay_seconds: float = 1.0):
        """Implement rate limiting delay"""
        time.sleep(delay_seconds)
    
    def _validate_and_clean_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean a post before returning"""
        try:
            # Basic validation
            if not post or not isinstance(post, dict):
                return None
            
            # Extract text content
            text = (post.get('text') or 
                   post.get('message') or 
                   post.get('content', ''))
            
            if not self.validator.validate_text_content(text):
                return None
            
            # Clean text
            post['cleaned_text'] = self.validator.clean_text(text)
            
            # Ensure required fields
            required_fields = ['id', 'created_at', 'text']
            for field in required_fields:
                if field not in post or not post[field]:
                    return None
            
            return post
            
        except Exception as e:
            logger.error(f"Error validating post: {e}")
            self.errors_count += 1
            return None
    
    def _normalize_post_structure(self, post: Dict[str, Any], 
                                 source: str) -> Dict[str, Any]:
        """Normalize post structure across different platforms"""
        normalized = {
            'id': str(post.get('id', '')),
            'source': source,
            'service': self.service,
            'text': post.get('text', post.get('message', post.get('content', ''))),
            'cleaned_text': post.get('cleaned_text', ''),
            'created_at': post.get('created_at', post.get('created_time', datetime.now().isoformat())),
            'author': post.get('author', post.get('user', post.get('from', {}))),
            'likes': post.get('likes', post.get('reactions', {}).get('like', 0)),
            'shares': post.get('shares', post.get('retweets', 0)),
            'comments': post.get('comments', 0),
            'url': post.get('url', post.get('permalink_url', '')),
            'metadata': {
                'raw_data': post,
                'extraction_date': datetime.now().isoformat(),
                'source_platform': source
            }
        }
        
        return normalized
    
    def _handle_extraction_error(self, error: Exception, context: str):
        """Handle and log extraction errors"""
        logger.error(f"Extraction error in {context}: {str(error)}")
        self.errors_count += 1
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            'service': self.service,
            'posts_extracted': self.posts_extracted,
            'errors_count': self.errors_count,
            'success_rate': (self.posts_extracted / (self.posts_extracted + self.errors_count) * 100) 
                           if (self.posts_extracted + self.errors_count) > 0 else 0
        }

class ExtractionError(Exception):
    """Custom exception for extraction errors"""
    pass

class RateLimitError(Exception):
    """Custom exception for rate limit errors"""
    pass

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass