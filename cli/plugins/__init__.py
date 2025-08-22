"""
CodeObit Plugin System
Enhanced plugin architecture for extensible functionality
"""

from .base import PluginBase, PluginType, PluginMetadata
from .manager import PluginManager
from .registry import PluginRegistry
from .loader import PluginLoader

__all__ = [
    'PluginBase',
    'PluginType', 
    'PluginMetadata',
    'PluginManager',
    'PluginRegistry',
    'PluginLoader'
]