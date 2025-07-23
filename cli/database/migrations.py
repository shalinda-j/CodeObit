"""
Database migration system for codeobit CLI
Handles database schema changes and versioning
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.now().isoformat()
    
    def up(self, db_manager):
        """Apply migration"""
        raise NotImplementedError
    
    def down(self, db_manager):
        """Rollback migration"""
        raise NotImplementedError

class InitialMigration(Migration):
    """Initial database setup migration"""
    
    def __init__(self):
        super().__init__("001", "Initial database setup")
    
    def up(self, db_manager):
        """Create initial tables"""
        db_manager.create_tables()
        logger.info("Applied initial migration: tables created")
    
    def down(self, db_manager):
        """Drop all tables"""
        if db_manager.db_type in ["sqlite", "postgresql"]:
            tables = ["project_analysis", "auto_saves", "code_generations", "projects", "users"]
            with db_manager.get_connection() as conn:
                for table in tables:
                    try:
                        conn.execute(f"DROP TABLE IF EXISTS {table}")
                        logger.info(f"Dropped table: {table}")
                    except Exception as e:
                        logger.warning(f"Failed to drop table {table}: {e}")
        elif db_manager.db_type == "mongodb":
            with db_manager.get_connection() as conn:
                collections = ["users", "projects", "code_generations", "auto_saves", "project_analysis"]
                for collection in collections:
                    try:
                        conn.database.drop_collection(collection)
                        logger.info(f"Dropped collection: {collection}")
                    except Exception as e:
                        logger.warning(f"Failed to drop collection {collection}: {e}")

class AddIndexesMigration(Migration):
    """Add database indexes for better performance"""
    
    def __init__(self):
        super().__init__("002", "Add performance indexes")
    
    def up(self, db_manager):
        """Add indexes"""
        if db_manager.db_type in ["sqlite", "postgresql"]:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)",
                "CREATE INDEX IF NOT EXISTS idx_code_generations_project_id ON code_generations(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_code_generations_language ON code_generations(language)",
                "CREATE INDEX IF NOT EXISTS idx_auto_saves_save_id ON auto_saves(save_id)",
                "CREATE INDEX IF NOT EXISTS idx_auto_saves_save_type ON auto_saves(save_type)",
                "CREATE INDEX IF NOT EXISTS idx_project_analysis_project_id ON project_analysis(project_id)"
            ]
            
            with db_manager.get_connection() as conn:
                for index_sql in indexes:
                    try:
                        conn.execute(index_sql)
                        logger.info(f"Created index: {index_sql.split()[-1]}")
                    except Exception as e:
                        logger.warning(f"Failed to create index: {e}")
        
        elif db_manager.db_type == "mongodb":
            # MongoDB indexes are created in the main table creation
            logger.info("MongoDB indexes already created during table creation")
    
    def down(self, db_manager):
        """Remove indexes"""
        if db_manager.db_type in ["sqlite", "postgresql"]:
            indexes = [
                "DROP INDEX IF EXISTS idx_projects_user_id",
                "DROP INDEX IF EXISTS idx_projects_status", 
                "DROP INDEX IF EXISTS idx_code_generations_project_id",
                "DROP INDEX IF EXISTS idx_code_generations_language",
                "DROP INDEX IF EXISTS idx_auto_saves_save_id",
                "DROP INDEX IF EXISTS idx_auto_saves_save_type",
                "DROP INDEX IF EXISTS idx_project_analysis_project_id"
            ]
            
            with db_manager.get_connection() as conn:
                for index_sql in indexes:
                    try:
                        conn.execute(index_sql)
                        logger.info(f"Dropped index: {index_sql.split()[-1]}")
                    except Exception as e:
                        logger.warning(f"Failed to drop index: {e}")

class MigrationManager:
    """Database migration manager"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.migrations = [
            InitialMigration(),
            AddIndexesMigration()
        ]
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Create migration tracking table if it doesn't exist"""
        if self.db_manager.db_type in ["sqlite", "postgresql"]:
            create_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(10) UNIQUE NOT NULL,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            with self.db_manager.get_connection() as conn:
                conn.execute(create_sql)
        
        elif self.db_manager.db_type == "mongodb":
            # Create collection if it doesn't exist
            with self.db_manager.get_connection() as conn:
                if "migrations" not in conn.database.list_collection_names():
                    conn.database.create_collection("migrations")
                    conn.database.migrations.create_index("version", unique=True)
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            if self.db_manager.db_type in ["sqlite", "postgresql"]:
                with self.db_manager.get_connection() as conn:
                    results = conn.fetch_all("SELECT version FROM migrations ORDER BY version")
                    return [row['version'] for row in results] if results else []
            
            elif self.db_manager.db_type == "mongodb":
                with self.db_manager.get_connection() as conn:
                    results = conn.get_collection("migrations").find({}, {"version": 1}).sort("version", 1)
                    return [doc["version"] for doc in results]
        
        except Exception as e:
            logger.warning(f"Failed to get applied migrations: {e}")
            return []
    
    def mark_migration_applied(self, migration: Migration):
        """Mark migration as applied"""
        data = {
            "version": migration.version,
            "description": migration.description,
            "applied_at": datetime.now().isoformat()
        }
        
        if self.db_manager.db_type in ["sqlite", "postgresql"]:
            with self.db_manager.get_connection() as conn:
                placeholders = ", ".join(["?" if self.db_manager.db_type == "sqlite" else "%s"] * len(data))
                columns = ", ".join(data.keys())
                query = f"INSERT INTO migrations ({columns}) VALUES ({placeholders})"
                conn.execute(query, tuple(data.values()))
        
        elif self.db_manager.db_type == "mongodb":
            with self.db_manager.get_connection() as conn:
                conn.get_collection("migrations").insert_one(data)
    
    def remove_migration_record(self, version: str):
        """Remove migration record (for rollback)"""
        if self.db_manager.db_type in ["sqlite", "postgresql"]:
            with self.db_manager.get_connection() as conn:
                query = "DELETE FROM migrations WHERE version = ?" if self.db_manager.db_type == "sqlite" else "DELETE FROM migrations WHERE version = %s"
                conn.execute(query, (version,))
        
        elif self.db_manager.db_type == "mongodb":
            with self.db_manager.get_connection() as conn:
                conn.get_collection("migrations").delete_one({"version": version})
    
    def migrate(self):
        """Apply all pending migrations"""
        applied_migrations = set(self.get_applied_migrations())
        pending_migrations = [m for m in self.migrations if m.version not in applied_migrations]
        
        if not pending_migrations:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Applying {len(pending_migrations)} migrations...")
        
        for migration in pending_migrations:
            try:
                logger.info(f"Applying migration {migration.version}: {migration.description}")
                migration.up(self.db_manager)
                self.mark_migration_applied(migration)
                logger.info(f"Successfully applied migration {migration.version}")
            except Exception as e:
                logger.error(f"Failed to apply migration {migration.version}: {e}")
                raise
        
        logger.info("All migrations applied successfully")
    
    def rollback(self, target_version: str = None):
        """Rollback migrations to target version"""
        applied_migrations = self.get_applied_migrations()
        
        if not applied_migrations:
            logger.info("No migrations to rollback")
            return
        
        # Find migrations to rollback
        migrations_to_rollback = []
        for version in reversed(applied_migrations):
            if target_version and version == target_version:
                break
            
            # Find migration object
            migration = next((m for m in self.migrations if m.version == version), None)
            if migration:
                migrations_to_rollback.append(migration)
            
            if not target_version:  # Rollback only one migration if no target specified
                break
        
        if not migrations_to_rollback:
            logger.info("No migrations to rollback")
            return
        
        logger.info(f"Rolling back {len(migrations_to_rollback)} migrations...")
        
        for migration in migrations_to_rollback:
            try:
                logger.info(f"Rolling back migration {migration.version}: {migration.description}")
                migration.down(self.db_manager)
                self.remove_migration_record(migration.version)
                logger.info(f"Successfully rolled back migration {migration.version}")
            except Exception as e:
                logger.error(f"Failed to rollback migration {migration.version}: {e}")
                raise
        
        logger.info("Rollback completed successfully")
    
    def status(self) -> Dict[str, any]:
        """Get migration status"""
        applied_migrations = set(self.get_applied_migrations())
        all_migrations = {m.version: m for m in self.migrations}
        
        return {
            "total_migrations": len(all_migrations),
            "applied_count": len(applied_migrations),
            "pending_count": len(all_migrations) - len(applied_migrations),
            "applied_migrations": sorted(applied_migrations),
            "pending_migrations": [v for v in sorted(all_migrations.keys()) if v not in applied_migrations],
            "migration_details": {
                v: {
                    "description": m.description,
                    "applied": v in applied_migrations
                }
                for v, m in all_migrations.items()
            }
        }
