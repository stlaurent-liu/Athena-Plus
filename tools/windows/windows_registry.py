import winreg

definition = {
    "name": "windows_registry",
    "description": "Read a value from Windows Registry",
    "input_schema": {
        "type": "object",
        "properties": {
            "key_path": {
                "type": "string",
                "description": "Registry key path, e.g. 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion'"
            },
            "value_name": {
                "type": "string",
                "description": "Value name to read (leave empty for default value)"
            }
        },
        "required": ["key_path"]
    }
}

hive_map = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKU": winreg.HKEY_USERS,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
}

async def tool(key_path: str, value_name: str = "") -> dict:
    # Split hive from path
    parts = key_path.split("\\", 1)
    if len(parts) != 2:
        return {"error": "Invalid key path format. Should be 'HIVE\\path\\to\\key'"}
    
    hive_name, path = parts
    if hive_name not in hive_map:
        return {"error": f"Unknown registry hive: {hive_name}. Available: {', '.join(hive_map.keys())}"}
    
    hive = hive_map[hive_name]
    
    try:
        key = winreg.OpenKey(hive, path)
        if not value_name:
            value_name = ""
        
        value, type_id = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        type_names = {
            winreg.REG_SZ: "REG_SZ (string)",
            winreg.REG_DWORD: "REG_DWORD (32-bit int)",
            winreg.REG_BINARY: "REG_BINARY",
            winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
        }
        
        return {
            "key_path": key_path,
            "value_name": value_name or "(default)",
            "value": value,
            "type": type_names.get(type_id, f"type_id={type_id}")
        }
    except FileNotFoundError:
        return {"error": f"Key or value not found: {key_path}\\{value_name}"}
    except PermissionError:
        return {"error": f"Permission denied: cannot read {key_path}\\{value_name}, need admin rights"}
    except Exception as e:
        return {"error": f"Failed to read registry: {str(e)}"}
