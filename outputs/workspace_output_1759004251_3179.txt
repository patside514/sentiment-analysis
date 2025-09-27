"""
Charts and visualization generator for sentiment analysis results.
Creates various types of charts using matplotlib and seaborn.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

from ..config import VizConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ChartsGenerator:
    """Generate various charts for sentiment analysis"""
    
    def __init__(self, style: str = None):
        self.style = style or VizConfig.PLOT_STYLE
        plt.style.use(self.style)
        self.colors = sns.color_palette(VizConfig.COLOR_PALETTE)
        
    def create_sentiment_pie_chart(self, sentiment_summary: Dict[str, Any], 
                                 title: str = "Sentiment Distribution",
                                 save_path: Optional[str] = None) -> plt.Figure:
        """Create pie chart for sentiment distribution"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Prepare data
            labels = ['Positive', 'Negative', 'Neutral']
            sizes = [
                sentiment_summary['percentages']['positive'],
                sentiment_summary['percentages']['negative'],
                sentiment_summary['percentages']['neutral']
            ]
            colors = ['#2E8B57', '#DC143C', '#808080']  # Green, Red, Gray
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=(0.05, 0.05, 0.05)
            )
            
            # Customize
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            # Style text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
            
            # Add count information
            total = sentiment_summary['total']
            counts = [
                sentiment_summary['positive'],
                sentiment_summary['negative'],
                sentiment_summary['neutral']
            ]
            
            legend_labels = [
                f"{label}: {count} ({size:.1f}%)" 
                for label, count, size in zip(labels, counts, sizes)
            ]
            
            ax.legend(
                wedges, legend_labels,
                title="Sentiment Counts",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1)
            )
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Sentiment pie chart saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment pie chart: {e}")
            return self._create_error_chart("Sentiment Pie Chart")
    
    def create_sentiment_bar_chart(self, sentiment_summary: Dict[str, Any],
                                 title: str = "Sentiment Analysis Results",
                                 save_path: Optional[str] = None) -> plt.Figure:
        """Create bar chart for sentiment analysis"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Left chart: Counts
            sentiments = ['Positive', 'Negative', 'Neutral']
            counts = [
                sentiment_summary['positive'],
                sentiment_summary['negative'],
                sentiment_summary['neutral']
            ]
            colors = ['#2E8B57', '#DC143C', '#808080']
            
            bars1 = ax1.bar(sentiments, counts, color=colors, alpha=0.8)
            ax1.set_title('Sentiment Counts', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Number of Posts')
            
            # Add value labels on bars
            for bar, count in zip(bars1, counts):
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                    f'{count}', ha='center', va='bottom', fontweight='bold'
                )
            
            # Right chart: Percentages
            percentages = [
                sentiment_summary['percentages']['positive'],
                sentiment_summary['percentages']['negative'],
                sentiment_summary['percentages']['neutral']
            ]
            
            bars2 = ax2.bar(sentiments, percentages, color=colors, alpha=0.8)
            ax2.set_title('Sentiment Percentages', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Percentage (%)')
            
            # Add percentage labels
            for bar, pct in zip(bars2, percentages):
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width()/2., height + max(percentages)*0.01,
                    f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold'
                )
            
            # Overall title
            fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
            
            # Add statistics
            stats_text = (
                f"Total Posts: {sentiment_summary['total']}\n"
                f"Avg Polarity: {sentiment_summary.get('average_polarity', 0):.3f}\n"
                f"Avg Confidence: {sentiment_summary.get('average_confidence', 0):.3f}"
            )
            
            fig.text(0.02, 0.02, stats_text, fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5))
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Sentiment bar chart saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment bar chart: {e}")
            return self._create_error_chart("Sentiment Bar Chart")
    
    def create_sentiment_trend_chart(self, temporal_data: List[Dict[str, Any]],
                                   title: str = "Sentiment Trends Over Time",
                                   save_path: Optional[str] = None) -> plt.Figure:
        """Create line chart for sentiment trends"""
        try:
            if not temporal_data:
                return self._create_empty_chart("No temporal data available")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Prepare data
            df = pd.DataFrame(temporal_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Group by date and sentiment
            daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
            
            # Ensure all sentiment columns exist
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment not in daily_sentiment.columns:
                    daily_sentiment[sentiment] = 0
            
            # Calculate percentages
            daily_totals = daily_sentiment.sum(axis=1)
            daily_percentages = daily_sentiment.div(daily_totals, axis=0) * 100
            
            # Plot lines
            colors = {'positive': '#2E8B57', 'negative': '#DC143C', 'neutral': '#808080'}
            
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in daily_percentages.columns:
                    ax.plot(
                        daily_percentages.index,
                        daily_percentages[sentiment],
                        label=sentiment.capitalize(),
                        color=colors[sentiment],
                        linewidth=2,
                        marker='o',
                        markersize=4
                    )
            
            # Customize
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Percentage (%)')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Sentiment trend chart saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment trend chart: {e}")
            return self._create_error_chart("Sentiment Trend Chart")
    
    def create_keyword_frequency_chart(self, keywords: List[Dict[str, Any]],
                                     title: str = "Top Keywords by Frequency",
                                     top_n: int = 20,
                                     save_path: Optional[str] = None) -> plt.Figure:
        """Create horizontal bar chart for keywords"""
        try:
            if not keywords:
                return self._create_empty_chart("No keywords available")
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Sort keywords by frequency
            sorted_keywords = sorted(keywords, key=lambda x: x['frequency'], reverse=True)[:top_n]
            
            # Prepare data
            keyword_names = [kw['keyword'] for kw in reversed(sorted_keywords)]
            frequencies = [kw['frequency'] for kw in reversed(sorted_keywords)]
            
            # Create horizontal bar chart
            bars = ax.barh(keyword_names, frequencies, color=self.colors[0], alpha=0.8)
            
            # Customize
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Frequency')
            
            # Add value labels
            for bar, freq in zip(bars, frequencies):
                width = bar.get_width()
                ax.text(
                    width + max(frequencies)*0.01, bar.get_y() + bar.get_height()/2.,
                    f'{freq}', ha='left', va='center', fontweight='bold'
                )
            
            # Improve layout
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Keyword frequency chart saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating keyword frequency chart: {e}")
            return self._create_error_chart("Keyword Frequency Chart")
    
    def create_keyword_score_chart(self, keywords: List[Dict[str, Any]],
                                 title: str = "Top Keywords by Relevance Score",
                                 top_n: int = 20,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """Create chart for keyword relevance scores"""
        try:
            if not keywords:
                return self._create_empty_chart("No keywords available")
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Sort keywords by score
            sorted_keywords = sorted(keywords, key=lambda x: x['score'], reverse=True)[:top_n]
            
            # Prepare data
            keyword_names = [kw['keyword'] for kw in reversed(sorted_keywords)]
            scores = [kw['score'] for kw in reversed(sorted_keywords)]
            
            # Create horizontal bar chart
            colors = plt.cm.viridis(np.linspace(0, 1, len(scores)))
            bars = ax.barh(keyword_names, scores, color=colors, alpha=0.8)
            
            # Customize
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Relevance Score')
            
            # Add value labels
            for bar, score in zip(bars, scores):
                width = bar.get_width()
                ax.text(
                    width + max(scores)*0.01, bar.get_y() + bar.get_height()/2.,
                    f'{score:.3f}', ha='left', va='center', fontweight='bold'
                )
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Keyword score chart saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating keyword score chart: {e}")
            return self._create_error_chart("Keyword Score Chart")
    
    def create_sentiment_confidence_chart(self, sentiment_results: List[Dict[str, Any]],
                                        title: str = "Sentiment Analysis Confidence Distribution",
                                        save_path: Optional[str] = None) -> plt.Figure:
        """Create histogram for sentiment confidence scores"""
        try:
            if not sentiment_results:
                return self._create_empty_chart("No sentiment results available")
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Extract confidence scores by sentiment
            confidence_by_sentiment = {
                'positive': [r['confidence'] for r in sentiment_results if r['sentiment'] == 'positive'],
                'negative': [r['confidence'] for r in sentiment_results if r['sentiment'] == 'negative'],
                'neutral': [r['confidence'] for r in sentiment_results if r['sentiment'] == 'neutral']
            }
            
            colors = {'positive': '#2E8B57', 'negative': '#DC143C', 'neutral': '#808080'}
            
            # Left chart: Histogram
            for sentiment, confidences in confidence_by_sentiment.items():
                if confidences:
                    ax1.hist(
                        confidences,
                        bins=20,
                        alpha=0.6,
                        label=sentiment.capitalize(),
                        color=colors[sentiment]
                    )
            
            ax1.set_title('Confidence Score Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Confidence Score')
            ax1.set_ylabel('Frequency')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Right chart: Box plot
            confidence_data = []
            labels = []
            
            for sentiment, confidences in confidence_by_sentiment.items():
                if confidences:
                    confidence_data.append(confidences)
                    labels.append(sentiment.capitalize())
            
            if confidence_data:
                box_plot = ax2.boxplot(
                    confidence_data,
                    labels=labels,
                    patch_artist=True
                )
                
                # Color the boxes
                for patch, sentiment in zip(box_plot['boxes'], labels):
                    patch.set_facecolor(colors[sentiment.lower()])
                    patch.set_alpha(0.6)
            
            ax2.set_title('Confidence Score Statistics', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Confidence Score')
            ax2.grid(True, alpha=0.3)
            
            # Overall title
            fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Sentiment confidence chart saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating sentiment confidence chart: {e}")
            return self._create_error_chart("Sentiment Confidence Chart")
    
    def create_overall_summary_chart(self, analysis_results: Dict[str, Any],
                                   title: str = "Analysis Summary Dashboard",
                                   save_path: Optional[str] = None) -> plt.Figure:
        """Create comprehensive summary dashboard"""
        try:
            fig = plt.figure(figsize=(16, 10))
            
            # Create grid layout
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
            
            # 1. Sentiment pie chart (top left)
            ax1 = fig.add_subplot(gs[0, 0])
            self._create_mini_pie_chart(ax1, analysis_results.get('sentiment_summary', {}))
            
            # 2. Keyword bar chart (top middle)
            ax2 = fig.add_subplot(gs[0, 1])
            self._create_mini_keyword_chart(ax2, analysis_results.get('keywords', [])[:10])
            
            # 3. Statistics text (top right)
            ax3 = fig.add_subplot(gs[0, 2])
            self._create_stats_text(ax3, analysis_results)
            
            # 4. Sentiment trend (middle, spans 2 columns)
            ax4 = fig.add_subplot(gs[1, :2])
            self._create_mini_trend_chart(ax4, analysis_results.get('temporal_data', []))
            
            # 5. Top keywords list (middle right)
            ax5 = fig.add_subplot(gs[1, 2])
            self._create_keywords_list(ax5, analysis_results.get('keywords', [])[:15])
            
            # 6. Sentiment confidence (bottom, spans all columns)
            ax6 = fig.add_subplot(gs[2, :])
            self._create_mini_confidence_chart(ax6, analysis_results.get('sentiment_results', []))
            
            # Main title
            fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Summary dashboard saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating summary dashboard: {e}")
            return self._create_error_chart("Analysis Summary Dashboard")
    
    def _create_mini_pie_chart(self, ax, sentiment_summary: Dict[str, Any]):
        """Create mini pie chart for dashboard"""
        try:
            if not sentiment_summary:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Sentiment Distribution', fontsize=12, fontweight='bold')
                return
            
            sizes = [
                sentiment_summary['percentages']['positive'],
                sentiment_summary['percentages']['negative'],
                sentiment_summary['percentages']['neutral']
            ]
            colors = ['#2E8B57', '#DC143C', '#808080']
            
            ax.pie(sizes, labels=['Pos', 'Neg', 'Neu'], colors=colors, autopct='%1.0f%%')
            ax.set_title('Sentiment Distribution', fontsize=12, fontweight='bold')
            
        except Exception as e:
            logger.error(f"Error creating mini pie chart: {e}")
    
    def _create_mini_keyword_chart(self, ax, keywords: List[Dict[str, Any]]):
        """Create mini keyword chart for dashboard"""
        try:
            if not keywords:
                ax.text(0.5, 0.5, 'No Keywords', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Top Keywords', fontsize=12, fontweight='bold')
                return
            
            top_keywords = keywords[:8]
            names = [kw['keyword'][:15] for kw in top_keywords]  # Truncate long keywords
            scores = [kw['score'] for kw in top_keywords]
            
            bars = ax.barh(names, scores, color=self.colors[1], alpha=0.7)
            ax.set_title('Top Keywords', fontsize=12, fontweight='bold')
            ax.set_xlabel('Score')
            
            # Remove spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        except Exception as e:
            logger.error(f"Error creating mini keyword chart: {e}")
    
    def _create_stats_text(self, ax, analysis_results: Dict[str, Any]):
        """Create statistics text box for dashboard"""
        try:
            stats = []
            
            if 'sentiment_summary' in analysis_results:
                sentiment = analysis_results['sentiment_summary']
                stats.extend([
                    f"Total Posts: {sentiment['total']}",
                    f"Avg Polarity: {sentiment.get('average_polarity', 0):.3f}",
                    f"Avg Confidence: {sentiment.get('average_confidence', 0):.3f}"
                ])
            
            if 'extraction_stats' in analysis_results:
                extraction = analysis_results['extraction_stats']
                stats.extend([
                    f"Extracted: {extraction['posts_extracted']}",
                    f"Success Rate: {extraction.get('success_rate', 0):.1f}%"
                ])
            
            if not stats:
                stats = ['No statistics available']
            
            ax.text(0.1, 0.9, '\n'.join(stats), transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
            
            ax.set_title('Statistics', fontsize=12, fontweight='bold')
            ax.axis('off')
            
        except Exception as e:
            logger.error(f"Error creating stats text: {e}")
            ax.text(0.5, 0.5, 'Error loading stats', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Statistics', fontsize=12, fontweight='bold')
            ax.axis('off')
    
    def _create_mini_trend_chart(self, ax, temporal_data: List[Dict[str, Any]]):
        """Create mini trend chart for dashboard"""
        try:
            if not temporal_data:
                ax.text(0.5, 0.5, 'No Temporal Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Sentiment Trends', fontsize=12, fontweight='bold')
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(temporal_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Group by date
            daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
            
            # Plot
            colors = {'positive': '#2E8B57', 'negative': '#DC143C', 'neutral': '#808080'}
            
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in daily_sentiment.columns:
                    ax.plot(
                        daily_sentiment.index,
                        daily_sentiment[sentiment],
                        label=sentiment.capitalize(),
                        color=colors[sentiment],
                        linewidth=1.5
                    )
            
            ax.set_title('Sentiment Trends', fontsize=12, fontweight='bold')
            ax.set_ylabel('Count')
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            
        except Exception as e:
            logger.error(f"Error creating mini trend chart: {e}")
            ax.text(0.5, 0.5, 'Error creating trend', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Sentiment Trends', fontsize=12, fontweight='bold')
    
    def _create_keywords_list(self, ax, keywords: List[Dict[str, Any]]):
        """Create keywords list for dashboard"""
        try:
            if not keywords:
                ax.text(0.5, 0.5, 'No Keywords', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Keywords List', fontsize=12, fontweight='bold')
                ax.axis('off')
                return
            
            # Create text list
            keyword_text = []
            for i, kw in enumerate(keywords[:20], 1):
                keyword_text.append(f"{i:2d}. {kw['keyword'][:25]} ({kw['frequency']})")
            
            ax.text(0.05, 0.95, '\n'.join(keyword_text), transform=ax.transAxes,
                   fontsize=8, verticalalignment='top', fontfamily='monospace')
            
            ax.set_title('Keywords List', fontsize=12, fontweight='bold')
            ax.axis('off')
            
        except Exception as e:
            logger.error(f"Error creating keywords list: {e}")
            ax.text(0.5, 0.5, 'Error loading keywords', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Keywords List', fontsize=12, fontweight='bold')
            ax.axis('off')
    
    def _create_mini_confidence_chart(self, ax, sentiment_results: List[Dict[str, Any]]):
        """Create mini confidence chart for dashboard"""
        try:
            if not sentiment_results:
                ax.text(0.5, 0.5, 'No Confidence Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Confidence Distribution', fontsize=12, fontweight='bold')
                return
            
            # Extract confidence scores
            confidences = [r.get('confidence', 0) for r in sentiment_results]
            
            # Create histogram
            ax.hist(confidences, bins=20, color=self.colors[2], alpha=0.7, edgecolor='black')
            ax.set_title('Confidence Distribution', fontsize=12, fontweight='bold')
            ax.set_xlabel('Confidence Score')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_conf = np.mean(confidences)
            ax.axvline(mean_conf, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_conf:.3f}')
            ax.legend()
            
        except Exception as e:
            logger.error(f"Error creating mini confidence chart: {e}")
            ax.text(0.5, 0.5, 'Error creating confidence chart', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Confidence Distribution', fontsize=12, fontweight='bold')
    
    def _create_error_chart(self, title: str) -> plt.Figure:
        """Create error chart when data is unavailable"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Error creating chart\nData unavailable', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=14, color='red')
        ax.set_title(f'{title} - Error', fontsize=14, fontweight='bold')
        ax.axis('off')
        return fig
    
    def _create_empty_chart(self, message: str) -> plt.Figure:
        """Create empty chart with message"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', transform=ax.transAxes,
               fontsize=14, color='gray')
        ax.axis('off')
        return fig
    
    def save_all_charts(self, analysis_results: Dict[str, Any], output_dir: str):
        """Save all charts to output directory"""
        try:
            import os
            
            # Create sentiment pie chart
            if 'sentiment_summary' in analysis_results:
                self.create_sentiment_pie_chart(
                    analysis_results['sentiment_summary'],
                    save_path=os.path.join(output_dir, 'sentiment_pie_chart.png')
                )
            
            # Create sentiment bar chart
            if 'sentiment_summary' in analysis_results:
                self.create_sentiment_bar_chart(
                    analysis_results['sentiment_summary'],
                    save_path=os.path.join(output_dir, 'sentiment_bar_chart.png')
                )
            
            # Create keyword charts
            if 'keywords' in analysis_results:
                self.create_keyword_frequency_chart(
                    analysis_results['keywords'],
                    save_path=os.path.join(output_dir, 'keyword_frequency_chart.png')
                )
                
                self.create_keyword_score_chart(
                    analysis_results['keywords'],
                    save_path=os.path.join(output_dir, 'keyword_score_chart.png')
                )
            
            # Create sentiment trend chart
            if 'temporal_data' in analysis_results:
                self.create_sentiment_trend_chart(
                    analysis_results['temporal_data'],
                    save_path=os.path.join(output_dir, 'sentiment_trend_chart.png')
                )
            
            # Create overall summary dashboard
            self.create_overall_summary_chart(
                analysis_results,
                save_path=os.path.join(output_dir, 'analysis_dashboard.png')
            )
            
            logger.info(f"All charts saved to {output_dir}")
            
        except Exception as e:
            logger.error(f"Error saving charts: {e}")