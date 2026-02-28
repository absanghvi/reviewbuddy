"""
LLM Factory for Creating Provider Instances

This module implements the factory pattern to create LLM client instances
based on the configured provider, making it easy to switch between providers.
"""

from src.llm_client import LLMClient
from src.openai_client import OpenAIClient
from src.anthropic_client import AnthropicClient
from config.llm_config import LLMConfig, LLMProvider


class LLMFactory:
    """Factory for creating LLM client instances"""
    
    _clients = {
        LLMProvider.OPENAI: OpenAIClient,
        LLMProvider.ANTHROPIC: AnthropicClient,
    }
    
    @staticmethod
    def create_client(config: LLMConfig) -> LLMClient:
        """
        Create an LLM client based on configuration.
        
        This method creates the appropriate LLM client instance based on
        the provider specified in the configuration. The factory makes it
        easy to swap providers by simply changing the PROVIDER env variable.
        
        Args:
            config: LLM configuration instance
        
        Returns:
            Configured LLM client instance
        
        Raises:
            ValueError: If provider is not supported or config is invalid
        """
        # Validate configuration
        if not config.validate_provider_config():
            raise ValueError(
                f"Invalid configuration for provider {config.provider}. "
                f"Ensure API key and model are set."
            )
        
        client_class = LLMFactory._clients.get(config.provider)
        
        if client_class is None:
            raise ValueError(
                f"Unsupported LLM provider: {config.provider}. "
                f"Supported providers: {list(LLMFactory._clients.keys())}"
            )
        
        return client_class(config)
    
    @staticmethod
    def register_provider(provider: str, client_class):
        """
        Register a custom LLM provider.
        
        This allows adding support for new LLM providers without modifying
        the factory class.
        
        Args:
            provider: Provider identifier string
            client_class: Class that implements LLMClient interface
        """
        LLMFactory._clients[provider] = client_class
    
    @staticmethod
    def get_supported_providers():
        """Get list of supported providers"""
        return list(LLMFactory._clients.keys())
