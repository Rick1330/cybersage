"""
Tests for the core services implementations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from services.openai_service import OpenAIService
from services.memory_service import MemoryService
from services.vectorstore_service import VectorStoreService
from services.logging_service import LoggingService


@pytest.mark.asyncio
async def test_openai_service_completion():
    """Test OpenAI service completion generation."""
    # Arrange
    service = OpenAIService(
        api_key="test_key",
        model="gpt-4"
    )
    
    with patch('openai.Completion.acreate') as mock_complete:
        mock_complete.return_value = Mock(
            choices=[Mock(text="Test response")],
            usage={"total_tokens": 10},
            model="gpt-4"
        )
        
        # Act
        result = await service.generate_completion("Test prompt")
        
        # Assert
        assert result["text"] == "Test response"
        assert "usage" in result
        assert result["model"] == "gpt-4"


@pytest.mark.asyncio
async def test_memory_service_session_management():
    """Test memory service session operations."""
    # Arrange
    service = MemoryService(redis_url="redis://localhost:6379")
    session_id = "test_session"
    test_data = {"key": "value"}
    
    # Act
    memory = await service.create_memory(session_id)
    await service.update_session(session_id, test_data)
    retrieved_data = await service.get_session(session_id)
    
    # Assert
    assert memory is not None
    assert retrieved_data == test_data


@pytest.mark.asyncio
async def test_vectorstore_service_operations():
    """Test vector store operations."""
    # Arrange
    service = VectorStoreService()
    test_texts = ["test document 1", "test document 2"]
    
    # Act
    await service.initialize()
    ids = await service.add_texts(test_texts)
    search_results = await service.similarity_search("test document")
    
    # Assert
    assert len(ids) == 2
    assert len(search_results) > 0


def test_logging_service_configuration():
    """Test logging service setup and configuration."""
    # Arrange
    service = LoggingService(
        config_path="configs/logging_config.yaml",
        app_name="test_app"
    )
    
    # Act
    logger = service.get_logger()
    
    # Assert
    assert logger is not None
    
    # Test error logging
    try:
        raise Exception("Test error")
    except Exception as e:
        service.log_error(e, {"context": "test"})
