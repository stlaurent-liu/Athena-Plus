"""
MCP Client Manager - 管理第三方MCP服务器连接
加载 mcp_servers.json 配置，连接远程MCP服务器，将工具注册到Athena
支持两种类型：
- sse: 远程HTTP服务器流式连接
- stdio: 本地子进程标准IO连接
"""

import json
import asyncio
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
import queue

import httpx

from athena.logger import logger
from agent.executor import BaseTool, ToolExecutor


class SSEMCPStream:
    """SSE MCP 连接流"""
    def __init__(self, url: str):
        self.url = url
        # 硬编码代理地址
        proxy = "http://127.0.0.1:7897"
        self.client = httpx.AsyncClient(proxy=proxy)
        self.response = None

    async def connect(self):
        """连接SSE MCP服务器"""
        try:
            logger.info(f"Connecting to SSE MCP: {self.url} (using proxy: http://127.0.0.1:7897)")
            self.response = await self.client.get(
                self.url,
                headers={"Accept": "text/event-stream"},
                timeout=None
            )
            self.response.raise_for_status()
            logger.info(f"SSE MCP connected successfully: {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to SSE MCP {self.url}: {str(e)}")
            logger.error(f"Connection error details: {repr(e)}")
            raise

    async def close(self):
        """关闭连接"""
        if self.response:
            await self.response.aclose()
        await self.client.aclose()

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送JSON-RPC请求"""
        # 对于SSE MCP，请求通过POST发送到同一个URL
        try:
            response = await self.client.post(self.url, json=request, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP request failed to {self.url}: {str(e)}")
            raise


class STDIOMCPStream:
    """STDIO MCP 连接流 - 本地子进程通过标准IO通信"""
    def __init__(self, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args
        self.env = env or {}
        self.process: Optional[subprocess.Popen] = None
        self._read_queue: queue.Queue = queue.Queue()
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
    
    async def connect(self):
        """启动子进程并连接"""
        try:
            # 合并环境变量
            full_env = dict(subprocess.os.environ)
            full_env.update(self.env)
            
            logger.info(f"Starting STDIO MCP process: {self.command} {' '.join(self.args)}")
            
            # 启动子进程
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=full_env
            )
            
            self._running = True
            
            # 启动读取线程
            self._read_thread = threading.Thread(target=self._read_output, daemon=True)
            self._read_thread.start()
            
            # 启动stderr读取线程（日志）
            self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self._stderr_thread.start()
            
            logger.info(f"STDIO MCP process started successfully, PID: {self.process.pid}")
            
        except Exception as e:
            logger.error(f"Failed to start STDIO MCP process: {str(e)}")
            logger.error(f"Full error: {repr(e)}")
            raise
    
    def _read_output(self):
        """读取stdout"""
        while self._running and self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if not line:
                break
            if line.strip():
                self._read_queue.put(line.strip())
    
    def _read_stderr(self):
        """读取stderr并记录到日志"""
        while self._running and self.process and self.process.stderr:
            line = self.process.stderr.readline()
            if not line:
                break
            if line.strip():
                logger.debug(f"[STDIO MCP stderr] {line.strip()}")
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送JSON-RPC请求并等待响应"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("STDIO process not started")
        
        # 发送请求
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # 等待响应（异步读取队列）
        response_line = await asyncio.get_event_loop().run_in_executor(
            None, self._read_queue.get
        )
        
        try:
            return json.loads(response_line)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {response_line}")
            raise
    
    async def close(self):
        """关闭子进程"""
        self._running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("STDIO MCP process terminated")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("STDIO MCP process killed after timeout")
            except Exception as e:
                logger.error(f"Error terminating STDIO process: {str(e)}")
        self.process = None


class MCPClient:
    """MCP客户端 - 连接一个第三方MCP服务器"""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.type = config.get("type", "stdio")
        self.url = config.get("url", "")
        self.command = config.get("command", "")
        self.args = config.get("args", [])
        self.env = config.get("env", {})
        self.stream: Optional[SSEMCPStream | STDIOMCPStream] = None
        self.tools: List[Dict[str, Any]] = []

    async def connect(self) -> bool:
        """连接MCP服务器"""
        logger.info(f"Connecting to MCP server '{self.name}', type={self.type}")
        if self.type == "sse":
            self.stream = SSEMCPStream(self.url)
            try:
                await self.stream.connect()
                # 获取工具列表
                tools_result = await self.send_request({
                    "jsonrpc": "2.0",
                    "id": "1",
                    "method": "tools/list",
                    "params": {}
                })
                if "result" in tools_result and "tools" in tools_result["result"]:
                    self.tools = tools_result["result"]["tools"]
                    logger.info(f"MCP server '{self.name}' connected, {len(self.tools)} tools available")
                    return True
                else:
                    logger.error(f"Failed to get tools from MCP {self.name}: response={tools_result}")
                    return False
            except Exception as e:
                logger.error(f"Failed to connect to MCP {self.name}: {str(e)}")
                logger.error(f"Full error: {repr(e)}")
                return False
        elif self.type == "stdio":
            self.stream = STDIOMCPStream(self.command, self.args, self.env)
            try:
                await self.stream.connect()
                # 获取工具列表
                tools_result = await self.send_request({
                    "jsonrpc": "2.0",
                    "id": "1",
                    "method": "tools/list",
                    "params": {}
                })
                if "result" in tools_result and "tools" in tools_result["result"]:
                    self.tools = tools_result["result"]["tools"]
                    logger.info(f"MCP server '{self.name}' connected, {len(self.tools)} tools available")
                    return True
                else:
                    logger.error(f"Failed to get tools from MCP {self.name}: response={tools_result}")
                    return False
            except Exception as e:
                logger.error(f"Failed to connect to MCP {self.name}: {str(e)}")
                logger.error(f"Full error: {repr(e)}")
                return False
        else:
            logger.error(f"Unsupported MCP type: {self.type}")
            return False

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到MCP服务器"""
        if self.stream:
            return await self.stream.send_request(request)
        raise RuntimeError("MCP not connected")

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        result = await self.send_request({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        })
        return result

    async def close(self):
        """关闭连接"""
        if self.stream:
            await self.stream.close()


class MCPToolWrapper(BaseTool):
    """将第三方MCP工具包装成Athena工具"""
    # 这些在动态子类创建时会被覆盖为类属性
    name: str = ""
    description: str = ""
    is_dangerous: bool = True
    _mcp_client: MCPClient = None
    _tool_def: Dict[str, Any] = None
    _schema: Dict[str, Any] = {}

    def __init__(self):
        # 无参构造，满足 Athena 要求
        pass

    def get_schema(self) -> Dict:
        """获取工具schema"""
        return self._schema

    async def execute(self, params: Dict[str, Any], session) -> Any:
        """执行工具 - 转发到第三方MCP"""
        result = await self._mcp_client.call_tool(
            self.name[len(f"{self._mcp_client.name}_"):],
            params
        )

        if "error" in result:
            return {
                "success": False,
                "error": result["error"].get("message", "Unknown MCP error")
            }

        if "result" in result:
            content = result["result"].get("content", [])
            is_error = result["result"].get("is_error", False)

            # 提取文本内容
            text_content = []
            for item in content:
                if item.get("type") == "text":
                    text_content.append(item.get("text", ""))

            full_text = "\n".join(text_content)

            if is_error:
                return {
                    "success": False,
                    "error": full_text
                }

            # 尝试解析JSON
            try:
                import json
                return json.loads(full_text)
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "result": full_text
                }

        return {
            "success": True,
            "result": result
        }


class MCPClientManager:
    """MCP客户端管理器 - 加载所有配置的第三方MCP服务器"""
    def __init__(self, config_path: str = "mcp_servers.json"):
        self.config_path = Path(config_path)
        self.clients: Dict[str, MCPClient] = {}
        self.connected: bool = False

    def load_config(self) -> Dict[str, Dict[str, Any]]:
        """加载MCP配置"""
        if not self.config_path.exists():
            logger.info(f"No MCP config found at {self.config_path}, no third-party MCP servers loaded")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            mcp_servers = config.get("mcpServers", {})
            logger.info(f"Loaded {len(mcp_servers)} MCP servers from {self.config_path}")
            return mcp_servers
        except Exception as e:
            logger.error(f"Failed to load MCP config from {self.config_path}: {e}")
            return {}

    async def connect_all(self, executor: ToolExecutor) -> int:
        """连接所有MCP服务器并注册工具"""
        logger.info("Starting to connect all third-party MCP servers...")
        configs = self.load_config()
        connected_count = 0

        for name, config in configs.items():
            client = MCPClient(name, config)
            try:
                if await client.connect():
                    self.clients[name] = client
                    # 注册所有工具
                    for tool_def in client.tools:
                        # 动态创建子类，将所有必要信息设置为类属性
                        # Athena 需要无参构造，所以把 client 和 tool_def 信息存在类层面
                        tool_cls = type(
                            f"{client.name}_{tool_def['name']}",
                            (MCPToolWrapper,),
                            {
                                "name": f"{client.name}_{tool_def['name']}",
                                "description": tool_def.get("description", f"MCP tool from {client.name}"),
                                "is_dangerous": True,
                                "_mcp_client": client,
                                "_tool_def": tool_def,
                                "_schema": tool_def.get("inputSchema", {}),
                            }
                        )
                        executor.register_tool(tool_cls)
                    connected_count += 1
                    logger.info(f"Registered {len(client.tools)} tools from MCP server '{name}'")
                else:
                    logger.error(f"MCP server '{name}' connection failed, skipping...")
            except Exception as e:
                logger.error(f"Unexpected error connecting to MCP '{name}': {str(e)}")
                logger.error(f"Full error: {repr(e)}")

        self.connected = True
        logger.info(f"Third-party MCP initialization complete: {connected_count}/{len(configs)} servers connected")
        return connected_count

    async def close_all(self):
        """关闭所有连接"""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()
        self.connected = False
        logger.info("All MCP clients closed")


# 单例实例
mcp_manager = MCPClientManager()