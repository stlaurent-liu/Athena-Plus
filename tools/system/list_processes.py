import psutil
from typing import List, Dict

definition = {
    "name": "list_processes",
    "description": "List all running processes with PID, name, CPU and memory usage",
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "number",
                "description": "Maximum number of processes to return (default 50)"
            },
            "sort_by": {
                "type": "string",
                "description": "Sort by: 'memory' or 'cpu' (default memory)"
            }
        }
    }
}

async def tool(limit: int = 50, sort_by: str = "memory") -> List[Dict]:
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            info = proc.info
            processes.append({
                "pid": info['pid'],
                "name": info['name'],
                "cpu_percent": round(info['cpu_percent'], 1),
                "memory_percent": round(info['memory_percent'], 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Sort
    if sort_by == "cpu":
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    else:
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    
    # Limit
    processes = processes[:limit]
    
    return processes
