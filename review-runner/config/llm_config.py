"""
LLM Configuration Module

This module handles configuration for LLM providers (OpenAI, Anthropic, etc.)
Configuration is loaded from environment variables via python-dotenv
"""

import os
from enum import Enum
from typing import Optional

# pydantic v2 moved BaseSettings to the separate `pydantic-settings` package.
# Try to import from there first for v2.5+, otherwise fall back to pydantic.
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except Exception:
    from pydantic import BaseSettings, Field


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseSettings):
    """
    LLM Configuration with support for multiple providers.
    Configuration can be loaded from environment variables or .env file.
    
    This makes the LLM connection configurable so any provider can be used
    by simply changing the PROVIDER environment variable.
    """
    
    # Provider Selection
    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider to use"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        alias="OPENAI_API_KEY",
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4",
        alias="OPENAI_MODEL",
        description="OpenAI model to use"
    )
    openai_temperature: float = Field(
        default=0.3,
        alias="OPENAI_TEMPERATURE",
        description="OpenAI temperature parameter"
    )
    openai_max_tokens: int = Field(
        default=2000,
        alias="OPENAI_MAX_TOKENS",
        description="Maximum tokens for OpenAI response"
    )
    
    # Anthropic Configuration
    anthropic_api_key: str = Field(
        default="",
        alias="ANTHROPIC_API_KEY",
        description="Anthropic API key"
    )
    anthropic_model: str = Field(
        default="claude-3-opus-20240229",
        alias="ANTHROPIC_MODEL",
        description="Anthropic model to use"
    )
    anthropic_max_tokens: int = Field(
        default=2000,
        alias="ANTHROPIC_MAX_TOKENS",
        description="Maximum tokens for Anthropic response"
    )
    
    # GitHub Configuration
    github_token: str = Field(
        default="",
        alias="GITHUB_TOKEN",
        description="GitHub personal access token"
    )
    
    # General Configuration
    timeout: int = Field(
        default=30,
        alias="TIMEOUT",
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        alias="MAX_RETRIES",
        description="Maximum retry attempts for API calls"
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    def get_api_key(self) -> str:
        """Get API key for the configured provider"""
        if self.provider == LLMProvider.OPENAI:
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Set OPENAI_API_KEY environment variable"
                )
            return self.openai_api_key
        elif self.provider == LLMProvider.ANTHROPIC:
            if not self.anthropic_api_key:
                raise ValueError(
                    "Anthropic API key not configured. "
                    "Set ANTHROPIC_API_KEY environment variable"
                )
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    @classmethod
    def load_from_env(cls) -> "LLMConfig":
        """Load configuration from environment variables"""
        return cls()
    
    def validate_provider_config(self) -> bool:
        """Validate that provider-specific config is complete"""
        if self.provider == LLMProvider.OPENAI:
            return bool(self.openai_api_key and self.openai_model)
        elif self.provider == LLMProvider.ANTHROPIC:
            return bool(self.anthropic_api_key and self.anthropic_model)
        return False
