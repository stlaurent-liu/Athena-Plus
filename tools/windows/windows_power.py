import os
import ctypes

definition = {
    "name": "windows_power",
    "description": "Perform power operations on Windows: shutdown, restart, sleep, hibernate, lock",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: shutdown, restart, sleep, hibernate, lock"
            },
            "delay_seconds": {
                "type": "number",
                "description": "Delay before action in seconds (default 0, immediate)"
            }
        },
        "required": ["action"]
    }
}

async def tool(action: str, delay_seconds: int = 0) -> str:
    actions = ["shutdown", "restart", "sleep", "hibernate", "lock"]
    if action not in actions:
        return f"Invalid action: {action}. Available: {', '.join(actions)}"
    
    if delay_seconds > 0:
        cmd = f"shutdown /f /t {delay_seconds} "
        if action == "shutdown":
            cmd += "/s"
        elif action == "restart":
            cmd += "/r"
        elif action == "hibernate":
            cmd = "shutdown /h"
        elif action == "sleep":
            # Use rundll32 for sleep
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return f"Scheduled system sleep after {delay_seconds}s delay"
        elif action == "lock":
            ctypes.windll.user32.LockWorkStation()
            return "Workstation locked"
        
        os.system(cmd)
        return f"Scheduled {action} after {delay_seconds} seconds"
    else:
        # Immediate action
        if action == "shutdown":
            os.system("shutdown /f /s /t 0")
        elif action == "restart":
            os.system("shutdown /f /r /t 0")
        elif action == "hibernate":
            os.system("shutdown /h")
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif action == "lock":
            ctypes.windll.user32.LockWorkStation()
        
        return f"Performing {action} immediately"
