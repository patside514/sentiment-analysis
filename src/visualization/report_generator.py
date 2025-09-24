"""
Report generator for sentiment analysis results.
Creates comprehensive HTML and PDF reports with all analysis results.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import base64
import io

try:
    from matplotlib import pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from ..config import OUTPUTS_DIR
from ..utils.logger import get_logger
from .charts_generator import ChartsGenerator
from .wordcloud_generator import WordCloudGenerator

logger = get_logger(__name__)

class ReportGenerator:
    """Generate comprehensive analysis reports"""
    
    def __init__(self):
        self.charts_generator = ChartsGenerator()
        self.wordcloud_generator = WordCloudGenerator()
    
    def generate_html_report(self, analysis_results: Dict[str, Any], 
                           service: str, source: str,
                           save_path: Optional[str] = None) -> str:
        """Generate comprehensive HTML report"""
        try:
            # Generate charts and word clouds
            charts_data = self._generate_charts_data(analysis_results)
            
            # Build HTML content
            html_content = self._build_html_report(
                analysis_results, service, source, charts_data
            )
            
            # Save HTML file
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML report saved to {save_path}")
            else:
                # Save to default location
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_path = OUTPUTS_DIR / f"{service}_{source}_report_{timestamp}.html"
                default_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(default_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML report saved to {default_path}")
                save_path = str(default_path)
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return ""
    
    def generate_pdf_report(self, analysis_results: Dict[str, Any],
                          service: str, source: str,
                          save_path: Optional[str] = None) -> str:
        """Generate PDF report"""
        try:
            # First generate HTML report
            html_path = self.generate_html_report(analysis_results, service, source)
            
            if not html_path:
                return ""
            
            # Convert HTML to PDF (simplified approach)
            # Note: For production, you'd want to use a proper HTML to PDF converter
            # like WeasyPrint, pdfkit, or reportlab
            
            if save_path:
                # Copy HTML content to PDF path (placeholder)
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Save as PDF (this is a placeholder - real implementation would need proper conversion)
                pdf_path = save_path
                with open(pdf_path, 'w', encoding='utf-8') as f:
                    f.write(f"PDF version of report\n\n{html_content[:1000]}...")
                
                logger.info(f"PDF report saved to {pdf_path}")
                return pdf_path
            else:
                # Use HTML path as fallback
                return html_path
                
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return ""
    
    def generate_summary_report(self, analysis_results: Dict[str, Any],
                              service: str, source: str) -> Dict[str, Any]:
        """Generate summary report data"""
        try:
            summary = {
                'metadata': {
                    'service': service,
                    'source': source,
                    'generated_at': datetime.now().isoformat(),
                    'report_version': '1.0'
                },
                'executive_summary': self._generate_executive_summary(analysis_results),
                'detailed_findings': self._generate_detailed_findings(analysis_results),
                'recommendations': self._generate_recommendations(analysis_results),
                'technical_details': self._generate_technical_details(analysis_results)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return {'error': str(e)}
    
    def _build_html_report(self, analysis_results: Dict[str, Any], 
                          service: str, source: str,
                          charts_data: Dict[str, str]) -> str:
        """Build HTML report content"""
        try:
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Extract key data
            sentiment_summary = analysis_results.get('sentiment_summary', {})
            keywords = analysis_results.get('keywords', [])
            temporal_data = analysis_results.get('temporal_data', [])
            extraction_stats = analysis_results.get('extraction_stats', {})
            
            # Build HTML
            html = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Social Media Sentiment Analysis Report - {service}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #2c3e50;
                        text-align: center;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        color: #34495e;
                        border-left: 4px solid #3498db;
                        padding-left: 15px;
                        margin-top: 30px;
                    }}
                    h3 {{
                        color: #2c3e50;
                        margin-top: 25px;
                    }}
                    .summary-box {{
                        background-color: #ecf0f1;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 5px solid #3498db;
                    }}
                    .metric {{
                        display: inline-block;
                        margin: 10px 20px 10px 0;
                        padding: 10px 15px;
                        background-color: #3498db;
                        color: white;
                        border-radius: 5px;
                        font-weight: bold;
                    }}
                    .positive {{ background-color: #27ae60; }}
                    .negative {{ background-color: #e74c3c; }}
                    .neutral {{ background-color: #95a5a6; }}
                    .chart-container {{
                        text-align: center;
                        margin: 20px 0;
                        padding: 15px;
                        background-color: #fafafa;
                        border-radius: 8px;
                    }}
                    .chart-container img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 5px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }}
                    th {{
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    .keyword-list {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        margin: 15px 0;
                    }}
                    .keyword-tag {{
                        background-color: #3498db;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-size: 0.9em;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        color: #7f8c8d;
                        font-size: 0.9em;
                    }}
                    .recommendation {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 5px;
                        padding: 15px;
                        margin: 10px 0;
                    }}
                    .recommendation h4 {{
                        color: #856404;
                        margin-top: 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Social Media Sentiment Analysis Report</h1>
                    <h2 style="text-align: center; color: #3498db;">Service: {service} | Source: {source}</h2>
                    <p style="text-align: center; color: #7f8c8d; font-style: italic;">Generated on {timestamp}</p>
                    
                    <div class="summary-box">
                        <h3>📊 Executive Summary</h3>
                        {self._generate_executive_summary_html(sentiment_summary, keywords)}
                    </div>
                    
                    <h2>🎯 Sentiment Analysis Results</h2>
                    <div class="chart-container">
                        <h3>Sentiment Distribution</h3>
                        {self._get_chart_html(charts_data.get('sentiment_pie'), 'Sentiment Pie Chart')}
                    </div>
                    
                    <div class="chart-container">
                        <h3>Sentiment Breakdown</h3>
                        {self._get_chart_html(charts_data.get('sentiment_bar'), 'Sentiment Bar Chart')}
                    </div>
            """
            
            # Add temporal analysis if available
            if temporal_data:
                html += f"""
                    <div class="chart-container">
                        <h3>Sentiment Trends Over Time</h3>
                        {self._get_chart_html(charts_data.get('sentiment_trend'), 'Sentiment Trend Chart')}
                    </div>
                """
            
            # Add keyword analysis
            if keywords:
                html += f"""
                    <h2>🔑 Keyword Analysis</h2>
                    <div class="chart-container">
                        <h3>Top Keywords by Frequency</h3>
                        {self._get_chart_html(charts_data.get('keyword_frequency'), 'Keyword Frequency Chart')}
                    </div>
                    
                    <div class="chart-container">
                        <h3>Top Keywords by Relevance Score</h3>
                        {self._get_chart_html(charts_data.get('keyword_score'), 'Keyword Score Chart')}
                    </div>
                """
                
                # Add keyword list
                html += self._generate_keyword_list_html(keywords[:20])
            
            # Add word cloud if available
            if 'wordcloud' in charts_data:
                html += f"""
                    <div class="chart-container">
                        <h3>Keywords Word Cloud</h3>
                        {self._get_chart_html(charts_data.get('wordcloud'), 'Keywords Word Cloud')}
                    </div>
                """
            
            # Add technical details
            html += f"""
                    <h2>⚙️ Technical Details</h2>
                    {self._generate_technical_details_html(analysis_results, extraction_stats)}
                    
                    <div class="footer">
                        <p>Generated by Social Media Sentiment Analysis Tool</p>
                        <p>Report generated on {timestamp}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error building HTML report: {e}")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"
    
    def _generate_charts_data(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate charts and convert to base64 for HTML embedding"""
        charts_data = {}
        
        try:
            if MATPLOTLIB_AVAILABLE:
                # Generate sentiment pie chart
                if 'sentiment_summary' in analysis_results:
                    fig = self.charts_generator.create_sentiment_pie_chart(
                        analysis_results['sentiment_summary']
                    )
                    charts_data['sentiment_pie'] = self._figure_to_base64(fig)
                    plt.close(fig)
                
                # Generate sentiment bar chart
                if 'sentiment_summary' in analysis_results:
                    fig = self.charts_generator.create_sentiment_bar_chart(
                        analysis_results['sentiment_summary']
                    )
                    charts_data['sentiment_bar'] = self._figure_to_base64(fig)
                    plt.close(fig)
                
                # Generate sentiment trend chart
                if 'temporal_data' in analysis_results:
                    fig = self.charts_generator.create_sentiment_trend_chart(
                        analysis_results['temporal_data']
                    )
                    charts_data['sentiment_trend'] = self._figure_to_base64(fig)
                    plt.close(fig)
                
                # Generate keyword charts
                if 'keywords' in analysis_results:
                    fig = self.charts_generator.create_keyword_frequency_chart(
                        analysis_results['keywords']
                    )
                    charts_data['keyword_frequency'] = self._figure_to_base64(fig)
                    plt.close(fig)
                    
                    fig = self.charts_generator.create_keyword_score_chart(
                        analysis_results['keywords']
                    )
                    charts_data['keyword_score'] = self._figure_to_base64(fig)
                    plt.close(fig)
                
                # Generate word cloud
                if 'keywords' in analysis_results:
                    wordcloud = self.wordcloud_generator.create_keyword_wordcloud(
                        analysis_results['keywords']
                    )
                    if wordcloud:
                        fig = plt.figure(figsize=(10, 6))
                        plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis('off')
                        plt.title('Keywords Word Cloud', fontsize=14, fontweight='bold')
                        charts_data['wordcloud'] = self._figure_to_base64(fig)
                        plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating charts data: {e}")
        
        return charts_data
    
    def _figure_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        try:
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            img_base64 = base64.b64encode(img_buffer.read()).decode()
            return f'<img src="data:image/png;base64,{img_base64}" alt="Chart" style="max-width: 100%; height: auto;">'
            
        except Exception as e:
            logger.error(f"Error converting figure to base64: {e}")
            return '<p>Error loading chart</p>'
    
    def _get_chart_html(self, chart_data: Optional[str], alt_text: str) -> str:
        """Get HTML for chart with fallback"""
        if chart_data:
            return chart_data
        else:
            return f'<p style="text-align: center; color: gray; font-style: italic;">{alt_text} not available</p>'
    
    def _generate_executive_summary_html(self, sentiment_summary: Dict[str, Any], 
                                       keywords: List[Dict[str, Any]]) -> str:
        """Generate executive summary HTML"""
        if not sentiment_summary:
            return "<p>No sentiment data available for summary.</p>"
        
        total = sentiment_summary.get('total', 0)
        positive_pct = sentiment_summary.get('percentages', {}).get('positive', 0)
        negative_pct = sentiment_summary.get('percentages', {}).get('negative', 0)
        neutral_pct = sentiment_summary.get('percentages', {}).get('neutral', 0)
        avg_polarity = sentiment_summary.get('average_polarity', 0)
        
        # Determine overall sentiment
        if positive_pct > 50:
            overall_sentiment = "predominantly positive"
            sentiment_color = "positive"
        elif negative_pct > 50:
            overall_sentiment = "predominantly negative"
            sentiment_color = "negative"
        else:
            overall_sentiment = "mixed"
            sentiment_color = "neutral"
        
        # Top keywords
        top_keywords = keywords[:5] if keywords else []
        
        html = f"""
            <div style="margin-bottom: 20px;">
                <p><strong>Overall Assessment:</strong> The sentiment analysis reveals a <span class="{sentiment_color}">{overall_sentiment}</span> 
                response to the service across social media platforms.</p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <span class="metric positive">Positive: {positive_pct:.1f}%</span>
                <span class="metric negative">Negative: {negative_pct:.1f}%</span>
                <span class="metric neutral">Neutral: {neutral_pct:.1f}%</span>
                <span class="metric">Total Posts: {total}</span>
            </div>
            
            <div style="margin-bottom: 20px;">
                <p><strong>Average Sentiment Score:</strong> {avg_polarity:.3f} 
                ({'Positive' if avg_polarity > 0.1 else 'Negative' if avg_polarity < -0.1 else 'Neutral'})</p>
            </div>
        """
        
        if top_keywords:
            html += """
            <div>
                <p><strong>Top Keywords:</strong></p>
                <div class="keyword-list">
            """
            for keyword in top_keywords:
                html += f'<span class="keyword-tag">{keyword["keyword"]}</span>'
            html += "</div></div>"
        
        return html
    
    def _generate_keyword_list_html(self, keywords: List[Dict[str, Any]]) -> str:
        """Generate keyword list HTML"""
        if not keywords:
            return ""
        
        html = """
            <h2>📋 Complete Keyword List</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Keyword</th>
                        <th>Frequency</th>
                        <th>Score</th>
                        <th>Method</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, keyword in enumerate(keywords, 1):
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{keyword['keyword']}</strong></td>
                    <td>{keyword['frequency']}</td>
                    <td>{keyword['score']:.3f}</td>
                    <td>{keyword.get('method', 'unknown')}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        """
        
        return html
    
    def _generate_technical_details_html(self, analysis_results: Dict[str, Any], 
                                       extraction_stats: Dict[str, Any]) -> str:
        """Generate technical details HTML"""
        html = "<div class='summary-box'>"
        
        # Extraction statistics
        if extraction_stats:
            html += f"""
                <h4>Data Extraction Statistics</h4>
                <ul>
                    <li>Posts Extracted: {extraction_stats.get('posts_extracted', 0)}</li>
                    <li>Errors Encountered: {extraction_stats.get('errors_count', 0)}</li>
                    <li>Success Rate: {extraction_stats.get('success_rate', 0):.1f}%</li>
                </ul>
            """
        
        # Analysis parameters
        if 'parameters' in analysis_results:
            params = analysis_results['parameters']
            html += f"""
                <h4>Analysis Parameters</h4>
                <ul>
                    <li>Service: {params.get('service', 'Unknown')}</li>
                    <li>Source: {params.get('source', 'Unknown')}</li>
                    <li>Time Period: {params.get('days', 0)} days</li>
                    <li>Max Posts: {params.get('max_posts', 0)}</li>
                </ul>
            """
        
        # Processing details
        html += """
            <h4>Processing Details</h4>
            <ul>
                <li>Sentiment Analysis: Multi-model approach (TextBlob + Transformers)</li>
                <li>Keyword Extraction: Combined TF-IDF, Frequency, and TextRank</li>
                <li>Language Support: French and English</li>
                <li>Data Validation: Comprehensive filtering and cleaning</li>
            </ul>
        """
        
        html += "</div>"
        return html
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        sentiment_summary = analysis_results.get('sentiment_summary', {})
        keywords = analysis_results.get('keywords', [])
        
        if not sentiment_summary:
            return {'error': 'No sentiment data available'}
        
        total = sentiment_summary.get('total', 0)
        positive_pct = sentiment_summary.get('percentages', {}).get('positive', 0)
        negative_pct = sentiment_summary.get('percentages', {}).get('negative', 0)
        avg_polarity = sentiment_summary.get('average_polarity', 0)
        
        # Key insights
        insights = []
        if positive_pct > 60:
            insights.append("Strong positive sentiment indicates good customer satisfaction")
        elif negative_pct > 40:
            insights.append("Significant negative sentiment requires attention")
        
        # Top themes from keywords
        top_keywords = [kw['keyword'] for kw in keywords[:10]] if keywords else []
        
        return {
            'total_posts': total,
            'sentiment_breakdown': {
                'positive': positive_pct,
                'negative': negative_pct,
                'neutral': 100 - positive_pct - negative_pct
            },
            'overall_sentiment': 'positive' if avg_polarity > 0.1 else 'negative' if avg_polarity < -0.1 else 'neutral',
            'key_insights': insights,
            'top_themes': top_keywords
        }
    
    def _generate_detailed_findings(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed findings"""
        findings = []
        
        # Sentiment findings
        if 'sentiment_summary' in analysis_results:
            sentiment = analysis_results['sentiment_summary']
            findings.append({
                'category': 'Sentiment Analysis',
                'finding': f"Overall sentiment is {sentiment.get('average_polarity', 0):.3f} "
                          f"({'positive' if sentiment.get('average_polarity', 0) > 0.1 else 'negative' if sentiment.get('average_polarity', 0) < -0.1 else 'neutral'})",
                'confidence': sentiment.get('average_confidence', 0)
            })
        
        # Keyword findings
        if 'keywords' in analysis_results:
            keywords = analysis_results['keywords'][:5]
            if keywords:
                findings.append({
                    'category': 'Key Themes',
                    'finding': f"Top themes include: {', '.join([kw['keyword'] for kw in keywords])}",
                    'confidence': 0.8
                })
        
        # Temporal findings
        if 'temporal_data' in analysis_results:
            findings.append({
                'category': 'Temporal Analysis',
                'finding': 'Temporal sentiment trends analyzed',
                'confidence': 0.7
            })
        
        return findings
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        sentiment_summary = analysis_results.get('sentiment_summary', {})
        positive_pct = sentiment_summary.get('percentages', {}).get('positive', 0)
        negative_pct = sentiment_summary.get('percentages', {}).get('negative', 0)
        
        if negative_pct > 30:
            recommendations.append({
                'priority': 'high',
                'recommendation': 'Address negative feedback themes identified in keyword analysis',
                'rationale': f'{negative_pct:.1f}% negative sentiment requires attention'
            })
        
        if positive_pct > 70:
            recommendations.append({
                'priority': 'medium',
                'recommendation': 'Leverage positive sentiment in marketing efforts',
                'rationale': 'Strong positive response can be amplified'
            })
        
        recommendations.append({
            'priority': 'medium',
            'recommendation': 'Monitor sentiment trends regularly',
            'rationale': 'Continuous monitoring helps identify emerging issues'
        })
        
        return recommendations
    
    def _generate_technical_details(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical details"""
        return {
            'extraction_method': analysis_results.get('extraction_stats', {}).get('method', 'API + Scraping'),
            'sentiment_models': ['TextBlob', 'Transformers'],
            'keyword_methods': ['TF-IDF', 'Frequency', 'TextRank'],
            'languages_supported': ['French', 'English'],
            'data_validation': 'Comprehensive filtering applied',
            'sample_size': analysis_results.get('sentiment_summary', {}).get('total', 0)
        }