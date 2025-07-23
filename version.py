"""
codeobit version information
"""

__version__ = "1.0.0-beta"
__author__ = "codeobit Development Team"
__email__ = "dev@codeobit.dev"
__description__ = "AI-Powered Interactive Development Environment"
__url__ = "https://github.com/yourusername/codeobit-v1"
__license__ = "MIT"

# Release information
RELEASE_TYPE = "Public Beta"
RELEASE_DATE = "2025-01-23"
CODENAME = "Vibe Coding"

# Minimum requirements
MIN_PYTHON_VERSION = "3.11"
SUPPORTED_PLATFORMS = ["Windows", "macOS", "Linux"]

# API versions
GEMINI_API_VERSION = "v1beta"
SUPPORTED_AI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro"
]

def get_version_info():
    """Get formatted version information"""
    return {
        "version": __version__,
        "release_type": RELEASE_TYPE,
        "release_date": RELEASE_DATE,
        "codename": CODENAME,
        "python_requirement": f">= {MIN_PYTHON_VERSION}",
        "platforms": SUPPORTED_PLATFORMS,
        "ai_models": SUPPORTED_AI_MODELS
    }

def get_version_string():
    """Get formatted version string for display"""
    return f"codeobit v{__version__} ({RELEASE_TYPE}) - {CODENAME}"
