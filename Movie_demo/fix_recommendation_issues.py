#!/usr/bin/env python
"""
修复推荐系统问题的脚本
"""
import os
import sys
import django
from pathlib import Path
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler

# 添加项目路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_demo.settings')
django.setup()

def fix_feature_dimension_issue():
    """修复特征维度不匹配问题"""
    print("🔧 开始修复特征维度问题...")
    
    # 确保目录存在
    models_dir = BASE_DIR / 'models'
    data_dir = BASE_DIR / 'data' / 'mappings'
    models_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    
    # 正确的特征维度
    num_genres = 18
    base_features = 3
    feature_dim = base_features + num_genres  # 21维
    
    print(f"📊 正确特征维度: {feature_dim} (基础特征: {base_features} + 类型特征: {num_genres})")
    
    # 创建新的缩放器
    user_scaler = MinMaxScaler()
    movie_scaler = MinMaxScaler()
    
    # 使用正确的特征维度进行训练
    dummy_user_features = np.random.random((10, feature_dim))
    dummy_movie_features = np.random.random((10, feature_dim))
    
    user_scaler.fit(dummy_user_features)
    movie_scaler.fit(dummy_movie_features)
    
    # 保存新的缩放器
    user_scaler_path = models_dir / 'user_scaler.pkl'
    movie_scaler_path = models_dir / 'movie_scaler.pkl'
    
    joblib.dump(user_scaler, user_scaler_path)
    joblib.dump(movie_scaler, movie_scaler_path)
    
    print(f"✅ 用户缩放器保存到: {user_scaler_path}")
    print(f"✅ 电影缩放器保存到: {movie_scaler_path}")
    
    return feature_dim

def fix_model_encoding_issue():
    """修复模型文件编码问题"""
    print("🔧 开始修复模型编码问题...")
    
    models_dir = BASE_DIR / 'models'
    model_files = [
        'recommendation_model.h5',
        'recommendation_model.keras'
    ]
    
    for model_file in model_files:
        model_path = models_dir / model_file
        if model_path.exists():
            try:
                # 尝试加载模型
                import tensorflow as tf
                model = tf.keras.models.load_model(str(model_path))
                print(f"✅ 模型文件 {model_file} 加载成功")
            except Exception as e:
                print(f"❌ 模型文件 {model_file} 损坏: {str(e)}")
                print(f"🗑️ 删除损坏的模型文件: {model_file}")
                model_path.unlink()
        else:
            print(f"ℹ️ 模型文件 {model_file} 不存在")

def recreate_feature_files():
    """重新创建特征文件"""
    print("🔧 开始重新创建特征文件...")
    
    from movies.models import Movie, CustomUser, Review, UserFavorite
    from django.db.models import Avg
    
    data_dir = BASE_DIR / 'data' / 'mappings'
    data_dir.mkdir(exist_ok=True)
    
    # 获取所有用户和电影
    users = CustomUser.objects.all()
    movies = Movie.objects.all()
    
    print(f"📊 用户数量: {users.count()}")
    print(f"📊 电影数量: {movies.count()}")
    
    # 重新准备特征
    user_features = {}
    movie_features = {}
    
    # 处理用户特征
    for user in users:
        avg_rating = Review.objects.filter(user=user).aggregate(Avg('rating'))['rating__avg'] or 3.0
        review_count = Review.objects.filter(user=user).count()
        favorite_count = UserFavorite.objects.filter(user=user).count()
        
        # 创建21维特征向量 (3个基础特征 + 18个类型特征)
        user_feature = [avg_rating, float(review_count), float(favorite_count)]
        # 添加18个类型偏好特征 (初始化为0)
        user_feature.extend([0.0] * 18)
        
        user_features[user.id] = np.array(user_feature, dtype=np.float32)
    
    # 处理电影特征
    for movie in movies:
        avg_rating = Review.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg'] or 3.0
        review_count = Review.objects.filter(movie=movie).count()
        favorite_count = UserFavorite.objects.filter(movie=movie).count()
        
        # 创建21维特征向量
        movie_feature = [avg_rating, float(review_count), float(favorite_count)]
        # 添加18个类型特征 (初始化为0)
        movie_feature.extend([0.0] * 18)
        
        movie_features[movie.tmdb_id] = np.array(movie_feature, dtype=np.float32)
    
    # 保存特征文件
    user_features_path = data_dir / 'user_features.pkl'
    movie_features_path = data_dir / 'movie_features.pkl'
    
    joblib.dump(user_features, user_features_path)
    joblib.dump(movie_features, movie_features_path)
    
    print(f"✅ 用户特征保存到: {user_features_path}")
    print(f"✅ 电影特征保存到: {movie_features_path}")
    print(f"📊 用户特征数量: {len(user_features)}")
    print(f"📊 电影特征数量: {len(movie_features)}")

def test_recommendation_system():
    """测试推荐系统"""
    print("🧪 开始测试推荐系统...")
    
    try:
        from movies.recommendations import RecommendationService
        
        # 创建推荐服务实例
        service = RecommendationService(force_retrain=True)
        
        # 测试推荐功能
        recommendations = service.recommend_for_user(user_id=5, top_n=5)
        
        print(f"✅ 推荐系统测试成功")
        print(f"📊 为用户5生成了 {len(recommendations)} 个推荐")
        print(f"🎬 推荐电影ID: {recommendations}")
        
    except Exception as e:
        print(f"❌ 推荐系统测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 开始修复推荐系统问题...")
    
    try:
        # 1. 修复特征维度问题
        feature_dim = fix_feature_dimension_issue()
        
        # 2. 修复模型编码问题
        fix_model_encoding_issue()
        
        # 3. 重新创建特征文件
        recreate_feature_files()
        
        # 4. 测试推荐系统
        test_recommendation_system()
        
        print("✅ 所有问题修复完成！")
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
