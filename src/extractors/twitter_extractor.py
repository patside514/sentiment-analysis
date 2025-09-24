"""
Twitter data extractor using Tweepy and snscrape as fallback.
Handles Twitter API v2 and legacy API access.
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time

import pandas as pd
from tqdm import tqdm

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

try:
    import snscrape.modules.twitter as sntwitter
    SN_SCRAPE_AVAILABLE = True
except ImportError:
    SN_SCRAPE_AVAILABLE = False

from .base_extractor import BaseExtractor, ExtractionError, RateLimitError, AuthenticationError
from ..config import APIConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TwitterExtractor(BaseExtractor):
    """Twitter data extractor"""
    
    def __init__(self, service: str, max_posts: int = 500):
        super().__init__(service, max_posts)
        self.api = None
        self.client = None
        self._setup_api()
    
    def _setup_api(self):
        """Setup Twitter API connections"""
        try:
            if TWEEPY_AVAILABLE and APIConfig.TWITTER_BEARER_TOKEN:
                # Twitter API v2
                self.client = tweepy.Client(
                    bearer_token=APIConfig.TWITTER_BEARER_TOKEN,
                    wait_on_rate_limit=True
                )
                
                # Legacy API for additional functionality
                if (APIConfig.TWITTER_API_KEY and 
                    APIConfig.TWITTER_API_SECRET and
                    APIConfig.TWITTER_ACCESS_TOKEN and
                    APIConfig.TWITTER_ACCESS_TOKEN_SECRET):
                    
                    auth = tweepy.OAuthHandler(
                        APIConfig.TWITTER_API_KEY,
                        APIConfig.TWITTER_API_SECRET
                    )
                    auth.set_access_token(
                        APIConfig.TWITTER_ACCESS_TOKEN,
                        APIConfig.TWITTER_ACCESS_TOKEN_SECRET
                    )
                    self.api = tweepy.API(auth, wait_on_rate_limit=True)
                
                logger.info("Twitter API setup successful")
            else:
                logger.warning("Twitter API credentials not available, will use snscrape")
                
        except Exception as e:
            logger.error(f"Twitter API setup failed: {e}")
            raise AuthenticationError(f"Twitter API authentication failed: {e}")
    
    def extract_posts(self, days: int = 30, **kwargs) -> List[Dict[str, Any]]:
        """Extract tweets using API or snscrape"""
        logger.info(f"Extracting Twitter posts for '{self.service}' from last {days} days")
        
        try:
            if self.client:
                return self._extract_with_api(days, **kwargs)
            elif SN_SCRAPE_AVAILABLE:
                return self._extract_with_snscrape(days, **kwargs)
            else:
                raise ExtractionError("No Twitter extraction method available")
                
        except Exception as e:
            self._handle_extraction_error(e, "Twitter extraction")
            return []
    
    def _extract_with_api(self, days: int, **kwargs) -> List[Dict[str, Any]]:
        """Extract tweets using Twitter API v2"""
        posts = []
        start_date, end_date = self._calculate_date_range(days)
        
        try:
            # Build query
            query = self._build_search_query()
            
            # Search recent tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=100,  # Max per request
                start_time=start_date.isoformat() + 'Z',
                end_time=end_date.isoformat() + 'Z',
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
                user_fields=['username', 'name'],
                expansions=['author_id']
            )
            
            # Process tweets
            for tweet_batch in tweets:
                if len(posts) >= self.max_posts:
                    break
                
                for tweet in tweet_batch.data:
                    if len(posts) >= self.max_posts:
                        break
                    
                    processed_tweet = self._process_tweet(tweet)
                    if processed_tweet:
                        posts.append(processed_tweet)
                        self.posts_extracted += 1
                
                # Rate limiting
                self._rate_limit_delay(0.5)
                
        except tweepy.TooManyRequests as e:
            logger.warning(f"Twitter rate limit reached: {e}")
            raise RateLimitError("Twitter rate limit exceeded")
        except Exception as e:
            logger.error(f"Twitter API error: {e}")
            raise ExtractionError(f"Twitter API error: {e}")
        
        logger.info(f"Extracted {len(posts)} tweets via API")
        return posts
    
    def _extract_with_snscrape(self, days: int, **kwargs) -> List[Dict[str, Any]]:
        """Extract tweets using snscrape as fallback"""
        posts = []
        start_date, end_date = self._calculate_date_range(days)
        
        try:
            query = self._build_search_query()
            
            # Build snscrape query with date range
            since_date = start_date.strftime("%Y-%m-%d")
            until_date = end_date.strftime("%Y-%m-%d")
            snscrape_query = f"{query} since:{since_date} until:{until_date}"
            
            logger.info(f"Using snscrape with query: {snscrape_query}")
            
            # Search tweets
            for i, tweet in enumerate(
                sntwitter.TwitterSearchScraper(snscrape_query).get_items()
            ):
                if len(posts) >= self.max_posts:
                    break
                
                processed_tweet = self._process_snscrape_tweet(tweet)
                if processed_tweet:
                    posts.append(processed_tweet)
                    self.posts_extracted += 1
                
                # Progress tracking
                if i % 50 == 0:
                    logger.info(f"Processed {i} tweets, extracted {len(posts)}")
            
        except Exception as e:
            logger.error(f"snscrape error: {e}")
            raise ExtractionError(f"snscrape extraction failed: {e}")
        
        logger.info(f"Extracted {len(posts)} tweets via snscrape")
        return posts
    
    def _build_search_query(self) -> str:
        """Build Twitter search query"""
        service_terms = self.service.lower().split()
        
        # Create query with service name and variations
        query_parts = []
        for term in service_terms:
            query_parts.append(term)
            query_parts.append(f"#{term}")
            query_parts.append(f"@{term}")
        
        # Add language filter (optional)
        query = " OR ".join(query_parts)
        
        # Exclude retweets for original content
        query += " -is:retweet"
        
        return query
    
    def _process_tweet(self, tweet) -> Optional[Dict[str, Any]]:
        """Process Twitter API tweet object"""
        try:
            tweet_data = {
                'id': str(tweet.id),
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat(),
                'author_id': str(tweet.author_id),
                'lang': getattr(tweet, 'lang', 'unknown'),
                'likes': tweet.public_metrics.get('like_count', 0),
                'retweets': tweet.public_metrics.get('retweet_count', 0),
                'replies': tweet.public_metrics.get('reply_count', 0),
                'quotes': tweet.public_metrics.get('quote_count', 0)
            }
            
            # Validate and clean
            validated_tweet = self._validate_and_clean_post(tweet_data)
            if validated_tweet:
                return self._normalize_post_structure(validated_tweet, 'twitter')
            
        except Exception as e:
            logger.error(f"Error processing tweet {getattr(tweet, 'id', 'unknown')}: {e}")
            self.errors_count += 1
        
        return None
    
    def _process_snscrape_tweet(self, tweet) -> Optional[Dict[str, Any]]:
        """Process snscrape tweet object"""
        try:
            tweet_data = {
                'id': str(tweet.id),
                'text': tweet.content,
                'created_at': tweet.date.isoformat(),
                'username': tweet.user.username,
                'display_name': tweet.user.displayname,
                'likes': tweet.likeCount,
                'retweets': tweet.retweetCount,
                'replies': tweet.replyCount,
                'quotes': tweet.quoteCount,
                'lang': getattr(tweet, 'lang', 'unknown')
            }
            
            # Validate and clean
            validated_tweet = self._validate_and_clean_post(tweet_data)
            if validated_tweet:
                return self._normalize_post_structure(validated_tweet, 'twitter')
            
        except Exception as e:
            logger.error(f"Error processing snscrape tweet: {e}")
            self.errors_count += 1
        
        return None
    
    def search_posts(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for specific tweets"""
        posts = []
        
        try:
            if self.client:
                tweets = self.client.search_recent_tweets(
                    query=query,
                    max_results=min(max_results, 100),
                    tweet_fields=['created_at', 'author_id', 'public_metrics']
                )
                
                for tweet in tweets.data:
                    processed_tweet = self._process_tweet(tweet)
                    if processed_tweet:
                        posts.append(processed_tweet)
                        self.posts_extracted += 1
            
            elif SN_SCRAPE_AVAILABLE:
                # Use snscrape for search
                for i, tweet in enumerate(
                    sntwitter.TwitterSearchScraper(query).get_items()
                ):
                    if len(posts) >= max_results:
                        break
                    
                    processed_tweet = self._process_snscrape_tweet(tweet)
                    if processed_tweet:
                        posts.append(processed_tweet)
                        self.posts_extracted += 1
            
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            self._handle_extraction_error(e, "Twitter search")
        
        return posts
    
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get tweet by ID"""
        try:
            if self.client:
                tweet = self.client.get_tweet(
                    post_id,
                    tweet_fields=['created_at', 'author_id', 'public_metrics']
                )
                
                if tweet.data:
                    return self._process_tweet(tweet.data)
            
            elif SN_SCRAPE_AVAILABLE:
                # Use snscrape to get tweet by ID
                for tweet in sntwitter.TwitterTweetScraper(post_id).get_items():
                    return self._process_snscrape_tweet(tweet)
            
        except Exception as e:
            logger.error(f"Error getting tweet {post_id}: {e}")
            self._handle_extraction_error(e, f"Get tweet {post_id}")
        
        return None