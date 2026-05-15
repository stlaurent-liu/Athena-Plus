import httpx
from athena.config import settings
from typing import AsyncGenerator

definition = {
    "name": "ollama_pull",
    "description": "Pull a model from Ollama library to local installation",
    "input_schema": {
        "type": "object",
        "properties": {
            "model": {
                "type": "string",
                "description": "Model name to pull, e.g. 'qwen2.5:7b'"
            }
        },
        "required": ["model"]
    }
}

async def tool(model: str) -> dict:
    base_url = settings.OLLAMA_BASE_URL.rstrip('/')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/pull",
                json={"name": model, "stream": False},
                timeout=3600  # Large models can take a long time
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                return {
                    "success": False,
                    "error": data["error"]
                }
            
            return {
                "success": True,
                "message": f"Successfully pulled model: {model}",
                "details": data
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to pull model: {str(e)}"
        }
