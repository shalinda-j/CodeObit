// CodeObit Web UI - Main JavaScript

// Global variables
let socket = null;
let toastContainer = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeUI();
    initializeSocketIO();
    setupGlobalEventListeners();
});

// Initialize UI components
function initializeUI() {
    // Create toast container
    createToastContainer();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup theme
    applyTheme();
    
    // Initialize provider dropdown
    initializeProviderDropdown();
    
    console.log('CodeObit Web UI initialized');
}

// Initialize Socket.IO connection
function initializeSocketIO() {
    if (typeof io !== 'undefined') {
        try {
            socket = io();
            
            socket.on('connect', function() {
                console.log('Connected to CodeObit server');
                updateConnectionStatus(true);
            });
            
            socket.on('disconnect', function() {
                console.log('Disconnected from CodeObit server');
                updateConnectionStatus(false);
            });
            
            socket.on('status', function(data) {
                showToast(data.message, 'info');
            });
            
            socket.on('error', function(data) {
                console.error('Socket error:', data);
                showToast(data.message || 'Connection error', 'danger');
            });
            
        } catch (error) {
            console.warn('Socket.IO not available:', error);
        }
    } else {
        console.warn('Socket.IO library not loaded');
    }
}

// Setup global event listeners
function setupGlobalEventListeners() {
    // Handle keyboard shortcuts
    document.addEventListener('keydown', handleGlobalKeyboard);
    
    // Handle provider selection
    document.addEventListener('click', function(e) {
        if (e.target.hasAttribute('data-provider')) {
            switchProvider(e.target.getAttribute('data-provider'));
        }
    });
    
    // Handle escape key for modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close any open modals
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) modal.hide();
            }
        }
    });
}

// Handle global keyboard shortcuts
function handleGlobalKeyboard(event) {
    // Ctrl/Cmd + K - Focus search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + / - Show help
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        showHelpModal();
    }
    
    // Ctrl/Cmd + N - New (context dependent)
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        handleNewShortcut();
    }
}

// Handle "New" shortcut based on current page
function handleNewShortcut() {
    const currentPath = window.location.pathname;
    
    switch (currentPath) {
        case '/chat':
            clearChat && clearChat();
            break;
        case '/projects':
            createProject && createProject();
            break;
        case '/files':
            createFile && createFile();
            break;
        default:
            window.location.href = '/chat';
    }
}

// Create toast container
function createToastContainer() {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);
}

// Show toast notification
function showToast(message, type = 'info', duration = 5000) {
    if (!toastContainer) {
        createToastContainer();
    }
    
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-triangle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    const bgColorMap = {
        success: 'text-bg-success',
        danger: 'text-bg-danger',
        warning: 'text-bg-warning',
        info: 'text-bg-info'
    };
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center ${bgColorMap[type]} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${iconMap[type]} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        delay: duration
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Show/hide loading overlay
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('status-indicator');
    if (statusIndicator) {
        const toast = statusIndicator.querySelector('.toast');
        const toastBody = toast.querySelector('.toast-body');
        
        if (connected) {
            toast.className = 'toast align-items-center text-bg-success border-0';
            toastBody.innerHTML = '<i class="fas fa-wifi me-2"></i>Connected to CodeObit';
        } else {
            toast.className = 'toast align-items-center text-bg-danger border-0';
            toastBody.innerHTML = '<i class="fas fa-wifi me-2"></i>Disconnected from CodeObit';
        }
        
        const bsToast = bootstrap.Toast.getOrCreateInstance(toast);
        bsToast.show();
    }
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Apply theme
function applyTheme() {
    const savedTheme = localStorage.getItem('codeObitTheme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    
    // Update theme toggle if exists
    const themeToggle = document.getElementById('theme');
    if (themeToggle) {
        themeToggle.value = savedTheme;
    }
}

// Switch theme
function switchTheme(theme) {
    localStorage.setItem('codeObitTheme', theme);
    document.body.setAttribute('data-theme', theme);
    showToast(`Switched to ${theme} theme`, 'success');
}

// Initialize provider dropdown
function initializeProviderDropdown() {
    const currentProvider = localStorage.getItem('currentProvider') || 'gemini';
    const providerElement = document.getElementById('current-provider');
    if (providerElement) {
        providerElement.textContent = currentProvider.charAt(0).toUpperCase() + currentProvider.slice(1);
    }
    
    // Update AI provider indicator in dashboard
    const aiProviderElement = document.getElementById('ai-provider');
    if (aiProviderElement) {
        aiProviderElement.textContent = currentProvider.charAt(0).toUpperCase() + currentProvider.slice(1);
    }
}

// Switch AI provider
function switchProvider(provider) {
    localStorage.setItem('currentProvider', provider);
    
    const providerElement = document.getElementById('current-provider');
    if (providerElement) {
        providerElement.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
    }
    
    const aiProviderElement = document.getElementById('ai-provider');
    if (aiProviderElement) {
        aiProviderElement.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
    }
    
    showToast(`Switched to ${provider}`, 'info');
    
    // Emit provider change if socket is available
    if (socket && socket.connected) {
        socket.emit('provider_change', { provider: provider });
    }
}

// Show help modal
function showHelpModal() {
    const helpModalHTML = `
        <div class="modal fade" id="helpModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content bg-dark">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle me-2"></i>CodeObit Help
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-keyboard me-2"></i>Keyboard Shortcuts</h6>
                                <ul class="list-unstyled">
                                    <li><kbd>Ctrl/Cmd + K</kbd> - Focus search</li>
                                    <li><kbd>Ctrl/Cmd + N</kbd> - New (context dependent)</li>
                                    <li><kbd>Ctrl/Cmd + /</kbd> - Show this help</li>
                                    <li><kbd>Ctrl + Enter</kbd> - Send message (in chat)</li>
                                    <li><kbd>Escape</kbd> - Close modal</li>
                                </ul>
                                
                                <h6><i class="fas fa-comments me-2"></i>Chat Features</h6>
                                <ul class="list-unstyled">
                                    <li><code>@filename.py</code> - Reference files</li>
                                    <li>Upload images for analysis</li>
                                    <li>Switch between AI providers</li>
                                    <li>Export chat history</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-robot me-2"></i>AI Providers</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-gem text-primary me-2"></i>Google Gemini - Fast responses</li>
                                    <li><i class="fas fa-brain text-info me-2"></i>Qwen 3 - Advanced reasoning</li>
                                    <li><i class="fas fa-bolt text-success me-2"></i>OpenAI GPT - Industry standard</li>
                                </ul>
                                
                                <h6><i class="fas fa-lightbulb me-2"></i>Tips</h6>
                                <ul class="list-unstyled">
                                    <li>Use specific questions for better responses</li>
                                    <li>Reference files to provide context</li>
                                    <li>Check settings for customization options</li>
                                    <li>Export your work regularly</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <a href="https://github.com/yourusername/codeobit" class="btn btn-primary" target="_blank">
                            <i class="fas fa-external-link-alt me-1"></i>Documentation
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing help modal if any
    const existingModal = document.getElementById('helpModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new help modal
    document.body.insertAdjacentHTML('beforeend', helpModalHTML);
    
    // Show modal
    const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
    helpModal.show();
    
    // Remove modal from DOM when hidden
    document.getElementById('helpModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Format date
function formatDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return 'Today, ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
        return 'Yesterday, ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays < 7) {
        return diffDays + ' days ago';
    } else {
        return date.toLocaleDateString();
    }
}

// Debounce function
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Copy to clipboard
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast(successMessage, 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard', 'danger');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showToast(successMessage, 'success');
        } catch (err) {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard', 'danger');
        }
        
        document.body.removeChild(textArea);
    }
}

// Download file
function downloadFile(content, filename, mimeType = 'text/plain') {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Animate element
function animateElement(element, animation, duration = 500) {
    element.style.animation = `${animation} ${duration}ms ease-out`;
    
    setTimeout(() => {
        element.style.animation = '';
    }, duration);
}

// Auto-resize textarea
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Setup auto-resize for all textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        // Initial resize
        autoResizeTextarea(textarea);
    });
});

// Handle image preview
function handleImagePreview(input, previewElement) {
    const file = input.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.src = e.target.result;
            previewElement.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Validate API key format
function validateApiKey(apiKey, provider) {
    if (!apiKey || apiKey.trim().length === 0) {
        return { valid: false, message: 'API key is required' };
    }
    
    switch (provider) {
        case 'gemini':
            if (!apiKey.startsWith('AI')) {
                return { valid: false, message: 'Gemini API key should start with "AI"' };
            }
            break;
        case 'openai':
            if (!apiKey.startsWith('sk-')) {
                return { valid: false, message: 'OpenAI API key should start with "sk-"' };
            }
            break;
        case 'qwen':
            if (!apiKey.startsWith('sk-or-')) {
                return { valid: false, message: 'OpenRouter API key should start with "sk-or-"' };
            }
            break;
    }
    
    return { valid: true };
}

// Export global functions for use in other scripts
window.CodeObitUI = {
    showToast,
    showLoading,
    switchProvider,
    copyToClipboard,
    downloadFile,
    formatFileSize,
    formatDate,
    debounce,
    animateElement,
    validateApiKey
};

console.log('CodeObit Web UI JavaScript loaded successfully');