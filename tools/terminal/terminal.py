import subprocess
import sys
from typing import Optional

definition = {
    "name": "terminal",
    "description": "Execute PowerShell command on the local Windows system",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The PowerShell command to execute"
            },
            "timeout": {
                "type": "number",
                "description": "Command timeout in seconds (default 120)"
            }
        },
        "required": ["command"]
    }
}

async def tool(command: str, timeout: int = 120) -> str:
    try:
        # On Windows, use powershell.exe
        result = subprocess.run(
            ["powershell.exe", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"Exit code: {result.returncode}\n\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}\n"
        
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"
