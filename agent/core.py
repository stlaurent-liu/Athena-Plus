"""
核心 Agent 类

原生 Windows AI Agent - 不依赖 Linux 版 Hermes
"""

from typing import List, Dict, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

from athena.logger import logger
from athena.config import settings
from athena.constants import SessionStatus
from agent.session import Session, SessionManager
from agent.executor import ToolExecutor
from agent.mcp_client import GabrielMCPClient
from agent.llm_client import LLMClient


@dataclass
class AgentConfig:
    """Agent 配置"""
    
    enable_cloud_mcp: bool = True
    auto_save_session: bool = True


class Agent:
    """核心 AI Agent - Windows 原生实现
    
    支持两种模式：
    - mcp-client: 所有推理走云端 Gabriel MCP，本地只执行工具
    - standalone: 本地独立推理，自己配置LLM API，不依赖云端
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.session_manager = SessionManager()
        self.tool_executor = ToolExecutor()
        
        # 根据模式初始化
        self.mode = settings.mode
        self.mcp_client: Optional[GabrielMCPClient] = None
        self.llm_client: Optional[LLMClient] = None
        
        if self.mode == "mcp-client":
            self._init_mcp_client()
            logger.info(f"Agent initialized in mcp-client mode")
        elif self.mode == "standalone":
            self._init_llm_client()
            logger.info(f"Agent initialized in standalone mode: model={settings.llm_model}")
        else:
            logger.error(f"Unknown mode: {self.mode}, falling back to mcp-client")
            self._init_mcp_client()
        
        logger.info(f"Agent initialized: mode={self.mode}")
    
    def _init_mcp_client(self) -> None:
        """初始化 MCP 客户端"""
        try:
            self.mcp_client = GabrielMCPClient(
                base_url=settings.gabriel_mcp_url,
                api_key=settings.gabriel_mcp_api_key
            )
            logger.info("Cloud Gabriel MCP client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            self.mcp_client = None
    
    def _init_llm_client(self) -> None:
        """初始化独立推理 LLM 客户端"""
        try:
            self.llm_client = LLMClient()
            logger.info("Standalone LLM client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self.llm_client = None
    
    def create_session(self) -> Session:
        """创建新会话"""
        session = self.session_manager.create_session()
        logger.debug(f"Created new session: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.session_manager.get_session(session_id)
    
    def list_sessions(self) -> List[Session]:
        """列出所有会话"""
        return self.session_manager.list_sessions()
    
    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """聊天交互
        
        - mcp-client 模式：所有推理走云端 Gabriel MCP
        - standalone 模式：本地独立推理
        """
        
        # 获取或创建会话
        if session_id:
            session = self.get_session(session_id)
            if not session:
                yield {"type": "error", "content": f"Session {session_id} not found"}
                return
        else:
            session = self.create_session()
        
        session.add_message("user", message)
        logger.debug(f"Session {session.session_id}: user message added")
        
        if self.mode == "mcp-client" and self.mcp_client:
            # 走云端 Gabriel MCP 推理
            try:
                async for chunk in self.mcp_client.stream_chat(session):
                    yield chunk
                logger.debug(f"Session {session.session_id}: MCP completed")
            except Exception as e:
                logger.error(f"MCP chat failed: {e}")
                yield {"type": "error", "content": f"MCP error: {str(e)}"}
        elif self.mode == "standalone" and self.llm_client:
            # 本地独立推理
            try:
                # 转换消息格式
                messages = [
                    {"role": m.role, "content": m.content}
                    for m in session.messages
                ]
                
                buffer = ""
                first_chunk = True
                async for chunk in self.llm_client.chat_stream(messages):
                    if "error" in chunk:
                        yield {"type": "error", "content": chunk["error"]}
                        break
                    
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        buffer += content
                        # 积累一点缓冲再输出，减少网络小包，显得更快
                        if len(buffer) >= 10 or content.endswith((" ", "\n", ".", "，", "。")):
                            if first_chunk:
                                # 第一条内容，开始记录回复
                                session.add_message("assistant", "")
                                first_chunk = False
                            # 追加到会话
                            session.messages[-1].content += buffer
                            yield {"type": "chunk", "content": buffer}
                            buffer = ""
                
                logger.debug(f"Session {session.session_id}: Standalone inference completed")
            except Exception as e:
                logger.error(f"Standalone chat failed: {e}")
                yield {"type": "error", "content": f"LLM error: {str(e)}"}
        else:
            yield {"type": "error", "content": f"No inference client available (mode={self.mode}) - check your configuration"}
        
        # 保存会话
        if self.config.auto_save_session:
            self.session_manager.save_session(session)
    
    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """执行工具"""
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}
        
        try:
            result = await self.tool_executor.execute(tool_name, params, session)
            logger.info(f"Tool {tool_name} executed successfully for session {session_id}")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {"success": False, "error": str(e)}
