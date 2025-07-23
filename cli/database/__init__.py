"""
Database module for codeobit CLI
Provides unified database interface with support for multiple database backends
"""

from .manager import DatabaseManager
from .models import BaseModel, User, Project, CodeGeneration, AutoSave
from .migrations import MigrationManager

__all__ = [
    'DatabaseManager',
    'BaseModel',
    'User', 
    'Project',
    'CodeGeneration',
    'AutoSave',
    'MigrationManager'
]
