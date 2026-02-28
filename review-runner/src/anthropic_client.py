"""
Anthropic Claude LLM Client Implementation

Provides integration with Anthropic's Claude API with automatic retry logic.
"""

from typing import Optional
import json
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type
)
from anthropic import Anthropic, RateLimitError, APIError
from src.llm_client import LLMClient


class AnthropicClient(LLMClient):
    """Anthropic Claude LLM Client Implementation"""
    
    def __init__(self, config):
        """
        Initialize Anthropic client.
        
        Args:
            config: LLMConfig instance with Anthropic settings
        """
        super().__init__(config)
        self.client = Anthropic(
            api_key=config.get_api_key(),
            timeout=config.timeout
        )
        self.model = config.anthropic_model
        self.max_tokens = config.anthropic_max_tokens
    
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError))
    )
    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Call Anthropic API with automatic retry on rate limits.
        
        Args:
            prompt: User message
            system_prompt: System-level instructions
            **kwargs: Additional parameters
        
        Returns:
            LLM response
        
        Raises:
            APIError: If API call fails after retries
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt or "",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            timeout=self.timeout,
            **kwargs
        )
        
        return response.content[0].text
    
    def validate_connection(self) -> bool:
        """
        Validate Anthropic connection by attempting a simple request.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "OK"
                    }
                ]
            )
            return response is not None
        except Exception as e:
            print(f"Anthropic connection validation failed: {e}")
            return False
