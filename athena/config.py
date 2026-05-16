"""
配置管理模块
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False)
    
    # 运行模式: 
    # - mcp-server: 纯粹MCP服务端，暴露本地工具给云端Gabriel调用（推荐用于你的场景）
    # - mcp-client: 连接云端Gabriel推理，本地只执行工具，你在Athena窗口聊天
    # - standalone: 独立推理，自己配置LLM API，不依赖云端
    mode: str = "mcp-server"
    
    # Cloud Gabriel MCP 连接 (mcp-client 模式生效)
    gabriel_mcp_url: str = "http://10.0.0.1:8000/mcp"
    gabriel_mcp_api_key: Optional[str] = None
    
    # LLM 配置 (standalone 模式生效)
    llm_provider: str = "doubao"
    llm_model: str = "doubao-seed-2-0-lite-260428"
    llm_base_url: str = "https://ark.cn-beijing.volces.com/api/coding/v3"
    llm_api_key: Optional[str] = None
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2048
    
    # 系统提示 / Agent身份
    system_prompt: Optional[str] = None
    
    # 本地 Ollama 配置（仅用于 Ollama 工具管理，不做推理）
    ollama_base_url: str = "http://127.0.0.1:11434"
    
    # 服务器配置
    host: str = "127.0.0.1"
    port: int = 8000
    
    # 数据目录
    data_dir: Path = Path("./data")
    
    # 安全配置
    enable_dangerous_command_confirmation: bool = False
    allowed_commands: list[str] = [
        "dir", "cd", "ls", "pwd", "cat", "type",
        "python", "python3", "pip", "git",
    ]
    
    # 开发模式
    debug: bool = False


settings = Settings()

# 确保数据目录存在
settings.data_dir.mkdir(parents=True, exist_ok=True)
