# Athena-Plus Windows 开发指南

**原生 Windows AI Agent 开发规范**

## 环境要求

### Python 环境
- Python 3.10+ (推荐 3.12)
- 虚拟环境：`.\venv\Scripts\Activate.ps1`
- pip 升级：`python -m pip install --upgrade pip`

### 必需依赖
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 安装 Windows 特定依赖
pip install pywin32 pypiwin32
```

### 系统要求
- Windows 10/11
- PowerShell 5.1+ 或 PowerShell 7+
- 可选：Ollama (本地模型运行)

## 项目结构

```
Athena-Plus/
├── athena/              # 核心基础库
├── agent/               # AI Agent 引擎
├── tools/               # 工具集
│   ├── base.py         # 工具基类
│   ├── files/          # 文件操作
│   ├── terminal/       # 终端命令
│   ├── system/         # 系统信息
│   ├── windows/        # Windows 专属工具
│   ├── browser/        # 浏览器集成
│   └── ollama/        # Ollama 管理
├── skills/             # 技能系统
├── web/                # Web UI + FastAPI
├── cli/                # 命令行界面
├── gui/                # PyWebView 桌面应用
└── data/               # 运行时数据
```

## 开发规范

### 1. 路径处理（Windows 兼容）
```python
from pathlib import Path

# ✅ 正确：使用 pathlib（跨平台兼容）
path = Path("data/logs/app.log")
absolute_path = path.resolve()

# ❌ 错误：硬编码路径分隔符
path = "data\\logs\\app.log"  # 不推荐
```

### 2. 命令执行（PowerShell vs Bash）
```python
import asyncio

# ✅ 正确：使用 asyncio.create_subprocess_shell (跨平台)
process = await asyncio.create_subprocess_shell(
    "dir" if os.name == 'nt' else 'ls',
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)

# ❌ 错误：假设系统使用 Bash
os.system("ls -la")  # Windows 上会失败
```

### 3. 编码处理（UTF-8 vs GBK）
```python
# ✅ 正确：显式指定编码
content = path.read_text(encoding='utf-8')

# 读取系统命令输出（Windows 可能返回 GBK）
stdout = stdout.decode('utf-8', errors='replace')
```

### 4. Windows 特定功能
```python
# ✅ 使用 pywin32 访问 Windows API
import win32api
import win32gui
import win32con

# 发送通知
win32gui.MessageBox(None, "消息", "标题", win32con.MB_OK)

# 注册表访问
import winreg
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft") as key:
    value, _ = winreg.QueryValueEx(key, "SomeValue")
```

### 5. 异步编程（asyncio）
```python
# ✅ 正确：使用 async/await
async def chat(message: str) -> AsyncGenerator[Dict, None]:
    async for chunk in mcp_client.stream_chat(session):
        yield chunk

# 调用
async for response in agent.chat("Hello"):
    print(response)
```

## 配置管理

### .env 文件配置
```bash
# 复制模板
copy .env.example .env

# 编辑配置
notepad .env
```

### 必需配置项
```bash
# 云端 Gabriel MCP 连接
GABRIEL_MCP_URL=http://10.0.0.1:8000/mcp
GABRIEL_MCP_API_KEY=your_api_key_here

# 本地 Ollama 配置
OLLAMA_BASE_URL=http://127.0.0.1:11434
DEFAULT_MODEL=qwen2.5:7b-instruct-q4_K_M

# 服务器配置
HOST=127.0.0.1
PORT=8000

# 安全配置
ENABLE_DANGEROUS_COMMAND_CONFIRMATION=true
ALLOWED_COMMANDS=dir,cd,python,git,pip
```

## 启动方式

### 1. Web 服务器模式（推荐）
```powershell
.\venv\Scripts\Activate.ps1
python main.py web
```

访问：http://127.0.0.1:8000/static/index.html

### 2. 命令行模式
```powershell
.\venv\Scripts\Activate.ps1
python main.py cli
```

### 3. 桌面 GUI 模式
```powershell
.\venv\Scripts\Activate.ps1
python main.py gui
```

## 测试

### 单元测试
```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

### 语法检查
```powershell
.\venv\Scripts\Activate.ps1
python -m py_compile agent/core.py
python -m py_compile tools/windows/windows_tools.py
```

### 类型检查
```powershell
.\venv\Scripts\Activate.ps1
mypy agent/ tools/
```

### Lint 检查
```powershell
.\venv\Scripts\Activate.ps1
flake8 agent/ tools/ web/ --max-line-length=120
```

## 常见问题

### 1. pywin32 安装失败
```powershell
# 解决方案：以管理员身份运行 PowerShell
.\venv\Scripts\Activate.ps1
pip uninstall pywin32 -y
pip install pywin32

# 执行 post-install 脚本
python .\venv\Scripts\pywin32_postinstall.py -install
```

### 2. PowerShell 执行策略错误
```powershell
# 允许本地脚本运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Ollama 连接失败
```powershell
# 检查 Ollama 是否运行
curl http://127.0.0.1:11434/api/tags

# 启动 Ollama 服务
ollama serve
```

### 4. MCP 连接失败
```powershell
# 检查云端 Gabriel 连接
curl http://10.0.0.1:8000/mcp/ping

# 检查 WireGuard 连接
ping 10.0.0.1
```

## 部署

### 开发模式
```powershell
# 启用调试模式
$env:DEBUG = "true"
python main.py web
```

### 生产模式
```powershell
# 禁用调试模式
$env:DEBUG = "false"
python main.py web --host 0.0.0.0 --port 8000
```

### Windows 开机自启
```powershell
# 创建启动脚本
@echo off
call .\venv\Scripts\activate.bat
python main.py web
```

保存到：`C:\Users\laure\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\athena-plus.bat`

## 项目状态

### ✅ 已完成
- [x] 项目骨架搭建
- [x] 核心 Agent 引擎（移除 Hermes 依赖）
- [x] 工具执行器框架
- [x] 文件操作工具（读/写/列表）
- [x] 系统信息工具
- [x] 终端命令工具
- [x] Windows 专属工具（通知/注册表/电源）
- [x] Ollama 模型管理工具
- [x] 技能加载器（兼容 Hermes 格式）
- [x] Web UI（FastAPI + 前端）
- [x] MCP 客户端（对接云端 Gabriel）

### 🚧 待完成
- [ ] CLI 命令行界面完善
- [ ] GUI 桌面应用（PyWebView）
- [ ] 技能系统测试
- [ ] 完整集成测试
- [ ] 性能优化
- [ ] 文档完善

## 贡献指南

### 添加新工具
1. 在 `tools/` 对应子目录创建工具类
2. 继承 `BaseTool`
3. 实现 `execute()` 和 `get_schema()` 方法
4. 在 `agent/executor.py` 中注册工具

### 添加新技能
1. 在 `skills/builtin/` 或 `skills/custom/` 创建目录
2. 创建 `SKILL.md`（YAML frontmatter + Markdown）
3. 重启服务自动加载

## 许可证

MIT License

---

**最后更新**: 2026-05-14  
**维护者**: Athena-Plus Team  
**支持**: Windows 10/11, Python 3.10+
