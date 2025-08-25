#!/usr/bin/env python3
"""
CodeObit Web UI Application
A modern web interface for the CodeObit CLI functionality
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import secrets

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.core import AISoftwareEngineerCLI
from cli.utils.config import ConfigManager
from cli.web.controllers.search_controller import SearchController
from cli.commands.project import ProjectCommand
from cli.commands.code import CodeCommand
from cli.commands.design import DesignCommand

class CodeObitWebApp:
    """Main Web Application class"""
    
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder='ui/templates',
                        static_folder='ui/static')
        self.app.config['SECRET_KEY'] = secrets.token_hex(16)
        
        # Enable CORS for development
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})
        
        # Initialize SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize CLI components
        self.cli = AISoftwareEngineerCLI()
        self.config_manager = ConfigManager()
        self.search_controller = SearchController()
        
        # Initialize commands
        self.project_cmd = ProjectCommand()
        self.code_cmd = CodeCommand()
        self.design_cmd = DesignCommand()
        
        self.setup_routes()
        self.setup_socketio_events()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('index.html')
        
        @self.app.route('/chat')
        def chat():
            """AI Chat interface"""
            return render_template('chat.html')
            
        @self.app.route('/projects')
        def projects():
            """Project management interface"""
            return render_template('projects.html')
            
        @self.app.route('/files')
        def files():
            """File explorer interface"""
            return render_template('files.html')
            
        @self.app.route('/settings')
        def settings():
            """Settings and configuration"""
            return render_template('settings.html')
        
        # API Routes
        @self.app.route('/api/chat', methods=['POST'])
        def api_chat():
            """Handle AI chat messages"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                provider = data.get('provider', 'gemini')
                
                if not message:
                    return jsonify({'error': 'Message is required'}), 400
                
                # Process message through CLI
                response = self.process_ai_message(message, provider)
                
                return jsonify({
                    'response': response,
                    'provider': provider,
                    'timestamp': self.get_timestamp()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects', methods=['GET'])
        def api_get_projects():
            """Get list of projects"""
            try:
                # Get projects from the project command
                projects = self.get_projects_list()
                return jsonify({'projects': projects})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects', methods=['POST'])
        def api_create_project():
            """Create a new project"""
            try:
                data = request.get_json()
                project_name = data.get('name', '')
                project_type = data.get('type', 'general')
                
                if not project_name:
                    return jsonify({'error': 'Project name is required'}), 400
                
                result = self.create_project(project_name, project_type)
                return jsonify({'success': True, 'result': result})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/search', methods=['POST'])
        def api_search():
            """Handle web search requests"""
            try:
                data = request.get_json()
                query = data.get('query', '')
                
                if not query:
                    return jsonify({'error': 'Query is required'}), 400
                
                results = self.search_controller.handle_command('search', [query])
                return jsonify({'results': results})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/files/<path:filepath>', methods=['GET'])
        def api_get_file(filepath):
            """Get file content"""
            try:
                full_path = Path(filepath)
                if not full_path.exists():
                    return jsonify({'error': 'File not found'}), 404
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return jsonify({
                    'content': content,
                    'path': str(filepath),
                    'size': full_path.stat().st_size
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config', methods=['GET'])
        def api_get_config():
            """Get current configuration"""
            try:
                config = self.config_manager.get_config()
                return jsonify({'config': config})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config', methods=['POST'])
        def api_update_config():
            """Update configuration"""
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
            emit('status', {'message': 'Connected to CodeObit Web UI'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """Handle real-time chat messages"""
            try:
                message = data.get('message', '')
                provider = data.get('provider', 'gemini')
                
                # Process message and emit response
                response = self.process_ai_message(message, provider)
                emit('chat_response', {
                    'response': response,
                    'provider': provider,
                    'timestamp': self.get_timestamp()
                })
                
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def process_ai_message(self, message, provider='gemini'):
        """Process AI message through the CLI"""
        try:
            from cli.ai.providers import get_provider
            
            # Get API key from config if available
            config = self.config_manager.get_config()
            api_key = config.get(f'{provider}_api_key')
            
            ai_provider = get_provider(provider, api_key)
            if ai_provider:
                response = ai_provider.generate_response(message)
                return response
            else:
                return f"AI Provider '{provider}' not available. Please check your API key configuration in Settings."
                
        except Exception as e:
            logging.error(f"Error processing AI message: {e}")
            return f"I apologize, but I encountered an error while processing your message. Please try again or contact support if the issue persists."
    
    def get_projects_list(self):
        """Get list of projects"""
        try:
            # This would integrate with the actual project command
            projects_dir = Path("projects")
            if not projects_dir.exists():
                return []
            
            projects = []
            for project_path in projects_dir.iterdir():
                if project_path.is_dir():
                    projects.append({
                        'name': project_path.name,
                        'path': str(project_path),
                        'type': 'general',  # You can enhance this to detect project type
                        'created': project_path.stat().st_ctime
                    })
            
            return projects
            
        except Exception as e:
            logging.error(f"Error getting projects list: {e}")
            return []
    
    def create_project(self, name, project_type):
        """Create a new project"""
        try:
            # This would integrate with the actual project creation logic
            projects_dir = Path("projects")
            projects_dir.mkdir(exist_ok=True)
            
            project_path = projects_dir / name
            project_path.mkdir(exist_ok=True)
            
            # Create basic project structure
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)
            
            # Create README
            readme_content = f"# {name}\n\nProject created with CodeObit CLI\n"
            (project_path / "README.md").write_text(readme_content)
            
            return f"Project '{name}' created successfully"
            
        except Exception as e:
            raise Exception(f"Error creating project: {str(e)}")
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the web application"""
        print(f"🚀 Starting CodeObit Web UI on http://{host}:{port}")
        print("💡 Access the web interface to use CodeObit with a modern UI!")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def main():
    """Main entry point for the web application"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CodeObit Web UI')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app = CodeObitWebApp()
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()