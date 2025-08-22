# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CodeObit CLI
Builds standalone executables for Windows and Linux
"""

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)
cli_dir = project_root / "cli"
config_dir = project_root / "config"
examples_dir = project_root / "examples"

# Define the main script
main_script = str(project_root / "main.py")

# Data files to include
data_files = [
    # Configuration files
    (str(config_dir / "config.yaml"), "config"),
    
    # CLI templates and data files
    (str(cli_dir / "utils" / "templates.py"), "cli/utils"),
    
    # Examples and templates
    (str(examples_dir), "examples"),
    
    # Any JSON/YAML files in the CLI directory
    (str(cli_dir), "cli"),
]

# Hidden imports - modules that PyInstaller might miss
hidden_imports = [
    # AI providers
    'google.genai',
    'google.auth',
    'google.auth.transport.requests',
    
    # CLI modules
    'cli.core',
    'cli.interactive',
    'cli.commands',
    'cli.commands.base',
    'cli.commands.browse',
    'cli.commands.code',
    'cli.commands.code_review',
    'cli.commands.database',
    'cli.commands.debug',
    'cli.commands.design',
    'cli.commands.devops',
    'cli.commands.docs',
    'cli.commands.learning',
    'cli.commands.project',
    'cli.commands.qa',
    'cli.commands.requirements',
    'cli.commands.security',
    'cli.commands.test',
    'cli.commands.visual_dev',
    'cli.commands.web',
    
    # AI modules
    'cli.ai.gemini_client',
    'cli.ai.learning_system',
    'cli.ai.multi_model_reviewer',
    'cli.ai.multi_provider',
    
    # Utility modules
    'cli.utils.config',
    'cli.utils.file_manager',
    'cli.utils.file_mention',
    'cli.utils.image_handler',
    'cli.utils.project_analyzer',
    'cli.utils.project_manager',
    'cli.utils.templates',
    'cli.utils.auto_save',
    
    # Plugin system
    'cli.plugins.base',
    'cli.plugins.manager',
    'cli.plugins.registry',
    'cli.plugins.loader',
    
    # Models
    'cli.models.project',
    
    # Database
    'cli.database.manager',
    'cli.database.models',
    'cli.database.migrations',
    
    # DevOps
    'cli.devops.ci_cd_generator',
    'cli.devops.docker_generator',
    'cli.devops.infrastructure_generator',
    'cli.devops.kubernetes_generator',
    'cli.devops.pipeline_generator',
    
    # Integrations
    'cli.integrations.aws_integration',
    'cli.integrations.github_integration',
    'cli.integrations.jira_integration',
    'cli.integrations.qwen3_integration',
    'cli.integrations.slack_integration',
    
    # Testing
    'cli.testing.advanced_framework',
    'cli.testing.performance_profiler',
    'cli.testing.visual_tester',
    
    # Web components
    'cli.web.app',
    'cli.web.controllers.search_controller',
    'cli.web.models.search_model',
    'cli.web.presenters.search_presenter',
    
    # Visual designer
    'cli.visual.designer',
    
    # Third-party dependencies that might be missed
    'yaml',
    'json',
    'requests',
    'rich',
    'rich.console',
    'rich.table',
    'rich.panel',
    'rich.progress',
    'rich.syntax',
    'rich.markdown',
    'beautifulsoup4',
    'bs4',
    'selenium',
    'selenium.webdriver',
    'flask',
    'flask_cors',
    'flask_socketio',
    'watchdog',
    'pillow',
    'PIL',
    'numpy',
    'psutil',
    'memory_profiler',
    'scikit-image',
    'skimage',
]

# Exclude modules that are not needed
excludes = [
    # Test modules
    'pytest',
    'unittest',
    'test',
    'tests',
    
    # Development tools
    'black',
    'flake8',
    'mypy',
    'coverage',
    
    # Jupyter/IPython
    'IPython',
    'jupyter',
    'notebook',
    
    # Unnecessary GUI libraries
    'tkinter',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
]

# Analysis configuration
a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove unnecessary files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Determine platform-specific settings
if sys.platform.startswith('win'):
    # Windows-specific settings
    exe_name = 'codeobit.exe'
    icon_file = None  # Add path to .ico file if available
    console = True
elif sys.platform.startswith('linux'):
    # Linux-specific settings
    exe_name = 'codeobit'
    icon_file = None  # Add path to .png file if available
    console = True
else:
    # Default settings
    exe_name = 'codeobit'
    icon_file = None
    console = True

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# Optional: Create a distribution directory (one-folder bundle)
# Uncomment the following lines if you prefer a folder distribution
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='codeobit'
# )