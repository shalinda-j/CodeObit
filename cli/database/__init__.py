"""
Database module for codeobit CLI
Provides unified database interface with support for multiple database backends
"""

from .manager import DatabaseManager, get_database_manager
from .models import BaseModel, User, Project, CodeGeneration, AutoSave
from .migrations import MigrationManager

__all__ = [
    'DatabaseManager',
    'get_database_manager',
    'BaseModel',
    'User', 
    'Project',
    'CodeGeneration',
    'AutoSave',
    'MigrationManager'
]
