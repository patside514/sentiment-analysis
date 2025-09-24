#!/usr/bin/env python3
"""
Social Media Sentiment Analysis Application
Main entry point for the CLI application.

Usage:
    python app.py --service "Uber" --source "twitter" --days 30
    python app.py -s "Netflix" -src "facebook" -d 15 -m 200
    python app.py --service "Airbnb" --source "google_reviews" --format html
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.cli import main

if __name__ == '__main__':
    main()