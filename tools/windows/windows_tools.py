"""
Windows 专属工具
"""

import win32api
import win32con
import win32gui
import win32process
from typing import Dict, Any
from pathlib import Path

from tools.base import BaseTool
from agent.session import Session


class WindowsNotificationTool(BaseTool):
    """发送Windows系统通知"""
    
    name = "windows_notification"
    description = "发送Windows桌面通知"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        title = params.get("title", "Athena-Plus Notification")
        message = params.get("message", "")
        
        if not message:
            raise ValueError("Missing required parameter: message")
        
        try:
            # 使用win32gui弹出通知
            win32gui.MessageBox(None, message, title, win32con.MB_OK | win32con.MB_ICONINFORMATION)
            return {"success": True, "title": title, "message": message}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "通知标题，默认为 'Athena-Plus Notification'"
                },
                "message": {
                    "type": "string",
                    "description": "通知内容"
                }
            },
            "required": ["message"]
        }


class GetWindowsInfoTool(BaseTool):
    """获取Windows系统详细信息"""
    
    name = "windows_info"
    description = "获取Windows系统详细信息"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        import platform
        
        info = {
            "windows_version": platform.version(),
            "windows_release": platform.release(),
            "csd_version": win32api.GetVersionEx()
        }
        
        return {"success": True, "info": info}


class WindowsRegistryTool(BaseTool):
    """读取Windows注册表"""
    
    name = "windows_registry"
    description = "读取Windows注册表键值"
    is_dangerous = False
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        import winreg
        
        hive_str = params.get("hive", "HKEY_CURRENT_USER")
        path = params.get("path", "")
        value_name = params.get("value_name")
        
        if not path:
            raise ValueError("Missing required parameter: path")
        
        # 映射 hive 字符串到 winreg 常量
        hive_map = {
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
        }
        
        hive = hive_map.get(hive_str, winreg.HKEY_CURRENT_USER)
        
        try:
            with winreg.OpenKey(hive, path) as key:
                if value_name is None:
                    # 枚举所有值
                    values = {}
                    i = 0
                    while True:
                        try:
                            name, data, _ = winreg.EnumValue(key, i)
                            values[name] = data
                            i += 1
                        except WindowsError:
                            break
                    return {"success": True, "values": values}
                else:
                    # 读取特定值
                    value, _ = winreg.QueryValueEx(key, value_name)
                    return {"success": True, "value": value}
        except WindowsError as e:
            return {"success": False, "error": str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "hive": {
                    "type": "string",
                    "description": "注册表根键",
                    "enum": ["HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE", "HKEY_CLASSES_ROOT", "HKEY_USERS", "HKEY_CURRENT_CONFIG"],
                    "default": "HKEY_CURRENT_USER"
                },
                "path": {
                    "type": "string",
                    "description": "注册表路径"
                },
                "value_name": {
                    "type": "string",
                    "description": "要读取的值名称（可选，不提供则枚举所有值）"
                }
            },
            "required": ["path"]
        }


class WindowsPowerTool(BaseTool):
    """Windows电源管理"""
    
    name = "windows_power"
    description = "Windows电源操作（休眠、重启、关机等）"
    is_dangerous = True  # 电源操作是危险的
    
    async def execute(self, params: Dict[str, Any], session: Session) -> Dict[str, Any]:
        action = params.get("action", "")
        
        if not action:
            raise ValueError("Missing required parameter: action")
        
        valid_actions = ["shutdown", "restart", "sleep", "hibernate", "lock"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Valid actions: {valid_actions}")
        
        # 需要确认危险操作
        confirmed = params.get("confirmed", False)
        if not confirmed:
            return {
                "success": False,
                "error": "Dangerous operation requires confirmation",
                "requires_confirmation": True,
                "message": f"Power action '{action}' requires explicit confirmation. Set confirmed=true to proceed."
            }
        
        try:
            if action == "shutdown":
                import os
                os.system("shutdown /s /t 0")
            elif action == "restart":
                import os
                os.system("shutdown /r /t 0")
            elif action == "sleep":
                import ctypes
                ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            elif action == "hibernate":
                import ctypes
                ctypes.windll.powrprof.SetSuspendState(1, 1, 0)
            elif action == "lock":
                import ctypes
                ctypes.windll.User32.LockWorkStation()
            
            return {"success": True, "action": action, "status": "initiated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "电源操作",
                    "enum": ["shutdown", "restart", "sleep", "hibernate", "lock"]
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "确认执行危险操作",
                    "default": False
                }
            },
            "required": ["action"]
        }
