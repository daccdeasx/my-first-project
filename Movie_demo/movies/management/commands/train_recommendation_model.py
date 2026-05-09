from django.core.management.base import BaseCommand
from movies.recommendations import RecommendationService
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '训练推荐模型'

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
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新训练，即使存在现有模型'
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write('初始化推荐服务...')
            recommendation_service = RecommendationService(force_retrain=options['force'])
            
            if options['force']:
                self.stdout.write('强制重新训练模型...')
            
            # 初始化服务
            recommendation_service.init_service()
            
            # 准备特征
            self.stdout.write('准备特征数据...')
            recommendation_service.prepare_features()
            
            # 训练模型
            self.stdout.write('开始训练模型...')
            history = recommendation_service.train_model(
                epochs=options['epochs'],
                batch_size=options['batch_size']
            )
            
            # 保存训练历史，便于绘制指标曲线
            try:
                hist_dict = history.history if hasattr(history, 'history') else None
                if hist_dict:
                    logs_dir = Path(recommendation_service.BASE_DIR) / 'logs'
                    logs_dir.mkdir(parents=True, exist_ok=True)
                    hist_path = logs_dir / 'training_history.json'
                    with hist_path.open('w', encoding='utf-8') as f:
                        json.dump(hist_dict, f, ensure_ascii=False, indent=2)
                    self.stdout.write(self.style.SUCCESS(f'训练历史已保存: {hist_path}'))
            except Exception as save_err:
                logger.warning(f'训练历史保存失败: {save_err}')
            
            self.stdout.write(self.style.SUCCESS('模型训练完成！'))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'训练失败: {str(e)}'))
            raise 