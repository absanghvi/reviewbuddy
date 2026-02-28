"""
Abstract Base Class for LLM Providers

This module defines the interface that all LLM client implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMClient(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config):
        """
        Initialize LLM client with configuration.
        
        Args:
            config: LLMConfig instance with provider-specific settings
        """
        self.config = config
        self.timeout = config.timeout
        self.max_retries = config.max_retries
    
    @abstractmethod
    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Make a call to the LLM with the given prompt.
        
        Args:
            prompt: The user message/prompt
            system_prompt: Optional system-level instructions
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLM response as string
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the LLM connection is working.
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass
