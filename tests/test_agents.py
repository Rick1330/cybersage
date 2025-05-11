"""
Tests for the Agent Manager module.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from core.agent_manager import AgentManager
from tools.base_tool import BaseTool


@pytest.mark.asyncio
async def test_create_agent(agent_manager: AgentManager):
    """Test agent creation with valid parameters."""
    # Arrange
    agent_id = "test_agent"
    agent_type = "security_scanner"
    mock_tool = Mock(spec=BaseTool)
    
    # Act
    agent = await agent_manager.create_agent(
        agent_id=agent_id,
        agent_type=agent_type,
        tools=[mock_tool]
    )
    
    # Assert
    assert agent is not None
    assert agent_id in agent_manager.agents


@pytest.mark.asyncio
async def test_get_agent(agent_manager: AgentManager):
    """Test retrieving an existing agent."""
    # Arrange
    agent_id = "test_agent"
    mock_agent = AsyncMock()
    agent_manager.agents[agent_id] = mock_agent
    
    # Act
    retrieved_agent = await agent_manager.get_agent(agent_id)
    
    # Assert
    assert retrieved_agent == mock_agent


@pytest.mark.asyncio
async def test_execute_task(agent_manager: AgentManager):
    """Test task execution with an existing agent."""
    # Arrange
    agent_id = "test_agent"
    task = "scan 192.168.1.1"
    mock_agent = AsyncMock()
    mock_agent.arun.return_value = "Task completed successfully"
    agent_manager.agents[agent_id] = mock_agent
    
    # Act
    result = await agent_manager.execute_task(agent_id, task)
    
    # Assert
    assert result == "Task completed successfully"
    mock_agent.arun.assert_called_once_with(task)


@pytest.mark.asyncio
async def test_execute_task_nonexistent_agent(agent_manager: AgentManager):
    """Test task execution with a non-existent agent."""
    # Arrange
    agent_id = "nonexistent_agent"
    task = "scan 192.168.1.1"
    
    # Act & Assert
    with pytest.raises(ValueError, match=f"Agent {agent_id} not found"):
        await agent_manager.execute_task(agent_id, task)
