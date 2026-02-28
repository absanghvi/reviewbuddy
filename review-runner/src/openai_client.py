"""
OpenAI LLM Client Implementation

Provides integration with OpenAI's API with automatic retry logic for rate limits.
"""

from typing import Optional
import json
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type
)
from openai import OpenAI, RateLimitError, APIError
from src.llm_client import LLMClient


class OpenAIClient(LLMClient):
    """OpenAI LLM Client Implementation"""
    
    def __init__(self, config):
        """
        Initialize OpenAI client.
        
        Args:
            config: LLMConfig instance with OpenAI settings
        """
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.get_api_key(),
            timeout=config.timeout
        )
        self.model = config.openai_model
        self.temperature = config.openai_temperature
        self.max_tokens = config.openai_max_tokens
    
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APIError))
    )
    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Call OpenAI API with automatic retry on rate limits.
        
        Args:
            prompt: User message
            system_prompt: System-level instructions
            temperature: Override default temperature
            **kwargs: Additional parameters (e.g., top_p, presence_penalty)
        
        Returns:
            LLM response
        
        Raises:
            APIError: If API call fails after retries
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    def validate_connection(self) -> bool:
        """
        Validate OpenAI connection by listing available models.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            response = self.client.models.list()
            return len(response.data) > 0
        except Exception as e:
            print(f"OpenAI connection validation failed: {e}")
            return False
