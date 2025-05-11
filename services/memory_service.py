"""
Memory Service - Manages persistent memory for agent sessions.

This service provides an interface for storing and retrieving conversation history,
agent state, and semantic memory using Redis as the backend storage.
"""

import json
import logging
from typing import Optional, Dict, Any, List
import redis.asyncio as redis
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory

logger = logging.getLogger(__name__)

class MemoryServiceError(Exception):
    """Base exception for memory service related errors."""
    pass

class MemoryService:
    def __init__(
        self,
        redis_url: str,
        ttl: int = 3600,  # 1 hour default TTL
        namespace: str = "cybersage"
    ):
        """Initialize the memory service.
        
        Args:
            redis_url: Redis connection URL
            ttl: Time-to-live for session data in seconds
            namespace: Namespace for Redis keys
        """
        try:
            self.redis = redis.from_url(redis_url)
            self.ttl = ttl
            self.namespace = namespace
            self._validate_connection()
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise MemoryServiceError(f"Redis initialization failed: {str(e)}") from e

    async def _validate_connection(self) -> None:
        """Validate Redis connection is working."""
        try:
            await self.redis.ping()
        except Exception as e:
            raise MemoryServiceError(f"Redis connection failed: {str(e)}") from e

    def _get_key(self, key_type: str, identifier: str) -> str:
        """Generate a namespaced Redis key.
        
        Args:
            key_type: Type of key (e.g., 'session', 'history')
            identifier: Unique identifier
            
        Returns:
            Namespaced Redis key
        """
        return f"{self.namespace}:{key_type}:{identifier}"

    async def create_memory(self, session_id: str) -> ConversationBufferMemory:
        """Create a new memory instance for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Configured ConversationBufferMemory instance
            
        Raises:
            MemoryServiceError: If memory creation fails
        """
        try:
            # Create Redis-backed message history
            message_history = RedisChatMessageHistory(
                url=self.redis.connection_pool.connection_kwargs['url'],
                ttl=self.ttl,
                session_id=self._get_key("history", session_id)
            )

            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                chat_memory=message_history
            )

            # Initialize session metadata
            session_data = {
                "created_at": datetime.utcnow().isoformat(),
                "last_access": datetime.utcnow().isoformat(),
                "message_count": 0
            }
            
            await self.redis.setex(
                self._get_key("session", session_id),
                self.ttl,
                json.dumps(session_data)
            )

            return memory

        except Exception as e:
            logger.error(f"Failed to create memory for session {session_id}: {str(e)}")
            raise MemoryServiceError(f"Memory creation failed: {str(e)}") from e

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None if not found
            
        Raises:
            MemoryServiceError: If retrieval fails
        """
        try:
            data = await self.redis.get(self._get_key("session", session_id))
            if data:
                session_data = json.loads(data)
                # Update last access time
                session_data["last_access"] = datetime.utcnow().isoformat()
                await self.update_session(session_id, session_data)
                return session_data
            return None
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            raise MemoryServiceError(f"Session retrieval failed: {str(e)}") from e

    async def update_session(
        self,
        session_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Update session data in Redis.
        
        Args:
            session_id: Session identifier
            data: Updated session data
            
        Raises:
            MemoryServiceError: If update fails
        """
        try:
            await self.redis.setex(
                self._get_key("session", session_id),
                self.ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {str(e)}")
            raise MemoryServiceError(f"Session update failed: {str(e)}") from e

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and its associated data.
        
        Args:
            session_id: Session identifier
            
        Raises:
            MemoryServiceError: If deletion fails
        """
        try:
            # Delete session metadata and history
            await self.redis.delete(
                self._get_key("session", session_id),
                self._get_key("history", session_id)
            )
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            raise MemoryServiceError(f"Session deletion failed: {str(e)}") from e

    async def extend_session(self, session_id: str) -> None:
        """Extend the TTL of a session and its data.
        
        Args:
            session_id: Session identifier
            
        Raises:
            MemoryServiceError: If extension fails
        """
        try:
            # Extend TTL for both session and history
            await self.redis.expire(self._get_key("session", session_id), self.ttl)
            await self.redis.expire(self._get_key("history", session_id), self.ttl)
        except Exception as e:
            logger.error(f"Failed to extend session {session_id}: {str(e)}")
            raise MemoryServiceError(f"Session extension failed: {str(e)}") from e

    async def list_sessions(self) -> List[str]:
        """List all active sessions.
        
        Returns:
            List of active session IDs
            
        Raises:
            MemoryServiceError: If listing fails
        """
        try:
            keys = await self.redis.keys(f"{self.namespace}:session:*")
            return [key.decode().split(":")[-1] for key in keys]
        except Exception as e:
            logger.error(f"Failed to list sessions: {str(e)}")
            raise MemoryServiceError(f"Session listing failed: {str(e)}") from e

    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to return
            
        Returns:
            List of conversation messages
            
        Raises:
            MemoryServiceError: If history retrieval fails
        """
        try:
            message_history = RedisChatMessageHistory(
                url=self.redis.connection_pool.connection_kwargs['url'],
                ttl=self.ttl,
                session_id=self._get_key("history", session_id)
            )
            
            messages = await message_history.messages
            if limit is not None:
                messages = messages[-limit:]
                
            return [
                {
                    "role": msg.type,
                    "content": msg.content,
                    "timestamp": msg.additional_kwargs.get("timestamp")
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Failed to get history for session {session_id}: {str(e)}")
            raise MemoryServiceError(f"History retrieval failed: {str(e)}") from e

    async def clear_conversation_history(self, session_id: str) -> None:
        """Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Raises:
            MemoryServiceError: If clearing fails
        """
        try:
            message_history = RedisChatMessageHistory(
                url=self.redis.connection_pool.connection_kwargs['url'],
                ttl=self.ttl,
                session_id=self._get_key("history", session_id)
            )
            await message_history.clear()
            
            # Reset message count in session metadata
            session_data = await self.get_session(session_id)
            if session_data:
                session_data["message_count"] = 0
                await self.update_session(session_id, session_data)
                
        except Exception as e:
            logger.error(f"Failed to clear history for session {session_id}: {str(e)}")
            raise MemoryServiceError(f"History clearing failed: {str(e)}") from e
