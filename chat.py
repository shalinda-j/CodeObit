#!/usr/bin/env python3
"""
Quick launcher for codeobit interactive chat mode
"""
import subprocess
import sys

if __name__ == "__main__":
    # Launch interactive mode directly
    subprocess.run([sys.executable, "main.py", "interactive"])