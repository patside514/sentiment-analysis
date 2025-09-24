#!/usr/bin/env python3
"""
Demo script to showcase the social media sentiment analysis capabilities
using simulated data when APIs are not available.
"""

import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from src.main import SocialMediaAnalyzer
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.nlp.keyword_extractor import KeywordExtractor
from src.visualization.charts_generator import ChartsGenerator
from src.visualization.wordcloud_generator import WordCloudGenerator
from src.utils.file_manager import FileManager

def generate_demo_data(service="DemoService", num_posts=100):
    """Generate realistic demo data for testing"""
    
    # Sample positive, negative, and neutral texts
    positive_texts = [
        f"J'adore {service} ! C'est vraiment génial et super pratique.",
        f"{service} est excellent, je recommande vivement !",
        f"Service impeccable avec {service}, toujours satisfait.",
        f"{service} a changé ma vie, c'est incroyable !",
        f"Que du positif avec {service}, bravo à l'équipe !",
        f"Je suis fan de {service}, c'est le meilleur !",
        f"{service} est top qualité, je suis très content.",
        f"Excellent service client chez {service}, très réactif.",
        f"{service} est fiable et efficace, parfait !",
        f"Super expérience avec {service}, je recommande !"
    ]
    
    negative_texts = [
        f"{service} est décevant, je ne suis pas satisfait.",
        f"Service médiocre avec {service}, à éviter.",
        f"Je déteste {service}, c'est nul.",
        f"{service} ne fonctionne pas correctement, problématique.",
        f"Mauvaise expérience avec {service}, déçu.",
        f"{service} est lent et bugué, pas content.",
        f"Service client inexistant chez {service}, catastrophe.",
        f"{service} est trop cher pour ce que c'est.",
        f"Je regrette d'avoir choisi {service}, mauvais choix.",
        f"{service} ne vaut pas le prix, déception."
    ]
    
    neutral_texts = [
        f"{service} est un service que j'utilise régulièrement.",
        f"J'ai testé {service}, c'est correct sans plus.",
        f"{service} fait le job, rien de spécial à signaler.",
        f"Utilisation normale de {service}, sans problème.",
        f"{service} est comme les autres, standard.",
        f"Rien à dire sur {service}, c'est passable.",
        f"Service moyen avec {service}, ni bon ni mauvais.",
        f"{service} remplit ses fonctions basiques.",
        f"Expérience normale avec {service}, sans surprise.",
        f"{service} est utilisable, c'est le principal."
    ]
    
    # Generate mixed data
    demo_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_posts):
        # Random sentiment distribution (40% positive, 30% negative, 30% neutral)
        sentiment_choice = random.choices(['positive', 'negative', 'neutral'], weights=[40, 30, 30])[0]
        
        if sentiment_choice == 'positive':
            text = random.choice(positive_texts)
        elif sentiment_choice == 'negative':
            text = random.choice(negative_texts)
        else:
            text = random.choice(neutral_texts)
        
        # Add some variation
        if random.random() > 0.7:
            text += f" #{service}{random.randint(1, 100)}"
        
        # Generate random date within the last 30 days
        random_date = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        post = {
            'id': f"demo_post_{i+1}",
            'text': text,
            'created_at': random_date.isoformat(),
            'source': 'demo',
            'service': service,
            'likes': random.randint(0, 100),
            'shares': random.randint(0, 50),
            'comments': random.randint(0, 20)
        }
        
        demo_data.append(post)
    
    return demo_data

def demo_sentiment_analysis():
    """Demonstrate sentiment analysis capabilities"""
    print("🧠 Demo: Sentiment Analysis")
    print("=" * 50)
    
    # Sample texts
    sample_texts = [
        "J'adore ce produit ! Il est génial et très pratique.",
        "Ce service est nul, je déteste vraiment.",
        "C'est correct, sans plus. Rien de spécial.",
        "Excellent service client, très réactif et professionnel.",
        "Déçu par la qualité, ça ne vaut pas le prix."
    ]
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    print("\nAnalyzing sample texts:")
    for i, text in enumerate(sample_texts, 1):
        result = analyzer.analyze_sentiment(text, language='fr')
        print(f"\n{i}. Text: {text[:50]}...")
        print(f"   Sentiment: {result['sentiment']} (confidence: {result['confidence']:.3f})")
        print(f"   Polarity: {result['polarity']:.3f}")
    
    # Batch analysis
    print(f"\n📊 Batch analysis summary:")
    results = analyzer.analyze_batch(sample_texts, language='fr')
    summary = analyzer.get_sentiment_summary(results)
    
    print(f"Total texts: {summary['total']}")
    print(f"Positive: {summary['positive']} ({summary['percentages']['positive']:.1f}%)")
    print(f"Negative: {summary['negative']} ({summary['percentages']['negative']:.1f}%)")
    print(f"Neutral: {summary['neutral']} ({summary['percentages']['neutral']:.1f}%)")

def demo_keyword_extraction():
    """Demonstrate keyword extraction capabilities"""
    print("\n\n🔑 Demo: Keyword Extraction")
    print("=" * 50)
    
    # Sample corpus
    sample_texts = [
        "Le service client est excellent et très réactif. J'apprécie beaucoup la qualité du support.",
        "La qualité du produit est remarquable, excellent rapport qualité-prix.",
        "Service rapide et efficace, je recommande vivement cette entreprise.",
        "Excellent service, très professionnel et réactif. Qualité supérieure.",
        "Le support technique est de grande qualité, service client exceptionnel."
    ]
    
    # Initialize extractor
    extractor = KeywordExtractor(max_keywords=10)
    
    print("\nExtracting keywords using different methods:")
    
    methods = ['tfidf', 'frequency', 'textrank', 'combined']
    for method in methods:
        print(f"\n📍 Method: {method.upper()}")
        keywords = extractor.extract_keywords(sample_texts, method=method)
        
        for i, kw in enumerate(keywords[:5], 1):
            print(f"   {i}. {kw['keyword']} (score: {kw['score']:.3f}, freq: {kw['frequency']})")

def demo_visualizations():
    """Demonstrate visualization capabilities"""
    print("\n\n📊 Demo: Visualizations")
    print("=" * 50)
    
    # Create sample sentiment data
    sentiment_summary = {
        'total': 100,
        'positive': 45,
        'negative': 25,
        'neutral': 30,
        'percentages': {
            'positive': 45.0,
            'negative': 25.0,
            'neutral': 30.0
        },
        'average_polarity': 0.15,
        'average_confidence': 0.75
    }
    
    # Create sample keyword data
    keywords = [
        {'keyword': 'service client', 'score': 0.95, 'frequency': 25, 'method': 'combined'},
        {'keyword': 'qualité', 'score': 0.88, 'frequency': 20, 'method': 'combined'},
        {'keyword': 'excellent', 'score': 0.82, 'frequency': 18, 'method': 'combined'},
        {'keyword': 'réactif', 'score': 0.75, 'frequency': 15, 'method': 'combined'},
        {'keyword': 'professionnel', 'score': 0.68, 'frequency': 12, 'method': 'combined'}
    ]
    
    # Initialize chart generator
    chart_gen = ChartsGenerator()
    
    print("Generating sample visualizations...")
    
    # Generate charts
    try:
        # Pie chart
        fig1 = chart_gen.create_sentiment_pie_chart(sentiment_summary, "Demo Sentiment Distribution")
        print("✅ Sentiment pie chart generated")
        
        # Bar chart
        fig2 = chart_gen.create_sentiment_bar_chart(sentiment_summary, "Demo Sentiment Analysis")
        print("✅ Sentiment bar chart generated")
        
        # Keyword charts
        fig3 = chart_gen.create_keyword_frequency_chart(keywords, "Demo Keywords")
        print("✅ Keyword frequency chart generated")
        
        # Dashboard
        demo_results = {
            'sentiment_summary': sentiment_summary,
            'keywords': keywords,
            'temporal_data': [],
            'sentiment_results': []
        }
        fig4 = chart_gen.create_overall_summary_chart(demo_results, "Demo Dashboard")
        print("✅ Summary dashboard generated")
        
        print("\n📈 Visualizations created successfully!")
        
    except Exception as e:
        print(f"⚠️  Visualization error: {e}")

def demo_complete_analysis():
    """Demonstrate complete analysis workflow"""
    print("\n\n🚀 Demo: Complete Analysis Workflow")
    print("=" * 50)
    
    # Generate demo data
    print("Generating demo data...")
    demo_data = generate_demo_data("DemoService", 50)
    
    print(f"✅ Generated {len(demo_data)} demo posts")
    
    # Simulate analysis
    print("\nSimulating complete analysis...")
    
    # Initialize components
    analyzer = SocialMediaAnalyzer()
    file_manager = FileManager()
    
    try:
        # Simulate sentiment analysis
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_results = []
        
        for item in demo_data:
            result = sentiment_analyzer.analyze_sentiment(item['text'], 'fr')
            result.update({
                'id': item['id'],
                'date': item['created_at'],
                'original_text': item['text']
            })
            sentiment_results.append(result)
        
        # Simulate keyword extraction
        keyword_extractor = KeywordExtractor(max_keywords=15)
        texts = [item['text'] for item in demo_data]
        keywords = keyword_extractor.extract_keywords(texts, 'combined')
        
        # Create results structure
        results = {
            'metadata': {
                'service': 'DemoService',
                'source': 'demo',
                'analysis_date': datetime.now().isoformat(),
                'parameters': {
                    'days': 30,
                    'max_posts': 50
                }
            },
            'sentiment_results': sentiment_results,
            'sentiment_summary': sentiment_analyzer.get_sentiment_summary(sentiment_results),
            'keywords': keywords,
            'raw_data': demo_data,
            'success': True
        }
        
        # Save results
        output_dir = file_manager.save_analysis_report(results, 'DemoService', 'demo')
        
        print(f"✅ Analysis completed successfully!")
        print(f"📁 Results saved to: {output_dir}")
        
        # Display summary
        summary = results['sentiment_summary']
        print(f"\n📊 Sentiment Summary:")
        print(f"   Total posts: {summary['total']}")
        print(f"   Positive: {summary['positive']} ({summary['percentages']['positive']:.1f}%)")
        print(f"   Negative: {summary['negative']} ({summary['percentages']['negative']:.1f}%)")
        print(f"   Neutral: {summary['neutral']} ({summary['percentages']['neutral']:.1f}%)")
        
        print(f"\n🔑 Top Keywords:")
        for i, kw in enumerate(keywords[:5], 1):
            print(f"   {i}. {kw['keyword']} (score: {kw['score']:.3f})")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    """Main demo function"""
    print("🎯 Social Media Sentiment Analysis - Demo")
    print("=" * 60)
    print("This demo showcases the capabilities of the sentiment analysis tool")
    print("using simulated data when APIs are not available.\n")
    
    # Run individual demos
    demo_sentiment_analysis()
    demo_keyword_extraction()
    demo_visualizations()
    demo_complete_analysis()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\nTo run real analysis with actual social media data:")
    print("1. Configure your API keys in .env file")
    print("2. Run: python app.py --service 'YourService' --source 'twitter' --days 30")
    print("\nFor more options, run: python app.py --help")

if __name__ == '__main__':
    main()