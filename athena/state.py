"""
全局状态管理
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict
from datetime import datetime

from athena.logger import logger


class AppState(Enum):
    """应用全局状态"""
    INIT = "init"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class GlobalState:
    """全局状态管理器"""
    
    app_state: AppState = AppState.INIT
    start_time: Optional[datetime] = None
    extra: Dict = field(default_factory=dict)
    
    @property
    def is_running(self) -> bool:
        return self.app_state == AppState.RUNNING
    
    def set_state(self, state: AppState) -> None:
        """设置应用状态"""
        if state == AppState.RUNNING and self.start_time is None:
            self.start_time = datetime.now()
        
        logger.debug(f"App state changed: {self.app_state} -> {state}")
        self.app_state = state
    
    def get_uptime(self) -> Optional[float]:
        """获取运行时长（秒）"""
        if self.start_time is None:
            return None
        return (datetime.now() - self.start_time).total_seconds()
    
    def set_extra(self, key: str, value) -> None:
        """设置额外状态"""
        self.extra[key] = value
    
    def get_extra(self, key: str, default=None):
        """获取额外状态"""
        return self.extra.get(key, default)


# 全局状态实例
global_state = GlobalState()
