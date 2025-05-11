"""
API Schemas Module

This module defines the Pydantic models for request/response validation.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class AgentConfig(BaseModel):
    """Configuration for creating a new agent."""
    agent_id: str
    agent_type: str
    tools: List[str]
    options: Optional[Dict[str, Any]] = None


class TaskRequest(BaseModel):
    """Request model for executing a task."""
    task_id: str
    agent_id: str
    task: str
    parameters: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Response model for task execution results."""
    task_id: str
    result: Any
    timestamp: datetime = datetime.utcnow()
    status: str = "completed"


class SessionResponse(BaseModel):
    """Response model for session information."""
    session_id: str
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
