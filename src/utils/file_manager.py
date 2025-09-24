"""
File management utilities for the social media sentiment analysis application.
Handles file operations, CSV exports, and data persistence.
"""
import csv
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

import pandas as pd

from ..config import OUTPUTS_DIR, CSV_SETTINGS
from .logger import get_logger

logger = get_logger(__name__)

class FileManager:
    """File operations manager"""
    
    def __init__(self, base_output_dir: Optional[Path] = None):
        self.base_output_dir = base_output_dir or OUTPUTS_DIR
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_timestamped_folder(self, service: str, source: str) -> Path:
        """Create a timestamped folder for analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{service}_{source}_{timestamp}"
        folder_path = self.base_output_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str, 
                    output_dir: Path, include_timestamp: bool = True) -> Path:
        """Save data to CSV file"""
        try:
            if include_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename}_{timestamp}.csv"
            else:
                filename = f"{filename}.csv"
            
            filepath = output_dir / filename
            
            if not data:
                logger.warning(f"No data to save to {filename}")
                return filepath
            
            # Convert to DataFrame for better CSV handling
            df = pd.DataFrame(data)
            
            # Ensure output directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            df.to_csv(filepath, **CSV_SETTINGS)
            
            logger.info(f"Saved {len(data)} records to {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving CSV file {filename}: {str(e)}")
            raise
    
    def save_json(self, data: Any, filename: str, output_dir: Path) -> Path:
        """Save data to JSON file"""
        try:
            filepath = output_dir / f"{filename}.json"
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Saved JSON data to {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving JSON file {filename}: {str(e)}")
            raise
    
    def save_analysis_report(self, analysis_results: Dict[str, Any], 
                           service: str, source: str) -> Path:
        """Save complete analysis report"""
        try:
            # Create timestamped folder
            output_dir = self.create_timestamped_folder(service, source)
            
            # Save raw data
            if 'raw_data' in analysis_results:
                self.save_to_csv(
                    analysis_results['raw_data'], 
                    'raw_data', 
                    output_dir
                )
            
            # Save processed data with sentiment
            if 'processed_data' in analysis_results:
                self.save_to_csv(
                    analysis_results['processed_data'],
                    'processed_data',
                    output_dir
                )
            
            # Save sentiment summary
            if 'sentiment_summary' in analysis_results:
                self.save_json(
                    analysis_results['sentiment_summary'],
                    'sentiment_summary',
                    output_dir
                )
            
            # Save keywords data
            if 'keywords_data' in analysis_results:
                self.save_to_csv(
                    analysis_results['keywords_data'],
                    'keywords',
                    output_dir
                )
            
            # Save complete report metadata
            report_metadata = {
                'service': service,
                'source': source,
                'analysis_date': datetime.now().isoformat(),
                'parameters': analysis_results.get('parameters', {}),
                'statistics': analysis_results.get('statistics', {}),
                'file_locations': {
                    'raw_data': 'raw_data_*.csv',
                    'processed_data': 'processed_data_*.csv',
                    'sentiment_summary': 'sentiment_summary.json',
                    'keywords': 'keywords_*.csv'
                }
            }
            
            self.save_json(report_metadata, 'report_metadata', output_dir)
            
            logger.info(f"Analysis report saved to {output_dir}")
            return output_dir
            
        except Exception as e:
            logger.error(f"Error saving analysis report: {str(e)}")
            raise
    
    def load_csv(self, filepath: Path) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            return pd.read_csv(filepath, encoding='utf-8-sig')
        except Exception as e:
            logger.error(f"Error loading CSV file {filepath}: {str(e)}")
            raise
    
    def load_json(self, filepath: Path) -> Any:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {str(e)}")
            raise
    
    def get_latest_analysis_folder(self, service: str, source: str) -> Optional[Path]:
        """Get the latest analysis folder for a service/source combination"""
        try:
            pattern = f"{service}_{source}_*"
            matching_folders = list(self.base_output_dir.glob(pattern))
            
            if not matching_folders:
                return None
            
            # Sort by timestamp (folder name contains timestamp)
            return max(matching_folders, key=lambda x: x.name)
            
        except Exception as e:
            logger.error(f"Error finding latest analysis folder: {str(e)}")
            return None
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """Clean up old analysis files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for folder in self.base_output_dir.iterdir():
                if folder.is_dir():
                    folder_date = datetime.fromtimestamp(folder.stat().st_mtime)
                    if folder_date < cutoff_date:
                        import shutil
                        shutil.rmtree(folder)
                        logger.info(f"Removed old folder: {folder.name}")
                        
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")