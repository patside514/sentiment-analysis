"""
Data validation utilities for the social media sentiment analysis application.
Provides validation for inputs, API responses, and processed data.
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

from ..config import AnalysisConfig, AVAILABLE_SOURCES

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_service_name(service: str) -> bool:
        """Validate service name parameter"""
        if not service or not isinstance(service, str):
            return False
        
        # Basic validation - allow alphanumeric, spaces, and common punctuation
        pattern = r'^[a-zA-Z0-9\s\-_.,&\'()]+$'
        return bool(re.match(pattern, service)) and len(service) <= 100
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """Validate data source"""
        return source.lower() in AVAILABLE_SOURCES
    
    @staticmethod
    def validate_days(days: int) -> bool:
        """Validate days parameter"""
        return (isinstance(days, int) and 
                1 <= days <= 365 and 
                days <= AnalysisConfig.DEFAULT_DAYS * 2)  # Max 60 days
    
    @staticmethod
    def validate_max_posts(max_posts: int) -> bool:
        """Validate max posts parameter"""
        return (isinstance(max_posts, int) and 
                AnalysisConfig.MIN_POSTS <= max_posts <= AnalysisConfig.MAX_POSTS)
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range"""
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            return False
        
        if start_date > end_date:
            return False
        
        # Check if range is not too large
        delta = end_date - start_date
        return delta.days <= AnalysisConfig.DEFAULT_DAYS * 2
    
    @staticmethod
    def validate_text_content(text: str) -> bool:
        """Validate text content"""
        if not text or not isinstance(text, str):
            return False
        
        # Check minimum length
        if len(text.strip()) < 10:
            return False
        
        # Check for excessive length
        if len(text) > 5000:
            return False
        
        # Basic content validation
        return not text.isspace()
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_tweet_data(tweet_data: Dict[str, Any]) -> bool:
        """Validate tweet data structure"""
        required_fields = ['id', 'text', 'created_at']
        
        if not isinstance(tweet_data, dict):
            return False
        
        # Check required fields
        for field in required_fields:
            if field not in tweet_data:
                return False
        
        # Validate text content
        if not DataValidator.validate_text_content(tweet_data.get('text', '')):
            return False
        
        # Validate date format
        try:
            datetime.fromisoformat(tweet_data['created_at'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return False
        
        return True
    
    @staticmethod
    def validate_facebook_post(post_data: Dict[str, Any]) -> bool:
        """Validate Facebook post data"""
        required_fields = ['id', 'message', 'created_time']
        
        if not isinstance(post_data, dict):
            return False
        
        for field in required_fields:
            if field not in post_data:
                return False
        
        # Validate message content
        if not DataValidator.validate_text_content(post_data.get('message', '')):
            return False
        
        return True
    
    @staticmethod
    def validate_google_review(review_data: Dict[str, Any]) -> bool:
        """Validate Google review data"""
        required_fields = ['review_id', 'text', 'rating', 'time']
        
        if not isinstance(review_data, dict):
            return False
        
        for field in required_fields:
            if field not in review_data:
                return False
        
        # Validate rating
        rating = review_data.get('rating')
        if not isinstance(rating, (int, float)) or not 1 <= rating <= 5:
            return False
        
        # Validate text content
        if not DataValidator.validate_text_content(review_data.get('text', '')):
            return False
        
        return True
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Basic text cleaning"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s@#.,!?\-\'"]', '', text)
        
        return text.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        if not filename:
            return "unnamed"
        
        # Remove or replace unsafe characters
        filename = re.sub(r'[<>:&quot;/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('._-')
        
        # Limit length
        return filename[:50] or "unnamed"

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_cli_args(service: str, source: str, days: int, max_posts: int) -> Dict[str, Any]:
    """Validate all CLI arguments"""
    errors = []
    
    # Validate service name
    if not DataValidator.validate_service_name(service):
        errors.append("Invalid service name. Use alphanumeric characters, spaces, and basic punctuation.")
    
    # Validate source
    if not DataValidator.validate_source(source):
        errors.append(f"Invalid source. Available sources: {', '.join(AVAILABLE_SOURCES)}")
    
    # Validate days
    if not DataValidator.validate_days(days):
        errors.append("Invalid days parameter. Must be between 1 and 60.")
    
    # Validate max posts
    if not DataValidator.validate_max_posts(max_posts):
        errors.append(f"Invalid max posts. Must be between {AnalysisConfig.MIN_POSTS} and {AnalysisConfig.MAX_POSTS}.")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'cleaned': {
            'service': DataValidator.clean_text(service),
            'source': source.lower(),
            'days': days,
            'max_posts': max_posts
        }
    }