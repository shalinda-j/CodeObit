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
    
    def add_parser(self, subparsers):
        """Add database command parser"""
        parser = subparsers.add_parser('database', help='Database management, migrations, and backups')
        
        db_subparsers = parser.add_subparsers(dest='db_action', help='Database actions')
        
        # Init command
        init_parser = db_subparsers.add_parser('init', help='Initialize database and run migrations')
        init_parser.add_argument('--db-type', choices=['sqlite', 'postgresql', 'mongodb'], 
                                default='sqlite', help='Database type to initialize')
        init_parser.add_argument('--connection-string', help='Custom database connection string')
        init_parser.add_argument('--force', action='store_true', help='Force initialization even if database exists')
        
        # Migrate command
        migrate_parser = db_subparsers.add_parser('migrate', help='Run pending database migrations')
        
        # Rollback command
        rollback_parser = db_subparsers.add_parser('rollback', help='Rollback database migrations')
        rollback_parser.add_argument('--target', help='Target migration version to rollback to')
        
        # Status command
        status_parser = db_subparsers.add_parser('status', help='Show database and migration status')
        
        # Backup command
        backup_parser = db_subparsers.add_parser('backup', help='Create database backup')
        backup_parser.add_argument('--output', '-o', help='Backup file path')
        backup_parser.add_argument('--format', choices=['sql', 'json'], default='json', help='Backup format')
        
        # Restore command
        restore_parser = db_subparsers.add_parser('restore', help='Restore database from backup')
        restore_parser.add_argument('backup_file', help='Backup file to restore from')
        restore_parser.add_argument('--format', choices=['sql', 'json'], help='Backup format (auto-detected if not specified)')
        restore_parser.add_argument('--force', action='store_true', help='Force restore even if data exists')
    
    def execute(self, args, config_manager, console):
        """Execute database command"""
        self.console = console
        
        if not hasattr(args, 'db_action') or not args.db_action:
            self.console.print("[red]No database action specified. Use --help for available actions.[/red]")
            return
        
        if args.db_action == 'init':
            self.init_database(args)
        elif args.db_action == 'migrate':
            self.migrate_database(args)
        elif args.db_action == 'rollback':
            self.rollback_database(args)
        elif args.db_action == 'status':
            self.database_status(args)
        elif args.db_action == 'backup':
            self.backup_database(args)
        elif args.db_action == 'restore':
            self.restore_database(args)
        else:
            self.console.print(f"[red]Unknown database action: {args.db_action}[/red]")
    
    def init_database(self, args):
        """Initialize database and run migrations"""
        try:
            db_type = args.db_type
            self.console.print(f"[blue]Initializing {db_type} database...[/blue]")
            
            # Create database manager
            db_manager = get_database_manager(args.connection_string, db_type)
            
            # Initialize migration manager
            migration_manager = MigrationManager(db_manager)
            
            # Check current status
            status = migration_manager.status()
            
            if status['applied_count'] > 0 and not args.force:
                self.console.print(f"[yellow]Database already initialized with {status['applied_count']} migrations applied.[/yellow]")
                self.console.print("[yellow]Use --force to reinitialize.[/yellow]")
                return
            
            # Run migrations
            self.console.print("[green]Running database migrations...[/green]")
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
            
            self.console.print(table)
            self.console.print(f"[green]✅ Database successfully initialized![/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to initialize database: {e}[/red]")
    
    def migrate_database(self, args):
        """Run pending database migrations"""
        try:
            self.console.print("[blue]Running database migrations...[/blue]")
            
            db_manager = get_database_manager()
            migration_manager = MigrationManager(db_manager)
            
            # Show current status
            status = migration_manager.status()
            
            if status['pending_count'] == 0:
                self.console.print("[green]✅ No pending migrations. Database is up to date.[/green]")
                return
            
            self.console.print(f"[yellow]Found {status['pending_count']} pending migrations:[/yellow]")
            for version in status['pending_migrations']:
                migration_info = status['migration_details'][version]
                self.console.print(f"  • {version}: {migration_info['description']}")
            
            # Run migrations
            migration_manager.migrate()
            
            self.console.print("[green]✅ All migrations applied successfully![/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Migration failed: {e}[/red]")
    
    def rollback_database(self, args):
        """Rollback database migrations"""
        try:
            db_manager = get_database_manager()
            migration_manager = MigrationManager(db_manager)
            
            status = migration_manager.status()
            
            if status['applied_count'] == 0:
                self.console.print("[yellow]No migrations to rollback.[/yellow]")
                return
            
            if args.target:
                self.console.print(f"[blue]Rolling back to migration {args.target}...[/blue]")
            else:
                self.console.print("[blue]Rolling back last migration...[/blue]")
            
            migration_manager.rollback(args.target)
            
            self.console.print("[green]✅ Rollback completed successfully![/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Rollback failed: {e}[/red]")
    
    def database_status(self, args):
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
            
            self.console.print(Panel(status_text, title="Database Status", border_style="blue"))
            
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
            
            self.console.print(migration_table)
            
            # Summary
            summary_text = Text()
            summary_text.append(f"Total Migrations: {migration_status['total_migrations']}\n", style="white")
            summary_text.append(f"Applied: {migration_status['applied_count']}\n", style="green")
            summary_text.append(f"Pending: {migration_status['pending_count']}\n", style="yellow")
            
            self.console.print(Panel(summary_text, title="Migration Summary", border_style="green"))
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to get database status: {e}[/red]")
    
    def backup_database(self, args):
        """Create database backup"""
        try:
            import json
            from datetime import datetime
            from pathlib import Path
            
            output = args.output
            format = args.format
            
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = f"codeobit_backup_{timestamp}.{format}"
            
            self.console.print(f"[blue]Creating database backup: {output}[/blue]")
            
            db_manager = get_database_manager()
            
            if format == 'json':
                # JSON backup - export all data
                backup_data = {}
                tables = ['users', 'projects', 'code_generations', 'auto_saves', 'project_analysis']
                
                for table in tables:
                    try:
                        records = db_manager.find_records(table)
                        backup_data[table] = records
                        self.console.print(f"  • Exported {len(records)} records from {table}")
                    except Exception as e:
                        self.console.print(f"  [yellow]Warning: Failed to backup {table}: {e}[/yellow]")
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
            
            self.console.print(f"[green]✅ Backup created successfully: {output}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Backup failed: {e}[/red]")
    
    def restore_database(self, args):
        """Restore database from backup"""
        try:
            from pathlib import Path
            import json
            
            backup_file = args.backup_file
            format = args.format
            force = args.force
            
            backup_path = Path(backup_file)
            if not backup_path.exists():
                raise Exception(f"Backup file not found: {backup_file}")
            
            # Auto-detect format if not specified
            if not format:
                format = 'json' if backup_path.suffix.lower() == '.json' else 'sql'
            
            self.console.print(f"[blue]Restoring database from: {backup_file}[/blue]")
            self.console.print(f"[blue]Format: {format.upper()}[/blue]")
            
            db_manager = get_database_manager()
            
            # Check if database has data
            stats = db_manager.get_stats()
            has_data = any(stats.get(f'{table}_count', 0) > 0 for table in ['users', 'projects', 'code_generations'])
            
            if has_data and not force:
                self.console.print("[yellow]Database contains data. Use --force to overwrite.[/yellow]")
                return
            
            if format == 'json':
                # JSON restore
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                # Clear existing data if force
                if force and has_data:
                    self.console.print("[yellow]Clearing existing data...[/yellow]")
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
                    self.console.print(f"  • Restoring {len(records)} records to {table}")
                    for record in records:
                        try:
                            # Remove id to let database auto-generate
                            if 'id' in record:
                                del record['id']
                            db_manager.insert_record(table, record)
                        except Exception as e:
                            self.console.print(f"    [yellow]Warning: Failed to restore record: {e}[/yellow]")
            
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
            
            self.console.print(f"[green]✅ Database restored successfully from {backup_file}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Restore failed: {e}[/red]")
