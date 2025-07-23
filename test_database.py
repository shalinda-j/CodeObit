#!/usr/bin/env python3
"""
Test script for codeobit database functionality
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.database import DatabaseManager, MigrationManager, get_database_manager
from cli.database.models import User, Project, CodeGeneration

def test_database():
    """Test database functionality"""
    print("🔧 Testing codeobit database functionality...")
    
    try:
        # Initialize database
        print("\n1. Initializing database...")
        db_manager = get_database_manager()
        print(f"✅ Database initialized: {db_manager.db_type}")
        
        # Test migrations
        print("\n2. Testing migrations...")
        migration_manager = MigrationManager(db_manager)
        migration_manager.migrate()
        print("✅ Migrations completed")
        
        # Test migration status
        status = migration_manager.status()
        print(f"✅ Migration status: {status['applied_count']}/{status['total_migrations']} applied")
        
        # Test database stats
        print("\n3. Testing database stats...")
        stats = db_manager.get_stats()
        print(f"✅ Database stats: {stats}")
        
        # Test model operations
        print("\n4. Testing model operations...")
        
        # Create a test user
        user = User(
            username="test_user",
            email="test@example.com",
            api_key="test_key"
        )
        user_id = user.save()
        print(f"✅ Created user with ID: {user_id}")
        
        # Create a test project
        project = Project(
            name="Test Project",
            description="A test project for database validation",
            project_type="web",
            user_id=user_id
        )
        project_id = project.save()
        print(f"✅ Created project with ID: {project_id}")
        
        # Create a test code generation
        code_gen = CodeGeneration(
            project_id=project_id,
            specification="Create a simple hello world function",
            language="python",
            generated_code="def hello_world():\n    return 'Hello, World!'",
            tokens_used=50
        )
        code_gen_id = code_gen.save()
        print(f"✅ Created code generation with ID: {code_gen_id}")
        
        # Test finding records
        print("\n5. Testing record retrieval...")
        found_user = User.find_by_id(user_id)
        print(f"✅ Found user: {found_user.username}")
        
        found_project = Project.find_by_id(project_id)
        print(f"✅ Found project: {found_project.name}")
        
        # Test relationships
        project_user = found_project.get_user()
        print(f"✅ Project owner: {project_user.username}")
        
        user_projects = Project.find_by_user(user_id)
        print(f"✅ User has {len(user_projects)} projects")
        
        # Test updating
        print("\n6. Testing record updates...")
        found_project.description = "Updated description"
        found_project.save()
        print("✅ Updated project description")
        
        # Test database stats after operations
        final_stats = db_manager.get_stats()
        print(f"\n7. Final database stats:")
        print(f"   Users: {final_stats.get('users_count', 0)}")
        print(f"   Projects: {final_stats.get('projects_count', 0)}")
        print(f"   Code Generations: {final_stats.get('code_generations_count', 0)}")
        
        print("\n🎉 All database tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
