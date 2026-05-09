#!/usr/bin/env python
"""
修复日志编码问题的脚本
"""
import os
import sys
import django
from pathlib import Path

# 设置UTF-8编码
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 添加项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_demo.settings')
django.setup()

def test_utf8_logging():
    """测试UTF-8日志记录"""
    import logging
    
    # 创建日志记录器
    logger = logging.getLogger('utf8_test')
    logger.setLevel(logging.DEBUG)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 确保日志目录存在
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # 文件处理器 - 明确使用UTF-8编码
    file_handler = logging.FileHandler(
        log_dir / 'utf8_test.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 测试中文日志
    logger.info("测试中文日志记录 - UTF-8编码")
    logger.warning("测试中文警告信息")
    logger.error("测试中文错误信息")
    
    print("UTF-8日志测试完成")
    print(f"请检查日志文件: {log_dir / 'utf8_test.log'}")

if __name__ == '__main__':
    test_utf8_logging()
