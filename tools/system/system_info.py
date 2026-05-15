import platform
import psutil
import os
from datetime import datetime

definition = {
    "name": "system_info",
    "description": "Get basic system information: OS, CPU, memory, disk usage",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

async def tool() -> dict:
    # OS info
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    
    # CPU
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory
    mem = psutil.virtual_memory()
    mem_total_gb = mem.total / (1024 ** 3)
    mem_used_gb = mem.used / (1024 ** 3)
    mem_percent = mem.percent
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_total_gb = disk.total / (1024 ** 3)
    disk_used_gb = disk.used / (1024 ** 3)
    disk_percent = disk.percent
    
    # Boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "os": {
            "name": os_name,
            "version": os_version,
            "release": os_release
        },
        "cpu": {
            "count_logical": cpu_count,
            "usage_percent": cpu_percent
        },
        "memory": {
            "total_gb": round(mem_total_gb, 2),
            "used_gb": round(mem_used_gb, 2),
            "usage_percent": mem_percent
        },
        "disk": {
            "total_gb": round(disk_total_gb, 2),
            "used_gb": round(disk_used_gb, 2),
            "usage_percent": disk_percent
        },
        "boot_time": boot_time
    }
