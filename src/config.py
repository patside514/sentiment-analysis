"""
Configuration module for the social media sentiment analysis application.
Handles API keys, default parameters, and environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CONFIG_DIR = BASE_DIR / "config"

# API Configuration
class APIConfig:
    """API keys and configuration"""
    # Twitter API
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Facebook API
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    
    # Google API
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Rate limiting
    TWITTER_RATE_LIMIT = 300  # requests per 15 minutes
    FACEBOOK_RATE_LIMIT = 200  # requests per hour
    GOOGLE_RATE_LIMIT = 100  # requests per day

# NLP Configuration
class NLPConfig:
    """NLP processing configuration"""
    SENTIMENT_MODELS = {
        'fr': 'textblob_fr',
        'en': 'textblob_en',
        'multilingual': 'transformers'
    }
    
    DEFAULT_LANGUAGE = 'auto'
    MIN_TEXT_LENGTH = 10
    MAX_TEXT_LENGTH = 1000
    
    # Keyword extraction
    MIN_KEYWORD_FREQUENCY = 2
    MAX_KEYWORDS = 50
    STOP_WORDS_LANG = ['french', 'english']

# Analysis Configuration
class AnalysisConfig:
    """Analysis parameters"""
    DEFAULT_DAYS = 30
    MAX_POSTS = 500
    MIN_POSTS = 50
    
    # Sentiment thresholds
    POSITIVE_THRESHOLD = 0.1
    NEGATIVE_THRESHOLD = -0.1
    
    # Time intervals for trend analysis
    TREND_INTERVALS = ['1D', '7D', '30D']

# Visualization Configuration
class VizConfig:
    """Visualization settings"""
    PLOT_STYLE = 'seaborn-v0_8'
    FIGURE_SIZE = (12, 8)
    COLOR_PALETTE = 'Set3'
    
    # Word cloud settings
    WC_WIDTH = 800
    WC_HEIGHT = 400
    WC_MAX_WORDS = 100
    WC_COLLOCATIONS = False

# Logging Configuration
class LoggingConfig:
    """Logging configuration"""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = OUTPUTS_DIR / 'app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

# Export settings
CSV_SETTINGS = {
    'encoding': 'utf-8-sig',
    'index': False,
    'quoting': 1  # QUOTE_ALL
}

# Available sources
AVAILABLE_SOURCES = ['twitter', 'facebook', 'google_reviews']
DEFAULT_SOURCE = 'twitter'