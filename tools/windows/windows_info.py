import platform
import psutil
import getpass
import socket

definition = {
    "name": "windows_info",
    "description": "Get detailed Windows system information",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

async def tool() -> dict:
    info = {}
    
    # Windows version
    info["windows_release"] = platform.win32_ver()
    
    # Computer name
    info["computer_name"] = socket.gethostname()
    
    # Username
    info["username"] = getpass.getuser()
    
    # CPU info
    info["cpu_count_physical"] = psutil.cpu_count(logical=False)
    info["cpu_count_logical"] = psutil.cpu_count(logical=True)
    
    # Memory
    mem = psutil.virtual_memory()
    info["memory_total_gb"] = round(mem.total / (1024**3), 2)
    info["memory_available_gb"] = round(mem.available / (1024**3), 2)
    
    # Disk info
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_percent": usage.percent
            })
        except PermissionError:
            continue
    info["disks"] = disks
    
    # Network
    info["hostname"] = socket.gethostname()
    try:
        info["ip_address"] = socket.gethostbyname(socket.gethostname())
    except:
        info["ip_address"] = "unavailable"
    
    return info
