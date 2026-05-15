@echo off
REM Start Athena-Plus MCP Server (standard MCP protocol)
REM This script will start the MCP server in the background

cd /d "%~dp0.."
call venv\Scripts\activate.bat
python main.py mcp-std
