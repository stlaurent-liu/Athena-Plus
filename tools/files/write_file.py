import os

definition = {
    "name": "write_file",
    "description": "Write content to a file on the local filesystem (overwrites existing)",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The absolute path where to write the file"
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file"
            }
        },
        "required": ["path", "content"]
    }
}

async def tool(path: str, content: str) -> str:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return f"Successfully wrote {len(content)} bytes to {path}"
