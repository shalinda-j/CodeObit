"""
Database models for codeobit CLI
Define data structures and ORM models for project entities
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from cli.database.manager import get_database_manager

@dataclass
class BaseModel:
    """Base model class for all database entities"""
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
        return cls(**data)
    
    def save(self) -> int:
        """Save model to database"""
        db = get_database_manager()
        data = self.to_dict()
        
        # Remove None values and id for insert
        clean_data = {k: v for k, v in data.items() if v is not None}
        if 'id' in clean_data:
            del clean_data['id']
        
        # Convert datetime objects to strings if needed
        for key, value in clean_data.items():
            if isinstance(value, datetime):
                clean_data[key] = value.isoformat()
        
        if self.id:
            # Update existing record
            db.update_record(self._table_name(), {'id': self.id}, clean_data)
            return self.id
        else:
            # Insert new record
            new_id = db.insert_record(self._table_name(), clean_data)
            self.id = new_id
            return new_id
    
    def delete(self) -> bool:
        """Delete model from database"""
        if not self.id:
            return False
            
        db = get_database_manager()
        return db.delete_record(self._table_name(), {'id': self.id})
    
    @classmethod
    def find_by_id(cls, record_id: int):
        """Find record by ID"""
        db = get_database_manager()
        record = db.find_record(cls._table_name(), {'id': record_id})
        return cls.from_dict(record) if record else None
    
    @classmethod
    def find_all(cls, filters: Dict[str, Any] = None) -> List['BaseModel']:
        """Find all records matching filters"""
        db = get_database_manager()
        records = db.find_records(cls._table_name(), filters)
        return [cls.from_dict(record) for record in records]
    
    @classmethod
    def _table_name(cls) -> str:
        """Get table name for this model"""
        return cls.__name__.lower() + 's'

@dataclass
class User(BaseModel):
    """User model"""
    username: str = ""
    email: str = ""
    api_key: Optional[str] = None
    preferences: Optional[str] = None
    
    @classmethod
    def _table_name(cls) -> str:
        return "users"
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences as dictionary"""
        if self.preferences:
            try:
                return json.loads(self.preferences)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_preferences(self, prefs: Dict[str, Any]):
        """Set user preferences from dictionary"""
        self.preferences = json.dumps(prefs)
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """Find user by username"""
        db = get_database_manager()
        record = db.find_record(cls._table_name(), {'username': username})
        return cls.from_dict(record) if record else None
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """Find user by email"""
        db = get_database_manager()
        record = db.find_record(cls._table_name(), {'email': email})
        return cls.from_dict(record) if record else None

@dataclass
class Project(BaseModel):
    """Project model"""
    name: str = ""
    description: Optional[str] = None
    project_type: Optional[str] = None
    status: str = "active"
    config: Optional[str] = None
    user_id: Optional[int] = None
    
    @classmethod
    def _table_name(cls) -> str:
        return "projects"
    
    def get_config(self) -> Dict[str, Any]:
        """Get project config as dictionary"""
        if self.config:
            try:
                return json.loads(self.config)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_config(self, config: Dict[str, Any]):
        """Set project config from dictionary"""
        self.config = json.dumps(config)
    
    def get_user(self) -> Optional[User]:
        """Get associated user"""
        if self.user_id:
            return User.find_by_id(self.user_id)
        return None
    
    @classmethod
    def find_by_user(cls, user_id: int) -> List['Project']:
        """Find all projects for a user"""
        return cls.find_all({'user_id': user_id})
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['Project']:
        """Find project by name"""
        db = get_database_manager()
        record = db.find_record(cls._table_name(), {'name': name})
        return cls.from_dict(record) if record else None

@dataclass
class CodeGeneration(BaseModel):
    """Code generation model"""
    project_id: Optional[int] = None
    specification: str = ""
    language: Optional[str] = None
    framework: Optional[str] = None
    generated_code: Optional[str] = None
    status: str = "completed"
    tokens_used: int = 0
    
    @classmethod
    def _table_name(cls) -> str:
        return "code_generations"
    
    def get_project(self) -> Optional[Project]:
        """Get associated project"""
        if self.project_id:
            return Project.find_by_id(self.project_id)
        return None
    
    @classmethod
    def find_by_project(cls, project_id: int) -> List['CodeGeneration']:
        """Find all code generations for a project"""
        return cls.find_all({'project_id': project_id})
    
    @classmethod
    def find_by_language(cls, language: str) -> List['CodeGeneration']:
        """Find all code generations by language"""
        return cls.find_all({'language': language})

@dataclass
class AutoSave(BaseModel):
    """Auto-save model"""
    save_id: str = ""
    file_path: str = ""
    content: Optional[str] = None
    save_type: Optional[str] = None
    metadata: Optional[str] = None
    size_chars: Optional[int] = None
    
    @classmethod
    def _table_name(cls) -> str:
        return "auto_saves"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata as dictionary"""
        if self.metadata:
            try:
                return json.loads(self.metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set metadata from dictionary"""
        self.metadata = json.dumps(metadata)
    
    @classmethod
    def find_by_save_id(cls, save_id: str) -> Optional['AutoSave']:
        """Find auto-save by save_id"""
        db = get_database_manager()
        record = db.find_record(cls._table_name(), {'save_id': save_id})
        return cls.from_dict(record) if record else None
    
    @classmethod
    def find_by_type(cls, save_type: str) -> List['AutoSave']:
        """Find all auto-saves by type"""
        return cls.find_all({'save_type': save_type})

@dataclass
class ProjectAnalysis(BaseModel):
    """Project analysis model"""
    project_id: Optional[int] = None
    analysis_data: Optional[str] = None
    health_score: Optional[float] = None
    issues_count: Optional[int] = None
    warnings_count: Optional[int] = None
    
    @classmethod
    def _table_name(cls) -> str:
        return "project_analysis"
    
    def get_analysis_data(self) -> Dict[str, Any]:
        """Get analysis data as dictionary"""
        if self.analysis_data:
            try:
                return json.loads(self.analysis_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_analysis_data(self, data: Dict[str, Any]):
        """Set analysis data from dictionary"""
        self.analysis_data = json.dumps(data)
    
    def get_project(self) -> Optional[Project]:
        """Get associated project"""
        if self.project_id:
            return Project.find_by_id(self.project_id)
        return None
    
    @classmethod
    def find_by_project(cls, project_id: int) -> List['ProjectAnalysis']:
        """Find all analyses for a project"""
        return cls.find_all({'project_id': project_id})
