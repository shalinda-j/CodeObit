"""
Database manager for codeobit CLI
Provides unified interface for multiple database backends (SQLite, PostgreSQL, MongoDB)
"""

import os
import sqlite3
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Base database connection class"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self.is_connected = False
    
    def connect(self):
        """Connect to database"""
        raise NotImplementedError
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
    
    def execute(self, query: str, params: tuple = None):
        """Execute query"""
        raise NotImplementedError
    
    def fetch_one(self, query: str, params: tuple = None):
        """Fetch single result"""
        raise NotImplementedError
    
    def fetch_all(self, query: str, params: tuple = None):
        """Fetch all results"""
        raise NotImplementedError

class SQLiteConnection(DatabaseConnection):
    """SQLite database connection"""
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            # Parse path from connection string
            if self.connection_string.startswith('sqlite:///'):
                db_path = self.connection_string[10:]  # Remove 'sqlite:///'
            else:
                db_path = self.connection_string
            
            # Ensure directory exists
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.is_connected = True
            logger.info(f"Connected to SQLite database: {db_path}")
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            raise
    
    def execute(self, query: str, params: tuple = None):
        """Execute query"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query: str, params: tuple = None):
        """Fetch single result"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None):
        """Fetch all results"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection"""
    
    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.psycopg2 = psycopg2
            self.RealDictCursor = RealDictCursor
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = self.psycopg2.connect(
                self.connection_string,
                cursor_factory=self.RealDictCursor
            )
            self.is_connected = True
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise
    
    def execute(self, query: str, params: tuple = None):
        """Execute query"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query: str, params: tuple = None):
        """Fetch single result"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None):
        """Fetch all results"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

class MongoDBConnection(DatabaseConnection):
    """MongoDB database connection"""
    
    def __init__(self, connection_string: str, database_name: str = "codeobit"):
        super().__init__(connection_string)
        self.database_name = database_name
        self.database = None
        try:
            from pymongo import MongoClient
            self.MongoClient = MongoClient
        except ImportError:
            raise ImportError("pymongo is required for MongoDB support. Install with: pip install pymongo")
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            self.connection = self.MongoClient(self.connection_string)
            self.database = self.connection[self.database_name]
            # Test connection
            self.connection.admin.command('ping')
            self.is_connected = True
            logger.info(f"Connected to MongoDB database: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB database: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        if not self.is_connected:
            raise RuntimeError("Not connected to database")
        return self.database[collection_name]
    
    def execute(self, operation: str, collection: str, document: Dict = None, filter_doc: Dict = None):
        """Execute MongoDB operation"""
        try:
            coll = self.get_collection(collection)
            
            if operation == "insert":
                return coll.insert_one(document)
            elif operation == "find":
                return list(coll.find(filter_doc or {}))
            elif operation == "find_one":
                return coll.find_one(filter_doc or {})
            elif operation == "update":
                return coll.update_one(filter_doc, {"$set": document})
            elif operation == "delete":
                return coll.delete_one(filter_doc)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            logger.error(f"Failed to execute MongoDB operation: {e}")
            raise

class DatabaseManager:
    """Unified database manager supporting multiple backends"""
    
    def __init__(self, connection_string: str = None, db_type: str = "sqlite"):
        """
        Initialize database manager
        
        Args:
            connection_string: Database connection string
            db_type: Database type (sqlite, postgresql, mongodb)
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string or self._get_default_connection_string()
        self.connection: Optional[DatabaseConnection] = None
        self._initialize_connection()
    
    def _get_default_connection_string(self) -> str:
        """Get default connection string based on db_type"""
        if self.db_type == "sqlite":
            db_path = Path.cwd() / ".codeobit" / "database" / "codeobit.db"
            return f"sqlite:///{db_path}"
        elif self.db_type == "postgresql":
            return os.getenv("DATABASE_URL", "postgresql://localhost:5432/codeobit")
        elif self.db_type == "mongodb":
            return os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _initialize_connection(self):
        """Initialize database connection based on type"""
        if self.db_type == "sqlite":
            self.connection = SQLiteConnection(self.connection_string)
        elif self.db_type == "postgresql":
            self.connection = PostgreSQLConnection(self.connection_string)
        elif self.db_type == "mongodb":
            self.connection = MongoDBConnection(self.connection_string)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def connect(self):
        """Connect to database"""
        if not self.connection.is_connected:
            self.connection.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected:
            self.connection.disconnect()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        try:
            self.connect()
            yield self.connection
        finally:
            # Don't disconnect here to allow connection reuse
            pass
    
    def create_tables(self):
        """Create database tables/collections"""
        if self.db_type in ["sqlite", "postgresql"]:
            self._create_sql_tables()
        elif self.db_type == "mongodb":
            self._create_mongo_collections()
    
    def _create_sql_tables(self):
        """Create SQL tables"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                api_key VARCHAR(255),
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                project_type VARCHAR(50),
                status VARCHAR(20) DEFAULT 'active',
                config TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS code_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                specification TEXT NOT NULL,
                language VARCHAR(50),
                framework VARCHAR(100),
                generated_code TEXT,
                status VARCHAR(20) DEFAULT 'completed',
                tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS auto_saves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_id VARCHAR(100) UNIQUE NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                content TEXT,
                save_type VARCHAR(50),
                metadata TEXT,
                size_chars INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS project_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                analysis_data TEXT,
                health_score FLOAT,
                issues_count INTEGER,
                warnings_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            """
        ]
        
        with self.get_connection() as conn:
            for table_sql in tables:
                conn.execute(table_sql)
        
        logger.info("SQL tables created successfully")
    
    def _create_mongo_collections(self):
        """Create MongoDB collections and indexes"""
        collections = [
            "users", "projects", "code_generations", 
            "auto_saves", "project_analysis"
        ]
        
        with self.get_connection() as conn:
            for collection_name in collections:
                # Create collection if it doesn't exist
                if collection_name not in conn.database.list_collection_names():
                    conn.database.create_collection(collection_name)
            
            # Create indexes
            conn.database.users.create_index("username", unique=True)
            conn.database.users.create_index("email", unique=True)
            conn.database.projects.create_index("name")
            conn.database.projects.create_index("user_id")
            conn.database.code_generations.create_index("project_id")
            conn.database.auto_saves.create_index("save_id", unique=True)
            conn.database.project_analysis.create_index("project_id")
        
        logger.info("MongoDB collections created successfully")
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert record into database"""
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            if self.db_type in ["sqlite", "postgresql"]:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" if self.db_type == "sqlite" else "%s"] * len(data))
                query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                cursor = conn.execute(query, tuple(data.values()))
                return cursor.lastrowid
            
            elif self.db_type == "mongodb":
                result = conn.execute("insert", table, data)
                return str(result.inserted_id)
    
    def find_records(self, table: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """Find records in database"""
        with self.get_connection() as conn:
            if self.db_type in ["sqlite", "postgresql"]:
                if filters:
                    where_clause = " AND ".join([f"{k} = ?" if self.db_type == "sqlite" else f"{k} = %s" 
                                               for k in filters.keys()])
                    query = f"SELECT * FROM {table} WHERE {where_clause}"
                    results = conn.fetch_all(query, tuple(filters.values()))
                else:
                    query = f"SELECT * FROM {table}"
                    results = conn.fetch_all(query)
                
                return [dict(row) for row in results] if results else []
            
            elif self.db_type == "mongodb":
                return conn.execute("find", table, filter_doc=filters or {})
    
    def find_record(self, table: str, filters: Dict[str, Any]) -> Optional[Dict]:
        """Find single record in database"""
        with self.get_connection() as conn:
            if self.db_type in ["sqlite", "postgresql"]:
                where_clause = " AND ".join([f"{k} = ?" if self.db_type == "sqlite" else f"{k} = %s" 
                                           for k in filters.keys()])
                query = f"SELECT * FROM {table} WHERE {where_clause}"
                result = conn.fetch_one(query, tuple(filters.values()))
                return dict(result) if result else None
            
            elif self.db_type == "mongodb":
                return conn.execute("find_one", table, filter_doc=filters)
    
    def update_record(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Update record in database"""
        data["updated_at"] = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            if self.db_type in ["sqlite", "postgresql"]:
                set_clause = ", ".join([f"{k} = ?" if self.db_type == "sqlite" else f"{k} = %s" 
                                      for k in data.keys()])
                where_clause = " AND ".join([f"{k} = ?" if self.db_type == "sqlite" else f"{k} = %s" 
                                           for k in filters.keys()])
                query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                conn.execute(query, tuple(data.values()) + tuple(filters.values()))
                return True
            
            elif self.db_type == "mongodb":
                result = conn.execute("update", table, data, filters)
                return result.modified_count > 0
    
    def delete_record(self, table: str, filters: Dict[str, Any]) -> bool:
        """Delete record from database"""
        with self.get_connection() as conn:
            if self.db_type in ["sqlite", "postgresql"]:
                where_clause = " AND ".join([f"{k} = ?" if self.db_type == "sqlite" else f"{k} = %s" 
                                           for k in filters.keys()])
                query = f"DELETE FROM {table} WHERE {where_clause}"
                conn.execute(query, tuple(filters.values()))
                return True
            
            elif self.db_type == "mongodb":
                result = conn.execute("delete", table, filter_doc=filters)
                return result.deleted_count > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            "db_type": self.db_type,
            "connection_string": self.connection_string,
            "is_connected": self.connection.is_connected if self.connection else False
        }
        
        if self.connection and self.connection.is_connected:
            try:
                if self.db_type in ["sqlite", "postgresql"]:
                    tables = ["users", "projects", "code_generations", "auto_saves", "project_analysis"]
                    for table in tables:
                        try:
                            count_result = self.find_records(table, {})
                            stats[f"{table}_count"] = len(count_result) if count_result else 0
                        except:
                            stats[f"{table}_count"] = 0
                
                elif self.db_type == "mongodb":
                    with self.get_connection() as conn:
                        collections = ["users", "projects", "code_generations", "auto_saves", "project_analysis"]
                        for collection in collections:
                            try:
                                count = conn.get_collection(collection).count_documents({})
                                stats[f"{collection}_count"] = count
                            except:
                                stats[f"{collection}_count"] = 0
            except Exception as e:
                logger.warning(f"Failed to get database stats: {e}")
        
        return stats

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager(connection_string: str = None, db_type: str = "sqlite") -> DatabaseManager:
    """Get or create global database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(connection_string, db_type)
        _db_manager.connect()
        _db_manager.create_tables()
    return _db_manager
