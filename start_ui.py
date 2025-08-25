#!/usr/bin/env python3
"""
CodeObit Web UI Startup Script
Quick launcher for the CodeObit web interface
"""

import sys
import os
import argparse
import webbrowser
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_cors', 
        'flask_socketio',
        'rich',
        'requests',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Please install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def show_banner():
    """Show startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ██╗████████╗
║  ██╔═══████╔═══████╔═══████╔════╝██╔═══████╔══████║╚══██╔══╝
║  ██║   ████║   ████║   ██████████║   ████████████████║   ██║   
║  ██║▄▄ ████║▄▄ ████║▄▄ ██████████║▄▄ ██████╔══████████║   ██║   
║  ╚██████╔╝╚██████╔╝╚██████╔╝███████╚██████╔██████╔╝██║   ██║   
║   ╚══════╝ ╚══════╝ ╚══════╝ ╚══════╝╚══════╝╚══════╝ ╚═╝   ╚═╝   
║                                                           ║
║              AI-Powered Development Environment           ║
║                        Web Interface                      ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='CodeObit Web UI Launcher')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies and exit')
    
    args = parser.parse_args()
    
    show_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_deps:
        print("✅ All dependencies are installed!")
        sys.exit(0)
    
    print("🚀 Starting CodeObit Web UI...")
    print(f"📡 Server: http://{args.host}:{args.port}")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser if not disabled
    if not args.no_browser and args.host in ['localhost', '127.0.0.1']:
        try:
            webbrowser.open(f"http://{args.host}:{args.port}")
            print("🌐 Opening browser...")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
    
    # Import and start the web app
    try:
        from web_app import CodeObitWebApp
        
        app = CodeObitWebApp()
        app.run(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        print("\n\n👋 CodeObit Web UI stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting CodeObit Web UI: {e}")
        print("💡 Try running with --debug for more information")
        sys.exit(1)

if __name__ == "__main__":
    main()