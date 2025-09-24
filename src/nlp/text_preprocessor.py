"""
Text preprocessing utilities for NLP analysis.
Handles cleaning, normalization, and language detection.
"""
import re
import string
from typing import List, Dict, Any, Optional
import unicodedata

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception as e:
    logger.warning(f"Could not download NLTK data: {e}")

class TextPreprocessor:
    """Text preprocessing utilities"""
    
    def __init__(self, language: str = 'auto'):
        self.language = language
        self.stop_words = {}
        self.stemmers = {}
        self._load_language_resources()
    
    def _load_language_resources(self):
        """Load language-specific resources"""
        languages = ['french', 'english']
        
        for lang in languages:
            try:
                # Load stopwords
                self.stop_words[lang] = set(stopwords.words(lang))
                
                # Load stemmer
                lang_code = 'french' if lang == 'french' else 'english'
                self.stemmers[lang] = SnowballStemmer(lang_code)
                
            except Exception as e:
                logger.warning(f"Could not load resources for {lang}: {e}")
    
    def preprocess_text(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Complete text preprocessing pipeline"""
        if not text or not isinstance(text, str):
            return {
                'original': text or '',
                'cleaned': '',
                'tokens': [],
                'language': language or self.language,
                'preprocessing_steps': []
            }
        
        result = {
            'original': text,
            'cleaned': '',
            'tokens': [],
            'language': language or self.language,
            'preprocessing_steps': []
        }
        
        try:
            # Step 1: Basic cleaning
            cleaned = self._basic_cleaning(text)
            result['preprocessing_steps'].append('basic_cleaning')
            
            # Step 2: Language detection (if auto)
            if result['language'] == 'auto':
                result['language'] = self._detect_language(cleaned)
                result['preprocessing_steps'].append('language_detection')
            
            # Step 3: Advanced cleaning
            cleaned = self._advanced_cleaning(cleaned, result['language'])
            result['preprocessing_steps'].append('advanced_cleaning')
            
            # Step 4: Tokenization
            tokens = self._tokenize(cleaned, result['language'])
            result['preprocessing_steps'].append('tokenization')
            
            # Step 5: Remove stopwords
            tokens = self._remove_stopwords(tokens, result['language'])
            result['preprocessing_steps'].append('stopword_removal')
            
            # Step 6: Stemming (optional)
            tokens = self._stem_tokens(tokens, result['language'])
            result['preprocessing_steps'].append('stemming')
            
            result['cleaned'] = cleaned
            result['tokens'] = tokens
            
        except Exception as e:
            logger.error(f"Error in text preprocessing: {e}")
            result['cleaned'] = text
            result['tokens'] = text.split()
        
        return result
    
    def _basic_cleaning(self, text: str) -> str:
        """Basic text cleaning"""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'[\+\(]?[0-9][0-9\s\-()\.]{7,}[0-9]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s@#.,!?\-\'"]', '', text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        return text.strip().lower()
    
    def _advanced_cleaning(self, text: str, language: str) -> str:
        """Advanced text cleaning based on language"""
        # Remove extra punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove numbers (optional, can be configured)
        text = re.sub(r'\d+', '', text)
        
        # Remove single characters
        text = re.sub(r'\b\w\b', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Language-specific cleaning
        if language == 'french':
            text = self._french_cleaning(text)
        elif language == 'english':
            text = self._english_cleaning(text)
        
        return text.strip()
    
    def _french_cleaning(self, text: str) -> str:
        """French-specific text cleaning"""
        # Remove common French contractions
        contractions = {
            "j'": "je ", "l'": "le ", "d'": "de ", "c'": "ce ",
            "n'": "ne ", "s'": "se ", "t'": "te ", "qu'": "que ",
            "m'": "me ", "v'": "vous "
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    def _english_cleaning(self, text: str) -> str:
        """English-specific text cleaning"""
        # Remove common English contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will",
            "'d": " would", "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    def _tokenize(self, text: str, language: str) -> List[str]:
        """Tokenize text"""
        try:
            # Use NLTK tokenizer
            tokens = word_tokenize(text, language='french' if language == 'french' else 'english')
            
            # Filter tokens
            tokens = [token for token in tokens if len(token) > 2]
            tokens = [token for token in tokens if token.isalpha()]
            
            return tokens
            
        except Exception as e:
            logger.error(f"Tokenization error: {e}")
            return text.split()
    
    def _remove_stopwords(self, tokens: List[str], language: str) -> List[str]:
        """Remove stopwords"""
        stopwords_set = self.stop_words.get(language, set())
        
        if not stopwords_set and SPACY_AVAILABLE:
            # Fallback to spaCy stopwords
            try:
                nlp = spacy.load('fr_core_news_sm' if language == 'french' else 'en_core_web_sm')
                stopwords_set = nlp.Defaults.stop_words
            except Exception:
                pass
        
        return [token for token in tokens if token.lower() not in stopwords_set]
    
    def _stem_tokens(self, tokens: List[str], language: str) -> List[str]:
        """Apply stemming to tokens"""
        stemmer = self.stemmers.get(language)
        
        if stemmer:
            return [stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Simple heuristic based on common words
        french_words = ['le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'est', 'sont']
        english_words = ['the', 'and', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of']
        
        text_lower = text.lower()
        
        french_score = sum(1 for word in french_words if word in text_lower)
        english_score = sum(1 for word in english_words if word in text_lower)
        
        if french_score > english_score:
            return 'french'
        else:
            return 'english'
    
    def clean_for_sentiment(self, text: str) -> str:
        """Clean text specifically for sentiment analysis"""
        if not text or not isinstance(text, str):
            return ""
        
        # Preserve emoticons and basic punctuation for sentiment
        text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s@#.,!?\-\'"():;]', '', text)  # Keep sentiment punctuation
        
        return text.strip()
    
    def extract_mentions_hashtags(self, text: str) -> Dict[str, List[str]]:
        """Extract mentions and hashtags"""
        mentions = re.findall(r'@\w+', text)
        hashtags = re.findall(r'#\w+', text)
        
        return {
            'mentions': mentions,
            'hashtags': hashtags
        }