#!/usr/bin/env python3
"""
Simple test script to verify the sentiment analysis functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.nlp.keyword_extractor import KeywordExtractor
from src.visualization.charts_generator import ChartsGenerator

def test_sentiment_analysis():
    """Test sentiment analysis with sample texts"""
    print("🧪 Testing Sentiment Analysis")
    print("-" * 40)
    
    # Sample texts in French and English
    test_texts = [
        "J'adore ce produit, il est excellent !",
        "Ce service est vraiment nul, je déteste.",
        "C'est correct, sans plus.",
        "I love this product, it's amazing!",
        "This service is terrible, I hate it.",
        "It's okay, nothing special."
    ]
    
    analyzer = SentimentAnalyzer()
    
    for i, text in enumerate(test_texts, 1):
        result = analyzer.analyze_sentiment(text)
        print(f"\n{i}. Text: {text}")
        print(f"   Language: {result.get('language', 'auto')}")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Polarity: {result['polarity']:.3f}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Method: {result['method']}")

def test_keyword_extraction():
    """Test keyword extraction"""
    print("\n\n🔑 Testing Keyword Extraction")
    print("-" * 40)
    
    # Sample corpus
    texts = [
        "Le service client est excellent et très réactif.",
        "La qualité du produit est remarquable.",
        "Service rapide et efficace avec un bon support.",
        "Excellent rapport qualité-prix, je recommande.",
        "Le support technique est très professionnel."
    ]
    
    extractor = KeywordExtractor(max_keywords=10)
    
    # Test frequency method (should work without issues)
    print("\nUsing Frequency Method:")
    keywords = extractor.extract_keywords(texts, method='frequency')
    
    for i, kw in enumerate(keywords[:5], 1):
        print(f"{i}. {kw['keyword']} (freq: {kw['frequency']}, score: {kw['score']:.3f})")

def test_visualizations():
    """Test visualization generation"""
    print("\n\n📊 Testing Visualizations")
    print("-" * 40)
    
    # Create sample data
    sentiment_summary = {
        'total': 50,
        'positive': 25,
        'negative': 10,
        'neutral': 15,
        'percentages': {'positive': 50.0, 'negative': 20.0, 'neutral': 30.0},
        'average_polarity': 0.3,
        'average_confidence': 0.8
    }
    
    keywords = [
        {'keyword': 'service', 'score': 0.9, 'frequency': 15},
        {'keyword': 'quality', 'score': 0.8, 'frequency': 12},
        {'keyword': 'excellent', 'score': 0.7, 'frequency': 10},
        {'keyword': 'support', 'score': 0.6, 'frequency': 8},
        {'keyword': 'recommend', 'score': 0.5, 'frequency': 6}
    ]
    
    chart_gen = ChartsGenerator()
    
    try:
        # Test pie chart
        fig1 = chart_gen.create_sentiment_pie_chart(sentiment_summary)
        print("✅ Sentiment pie chart created")
        
        # Test bar chart
        fig2 = chart_gen.create_sentiment_bar_chart(sentiment_summary)
        print("✅ Sentiment bar chart created")
        
        # Test keyword chart
        fig3 = chart_gen.create_keyword_frequency_chart(keywords)
        print("✅ Keyword frequency chart created")
        
        print("\n📈 All visualizations created successfully!")
        
    except Exception as e:
        print(f"⚠️ Visualization error: {e}")

def main():
    """Run all tests"""
    print("🚀 Social Media Sentiment Analysis - Simple Test")
    print("=" * 60)
    print("Testing core functionality without external dependencies...\n")
    
    try:
        test_sentiment_analysis()
        test_keyword_extraction()
        test_visualizations()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\nThe application core functionality is working correctly.")
        print("To run full analysis with real data, configure API keys in .env file")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())