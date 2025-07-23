#!/usr/bin/env python3
"""
Setup script for CodeObit CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="codeobit",
    version="1.0.0-beta",
    author="CodeObit Development Team",
    author_email="dev@codeobit.dev",
    description="AI-Powered Interactive Development Environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shalinda-j/CodeObit",
    project_urls={
        "Bug Tracker": "https://github.com/shalinda-j/CodeObit/issues",
        "Documentation": "https://github.com/shalinda-j/CodeObit/blob/main/README.md",
        "Source Code": "https://github.com/shalinda-j/CodeObit",
        "Discussions": "https://github.com/shalinda-j/CodeObit/discussions",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.22.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codeobit=main:main",
            "cb=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cli": ["**/*.yaml", "**/*.json", "**/*.txt"],
        "config": ["*.yaml"],
        "examples": ["**/*"],
    },
    keywords=[
        "ai", "cli", "development", "automation", "gemini", 
        "interactive", "code-generation", "assistant", "chatbot"
    ],
    zip_safe=False,
)
