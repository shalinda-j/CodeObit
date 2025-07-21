"""
File management utilities for the AI Software Engineer CLI
"""

import os
import json
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Handles file operations for the CLI application"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the file manager
        
        Args:
            base_path: Base directory for file operations (defaults to current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.ensure_directory(self.base_path)
    
    def ensure_directory(self, path: Path) -> None:
        """
        Ensure directory exists, create if it doesn't
        
        Args:
            path: Directory path to ensure
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise
    
    def read_file(self, file_path: str) -> str:
        """
        Read content from a file
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            str: File content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If file reading fails
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> None:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write
            create_dirs: Create parent directories if they don't exist
            
        Raises:
            Exception: If file writing fails
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if create_dirs:
                self.ensure_directory(path.parent)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Successfully wrote file: {path}")
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise
    
    def read_json(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dict[str, Any]: Parsed JSON data
            
        Raises:
            Exception: If JSON reading or parsing fails
        """
        try:
            content = self.read_file(file_path)
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise Exception(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to read JSON file {file_path}: {e}")
            raise
    
    def write_json(self, file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
        """
        Write data to JSON file
        
        Args:
            file_path: Path to the JSON file
            data: Data to write
            indent: JSON indentation
            
        Raises:
            Exception: If JSON writing fails
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            self.write_file(file_path, content)
        except Exception as e:
            logger.error(f"Failed to write JSON file {file_path}: {e}")
            raise
    
    def read_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse YAML file
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dict[str, Any]: Parsed YAML data
            
        Raises:
            Exception: If YAML reading or parsing fails
        """
        try:
            content = self.read_file(file_path)
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in file {file_path}: {e}")
            raise Exception(f"Invalid YAML format: {e}")
        except Exception as e:
            logger.error(f"Failed to read YAML file {file_path}: {e}")
            raise
    
    def write_yaml(self, file_path: str, data: Dict[str, Any]) -> None:
        """
        Write data to YAML file
        
        Args:
            file_path: Path to the YAML file
            data: Data to write
            
        Raises:
            Exception: If YAML writing fails
        """
        try:
            content = yaml.dump(data, default_flow_style=False, indent=2)
            self.write_file(file_path, content)
        except Exception as e:
            logger.error(f"Failed to write YAML file {file_path}: {e}")
            raise
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    def directory_exists(self, dir_path: str) -> bool:
        """
        Check if directory exists
        
        Args:
            dir_path: Directory path to check
            
        Returns:
            bool: True if directory exists, False otherwise
        """
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path
            return path.exists() and path.is_dir()
        except Exception:
            return False
    
    def list_files(self, directory: str = ".", pattern: str = "*", 
                   recursive: bool = False) -> List[str]:
        """
        List files in directory
        
        Args:
            directory: Directory to search in
            pattern: File pattern to match
            recursive: Search recursively
            
        Returns:
            List[str]: List of file paths
        """
        try:
            path = Path(directory)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                return []
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            return [str(f.relative_to(self.base_path)) for f in files if f.is_file()]
            
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    def copy_file(self, source: str, destination: str) -> None:
        """
        Copy file from source to destination
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Raises:
            Exception: If file copying fails
        """
        try:
            import shutil
            
            src_path = Path(source)
            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            
            dst_path = Path(destination)
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path
            
            self.ensure_directory(dst_path.parent)
            shutil.copy2(src_path, dst_path)
            
            logger.info(f"Successfully copied {source} to {destination}")
            
        except Exception as e:
            logger.error(f"Failed to copy file {source} to {destination}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> None:
        """
        Delete a file
        
        Args:
            file_path: Path to file to delete
            
        Raises:
            Exception: If file deletion fails
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if path.exists():
                path.unlink()
                logger.info(f"Successfully deleted file: {path}")
            else:
                logger.warning(f"File not found for deletion: {path}")
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            int: File size in bytes
            
        Raises:
            Exception: If file size cannot be determined
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            return path.stat().st_size
            
        except Exception as e:
            logger.error(f"Failed to get file size for {file_path}: {e}")
            raise
    
    def create_backup(self, file_path: str, backup_suffix: str = ".backup") -> str:
        """
        Create a backup of a file
        
        Args:
            file_path: Path to file to backup
            backup_suffix: Suffix to add to backup file
            
        Returns:
            str: Path to backup file
            
        Raises:
            Exception: If backup creation fails
        """
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            backup_path = path.with_suffix(path.suffix + backup_suffix)
            self.copy_file(str(path), str(backup_path))
            
            return str(backup_path.relative_to(self.base_path))
            
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            raise
    
    def get_project_files(self, extensions: Optional[List[str]] = None) -> List[str]:
        """
        Get all project files with specified extensions
        
        Args:
            extensions: List of file extensions to include (e.g., ['.py', '.js'])
            
        Returns:
            List[str]: List of project file paths
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.rs']
        
        all_files = []
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = self.list_files(".", pattern, recursive=True)
            all_files.extend(files)
        
        # Filter out common build/dependency directories
        excluded_dirs = {'node_modules', '__pycache__', '.git', '.venv', 'venv', 'build', 'dist', '.pytest_cache'}
        
        filtered_files = []
        for file_path in all_files:
            path_parts = Path(file_path).parts
            if not any(excluded_dir in path_parts for excluded_dir in excluded_dirs):
                filtered_files.append(file_path)
        
        return filtered_files
