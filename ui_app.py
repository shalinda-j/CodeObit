#!/usr/bin/env python3
"""
CodeObit UI Application
Web-based interface for the CodeObit CLI tool
"""

import os
import sys
import json
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.core import AISoftwareEngineerCLI
from cli.utils.config import ConfigManager
from cli.interactive import InteractiveCLI

# Initialize Flask app
app = Flask(__name__, 
           static_folder='ui/build',
           template_folder='ui/templates')

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ui_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Session storage for active CLI instances
active_sessions = {}

class UICommandHandler:
    """Handler for executing CLI commands from the UI"""
    
    def __init__(self):
        self.cli = AISoftwareEngineerCLI()
        self.config_manager = ConfigManager()
        
    def execute_command(self, command_type, params, session_id):
        """Execute a CLI command and return the result"""
        try:
            if command_type in self.cli.commands:
                command_obj = self.cli.commands[command_type]
                result = command_obj.execute(**params)
                return {
                    'success': True,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command_type}',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Initialize command handler
command_handler = UICommandHandler()

# API Routes
@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0-beta',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/providers')
def get_providers():
    """Get available AI providers"""
    try:
        config = command_handler.config_manager.get_config()
        providers = config.get('providers', {})
        return jsonify({
            'success': True,
            'providers': list(providers.keys()),
            'current': config.get('default_provider', 'gemini')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects')
def get_projects():
    """Get list of projects"""
    try:
        projects_dir = Path.home() / '.ai_engineer' / 'projects'
        if projects_dir.exists():
            projects = [d.name for d in projects_dir.iterdir() if d.is_dir()]
            return jsonify({
                'success': True,
                'projects': projects
            })
        return jsonify({'success': True, 'projects': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a CLI command"""
    try:
        data = request.json
        command_type = data.get('command')
        params = data.get('params', {})
        session_id = session.get('session_id', 'default')
        
        result = command_handler.execute_command(command_type, params, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save file to temporary location
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'path': str(file_path),
            'size': file_path.stat().st_size
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/browse', methods=['POST'])
def browse_url():
    """Browse and summarize a URL"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL required'}), 400
        
        browse_cmd = command_handler.cli.commands.get('browse')
        if browse_cmd:
            result = browse_cmd.execute(url=url)
            return jsonify({
                'success': True,
                'content': result.get('content', ''),
                'summary': result.get('summary', '')
            })
        
        return jsonify({'success': False, 'error': 'Browse command not available'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    session_id = request.sid
    active_sessions[session_id] = {
        'connected_at': datetime.now(),
        'room': session_id
    }
    join_room(session_id)
    emit('connected', {'session_id': session_id})
    logger.info(f"Client connected: {session_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    if session_id in active_sessions:
        leave_room(session_id)
        del active_sessions[session_id]
    logger.info(f"Client disconnected: {session_id}")

@socketio.on('execute_interactive')
def handle_interactive_command(data):
    """Execute command with real-time output streaming"""
    session_id = request.sid
    command = data.get('command')
    
    def stream_output():
        try:
            # Execute command and stream output
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    socketio.emit('command_output', {
                        'output': line,
                        'session_id': session_id
                    }, room=session_id)
            
            process.wait()
            socketio.emit('command_complete', {
                'return_code': process.returncode,
                'session_id': session_id
            }, room=session_id)
            
        except Exception as e:
            socketio.emit('command_error', {
                'error': str(e),
                'session_id': session_id
            }, room=session_id)
    
    # Run in separate thread to avoid blocking
    thread = threading.Thread(target=stream_output)
    thread.daemon = True
    thread.start()

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat messages for AI interaction"""
    session_id = request.sid
    message = data.get('message')
    provider = data.get('provider', 'gemini')
    
    try:
        # Process message through AI
        interactive_cli = InteractiveCLI()
        response = interactive_cli.process_message(message, provider)
        
        socketio.emit('chat_response', {
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }, room=session_id)
        
    except Exception as e:
        socketio.emit('chat_error', {
            'error': str(e),
            'session_id': session_id
        }, room=session_id)

# Static file serving for React app
@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('ui/build/static', path)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """Main entry point for the UI application"""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting CodeObit UI on port {port}")
    
    # Create required directories
    Path('uploads').mkdir(exist_ok=True)
    Path('ui/templates').mkdir(parents=True, exist_ok=True)
    Path('ui/build/static').mkdir(parents=True, exist_ok=True)
    
    # Run the app with SocketIO
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=port, 
                 debug=debug,
                 allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()