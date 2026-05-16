# Athena-Plus ☁️💻

**Lightweight Windows local MCP server - Provides native Windows tool execution capability for cloud AI agents. Perfect architecture: cloud reasoning + local execution.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Architecture

```
Cloud AI Agent (Gabriel/Hermes/Claude Desktop) ←→ WireGuard VPN ←→ Athena-Plus (local MCP server) ←→ Operate your Windows
```

- 🧠 **Cloud**: Responsible for reasoning, conversation, memory
- 💻 **Local**: Responsible for tool execution, file operations, command running, Windows system management
- 🔒 **Privacy & Security**: All data stays local, never uploaded to cloud
- ⚡ **Save cloud memory**: One MCP entry point, all tools are discovered dynamically

## ✨ Features

- ✅ **Standard MCP Protocol** - Compatible with any AI agent that supports MCP
- ✅ **Five running modes**: 
  - `mcp-std` (**recommended**): Standard MCP protocol server, exposes local tools to cloud AI
  - `mcp-server`: Custom MCP API (legacy, kept for compatibility)
  - `mcp-client`: All inference goes to cloud Gabriel MCP, you chat in Athena window locally
  - `standalone`: Standalone inference with your own LLM API key, run completely local
  - `gui`: Desktop GUI chat
- ✅ **Third-party MCP server support** - Load any external MCP server (like Windows-MCP for desktop automation) via `mcp_servers.json`
- ✅ **13+ built-in tools + 40+ desktop automation tools**:
  - 📁 File operations: read/write/list directory
  - 🖥️ Terminal: Execute PowerShell commands
  - ℹ️ System: CPU/memory/process info
  - 🪟 Windows-specific: Notification/Registry/Power management
  - 🧠 Ollama: Local model management/text generation
  - 🖱️ **Windows Desktop Automation**: Full mouse/keyboard/screenshot/OCR control via [Windows-MCP.Net](https://github.com/shuyu-labs/Windows-MCP.Net)
- ✅ **Auto-start on boot** - Windows hidden startup guide included
- ✅ **Lightweight** - Less than 50MB memory usage

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python 3.10+
- [WireGuard](https://www.wireguard.com/) (**required if you need cloud access**) - tunnel through NAT to expose local service to cloud

### Installation

```powershell
git clone https://github.com/stlaurent-liu/Athena-Plus.git
cd Athena-Plus
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env to fill your configuration (default config works for mcp-std mode)
```

### Running

```powershell
# Default: Standard MCP server (for cloud AI to connect)
python main.py
# Or use the startup script
.\scripts\start-mcp-server.bat
```

### Set auto-start on Windows boot

See: [docs/autostart-windows.md](docs/autostart-windows.md)

## ⚙️ Configuration

| Mode | Usage | Need API Key? |
|------|-------|---------------|
| `mcp-std` | Standard MCP server, expose local tools to cloud AI | ❌ No |
| `standalone` | Run standalone, local inference with your own API | ✅ Yes |
| `gui` | Local desktop GUI chat | ✅ Yes (if standalone) |

### Third-party MCP Servers Configuration

Create `mcp_servers.json` (copy from `mcp_servers.json.example`) to add external MCP servers:

```json
{
  "mcpServers": {
    "windows-mcp": {
      "type": "stdio",
      "command": "C:\\Users\\YOUR_USERNAME\\.dotnet\\tools\\Windows-MCP.Net.exe",
      "args": [],
      "env": {}
    }
  }
}
```

Supported types: `stdio` and `sse`. All tools from third-party MCP servers will be automatically loaded and available to your cloud AI agent.

### Cloud AI Configuration (on cloud side)

Add this to your `config.yaml` MCP servers section:

```yaml
mcp_servers:
  athena-plus:
    transport: http
    url: http://<your-local-ip-via-wireguard>:8000/mcp
    enabled: true
    connect_timeout: 60
```

## 🛠️ Available Built-in Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read text file content |
| `write_file` | Write text content to file |
| `list_directory` | List files and directories |
| `terminal` | Execute PowerShell commands |
| `system_info` | Get system info (OS/CPU/Memory/Disk) |
| `list_processes` | List running processes |
| `windows_notification` | Send Windows desktop notification |
| `windows_info` | Get Windows system detailed info |
| `windows_registry` | Read Windows registry key |
| `windows_power` | Windows power operations (shutdown/restart/sleep/hibernate/lock) |
| `ollama_list_models` | List all local Ollama models |
| `ollama_pull` | Pull model from Ollama |
| `ollama_generate` | Generate text with local Ollama model |

> **40+ additional desktop automation tools via Windows-MCP**: mouse move/click, keyboard input, screenshot, OCR text recognition, window management, color picking, etc. Enable it by adding to `mcp_servers.json`.

## 🤝 Contributing

Issues and pull requests are welcome!

## 📝 License

[MIT](LICENSE)
