@echo off
:: Athena-Plus MCP Server startup script
:: Auto-start on boot, run in background

chdir /d "%~dp0\.."

:: Activate venv and start
call venv\Scripts\activate.bat

:: Start Standard MCP server, default port 8000
python main.py mcp-std > data\athena-mcp.log 2>&1

:: Keep window open if exit with error
if %errorlevel% neq 0 (
    echo Error: Athena MCP server exited with code %errorlevel%
    pause
)
