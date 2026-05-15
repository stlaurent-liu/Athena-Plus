import win32api
import win32con
import win32gui
import struct
import time

definition = {
    "name": "windows_notification",
    "description": "Send a desktop notification to Windows",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Notification title"
            },
            "message": {
                "type": "string",
                "description": "Notification message content"
            }
        },
        "required": ["title", "message"]
    }
}

async def tool(title: str, message: str) -> str:
    # Simple Windows notification using balloon tip
    # This works on Windows 10/11
    try:
        # Register a window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = win32gui.DefWindowProc
        wc.lpszClassName = "AthenaNotify"
        class_atom = win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(class_atom, "AthenaNotify", 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Shell notify icon
        nid = (
            hwnd,
            0,
            win32gui.NIF_INFO,
            0,
            "Athena Notification",
            0,
            message,
            5000,
            title,
        )
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (hwnd, 0))
        win32gui.DestroyWindow(hwnd)
        
        return f"Notification sent: '{title}' - '{message}'"
    except Exception as e:
        return f"Failed to send notification: {str(e)}"
