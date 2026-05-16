"""
工具基类 - 所有工具继承此类
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any

from agent.session import Session


class BaseTool(ABC):
    """工具基类
    
    所有具体工具必须继承此类并实现：
    - name: 工具名称（唯一标识）
    - description: 工具描述
    - is_dangerous: 是否为危险操作（默认False）
    - execute(): 执行方法
    """
    
    name: str
    description: str
    is_dangerous: bool = False
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], session: Session) -> Any:
        """执行工具
        
        Args:
            params: 参数字典
            session: 当前会话
        
        Returns:
            执行结果
        """
        pass
    
    def get_json_schema(self) -> Dict[str, Any]:
        """获取JSON Schema用于参数验证
        
        默认返回空schema，子类可以重写
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
