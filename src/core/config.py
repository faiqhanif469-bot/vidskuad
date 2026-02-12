"""
Configuration management for AI Video Production System
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class APIConfig:
    """API keys configuration"""
    gemini_api_key: Optional[str] = None
    pexels_api_key: Optional[str] = None
    pixabay_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            pexels_api_key=os.getenv('PEXELS_API_KEY'),
            pixabay_api_key=os.getenv('PIXABAY_API_KEY')
        )


@dataclass
class ModelConfig:
    """LLM model configuration"""
    provider: str = "groq"  # groq, gemini, openai, anthropic, ollama
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    # Provider-specific settings
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    
    @classmethod
    def from_env(cls, provider: str = None):
        """Load model config from environment"""
        provider = provider or os.getenv('LLM_PROVIDER', 'groq')
        
        config = cls(provider=provider)
        
        if provider == "groq":
            config.model_name = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
            config.groq_api_key = os.getenv('GROQ_API_KEY')
        elif provider == "gemini":
            config.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        elif provider == "openai":
            config.model_name = os.getenv('OPENAI_MODEL', 'gpt-4o')
            config.openai_api_key = os.getenv('OPENAI_API_KEY')
        elif provider == "anthropic":
            config.model_name = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
            config.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        elif provider == "ollama":
            config.model_name = os.getenv('OLLAMA_MODEL', 'llama3.1:70b')
            config.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        return config


@dataclass
class SearchConfig:
    """Search configuration"""
    max_results_per_platform: int = 10
    timeout_seconds: int = 10
    default_platforms: list = None
    
    def __post_init__(self):
        if self.default_platforms is None:
            self.default_platforms = ['youtube', 'pexels', 'pixabay']


class Config:
    """Main configuration class"""
    
    def __init__(self, llm_provider: str = None):
        self.api = APIConfig.from_env()
        self.model = ModelConfig.from_env(llm_provider)
        self.search = SearchConfig()
    
    @classmethod
    def load(cls, llm_provider: str = None):
        """Load configuration"""
        return cls(llm_provider)
