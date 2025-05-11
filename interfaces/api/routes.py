"""
API Routes Module

This module defines the API endpoints and their handlers.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from .schemas import (
    TaskRequest,
    TaskResponse,
    AgentConfig,
    SessionResponse
)
from core.agent_manager import AgentManager
from services.memory_service import MemoryService

router = APIRouter()

@router.post("/agents", response_model=Dict[str, str])
async def create_agent(config: AgentConfig):
    """Create a new agent with specified configuration."""
    try:
        agent_id = await agent_manager.create_agent(
            agent_id=config.agent_id,
            agent_type=config.agent_type,
            tools=config.tools
        )
        return {"agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute a task using a specified agent."""
    try:
        result = await agent_manager.execute_task(
            request.agent_id,
            request.task
        )
        return TaskResponse(
            task_id=request.task_id,
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions():
    """List all active sessions."""
    try:
        sessions = await memory_service.list_sessions()
        return [
            SessionResponse(session_id=s)
            for s in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated data."""
    try:
        await memory_service.delete_session(session_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
