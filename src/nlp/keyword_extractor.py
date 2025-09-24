"""
Keyword extraction module using multiple techniques.
Supports TF-IDF, TextRank, and frequency-based extraction.
"""
from typing import List, Dict, Any, Optional, Tuple
import re
from collections import Counter
from itertools import combinations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from .text_preprocessor import TextPreprocessor
from ..utils.logger import get_logger

logger = get_logger(__name__)

class KeywordExtractor:
    """Multi-technique keyword extractor"""
    
    def __init__(self, language: str = 'auto', max_keywords: int = 50):
        self.language = language
        self.max_keywords = max_keywords
        self.preprocessor = TextPreprocessor(language)
        self.tfidf_vectorizer = None
    
    def extract_keywords(self, texts: List[str], method: str = 'combined') -> List[Dict[str, Any]]:
        """Extract keywords from texts using specified method"""
        if not texts:
            return []
        
        try:
            if method == 'tfidf':
                return self._extract_with_tfidf(texts)
            elif method == 'frequency':
                return self._extract_with_frequency(texts)
            elif method == 'textrank':
                return self._extract_with_textrank(texts)
            elif method == 'combined':
                return self._extract_combined(texts)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
    
    def _extract_with_tfidf(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract keywords using TF-IDF"""
        try:
            # Preprocess texts
            processed_texts = []
            for text in texts:
                result = self.preprocessor.preprocess_text(text)
                processed_texts.append(' '.join(result['tokens']))
            
            # Create TF-IDF vectorizer
            stop_words_lang = 'english' if self.language == 'english' else 'english'  # Default to English
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.8,
                stop_words=stop_words_lang
            )
            
            # Fit and transform
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF scores across all documents
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get top keywords
            top_indices = np.argsort(mean_scores)[-self.max_keywords:][::-1]
            
            keywords = []
            for idx in top_indices:
                keyword = feature_names[idx]
                score = mean_scores[idx]
                
                if score > 0:
                    keywords.append({
                        'keyword': keyword,
                        'score': float(score),
                        'frequency': self._calculate_frequency(keyword, processed_texts),
                        'method': 'tfidf'
                    })
            
            return keywords
            
        except Exception as e:
            logger.error(f"TF-IDF extraction error: {e}")
            return []
    
    def _extract_with_frequency(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract keywords based on frequency"""
        try:
            # Preprocess all texts
            all_tokens = []
            for text in texts:
                result = self.preprocessor.preprocess_text(text)
                all_tokens.extend(result['tokens'])
            
            # Count token frequencies
            token_counts = Counter(all_tokens)
            
            # Filter by minimum frequency
            min_frequency = max(2, len(texts) * 0.01)
            frequent_tokens = {
                token: count for token, count in token_counts.items()
                if count >= min_frequency
            }
            
            # Calculate scores (normalized frequency)
            max_count = max(frequent_tokens.values()) if frequent_tokens else 1
            keywords = []
            
            for token, count in sorted(frequent_tokens.items(), key=lambda x: x[1], reverse=True):
                if len(keywords) >= self.max_keywords:
                    break
                
                keywords.append({
                    'keyword': token,
                    'score': count / max_count,
                    'frequency': count,
                    'method': 'frequency'
                })
            
            return keywords
            
        except Exception as e:
            logger.error(f"Frequency extraction error: {e}")
            return []
    
    def _extract_with_textrank(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract keywords using TextRank algorithm"""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy not available, falling back to TF-IDF")
            return self._extract_with_tfidf(texts)
        
        try:
            # Load spaCy model
            nlp = spacy.load('fr_core_news_sm' if self.language == 'french' else 'en_core_web_sm')
            
            # Process texts
            all_words = []
            sentences = []
            
            for text in texts:
                doc = nlp(text)
                sentences.extend(list(doc.sents))
                
                for token in doc:
                    if self._is_valid_token(token):
                        all_words.append(token.lemma_.lower())
            
            # Build word co-occurrence graph
            co_occurrence = self._build_cooccurrence_matrix(all_words)
            
            # Calculate TextRank scores
            textrank_scores = self._calculate_textrank(co_occurrence)
            
            # Get top keywords
            top_words = sorted(textrank_scores.items(), key=lambda x: x[1], reverse=True)
            
            keywords = []
            for word, score in top_words[:self.max_keywords]:
                frequency = all_words.count(word)
                keywords.append({
                    'keyword': word,
                    'score': score,
                    'frequency': frequency,
                    'method': 'textrank'
                })
            
            return keywords
            
        except Exception as e:
            logger.error(f"TextRank extraction error: {e}")
            return self._extract_with_tfidf(texts)  # Fallback
    
    def _extract_combined(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Combine multiple keyword extraction methods"""
        # Extract keywords using different methods
        tfidf_keywords = {k['keyword']: k for k in self._extract_with_tfidf(texts)}
        frequency_keywords = {k['keyword']: k for k in self._extract_with_frequency(texts)}
        textrank_keywords = {k['keyword']: k for k in self._extract_with_textrank(texts)}
        
        # Combine all unique keywords
        all_keywords = set(tfidf_keywords.keys()) | set(frequency_keywords.keys()) | set(textrank_keywords.keys())
        
        combined_keywords = []
        for keyword in all_keywords:
            scores = []
            frequencies = []
            methods = []
            
            if keyword in tfidf_keywords:
                scores.append(tfidf_keywords[keyword]['score'])
                frequencies.append(tfidf_keywords[keyword]['frequency'])
                methods.append('tfidf')
            
            if keyword in frequency_keywords:
                scores.append(frequency_keywords[keyword]['score'])
                frequencies.append(frequency_keywords[keyword]['frequency'])
                methods.append('frequency')
            
            if keyword in textrank_keywords:
                scores.append(textrank_keywords[keyword]['score'])
                frequencies.append(textrank_keywords[keyword]['frequency'])
                methods.append('textrank')
            
            # Calculate combined score (average)
            combined_score = np.mean(scores)
            total_frequency = sum(frequencies)
            
            combined_keywords.append({
                'keyword': keyword,
                'score': combined_score,
                'frequency': total_frequency,
                'methods': methods,
                'method': 'combined'
            })
        
        # Sort by combined score
        combined_keywords.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_keywords[:self.max_keywords]
    
    def _build_cooccurrence_matrix(self, words: List[str], window_size: int = 4) -> Dict[str, Dict[str, int]]:
        """Build co-occurrence matrix for TextRank"""
        co_occurrence = {}
        
        for i, word in enumerate(words):
            if word not in co_occurrence:
                co_occurrence[word] = {}
            
            # Look at words within window
            start = max(0, i - window_size)
            end = min(len(words), i + window_size + 1)
            
            for j in range(start, end):
                if i != j:
                    other_word = words[j]
                    if other_word not in co_occurrence[word]:
                        co_occurrence[word][other_word] = 0
                    co_occurrence[word][other_word] += 1
        
        return co_occurrence
    
    def _calculate_textrank(self, co_occurrence: Dict[str, Dict[str, int]], 
                           max_iterations: int = 100, damping_factor: float = 0.85) -> Dict[str, float]:
        """Calculate TextRank scores"""
        words = list(co_occurrence.keys())
        scores = {word: 1.0 for word in words}
        
        for _ in range(max_iterations):
            new_scores = {}
            
            for word in words:
                score = (1 - damping_factor)
                
                # Add contribution from neighbors
                for other_word, weight in co_occurrence[word].items():
                    if other_word in scores:
                        other_total_weight = sum(co_occurrence[other_word].values())
                        if other_total_weight > 0:
                            score += damping_factor * (scores[other_word] * weight / other_total_weight)
                
                new_scores[word] = score
            
            scores = new_scores
        
        return scores
    
    def _is_valid_token(self, token) -> bool:
        """Check if spaCy token is valid for keyword extraction"""
        return (token.is_alpha and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2)
    
    def _calculate_frequency(self, keyword: str, texts: List[str]) -> int:
        """Calculate frequency of keyword in texts"""
        count = 0
        for text in texts:
            count += text.lower().count(keyword.lower())
        return count
    
    def extract_key_phrases(self, texts: List[str], min_length: int = 2, 
                          max_length: int = 4) -> List[Dict[str, Any]]:
        """Extract key phrases (multi-word keywords)"""
        try:
            # Preprocess texts
            processed_texts = []
            for text in texts:
                result = self.preprocessor.preprocess_text(text)
                processed_texts.append(' '.join(result['tokens']))
            
            # Extract n-grams
            all_ngrams = []
            for n in range(min_length, max_length + 1):
                ngrams = self._extract_ngrams(processed_texts, n)
                all_ngrams.extend(ngrams)
            
            # Count n-gram frequencies
            ngram_counts = Counter(all_ngrams)
            
            # Filter by minimum frequency
            min_frequency = max(2, len(texts) * 0.005)
            frequent_ngrams = {
                ngram: count for ngram, count in ngram_counts.items()
                if count >= min_frequency
            }
            
            # Calculate scores
            phrases = []
            for ngram, count in sorted(frequent_ngrams.items(), key=lambda x: x[1], reverse=True):
                if len(phrases) >= self.max_keywords:
                    break
                
                phrases.append({
                    'keyword': ' '.join(ngram),
                    'score': count / max(frequent_ngrams.values()),
                    'frequency': count,
                    'length': len(ngram),
                    'method': 'ngram'
                })
            
            return phrases
            
        except Exception as e:
            logger.error(f"Key phrase extraction error: {e}")
            return []
    
    def _extract_ngrams(self, texts: List[str], n: int) -> List[tuple]:
        """Extract n-grams from texts"""
        ngrams = []
        
        for text in texts:
            words = text.split()
            if len(words) >= n:
                for i in range(len(words) - n + 1):
                    ngram = tuple(words[i:i + n])
                    ngrams.append(ngram)
        
        return ngrams
    
    def get_keyword_trends(self, keywords: List[str], texts: List[str], 
                          dates: List[str]) -> Dict[str, Any]:
        """Analyze keyword trends over time"""
        if len(texts) != len(dates):
            raise ValueError("Texts and dates lists must have the same length")
        
        trends = {}
        
        for keyword in keywords:
            keyword_trend = []
            
            for text, date in zip(texts, dates):
                # Count keyword occurrences
                count = text.lower().count(keyword.lower())
                
                keyword_trend.append({
                    'date': date,
                    'count': count,
                    'present': count > 0
                })
            
            trends[keyword] = keyword_trend
        
        return trends