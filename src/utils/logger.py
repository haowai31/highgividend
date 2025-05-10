"""
日志工具模块 - 负责日志的配置和格式化
"""
import logging
import os
from typing import Optional
from pathlib import Path

def setup_logger(name: str, 
                log_level: str = "INFO",
                log_file: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
        log_file: 日志文件路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
        
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger 