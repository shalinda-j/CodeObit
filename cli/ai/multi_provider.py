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
        self.available_models: Dict[str, List[str]] = {}
        self.provider_shortcuts = {
            '!gpt': 'openai',
            '!gemini': 'gemini', 
            '!qwen': 'qwen3',
            '!claude': 'claude',
            '!kimi': 'kimi',
            '!deepseek': 'deepseek',
            '!openrouter': 'openrouter',
            '!perplexity': 'perplexity',
            '!groq': 'groq',
            '!cohere': 'cohere',
            '!mistral': 'mistral'
        }
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
                    "request_format": "gemini",
                    "available_models": [
                        "gemini-2.5-flash",
                        "gemini-2.5-pro",
                        "gemini-1.5-flash",
                        "gemini-1.5-pro"
                    ]
                },
                "openai": {
                    "name": "OpenAI GPT",
                    "model": "gpt-4",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "headers": {},
                    "request_format": "openai",
                    "available_models": [
                        "gpt-4",
                        "gpt-4-turbo",
                        "gpt-3.5-turbo",
                        "gpt-4o",
                        "gpt-4o-mini"
                    ]
                },
                "claude": {
                    "name": "Anthropic Claude",
                    "model": "claude-3-5-sonnet-20241022",
                    "api_key": "",
                    "base_url": "https://api.anthropic.com/v1",
                    "headers": {},
                    "request_format": "anthropic",
                    "available_models": [
                        "claude-3-5-sonnet-20241022",
                        "claude-3-5-haiku-20241022",
                        "claude-3-opus-20240229",
                        "claude-3-sonnet-20240229",
                        "claude-3-haiku-20240307"
                    ]
                },
                "qwen3": {
                    "name": "Qwen 3 (OpenRouter)",
                    "model": "qwen/qwen-2.5-72b-instruct",
                    "api_key": "",
                    "base_url": "https://openrouter.ai/api/v1",
                    "headers": {
                        "HTTP-Referer": "https://codeobit.dev",
                        "X-Title": "CodeObit CLI"
                    },
                    "request_format": "openai",
                    "available_models": [
                        "qwen/qwen-2.5-72b-instruct",
                        "qwen/qwen-2.5-32b-instruct",
                        "qwen/qwen-2.5-14b-instruct",
                        "qwen/qwen-2.5-7b-instruct"
                    ]
                },
                "kimi": {
                    "name": "Moonshot Kimi",
                    "model": "moonshot-v1-8k",
                    "api_key": "",
                    "base_url": "https://api.moonshot.cn/v1",
                    "headers": {},
                    "request_format": "openai",
                    "available_models": [
                        "moonshot-v1-8k",
                        "moonshot-v1-32k",
                        "moonshot-v1-128k"
                    ]
                },
                "deepseek": {
                    "name": "DeepSeek",
                    "model": "deepseek-chat",
                    "api_key": "",
                    "base_url": "https://api.deepseek.com/v1",
                    "headers": {},
                    "request_format": "openai",
                    "available_models": [
                        "deepseek-chat",
                        "deepseek-coder"
                    ]
                },
                "openrouter": {
                    "name": "OpenRouter",
                    "model": "meta-llama/llama-3.1-405b-instruct",
                    "api_key": "",
                    "base_url": "https://openrouter.ai/api/v1",
                    "headers": {
                        "HTTP-Referer": "https://codeobit.dev",
                        "X-Title": "CodeObit CLI"
                    },
                    "request_format": "openai",
                    "available_models": [
                        "meta-llama/llama-3.1-405b-instruct",
                        "meta-llama/llama-3.1-70b-instruct",
                        "meta-llama/llama-3.1-8b-instruct",
                        "google/gemini-pro-1.5",
                        "anthropic/claude-3.5-sonnet"
                    ]
                },
                "perplexity": {
                    "name": "Perplexity",
                    "model": "llama-3.1-sonar-large-128k-online",
                    "api_key": "",
                    "base_url": "https://api.perplexity.ai",
                    "headers": {},
                    "request_format": "openai",
                    "available_models": [
                        "llama-3.1-sonar-large-128k-online",
                        "llama-3.1-sonar-small-128k-online",
                        "llama-3.1-sonar-large-128k-chat",
                        "llama-3.1-sonar-small-128k-chat"
                    ]
                },
                "groq": {
                    "name": "Groq",
                    "model": "llama-3.1-70b-versatile",
                    "api_key": "",
                    "base_url": "https://api.groq.com/openai/v1",
                    "headers": {},
                    "request_format": "openai",
                    "available_models": [
                        "llama-3.1-70b-versatile",
                        "llama-3.1-8b-instant",
                        "mixtral-8x7b-32768",
                        "gemma2-9b-it"
                    ]
                },
                "cohere": {
                    "name": "Cohere",
                    "model": "command-r-plus",
                    "api_key": "",
                    "base_url": "https://api.cohere.ai/v1",
                    "headers": {},
                    "request_format": "cohere",
                    "available_models": [
                        "command-r-plus",
                        "command-r",
                        "command",
                        "command-nightly"
                    ]
                },
                "mistral": {
                    "name": "Mistral AI",
                    "model": "mistral-large-latest",
                    "api_key": "",
                    "base_url": "https://api.mistral.ai/v1",
                    "headers": {},
                    "request_format": "openai",
                    "available_models": [
                        "mistral-large-latest",
                        "mistral-medium-latest",
                        "mistral-small-latest",
                        "open-mistral-7b",
                        "open-mixtral-8x7b"
                    ]
                }
            },
            "current_provider": None
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
    
    def handle_provider_shortcut(self, shortcut: str) -> Optional[str]:
        """Handle provider shortcuts like !gpt, !gemini, etc."""
        return self.provider_shortcuts.get(shortcut.lower())
    
    def setup_provider_interactive(self, provider_name: str) -> bool:
        """Interactively setup a provider with API key and model selection"""
        try:
            from rich.console import Console
            from rich.prompt import Prompt, IntPrompt
            from rich.table import Table
            from rich.panel import Panel
            
            console = Console()
            
            # Load default config to get provider info
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
            else:
                self.create_default_config()
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
            
            if provider_name not in config_data['providers']:
                console.print(f"[red]Unknown provider: {provider_name}[/red]")
                return False
            
            provider_config = config_data['providers'][provider_name]
            
            # Show provider info
            info_panel = Panel(
                f"[bold cyan]{provider_config['name']}[/bold cyan]\n\n"
                f"Base URL: {provider_config.get('base_url', 'N/A')}\n"
                f"Format: {provider_config.get('request_format', 'openai')}",
                title=f"🤖 Setting up {provider_name}",
                border_style="cyan"
            )
            console.print(info_panel)
            
            # Get API key
            api_key = Prompt.ask(
                f"[yellow]Enter your {provider_config['name']} API key[/yellow]",
                password=True
            )
            
            if not api_key:
                console.print("[red]API key is required[/red]")
                return False
            
            # Show available models
            available_models = provider_config.get('available_models', [provider_config['model']])
            
            if len(available_models) > 1:
                console.print("\n[bold]Available Models:[/bold]")
                table = Table()
                table.add_column("#", style="cyan")
                table.add_column("Model", style="green")
                
                for i, model in enumerate(available_models, 1):
                    table.add_row(str(i), model)
                
                console.print(table)
                
                model_choice = IntPrompt.ask(
                    "Select model number",
                    default=1,
                    choices=[str(i) for i in range(1, len(available_models) + 1)]
                )
                selected_model = available_models[model_choice - 1]
            else:
                selected_model = available_models[0]
            
            # Create headers
            headers = provider_config.get("headers", {}).copy()
            if provider_config.get("request_format") == "openai":
                headers["Authorization"] = f"Bearer {api_key}"
                headers["Content-Type"] = "application/json"
            elif provider_config.get("request_format") == "anthropic":
                headers["x-api-key"] = api_key
                headers["Content-Type"] = "application/json"
                headers["anthropic-version"] = "2023-06-01"
            
            # Create provider config
            config = AIProviderConfig(
                name=provider_config["name"],
                api_key=api_key,
                base_url=provider_config.get("base_url", ""),
                model=selected_model,
                headers=headers,
                request_format=provider_config.get("request_format", "openai")
            )
            
            # Create provider instance
            provider = self._create_provider_instance(provider_name, config)
            if not provider:
                return False
            
            # Test connection
            console.print("[yellow]Testing connection...[/yellow]")
            if provider.test_connection():
                console.print(f"[green]✓ Successfully connected to {provider_config['name']}![/green]")
                self.providers[provider_name] = provider
                self.current_provider = provider_name
                
                # Update config file
                config_data['providers'][provider_name]['model'] = selected_model
                config_data['current_provider'] = provider_name
                
                with open(self.config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                return True
            else:
                console.print(f"[red]✗ Failed to connect to {provider_config['name']}[/red]")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup provider {provider_name}: {e}")
            return False
    
    def _create_provider_instance(self, provider_name: str, config: AIProviderConfig) -> Optional[BaseAIProvider]:
        """Create provider instance based on name"""
        try:
            if provider_name == "gemini":
                return GeminiProvider(config)
            elif provider_name in ["openai", "qwen3", "kimi", "deepseek", "openrouter", "perplexity", "groq", "mistral"]:
                return OpenAIProvider(config)
            elif provider_name == "claude":
                return self._create_claude_provider(config)
            elif provider_name == "cohere":
                return self._create_cohere_provider(config)
            else:
                # Default to OpenAI-compatible provider
                return OpenAIProvider(config)
        except Exception as e:
            logger.error(f"Failed to create provider instance for {provider_name}: {e}")
            return None
    
    def _create_claude_provider(self, config: AIProviderConfig) -> BaseAIProvider:
        """Create Claude provider (Anthropic API)"""
        # For now, use OpenAI-compatible format as many providers support it
        # In future, create dedicated ClaudeProvider class
        return OpenAIProvider(config)
    
    def _create_cohere_provider(self, config: AIProviderConfig) -> BaseAIProvider:
        """Create Cohere provider"""
        # For now, use OpenAI-compatible format
        # In future, create dedicated CohereProvider class
        return OpenAIProvider(config)
    
    def list_all_available_providers(self) -> List[Dict[str, Any]]:
        """List all available providers (configured and unconfigured)"""
        result = []
        
        # Load default config to get all possible providers
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
            else:
                self.create_default_config()
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
            
            for name, config in config_data['providers'].items():
                shortcut = None
                for sc, pn in self.provider_shortcuts.items():
                    if pn == name:
                        shortcut = sc
                        break
                
                result.append({
                    "name": name,
                    "display_name": config['name'],
                    "shortcut": shortcut,
                    "configured": name in self.providers,
                    "active": name == self.current_provider,
                    "models": config.get('available_models', [config.get('model', 'Unknown')])
                })
        except Exception as e:
            logger.error(f"Failed to list providers: {e}")
        
        return result
    
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
