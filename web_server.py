#!/usr/bin/env python3
"""
CodeObit Web Server
Standalone web server for the CodeObit AI-powered development environment
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.web.app import CodeObitWebApp

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('codeobit_web.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point for the CodeObit Web Server"""
    parser = argparse.ArgumentParser(
        description="CodeObit Web Server - AI-Powered Development Environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_server.py                    # Start server on default port 5000
  python web_server.py --port 8080       # Start server on port 8080
  python web_server.py --host 0.0.0.0    # Allow external connections
  python web_server.py --debug           # Enable debug mode
        """
    )
    
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind the server to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port', 
        type=int,
        default=5000,
        help='Port to bind the server to (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    try:
        # Setup logging
        log_level = getattr(logging, args.log_level.upper())
        setup_logging(log_level)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting CodeObit Web Server...")
        
        # Create and run the web application
        web_app = CodeObitWebApp()
        
        # Print startup information
        print("\n" + "="*60)
        print("🚀 CodeObit Web Server Starting...")
        print("="*60)
        print(f"📍 URL: http://{args.host}:{args.port}")
        print(f"🔧 Debug Mode: {'Enabled' if args.debug else 'Disabled'}")
        print(f"📝 Log Level: {args.log_level}")
        print("="*60)
        print("Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        # Run the server
        web_app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()