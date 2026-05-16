"""
MCP 客户端 - 对接云端 Gabriel
"""

import json
from typing import Dict, Any, AsyncGenerator, Optional
import httpx

from athena.logger import logger
from athena.config import settings
from athena.constants import DEFAULT_MCP_TIMEOUT
from agent.session import Session


class GabrielMCPClient:
    """云端 Gabriel MCP 客户端"""
    
    def __init__(
        self,
        base_url: str = settings.gabriel_mcp_url,
        api_key: Optional[str] = settings.gabriel_mcp_api_key,
        timeout: float = DEFAULT_MCP_TIMEOUT
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"
    
    async def stream_chat(self, session: Session) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天"""
        payload = {
            "session_id": session.session_id,
            "messages": [m.to_dict() for m in session.messages]
        }
        
        url = f"{self.base_url}/chat"
        logger.debug(f"Sending chat request to Gabriel MCP: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                    headers=self._headers
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            line = line[6:]
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            yield {"type": "chunk", "content": line}
        except Exception as e:
            logger.error(f"MCP chat request failed: {e}")
            yield {"type": "error", "content": f"MCP request failed: {str(e)}"}
    
    async def ping(self) -> bool:
        """Ping 检查连接"""
        try:
            url = f"{self.base_url}/ping"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self._headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False
    
    async def submit_tool_result(
        self,
        session_id: str,
        tool_name: str,
        result: Any,
        success: bool = True
    ) -> Dict[str, Any]:
        """提交工具执行结果回云端"""
        url = f"{self.base_url}/tool_result"
        payload = {
            "session_id": session_id,
            "tool_name": tool_name,
            "result": result,
            "success": success
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to submit tool result: {e}")
            return {"success": False, "error": str(e)}
