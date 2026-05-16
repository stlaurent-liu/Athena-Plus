"""
FastAPI 后端服务器
"""

import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncGenerator

from athena.logger import logger
from athena.config import settings
from agent.core import Agent
from agent.session import Session

# 创建FastAPI应用
app = FastAPI(
    title="Athena-Plus API",
    description="Native Windows AI Agent API",
    version="0.1.0"
)

# 全局Agent实例
agent = Agent()


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: Optional[str] = None


class OpenAIChatRequest(BaseModel):
    """OpenAI 兼容聊天请求 - 适配前端"""
    model: str
    messages: List[Dict[str, Any]]
    temperature: Optional[float] = 0.9
    stream: Optional[bool] = True


class ToolExecuteRequest(BaseModel):
    """工具执行请求"""
    tool_name: str
    params: Dict[str, Any]
    session_id: str


@app.get("/")
async def root():
    """根路径 - 重定向到前端聊天页面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")


@app.get("/api")
async def api_root():
    """API根路径"""
    return {"name": "Athena-Plus API", "version": "0.1.0", "status": "running"}


@app.get("/ping")
async def ping():
    """健康检查"""
    return {"ping": "pong", "status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """流式聊天接口"""
    
    async def stream_response() -> AsyncGenerator[str, None]:
        async for chunk in agent.chat(request.message, request.session_id):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: OpenAIChatRequest):
    """OpenAI 兼容的聊天补全接口 - 适配前端"""
    # 提取最后一条用户消息
    last_message = None
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            last_message = msg.get("content", "")
            break
    
    if not last_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    # 转换为 SSE 流式输出（OpenAI 兼容格式）
    async def stream_response() -> AsyncGenerator[str, None]:
        async for chunk in agent.chat(last_message, None):
            # 封装成 OpenAI SSE 格式
            openai_chunk = {
                "id": "athena-" + str(hash(last_message)),
                "object": "chat.completion.chunk",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [
                    {
                        "delta": {
                            "content": chunk.get("content", "") if isinstance(chunk, dict) else chunk
                        },
                        "index": 0,
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(openai_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )


@app.post("/api/tool/execute")
async def execute_tool(request: ToolExecuteRequest):
    """执行工具"""
    result = await agent.execute_tool(
        request.tool_name,
        request.params,
        request.session_id
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Execution failed"))
    return result


@app.get("/api/sessions")
async def list_sessions():
    """列出所有会话"""
    sessions = agent.list_sessions()
    return {"sessions": [s.to_dict() for s in sessions]}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话"""
    session = agent.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = agent.session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@app.get("/api/tools")
async def list_tools():
    """列出所有可用工具"""
    tools = agent.tool_executor.list_available_tools()
    return {"tools": tools}


@app.get("/api/skills")
async def list_skills():
    """列出所有技能"""
    from skills.loader import SkillLoader
    loader = SkillLoader()
    return {"skills": loader.list_skills()}


# 挂载静态文件（前端UI）
from pathlib import Path
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
