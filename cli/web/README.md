# CodeObit Web UI

A modern, responsive web interface for the CodeObit AI-powered development environment.

## Features

- **Modern Dark Theme**: Beautiful dark UI with gradient backgrounds and smooth animations
- **Real-time Terminal**: Interactive terminal with command history and syntax highlighting
- **Project Management**: Create, view, and manage projects through the web interface
- **Quick Actions**: One-click access to common CodeObit commands
- **Real-time Communication**: WebSocket-based communication for instant feedback
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Keyboard Shortcuts**: Power user shortcuts for efficient navigation

## Getting Started

### Starting the Web UI

You can start the web UI in several ways:

#### 1. Using the CLI command
```bash
# Start with default settings (localhost:5000)
python main.py web

# Start on a different port
python main.py web --port 8080

# Allow external connections
python main.py web --host 0.0.0.0 --port 8080

# Enable debug mode
python main.py web --debug
```

#### 2. Using the standalone web server
```bash
# Start with default settings
python web_server.py

# Start with custom settings
python web_server.py --host 0.0.0.0 --port 8080 --debug
```

#### 3. Using the CLI directly
```bash
# Start the main CLI and use web command
codeobit web
```

### Accessing the Web UI

Once started, open your browser and navigate to:
- **Default**: http://127.0.0.1:5000
- **External**: http://your-server-ip:port

## UI Components

### Main Dashboard
- **System Status**: Shows connection status, version, and available features
- **Quick Actions**: One-click buttons for common operations
- **Command History**: Recent commands with click-to-repeat functionality

### Terminal Interface
- **Real-time Output**: Live command execution with color-coded results
- **Command Input**: Type commands directly or use the quick action buttons
- **Export Functionality**: Download terminal logs for debugging

### Project Management
- **Project List**: View all your CodeObit projects
- **Project Creation**: Create new projects with templates
- **Project Selection**: Click to select and work with specific projects

### Feature Cards
- **Code Generation**: AI-powered code generation and analysis
- **Design & Architecture**: System design and architecture planning
- **Testing**: Automated testing and test generation
- **Security**: Security analysis and vulnerability scanning
- **Documentation**: Generate comprehensive documentation
- **Project Management**: Project structure and settings management

## Keyboard Shortcuts

- **Ctrl/Cmd + Enter**: Execute command
- **Ctrl/Cmd + L**: Clear terminal
- **Ctrl/Cmd + K**: Focus command input
- **Enter**: Execute command from input field

## API Endpoints

The web UI provides several REST API endpoints:

- `GET /api/status` - Get system status and version
- `GET /api/commands` - Get available commands
- `POST /api/execute` - Execute a CLI command
- `GET /api/projects` - Get list of projects
- `GET/POST /api/config` - Get or update configuration

## WebSocket Events

Real-time communication via Socket.IO:

- `connect` - Client connected
- `disconnect` - Client disconnected
- `execute_command` - Execute command in real-time
- `command_result` - Command execution result
- `status` - System status updates

## Development

### Project Structure
```
cli/web/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Main HTML template
├── static/
│   ├── js/
│   │   └── app.js      # Main JavaScript application
│   └── favicon.ico     # Favicon
├── controllers/        # MVC controllers
├── models/            # Data models
├── presenters/        # View presenters
└── README.md          # This file
```

### Customization

#### Themes
The web UI uses CSS custom properties for easy theming. Modify the `:root` variables in `templates/index.html`:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --accent-color: #06b6d4;
    /* ... more variables */
}
```

#### Adding New Features
1. Add new API endpoints in `app.py`
2. Update the frontend JavaScript in `static/js/app.js`
3. Add UI components to `templates/index.html`

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Use a different port
   python main.py web --port 8080
   ```

2. **Connection refused**
   - Check if the server is running
   - Verify the host and port settings
   - Check firewall settings

3. **Commands not working**
   - Ensure CodeObit CLI is properly initialized
   - Check API key configuration
   - Verify command syntax

### Debug Mode
Enable debug mode for detailed error information:
```bash
python main.py web --debug
```

## Browser Compatibility

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the main LICENSE file for details.