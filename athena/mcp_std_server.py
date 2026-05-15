"""
Standard MCP (Model Context Protocol) HTTP Server
Follows MCP specification: https://spec.modelcontextprotocol.io/
"""

import json
from typing import Any, Dict, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from athena.logger import logger
from agent.executor import ToolExecutor
from agent.schemas import ToolCall, ToolResult


# Create FastAPI app
app = FastAPI(title="Athena-Plus MCP Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global tool executor
executor = ToolExecutor()


@app.get("/")
async def root():
    """Health check"""
    return {
        "name": "Athena-Plus MCP Server",
        "version": "1.0.0",
        "tools_count": len(executor.list_available_tools()),
        "status": "running"
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP JSON-RPC endpoint"""
    try:
        body = await request.json()
        logger.debug(f"Received MCP request: {json.dumps(body, indent=2)}")
        
        # JSON-RPC 2.0 format
        jsonrpc = body.get("jsonrpc", "2.0")
        method = body.get("method")
        params = body.get("params", {})
        id = body.get("id")
        
        # Handle different methods
        if method == "initialize":
            # Initialize request - return server info and tools list
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "athena-plus",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
            return {"jsonrpc": jsonrpc, "id": id, "result": result}
        
        elif method == "tools/list":
            # List all available tools
            tools = executor.list_available_tools()
            return {"jsonrpc": jsonrpc, "id": id, "result": {"tools": tools}}
        
        elif method == "tools/call":
            # Call a tool
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"Calling tool: {name}, arguments: {arguments}")
            
            result = await executor.execute_tool(name, arguments)
            
            if result.success:
                return {
                    "jsonrpc": jsonrpc,
                    "id": id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result.content)
                            }
                        ]
                    }
                }
            else:
                return {
                    "jsonrpc": jsonrpc,
                    "id": id,
                    "error": {
                        "code": -32000,
                        "message": str(result.error)
                    }
                }
        
        else:
            # Method not found
            logger.warning(f"Unknown MCP method: {method}")
            return {
                "jsonrpc": jsonrpc,
                "id": id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32600,
                "message": f"Invalid request: {str(e)}"
            }
        }


@app.get("/ping")
async def ping():
    """Simple ping for health check"""
    return {"pong": True, "tools": len(executor.list_available_tools())}


# For backwards compatibility - old endpoint
@app.post("/api/mcp")
async def legacy_mcp(request: Request):
    """Legacy endpoint for backwards compatibility"""
    return await mcp_endpoint(request)
