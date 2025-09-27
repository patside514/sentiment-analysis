"""
Main orchestration module for the social media sentiment analysis application.
Coordinates all components and manages the analysis workflow.
"""
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

from .config import AnalysisConfig, AVAILABLE_SOURCES
from .extractors.base_extractor import BaseExtractor, ExtractionError
from .extractors.twitter_extractor import TwitterExtractor
from .extractors.facebook_extractor import FacebookExtractor
from .extractors.google_reviews_extractor import GoogleReviewsExtractor
from .nlp.sentiment_analyzer import SentimentAnalyzer, SentimentTrendAnalyzer
from .nlp.keyword_extractor import KeywordExtractor
from .nlp.text_preprocessor import TextPreprocessor
from .visualization.charts_generator import ChartsGenerator
from .visualization.wordcloud_generator import WordCloudGenerator
from .visualization.report_generator import ReportGenerator
from .utils.logger import get_logger, app_logger
from .utils.file_manager import FileManager
from .utils.data_validator import DataValidator

logger = get_logger(__name__)

class SocialMediaAnalyzer:
    """Main orchestrator for social media sentiment analysis"""
    
    def __init__(self):
        self.extractor = None
        self.sentiment_analyzer = None
        self.keyword_extractor = None
        self.text_preprocessor = TextPreprocessor()
        self.charts_generator = ChartsGenerator()
        self.wordcloud_generator = WordCloudGenerator()
        self.report_generator = ReportGenerator()
        self.file_manager = FileManager()
        self.validator = DataValidator()
        
        logger.info("SocialMediaAnalyzer initialized")
    
    def analyze(self, service: str, source: str, days: int = 30, max_posts: int = 500,
                language: str = 'auto', sentiment_model: str = 'auto',
                keyword_method: str = 'combined', progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Perform complete social media sentiment analysis
        
        Args:
            service: Service/brand name to analyze
            source: Social media source (twitter, facebook, google_reviews)
            days: Number of days to analyze
            max_posts: Maximum number of posts to extract
            language: Language for analysis
            sentiment_model: Sentiment analysis model to use
            keyword_method: Keyword extraction method
            progress_callback: Callback function for progress updates
        
        Returns:
            Complete analysis results dictionary
        """
        try:
            start_time = time.time()
            
            if progress_callback:
                progress_callback(f"Starting analysis for '{service}' from {source}")
            
            logger.info(f"Starting analysis: service={service}, source={source}, days={days}, max_posts={max_posts}")
            
            # Step 1: Data Extraction
            if progress_callback:
                progress_callback("Extracting data from social media...")
            
            raw_data = self._extract_data(service, source, days, max_posts)
            
            if not raw_data:
                logger.error("No data extracted")
                return {'error': 'No data extracted', 'success': False}
            
            if progress_callback:
                progress_callback(f"Extracted {len(raw_data)} posts")
            
            # Step 2: Text Preprocessing
            if progress_callback:
                progress_callback("Preprocessing text data...")
            
            processed_data = self._preprocess_data(raw_data, language)
            
            # Step 3: Sentiment Analysis
            if progress_callback:
                progress_callback("Analyzing sentiment...")
            
            sentiment_results = self._analyze_sentiment(processed_data, sentiment_model, language)
            
            # Step 4: Keyword Extraction
            if progress_callback:
                progress_callback("Extracting keywords...")
            
            keywords = self._extract_keywords(processed_data, keyword_method)
            
            # Step 5: Temporal Analysis (if date data available)
            temporal_analysis = None
            if any('created_at' in item for item in processed_data):
                if progress_callback:
                    progress_callback("Analyzing temporal trends...")
                temporal_analysis = self._analyze_temporal_trends(sentiment_results, processed_data)
            
            # Step 6: Generate Summary Statistics
            if progress_callback:
                progress_callback("Generating summary statistics...")
            
            summary_stats = self._generate_summary_statistics(
                sentiment_results, keywords, raw_data, processed_data
            )
            
            # Step 7: Compile Results
            if progress_callback:
                progress_callback("Compiling final results...")
            
            results = self._compile_results(
                service, source, days, max_posts, raw_data, processed_data,
                sentiment_results, keywords, temporal_analysis, summary_stats
            )
            
            # Step 8: Generate Visualizations
            if progress_callback:
                progress_callback("Generating visualizations...")
            
            self._generate_visualizations(results)
            
            # Step 9: Save Results
            if progress_callback:
                progress_callback("Saving results...")
            
            output_dir = self.file_manager.save_analysis_report(results, service, source)
            
            execution_time = time.time() - start_time
            
            results['metadata']['execution_time'] = execution_time
            results['metadata']['output_directory'] = str(output_dir)
            
            logger.info(f"Analysis completed successfully in {execution_time:.2f} seconds")
            logger.info(f"Results saved to: {output_dir}")
            
            if progress_callback:
                progress_callback(f"Analysis completed in {execution_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {'error': str(e), 'success': False}
    
    def _extract_data(self, service: str, source: str, days: int, max_posts: int) -> List[Dict[str, Any]]:
        """Extract data from social media source"""
        try:
            # Initialize appropriate extractor
            if source.lower() == 'twitter':
                self.extractor = TwitterExtractor(service, max_posts)
            elif source.lower() == 'facebook':
                self.extractor = FacebookExtractor(service, max_posts)
            elif source.lower() == 'google_reviews':
                self.extractor = GoogleReviewsExtractor(service, max_posts)
            else:
                raise ValueError(f"Unsupported source: {source}")
            
            # Extract data
            raw_data = self.extractor.extract_posts(days=days)
            
            logger.info(f"Extracted {len(raw_data)} posts from {source}")
            return raw_data
            
        except ExtractionError as e:
            logger.error(f"Data extraction failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during data extraction: {e}")
            raise
    
    def _preprocess_data(self, raw_data: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Preprocess extracted data"""
        processed_data = []
        
        for item in raw_data:
            try:
                # Extract text content
                text = item.get('text', item.get('message', item.get('content', '')))
                
                if not text or not self.validator.validate_text_content(text):
                    continue
                
                # Preprocess text
                preprocessing_result = self.text_preprocessor.preprocess_text(text, language)
                
                # Create processed item
                processed_item = item.copy()
                processed_item.update({
                    'cleaned_text': preprocessing_result['cleaned'],
                    'tokens': preprocessing_result['tokens'],
                    'language': preprocessing_result['language'],
                    'preprocessing_steps': preprocessing_result['preprocessing_steps']
                })
                
                processed_data.append(processed_item)
                
            except Exception as e:
                logger.warning(f"Error preprocessing item {item.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Preprocessed {len(processed_data)} items")
        return processed_data
    
    def _analyze_sentiment(self, processed_data: List[Dict[str, Any]], 
                          sentiment_model: str, language: str) -> List[Dict[str, Any]]:
        """Analyze sentiment of processed data"""
        self.sentiment_analyzer = SentimentAnalyzer(sentiment_model, language)
        
        sentiment_results = []
        texts = [item['cleaned_text'] for item in processed_data]
        
        # Analyze sentiment for each text
        for i, (item, text) in enumerate(zip(processed_data, texts)):
            try:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(
                    text, item.get('language', language)
                )
                
                # Add metadata
                sentiment_result.update({
                    'id': item.get('id'),
                    'original_text': item.get('text', ''),
                    'date': item.get('created_at'),
                    'source': item.get('source'),
                    'service': item.get('service')
                })
                
                sentiment_results.append(sentiment_result)
                
            except Exception as e:
                logger.warning(f"Error analyzing sentiment for item {item.get('id', i)}: {e}")
                continue
        
        logger.info(f"Analyzed sentiment for {len(sentiment_results)} items")
        return sentiment_results
    
    def _extract_keywords(self, processed_data: List[Dict[str, Any]], 
                         keyword_method: str) -> List[Dict[str, Any]]:
        """Extract keywords from processed data"""
        self.keyword_extractor = KeywordExtractor(
            language='auto',  # Use auto-detection
            max_keywords=50
        )
        
        # Extract texts for keyword analysis
        texts = [item['cleaned_text'] for item in processed_data if item.get('cleaned_text')]
        
        if not texts:
            logger.warning("No texts available for keyword extraction")
            return []
        
        # Extract keywords
        keywords = self.keyword_extractor.extract_keywords(texts, keyword_method)
        
        # Also extract key phrases
        key_phrases = self.keyword_extractor.extract_key_phrases(texts)
        
        # Combine keywords and phrases
        all_keywords = keywords + key_phrases
        
        # Sort by score and limit
        all_keywords.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Extracted {len(all_keywords)} keywords/phrases")
        return all_keywords[:50]  # Limit to top 50
    
    def _analyze_temporal_trends(self, sentiment_results: List[Dict[str, Any]], 
                                processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal trends in sentiment"""
        try:
            trend_analyzer = SentimentTrendAnalyzer(self.sentiment_analyzer)
            
            # Prepare data for temporal analysis
            texts = []
            dates = []
            
            for result, item in zip(sentiment_results, processed_data):
                if item.get('created_at'):
                    texts.append(result.get('original_text', ''))
                    dates.append(item['created_at'])
            
            if not texts or not dates:
                logger.warning("Insufficient temporal data for trend analysis")
                return {}
            
            # Analyze trends
            trends = trend_analyzer.analyze_temporal_trends(texts, dates)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing temporal trends: {e}")
            return {}
    
    def _generate_summary_statistics(self, sentiment_results: List[Dict[str, Any]],
                                   keywords: List[Dict[str, Any]], 
                                   raw_data: List[Dict[str, Any]],
                                   processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        try:
            # Sentiment statistics
            sentiment_stats = self.sentiment_analyzer.get_sentiment_summary(sentiment_results)
            
            # Extraction statistics
            extraction_stats = self.extractor.get_extraction_stats() if self.extractor else {}
            
            # Processing statistics
            processing_stats = {
                'raw_data_count': len(raw_data),
                'processed_data_count': len(processed_data),
                'processing_success_rate': (len(processed_data) / len(raw_data) * 100) if raw_data else 0
            }
            
            # Keyword statistics
            keyword_stats = {
                'total_keywords': len(keywords),
                'avg_keyword_score': sum(kw.get('score', 0) for kw in keywords) / len(keywords) if keywords else 0,
                'top_keyword': keywords[0]['keyword'] if keywords else None
            }
            
            return {
                'sentiment_stats': sentiment_stats,
                'extraction_stats': extraction_stats,
                'processing_stats': processing_stats,
                'keyword_stats': keyword_stats
            }
            
        except Exception as e:
            logger.error(f"Error generating summary statistics: {e}")
            return {}
    
    def _compile_results(self, service: str, source: str, days: int, max_posts: int,
                        raw_data: List[Dict[str, Any]], processed_data: List[Dict[str, Any]],
                        sentiment_results: List[Dict[str, Any]], keywords: List[Dict[str, Any]],
                        temporal_analysis: Optional[Dict[str, Any]], 
                        summary_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Compile all results into final structure"""
        try:
            results = {
                'metadata': {
                    'service': service,
                    'source': source,
                    'analysis_date': datetime.now().isoformat(),
                    'parameters': {
                        'days': days,
                        'max_posts': max_posts,
                        'language': 'auto',
                        'sentiment_model': 'auto',
                        'keyword_method': 'combined'
                    }
                },
                'raw_data': raw_data,
                'processed_data': processed_data,
                'sentiment_results': sentiment_results,
                'sentiment_summary': summary_stats.get('sentiment_stats', {}),
                'keywords': keywords,
                'temporal_data': temporal_analysis.get('detailed_results', []) if temporal_analysis else [],
                'statistics': summary_stats,
                'success': True
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error compiling results: {e}")
            return {'error': str(e), 'success': False}
    
    def _generate_visualizations(self, results: Dict[str, Any]):
        """Generate visualizations for results"""
        try:
            # Create output directory for charts
            output_dir = Path(results['metadata']['output_directory']) / 'charts'
            output_dir.mkdir(exist_ok=True)
            
            # Generate charts
            self.charts_generator.save_all_charts(results, str(output_dir))
            
            # Generate word clouds
            wordclouds_dir = Path(results['metadata']['output_directory']) / 'wordclouds'
            wordclouds_dir.mkdir(exist_ok=True)
            self.wordcloud_generator.generate_all_wordclouds(results, str(wordclouds_dir))
            
            logger.info("Visualizations generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")

# Convenience function for direct usage
def analyze_social_media(service: str, source: str = 'twitter', days: int = 30, 
                        max_posts: int = 500, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to perform social media sentiment analysis
    
    Args:
        service: Service/brand name to analyze
        source: Social media source (twitter, facebook, google_reviews)
        days: Number of days to analyze
        max_posts: Maximum number of posts to extract
        **kwargs: Additional parameters (language, sentiment_model, etc.)
    
    Returns:
        Analysis results dictionary
    """
    analyzer = SocialMediaAnalyzer()
    
    return analyzer.analyze(
        service=service,
        source=source,
        days=days,
        max_posts=max_posts,
        **kwargs
    )