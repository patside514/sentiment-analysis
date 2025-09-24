"""
Word cloud generator for keyword visualization.
Creates word clouds from keywords and text data.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from PIL import Image

try:
    from wordcloud import WordCloud, STOPWORDS
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

from ..config import VizConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class WordCloudGenerator:
    """Generate word clouds from keywords and text data"""
    
    def __init__(self):
        self.width = VizConfig.WC_WIDTH
        self.height = VizConfig.WC_HEIGHT
        self.max_words = VizConfig.WC_MAX_WORDS
        self.collocations = VizConfig.WC_COLLOCATIONS
        
    def create_keyword_wordcloud(self, keywords: List[Dict[str, Any]], 
                               title: str = "Keywords Word Cloud",
                               save_path: Optional[str] = None,
                               colormap: str = 'viridis') -> Optional['WordCloud']:
        """Create word cloud from keywords with scores"""
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud library not available")
            return None
        
        if not keywords:
            logger.warning("No keywords provided for word cloud")
            return None
        
        try:
            # Prepare word frequencies from keywords
            word_frequencies = {}
            for keyword in keywords:
                word = keyword['keyword']
                # Use score as weight, fallback to frequency
                weight = keyword.get('score', keyword.get('frequency', 1))
                word_frequencies[word] = weight
            
            # Create word cloud
            wordcloud = WordCloud(
                width=self.width,
                height=self.height,
                max_words=self.max_words,
                colormap=colormap,
                background_color='white',
                relative_scaling=0.5,
                min_font_size=10,
                max_font_size=100,
                collocations=self.collocations,
                stopwords=set()  # We already filtered keywords
            ).generate_from_frequencies(word_frequencies)
            
            # Create visualization
            self._visualize_wordcloud(wordcloud, title, save_path)
            
            logger.info(f"Keyword word cloud created with {len(word_frequencies)} words")
            return wordcloud
            
        except Exception as e:
            logger.error(f"Error creating keyword word cloud: {e}")
            return None
    
    def create_text_wordcloud(self, texts: List[str], 
                            title: str = "Text Word Cloud",
                            save_path: Optional[str] = None,
                            colormap: str = 'plasma',
                            additional_stopwords: Optional[set] = None) -> Optional['WordCloud']:
        """Create word cloud from raw text data"""
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud library not available")
            return None
        
        if not texts:
            logger.warning("No texts provided for word cloud")
            return None
        
        try:
            # Combine all texts
            combined_text = ' '.join(texts)
            
            # Prepare stopwords
            stopwords = set(STOPWORDS)
            if additional_stopwords:
                stopwords.update(additional_stopwords)
            
            # Add language-specific stopwords
            if hasattr(self, 'language'):
                from ..nlp.text_preprocessor import TextPreprocessor
                preprocessor = TextPreprocessor(self.language)
                if hasattr(preprocessor, 'stop_words'):
                    for lang_stopwords in preprocessor.stop_words.values():
                        stopwords.update(lang_stopwords)
            
            # Create word cloud
            wordcloud = WordCloud(
                width=self.width,
                height=self.height,
                max_words=self.max_words,
                colormap=colormap,
                background_color='white',
                relative_scaling=0.5,
                min_font_size=10,
                max_font_size=100,
                collocations=self.collocations,
                stopwords=stopwords
            ).generate(combined_text)
            
            # Create visualization
            self._visualize_wordcloud(wordcloud, title, save_path)
            
            logger.info(f"Text word cloud created from {len(texts)} texts")
            return wordcloud
            
        except Exception as e:
            logger.error(f"Error creating text word cloud: {e}")
            return None
    
    def create_sentiment_wordcloud(self, sentiment_results: List[Dict[str, Any]],
                                 sentiment_type: str = 'positive',
                                 title: str = None,
                                 save_path: Optional[str] = None,
                                 colormap: str = None) -> Optional['WordCloud']:
        """Create word cloud for specific sentiment"""
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud library not available")
            return None
        
        if not sentiment_results:
            logger.warning("No sentiment results provided")
            return None
        
        try:
            # Filter texts by sentiment
            sentiment_texts = []
            for result in sentiment_results:
                if result['sentiment'] == sentiment_type:
                    # Extract text from result
                    text = result.get('text', '')
                    if text and text != '...':  # Skip truncated indicators
                        sentiment_texts.append(text)
            
            if not sentiment_texts:
                logger.warning(f"No texts found for sentiment: {sentiment_type}")
                return None
            
            # Set default parameters based on sentiment
            if title is None:
                title = f"{sentiment_type.capitalize()} Sentiment Word Cloud"
            
            if colormap is None:
                colormap = {
                    'positive': 'Greens',
                    'negative': 'Reds',
                    'neutral': 'Grays'
                }.get(sentiment_type, 'viridis')
            
            # Create word cloud
            wordcloud = self.create_text_wordcloud(
                texts=sentiment_texts,
                title=title,
                save_path=save_path,
                colormap=colormap
            )
            
            return wordcloud
            
        except Exception as e:
            logger.error(f"Error creating sentiment word cloud: {e}")
            return None
    
    def create_comparison_wordcloud(self, keywords_groups: Dict[str, List[Dict[str, Any]]],
                                  title: str = "Keywords Comparison",
                                  save_path: Optional[str] = None) -> Optional['WordCloud']:
        """Create word cloud comparing different groups of keywords"""
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud library not available")
            return None
        
        if not keywords_groups:
            logger.warning("No keyword groups provided")
            return None
        
        try:
            # Combine all keywords with group prefixes
            combined_frequencies = {}
            
            for group_name, keywords in keywords_groups.items():
                for keyword in keywords:
                    word = f"{group_name}:{keyword['keyword']}"
                    weight = keyword.get('score', keyword.get('frequency', 1))
                    combined_frequencies[word] = weight
            
            # Create word cloud
            wordcloud = WordCloud(
                width=self.width,
                height=self.height,
                max_words=self.max_words,
                colormap='tab10',
                background_color='white',
                relative_scaling=0.5,
                min_font_size=10,
                max_font_size=100,
                collocations=False
            ).generate_from_frequencies(combined_frequencies)
            
            # Create visualization
            self._visualize_wordcloud(wordcloud, title, save_path)
            
            logger.info(f"Comparison word cloud created with {len(combined_frequencies)} words")
            return wordcloud
            
        except Exception as e:
            logger.error(f"Error creating comparison word cloud: {e}")
            return None
    
    def create_custom_shape_wordcloud(self, keywords: List[Dict[str, Any]],
                                    mask_image_path: str,
                                    title: str = "Custom Shape Word Cloud",
                                    save_path: Optional[str] = None,
                                    colormap: str = 'viridis') -> Optional['WordCloud']:
        """Create word cloud in custom shape"""
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud library not available")
            return None
        
        if not keywords:
            logger.warning("No keywords provided")
            return None
        
        try:
            # Load mask image
            mask = np.array(Image.open(mask_image_path))
            
            # Prepare word frequencies
            word_frequencies = {}
            for keyword in keywords:
                word = keyword['keyword']
                weight = keyword.get('score', keyword.get('frequency', 1))
                word_frequencies[word] = weight
            
            # Create word cloud with mask
            wordcloud = WordCloud(
                width=self.width,
                height=self.height,
                max_words=self.max_words,
                colormap=colormap,
                background_color='white',
                mask=mask,
                relative_scaling=0.5,
                min_font_size=10,
                max_font_size=100,
                collocations=self.collocations,
                contour_width=3,
                contour_color='steelblue'
            ).generate_from_frequencies(word_frequencies)
            
            # Create visualization
            self._visualize_wordcloud(wordcloud, title, save_path)
            
            logger.info(f"Custom shape word cloud created")
            return wordcloud
            
        except Exception as e:
            logger.error(f"Error creating custom shape word cloud: {e}")
            return None
    
    def _visualize_wordcloud(self, wordcloud: 'WordCloud', title: str, save_path: Optional[str]):
        """Visualize word cloud"""
        try:
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Word cloud saved to {save_path}")
            else:
                plt.show()
                
        except Exception as e:
            logger.error(f"Error visualizing word cloud: {e}")
    
    def create_wordcloud_comparison_grid(self, sentiment_results: List[Dict[str, Any]],
                                       title: str = "Sentiment Word Clouds Comparison",
                                       save_path: Optional[str] = None) -> bool:
        """Create grid of word clouds for different sentiments"""
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud library not available")
            return False
        
        try:
            # Create figure with subplots
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            fig.suptitle(title, fontsize=16, fontweight='bold')
            
            sentiments = ['positive', 'negative', 'neutral']
            colormaps = ['Greens', 'Reds', 'Grays']
            titles = ['Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment']
            
            for i, (sentiment, colormap, subtitle) in enumerate(zip(sentiments, colormaps, titles)):
                # Filter texts for this sentiment
                sentiment_texts = [
                    r.get('text', '') for r in sentiment_results 
                    if r['sentiment'] == sentiment and r.get('text', '') and r.get('text', '') != '...'
                ]
                
                if sentiment_texts:
                    # Create word cloud
                    wordcloud = self.create_text_wordcloud(
                        texts=sentiment_texts,
                        title=subtitle,
                        colormap=colormap
                    )
                    
                    if wordcloud:
                        axes[i].imshow(wordcloud, interpolation='bilinear')
                        axes[i].set_title(subtitle, fontsize=12, fontweight='bold')
                    else:
                        axes[i].text(0.5, 0.5, 'No Data', ha='center', va='center', 
                                   transform=axes[i].transAxes)
                        axes[i].set_title(subtitle, fontsize=12, fontweight='bold')
                else:
                    axes[i].text(0.5, 0.5, 'No Data', ha='center', va='center', 
                               transform=axes[i].transAxes)
                    axes[i].set_title(subtitle, fontsize=12, fontweight='bold')
                
                axes[i].axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Word cloud comparison grid saved to {save_path}")
            else:
                plt.show()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating word cloud comparison grid: {e}")
            return False
    
    def generate_all_wordclouds(self, analysis_results: Dict[str, Any], output_dir: str):
        """Generate all types of word clouds"""
        try:
            import os
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Keyword word cloud
            if 'keywords' in analysis_results:
                self.create_keyword_wordcloud(
                    keywords=analysis_results['keywords'],
                    save_path=os.path.join(output_dir, 'keywords_wordcloud.png')
                )
            
            # Sentiment word clouds
            if 'sentiment_results' in analysis_results:
                # Individual sentiment word clouds
                for sentiment in ['positive', 'negative', 'neutral']:
                    self.create_sentiment_wordcloud(
                        sentiment_results=analysis_results['sentiment_results'],
                        sentiment_type=sentiment,
                        save_path=os.path.join(output_dir, f'{sentiment}_sentiment_wordcloud.png')
                    )
                
                # Comparison grid
                self.create_wordcloud_comparison_grid(
                    sentiment_results=analysis_results['sentiment_results'],
                    save_path=os.path.join(output_dir, 'sentiment_wordclouds_comparison.png')
                )
            
            # Text word cloud (if raw texts available)
            if 'raw_texts' in analysis_results:
                self.create_text_wordcloud(
                    texts=analysis_results['raw_texts'],
                    save_path=os.path.join(output_dir, 'text_wordcloud.png')
                )
            
            logger.info(f"All word clouds generated in {output_dir}")
            
        except Exception as e:
            logger.error(f"Error generating word clouds: {e}")