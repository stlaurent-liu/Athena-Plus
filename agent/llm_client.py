"""
独立推理 LLM 客户端 - 支持多种云端API
兼容 OpenAI 格式，支持 doubao/deepseek/openai 等
"""

import json
from typing import Dict, Any, AsyncGenerator, Optional
import httpx

from athena.logger import logger
from athena.config import settings


class LLMClient:
    """通用 LLM 客户端，支持 OpenAI 兼容格式"""
    
    def __init__(
        self,
        provider: str = None,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens
        
        self._headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"LLMClient initialized: provider={self.provider}, model={self.model}")
    
    def get_default_system_prompt(self) -> str:
        """获取默认系统提示/Agent身份"""
        if settings.system_prompt:
            return settings.system_prompt
        
        return """你是 Athena-Plus，一个运行在 Windows 本地的轻量 AI Agent。

你的定位：
- 专注于 Windows 本地操作，帮助用户管理文件、运行命令、开发调试
- 配合云端 Gabriel 协同工作，你负责本地执行，Gabriel 负责深度推理
- 回答简洁直接，使用中文，保持专业友好

核心规则：
- 不确定的信息不要猜测，直接询问用户
- 操作本地文件/系统时，先确认再执行
- 保持响应迅速，不冗长"""
    
    async def chat_stream(
        self,
        messages: list[Dict[str, str]],
        system_prompt: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天"""
        
        # 插入系统提示
        full_messages = []
        has_system = any(msg.get("role") == "system" for msg in messages)
        
        if not has_system:
            full_messages.append({
                "role": "system",
                "content": system_prompt or self.get_default_system_prompt()
            })
        
        full_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": True,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        # 处理不同平台的路径拼接
        # OpenAI标准: {base_url}/v1/chat/completions
        # 火山方舟: {base_url}/chat/completions (base_url 已经包含 /api/v3)
        if "/v1" in self.base_url or "/v3" in self.base_url:
            # base_url 已经包含版本段，直接拼 chat/completions
            url = f"{self.base_url}/chat/completions"
        else:
            # 标准 OpenAI 格式
            url = f"{self.base_url}/v1/chat/completions"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                    headers=self._headers
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            line = line[6:]
                        if line == "[DONE]":
                            break
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"LLM chat request failed: {e}")
            yield {
                "type": "error",
                "error": str(e)
            }