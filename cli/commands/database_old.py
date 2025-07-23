"""
Database management commands for codeobit CLI
Handles database initialization, migrations, and maintenance
"""

import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from cli.database import DatabaseManager, MigrationManager, get_database_manager
from cli.utils.config import ConfigManager

logger = logging.getLogger(__name__)

class DatabaseCommand:
    """Database management commands"""
    
    def __init__(self):
        self.console = Console()

@database_group.command('init')
@click.option('--db-type', type=click.Choice(['sqlite', 'postgresql', 'mongodb']), 
              default='sqlite', help='Database type to initialize')
@click.option('--connection-string', help='Custom database connection string')
@click.option('--force', is_flag=True, help='Force initialization even if database exists')
def init_database(db_type, connection_string, force):
    """Initialize database and run migrations"""
    try:
        console.print(f"[blue]Initializing {db_type} database...[/blue]")
        
        # Create database manager
        db_manager = get_database_manager(connection_string, db_type)
        
        # Initialize migration manager
        migration_manager = MigrationManager(db_manager)
        
        # Check current status
        status = migration_manager.status()
        
        if status['applied_count'] > 0 and not force:
            console.print(f"[yellow]Database already initialized with {status['applied_count']} migrations applied.[/yellow]")
            console.print("[yellow]Use --force to reinitialize.[/yellow]")
            return
        
        # Run migrations
        console.print("[green]Running database migrations...[/green]")
        migration_manager.migrate()
        
        # Show final status
        final_status = migration_manager.status()
        
        table = Table(title="Database Initialization Complete")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Database Type", db_type.upper())
        table.add_row("Total Migrations", str(final_status['total_migrations']))
        table.add_row("Applied Migrations", str(final_status['applied_count']))
        table.add_row("Pending Migrations", str(final_status['pending_count']))
        
        console.print(table)
        console.print(f"[green]✅ Database successfully initialized![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize database: {e}[/red]")
        raise click.ClickException(str(e))

@database_group.command('migrate')
def migrate_database():
    """Run pending database migrations"""
    try:
        console.print("[blue]Running database migrations...[/blue]")
        
        db_manager = get_database_manager()
        migration_manager = MigrationManager(db_manager)
        
        # Show current status
        status = migration_manager.status()
        
        if status['pending_count'] == 0:
            console.print("[green]✅ No pending migrations. Database is up to date.[/green]")
            return
        
        console.print(f"[yellow]Found {status['pending_count']} pending migrations:[/yellow]")
        for version in status['pending_migrations']:
            migration_info = status['migration_details'][version]
            console.print(f"  • {version}: {migration_info['description']}")
        
        # Run migrations
        migration_manager.migrate()
        
        console.print("[green]✅ All migrations applied successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Migration failed: {e}[/red]")
        raise click.ClickException(str(e))

@database_group.command('rollback')
@click.option('--target', help='Target migration version to rollback to')
def rollback_database(target):
    """Rollback database migrations"""
    try:
        db_manager = get_database_manager()
        migration_manager = MigrationManager(db_manager)
        
        status = migration_manager.status()
        
        if status['applied_count'] == 0:
            console.print("[yellow]No migrations to rollback.[/yellow]")
            return
        
        if target:
            console.print(f"[blue]Rolling back to migration {target}...[/blue]")
        else:
            console.print("[blue]Rolling back last migration...[/blue]")
        
        migration_manager.rollback(target)
        
        console.print("[green]✅ Rollback completed successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Rollback failed: {e}[/red]")
        raise click.ClickException(str(e))

@database_group.command('status')
def database_status():
    """Show database and migration status"""
    try:
        db_manager = get_database_manager()
        
        # Database connection info
        db_stats = db_manager.get_stats()
        
        # Create status panel
        status_text = Text()
        status_text.append("Database Status\n", style="bold blue")
        status_text.append(f"Type: {db_stats['db_type'].upper()}\n", style="cyan")
        status_text.append(f"Connected: {'✅' if db_stats['is_connected'] else '❌'}\n")
        
        if db_stats['is_connected']:
            status_text.append(f"Users: {db_stats.get('users_count', 0)}\n", style="green")
            status_text.append(f"Projects: {db_stats.get('projects_count', 0)}\n", style="green")
            status_text.append(f"Code Generations: {db_stats.get('code_generations_count', 0)}\n", style="green")
            status_text.append(f"Auto Saves: {db_stats.get('auto_saves_count', 0)}\n", style="green")
            status_text.append(f"Project Analyses: {db_stats.get('project_analysis_count', 0)}\n", style="green")
        
        console.print(Panel(status_text, title="Database Status", border_style="blue"))
        
        # Migration status
        migration_manager = MigrationManager(db_manager)
        migration_status = migration_manager.status()
        
        # Create migration table
        migration_table = Table(title="Migration Status")
        migration_table.add_column("Version", style="cyan")
        migration_table.add_column("Description", style="white")
        migration_table.add_column("Status", style="green")
        
        for version, details in migration_status['migration_details'].items():
            status_icon = "✅" if details['applied'] else "⏳"
            status_text = "Applied" if details['applied'] else "Pending"
            migration_table.add_row(version, details['description'], f"{status_icon} {status_text}")
        
        console.print(migration_table)
        
        # Summary
        summary_text = Text()
        summary_text.append(f"Total Migrations: {migration_status['total_migrations']}\n", style="white")
        summary_text.append(f"Applied: {migration_status['applied_count']}\n", style="green")
        summary_text.append(f"Pending: {migration_status['pending_count']}\n", style="yellow")
        
        console.print(Panel(summary_text, title="Migration Summary", border_style="green"))
        
    except Exception as e:
        console.print(f"[red]❌ Failed to get database status: {e}[/red]")
        raise click.ClickException(str(e))

@database_group.command('backup')
@click.option('--output', '-o', help='Backup file path')
@click.option('--format', type=click.Choice(['sql', 'json']), default='sql', help='Backup format')
def backup_database(output, format):
    """Create database backup"""
    try:
        import json
        from datetime import datetime
        from pathlib import Path
        
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"codeobit_backup_{timestamp}.{format}"
        
        console.print(f"[blue]Creating database backup: {output}[/blue]")
        
        db_manager = get_database_manager()
        
        if format == 'json':
            # JSON backup - export all data
            backup_data = {}
            tables = ['users', 'projects', 'code_generations', 'auto_saves', 'project_analysis']
            
            for table in tables:
                try:
                    records = db_manager.find_records(table)
                    backup_data[table] = records
                    console.print(f"  • Exported {len(records)} records from {table}")
                except Exception as e:
                    console.print(f"  [yellow]Warning: Failed to backup {table}: {e}[/yellow]")
                    backup_data[table] = []
            
            # Save JSON backup
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
        
        elif format == 'sql' and db_manager.db_type == 'sqlite':
            # SQLite backup using .backup command
            import subprocess
            db_path = db_manager.connection_string.replace('sqlite:///', '')
            
            cmd = ['sqlite3', db_path, f'.backup {output}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"SQLite backup failed: {result.stderr}")
        
        else:
            raise Exception(f"Backup format '{format}' not supported for {db_manager.db_type}")
        
        console.print(f"[green]✅ Backup created successfully: {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Backup failed: {e}[/red]")
        raise click.ClickException(str(e))

@database_group.command('restore')
@click.argument('backup_file')
@click.option('--format', type=click.Choice(['sql', 'json']), help='Backup format (auto-detected if not specified)')
@click.option('--force', is_flag=True, help='Force restore even if data exists')
def restore_database(backup_file, format, force):
    """Restore database from backup"""
    try:
        from pathlib import Path
        import json
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise Exception(f"Backup file not found: {backup_file}")
        
        # Auto-detect format if not specified
        if not format:
            format = 'json' if backup_path.suffix.lower() == '.json' else 'sql'
        
        console.print(f"[blue]Restoring database from: {backup_file}[/blue]")
        console.print(f"[blue]Format: {format.upper()}[/blue]")
        
        db_manager = get_database_manager()
        
        # Check if database has data
        stats = db_manager.get_stats()
        has_data = any(stats.get(f'{table}_count', 0) > 0 for table in ['users', 'projects', 'code_generations'])
        
        if has_data and not force:
            console.print("[yellow]Database contains data. Use --force to overwrite.[/yellow]")
            return
        
        if format == 'json':
            # JSON restore
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Clear existing data if force
            if force and has_data:
                console.print("[yellow]Clearing existing data...[/yellow]")
                tables = ['project_analysis', 'auto_saves', 'code_generations', 'projects', 'users']
                for table in tables:
                    try:
                        # This is a simple approach - in production you'd want more sophisticated clearing
                        records = db_manager.find_records(table)
                        for record in records:
                            db_manager.delete_record(table, {'id': record['id']})
                    except:
                        pass
            
            # Restore data
            for table, records in backup_data.items():
                console.print(f"  • Restoring {len(records)} records to {table}")
                for record in records:
                    try:
                        # Remove id to let database auto-generate
                        if 'id' in record:
                            del record['id']
                        db_manager.insert_record(table, record)
                    except Exception as e:
                        console.print(f"    [yellow]Warning: Failed to restore record: {e}[/yellow]")
        
        elif format == 'sql' and db_manager.db_type == 'sqlite':
            # SQLite restore
            import subprocess
            db_path = db_manager.connection_string.replace('sqlite:///', '')
            
            # Disconnect from database
            db_manager.disconnect()
            
            # Restore using sqlite3
            cmd = ['sqlite3', db_path, f'.restore {backup_file}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"SQLite restore failed: {result.stderr}")
            
            # Reconnect
            db_manager.connect()
        
        else:
            raise Exception(f"Restore format '{format}' not supported for {db_manager.db_type}")
        
        console.print(f"[green]✅ Database restored successfully from {backup_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Restore failed: {e}[/red]")
        raise click.ClickException(str(e))
