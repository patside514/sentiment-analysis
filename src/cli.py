"""
Command-line interface for the social media sentiment analysis application.
Handles argument parsing, validation, and user interaction.
"""
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

import click
from colorama import init, Fore, Style
from tqdm import tqdm

from .config import AVAILABLE_SOURCES, DEFAULT_SOURCE, AnalysisConfig
from .utils.logger import get_logger, app_logger
from .utils.data_validator import validate_cli_args
from .utils.file_manager import FileManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

logger = get_logger(__name__)

class ColoredFormatter:
    """Color formatter for CLI output"""
    
    COLORS = {
        'info': Fore.BLUE,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'error': Fore.RED,
        'bold': Style.BRIGHT,
        'reset': Style.RESET_ALL
    }
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Apply color to text"""
        return f"{ColoredFormatter.COLORS.get(color, '')}{text}{ColoredFormatter.COLORS['reset']}"
    
    @staticmethod
    def print_colored(text: str, color: str = 'info'):
        """Print colored text"""
        click.echo(ColoredFormatter.colorize(text, color))

@click.command()
@click.option('--service', '-s', 
              required=True,
              help='Service or brand name to analyze (e.g., "Uber", "Netflix")')
@click.option('--source', '-src',
              type=click.Choice(AVAILABLE_SOURCES, case_sensitive=False),
              default=DEFAULT_SOURCE,
              help='Social media source to analyze')
@click.option('--days', '-d',
              type=click.IntRange(1, 60),
              default=AnalysisConfig.DEFAULT_DAYS,
              help='Number of days to analyze (1-60)')
@click.option('--max-posts', '-m',
              type=click.IntRange(AnalysisConfig.MIN_POSTS, AnalysisConfig.MAX_POSTS),
              default=AnalysisConfig.MAX_POSTS,
              help=f'Maximum number of posts to extract ({AnalysisConfig.MIN_POSTS}-{AnalysisConfig.MAX_POSTS})')
@click.option('--output-dir', '-o',
              type=click.Path(path_type=Path),
              default=None,
              help='Output directory for results')
@click.option('--format', '-f',
              type=click.Choice(['csv', 'json', 'html', 'all'], case_sensitive=False),
              default='all',
              help='Output format for results')
@click.option('--language', '-l',
              type=click.Choice(['auto', 'fr', 'en'], case_sensitive=False),
              default='auto',
              help='Language for analysis (auto-detection by default)')
@click.option('--sentiment-model', '-sm',
              type=click.Choice(['auto', 'textblob', 'transformers'], case_sensitive=False),
              default='auto',
              help='Sentiment analysis model to use')
@click.option('--keyword-method', '-km',
              type=click.Choice(['tfidf', 'frequency', 'textrank', 'combined'], case_sensitive=False),
              default='combined',
              help='Keyword extraction method')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose output')
@click.option('--quiet', '-q',
              is_flag=True,
              help='Suppress non-error output')
@click.option('--config-file', '-c',
              type=click.Path(exists=True, path_type=Path),
              help='Configuration file path')
@click.option('--dry-run', '-dr',
              is_flag=True,
              help='Perform a dry run without actual data extraction')
@click.version_option(version='1.0.0', prog_name='Social Media Sentiment Analyzer')

def main(service: str, source: str, days: int, max_posts: int, output_dir: Optional[Path],
         format: str, language: str, sentiment_model: str, keyword_method: str,
         verbose: bool, quiet: bool, config_file: Optional[Path], dry_run: bool):
    """
    Social Media Sentiment Analysis Tool
    
    Extract and analyze sentiment from social media posts about a specific service or brand.
    
    Example usage:
    
    \b
        python app.py --service "Uber" --source "twitter" --days 30
        python app.py -s "Netflix" -src "facebook" -d 15 -m 200
        python app.py --service "Airbnb" --source "google_reviews" --format html
    """
    
    # Setup logging based on verbosity
    if quiet:
        app_logger.logger.setLevel('ERROR')
    elif verbose:
        app_logger.logger.setLevel('DEBUG')
    else:
        app_logger.logger.setLevel('INFO')
    
    # Print banner
    if not quiet:
        print_banner()
    
    # Validate inputs
    validation_result = validate_cli_args(service, source, days, max_posts)
    
    if not validation_result['valid']:
        error_msg = "Validation errors:\n" + "\n".join(f"  - {error}" for error in validation_result['errors'])
        click.echo(ColoredFormatter.colorize(error_msg, 'error'), err=True)
        sys.exit(1)
    
    # Use cleaned values
    cleaned_args = validation_result['cleaned']
    service = cleaned_args['service']
    source = cleaned_args['source']
    
    # Print configuration summary
    if not quiet:
        print_configuration(service, source, days, max_posts, output_dir, format, 
                          language, sentiment_model, keyword_method, config_file)
    
    # Confirm before proceeding (unless quiet mode)
    if not quiet and not dry_run:
        if not click.confirm(ColoredFormatter.colorize("Proceed with analysis?", 'info')):
            click.echo(ColoredFormatter.colorize("Analysis cancelled by user.", 'warning'))
            sys.exit(0)
    
    # Perform dry run if requested
    if dry_run:
        perform_dry_run(service, source, days, max_posts, output_dir, format,
                       language, sentiment_model, keyword_method)
        return
    
    # Run analysis
    try:
        success = run_analysis(service, source, days, max_posts, output_dir, format,
                             language, sentiment_model, keyword_method, quiet)
        
        if success:
            if not quiet:
                click.echo(ColoredFormatter.colorize("✅ Analysis completed successfully!", 'success'))
            sys.exit(0)
        else:
            if not quiet:
                click.echo(ColoredFormatter.colorize("❌ Analysis failed!", 'error'), err=True)
            sys.exit(1)
            
    except KeyboardInterrupt:
        if not quiet:
            click.echo(ColoredFormatter.colorize("\n⚠️ Analysis interrupted by user.", 'warning'))
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        if not quiet:
            click.echo(ColoredFormatter.colorize(f"❌ Unexpected error: {e}", 'error'), err=True)
        sys.exit(1)

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║  🚀 Social Media Sentiment Analysis Tool 🚀                          ║
    ║                                                                       ║
    ║  Extract and analyze sentiment from social media platforms            ║
    ║  Powered by NLP and Machine Learning                                  ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    click.echo(ColoredFormatter.colorize(banner, 'info'))
    click.echo()

def print_configuration(service: str, source: str, days: int, max_posts: int,
                       output_dir: Optional[Path], format: str, language: str,
                       sentiment_model: str, keyword_method: str, config_file: Optional[Path]):
    """Print configuration summary"""
    config_text = f"""
    📋 Configuration Summary:
    
    🔍 Analysis Parameters:
       Service: {ColoredFormatter.colorize(service, 'bold')}
       Source: {ColoredFormatter.colorize(source.upper(), 'bold')}
       Time Period: {ColoredFormatter.colorize(f'{days} days', 'info')}
       Max Posts: {ColoredFormatter.colorize(str(max_posts), 'info')}
    
    ⚙️ Processing Options:
       Language: {ColoredFormatter.colorize(language, 'info')}
       Sentiment Model: {ColoredFormatter.colorize(sentiment_model, 'info')}
       Keyword Method: {ColoredFormatter.colorize(keyword_method, 'info')}
       Output Format: {ColoredFormatter.colorize(format.upper(), 'info')}
    """
    
    if output_dir:
        config_text += f"\n       Output Directory: {ColoredFormatter.colorize(str(output_dir), 'info')}"
    
    if config_file:
        config_text += f"\n       Config File: {ColoredFormatter.colorize(str(config_file), 'info')}"
    
    click.echo(config_text)
    click.echo()

def perform_dry_run(service: str, source: str, days: int, max_posts: int,
                   output_dir: Optional[Path], format: str, language: str,
                   sentiment_model: str, keyword_method: str):
    """Perform dry run simulation"""
    click.echo(ColoredFormatter.colorize("\n🔍 DRY RUN MODE - Simulation Only\n", 'warning'))
    
    # Simulate analysis steps
    steps = [
        "Validating input parameters",
        "Checking API credentials",
        "Estimating data volume",
        "Preparing analysis pipeline",
        "Generating output preview"
    ]
    
    with tqdm(total=len(steps), desc="Simulating analysis", unit="step") as pbar:
        for step in steps:
            pbar.set_description(f"Simulating: {step}")
            time.sleep(0.5)  # Simulate processing time
            pbar.update(1)
    
    # Show preview of what would be generated
    click.echo(f"\n{ColoredFormatter.colorize('📊 Expected Output Preview:', 'info')}")
    click.echo(f"   • CSV files with raw and processed data")
    click.echo(f"   • Sentiment analysis results")
    click.echo(f"   • Keyword extraction results")
    click.echo(f"   • Visualization charts (pie, bar, trend)")
    click.echo(f"   • Word clouds")
    click.echo(f"   • Comprehensive HTML report")
    
    click.echo(f"\n{ColoredFormatter.colorize('✅ Dry run completed successfully!', 'success')}")
    click.echo(f"   Run without --dry-run to perform actual analysis.")

def run_analysis(service: str, source: str, days: int, max_posts: int,
                output_dir: Optional[Path], format: str, language: str,
                sentiment_model: str, keyword_method: str, quiet: bool) -> bool:
    """Run the actual analysis"""
    from .main import SocialMediaAnalyzer
    
    try:
        # Initialize analyzer
        analyzer = SocialMediaAnalyzer()
        
        # Set output directory
        if output_dir:
            file_manager = FileManager(output_dir)
        else:
            file_manager = FileManager()
        
        # Run analysis with progress tracking
        if not quiet:
            click.echo(ColoredFormatter.colorize("\n🚀 Starting analysis...", 'info'))
        
        results = analyzer.analyze(
            service=service,
            source=source,
            days=days,
            max_posts=max_posts,
            language=language,
            sentiment_model=sentiment_model,
            keyword_method=keyword_method,
            progress_callback=lambda msg: logger.info(msg) if not quiet else None
        )
        
        if not results:
            logger.error("Analysis returned no results")
            return False
        
        # Save results
        if not quiet:
            click.echo(ColoredFormatter.colorize("\n💾 Saving results...", 'info'))
        
        output_path = file_manager.save_analysis_report(results, service, source)
        
        # Generate additional formats if requested
        if format != 'csv':  # CSV is already included in the analysis report
            if not quiet:
                click.echo(ColoredFormatter.colorize(f"\n📄 Generating {format.upper()} report...", 'info'))
            
            if format in ['html', 'all']:
                from .visualization.report_generator import ReportGenerator
                report_gen = ReportGenerator()
                html_path = report_gen.generate_html_report(results, service, source)
                if html_path and not quiet:
                    click.echo(ColoredFormatter.colorize(f"   HTML report: {html_path}", 'success'))
        
        if not quiet:
            click.echo(f"\n{ColoredFormatter.colorize('📁 Results saved to:', 'info')} {output_path}")
            click.echo(f"   {ColoredFormatter.colorize('Service:', 'info')} {service}")
            click.echo(f"   {ColoredFormatter.colorize('Source:', 'info')} {source}")
            click.echo(f"   {ColoredFormatter.colorize('Posts analyzed:', 'info')} {results.get('sentiment_summary', {}).get('total', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if not quiet:
            click.echo(ColoredFormatter.colorize(f"❌ Analysis failed: {e}", 'error'), err=True)
        return False

if __name__ == '__main__':
    main()