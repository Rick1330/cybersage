"""
Agent Manager Module - Creates and manages CyberSage agents.

This module is responsible for initializing, configuring, and managing AI agents
that can perform various cybersecurity tasks using LangChain and custom tools.
"""

from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime
import logging
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools.base import BaseTool
from services.memory_service import MemoryService
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

class AgentNotFoundError(AgentError):
    """Raised when an agent with specified ID is not found."""
    pass

class AgentManager:
    def __init__(self, openai_service: OpenAIService, memory_service: MemoryService):
        self.openai_service = openai_service
        self.memory_service = memory_service
        self.agents: Dict[str, Any] = {}
        self.agent_metadata: Dict[str, Dict[str, Any]] = {}

    async def create_agent(
        self, 
        agent_id: str, 
        agent_type: str,
        tools: List[BaseTool],
        description: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Create a new agent with specified tools and configuration.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent to create
            tools: List of tools the agent can use
            description: Optional description of agent's purpose
            **kwargs: Additional configuration parameters
            
        Returns:
            The created agent instance
            
        Raises:
            ValueError: If agent_id already exists
            AgentError: If agent creation fails
        """
        if agent_id in self.agents:
            raise ValueError(f"Agent with ID {agent_id} already exists")

        try:
            llm = self.openai_service.get_llm()
            memory = self.memory_service.create_memory(agent_id)
            
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                memory=memory,
                verbose=True
            )
            
            self.agents[agent_id] = agent
            self.agent_metadata[agent_id] = {
                "type": agent_type,
                "description": description,
                "created_at": datetime.utcnow().isoformat(),
                "tool_count": len(tools),
                "status": "active"
            }
            
            logger.info(f"Created agent {agent_id} of type {agent_type}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {str(e)}")
            raise AgentError(f"Failed to create agent: {str(e)}") from e

    async def get_agent(self, agent_id: str) -> Any:
        """Retrieve an existing agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            
        Returns:
            The agent instance
            
        Raises:
            AgentNotFoundError: If agent doesn't exist
        """
        if agent_id not in self.agents:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        return self.agents[agent_id]

    async def execute_task(self, agent_id: str, task: str) -> str:
        """Execute a task using the specified agent.
        
        Args:
            agent_id: ID of the agent to use
            task: Task description to execute
            
        Returns:
            The result of the task execution
            
        Raises:
            AgentNotFoundError: If agent doesn't exist
            AgentError: If task execution fails
        """
        try:
            agent = await self.get_agent(agent_id)
            logger.info(f"Executing task with agent {agent_id}: {task[:100]}...")
            return await agent.arun(task)
        except AgentNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Task execution failed for agent {agent_id}: {str(e)}")
            raise AgentError(f"Task execution failed: {str(e)}") from e

    async def delete_agent(self, agent_id: str) -> None:
        """Delete an agent and clean up its resources.
        
        Args:
            agent_id: ID of the agent to delete
            
        Raises:
            AgentNotFoundError: If agent doesn't exist
        """
        if agent_id not in self.agents:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
            
        try:
            # Clean up memory
            await self.memory_service.clear_memory(agent_id)
            
            # Remove agent
            del self.agents[agent_id]
            del self.agent_metadata[agent_id]
            
            logger.info(f"Deleted agent {agent_id}")
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {str(e)}")
            raise AgentError(f"Failed to delete agent: {str(e)}") from e

    @asynccontextmanager
    async def agent_session(self, agent_id: str):
        """Context manager for using an agent within a session.
        
        Ensures proper cleanup of resources after use.
        
        Args:
            agent_id: ID of the agent to use in the session
            
        Yields:
            The agent instance
        """
        try:
            agent = await self.get_agent(agent_id)
            yield agent
        finally:
            # Perform any cleanup needed
            await self.memory_service.save_memory(agent_id)

    def get_agent_metadata(self, agent_id: str) -> Dict[str, Any]:
        """Get metadata about an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary containing agent metadata
            
        Raises:
            AgentNotFoundError: If agent doesn't exist
        """
        if agent_id not in self.agent_metadata:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        return self.agent_metadata[agent_id].copy()
