"""
Athena-Plus - Native Windows AI Agent
Main entry point
"""

import argparse
import uvicorn

from athena.logger import logger
from athena.config import settings
from athena.state import global_state, AppState


def run_web_server(host: str = None, port: int = None):
    """启动FastAPI Web服务器（聊天界面）"""
    host = host or settings.host
    port = port or settings.port
    
    logger.info(f"Starting web server at http://{host}:{port}")
    global_state.set_state(AppState.RUNNING)
    
    uvicorn.run(
        "web.server:app",
        host=host,
        port=port,
        reload=settings.debug
    )


def run_mcp_server_std(host: str = None, port: int = None):
    """启动标准MCP协议HTTP服务端 - 符合MCP规范，供云端Gabriel作为MCP服务器加载"""
    host = host or settings.host
    port = port or settings.port
    
    from agent.executor import ToolExecutor
    executor = ToolExecutor()
    
    logger.info(f"Starting Standard MCP Server at http://{host}:{port}")
    logger.info(f"Mode: standard MCP server, exposes {len(executor.list_available_tools())} tools")
    global_state.set_state(AppState.RUNNING)
    
    uvicorn.run(
        "athena.mcp_std_server:app",
        host=host,
        port=port,
        reload=settings.debug
    )


def run_mcp_server(host: str = None, port: int = None):
    """启动自定义MCP服务端 - 纯粹暴露本地工具给云端Gabriel"""
    host = host or settings.host
    port = port or settings.port
    
    from agent.core import Agent
    agent = Agent()
    
    logger.info(f"Starting MCP server at http://{host}:{port}")
    logger.info(f"Mode: pure MCP server, exposes {len(agent.tool_executor.list_available_tools())} tools")
    global_state.set_state(AppState.RUNNING)
    
    uvicorn.run(
        "athena.mcp_server:app",
        host=host,
        port=port,
        reload=settings.debug
    )


def run_cli():
    """启动命令行交互模式"""
    logger.info("Starting CLI mode (not implemented yet)")
    print("CLI mode coming soon...")


def run_gui():
    """启动PyWebView桌面GUI"""
    import webview
    from athena.config import settings
    
    # 先在后台启动服务器
    import threading
    thread = threading.Thread(
        target=run_web_server,
        args=(settings.host, settings.port),
        daemon=True
    )
    thread.start()
    
    # GUI 访问本地必须用 127.0.0.1，不能用 0.0.0.0
    gui_host = "127.0.0.1"
    url = f"http://{gui_host}:{settings.port}/static/index.html"
    
    logger.info(f"Starting GUI window: {url}")
    window = webview.create_window(
        "Athena-Plus AI Agent",
        url,
        width=1200,
        height=800,
        min_size=(800, 600)
    )
    
    global_state.set_state(AppState.RUNNING)
    webview.start()


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="Athena-Plus Native Windows AI Agent")
    parser.add_argument(
        "mode",
        choices=["mcp-std", "mcp-server", "web", "cli", "gui"],
        default="mcp-std",
        nargs="?",
        help="启动模式: \nmcp-std (默认，标准MCP协议服务端，供云端作为MCP服务器加载) \nmcp-server (自定义API) \nweb (WebAPI聊天界面) \ncli (命令行) \ngui (桌面GUI)"
    )
    parser.add_argument("--host", help="Web服务器监听地址")
    parser.add_argument("--port", type=int, help="Web服务器端口")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Athena-Plus in {args.mode} mode")
    
    if args.mode == "mcp-std":
        run_mcp_server_std(args.host, args.port)
    elif args.mode == "mcp-server":
        run_mcp_server(args.host, args.port)
    elif args.mode == "web":
        run_web_server(args.host, args.port)
    elif args.mode == "cli":
        run_cli()
    elif args.mode == "gui":
        run_gui()


if __name__ == "__main__":
    main()
