#!/usr/bin/env python3
"""
AI Software Engineer CLI
A comprehensive AI-powered CLI tool for software engineering workflows using Google Gemini.
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.core import AISoftwareEngineerCLI

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ai_engineer.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point for the AI Software Engineer CLI"""
    try:
        setup_logging()
        cli = AISoftwareEngineerCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
