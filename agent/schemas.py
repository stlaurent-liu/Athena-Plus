from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class ToolDefinition(BaseModel):
    """Tool definition following MCP format"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    
    def to_mcp(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class ToolCall(BaseModel):
    """Incoming tool call"""
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    """Result of tool execution"""
    success: bool
    content: Optional[Any] = None
    error: Optional[str] = None
