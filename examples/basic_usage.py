#!/usr/bin/env python3
"""
Basic usage examples for CodeObit CLI
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.core import AISoftwareEngineerCLI


def main():
    """Demonstrate basic CLI usage"""
    
    print("🚀 CodeObit CLI - Basic Usage Examples")
    print("=" * 50)
    
    # Initialize CLI
    cli = AISoftwareEngineerCLI()
    
    # Show welcome message
    print("\n1. Welcome Message:")
    cli.show_welcome()
    
    # Show available commands
    print("\n2. Available Commands:")
    for command_name in cli.commands.keys():
        command = cli.commands[command_name]
        print(f"   - {command_name}: {command.__class__.__doc__ or 'No description available'}")
    
    print("\n3. Example Usage:")
    print("   # Interactive mode")
    print("   python main.py interactive")
    print()
    print("   # Generate code")
    print('   python main.py code generate --input "Create a Python function" --language Python')
    print()
    print("   # Analyze requirements")
    print('   python main.py requirements generate --input "Build a web app"')
    print()
    print("   # Browse web resources")
    print('   python main.py browse "https://docs.python.org"')
    
    print("\n✨ Ready to start coding with AI assistance!")


if __name__ == '__main__':
    main()
