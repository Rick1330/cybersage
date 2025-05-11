"""
Test configuration and fixtures for the CyberSage test suite.
"""

import pytest
from typing import AsyncGenerator
import asyncio
from unittest.mock import Mock, AsyncMock
from services.openai_service import OpenAIService
from services.memory_service import MemoryService
from services.vectorstore_service import VectorStoreService
from core.agent_manager import AgentManager


@pytest.fixture
async def openai_service() -> AsyncGenerator[OpenAIService, None]:
    """Fixture for mocked OpenAI service."""
    service = OpenAIService(
        api_key="test_key",
        model="gpt-4",
        temperature=0.7
    )
    service.get_llm = Mock()
    service.generate_completion = AsyncMock()
    yield service


@pytest.fixture
async def memory_service() -> AsyncGenerator[MemoryService, None]:
    """Fixture for mocked Memory service."""
    service = MemoryService(redis_url="redis://localhost:6379")
    service.create_memory = AsyncMock()
    service.get_session = AsyncMock()
    service.update_session = AsyncMock()
    yield service


@pytest.fixture
async def vector_store() -> AsyncGenerator[VectorStoreService, None]:
    """Fixture for mocked Vector Store service."""
    service = VectorStoreService()
    service.initialize = AsyncMock()
    service.add_texts = AsyncMock()
    service.similarity_search = AsyncMock()
    yield service


@pytest.fixture
async def agent_manager(
    openai_service: OpenAIService,
    memory_service: MemoryService
) -> AsyncGenerator[AgentManager, None]:
    """Fixture for AgentManager with mocked dependencies."""
    manager = AgentManager(
        openai_service=openai_service,
        memory_service=memory_service
    )
    yield manager
