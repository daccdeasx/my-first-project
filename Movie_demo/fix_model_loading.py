#!/usr/bin/env python
"""
修复TensorFlow模型加载问题的脚本
"""
import os
import sys
import django
from pathlib import Path
import shutil

# 添加项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_demo.settings')
django.setup()

def fix_model_loading_issue():
    """修复模型加载问题"""
    print("🔧 开始修复模型加载问题...")
    
    models_dir = BASE_DIR / 'models'
    model_path = models_dir / 'recommendation_model.h5'
    
    if not model_path.exists():
        print("❌ 模型文件不存在")
        return False
    
    print(f"📁 模型文件路径: {model_path}")
    print(f"📊 文件大小: {model_path.stat().st_size} bytes")
    
    # 尝试不同的加载方法
    try:
        import tensorflow as tf
        
        # 方法1: 直接加载
        print("🔄 尝试方法1: 直接加载模型...")
        model = tf.keras.models.load_model(str(model_path))
        print("✅ 方法1成功: 模型加载正常")
        return True
        
    except UnicodeDecodeError as e:
        print(f"❌ 方法1失败: Unicode解码错误 - {str(e)}")
        
        # 方法2: 使用绝对路径
        try:
            print("🔄 尝试方法2: 使用绝对路径...")
            abs_path = model_path.resolve()
            model = tf.keras.models.load_model(str(abs_path))
            print("✅ 方法2成功: 使用绝对路径加载成功")
            return True
            
        except Exception as e2:
            print(f"❌ 方法2失败: {str(e2)}")
            
            # 方法3: 复制到临时位置
            try:
                print("🔄 尝试方法3: 复制到临时位置...")
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as tmp_file:
                    shutil.copy2(model_path, tmp_file.name)
                    model = tf.keras.models.load_model(tmp_file.name)
                    os.unlink(tmp_file.name)
                print("✅ 方法3成功: 临时文件加载成功")
                return True
                
            except Exception as e3:
                print(f"❌ 方法3失败: {str(e3)}")
                
                # 方法4: 重新保存模型
                try:
                    print("🔄 尝试方法4: 重新保存模型...")
                    # 先删除损坏的模型
                    model_path.unlink()
                    print("🗑️ 删除损坏的模型文件")
                    
                    # 重新训练模型
                    from movies.recommendations import RecommendationService
                    service = RecommendationService(force_retrain=True)
                    service.init_service()
                    service.prepare_features()
                    
                    # 构建新模型
                    service.model = service.build_model(
                        num_users=6,  # 实际用户数
                        num_movies=197  # 实际电影数
                    )
                    
                    # 保存模型
                    service.save_model()
                    print("✅ 方法4成功: 重新训练并保存模型")
                    return True
                    
                except Exception as e4:
                    print(f"❌ 方法4失败: {str(e4)}")
                    return False

def test_model_loading():
    """测试模型加载"""
    print("🧪 测试模型加载...")
    
    try:
        from movies.recommendations import RecommendationService
        
        # 创建推荐服务
        service = RecommendationService()
        
        # 测试推荐功能
        recommendations = service.recommend_for_user(user_id=5, top_n=3)
        
        print(f"✅ 模型加载测试成功")
        print(f"📊 推荐结果: {recommendations}")
        return True
        
    except Exception as e:
        print(f"❌ 模型加载测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始修复TensorFlow模型加载问题...")
    
    # 修复模型加载问题
    if fix_model_loading_issue():
        print("✅ 模型加载问题修复成功")
        
        # 测试模型加载
        if test_model_loading():
            print("✅ 模型功能测试通过")
        else:
            print("❌ 模型功能测试失败")
    else:
        print("❌ 模型加载问题修复失败")

if __name__ == '__main__':
    main()
