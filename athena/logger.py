"""
日志模块
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from athena.config import settings
from athena.constants import LOG_FILE


def setup_logger(name: str = "athena", log_file: Optional[Path] = None) -> logging.Logger:
    """设置日志"""
    
    if log_file is None:
        log_file = settings.data_dir / "athena.log"
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# 全局日志实例
logger = setup_logger()
