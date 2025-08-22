"""
Plugin Loader for CodeObit CLI
Handles dynamic loading and hot-reloading of plugins
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

from .base import PluginBase, PluginMetadata
from .manager import PluginManager

logger = logging.getLogger(__name__)

class PluginFileHandler(FileSystemEventHandler):
    """File system event handler for plugin hot-reloading"""
    
    def __init__(self, plugin_loader):
        self.plugin_loader = plugin_loader
        self.debounce_time = 1.0  # seconds
        self.pending_reloads: Dict[str, float] = {}
        self.reload_lock = threading.Lock()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only handle Python files and plugin manifests
        if file_path.suffix not in ['.py', '.json'] or file_path.name.startswith('.'):
            return
        
        plugin_name = self._get_plugin_name_from_path(file_path)
        if plugin_name:
            with self.reload_lock:
                # Debounce rapid file changes
                current_time = time.time()
                if (plugin_name not in self.pending_reloads or 
                    current_time - self.pending_reloads[plugin_name] > self.debounce_time):
                    
                    self.pending_reloads[plugin_name] = current_time
                    # Schedule reload after debounce period
                    threading.Timer(
                        self.debounce_time, 
                        self._reload_plugin, 
                        args=[plugin_name]
                    ).start()
    
    def _get_plugin_name_from_path(self, file_path: Path) -> Optional[str]:
        """Extract plugin name from file path"""
        # Check if file is in a plugin directory
        for plugin_path in self.plugin_loader.manager.plugin_paths:
            try:
                relative_path = file_path.relative_to(plugin_path)
                # First directory component should be plugin name
                if relative_path.parts:
                    return relative_path.parts[0]
            except ValueError:
                continue
        return None
    
    def _reload_plugin(self, plugin_name: str):
        """Reload a specific plugin"""
        try:
            logger.info(f"Hot-reloading plugin: {plugin_name}")
            self.plugin_loader.manager.reload_plugin(plugin_name)
        except Exception as e:
            logger.error(f"Failed to hot-reload plugin {plugin_name}: {e}")

class PluginLoader:
    """Advanced plugin loader with hot-reloading capabilities"""
    
    def __init__(self, manager: PluginManager):
        self.manager = manager
        self.hot_reload_enabled = False
        self.file_observer: Optional[Observer] = None
        self.file_handler: Optional[PluginFileHandler] = None
        
        # Plugin loading callbacks
        self.load_callbacks: List[Callable[[str], None]] = []
        self.unload_callbacks: List[Callable[[str], None]] = []
    
    def enable_hot_reload(self):
        """Enable hot-reloading of plugins"""
        try:
            if self.hot_reload_enabled:
                return
            
            self.file_handler = PluginFileHandler(self)
            self.file_observer = Observer()
            
            # Watch all plugin paths
            for plugin_path in self.manager.plugin_paths:
                if plugin_path.exists():
                    self.file_observer.schedule(
                        self.file_handler,
                        str(plugin_path),
                        recursive=True
                    )
            
            self.file_observer.start()
            self.hot_reload_enabled = True
            logger.info("Plugin hot-reloading enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable hot-reloading: {e}")
    
    def disable_hot_reload(self):
        """Disable hot-reloading of plugins"""
        if not self.hot_reload_enabled:
            return
        
        try:
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
                self.file_observer = None
            
            self.file_handler = None
            self.hot_reload_enabled = False
            logger.info("Plugin hot-reloading disabled")
            
        except Exception as e:
            logger.error(f"Failed to disable hot-reloading: {e}")
    
    def add_load_callback(self, callback: Callable[[str], None]):
        """Add callback for plugin load events"""
        self.load_callbacks.append(callback)
    
    def add_unload_callback(self, callback: Callable[[str], None]):
        """Add callback for plugin unload events"""
        self.unload_callbacks.append(callback)
    
    def trigger_load_callbacks(self, plugin_name: str):
        """Trigger all load callbacks"""
        for callback in self.load_callbacks:
            try:
                callback(plugin_name)
            except Exception as e:
                logger.error(f"Load callback failed for {plugin_name}: {e}")
    
    def trigger_unload_callbacks(self, plugin_name: str):
        """Trigger all unload callbacks"""
        for callback in self.unload_callbacks:
            try:
                callback(plugin_name)
            except Exception as e:
                logger.error(f"Unload callback failed for {plugin_name}: {e}")
    
    def load_plugin_safe(self, plugin_info: Dict[str, str]) -> bool:
        """Safely load a plugin with error handling and validation"""
        plugin_name = plugin_info.get('name', 'unknown')
        
        try:
            # Validate plugin info
            if not self._validate_plugin_info(plugin_info):
                return False
            
            # Check dependencies
            missing_deps = self._check_dependencies(plugin_info)
            if missing_deps:
                logger.error(f"Plugin {plugin_name} has missing dependencies: {missing_deps}")
                return False
            
            # Load the plugin
            if self.manager.load_plugin(plugin_info):
                self.trigger_load_callbacks(plugin_name)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Safe load failed for plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin_safe(self, plugin_name: str) -> bool:
        """Safely unload a plugin with dependency checking"""
        try:
            # Check if other plugins depend on this one
            dependents = self.manager.registry.get_dependents(plugin_name)
            if dependents:
                logger.warning(f"Plugin {plugin_name} has dependents: {dependents}")
                # Optionally unload dependents first
                for dependent in dependents:
                    if dependent in self.manager.loaded_plugins:
                        self.unload_plugin_safe(dependent)
            
            # Unload the plugin
            if self.manager.unload_plugin(plugin_name):
                self.trigger_unload_callbacks(plugin_name)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Safe unload failed for plugin {plugin_name}: {e}")
            return False
    
    def _validate_plugin_info(self, plugin_info: Dict[str, str]) -> bool:
        """Validate plugin information"""
        required_fields = ['name', 'version', 'type', 'path']
        
        for field in required_fields:
            if field not in plugin_info:
                logger.error(f"Plugin info missing required field: {field}")
                return False
        
        # Validate plugin type
        valid_types = [pt.value for pt in self.manager.registry.PluginType]
        if plugin_info['type'] not in valid_types:
            logger.error(f"Invalid plugin type: {plugin_info['type']}")
            return False
        
        # Validate path exists
        plugin_path = Path(plugin_info['path'])
        if not plugin_path.exists():
            logger.error(f"Plugin path does not exist: {plugin_path}")
            return False
        
        return True
    
    def _check_dependencies(self, plugin_info: Dict[str, str]) -> List[str]:
        """Check if plugin dependencies are available"""
        dependencies = plugin_info.get('dependencies', [])
        missing_deps = []
        
        for dep in dependencies:
            if dep not in self.manager.loaded_plugins:
                missing_deps.append(dep)
        
        return missing_deps
    
    def batch_load_plugins(self, plugin_infos: List[Dict[str, str]]) -> Dict[str, bool]:
        """Load multiple plugins in the correct order"""
        results = {}
        
        # Extract plugin names
        plugin_names = [info['name'] for info in plugin_infos]
        
        # Get correct load order based on dependencies
        load_order = self.manager.registry.get_load_order(plugin_names)
        
        # Create a mapping for quick lookup
        info_map = {info['name']: info for info in plugin_infos}
        
        # Load plugins in dependency order
        for plugin_name in load_order:
            if plugin_name in info_map:
                results[plugin_name] = self.load_plugin_safe(info_map[plugin_name])
            else:
                logger.warning(f"Plugin {plugin_name} not found in provided infos")
                results[plugin_name] = False
        
        return results
    
    def batch_unload_plugins(self, plugin_names: List[str]) -> Dict[str, bool]:
        """Unload multiple plugins in reverse dependency order"""
        results = {}
        
        # Get correct unload order (reverse of load order)
        load_order = self.manager.registry.get_load_order(plugin_names)
        unload_order = list(reversed(load_order))
        
        # Unload plugins in reverse dependency order
        for plugin_name in unload_order:
            results[plugin_name] = self.unload_plugin_safe(plugin_name)
        
        return results
    
    def get_plugin_status(self) -> Dict[str, Dict[str, str]]:
        """Get status of all plugins"""
        status = {}
        
        # Loaded plugins
        for plugin_name, plugin in self.manager.loaded_plugins.items():
            status[plugin_name] = {
                'status': 'loaded',
                'enabled': str(plugin.enabled),
                'type': plugin.metadata.plugin_type.value,
                'version': plugin.metadata.version
            }
        
        # Discovered but not loaded plugins
        discovered = self.manager.discover_plugins()
        for plugin_info in discovered:
            plugin_name = plugin_info['name']
            if plugin_name not in status:
                status[plugin_name] = {
                    'status': 'discovered',
                    'enabled': 'false',
                    'type': plugin_info.get('type', 'unknown'),
                    'version': plugin_info.get('version', 'unknown')
                }
        
        return status
    
    def cleanup(self):
        """Cleanup loader resources"""
        self.disable_hot_reload()
        self.load_callbacks.clear()
        self.unload_callbacks.clear()