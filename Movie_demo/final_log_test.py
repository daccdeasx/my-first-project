#!/usr/bin/env python
"""
最终日志测试脚本
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

def test_all_logging():
    """测试所有日志功能"""
    import logging
    
    # 测试推荐服务日志
    logger = logging.getLogger('recommendations')
    logger.info("推荐服务启动 - 模型加载成功")
    logger.warning("推荐服务警告 - 部分特征缺失")
    logger.error("推荐服务错误 - 模型预测失败")
    
    # 测试电影服务日志
    movie_logger = logging.getLogger('movies')
    movie_logger.info("电影服务启动 - 数据同步完成")
    movie_logger.warning("电影服务警告 - TMDB API调用失败")
    
    # 测试用户服务日志
    user_logger = logging.getLogger('users')
    user_logger.info("用户服务启动 - 用户认证成功")
    user_logger.warning("用户服务警告 - 密码强度不足")
    
    print("所有日志测试完成")
    print("请检查以下日志文件:")
    print("- logs/system.log (系统日志)")
    print("- logs/recommendations.log (推荐服务日志)")

if __name__ == '__main__':
    test_all_logging()
