"""
MCP Server - 纯粹MCP服务端
暴露本地工具给云端Gabriel调用
"""

import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from athena.logger import logger
from athena.config import settings
from agent.core import Agent
from agent.executor import ToolExecutor


app = FastAPI(
    title="Athena-Plus MCP Server",
    description="Windows Local Tools MCP Server for Cloud Gabriel",
    version="0.1.0"
)

# 全局Agent实例
agent = Agent()
tool_executor = ToolExecutor()


class MCPRequest(BaseModel):
    """MCP 工具调用请求"""
    tool_name: str
    params: Dict[str, Any]
    session_id: Optional[str] = None


@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": "Athena-Plus MCP Server",
        "mode": "mcp-server",
        "status": "running",
        "tools_count": len(tool_executor.list_available_tools())
    }


@app.get("/ping")
async def ping():
    """ping 健康检查"""
    return {"ping": "pong", "status": "ok"}


@app.get("/mcp/tools")
async def list_tools():
    """列出所有可用工具"""
    tools = tool_executor.list_available_tools()
    return {"tools": tools}


@app.post("/mcp/execute")
async def execute_tool(request: MCPRequest):
    """执行工具"""
    try:
        if not request.session_id:
            # 创建临时会话
            session = agent.create_session()
            session_id = session.session_id
        else:
            session = agent.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
            session_id = request.session_id
        
        result = await agent.execute_tool(
            request.tool_name,
            request.params,
            session_id
        )
        
        return result
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions():
    """列出所有会话"""
    sessions = agent.list_sessions()
    return {"sessions": [s.to_dict() for s in sessions]}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = agent.session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {"success": True}