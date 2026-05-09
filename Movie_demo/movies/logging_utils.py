# movies/logging_utils.py
import logging
import logging.handlers
import os
import sys
import io
from django.conf import settings

def setup_logger(name, level=logging.DEBUG):
    """
    设置带有正确编码的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 确保日志目录存在
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 文件处理器 - 使用UTF-8编码
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, f'{name}.log'),
        encoding='utf-8',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器 - 使用UTF-8编码的StringIO
    console_handler = logging.StreamHandler(
        io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    )
    console_handler.setLevel(logging.DEBUG)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    """
    获取日志记录器，如果不存在则创建
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

# 预定义的日志记录器
recommendation_logger = get_logger('recommendations')
movie_logger = get_logger('movies')
user_logger = get_logger('users')
api_logger = get_logger('api')
