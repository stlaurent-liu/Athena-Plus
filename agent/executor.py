"""
Tool executor for MCP - loads all available tools and executes them
"""

import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path

from agent.schemas import ToolDefinition, ToolCall, ToolResult
from athena.logger import logger


class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.definitions: Dict[str, ToolDefinition] = {}
        self._load_tools()
    
    def _load_tools(self):
        """Dynamically load all tools from the tools directory"""
        tools_root = Path(__file__).parent.parent / "tools"
        
        # Scan all subdirectories
        for tool_dir in tools_root.glob("**/*"):
            if tool_dir.is_file() and tool_dir.suffix == ".py" and not tool_dir.name.startswith("_"):
                module_path = f"tools.{tool_dir.parent.name}.{tool_dir.stem}"
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "tool") and hasattr(module, "definition"):
                        definition = module.definition
                        self.tools[definition.name] = module.tool
                        self.definitions[definition.name] = definition
                        logger.debug(f"Loaded tool: {definition.name}")
                except Exception as e:
                    logger.warning(f"Failed to load tool {module_path}: {e}")
        
        # Log loaded tools
        logger.info(f"Loaded {len(self.tools)} tools total")
        for name in self.tools.keys():
            logger.info(f"  - {name}")
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """Return all tool definitions in MCP format"""
        return [def_.to_mcp() for def_ in self.definitions.values()]
    
    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name"""
        return self.definitions.get(name)
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name with given arguments"""
        if name not in self.tools:
            return ToolResult(success=False, error=f"Tool not found: {name}")
        
        try:
            tool_func = self.tools[name]
            result = await tool_func(**arguments)
            return ToolResult(success=True, content=result)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return ToolResult(success=False, error=f"{str(e)}")
