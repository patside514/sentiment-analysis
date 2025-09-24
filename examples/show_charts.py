#!/usr/bin/env python3
"""
Script to demonstrate chart generation capabilities
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from visualization.charts_generator import ChartsGenerator
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def main():
    print("🎨 Generating Sample Visualizations")
    print("=" * 50)
    
    # Create sample data
    sentiment_summary = {
        'total': 100,
        'positive': 45,
        'negative': 25,
        'neutral': 30,
        'percentages': {'positive': 45.0, 'negative': 25.0, 'neutral': 30.0},
        'average_polarity': 0.15,
        'average_confidence': 0.75
    }
    
    keywords = [
        {'keyword': 'service client', 'score': 0.95, 'frequency': 25},
        {'keyword': 'qualité', 'score': 0.88, 'frequency': 20},
        {'keyword': 'excellent', 'score': 0.82, 'frequency': 18},
        {'keyword': 'rapide', 'score': 0.75, 'frequency': 15},
        {'keyword': 'professionnel', 'score': 0.68, 'frequency': 12}
    ]
    
    # Generate charts
    chart_gen = ChartsGenerator()
    
    print("Creating visualizations...")
    
    # Pie chart
    fig1 = chart_gen.create_sentiment_pie_chart(sentiment_summary, 'Sentiment Distribution')
    print("✅ Sentiment pie chart created")
    
    # Bar chart  
    fig2 = chart_gen.create_sentiment_bar_chart(sentiment_summary, 'Sentiment Analysis Results')
    print("✅ Sentiment bar chart created")
    
    # Keyword chart
    fig3 = chart_gen.create_keyword_frequency_chart(keywords, 'Top Keywords by Frequency')
    print("✅ Keyword frequency chart created")
    
    # Dashboard
    demo_results = {
        'sentiment_summary': sentiment_summary,
        'keywords': keywords,
        'temporal_data': [],
        'sentiment_results': []
    }
    fig4 = chart_gen.create_overall_summary_chart(demo_results, 'Analysis Dashboard')
    print("✅ Summary dashboard created")
    
    print("\n🎉 All visualizations generated successfully!")
    print("📊 In a real execution, these would be saved as PNG files")
    print("📁 Charts would be saved in: outputs/[service]_[source]_[timestamp]/charts/")

if __name__ == '__main__':
    main()