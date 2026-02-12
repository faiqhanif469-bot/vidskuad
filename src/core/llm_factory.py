"""
LLM Factory - Creates LLM instances for different providers
"""

from typing import Any
from src.core.config import ModelConfig


class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    def create_llm(config: ModelConfig) -> Any:
        """
        Create LLM instance based on provider
        
        Supports:
        - groq: Llama 3.3 70B (FASTEST, FREE)
        - gemini: Google Gemini (fast, cheap)
        - openai: GPT-4 (most capable)
        - anthropic: Claude (best reasoning)
        - ollama: Local models (free, private)
        """
        
        if config.provider == "groq":
            return LLMFactory._create_groq(config)
        elif config.provider == "gemini":
            return LLMFactory._create_gemini(config)
        elif config.provider == "openai":
            return LLMFactory._create_openai(config)
        elif config.provider == "anthropic":
            return LLMFactory._create_anthropic(config)
        elif config.provider == "ollama":
            return LLMFactory._create_ollama(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    @staticmethod
    def _create_groq(config: ModelConfig):
        """Create Groq LLM (Llama 3.3 70B - FASTEST!)"""
        from langchain_groq import ChatGroq
        
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY required for Groq")
        
        return ChatGroq(
            model=config.model_name,
            groq_api_key=config.groq_api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    @staticmethod
    def _create_gemini(config: ModelConfig):
        """Create Gemini LLM"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY required for Gemini")
        
        return ChatGoogleGenerativeAI(
            model=config.model_name,
            google_api_key=api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    @staticmethod
    def _create_openai(config: ModelConfig):
        """Create OpenAI LLM"""
        from langchain_openai import ChatOpenAI
        
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY required for OpenAI")
        
        return ChatOpenAI(
            model=config.model_name,
            api_key=config.openai_api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    @staticmethod
    def _create_anthropic(config: ModelConfig):
        """Create Anthropic Claude LLM"""
        from langchain_anthropic import ChatAnthropic
        
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY required for Anthropic")
        
        return ChatAnthropic(
            model=config.model_name,
            api_key=config.anthropic_api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    @staticmethod
    def _create_ollama(config: ModelConfig):
        """Create Ollama LLM (local)"""
        from langchain_ollama import ChatOllama
        
        return ChatOllama(
            model=config.model_name,
            base_url=config.ollama_base_url,
            temperature=config.temperature
        )
