import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# 设置默认Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_demo.settings')

app = Celery('Movie_demo')

# 使用Django的设置文件配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 设置定时任务
app.conf.beat_schedule = {
    # 每天凌晨3点更新推荐模型
    'update-recommendation-model': {
        'task': 'movies.tasks.update_recommendation_model',
        'schedule': crontab(hour=3, minute=0),
    },
    # 每4小时更新一次用户特征
    'update-user-features': {
        'task': 'movies.tasks.update_user_features',
        'schedule': crontab(hour='*/4'),
    },
    # 每周清理一次旧模型文件
    'cleanup-old-models': {
        'task': 'movies.tasks.cleanup_old_models',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # 每周一凌晨2点
    },
}

# 自动发现任务
app.autodiscover_tasks() 