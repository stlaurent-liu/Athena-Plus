"""
终端命令执行工具
"""

import asyncio
from typing import Dict, Any

from tools.base import BaseTool
from agent.session import Session


class TerminalTool(BaseTool):
    """执行终端/命令行命令"""
    
    name = "terminal"
    description = "执行PowerShell/命令行命令"
    is_dangerous = True  # 终端命令默认危险，需要确认
    
    async def execute(self, params: Dict[str, Any], session: Session = None) -> Dict[str, Any]:
        """执行命令"""
        command = params.get("command")
        if not command:
            raise ValueError("Missing required parameter: command")
        
        cwd = params.get("cwd")
        
        logger = None
        if session and hasattr(session, 'metadata'):
            logger = session.metadata.get("logger", None)
        
        # Windows 使用 asyncio.create_subprocess_shell
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "command": command,
            "exit_code": process.returncode,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "success": process.returncode == 0
        }
    
    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的命令"
                },
                "cwd": {
                    "type": "string",
                    "description": "工作目录（可选）"
                }
            },
            "required": ["command"]
        }
