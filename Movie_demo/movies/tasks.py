# movies/tasks.py
from celery import shared_task
from .recommendations import RecommendationService, logger
from .views import get_or_create_movie
from django.utils import timezone
from datetime import timedelta
import logging
from django.core.cache import cache
from django.db.models import Count, Avg

logger = logging.getLogger(__name__)

@shared_task
def daily_model_retrain():
    service = RecommendationService()
    service.load_mappings()
    service.prepare_features()
    service.train_model(epochs=10)
    logger.info("Daily model retraining completed")

@shared_task
def refresh_features():
    service = RecommendationService()
    service.prepare_features()
    service.save_scaler()
    logger.info("Feature refresh completed")

def async_sync_movies(movie_ids):
    for mid in movie_ids:
        try:
            get_or_create_movie(mid)
        except Exception as e:
            logger.error(f"异步同步失败 {mid}: {str(e)}")

@shared_task
def update_recommendation_model():
    """定时更新推荐模型"""
    try:
        # 获取锁，防止多个worker同时执行
        lock_id = "update_recommendation_model_lock"
        if cache.add(lock_id, "true", timeout=3600):  # 1小时锁
            try:
                logger.info("开始更新推荐模型...")
                
                # 初始化推荐服务
                recommendation_service = RecommendationService()
                recommendation_service.init_service()
                
                # 准备特征
                recommendation_service.prepare_features()
                
                # 训练模型
                recommendation_service.train_model(
                    epochs=10,
                    batch_size=256
                )
                
                logger.info("推荐模型更新完成")
                
                # 记录更新时间
                cache.set(
                    'last_model_update',
                    timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    timeout=None
                )
                
            finally:
                # 释放锁
                cache.delete(lock_id)
        else:
            logger.warning("另一个更新任务正在进行中")
            
    except Exception as e:
        logger.error(f"更新推荐模型时出错: {str(e)}")
        raise

@shared_task
def update_user_features():
    """更新用户特征（可以更频繁执行）"""
    try:
        recommendation_service = RecommendationService()
        recommendation_service.prepare_features()
        logger.info("用户特征更新完成")
    except Exception as e:
        logger.error(f"更新用户特征时出错: {str(e)}")
        raise

@shared_task
def cleanup_old_models():
    """清理旧的模型文件"""
    try:
        import os
        from django.conf import settings
        
        model_dir = os.path.join(settings.BASE_DIR, 'models')
        backup_dir = os.path.join(model_dir, 'backup')
        
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        
        # 保留最近5个备份
        backup_files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.h5')],
            reverse=True
        )[5:]
        
        # 删除旧备份
        for f in backup_files:
            os.remove(os.path.join(backup_dir, f))
            
        logger.info(f"清理了 {len(backup_files)} 个旧模型文件")
        
    except Exception as e:
        logger.error(f"清理旧模型文件时出错: {str(e)}")