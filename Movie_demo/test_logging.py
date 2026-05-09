#!/usr/bin/env python
"""
测试日志编码脚本
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

def test_logging():
    """测试日志功能"""
    from movies.logging_utils import get_logger
    
    # 测试推荐服务日志
    logger = get_logger('recommendations')
    logger.info("测试推荐服务日志记录")
    logger.warning("测试推荐服务警告信息")
    logger.error("测试推荐服务错误信息")
    
    # 测试中文日志
    logger.info("测试中文日志记录 - 推荐模型加载成功")
    logger.warning("测试中文警告 - 模型文件不存在")
    logger.error("测试中文错误 - 推荐生成失败")
    
    print("日志测试完成，请检查logs目录下的recommendations.log文件")

if __name__ == '__main__':
    test_logging()
