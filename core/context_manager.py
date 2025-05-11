"""
Context Manager Module - Handles session and security context for CyberSage.

This module manages conversation context, security state, and analytical context
between interactions, providing persistence and state management for agent sessions
with proper security tracking and audit logging.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from enum import Enum
from services.memory_service import MemoryService
from services.logging_service import LoggingService

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for context classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContextType(Enum):
    """Types of contexts that can be managed."""
    SECURITY_SCAN = "security_scan"
    THREAT_ANALYSIS = "threat_analysis"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE_CHECK = "compliance_check"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"

class ContextError(Exception):
    """Base exception for context-related errors."""
    pass

class ContextManager:
    def __init__(
        self,
        memory_service: MemoryService,
        logging_service: Optional[LoggingService] = None,
        context_ttl: int = 3600  # 1 hour default
    ):
        """Initialize the context manager.
        
        Args:
            memory_service: Service for persistent memory storage
            logging_service: Optional service for audit logging
            context_ttl: Time-to-live for context data in seconds
        """
        self.memory_service = memory_service
        self.logging_service = logging_service
        self.context_ttl = context_ttl
        self.active_contexts: Dict[str, Dict[str, Any]] = {}
        self.security_contexts: Dict[str, Set[str]] = {}  # Track security-sensitive sessions

    async def create_context(
        self,
        session_id: str,
        context_type: ContextType,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new context for a session.
        
        Args:
            session_id: Unique session identifier
            context_type: Type of context being created
            security_level: Security classification level
            metadata: Additional context metadata
            
        Returns:
            Created context dictionary
            
        Raises:
            ContextError: If context creation fails
        """
        try:
            # Initialize context structure
            context = {
                "session_id": session_id,
                "context_type": context_type.value,
                "security_level": security_level.value,
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "expiry": (datetime.utcnow() + timedelta(seconds=self.context_ttl)).isoformat(),
                "state": {
                    "status": "initialized",
                    "phase": "setup",
                    "artifacts": [],
                    "findings": [],
                    "alerts": []
                },
                "metadata": metadata or {},
                "memory": await self.memory_service.create_memory(session_id)
            }
            
            # Store context
            self.active_contexts[session_id] = context
            
            # Track security context if needed
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                self._add_security_context(session_id)
            
            # Audit log the creation
            await self._audit_log(
                session_id,
                "context_created",
                {"context_type": context_type.value, "security_level": security_level.value}
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create context for session {session_id}: {str(e)}")
            raise ContextError(f"Context creation failed: {str(e)}") from e

    async def get_context(
        self,
        session_id: str,
        validate_security: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve context for a session.
        
        Args:
            session_id: Session identifier
            validate_security: Whether to validate security requirements
            
        Returns:
            Context dictionary or None if not found
            
        Raises:
            ContextError: If security validation fails
        """
        try:
            # Check active contexts first
            context = self.active_contexts.get(session_id)
            
            if not context:
                # Try to load from persistent storage
                stored_context = await self.memory_service.get_session(session_id)
                if stored_context:
                    context = stored_context
                    self.active_contexts[session_id] = context
                    
                    # Restore security tracking if needed
                    if context.get("security_level") in [SecurityLevel.HIGH.value, SecurityLevel.CRITICAL.value]:
                        self._add_security_context(session_id)
            
            if context:
                # Validate expiry
                expiry = datetime.fromisoformat(context["expiry"])
                if datetime.utcnow() > expiry:
                    await self.clear_context(session_id)
                    return None
                
                # Validate security if required
                if validate_security and session_id in self.security_contexts:
                    await self._validate_security_context(session_id)
                
                # Update last access
                context["last_updated"] = datetime.utcnow().isoformat()
                
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context for session {session_id}: {str(e)}")
            raise ContextError(f"Context retrieval failed: {str(e)}") from e

    async def update_context(
        self,
        session_id: str,
        updates: Dict[str, Any],
        phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update context with new information.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of updates to apply
            phase: Optional new phase to set
            
        Returns:
            Updated context dictionary
            
        Raises:
            ContextError: If update fails or context not found
        """
        try:
            context = await self.get_context(session_id)
            if not context:
                raise ContextError(f"Context not found for session {session_id}")
            
            # Update state
            context["state"].update(updates)
            
            # Update phase if provided
            if phase:
                context["state"]["phase"] = phase
            
            context["last_updated"] = datetime.utcnow().isoformat()
            
            # Extend expiry
            context["expiry"] = (datetime.utcnow() + timedelta(seconds=self.context_ttl)).isoformat()
            
            # Persist updates
            await self.memory_service.update_session(session_id, context)
            
            # Audit log significant updates
            if "findings" in updates or "alerts" in updates:
                await self._audit_log(
                    session_id,
                    "context_updated",
                    {"updates": list(updates.keys())}
                )
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to update context for session {session_id}: {str(e)}")
            raise ContextError(f"Context update failed: {str(e)}") from e

    async def add_finding(
        self,
        session_id: str,
        finding: Dict[str, Any]
    ) -> None:
        """Add a security finding to the context.
        
        Args:
            session_id: Session identifier
            finding: Finding details
            
        Raises:
            ContextError: If adding finding fails
        """
        try:
            context = await self.get_context(session_id)
            if not context:
                raise ContextError(f"Context not found for session {session_id}")
            
            # Add timestamp to finding
            finding["timestamp"] = datetime.utcnow().isoformat()
            
            # Add to findings list
            context["state"]["findings"].append(finding)
            
            # Update context
            await self.update_context(session_id, {"findings": context["state"]["findings"]})
            
            # Audit log critical findings
            if finding.get("severity") in ["high", "critical"]:
                await self._audit_log(
                    session_id,
                    "critical_finding_added",
                    {"finding": finding}
                )
            
        except Exception as e:
            logger.error(f"Failed to add finding for session {session_id}: {str(e)}")
            raise ContextError(f"Adding finding failed: {str(e)}") from e

    async def clear_context(
        self,
        session_id: str,
        audit_reason: Optional[str] = None
    ) -> None:
        """Clear context for a session.
        
        Args:
            session_id: Session identifier
            audit_reason: Optional reason for clearing context
            
        Raises:
            ContextError: If clearing context fails
        """
        try:
            # Remove from active contexts
            if session_id in self.active_contexts:
                del self.active_contexts[session_id]
            
            # Remove security tracking
            if session_id in self.security_contexts:
                self.security_contexts[session_id].clear()
                del self.security_contexts[session_id]
            
            # Clear persistent storage
            await self.memory_service.delete_session(session_id)
            
            # Audit log the clearing
            await self._audit_log(
                session_id,
                "context_cleared",
                {"reason": audit_reason or "session_ended"}
            )
            
        except Exception as e:
            logger.error(f"Failed to clear context for session {session_id}: {str(e)}")
            raise ContextError(f"Context clearing failed: {str(e)}") from e

    def _add_security_context(self, session_id: str) -> None:
        """Add session to security context tracking."""
        if session_id not in self.security_contexts:
            self.security_contexts[session_id] = set()

    async def _validate_security_context(self, session_id: str) -> None:
        """Validate security requirements for a context."""
        # Implementation depends on specific security requirements
        pass

    async def _audit_log(
        self,
        session_id: str,
        action: str,
        details: Dict[str, Any]
    ) -> None:
        """Log an audit event if logging service is available."""
        if self.logging_service:
            await self.logging_service.log_audit_event(
                session_id=session_id,
                action=action,
                details=details
            )
