"""
Ollama 本地模型管理工具
"""

import httpx
from typing import Dict, Any, List

from athena.config import settings
from tools.base import BaseTool
from agent.session import Session


class OllamaListModelsTool(BaseTool):
    """列出Ollama本地模型"""
    
    name = "ollama_list_models"
    description = "列出Ollama本地所有可用模型"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        base_url = settings.ollama_base_url
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                
                models = data.get("models", [])
                
                return {
                    "success": True,
                    "models": models,
                    "count": len(models)
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to connect to Ollama: {str(e)}",
                "help": "Make sure Ollama is running on {base_url}"
            }


class OllamaPullModelTool(BaseTool):
    """拉取Ollama模型"""
    
    name = "ollama_pull"
    description = "从Ollama拉取模型"
    is_dangerous = False  # 网络请求不危险
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        model_name = params.get("model")
        if not model_name:
            raise ValueError("Missing required parameter: model")
        
        base_url = settings.ollama_base_url
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:  # 拉取模型可能很慢
                response = await client.post(
                    f"{base_url}/api/pull",
                    json={"name": model_name}
                )
                response.raise_for_status()
                return {
                    "success": True,
                    "model": model_name,
                    "status": "pulled"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to pull model: {str(e)}"
            }
    
    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "模型名称，例如 'qwen2.5:7b-instruct-q4_K_M'"
                }
            },
            "required": ["model"]
        }


class OllamaGenerateTool(BaseTool):
    """使用Ollama本地生成文本"""
    
    name = "ollama_generate"
    description = "使用本地Ollama模型生成文本"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        prompt = params.get("prompt")
        model = params.get("model", settings.default_model)
        
        if not prompt:
            raise ValueError("Missing required parameter: prompt")
        
        base_url = settings.ollama_base_url
        options = params.get("options", {})
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "options": options,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "model": model,
                    "response": data.get("response", ""),
                    "total_duration": data.get("total_duration", 0) / 1e9  # 转换为秒
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation failed: {str(e)}"
            }
    
    def get_json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "输入提示词"
                },
                "model": {
                    "type": "string",
                    "description": f"模型名称，默认使用配置中的 {settings.default_model}"
                },
                "options": {
                    "type": "object",
                    "description": "Ollama生成选项（temperature、num_predict等，可选）"
                }
            },
            "required": ["prompt"]
        }


# 导出主类供注册
class OllamaTool(BaseTool):
    """Ollama工具集合 - 本地模型管理"""
    name = "ollama"
    description = "Ollama本地模型管理工具集合"
# 实际上单独注册每个工具，这个类只是占位
