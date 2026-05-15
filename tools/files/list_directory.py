import os
from typing import List, Dict

definition = {
    "name": "list_directory",
    "description": "List all files and directories in a given directory",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The absolute path of the directory to list"
            },
            "depth": {
                "type": "number",
                "description": "How many levels deep to list (default 1)"
            }
        },
        "required": ["path"]
    }
}

def list_dir_recursive(path: str, current_depth: int, max_depth: int) -> List[Dict[str, str]]:
    result = []
    if not os.path.exists(path):
        return []
    
    try:
        items = sorted(os.listdir(path))
        for item in items:
            if item.startswith('.') or item in ['__pycache__', 'venv', 'node_modules']:
                continue
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                result.append({"type": "directory", "name": item, "path": full_path})
                if current_depth < max_depth:
                    result.extend(list_dir_recursive(full_path, current_depth + 1, max_depth))
            else:
                size = os.path.getsize(full_path)
                result.append({"type": "file", "name": item, "path": full_path, "size_bytes": size})
    except PermissionError:
        result.append({"type": "error", "name": "[ACCESS DENIED]", "path": path})
    except Exception as e:
        result.append({"type": "error", "name": str(e), "path": path})
    return result

async def tool(path: str, depth: int = 1) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return [{"error": f"Path does not exist: {path}"}]
    if not os.path.isdir(path):
        return [{"error": f"Path is not a directory: {path}"}]
    
    items = list_dir_recursive(path, 1, depth)
    return items
