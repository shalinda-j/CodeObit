"""
Configuration management for the AI Software Engineer CLI
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for the AI Software Engineer CLI"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to configuration file (defaults to config/config.yaml)
        """
        self.config_path = Path(config_path) if config_path else Path("config/config.yaml")
        self.config_data: Dict[str, Any] = {}
        self.defaults = self._get_default_config()
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            'api_key': '',
            'default_model': 'gemini-2.5-flash',
            'pro_model': 'gemini-2.5-pro',
            'project_directory': str(Path.cwd()),
            'output_format': 'rich',
            'logging': {
                'level': 'INFO',
                'file': 'ai_engineer.log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'templates': {
                'directory': 'templates',
                'default_project_template': 'standard'
            },
            'ai': {
                'temperature': 0.7,
                'max_tokens': 4096,
                'timeout': 30
            },
            'project': {
                'default_team_size': 3,
                'default_duration': '12 weeks',
                'default_methodology': 'agile'
            },
            'security': {
                'default_standard': 'OWASP',
                'scan_severity': 'medium',
                'include_dependencies': True
            },
            'documentation': {
                'default_format': 'markdown',
                'include_examples': True,
                'auto_generate_toc': True
            },
            'testing': {
                'default_framework': 'pytest',
                'coverage_target': 80,
                'include_integration_tests': True
            }
        }
    
    def load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load configuration from file
        
        Args:
            config_path: Optional path to configuration file
        """
        if config_path:
            self.config_path = Path(config_path)
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.info("Configuration file not found, using defaults")
                self.config_data = {}
            
            # Merge with defaults
            self.config_data = self._merge_config(self.defaults, self.config_data)
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config_data = self.defaults.copy()
    
    def save_config(self, config_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Save configuration to file
        
        Args:
            config_data: Configuration data to save (uses current config if not provided)
        """
        try:
            data_to_save = config_data if config_data is not None else self.config_data
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data_to_save, f, default_flow_style=False, indent=2)
            
            if config_data is not None:
                self.config_data = self._merge_config(self.defaults, data_to_save)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation like 'ai.temperature')
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        try:
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        try:
            keys = key.split('.')
            config = self.config_data
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
        except Exception as e:
            logger.error(f"Failed to set configuration value {key}: {e}")
            raise
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values
        
        Args:
            updates: Dictionary of configuration updates
        """
        try:
            self.config_data = self._merge_config(self.config_data, updates)
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """
        Check if CLI is properly initialized
        
        Returns:
            bool: True if initialized, False otherwise
        """
        api_key = self.get('api_key') or os.getenv('GEMINI_API_KEY')
        return bool(api_key and self.config_path.exists())
    
    def get_api_key(self) -> Optional[str]:
        """
        Get API key from config or environment
        
        Returns:
            Optional[str]: API key if available
        """
        return self.get('api_key') or os.getenv('GEMINI_API_KEY')
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge configuration dictionaries
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Dict[str, Any]: Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config_data = self.defaults.copy()
    
    def validate_config(self) -> Dict[str, str]:
        """
        Validate current configuration
        
        Returns:
            Dict[str, str]: Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Check API key
        api_key = self.get_api_key()
        if not api_key:
            errors['api_key'] = "API key is required"
        
        # Check project directory
        project_dir = self.get('project_directory')
        if project_dir and not Path(project_dir).exists():
            errors['project_directory'] = f"Project directory does not exist: {project_dir}"
        
        # Check logging level
        log_level = self.get('logging.level')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            errors['logging.level'] = f"Invalid logging level: {log_level}"
        
        # Check AI temperature
        temperature = self.get('ai.temperature')
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 1:
            errors['ai.temperature'] = "Temperature must be a number between 0 and 1"
        
        # Check coverage target
        coverage = self.get('testing.coverage_target')
        if not isinstance(coverage, int) or coverage < 0 or coverage > 100:
            errors['testing.coverage_target'] = "Coverage target must be an integer between 0 and 100"
        
        return errors
    
    def export_config(self, file_path: str) -> None:
        """
        Export current configuration to a file
        
        Args:
            file_path: Path to export file
        """
        try:
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration exported to {export_path}")
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            raise
    
    def import_config(self, file_path: str) -> None:
        """
        Import configuration from a file
        
        Args:
            file_path: Path to import file
        """
        try:
            import_path = Path(file_path)
            
            if not import_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {import_path}")
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = yaml.safe_load(f) or {}
            
            self.config_data = self._merge_config(self.defaults, imported_config)
            self.save_config()
            
            logger.info(f"Configuration imported from {import_path}")
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            raise
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration data
        
        Returns:
            Dict[str, Any]: Complete configuration
        """
        return self.config_data.copy()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a specific configuration section
        
        Args:
            section: Section name
            
        Returns:
            Dict[str, Any]: Section configuration
        """
        return self.get(section, {})
