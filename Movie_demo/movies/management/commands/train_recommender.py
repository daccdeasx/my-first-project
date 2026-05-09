# movies/management/commands/train_recommender.py
import os

from django.core.management.base import BaseCommand
from django.utils import timezone  # 添加这行
import logging

from movies.recommendations import RecommendationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '训练推荐系统模型'

    def add_arguments(self, parser):
        parser.add_argument(
            '--epochs',
            type=int,
            default=10,
            help='训练轮数'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=256,
            help='批次大小'
        )

    # management/commands/train_recommender.py
    def handle(self, *args, **options):
        try:
            service = RecommendationService()
            service.init_service()

            # 验证必要属性
            essential_attrs = [
                'user_mapping', 'movie_mapping',
                'user_features', 'movie_features',
                'model'
            ]
            for attr in essential_attrs:
                if not hasattr(service, attr):
                    raise AttributeError(f"缺失关键属性: {attr}")

            # 执行训练
            self.stdout.write(self.style.SUCCESS('开始模型训练...'))
            service.train_model(
                epochs=options['epochs'],
                batch_size=options['batch_size']
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'训练失败: {str(e)}'))
            # 生成简单错误报告
            error_report = f"""
            [ERROR REPORT]
            时间: {timezone.now()}
            异常类型: {type(e).__name__}
            异常信息: {str(e)}
            服务状态: 
                - 用户映射: {len(getattr(service, 'user_mapping', {}))}
                - 电影映射: {len(getattr(service, 'movie_mapping', {}))}
                - 模型存在: {os.path.exists(service.MODEL_PATH)}
            """
            logger.critical(error_report)
            self.stdout.write(self.style.NOTICE(error_report))