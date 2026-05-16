"""
文件操作工具
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from tools.base import BaseTool
from agent.session import Session


class ReadFileTool(BaseTool):
    """读取文件内容"""
    
    name = "read_file"
    description = "读取文本文件内容"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        path_str = params.get("path")
        if not path_str:
            raise ValueError("Missing required parameter: path")
        
        path = Path(path_str)
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        
        if not path.is_file():
            return {"success": False, "error": f"Not a file: {path}"}
        
        try:
            content = path.read_text(encoding="utf-8")
            return {
                "success": True,
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "content": content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径（绝对路径或相对路径）"
                }
            },
            "required": ["path"]
        }


class WriteFileTool(BaseTool):
    """写入文件内容"""
    
    name = "write_file"
    description = "写入文本内容到文件"
    is_dangerous = True  # 写入文件可能覆盖，标记危险
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        path_str = params.get("path")
        content = params.get("content")
        
        if not path_str or content is None:
            raise ValueError("Missing required parameters: path and content")
        
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            path.write_text(content, encoding="utf-8")
            return {
                "success": True,
                "path": str(path),
                "bytes_written": len(content.encode("utf-8"))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目标文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的文本内容"
                }
            },
            "required": ["path", "content"]
        }


class ListDirectoryTool(BaseTool):
    """列出目录内容"""
    
    name = "list_directory"
    description = "列出目录下的文件和子目录"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        path_str = params.get("path", ".")
        path = Path(path_str)
        
        if not path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "path": str(item),
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else None
            })
        
        return {
            "success": True,
            "path": str(path),
            "items": items,
            "count": len(items)
        }
    
    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目录路径，默认为当前目录"
                }
            }
        }
