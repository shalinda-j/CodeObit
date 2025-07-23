"""
Auto-save functionality for codeobit CLI
Provides automatic saving of generated code, configurations, and project data
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import logging

logger = logging.getLogger(__name__)

class AutoSaveManager:
    """Manages auto-save functionality for the CLI"""
    
    def __init__(self, base_path: Optional[str] = None, interval: int = 30):
        """
        Initialize auto-save manager
        
        Args:
            base_path: Base directory for auto-saves
            interval: Auto-save interval in seconds
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.interval = interval
        self.auto_save_dir = self.base_path / ".codeobit" / "autosave"
        self.auto_save_dir.mkdir(parents=True, exist_ok=True)
        
        self._save_queue: Dict[str, Dict[str, Any]] = {}
        self._save_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        
        # Callbacks for different save types
        self._save_callbacks: Dict[str, Callable] = {}
        
    def start(self):
        """Start the auto-save thread"""
        if self._running:
            return
            
        self._running = True
        self._stop_event.clear()
        self._save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self._save_thread.start()
        logger.info(f"Auto-save started with {self.interval}s interval")
    
    def stop(self):
        """Stop the auto-save thread"""
        if not self._running:
            return
            
        self._running = False
        self._stop_event.set()
        
        if self._save_thread:
            self._save_thread.join(timeout=5)
        
        # Perform final save
        self._perform_saves()
        logger.info("Auto-save stopped")
    
    def register_callback(self, save_type: str, callback: Callable):
        """Register a save callback for a specific type"""
        self._save_callbacks[save_type] = callback
        
    def queue_save(self, save_id: str, content: str, file_path: str, 
                   save_type: str = "code", metadata: Optional[Dict] = None):
        """
        Queue content for auto-save
        
        Args:
            save_id: Unique identifier for the save item
            content: Content to save
            file_path: Target file path
            save_type: Type of save (code, config, project, etc.)
            metadata: Additional metadata
        """
        self._save_queue[save_id] = {
            "content": content,
            "file_path": file_path,
            "save_type": save_type,
            "metadata": metadata or {},
            "timestamp": datetime.now(),
            "modified": True
        }
        logger.debug(f"Queued auto-save for {save_id}")
    
    def save_immediately(self, save_id: str) -> bool:
        """
        Save a specific item immediately
        
        Args:
            save_id: ID of item to save
            
        Returns:
            bool: True if saved successfully
        """
        if save_id not in self._save_queue:
            logger.warning(f"Save ID {save_id} not found in queue")
            return False
        
        item = self._save_queue[save_id]
        return self._save_item(save_id, item)
    
    def save_all_immediately(self) -> Dict[str, bool]:
        """
        Save all queued items immediately
        
        Returns:
            Dict[str, bool]: Results of save operations
        """
        results = {}
        for save_id in list(self._save_queue.keys()):
            results[save_id] = self.save_immediately(save_id)
        return results
    
    def get_auto_save_history(self, save_id: str) -> List[Dict[str, Any]]:
        """
        Get auto-save history for a specific item
        
        Args:
            save_id: Save ID to get history for
            
        Returns:
            List of auto-save entries
        """
        history_file = self.auto_save_dir / f"{save_id}_history.json"
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read auto-save history for {save_id}: {e}")
            return []
    
    def restore_from_auto_save(self, save_id: str, version: Optional[int] = None) -> Optional[str]:
        """
        Restore content from auto-save
        
        Args:
            save_id: Save ID to restore
            version: Specific version to restore (latest if None)
            
        Returns:
            Restored content or None if not found
        """
        history = self.get_auto_save_history(save_id)
        if not history:
            return None
        
        if version is None:
            # Get latest version
            entry = history[-1]
        else:
            # Get specific version
            if version >= len(history):
                logger.warning(f"Version {version} not found for {save_id}")
                return None
            entry = history[version]
        
        auto_save_file = self.auto_save_dir / entry["filename"]
        if not auto_save_file.exists():
            logger.error(f"Auto-save file not found: {auto_save_file}")
            return None
        
        try:
            with open(auto_save_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to restore from auto-save: {e}")
            return None
    
    def cleanup_old_saves(self, max_age_days: int = 7, max_versions: int = 10):
        """
        Clean up old auto-save files
        
        Args:
            max_age_days: Maximum age in days to keep
            max_versions: Maximum versions per save ID to keep
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        for history_file in self.auto_save_dir.glob("*_history.json"):
            save_id = history_file.stem.replace("_history", "")
            history = self.get_auto_save_history(save_id)
            
            if not history:
                continue
            
            # Filter by age and limit versions
            filtered_history = []
            for entry in history:
                entry_date = datetime.fromisoformat(entry["timestamp"])
                if entry_date > cutoff_date:
                    filtered_history.append(entry)
            
            # Keep only latest versions
            filtered_history = filtered_history[-max_versions:]
            
            # Remove old files
            for entry in history:
                if entry not in filtered_history:
                    old_file = self.auto_save_dir / entry["filename"]
                    if old_file.exists():
                        old_file.unlink()
            
            # Update history
            if filtered_history != history:
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_history, f, indent=2)
                logger.info(f"Cleaned up auto-save history for {save_id}")
    
    def _auto_save_loop(self):
        """Main auto-save loop"""
        while self._running and not self._stop_event.wait(self.interval):
            try:
                self._perform_saves()
            except Exception as e:
                logger.error(f"Auto-save loop error: {e}")
    
    def _perform_saves(self):
        """Perform all queued saves"""
        if not self._save_queue:
            return
        
        for save_id in list(self._save_queue.keys()):
            item = self._save_queue[save_id]
            if item.get("modified", False):
                self._save_item(save_id, item)
    
    def _save_item(self, save_id: str, item: Dict[str, Any]) -> bool:
        """
        Save a single item
        
        Args:
            save_id: Unique save identifier
            item: Save item data
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Generate auto-save filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{save_id}_{timestamp}.auto"
            auto_save_path = self.auto_save_dir / filename
            
            # Save content to auto-save location
            with open(auto_save_path, 'w', encoding='utf-8') as f:
                f.write(item["content"])
            
            # Update history
            self._update_history(save_id, {
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "file_path": item["file_path"],
                "save_type": item["save_type"],
                "metadata": item["metadata"],
                "size": len(item["content"])
            })
            
            # ALWAYS save to the target file path
            target_file_path = Path(item["file_path"])
            
            # Handle absolute vs relative paths properly
            if not target_file_path.is_absolute():
                target_file_path = self.base_path / target_file_path
            
            # Ensure target directory exists
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to target file with callback or direct write
            save_type = item["save_type"]
            if save_type in self._save_callbacks:
                try:
                    self._save_callbacks[save_type](str(target_file_path), item["content"])
                    logger.info(f"Saved via callback to {target_file_path}")
                except Exception as e:
                    logger.error(f"Save callback failed for {save_type}: {e}")
                    # Fallback to direct write
                    with open(target_file_path, 'w', encoding='utf-8') as f:
                        f.write(item["content"])
                    logger.info(f"Fallback save to {target_file_path}")
            else:
                # Direct save to target file
                with open(target_file_path, 'w', encoding='utf-8') as f:
                    f.write(item["content"])
                logger.info(f"Direct save to {target_file_path}")
            
            # Mark as saved
            item["modified"] = False
            logger.info(f"Auto-saved {save_id} to both {auto_save_path} and {target_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to auto-save {save_id}: {e}")
            return False
    
    def _update_history(self, save_id: str, entry: Dict[str, Any]):
        """Update auto-save history for a save ID"""
        history_file = self.auto_save_dir / f"{save_id}_history.json"
        
        try:
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.append(entry)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update auto-save history: {e}")

# Global auto-save manager instance
_auto_save_manager: Optional[AutoSaveManager] = None

def get_auto_save_manager() -> AutoSaveManager:
    """Get or create global auto-save manager"""
    global _auto_save_manager
    if _auto_save_manager is None:
        _auto_save_manager = AutoSaveManager()
        _auto_save_manager.start()
    return _auto_save_manager

def auto_save_code(save_id: str, content: str, file_path: str, metadata: Optional[Dict] = None):
    """Convenience function to auto-save code"""
    manager = get_auto_save_manager()
    manager.queue_save(save_id, content, file_path, "code", metadata)

def auto_save_config(save_id: str, content: str, file_path: str, metadata: Optional[Dict] = None):
    """Convenience function to auto-save configuration"""
    manager = get_auto_save_manager()
    manager.queue_save(save_id, content, file_path, "config", metadata)

def auto_save_project(save_id: str, content: str, file_path: str, metadata: Optional[Dict] = None):
    """Convenience function to auto-save project data"""
    manager = get_auto_save_manager()
    manager.queue_save(save_id, content, file_path, "project", metadata)
