# CodeObit UI Guide

## 📖 Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Features](#features)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Overview

CodeObit UI is a modern web-based interface that provides a visual and interactive way to use all CodeObit CLI features. Built with Flask backend and React frontend, it offers real-time communication, beautiful design, and seamless integration with the existing CLI functionality.

## Getting Started

### Installation

1. **Using the startup scripts:**
   ```bash
   # Linux/macOS
   ./run_ui.sh
   
   # Windows
   run_ui.bat
   ```

2. **Using Docker:**
   ```bash
   docker-compose up -d
   ```

3. **Manual installation:**
   ```bash
   # Install dependencies
   pip install flask flask-cors flask-socketio
   
   # Run the application
   python ui_app.py
   ```

### Accessing the UI

Open your browser and navigate to: `http://localhost:5000`

## Features

### 🎨 User Interface Components

#### 1. **AI Chat Interface**
- Real-time conversation with AI
- Support for multiple AI providers (Gemini, GPT-4, Qwen3)
- Syntax highlighting for code blocks
- File references with `@filename` syntax
- Image upload and analysis

#### 2. **Command Palette**
- Visual access to all CLI commands
- One-click execution
- Command categories:
  - Requirements generation
  - System design
  - Code generation
  - Testing
  - Security audit
  - Documentation
  - DevOps setup
  - Debugging

#### 3. **Integrated Terminal**
- Execute shell commands directly from the browser
- Real-time output streaming
- Command history
- Syntax highlighting

#### 4. **Project Manager**
- Create new projects
- Switch between projects
- View project files and structure
- Export projects

#### 5. **File Explorer**
- Browse project files
- Edit files in-browser
- Upload files
- Download files

### 🔌 WebSocket Features

The UI uses WebSocket connections for real-time communication:

- **Live command output**: See command execution results as they happen
- **Chat streaming**: AI responses stream in real-time
- **File watching**: Auto-refresh when files change
- **Progress indicators**: Track long-running operations

### 🎯 API Endpoints

#### Health Check
```http
GET /api/health
```
Returns server status and version information.

#### Get Providers
```http
GET /api/providers
```
Returns available AI providers and current selection.

#### Execute Command
```http
POST /api/execute
Content-Type: application/json

{
  "command": "requirements",
  "params": {
    "description": "E-commerce platform"
  }
}
```
Executes a CLI command with parameters.

#### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

file: <binary>
```
Uploads a file for processing.

#### Browse URL
```http
POST /api/browse
Content-Type: application/json

{
  "url": "https://example.com"
}
```
Browses and summarizes a web page.

### WebSocket Events

#### Client → Server

**chat_message**
```javascript
socket.emit('chat_message', {
  message: "Generate a Python function",
  provider: "gemini"
});
```

**execute_interactive**
```javascript
socket.emit('execute_interactive', {
  command: "python script.py"
});
```

#### Server → Client

**chat_response**
```javascript
socket.on('chat_response', (data) => {
  console.log(data.response);
});
```

**command_output**
```javascript
socket.on('command_output', (data) => {
  console.log(data.output);
});
```

## Architecture

### Backend (Flask)

```
ui_app.py
├── Flask Application
│   ├── REST API endpoints
│   ├── WebSocket handlers
│   └── Static file serving
├── UICommandHandler
│   ├── CLI command execution
│   └── Result formatting
└── Session Management
    ├── Active connections
    └── User sessions
```

### Frontend (React)

```
index.html
├── React Components
│   ├── CodeObitUI (Main)
│   ├── Chat Interface
│   ├── Command Palette
│   ├── Terminal
│   └── File Explorer
├── WebSocket Client
│   ├── Connection management
│   └── Event handlers
└── State Management
    ├── Messages
    ├── Active view
    └── Provider selection
```

## Customization

### Theming

Modify the CSS in `ui/templates/index.html`:

```css
/* Change primary colors */
body {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

.btn-primary {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}
```

### Adding New Commands

1. Add command to backend (`ui_app.py`):
```python
@app.route('/api/custom-command', methods=['POST'])
def custom_command():
    # Your implementation
    return jsonify({'success': True})
```

2. Add to frontend command palette:
```javascript
const commands = [
    // ... existing commands
    { name: 'Custom', icon: '🔧', desc: 'Custom command', cmd: 'custom' }
];
```

### Environment Variables

Create a `.env` file:

```bash
# Server Configuration
PORT=5000
DEBUG=False
SECRET_KEY=your-secret-key

# AI Provider Keys
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key

# Feature Flags
ENABLE_AUTH=true
ENABLE_LOGGING=true
MAX_UPLOAD_SIZE=16777216  # 16MB in bytes
```

## Deployment

### Production Setup

1. **Update configuration:**
```python
# ui_app.py
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

2. **Use production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet ui_app:app
```

3. **Setup reverse proxy (Nginx):**
```nginx
server {
    listen 80;
    server_name codeobit.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codeobit-ui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codeobit-ui
  template:
    metadata:
      labels:
        app: codeobit-ui
    spec:
      containers:
      - name: codeobit-ui
        image: codeobit/ui:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: codeobit-ui-service
spec:
  selector:
    app: codeobit-ui
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## Troubleshooting

### Common Issues

#### 1. **Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000  # Linux/macOS
netstat -ano | findstr :5000  # Windows

# Kill the process or use different port
export PORT=5001
python ui_app.py
```

#### 2. **WebSocket Connection Failed**
- Check firewall settings
- Ensure CORS is properly configured
- Verify WebSocket support in reverse proxy

#### 3. **Module Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
pip install flask flask-cors flask-socketio
```

#### 4. **UI Not Loading**
- Clear browser cache
- Check browser console for errors
- Verify all directories exist:
```bash
mkdir -p ui/templates ui/build/static uploads
```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export DEBUG=True
export FLASK_ENV=development
python ui_app.py
```

### Logging

Check logs for errors:

```bash
# Application logs
tail -f ui_app.log

# Docker logs
docker-compose logs -f codeobit-ui
```

## Security Considerations

1. **Authentication**: Implement user authentication for production
2. **HTTPS**: Use SSL certificates in production
3. **API Keys**: Never commit API keys to version control
4. **File Uploads**: Validate and sanitize all uploads
5. **Rate Limiting**: Implement rate limiting for API endpoints
6. **CORS**: Configure CORS properly for production

## Contributing

To contribute to the UI development:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [Report bugs](https://github.com/shalinda-j/CodeObit/issues)
- Discussions: [Ask questions](https://github.com/shalinda-j/CodeObit/discussions)

## License

MIT License - See LICENSE file for details