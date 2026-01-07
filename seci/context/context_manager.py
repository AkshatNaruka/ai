"""
Context manager for maintaining conversation state and history.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a single message in the conversation."""
    
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ConversationContext:
    """Represents a conversation context with history and state."""
    
    session_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime = field(default_factory=lambda: datetime.now())
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the conversation."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Get messages, optionally limited to recent N messages."""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ContextManager:
    """
    Manages conversation contexts for multiple sessions.
    Stores and retrieves conversation history.
    """
    
    def __init__(self, max_history: int = 10, max_sessions: int = 1000):
        """
        Initialize context manager.
        
        Args:
            max_history: Maximum messages to keep per session
            max_sessions: Maximum number of sessions to maintain
        """
        self.max_history = max_history
        self.max_sessions = max_sessions
        self.contexts: Dict[str, ConversationContext] = {}
        
        logger.info(f"ContextManager initialized (max_history={max_history})")
    
    def get_or_create_context(self, session_id: str) -> ConversationContext:
        """
        Get existing context or create new one.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            ConversationContext for the session
        """
        if session_id not in self.contexts:
            logger.info(f"Creating new context for session: {session_id}")
            self.contexts[session_id] = ConversationContext(session_id=session_id)
            
            # Clean up old sessions if limit exceeded
            if len(self.contexts) > self.max_sessions:
                self._cleanup_old_sessions()
        
        return self.contexts[session_id]
    
    def add_user_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add a user message to the conversation."""
        context = self.get_or_create_context(session_id)
        context.add_message("user", content, metadata)
        self._trim_history(context)
        logger.debug(f"Added user message to session {session_id}")
    
    def add_assistant_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add an assistant message to the conversation."""
        context = self.get_or_create_context(session_id)
        context.add_message("assistant", content, metadata)
        self._trim_history(context)
        logger.debug(f"Added assistant message to session {session_id}")
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get context for a session."""
        return self.contexts.get(session_id)
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get conversation history for a session."""
        context = self.contexts.get(session_id)
        if not context:
            return []
        return context.get_messages(limit)
    
    def clear_context(self, session_id: str) -> None:
        """Clear context for a session."""
        if session_id in self.contexts:
            del self.contexts[session_id]
            logger.info(f"Cleared context for session: {session_id}")
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs."""
        return list(self.contexts.keys())
    
    def export_context(self, session_id: str) -> Optional[str]:
        """Export context as JSON string."""
        context = self.contexts.get(session_id)
        if not context:
            return None
        return json.dumps(context.to_dict(), indent=2)
    
    def _trim_history(self, context: ConversationContext) -> None:
        """Trim history to max_history messages."""
        if len(context.messages) > self.max_history:
            context.messages = context.messages[-self.max_history:]
    
    def _cleanup_old_sessions(self) -> None:
        """Remove oldest sessions to maintain max_sessions limit."""
        # Sort by updated_at and remove oldest
        sorted_sessions = sorted(
            self.contexts.items(),
            key=lambda x: x[1].updated_at
        )
        
        # Keep only max_sessions
        sessions_to_remove = sorted_sessions[:-self.max_sessions]
        for session_id, _ in sessions_to_remove:
            del self.contexts[session_id]
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
