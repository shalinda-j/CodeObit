# 🗄️ codeobit Database System

This document outlines the comprehensive database system implemented for the codeobit AI-powered CLI.

## 🎯 Overview

The codeobit database system provides a robust, multi-backend solution for storing and managing project data, user information, code generations, and more. It includes full migration support, backup/restore capabilities, and comprehensive management tools.

## 🏗️ Architecture

### Multi-Database Backend Support
- **SQLite** (default): Lightweight, file-based database perfect for single-user scenarios
- **PostgreSQL**: Enterprise-grade relational database for multi-user environments
- **MongoDB**: NoSQL database for flexible document storage

### Core Components

1. **Database Manager** (`cli/database/manager.py`)
   - Unified interface for all database backends
   - Connection management and pooling
   - CRUD operations abstraction

2. **Models** (`cli/database/models.py`)
   - ORM-like data models with relationships
   - Automatic timestamp management
   - Type-safe data operations

3. **Migration System** (`cli/database/migrations.py`)
   - Version-controlled schema changes
   - Forward and backward migration support
   - Automatic migration tracking

4. **CLI Commands** (`cli/commands/database.py`)
   - User-friendly database management interface
   - Backup and restore capabilities
   - Status monitoring and reporting

## 📊 Data Models

### User
- **Fields**: id, username, email, api_key, preferences, created_at, updated_at
- **Purpose**: Store user account information and preferences
- **Relationships**: One-to-many with Projects

### Project
- **Fields**: id, name, description, project_type, status, config, user_id, created_at, updated_at
- **Purpose**: Represent development projects and their configurations
- **Relationships**: Belongs to User, has many CodeGenerations and ProjectAnalyses

### CodeGeneration
- **Fields**: id, project_id, specification, language, framework, generated_code, status, tokens_used, created_at, updated_at
- **Purpose**: Track AI-generated code and associated metadata
- **Relationships**: Belongs to Project

### AutoSave
- **Fields**: id, save_id, file_path, content, save_type, metadata, size_chars, created_at
- **Purpose**: Store automatic backups of work in progress
- **Relationships**: Independent entity

### ProjectAnalysis
- **Fields**: id, project_id, analysis_data, health_score, issues_count, warnings_count, created_at
- **Purpose**: Store project health metrics and analysis results
- **Relationships**: Belongs to Project

## 🚀 Usage

### Database Initialization
```bash
# Initialize with default SQLite
python main.py database init

# Initialize with PostgreSQL
python main.py database init --db-type postgresql --connection-string "postgresql://user:pass@localhost:5432/codeobit"

# Force reinitialize
python main.py database init --force
```

### Migration Management
```bash
# Run pending migrations
python main.py database migrate

# Check migration status
python main.py database status

# Rollback last migration
python main.py database rollback

# Rollback to specific version
python main.py database rollback --target 001
```

### Backup and Restore
```bash
# Create JSON backup
python main.py database backup --format json --output my_backup.json

# Create SQL backup (SQLite only)
python main.py database backup --format sql

# Restore from backup
python main.py database restore my_backup.json

# Force restore (overwrite existing data)
python main.py database restore my_backup.json --force
```

### Status Monitoring
```bash
# View comprehensive database status
python main.py database status
```

## 🔧 Programmatic Usage

### Using Models
```python
from cli.database.models import User, Project, CodeGeneration

# Create a new user
user = User(username="developer", email="dev@example.com")
user_id = user.save()

# Create a project
project = Project(
    name="My App",
    description="A sample application",
    project_type="web",
    user_id=user_id
)
project_id = project.save()

# Find records
user = User.find_by_username("developer")
projects = Project.find_by_user(user_id)
```

### Using Database Manager
```python
from cli.database import get_database_manager

db = get_database_manager()

# Get database statistics
stats = db.get_stats()
print(f"Connected to {stats['db_type']} database")
print(f"Users: {stats['users_count']}")

# Raw database operations
records = db.find_records("users", {"username": "developer"})
db.insert_record("projects", {"name": "New Project", "description": "..."})
```

## 🔄 Migration System

### Current Migrations

1. **001 - Initial database setup**
   - Creates all core tables with proper relationships
   - Sets up foreign key constraints
   - Establishes initial schema

2. **002 - Add performance indexes**
   - Adds indexes for frequently queried columns
   - Improves query performance for relationships
   - Optimizes search operations

### Adding New Migrations

To add a new migration, create a new class in `cli/database/migrations.py`:

```python
class AddNewFeatureMigration(Migration):
    def __init__(self):
        super().__init__("003", "Add new feature table")
    
    def up(self, db_manager):
        """Apply migration"""
        # Add your migration logic here
        pass
    
    def down(self, db_manager):
        """Rollback migration"""
        # Add your rollback logic here
        pass
```

Then add it to the `MigrationManager.migrations` list.

## 🔐 Security Features

- **Connection Security**: Support for encrypted connections (PostgreSQL/MongoDB)
- **Data Validation**: Type checking and validation at the model level
- **Backup Encryption**: JSON backups can be encrypted (implement as needed)
- **Access Control**: Database-level permissions (when using PostgreSQL/MongoDB)

## 📈 Performance Optimizations

- **Connection Pooling**: Reused database connections
- **Lazy Loading**: Models load related data on demand
- **Indexed Queries**: All frequently accessed columns are indexed
- **Batch Operations**: Support for bulk inserts and updates

## 🧪 Testing

The database system includes comprehensive testing:

```bash
# Run database tests
python test_database.py
```

Test coverage includes:
- ✅ Database connection and initialization
- ✅ Model CRUD operations
- ✅ Migration system functionality  
- ✅ Backup and restore operations
- ✅ Multi-backend compatibility

## 🔮 Future Enhancements

### Planned Features
- **Data Encryption**: Automatic encryption for sensitive fields
- **Sharding Support**: Horizontal scaling for large datasets
- **Caching Layer**: Redis integration for frequently accessed data
- **Audit Logging**: Track all database changes
- **Real-time Sync**: Multi-user collaboration support
- **GraphQL API**: Query interface for external integrations

### Database Backends
- **Planned**: Redis support for caching and session storage
- **Planned**: ClickHouse support for analytics and metrics
- **Planned**: DuckDB support for analytical workloads

## 🎉 Benefits

### For Users
- **Zero Configuration**: Works out of the box with SQLite
- **Scalable**: Easy upgrade path to PostgreSQL or MongoDB
- **Reliable**: Full backup and migration support
- **Fast**: Optimized queries and connection management

### For Developers
- **Type Safe**: Full TypeScript-like safety in Python
- **Flexible**: Easy to extend with new models and relationships
- **Testable**: Comprehensive test coverage and mocking support
- **Maintainable**: Clean separation of concerns and clear APIs

## 📞 Support

The database system is fully integrated with codeobit's logging and error handling:

- Database operations are logged to `ai_engineer.log`
- Connection issues are reported with helpful error messages
- Migration failures include rollback information
- Backup operations provide detailed progress feedback

For additional support or feature requests, refer to the main codeobit documentation or create an issue in the project repository.

---

*This database system powers the entire codeobit ecosystem, providing reliable data persistence for all AI-powered development workflows.* 🚀
