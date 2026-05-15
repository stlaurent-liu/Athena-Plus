import httpx
from athena.config import settings
from typing import List, Dict

definition = {
    "name": "ollama_list_models",
    "description": "List all available models in local Ollama installation",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

async def tool() -> dict:
    base_url = settings.OLLAMA_BASE_URL.rstrip('/')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/tags", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                models.append({
                    "name": model.get("name"),
                    "digest": model.get("digest")[:12],
                    "size_gb": round(model.get("size", 0) / (1024**3), 2),
                    "modified_at": model.get("modified_at")
                })
            
            return {
                "success": True,
                "models": models,
                "count": len(models)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list models: {str(e)}\nCheck if Ollama is running at {base_url}"
        }
