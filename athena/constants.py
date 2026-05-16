"""
全局常量定义
"""

from pathlib import Path

# 版本信息
VERSION = "0.1.0"
APP_NAME = "Athena-Plus"

# 路径常量
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
BUILTIN_SKILLS_DIR = SKILLS_DIR / "builtin"
CUSTOM_SKILLS_DIR = SKILLS_DIR / "custom"

# 数据库
DB_FILE = "{data_dir}/athena.db"

# 日志
LOG_FILE = "{data_dir}/athena.log"

# MCP 相关
DEFAULT_MCP_TIMEOUT = 30.0

# 会话状态
class SessionStatus:
    """会话状态常量"""
    INIT = "init"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    ERROR = "error"


# 工具执行状态
class ExecutionStatus:
    """工具执行状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
