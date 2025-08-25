/**
 * CodeObit Web UI - Main JavaScript Application
 * Handles all frontend functionality and communication with the backend
 */

class CodeObitWebApp {
    constructor() {
        this.socket = null;
        this.commandHistory = [];
        this.currentProject = null;
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.initializeSocketIO();
        this.loadSystemStatus();
        this.loadProjects();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
    }
    
    initializeSocketIO() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.logToTerminal('Connected to CodeObit server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.logToTerminal('Disconnected from CodeObit server', 'error');
        });
        
        this.socket.on('status', (data) => {
            this.logToTerminal(data.message, 'info');
        });
        
        this.socket.on('command_result', (data) => {
            if (data.success) {
                this.logToTerminal(`Command executed successfully: ${data.command}`, 'success');
                this.logToTerminal(data.result, 'info');
            } else {
                this.logToTerminal(`Command failed: ${data.error}`, 'error');
            }
        });
    }
    
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        const statusText = document.getElementById('connectionText');
        
        if (connected) {
            statusIndicator.className = 'status-indicator status-online';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'status-indicator status-offline';
            statusText.textContent = 'Disconnected';
        }
    }
    
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            const statusElement = document.getElementById('systemStatus');
            statusElement.innerHTML = `
                <div class="mb-2">
                    <strong>Version:</strong> ${status.version}
                </div>
                <div class="mb-2">
                    <strong>Status:</strong> 
                    <span class="text-success">${status.status}</span>
                </div>
                <div>
                    <strong>Features:</strong> ${status.features.length} available
                </div>
            `;
        } catch (error) {
            console.error('Error loading system status:', error);
            document.getElementById('systemStatus').innerHTML = 
                '<div class="text-danger">Error loading status</div>';
        }
    }
    
    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            const projects = await response.json();
            
            const projectsList = document.getElementById('projectsList');
            
            if (projects.length === 0) {
                projectsList.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-folder-open fa-2x mb-3"></i>
                        <p>No projects found</p>
                        <button class="btn btn-primary btn-sm" onclick="createNewProject()">
                            Create Your First Project
                        </button>
                    </div>
                `;
                return;
            }
            
            projectsList.innerHTML = projects.map(project => `
                <div class="project-item" onclick="selectProject('${project.name}')">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${project.name}</h6>
                            <small class="text-muted">
                                ${project.description || 'No description'}
                            </small>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">
                                ${new Date(project.created * 1000).toLocaleDateString()}
                            </small>
                        </div>
                    </div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error loading projects:', error);
            document.getElementById('projectsList').innerHTML = 
                '<div class="text-danger">Error loading projects</div>';
        }
    }
    
    setupEventListeners() {
        // Command input handling
        const commandInput = document.getElementById('commandInput');
        commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.executeCommandFromInput();
            }
        });
        
        // Auto-resize terminal
        const terminalOutput = document.getElementById('terminalOutput');
        const resizeObserver = new ResizeObserver(() => {
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        });
        resizeObserver.observe(terminalOutput);
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to execute command
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.executeCommandFromInput();
            }
            
            // Ctrl/Cmd + L to clear terminal
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.clearTerminal();
            }
            
            // Ctrl/Cmd + K to focus command input
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('commandInput').focus();
            }
        });
    }
    
    async executeCommand(command, args = []) {
        const commandString = `${command} ${args.join(' ')}`.trim();
        
        // Add to command history
        this.addToCommandHistory(commandString);
        
        // Log command to terminal
        this.logToTerminal(`$ ${commandString}`, 'command');
        
        try {
            if (this.isConnected && this.socket) {
                // Use Socket.IO for real-time execution
                this.socket.emit('execute_command', { command, args });
            } else {
                // Fallback to REST API
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command, args })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.logToTerminal(result.result, 'success');
                } else {
                    this.logToTerminal(`Error: ${result.error}`, 'error');
                }
            }
        } catch (error) {
            console.error('Error executing command:', error);
            this.logToTerminal(`Error: ${error.message}`, 'error');
        }
    }
    
    executeCommandFromInput() {
        const commandInput = document.getElementById('commandInput');
        const command = commandInput.value.trim();
        
        if (!command) return;
        
        // Parse command and arguments
        const parts = command.split(' ');
        const mainCommand = parts[0];
        const args = parts.slice(1);
        
        this.executeCommand(mainCommand, args);
        commandInput.value = '';
    }
    
    addToCommandHistory(command) {
        this.commandHistory.unshift(command);
        if (this.commandHistory.length > 10) {
            this.commandHistory.pop();
        }
        
        this.updateCommandHistoryDisplay();
    }
    
    updateCommandHistoryDisplay() {
        const historyElement = document.getElementById('commandHistory');
        
        if (this.commandHistory.length === 0) {
            historyElement.innerHTML = '<div class="text-muted small">No commands yet</div>';
            return;
        }
        
        historyElement.innerHTML = this.commandHistory.map(cmd => `
            <div class="command-item" onclick="executeCommandFromHistory('${cmd}')">
                <i class="fas fa-terminal me-2 text-muted"></i>
                <small>${cmd}</small>
            </div>
        `).join('');
    }
    
    executeCommandFromHistory(command) {
        document.getElementById('commandInput').value = command;
        this.executeCommandFromInput();
    }
    
    logToTerminal(message, type = 'info') {
        const terminalOutput = document.getElementById('terminalOutput');
        const timestamp = new Date().toLocaleTimeString();
        
        let icon = 'info-circle';
        let className = 'text-info';
        
        switch (type) {
            case 'success':
                icon = 'check-circle';
                className = 'text-success';
                break;
            case 'error':
                icon = 'exclamation-circle';
                className = 'text-danger';
                break;
            case 'warning':
                icon = 'exclamation-triangle';
                className = 'text-warning';
                break;
            case 'command':
                icon = 'chevron-right';
                className = 'text-primary';
                break;
        }
        
        const logEntry = document.createElement('div');
        logEntry.className = className;
        logEntry.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            <span class="text-muted">[${timestamp}]</span>
            ${message}
        `;
        
        terminalOutput.appendChild(logEntry);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
    
    clearTerminal() {
        const terminalOutput = document.getElementById('terminalOutput');
        terminalOutput.innerHTML = `
            <div class="text-success">
                <i class="fas fa-check-circle me-2"></i>Terminal cleared
            </div>
        `;
    }
    
    exportLog() {
        const terminalOutput = document.getElementById('terminalOutput');
        const logContent = terminalOutput.innerText;
        
        const blob = new Blob([logContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `codeobit-log-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.logToTerminal('Log exported successfully', 'success');
    }
    
    selectProject(projectName) {
        this.currentProject = projectName;
        this.logToTerminal(`Selected project: ${projectName}`, 'info');
        
        // Update UI to show selected project
        document.querySelectorAll('.project-item').forEach(item => {
            item.classList.remove('border-primary');
        });
        
        event.target.closest('.project-item').classList.add('border-primary');
    }
    
    createNewProject() {
        const modal = new bootstrap.Modal(document.getElementById('newProjectModal'));
        modal.show();
    }
    
    async submitNewProject() {
        const name = document.getElementById('projectName').value;
        const type = document.getElementById('projectType').value;
        const description = document.getElementById('projectDescription').value;
        
        if (!name) {
            alert('Please enter a project name');
            return;
        }
        
        try {
            await this.executeCommand('project', ['new', name, '--type', type, '--description', description]);
            
            // Close modal and reload projects
            const modal = bootstrap.Modal.getInstance(document.getElementById('newProjectModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('newProjectForm').reset();
            
            // Reload projects list
            setTimeout(() => this.loadProjects(), 1000);
            
        } catch (error) {
            console.error('Error creating project:', error);
        }
    }
}

// Global functions for HTML onclick handlers
function executeCommand(command, args) {
    window.codeobitApp.executeCommand(command, args);
}

function executeCommandFromInput() {
    window.codeobitApp.executeCommandFromInput();
}

function executeCommandFromHistory(command) {
    window.codeobitApp.executeCommandFromHistory(command);
}

function clearTerminal() {
    window.codeobitApp.clearTerminal();
}

function exportLog() {
    window.codeobitApp.exportLog();
}

function createNewProject() {
    window.codeobitApp.createNewProject();
}

function submitNewProject() {
    window.codeobitApp.submitNewProject();
}

function selectProject(projectName) {
    window.codeobitApp.selectProject(projectName);
}

function toggleTheme() {
    // Theme toggle functionality can be implemented here
    console.log('Theme toggle clicked');
}

function handleCommandKeyPress(event) {
    if (event.key === 'Enter') {
        executeCommandFromInput();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.codeobitApp = new CodeObitWebApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.codeobitApp) {
        window.codeobitApp.loadSystemStatus();
        window.codeobitApp.loadProjects();
    }
});