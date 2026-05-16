"""
系统信息工具
"""

import platform
import psutil
from datetime import datetime
from typing import Dict, Any

from tools.base import BaseTool
from agent.session import Session


class SystemInfoTool(BaseTool):
    """获取系统信息"""
    
    name = "system_info"
    description = "获取系统信息（OS、CPU、内存、磁盘）"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        # OS 基本信息
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "node": platform.node(),
            "python_version": platform.python_version()
        }
        
        # CPU 信息
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=0.5)
        }
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
            "percent_used": memory.percent
        }
        
        # 磁盘信息
        disk = psutil.disk_usage("/")
        disk_info = {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "percent_used": disk.percent
        }
        
        # 运行时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        
        return {
            "success": True,
            "os": os_info,
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "boot_time": boot_time.isoformat(),
            "uptime_seconds": uptime_seconds
        }


class ListProcessesTool(BaseTool):
    """列出运行中的进程"""
    
    name = "list_processes"
    description = "列出当前运行的进程"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "memory_percent": proc.info["memory_percent"]
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "success": True,
            "processes": processes[:100],  # 限制最多返回前100个
            "total_count": len(processes)
        }


# 导出主类供注册
class SystemTool(BaseTool):
    """系统工具集合 - 聚合"""
    name = "system"
    description = "系统信息和进程管理工具集合"
# 实际上单独注册每个工具，这个类只是占位
