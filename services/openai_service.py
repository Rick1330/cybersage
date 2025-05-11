"""
OpenAI Service - Encapsulates OpenAI API interactions.

This service handles all interactions with OpenAI's API, providing a consistent
interface for model interactions, token management, rate limiting, and content safety.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import openai
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)

class OpenAIServiceError(Exception):
    """Base exception for OpenAI service related errors."""
    pass

class OpenAIService:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Initialize OpenAI service with configuration.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens per request
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.last_request: Optional[datetime] = None
        openai.api_key = api_key

    def get_llm(self) -> OpenAI:
        """Get a LangChain LLM instance."""
        return OpenAI(
            temperature=self.temperature,
            model_name=self.model,
            max_tokens=self.max_tokens,
            openai_api_key=self.api_key
        )

    def get_chat_model(self) -> ChatOpenAI:
        """Get a LangChain ChatModel instance."""
        return ChatOpenAI(
            temperature=self.temperature,
            model_name=self.model,
            max_tokens=self.max_tokens,
            openai_api_key=self.api_key
        )

    async def _handle_rate_limits(self) -> None:
        """Handle rate limiting between API calls."""
        if self.last_request:
            elapsed = datetime.now() - self.last_request
            if elapsed < timedelta(seconds=1):
                await asyncio.sleep(1 - elapsed.total_seconds())
        self.last_request = datetime.now()

    async def generate_completion(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a completion directly using OpenAI API.
        
        Args:
            prompt: Input text prompt
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary containing generated text and metadata
            
        Raises:
            OpenAIServiceError: If API request fails
        """
        try:
            await self._handle_rate_limits()
            
            response = await openai.Completion.acreate(
                engine=self.model,
                prompt=prompt,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
            )
            return {
                'text': response.choices[0].text,
                'usage': response.usage,
                'model': response.model
            }
        except Exception as e:
            logger.error(f"OpenAI API error in completion: {str(e)}")
            raise OpenAIServiceError(f"Completion generation failed: {str(e)}") from e

    async def create_embedding(self, text: str) -> List[float]:
        """Create an embedding vector for the given text.
        
        Args:
            text: Text to create embedding for
            
        Returns:
            List of embedding values
            
        Raises:
            OpenAIServiceError: If embedding creation fails
        """
        try:
            await self._handle_rate_limits()
            
            response = await openai.Embedding.acreate(
                input=text,
                model="text-embedding-ada-002"
            )
            
            return response["data"][0]["embedding"]
            
        except Exception as e:
            logger.error(f"Failed to create embedding: {str(e)}")
            raise OpenAIServiceError(f"Embedding creation failed: {str(e)}") from e

    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Check content against OpenAI's moderation endpoint.
        
        Args:
            text: Text to moderate
            
        Returns:
            Dictionary containing moderation results
            
        Raises:
            OpenAIServiceError: If moderation check fails
        """
        try:
            await self._handle_rate_limits()
            
            response = await openai.Moderation.acreate(input=text)
            return response["results"][0]
            
        except Exception as e:
            logger.error(f"Content moderation failed: {str(e)}")
            raise OpenAIServiceError(f"Content moderation failed: {str(e)}") from e

    def validate_api_key(self) -> bool:
        """Validate that the API key is working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            openai.Model.list()
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False
