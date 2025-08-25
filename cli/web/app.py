"""
CodeObit Web UI - Flask Application
Provides a modern web interface for the AI Software Engineer CLI
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Import CLI components
from cli.core import AISoftwareEngineerCLI
from cli.utils.config import ConfigManager
from cli.commands.code import CodeCommand
from cli.commands.design import DesignCommand
from cli.commands.test import TestCommand
from cli.commands.security import SecurityCommand
from cli.commands.docs import DocsCommand
from cli.commands.project import ProjectCommand

class CodeObitWebApp:
    """Main web application class for CodeObit UI"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'codeobit-dev-secret-key')
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        
        # Initialize extensions
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize CLI components
        self.cli = AISoftwareEngineerCLI()
        self.config_manager = ConfigManager()
        
        # Initialize commands
        self.commands = {
            'code': CodeCommand(),
            'design': DesignCommand(),
            'test': TestCommand(),
            'security': SecurityCommand(),
            'docs': DocsCommand(),
            'project': ProjectCommand()
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self.setup_routes()
        self.setup_socketio_events()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def api_status():
            """API status endpoint"""
            return jsonify({
                'status': 'online',
                'version': '1.0.0-beta',
                'features': list(self.commands.keys())
            })
        
        @self.app.route('/api/commands', methods=['GET'])
        def api_commands():
            """Get available commands"""
            commands_info = {}
            for name, command in self.commands.items():
                commands_info[name] = {
                    'name': name,
                    'description': getattr(command, 'description', f'{name.title()} command'),
                    'help': getattr(command, 'help', f'Execute {name} operations')
                }
            return jsonify(commands_info)
        
        @self.app.route('/api/execute', methods=['POST'])
        def api_execute():
            """Execute a CLI command via API"""
            try:
                data = request.get_json()
                command = data.get('command')
                args = data.get('args', [])
                
                if not command or command not in self.commands:
                    return jsonify({'error': f'Unknown command: {command}'}), 400
                
                # Execute command
                result = self.commands[command].execute(args)
                
                return jsonify({
                    'success': True,
                    'command': command,
                    'result': result
                })
                
            except Exception as e:
                self.logger.error(f"Error executing command: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects', methods=['GET'])
        def api_projects():
            """Get list of projects"""
            try:
                projects_dir = Path('projects')
                if not projects_dir.exists():
                    return jsonify([])
                
                projects = []
                for project_dir in projects_dir.iterdir():
                    if project_dir.is_dir():
                        project_info = {
                            'name': project_dir.name,
                            'path': str(project_dir),
                            'created': project_dir.stat().st_ctime
                        }
                        
                        # Try to read project metadata
                        metadata_file = project_dir / 'project.json'
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                    project_info.update(metadata)
                            except:
                                pass
                        
                        projects.append(project_info)
                
                return jsonify(projects)
                
            except Exception as e:
                self.logger.error(f"Error getting projects: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config', methods=['GET', 'POST'])
        def api_config():
            """Get or update configuration"""
            if request.method == 'GET':
                try:
                    config = self.config_manager.get_config()
                    return jsonify(config)
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            elif request.method == 'POST':
                try:
                    data = request.get_json()
                    self.config_manager.update_config(data)
                    return jsonify({'success': True})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
    
    def setup_socketio_events(self):
        """Setup SocketIO events for real-time communication"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.logger.info('Client connected')
            emit('status', {'message': 'Connected to CodeObit Web UI'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.logger.info('Client disconnected')
        
        @self.socketio.on('execute_command')
        def handle_execute_command(data):
            """Handle real-time command execution"""
            try:
                command = data.get('command')
                args = data.get('args', [])
                
                if not command or command not in self.commands:
                    emit('command_result', {
                        'success': False,
                        'error': f'Unknown command: {command}'
                    })
                    return
                
                # Execute command
                result = self.commands[command].execute(args)
                
                emit('command_result', {
                    'success': True,
                    'command': command,
                    'result': result
                })
                
            except Exception as e:
                self.logger.error(f"Error in real-time command execution: {e}")
                emit('command_result', {
                    'success': False,
                    'error': str(e)
                })
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the web application"""
        self.logger.info(f"Starting CodeObit Web UI on http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def create_app():
    """Factory function to create the Flask app"""
    web_app = CodeObitWebApp()
    return web_app.app

if __name__ == '__main__':
    web_app = CodeObitWebApp()
    web_app.run(debug=True)