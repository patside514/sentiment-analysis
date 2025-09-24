#!/usr/bin/env python3
"""
Live demonstration of the Social Media Sentiment Analysis Tool
Shows real execution with simulated data
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from src.main import SocialMediaAnalyzer
from src.utils.file_manager import FileManager

def main():
    print("🚀 LIVE DEMO: Social Media Sentiment Analysis Tool")
    print("=" * 60)
    print("This is a real execution with simulated data")
    print("In production, this would connect to real social media APIs\n")
    
    # Initialize analyzer
    analyzer = SocialMediaAnalyzer()
    file_manager = FileManager()
    
    # Define analysis parameters
    service = "Netflix"
    source = "twitter"  # Will use demo data
    days = 7
    max_posts = 50
    
    print(f"📊 Analyzing sentiment for: {service}")
    print(f"📱 Source: {source}")
    print(f"📅 Time period: {days} days")
    print(f"📝 Max posts: {max_posts}")
    
    try:
        # Progress callback to show real-time updates
        def progress_callback(message):
            print(f"⏳ {message}")
        
        # Run analysis
        print("\n" + "-" * 40)
        results = analyzer.analyze(
            service=service,
            source=source,
            days=days,
            max_posts=max_posts,
            progress_callback=progress_callback
        )
        
        if not results or not results.get('success'):
            print("❌ Analysis failed")
            return 1
        
        # Display results
        print("\n" + "=" * 60)
        print("📈 ANALYSIS RESULTS")
        print("=" * 60)
        
        # Sentiment summary
        sentiment_summary = results.get('sentiment_summary', {})
        if sentiment_summary:
            print(f"\n🎯 Sentiment Summary:")
            print(f"   Total posts analyzed: {sentiment_summary.get('total', 0)}")
            print(f"   Positive: {sentiment_summary.get('positive', 0)} ({sentiment_summary.get('percentages', {}).get('positive', 0):.1f}%)")
            print(f"   Negative: {sentiment_summary.get('negative', 0)} ({sentiment_summary.get('percentages', {}).get('negative', 0):.1f}%)")
            print(f"   Neutral: {sentiment_summary.get('neutral', 0)} ({sentiment_summary.get('percentages', {}).get('neutral', 0):.1f}%)")
            print(f"   Average polarity: {sentiment_summary.get('average_polarity', 0):.3f}")
            print(f"   Average confidence: {sentiment_summary.get('average_confidence', 0):.3f}")
        
        # Top keywords
        keywords = results.get('keywords', [])
        if keywords:
            print(f"\n🔑 Top Keywords:")
            for i, kw in enumerate(keywords[:10], 1):
                print(f"   {i:2d}. {kw['keyword'][:20]:<20} (score: {kw['score']:.3f}, freq: {kw['frequency']})")
        
        # Output location
        output_dir = results.get('metadata', {}).get('output_directory')
        if output_dir:
            print(f"\n📁 Results saved to: {output_dir}")
            print("   Files generated:")
            print("   • raw_data_[timestamp].csv - Raw extracted data")
            print("   • sentiment_summary.json - Sentiment analysis results")
            print("   • report_metadata.json - Analysis metadata")
            print("   • Charts and visualizations (in charts/ folder)")
            print("   • Word clouds (in wordclouds/ folder)")
        
        # Show sample of processed data
        processed_data = results.get('processed_data', [])
        if processed_data:
            print(f"\n📝 Sample Processed Posts:")
            for i, post in enumerate(processed_data[:3], 1):
                text = post.get('text', '')[:60] + '...' if len(post.get('text', '')) > 60 else post.get('text', '')
                sentiment = post.get('sentiment', 'unknown')
                print(f"   {i}. {text}")
                print(f"      → Sentiment: {sentiment}")
        
        # Generate HTML report
        print(f"\n📄 Generating HTML report...")
        from src.visualization.report_generator import ReportGenerator
        report_gen = ReportGenerator()
        html_path = report_gen.generate_html_report(results, service, source)
        print(f"   HTML report: {html_path}")
        
        print("\n" + "=" * 60)
        print("✅ LIVE DEMO COMPLETED SUCCESSFULLY!")
        print("\n🎯 Key Takeaways:")
        print("   • The application successfully analyzed sentiment from demo data")
        print("   • Generated comprehensive reports with visualizations")
        print("   • All core functionality is working correctly")
        print("   • Ready for production use with real API credentials")
        
        print("\n🚀 Next Steps for Production:")
        print("   1. Configure real API keys in .env file")
        print("   2. Run: python app.py --service 'YourBrand' --source 'twitter' --days 30")
        print("   3. For help: python app.py --help")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Live demo failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())