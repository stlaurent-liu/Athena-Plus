"""
工具执行器 - 安全沙箱+危险确认
"""

from typing import Dict, Any, Optional, List, Type
from abc import ABC, abstractmethod
import asyncio
import shlex

from athena.logger import logger
from athena.config import settings
from athena.constants import ExecutionStatus
from agent.session import Session


class BaseTool(ABC):
    """工具基类"""
    
    name: str
    description: str
    is_dangerous: bool = False
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], session: Session) -> Any:
        """执行工具"""
        pass
    
    def get_schema(self) -> Dict:
        """获取参数 schema"""
        return {}


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
    
    def register(self, tool_cls: Type[BaseTool]) -> None:
        """注册工具"""
        self._tools[tool_cls.name] = tool_cls
        logger.debug(f"Registered tool: {tool_cls.name}")
    
    def get_tool(self, name: str) -> Optional[Type[BaseTool]]:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [
            {
                "name": cls.name,
                "description": cls.description,
                "is_dangerous": cls.is_dangerous
            }
            for cls in self._tools.values()
        ]


class ToolExecutor:
    """工具执行器"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self._load_builtin_tools()
        logger.info(f"Tool executor initialized, {len(self.registry._tools)} tools registered")
    
    def _load_builtin_tools(self) -> None:
        """加载内置工具"""
        # 延迟导入避免循环依赖
        from tools.files.files import ReadFileTool, WriteFileTool, ListDirectoryTool
        from tools.terminal.terminal import TerminalTool
        from tools.system.system import SystemInfoTool, ListProcessesTool
        from tools.windows.windows_tools import WindowsNotificationTool, GetWindowsInfoTool, WindowsRegistryTool, WindowsPowerTool
        from tools.ollama.ollama import OllamaListModelsTool, OllamaPullModelTool, OllamaGenerateTool
        
        # 注册所有内置工具
        self.register_tool(ReadFileTool)
        self.register_tool(WriteFileTool)
        self.register_tool(ListDirectoryTool)
        self.register_tool(TerminalTool)
        self.register_tool(SystemInfoTool)
        self.register_tool(ListProcessesTool)
        self.register_tool(WindowsNotificationTool)
        self.register_tool(GetWindowsInfoTool)
        self.register_tool(WindowsRegistryTool)
        self.register_tool(WindowsPowerTool)
        self.register_tool(OllamaListModelsTool)
        self.register_tool(OllamaPullModelTool)
        self.register_tool(OllamaGenerateTool)
        
        # 加载第三方MCP服务器
        from agent.mcp_client_manager import mcp_manager
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(mcp_manager.connect_all(self))
    
    def register_tool(self, tool_cls: Type[BaseTool]) -> None:
        """注册工具"""
        self.registry.register(tool_cls)
    
    async def execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        session: Session,
        skip_confirmation: bool = False
    ) -> Any:
        """执行工具"""
        tool_cls = self.registry.get_tool(tool_name)
        if not tool_cls:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # 危险操作确认
        if tool_cls.is_dangerous and settings.enable_dangerous_command_confirmation and not skip_confirmation:
            logger.warning(f"Dangerous tool {tool_name} execution requires confirmation")
            raise PermissionError(f"Dangerous operation '{tool_name}' requires explicit confirmation")
        
        # 检查命令白名单（针对终端工具）
        if tool_name == "terminal" and "command" in params:
            cmd = params["command"]
            first_word = shlex.split(cmd)[0] if cmd else ""
            if first_word not in settings.allowed_commands:
                logger.warning(f"Command '{first_word}' not in allowed list")
                raise PermissionError(f"Command '{first_word}' is not allowed")
        
        # 实例化并执行
        tool = tool_cls()
        logger.debug(f"Executing tool: {tool_name} with params: {params}")
        
        result = await tool.execute(params, session)
        logger.debug(f"Tool {tool_name} execution completed")
        
        return result
    
    def list_available_tools(self) -> List[Dict]:
        """列出所有可用工具"""
        return self.registry.list_tools()