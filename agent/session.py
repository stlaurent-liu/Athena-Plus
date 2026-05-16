"""
会话管理 - 兼容 Hermes 记忆格式
"""

import uuid
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from athena.logger import logger
from athena.config import settings
from athena.constants import SessionStatus


@dataclass
class Message:
    """对话消息"""
    
    role: str  # user / assistant / system / tool
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典（兼容Hermes格式）"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """从字典创建"""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class Session:
    """对话会话"""
    
    session_id: str
    status: str = SessionStatus.INIT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> Message:
        """添加消息"""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg
    
    def to_dict(self) -> Dict:
        """转换为字典（兼容Hermes记忆格式）"""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [m.to_dict() for m in self.messages],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """从字典创建"""
        session = cls(
            session_id=data["session_id"],
            status=data.get("status", SessionStatus.INIT),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )
        session.messages = [Message.from_dict(m) for m in data["messages"]]
        return session


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.storage_dir = settings.data_dir / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_sessions()
    
    def create_session(self) -> Session:
        """创建新会话"""
        session_id = str(uuid.uuid4())[:8]
        session = Session(session_id=session_id)
        self.sessions[session_id] = session
        logger.debug(f"Created session {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Session]:
        """列出所有会话"""
        return list(self.sessions.values())
    
    def save_session(self, session: Session) -> bool:
        """保存会话到磁盘"""
        try:
            file_path = self.storage_dir / f"{session.session_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved session {session.session_id} to disk")
            return True
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id not in self.sessions:
            return False
        
        file_path = self.storage_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
        
        del self.sessions[session_id]
        logger.debug(f"Deleted session {session_id}")
        return True
    
    def _load_sessions(self) -> None:
        """从磁盘加载所有会话"""
        if not self.storage_dir.exists():
            return
        
        count = 0
        for json_file in self.storage_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = Session.from_dict(data)
                self.sessions[session.session_id] = session
                count += 1
            except Exception as e:
                logger.warning(f"Failed to load session {json_file}: {e}")
        
        logger.info(f"Loaded {count} sessions from storage")
