from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # Running mode
    MODE: str = "mcp-std"
    
    # Cloud Gabriel MCP connection (for mcp-client mode)
    GABRIEL_MCP_URL: str = "http://10.0.0.1:8643"
    GABRIEL_MCP_API_KEY: Optional[str] = None
    
    # LLM configuration (for standalone mode)
    LLM_PROVIDER: str = "doubao"
    LLM_MODEL: str = "doubao-seed-2-0-lite-260428"
    LLM_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    LLM_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    
    # Custom system prompt
    SYSTEM_PROMPT: Optional[str] = None
    
    # Local Ollama
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Data directory
    DATA_DIR: str = "./data"
    
    # Debug mode
    DEBUG: bool = False
    
    # Computed properties
    @property
    def host(self) -> str:
        return self.HOST
    
    @property
    def port(self) -> int:
        return self.PORT
    
    @property
    def data_dir(self) -> str:
        return self.DATA_DIR
    
    @property
    def debug(self) -> bool:
        return self.DEBUG


settings = Settings()
