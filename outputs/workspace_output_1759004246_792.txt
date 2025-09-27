"""
Sentiment analysis module using multiple approaches.
Supports TextBlob, Transformers, and custom models.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer:
    """Multi-model sentiment analyzer"""
    
    def __init__(self, model_type: str = 'auto', language: str = 'auto'):
        self.model_type = model_type
        self.language = language
        self.models = {}
        self._setup_models()
    
    def _setup_models(self):
        """Setup sentiment analysis models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Setup multilingual transformer model
                self.models['transformers'] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                logger.info("Transformers sentiment model loaded")
            
            if TEXTBLOB_AVAILABLE:
                logger.info("TextBlob sentiment analysis available")
            
        except Exception as e:
            logger.error(f"Error setting up sentiment models: {e}")
    
    def analyze_sentiment(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        if not text or not isinstance(text, str):
            return self._get_neutral_result()
        
        try:
            lang = language or self.language or self._detect_language(text)
            
            # Choose analysis method
            if self.model_type == 'transformers' and TRANSFORMERS_AVAILABLE:
                result = self._analyze_with_transformers(text)
            elif lang == 'french' and TEXTBLOB_AVAILABLE:
                result = self._analyze_with_textblob_fr(text)
            else:
                result = self._analyze_with_textblob_en(text)
            
            # Add metadata
            result.update({
                'text': text[:100] + '...' if len(text) > 100 else text,
                'language': lang,
                'model_used': self.model_type
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._get_neutral_result()
    
    def analyze_batch(self, texts: List[str], language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        results = []
        
        for text in texts:
            result = self.analyze_sentiment(text, language)
            results.append(result)
        
        return results
    
    def _analyze_with_transformers(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Transformers"""
        try:
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            result = self.models['transformers'](text)[0]
            
            label = result['label'].lower()
            score = result['score']
            
            # Map to standard sentiment
            if 'positive' in label:
                sentiment = 'positive'
                polarity = score
            elif 'negative' in label:
                sentiment = 'negative'
                polarity = -score
            else:
                sentiment = 'neutral'
                polarity = 0
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'confidence': score,
                'raw_label': result['label'],
                'method': 'transformers'
            }
            
        except Exception as e:
            logger.error(f"Transformers analysis error: {e}")
            return self._analyze_with_textblob_en(text)  # Fallback
    
    def _analyze_with_textblob_en(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob (English)"""
        if not TEXTBLOB_AVAILABLE:
            return self._get_neutral_result()
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity),
                'method': 'textblob_en'
            }
            
        except Exception as e:
            logger.error(f"TextBlob English analysis error: {e}")
            return self._get_neutral_result()
    
    def _analyze_with_textblob_fr(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob (French)"""
        if not TEXTBLOB_AVAILABLE:
            return self._get_neutral_result()
        
        try:
            # TextBlob works with French text, though accuracy may vary
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Adjust thresholds for French (more conservative)
            if polarity > 0.2:
                sentiment = 'positive'
                confidence = polarity
            elif polarity < -0.2:
                sentiment = 'negative'
                confidence = abs(polarity)
            else:
                sentiment = 'neutral'
                confidence = 1.0 - abs(polarity)  # Higher confidence for neutral
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': confidence,
                'method': 'textblob_fr'
            }
            
        except Exception as e:
            logger.error(f"TextBlob French analysis error: {e}")
            return self._analyze_with_textblob_en(text)  # Fallback to English
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for sentiment analysis"""
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
    
    def _get_neutral_result(self) -> Dict[str, Any]:
        """Return neutral sentiment result"""
        return {
            'sentiment': 'neutral',
            'polarity': 0.0,
            'subjectivity': 0.0,
            'confidence': 0.0,
            'method': 'fallback',
            'error': 'Analysis failed'
        }
    
    def get_sentiment_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics for sentiment analysis results"""
        if not results:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'percentages': {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                },
                'average_polarity': 0.0,
                'average_confidence': 0.0
            }
        
        total = len(results)
        positive = sum(1 for r in results if r['sentiment'] == 'positive')
        negative = sum(1 for r in results if r['sentiment'] == 'negative')
        neutral = sum(1 for r in results if r['sentiment'] == 'neutral')
        
        avg_polarity = np.mean([r['polarity'] for r in results])
        avg_confidence = np.mean([r.get('confidence', 0) for r in results])
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'percentages': {
                'positive': round(positive / total * 100, 2),
                'negative': round(negative / total * 100, 2),
                'neutral': round(neutral / total * 100, 2)
            },
            'average_polarity': round(avg_polarity, 3),
            'average_confidence': round(avg_confidence, 3)
        }

class SentimentTrendAnalyzer:
    """Analyze sentiment trends over time"""
    
    def __init__(self, analyzer: SentimentAnalyzer):
        self.analyzer = analyzer
    
    def analyze_temporal_trends(self, texts: List[str], dates: List[str]) -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        if len(texts) != len(dates):
            raise ValueError("Texts and dates lists must have the same length")
        
        # Combine and sort by date
        dated_texts = list(zip(dates, texts))
        dated_texts.sort(key=lambda x: x[0])
        
        # Analyze sentiment for each text
        results = []
        for date, text in dated_texts:
            sentiment_result = self.analyzer.analyze_sentiment(text)
            sentiment_result['date'] = date
            results.append(sentiment_result)
        
        # Group by date intervals
        trends = self._group_by_date_intervals(results)
        
        return {
            'detailed_results': results,
            'trends_by_interval': trends,
            'overall_trend': self._calculate_overall_trend(results)
        }
    
    def _group_by_date_intervals(self, results: List[Dict[str, Any]], 
                                interval_days: int = 7) -> Dict[str, Any]:
        """Group sentiment results by date intervals"""
        from datetime import datetime, timedelta
        
        if not results:
            return {}
        
        # Parse dates
        dated_results = []
        for result in results:
            try:
                date = datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
                dated_results.append((date, result))
            except Exception:
                continue
        
        if not dated_results:
            return {}
        
        # Sort by date
        dated_results.sort(key=lambda x: x[0])
        
        # Group by intervals
        start_date = dated_results[0][0]
        end_date = dated_results[-1][0]
        
        intervals = {}
        current_date = start_date
        
        while current_date <= end_date:
            interval_end = current_date + timedelta(days=interval_days)
            interval_key = current_date.strftime("%Y-%m-%d")
            
            interval_results = [
                result for date, result in dated_results
                if current_date <= date < interval_end
            ]
            
            if interval_results:
                interval_summary = self.analyzer.get_sentiment_summary(interval_results)
                intervals[interval_key] = interval_summary
            
            current_date = interval_end
        
        return intervals
    
    def _calculate_overall_trend(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall sentiment trend"""
        if not results:
            return {'direction': 'stable', 'strength': 0}
        
        # Calculate trend based on polarity changes
        polarities = [r['polarity'] for r in results]
        
        if len(polarities) < 2:
            return {'direction': 'stable', 'strength': 0}
        
        # Simple linear trend
        x = list(range(len(polarities)))
        y = polarities
        
        # Calculate correlation coefficient
        correlation = np.corrcoef(x, y)[0, 1]
        
        if correlation > 0.3:
            direction = 'improving'
        elif correlation < -0.3:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'strength': abs(correlation),
            'correlation': correlation
        }