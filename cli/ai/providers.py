"""
AI Provider Integration for CodeObit Web UI
Handles different AI providers (Gemini, OpenAI, Qwen) for the web interface
"""

import os
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def generate_response(self, message: str, **kwargs) -> str:
        """Generate response from the AI provider"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider is accessible"""
        pass

class GeminiProvider(AIProvider):
    """Google Gemini AI Provider"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.model_name = "gemini-2.5-flash"
        
    def generate_response(self, message: str, **kwargs) -> str:
        """Generate response using Gemini"""
        try:
            # This would integrate with the actual Gemini API
            # For now, returning a mock response
            return f"Gemini Response: I understand you want to discuss '{message}'. As an AI assistant, I'm here to help you with coding, project management, and technical questions. How can I assist you further?"
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            return f"I'm sorry, but I encountered an error while processing your request. Please try again."
    
    def test_connection(self) -> bool:
        """Test Gemini connection"""
        try:
            # Simulate connection test
            return True
        except Exception as e:
            self.logger.error(f"Gemini connection test failed: {e}")
            return False

class OpenAIProvider(AIProvider):
    """OpenAI GPT Provider"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.model_name = "gpt-4"
        
    def generate_response(self, message: str, **kwargs) -> str:
        """Generate response using OpenAI GPT"""
        try:
            # This would integrate with the actual OpenAI API
            # For now, returning a mock response
            return f"GPT Response: Thank you for your message about '{message}'. I'm here to help you with code generation, debugging, architecture design, and answering technical questions. What specific assistance do you need?"
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return f"I'm sorry, but I encountered an error while processing your request. Please try again."
    
    def test_connection(self) -> bool:
        """Test OpenAI connection"""
        try:
            # Simulate connection test
            return True
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {e}")
            return False

class QwenProvider(AIProvider):
    """Qwen AI Provider via OpenRouter"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.model_name = "qwen/qwen-2.5-72b-instruct"
        
    def generate_response(self, message: str, **kwargs) -> str:
        """Generate response using Qwen"""
        try:
            # This would integrate with the actual Qwen API via OpenRouter
            # For now, returning a mock response
            return f"Qwen Response: I've analyzed your request about '{message}'. As an advanced reasoning model, I can help with complex problem-solving, code architecture, algorithms, and detailed technical explanations. What would you like to explore?"
        except Exception as e:
            self.logger.error(f"Qwen API error: {e}")
            return f"I'm sorry, but I encountered an error while processing your request. Please try again."
    
    def test_connection(self) -> bool:
        """Test Qwen connection"""
        try:
            # Simulate connection test
            return True
        except Exception as e:
            self.logger.error(f"Qwen connection test failed: {e}")
            return False

# Provider registry
PROVIDERS = {
    'gemini': GeminiProvider,
    'openai': OpenAIProvider,
    'qwen': QwenProvider
}

def get_provider(provider_name: str, api_key: str = None) -> Optional[AIProvider]:
    """Get an AI provider instance"""
    provider_class = PROVIDERS.get(provider_name.lower())
    if provider_class:
        return provider_class(api_key)
    return None

def list_providers() -> list:
    """List all available providers"""
    return list(PROVIDERS.keys())

def get_provider_info() -> Dict[str, Any]:
    """Get information about all providers"""
    return {
        'gemini': {
            'name': 'Google Gemini',
            'description': 'Lightning-fast responses with Gemini 2.5-flash/pro',
            'icon': 'fa-gem',
            'color': 'primary',
            'models': ['gemini-2.5-flash', 'gemini-2.5-pro']
        },
        'openai': {
            'name': 'OpenAI GPT',
            'description': 'Industry-leading language understanding',
            'icon': 'fa-bolt',
            'color': 'success',
            'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
        },
        'qwen': {
            'name': 'Qwen 3',
            'description': 'Advanced reasoning via OpenRouter integration',
            'icon': 'fa-brain',
            'color': 'info',
            'models': ['qwen/qwen-2.5-72b-instruct', 'qwen/qwen-2.5-32b-instruct']
        }
    }