"""
Workflow Engine Service - Orchestrates security assessment workflows.

This service manages the execution of complex security assessment workflows,
coordinating multiple tools and maintaining state across steps.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from enum import Enum
import uuid

from core.context_manager import ContextManager, ContextType, SecurityLevel
from services.logging_service import LoggingService
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class WorkflowStepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    pass

class WorkflowStep:
    """Represents a single step in a workflow."""
    
    def __init__(
        self,
        name: str,
        tool: BaseTool,
        params: Dict[str, Any],
        conditions: Optional[List[Callable[..., bool]]] = None,
        retry_count: int = 3,
        timeout: int = 300,
        cleanup: Optional[Callable[..., Awaitable[None]]] = None
    ):
        """Initialize workflow step.
        
        Args:
            name: Step name
            tool: Tool to execute
            params: Parameters for tool execution
            conditions: Optional list of conditions that must be met
            retry_count: Number of retries on failure
            timeout: Step timeout in seconds
            cleanup: Optional cleanup function
        """
        self.name = name
        self.tool = tool
        self.params = params
        self.conditions = conditions or []
        self.retry_count = retry_count
        self.timeout = timeout
        self.cleanup = cleanup
        self.status = WorkflowStepStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

class SecurityWorkflow:
    """Represents a security assessment workflow."""
    
    def __init__(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep],
        context_manager: ContextManager,
        logging_service: LoggingService,
        security_level: SecurityLevel = SecurityLevel.HIGH
    ):
        """Initialize security workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps
            context_manager: Context manager instance
            logging_service: Logging service instance
            security_level: Security level for the workflow
        """
        self.workflow_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.steps = steps
        self.context_manager = context_manager
        self.logging_service = logging_service
        self.security_level = security_level
        self.status = WorkflowStatus.PENDING
        self.current_step = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.results: Dict[str, Any] = {}

    async def execute(self) -> Dict[str, Any]:
        """Execute the workflow.
        
        Returns:
            Dict containing workflow results
            
        Raises:
            WorkflowError: If workflow execution fails
        """
        try:
            self.start_time = datetime.utcnow()
            self.status = WorkflowStatus.RUNNING
            
            # Create workflow context
            context = await self.context_manager.create_context(
                self.workflow_id,
                ContextType.SECURITY_SCAN,
                self.security_level
            )
            
            # Log workflow start
            await self.logging_service.log_audit_event(
                self.workflow_id,
                "workflow_started",
                {
                    "name": self.name,
                    "description": self.description,
                    "security_level": self.security_level.value
                }
            )

            # Execute steps
            for i, step in enumerate(self.steps):
                self.current_step = i
                
                try:
                    # Check conditions
                    if not all(cond() for cond in step.conditions):
                        step.status = WorkflowStepStatus.SKIPPED
                        continue

                    # Execute step
                    step_result = await self._execute_step(step)
                    self.results[step.name] = step_result
                    
                    # Update context
                    await self.context_manager.update_context(
                        self.workflow_id,
                        {f"step_{i}_result": step_result}
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Step {step.name} failed: {str(e)}",
                        extra={"workflow_id": self.workflow_id}
                    )
                    step.status = WorkflowStepStatus.FAILED
                    step.error = str(e)
                    
                    # Attempt cleanup if provided
                    if step.cleanup:
                        try:
                            await step.cleanup()
                        except Exception as cleanup_error:
                            logger.error(
                                f"Cleanup for step {step.name} failed: {str(cleanup_error)}",
                                extra={"workflow_id": self.workflow_id}
                            )
                    
                    raise WorkflowError(f"Workflow failed at step {step.name}: {str(e)}")

            self.status = WorkflowStatus.COMPLETED
            self.end_time = datetime.utcnow()
            
            # Log workflow completion
            await self.logging_service.log_audit_event(
                self.workflow_id,
                "workflow_completed",
                {
                    "name": self.name,
                    "duration": (self.end_time - self.start_time).total_seconds(),
                    "steps_completed": len(self.steps)
                }
            )
            
            return self.get_results()
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.end_time = datetime.utcnow()
            
            # Log workflow failure
            await self.logging_service.log_audit_event(
                self.workflow_id,
                "workflow_failed",
                {
                    "name": self.name,
                    "error": str(e),
                    "step": self.current_step
                }
            )
            
            raise WorkflowError(f"Workflow execution failed: {str(e)}")

    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step.
        
        Args:
            step: Step to execute
            
        Returns:
            Step execution results
            
        Raises:
            WorkflowError: If step execution fails
        """
        step.start_time = datetime.utcnow()
        step.status = WorkflowStepStatus.RUNNING
        
        # Log step start
        await self.logging_service.log_audit_event(
            self.workflow_id,
            "step_started",
            {
                "step_name": step.name,
                "params": step.params
            }
        )

        tries = 0
        last_error = None
        
        while tries < step.retry_count:
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    step.tool.execute(**step.params),
                    timeout=step.timeout
                )
                
                step.status = WorkflowStepStatus.COMPLETED
                step.end_time = datetime.utcnow()
                step.result = result
                
                # Log step completion
                await self.logging_service.log_audit_event(
                    self.workflow_id,
                    "step_completed",
                    {
                        "step_name": step.name,
                        "duration": (step.end_time - step.start_time).total_seconds()
                    }
                )
                
                return result
                
            except asyncio.TimeoutError:
                last_error = f"Step timed out after {step.timeout} seconds"
            except Exception as e:
                last_error = str(e)
                
            tries += 1
            if tries < step.retry_count:
                await asyncio.sleep(2 ** tries)  # Exponential backoff

        step.status = WorkflowStepStatus.FAILED
        step.end_time = datetime.utcnow()
        step.error = last_error
        
        # Log step failure
        await self.logging_service.log_audit_event(
            self.workflow_id,
            "step_failed",
            {
                "step_name": step.name,
                "error": last_error,
                "retries": tries
            }
        )
        
        raise WorkflowError(
            f"Step {step.name} failed after {tries} attempts: {last_error}"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": len(self.steps),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "error": step.error
                }
                for step in self.steps
            ]
        }

    def get_results(self) -> Dict[str, Any]:
        """Get workflow results."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds()
            if self.end_time and self.start_time else None,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "start_time": step.start_time.isoformat()
                    if step.start_time else None,
                    "end_time": step.end_time.isoformat()
                    if step.end_time else None,
                    "duration": (step.end_time - step.start_time).total_seconds()
                    if step.end_time and step.start_time else None,
                    "result": step.result,
                    "error": step.error
                }
                for step in self.steps
            ],
            "results": self.results
        }

    async def cancel(self) -> None:
        """Cancel workflow execution."""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.CANCELLED
            self.end_time = datetime.utcnow()
            
            # Cancel current step if running
            current_step = self.steps[self.current_step]
            if current_step.status == WorkflowStepStatus.RUNNING:
                current_step.status = WorkflowStepStatus.FAILED
                current_step.end_time = datetime.utcnow()
                current_step.error = "Cancelled by user"
                
                # Attempt cleanup
                if current_step.cleanup:
                    try:
                        await current_step.cleanup()
                    except Exception as e:
                        logger.error(
                            f"Cleanup failed for cancelled step {current_step.name}: {str(e)}"
                        )
            
            # Log cancellation
            await self.logging_service.log_audit_event(
                self.workflow_id,
                "workflow_cancelled",
                {
                    "name": self.name,
                    "step": self.current_step
                }
            )

    async def pause(self) -> None:
        """Pause workflow execution."""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.PAUSED
            
            # Log pause
            await self.logging_service.log_audit_event(
                self.workflow_id,
                "workflow_paused",
                {
                    "name": self.name,
                    "step": self.current_step
                }
            )

    async def resume(self) -> None:
        """Resume workflow execution."""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.RUNNING
            
            # Log resume
            await self.logging_service.log_audit_event(
                self.workflow_id,
                "workflow_resumed",
                {
                    "name": self.name,
                    "step": self.current_step
                }
            )
            
            # Continue execution
            await self.execute()
