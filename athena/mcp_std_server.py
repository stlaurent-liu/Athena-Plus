"""
Standard MCP HTTP Server - Model Context Protocol
https://spec.modelcontextprotocol.io/

Athena-Plus 标准MCP服务器
暴露所有本地工具给云端Gabriel调用
"""

import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

from athena.logger import logger
from athena.config import settings
from agent.executor import ToolExecutor


app = FastAPI(
    title="Athena-Plus MCP Server",
    description="Standard MCP Server for Windows local tools",
    version="0.1.0"
)

tool_executor = ToolExecutor()


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = None


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> Response:
    """标准MCP JSON-RPC端点"""
    try:
        body = await request.json()
        req = JSONRPCRequest(**body)
        
        response = await handle_jsonrpc_request(req)
        return Response(
            content=json.dumps(response),
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return Response(
            content=json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }),
            media_type="application/json",
            status_code=500
        )


async def handle_jsonrpc_request(req: JSONRPCRequest) -> Dict[str, Any]:
    """处理JSON-RPC请求"""
    
    if req.method == "initialize":
        # 初始化握手
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "athena-plus",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "tools": {},
                }
            }
        }
    
    elif req.method == "tools/list":
        # 列出所有可用工具
        tools = tool_executor.list_available_tools()
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {
                "tools": tools
            }
        }
    
    elif req.method == "tools/call":
        # 调用工具
        params = req.params or {}
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not name:
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "error": {
                    "code": -32602,
                    "message": "Missing tool name"
                }
            }
        
        try:
            # 工具执行
            # 这里session_id可以传空，因为工具执行不需要会话状态
            result = await tool_executor.execute(name, arguments, None)
            
            # 转换为MCP内容格式
            content = [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }
            ]
            
            # ========== 感知-动作闭环：自动截图 ==========
            # 对Windows-MCP交互工具，执行后自动截图，供云端AI视觉分析
            interactive_tools = [
                "windows-mcp_click", "windows-mcp_move", "windows-mcp_drag", 
                "windows-mcp_scroll", "windows-mcp_type", "windows-mcp_key", 
                "windows-mcp_shortcut", "windows-mcp_launch_app", 
                "windows-mcp_switch_app", "windows-mcp_resize_app"
            ]
            if name in interactive_tools:
                # 调用截图工具
                screenshot_result = await tool_executor.execute(
                    "windows-mcp_take_screenshot",
                    {},
                    None
                )
                # 提取截图路径加到返回结果
                if screenshot_result.get("success", False):
                    # 解析结果文本
                    try:
                        import ast
                        screenshot_text = screenshot_result.get("result", "")
                        if isinstance(screenshot_text, str):
                            # 尝试提取路径
                            import re
                            match = re.search(r'(([A-Za-z]:)?\\[^\\/:*?"<>|\r\n]+)+\.png', screenshot_text)
                            if match:
                                screenshot_path = match.group(0)
                                result["screenshot_path"] = screenshot_path
                                content.append({
                                    "type": "text", 
                                    "text": f"\n[Auto-screenshot saved to: {screenshot_path}]"
                                })
                    except Exception:
                        pass  # 忽略提取错误
            
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "result": {
                    "content": content,
                    "is_error": not result.get("success", False)
                }
            }
        except Exception as e:
            logger.error(f"Tool execution error: {name} - {e}")
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "error": {
                    "code": -32000,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    elif req.method == "shutdown":
        # 关闭服务端（可选，不处理）
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "result": {}
        }
    
    else:
        # 未知方法
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {req.method}"
            }
        }


@app.get("/")
async def root():
    """健康检查"""
    tools = tool_executor.list_available_tools()
    return {
        "name": "Athena-Plus MCP Server",
        "status": "running",
        "tools_count": len(tools),
        "mode": settings.mode
    }


@app.get("/ping")
async def ping():
    """ping 健康检查"""
    return {"ping": "pong", "status": "ok"}
