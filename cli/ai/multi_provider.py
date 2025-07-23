"""
Multi-AI Provider Manager for CodeObit CLI
Supports multiple AI providers including Gemini, Qwen 3 via OpenRouter, and others
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    """Configuration for an AI provider"""
    name: str
    api_key: str
    base_url: str
    model: str
    headers: Dict[str, str]
    request_format: str = "openai"  # openai, anthropic, gemini

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.name = config.name
        
    @abstractmethod
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.7) -> str:
        """Generate content using the AI provider"""
        pass
        
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the AI provider"""
        pass

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=config.api_key)
            self.types = types
        except ImportError:
            raise ImportError("google-genai library is required for Gemini provider")
    
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.7) -> str:
        try:
            config = self.types.GenerateContentConfig(temperature=temperature)
            if system_instruction:
                config.system_instruction = system_instruction
                
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=prompt,
                config=config
            )
            
            return response.text if response.text else "No content generated"
        except Exception as e:
            logger.error(f"Gemini content generation failed: {e}")
            raise Exception(f"Failed to generate content: {e}")
    
    def test_connection(self) -> bool:
        try:
            response = self.client.models.generate_content(
                model=self.config.model,
                contents="Hello, test connection"
            )
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

class Qwen3Provider(BaseAIProvider):
    """Qwen 3 AI provider via OpenRouter"""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(config.headers)
    
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.7) -> str:
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4000
            }
            
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception("No content in response")
                
        except Exception as e:
            logger.error(f"Qwen3 content generation failed: {e}")
            raise Exception(f"Failed to generate content: {e}")
    
    def test_connection(self) -> bool:
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Qwen3 connection test failed: {e}")
            return False

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update(config.headers)
    
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.7) -> str:
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4000
            }
            
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"OpenAI content generation failed: {e}")
            raise Exception(f"Failed to generate content: {e}")
    
    def test_connection(self) -> bool:
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False

class MultiAIProviderManager:
    """Manager for multiple AI providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.current_provider: Optional[str] = None
        self.config_file = ".codeobit/ai_providers.json"
        self.load_providers()
    
    def load_providers(self):
        """Load AI provider configurations"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                for provider_name, provider_config in config_data.get("providers", {}).items():
                    self.add_provider_from_config(provider_name, provider_config)
                    
                self.current_provider = config_data.get("current_provider")
            else:
                # Create default configuration
                self.create_default_config()
        except Exception as e:
            logger.error(f"Failed to load AI providers: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default provider configuration"""
        default_config = {
            "providers": {
                "gemini": {
                    "name": "Google Gemini",
                    "model": "gemini-2.5-flash",
                    "api_key": "",
                    "base_url": "",
                    "headers": {},
                    "request_format": "gemini"
                },
                "qwen3": {
                    "name": "Qwen 3",
                    "model": "qwen/qwen-2.5-72b-instruct",
                    "api_key": "",
                    "base_url": "https://openrouter.ai/api/v1",
                    "headers": {
                        "HTTP-Referer": "https://codeobit.dev",
                        "X-Title": "CodeObit CLI"
                    },
                    "request_format": "openai"
                },
                "openai": {
                    "name": "OpenAI GPT",
                    "model": "gpt-4",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "headers": {},
                    "request_format": "openai"
                }
            },
            "current_provider": "gemini"
        }
        
        # Create config directory
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    def add_provider_from_config(self, name: str, config_dict: Dict[str, Any]):
        """Add provider from configuration dictionary"""
        try:
            # Set API key from environment if not in config
            api_key = config_dict.get("api_key")
            if not api_key:
                env_key = f"{name.upper()}_API_KEY"
                api_key = os.getenv(env_key)
                if not api_key and name == "gemini":
                    api_key = os.getenv("GEMINI_API_KEY")
                elif not api_key and name == "qwen3":
                    api_key = os.getenv("OPENROUTER_API_KEY")
                elif not api_key and name == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                logger.warning(f"No API key found for provider {name}")
                return
            
            # Create headers
            headers = config_dict.get("headers", {}).copy()
            if config_dict.get("request_format") == "openai":
                headers["Authorization"] = f"Bearer {api_key}"
                headers["Content-Type"] = "application/json"
            
            config = AIProviderConfig(
                name=config_dict["name"],
                api_key=api_key,
                base_url=config_dict.get("base_url", ""),
                model=config_dict["model"],
                headers=headers,
                request_format=config_dict.get("request_format", "openai")
            )
            
            # Create provider instance
            if name == "gemini":
                provider = GeminiProvider(config)
            elif name == "qwen3":
                provider = Qwen3Provider(config)
            elif name == "openai":
                provider = OpenAIProvider(config)
            else:
                logger.warning(f"Unknown provider type: {name}")
                return
            
            self.providers[name] = provider
            logger.info(f"Added AI provider: {name}")
            
        except Exception as e:
            logger.error(f"Failed to add provider {name}: {e}")
    
    def set_current_provider(self, provider_name: str) -> bool:
        """Set the current active provider"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            self.save_config()
            return True
        return False
    
    def get_current_provider(self) -> Optional[BaseAIProvider]:
        """Get the current active provider"""
        if self.current_provider and self.current_provider in self.providers:
            return self.providers[self.current_provider]
        return None
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all available providers"""
        result = []
        for name, provider in self.providers.items():
            result.append({
                "name": name,
                "display_name": provider.config.name,
                "model": provider.config.model,
                "active": name == self.current_provider
            })
        return result
    
    def test_provider(self, provider_name: str) -> bool:
        """Test a specific provider"""
        if provider_name in self.providers:
            return self.providers[provider_name].test_connection()
        return False
    
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.7, provider: Optional[str] = None) -> str:
        """Generate content using current or specified provider"""
        provider_name = provider or self.current_provider
        
        if not provider_name or provider_name not in self.providers:
            raise Exception("No active AI provider available")
        
        return self.providers[provider_name].generate_content(prompt, system_instruction, temperature)
    
    def save_config(self):
        """Save current configuration"""
        try:
            config_data = {
                "providers": {},
                "current_provider": self.current_provider
            }
            
            # Note: We don't save API keys to file for security
            for name, provider in self.providers.items():
                config_data["providers"][name] = {
                    "name": provider.config.name,
                    "model": provider.config.model,
                    "api_key": "",  # Don't save API key
                    "base_url": provider.config.base_url,
                    "headers": {k: v for k, v in provider.config.headers.items() 
                              if not k.lower().startswith('authorization')},
                    "request_format": provider.config.request_format
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save AI provider config: {e}")

# Global instance
_provider_manager = None

def get_provider_manager() -> MultiAIProviderManager:
    """Get or create global provider manager"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = MultiAIProviderManager()
    return _provider_manager
