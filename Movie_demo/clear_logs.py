#!/usr/bin/env python
"""
清理日志文件脚本
用于解决日志编码问题
"""
import os
import sys
import django
from pathlib import Path

# 添加项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_demo.settings')
django.setup()

def clear_logs():
    """清理日志文件"""
    log_dir = BASE_DIR / 'logs'
    
    if log_dir.exists():
        print("正在清理日志文件...")
        for log_file in log_dir.glob('*.log'):
            print(f"删除日志文件: {log_file}")
            log_file.unlink()
        print("日志文件清理完成")
    else:
        print("日志目录不存在，创建中...")
        log_dir.mkdir(exist_ok=True)
        print("日志目录创建完成")

def test_logging():
    """测试日志功能"""
    from movies.logging_utils import get_logger
    
    logger = get_logger('test')
    logger.info("测试中文日志记录")
    logger.warning("测试警告信息")
    logger.error("测试错误信息")
    print("日志测试完成，请检查logs目录下的test.log文件")

if __name__ == '__main__':
    clear_logs()
    test_logging()
