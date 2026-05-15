import os
from typing import Optional
from athena.config import settings

definition = {
    "name": "read_file",
    "description": "Read the contents of a text file from the local filesystem",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The absolute path of the file to read"
            },
            "offset": {
                "type": "number",
                "description": "Start reading from this line (0-indexed, default 0)"
            },
            "length": {
                "type": "number",
                "description": "Maximum number of lines to read (default 1000)"
            }
        },
        "required": ["path"]
    }
}

async def tool(path: str, offset: int = 0, length: int = 1000) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    end = offset + length
    content = ''.join(lines[offset:end])
    
    stats = f"\n\n---\nRead lines {offset} to {min(end, len(lines))} of {len(lines)} total lines"
    return content + stats
