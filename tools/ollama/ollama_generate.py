import httpx
from athena.config import settings
from typing import Optional

definition = {
    "name": "ollama_generate",
    "description": "Generate text completion using a local Ollama model",
    "input_schema": {
        "type": "object",
        "properties": {
            "model": {
                "type": "string",
                "description": "Model name to use, e.g. 'qwen2.5:7b'"
            },
            "prompt": {
                "type": "string",
                "description": "Input prompt for generation"
            },
            "temperature": {
                "type": "number",
                "description": "Temperature for sampling (0-1), default 0.7"
            },
            "max_tokens": {
                "type": "number",
                "description": "Maximum tokens to generate"
            }
        },
        "required": ["model", "prompt"]
    }
}

async def tool(model: str, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> dict:
    base_url = settings.OLLAMA_BASE_URL.rstrip('/')
    
    if temperature is None:
        temperature = 0.7
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = int(max_tokens)
            
            response = await client.post(
                f"{base_url}/api/generate",
                json=payload,
                timeout=600
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "model": model,
                "response": data.get("response", ""),
                "total_duration_ms": data.get("total_duration", 0) / 1_000_000,
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0)
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate: {str(e)}"
        }
