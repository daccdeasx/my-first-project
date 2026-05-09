import os
import logging
import numpy as np
from django.db import transaction
from django.db.models import Count, Avg, Q
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
import joblib
from django.conf import settings
from sklearn.cluster import KMeans
from django.utils import timezone
import pickle

from movies.models import Movie, CustomUser, Review, UserFavorite

# 配置logger - 使用UTF-8编码
from .logging_utils import get_logger
logger = get_logger('recommendations')

# 尝试导入TensorFlow
try:
    import tensorflow as tf
    from tensorflow.keras.layers import Embedding, Flatten, Dense, Concatenate, Input, Dropout
    from tensorflow.keras.models import Model, load_model
    from tensorflow.keras.optimizers import Adam
    
    # 配置TensorFlow
    tf.config.set_visible_devices([], 'GPU')  # 禁用GPU
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)
    
    TENSORFLOW_AVAILABLE = True
    logger.info("TensorFlow successfully imported")
except ImportError as e:
    logger.warning(f"TensorFlow import failed: {str(e)}")
    TENSORFLOW_AVAILABLE = False
except Exception as e:
    logger.warning(f"TensorFlow configuration failed: {str(e)}")
    TENSORFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


def default_user_feature():
    # 基础特征：平均评分、评论数、收藏数
    base_features = [3.0, 0.0, 0.0]
    # 类型偏好：18个类型的偏好分数（全部为0）
    genre_preferences = [0.0] * 18
    return base_features + genre_preferences


def default_movie_feature():
    # 基础特征：平均评分、评论数、收藏数
    base_features = [3.0, 0.0, 0.0]
    # 类型向量：18个类型的独热编码（全部为0）
    genre_vector = [0.0] * 18
    return base_features + genre_vector


class RecommendationService:
    """推荐服务"""
    
    def __init__(self, force_retrain=False):
        """初始化推荐服务
        
        Args:
            force_retrain: 是否强制重新训练模型
        """
        self.force_retrain = force_retrain
        self.model = None
        
        # 创建必要的目录
        os.makedirs(os.path.join(settings.BASE_DIR, 'models'), exist_ok=True)
        os.makedirs(os.path.join(settings.BASE_DIR, 'data', 'mappings'), exist_ok=True)
        os.makedirs(os.path.join(settings.BASE_DIR, 'logs'), exist_ok=True)

        # 调整路径配置
        self.BASE_DIR = settings.BASE_DIR
        self.MODEL_DIR = os.path.join(settings.BASE_DIR, 'models')
        self.DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
        self.MAPPING_DIR = os.path.join(self.DATA_DIR, 'mappings')

        # 文件路径 - 使用.h5格式（更稳定）
        self.model_path = os.path.join(self.MODEL_DIR, 'recommendation_model.h5')
        self.MODEL_PATH = self.model_path  # 保持大写命名的兼容性
        self.USER_SCALER_PATH = os.path.join(self.MODEL_DIR, 'user_scaler.pkl')
        self.MOVIE_SCALER_PATH = os.path.join(self.MODEL_DIR, 'movie_scaler.pkl')
        self.USER_FEATURES_PATH = os.path.join(self.MAPPING_DIR, 'user_features.pkl')
        self.MOVIE_FEATURES_PATH = os.path.join(self.MAPPING_DIR, 'movie_features.pkl')
        self.FEATURE_SIZE = 64

        # 默认特征函数
        self.default_user_feature = default_user_feature
        self.default_movie_feature = default_movie_feature

        # 核心数据结构
        self.user_mapping = {}
        self.movie_mapping = {}
        self.user_features = defaultdict(self.default_user_feature)
        self.movie_features = defaultdict(self.default_movie_feature)
        self.user_scaler = MinMaxScaler()
        self.movie_scaler = MinMaxScaler()
        self.movie_embeddings = {}

        try:
            if not TENSORFLOW_AVAILABLE:
                logger.warning("TensorFlow不可用，将使用规则基础推荐")
                self.build_fallback_model()
            else:
                # 初始化服务
                self.init_service()
                # 加载映射和特征
                self.load_mappings()
                self.load_features()
        except Exception as e:
            logger.error(f"推荐服务初始化失败: {str(e)}")
            # 使用应急模型
            self.build_fallback_model()

    def init_service(self):
        """初始化推荐服务"""
        try:
            # 尝试加载现有模型
            if os.path.exists(self.model_path) and not self.force_retrain:
                try:
                    # 加载.h5格式模型
                    self.model = load_model(self.model_path)
                    logger.info("成功加载现有模型")
                except Exception as e:
                    logger.warning(f"加载现有模型失败: {str(e)}")
                    self.model = None
            
            # 如果没有模型，构建一个新的
            if self.model is None:
                logger.info("构建新模型")
                try:
                    self.model = self.build_model(
                        num_users=max(CustomUser.objects.count(), 100),
                        num_movies=max(Movie.objects.count(), 100)
                    )
                    logger.info("新模型构建成功")
                except Exception as e:
                    logger.error(f"构建新模型失败: {str(e)}")
                    self.build_fallback_model()
            
            logger.info("推荐服务初始化完成")
            
        except Exception as e:
            logger.error(f"初始化推荐服务失败: {str(e)}")
            self.build_fallback_model()

    def _init_embeddings(self):
        if self.model:
            movie_embedding_layer = self.model.get_layer('movie_embedding')
            weights = movie_embedding_layer.get_weights()[0]
            for mid, idx in self.movie_mapping.items():
                self.movie_embeddings[mid] = weights[idx]

    def load_mappings(self):
        """加载用户和电影的映射关系（兼容Windows路径）"""
        map_dir = os.path.join(settings.BASE_DIR, 'data', 'mappings')
        try:
            self.user_mapping = joblib.load(os.path.join(map_dir, 'user_mapping.pkl'))
            self.movie_mapping = joblib.load(os.path.join(map_dir, 'movie_mapping.pkl'))
            logger.debug("成功加载现有映射文件")
        except FileNotFoundError:
            logger.warning("映射文件不存在，创建新映射")
            self._create_new_mappings()
            self.save_mappings()

    def save_mappings(self):
        map_dir = os.path.join(settings.BASE_DIR, 'data/mappings')
        joblib.dump(self.user_mapping, os.path.join(map_dir, 'user_mapping.pkl'))
        joblib.dump(self.movie_mapping, os.path.join(map_dir, 'movie_mapping.pkl'))

    def load_features(self):
        """加载特征数据"""
        try:
            logger.info(f"尝试加载用户特征文件: {self.USER_FEATURES_PATH}")
            logger.info(f"尝试加载电影特征文件: {self.MOVIE_FEATURES_PATH}")

            if not os.path.exists(self.USER_FEATURES_PATH):
                raise FileNotFoundError(f"用户特征文件不存在: {self.USER_FEATURES_PATH}")
            if not os.path.exists(self.MOVIE_FEATURES_PATH):
                raise FileNotFoundError(f"电影特征文件不存在: {self.MOVIE_FEATURES_PATH}")

            user_features = joblib.load(self.USER_FEATURES_PATH)
            movie_features = joblib.load(self.MOVIE_FEATURES_PATH)

            # 使用绑定的默认函数
            self.user_features = defaultdict(self.default_user_feature, user_features)
            self.movie_features = defaultdict(self.default_movie_feature, movie_features)

            # 加载scaler
            self.user_scaler = joblib.load(self.USER_SCALER_PATH)
            self.movie_scaler = joblib.load(self.MOVIE_SCALER_PATH)

            logger.info("成功加载特征缓存")
        except Exception as e:
            logger.error(f"特征加载失败: {str(e)}")
            # 初始化默认scaler - 使用21维特征
            default_user_feat = default_user_feature()
            default_movie_feat = default_movie_feature()
            self.user_scaler = MinMaxScaler().fit([default_user_feat])
            self.movie_scaler = MinMaxScaler().fit([default_movie_feat])
            self.prepare_features()

    def prepare_features(self):
        """准备训练数据"""
        try:
            # 获取所有用户和电影的特征
            user_features = {}
            movie_features = {}
            
            # 处理用户特征
            for user in CustomUser.objects.all():
                # 获取用户统计数据
                avg_rating = Review.objects.filter(user=user).aggregate(Avg('rating'))['rating__avg'] or 3.0
                review_count = Review.objects.filter(user=user).count()
                favorite_count = UserFavorite.objects.filter(user=user).count()
                
                # 获取用户的类型偏好
                genre_preferences = self._get_user_genre_preferences(user.id)
                
                # 组合所有特征
                user_features[user.id] = np.array([
                    avg_rating,
                    float(review_count),
                    float(favorite_count),
                    *genre_preferences  # 展开类型偏好向量
                ], dtype=np.float32)
            
            # 处理电影特征
            for movie in Movie.objects.all():
                # 基础特征
                avg_rating = Review.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg'] or 3.0
                review_count = Review.objects.filter(movie=movie).count()
                favorite_count = UserFavorite.objects.filter(movie=movie).count()
                
                # 类型向量
                genre_vector = self._get_genre_vector(movie.genres)
                
                # 组合所有特征 - 使用tmdb_id作为键
                movie_features[movie.tmdb_id] = np.array([
                    avg_rating,
                    float(review_count),
                    float(favorite_count),
                    *genre_vector  # 展开类型向量
                ], dtype=np.float32)
            
            # 保存特征
            self.user_features = user_features
            self.movie_features = movie_features
            
            # 训练缩放器
            if user_features:
                user_feature_array = np.array(list(user_features.values()))
                self.user_scaler.fit(user_feature_array)
                logger.info(f"用户特征缩放器训练完成，特征维度: {user_feature_array.shape[1]}")
            
            if movie_features:
                movie_feature_array = np.array(list(movie_features.values()))
                self.movie_scaler.fit(movie_feature_array)
                logger.info(f"电影特征缩放器训练完成，特征维度: {movie_feature_array.shape[1]}")
            
            logger.info(f"特征准备完成：用户数={len(user_features)}, 电影数={len(movie_features)}")
            
        except Exception as e:
            logger.error(f"特征准备失败: {str(e)}")
            raise

    def _get_user_features(self, user_id):
        """计算用户特征"""
        # 实现用户特征计算逻辑
        pass

    def _get_genre_vector(self, genres):

        """获取电影类型的向量表示"""
        # 定义所有可能的电影类型（使用英文，与TMDB API保持一致）
        all_genres = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
            'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
            'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
            'Thriller', 'War', 'Western'
        ]
        
        # 创建类型映射字典
        genre_mapping = {
            '动作': 'Action', '冒险': 'Adventure', '动画': 'Animation',
            '喜剧': 'Comedy', '犯罪': 'Crime', '纪录片': 'Documentary',
            '剧情': 'Drama', '家庭': 'Family', '奇幻': 'Fantasy',
            '历史': 'History', '恐怖': 'Horror', '音乐': 'Music',
            '悬疑': 'Mystery', '爱情': 'Romance', '科幻': 'Science Fiction',
            '惊悚': 'Thriller', '战争': 'War', '西部': 'Western'
        }
        
        # 处理genres可能是列表或字符串的情况
        if isinstance(genres, str):
            movie_genres = [g.strip() for g in genres.split(',')]
        elif isinstance(genres, list):
            movie_genres = genres
        else:
            movie_genres = []
        
        # 将中文类型转换为英文
        movie_genres = [genre_mapping.get(g, g) for g in movie_genres]
        
        # 创建独热编码向量
        return [1.0 if genre in movie_genres else 0.0 for genre in all_genres]

    def _get_user_genre_preferences(self, user_id):
        """计算用户对不同类型的偏好"""
        # 定义所有可能的电影类型（与_get_genre_vector保持一致）
        all_genres = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
            'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
            'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
            'Thriller', 'War', 'Western'
        ]
        
        # 初始化每个类型的评分和计数
        genre_ratings = {genre: [] for genre in all_genres}
        genre_counts = {genre: 0 for genre in all_genres}
        
        # 获取用户评分
        reviews = Review.objects.filter(user_id=user_id).select_related('movie')
        for review in reviews:
            if review.movie.genres:
                movie_genres = self._get_genre_vector(review.movie.genres)
                for i, is_genre in enumerate(movie_genres):
                    if is_genre:
                        genre_ratings[all_genres[i]].append(review.rating)
                        genre_counts[all_genres[i]] += 1
        
        # 获取用户收藏
        favorites = UserFavorite.objects.filter(user_id=user_id).select_related('movie')
        for favorite in favorites:
            if favorite.movie.genres:
                movie_genres = self._get_genre_vector(favorite.movie.genres)
                for i, is_genre in enumerate(movie_genres):
                    if is_genre:
                        genre_counts[all_genres[i]] += 2  # 收藏的权重更高
        
        # 计算每个类型的偏好分数
        genre_preferences = []
        for genre in all_genres:
            if genre_ratings[genre]:
                avg_rating = sum(genre_ratings[genre]) / len(genre_ratings[genre])
                count_weight = min(genre_counts[genre] / 5, 1)  # 观看/收藏数量的权重
                preference = avg_rating * (1 + count_weight)
            else:
                preference = 0.0
            genre_preferences.append(float(preference))
        
        return genre_preferences

    def build_model(self, num_users, num_movies):
        """构建推荐模型"""
        from tensorflow.keras.layers import Input, Embedding, Flatten, Dense, Concatenate, Dropout
        from tensorflow.keras.models import Model
        
        # 计算特征维度
        num_genres = 18  # 更新为新的类型数量
        base_features = 3  # 平均评分、评论数、收藏数
        feature_dim = base_features + num_genres  # 总特征维度
        
        # 输入层
        user_input = Input(shape=(1,), name='user_input')
        movie_input = Input(shape=(1,), name='movie_input')
        user_features_input = Input(shape=(feature_dim,), name='user_features_input')
        movie_features_input = Input(shape=(feature_dim,), name='movie_features_input')
        
        # Embedding层
        user_embedding = Embedding(num_users, 50, name='user_embedding')(user_input)
        movie_embedding = Embedding(num_movies, 50, name='movie_embedding')(movie_input)
        
        # 展平Embedding
        user_embedding_flat = Flatten()(user_embedding)
        movie_embedding_flat = Flatten()(movie_embedding)
        
        # 合并所有特征
        concat = Concatenate()(
            [user_embedding_flat, movie_embedding_flat, user_features_input, movie_features_input]
        )
        
        # 全连接层（增加了dropout来防止过拟合）
        dense1 = Dense(256, activation='relu')(concat)
        dropout1 = Dropout(0.3)(dense1)
        
        dense2 = Dense(128, activation='relu')(dropout1)
        dropout2 = Dropout(0.2)(dense2)
        
        dense3 = Dense(64, activation='relu')(dropout2)
        dropout3 = Dropout(0.1)(dense3)
        
        # 输出层
        output = Dense(1, activation='linear')(dropout3)
        
        # 构建模型
        model = Model(
            inputs=[user_input, movie_input, user_features_input, movie_features_input],
            outputs=output
        )
        
        # 编译模型
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        return model

    def recommend_for_user(self, user_id, top_n=10, watched_tmdb_ids=None):
        """为用户推荐电影"""
        try:
            logger.info(f"开始为用户 {user_id} 生成推荐")

            # 评估时可能需要自定义“已看集合”（例如留一法：把留出的正例从已看集合移除）
            if watched_tmdb_ids is None:
                watched_movies = set(
                    Review.objects.filter(user_id=user_id)
                    .values_list('movie__tmdb_id', flat=True)
                )
            else:
                watched_movies = set(int(mid) for mid in watched_tmdb_ids if mid is not None)

            # 收藏集合目前未用于候选过滤，但保留变量便于后续扩展
            favorite_movies = set(
                UserFavorite.objects.filter(user_id=user_id)
                .values_list('movie__tmdb_id', flat=True)
            )
            
            # 获取用户评分历史
            user_reviews = Review.objects.filter(user_id=user_id).select_related('movie')
            
            # 获取用户的类型偏好
            genre_preferences = self._get_user_genre_preferences(user_id)
            
            # 获取候选电影
            candidate_movies = Movie.objects.exclude(
                tmdb_id__in=watched_movies
            ).filter(
                poster_path__isnull=False
            ).exclude(
                poster_path=''
            )
            
            # 如果没有候选电影，返回热门电影
            if not candidate_movies.exists():
                logger.warning("没有合适的候选电影，返回热门电影")
                return self._get_popular_movies(top_n)
            
            try:
                # 使用深度学习模型进行预测
                if self.model:
                    logger.info("使用深度学习模型生成推荐")
                    movie_scores = []
                    
                    # 准备用户特征
                    user_idx = self.user_mapping.get(user_id, 0)
                    user_features = self.user_features[user_id]
                    user_features = self.user_scaler.transform([user_features])[0]
                    
                    # 批量预测所有候选电影
                    batch_size = 100
                    for i in range(0, len(candidate_movies), batch_size):
                        batch_movies = candidate_movies[i:i+batch_size]
                        
                        # 准备电影特征
                        movie_indices = []
                        movie_features_batch = []
                        
                        for movie in batch_movies:
                            movie_idx = self.movie_mapping.get(movie.tmdb_id, 0)
                            movie_indices.append(movie_idx)
                            
                            movie_features = self.movie_features[movie.tmdb_id]
                            movie_features = self.movie_scaler.transform([movie_features])[0]
                            movie_features_batch.append(movie_features)
                        
                        # 转换为numpy数组
                        movie_indices = np.array(movie_indices)
                        movie_features_batch = np.array(movie_features_batch)
                        
                        # 准备批量输入
                        user_indices = np.full_like(movie_indices, user_idx)
                        user_features_batch = np.tile(user_features, (len(batch_movies), 1))
                        
                        # 模型预测
                        predictions = self.model.predict([
                            user_indices,
                            movie_indices,
                            user_features_batch,
                            movie_features_batch
                        ], verbose=0)
                        
                        # 结合其他特征计算最终分数
                        for movie, pred_score in zip(batch_movies, predictions):
                            try:
                                # 基础分数（模型预测）
                                base_score = float(pred_score[0])
                                
                                # 时效性权重
                                recency_score = 0
                                if movie.release_date:
                                    days_old = (timezone.now().date() - movie.release_date).days
                                    if days_old <= 90:  # 三个月内的新片
                                        recency_score = 1.2
                                    elif days_old <= 180:  # 六个月内
                                        recency_score = 1.1
                                    else:
                                        recency_score = 1.0
                                
                                # 热度权重
                                popularity_score = 1.0
                                if movie.vote_count:
                                    if movie.vote_count > 1000:
                                        popularity_score = 1.2
                                    elif movie.vote_count > 500:
                                        popularity_score = 1.1
                                
                                # 综合评分 - 增加模型预测权重
                                final_score = (
                                    base_score * 0.9 +     # 模型预测分数（提高权重）
                                    recency_score * 0.05 + # 时效性
                                    popularity_score * 0.05 # 热度
                                )
                                
                                movie_scores.append((movie.tmdb_id, final_score))
                            except Exception as e:
                                logger.warning(f"计算电影 {movie.tmdb_id} 的推荐分数时出错: {str(e)}")
                                continue
                    
                    # 排序并返回推荐结果
                    movie_scores.sort(key=lambda x: x[1], reverse=True)
                    recommended_ids = [mid for mid, _ in movie_scores[:top_n]]
                    
                    logger.info(f"成功为用户 {user_id} 生成 {len(recommended_ids)} 个推荐")
                    return recommended_ids
                
                else:
                    logger.warning("模型未加载，使用规则基础推荐")
                    raise Exception("Model not available")
                    
            except Exception as e:
                logger.error(f"深度学习推荐失败，切换到规则推荐: {str(e)}")
                # 使用规则基础推荐作为备选
                return self._rule_based_recommend(user_id, candidate_movies, top_n)
            
        except Exception as e:
            logger.error(f"推荐生成失败: {str(e)}")
            return self._get_popular_movies(top_n)

    def _rule_based_recommend(self, user_id, candidate_movies, top_n):
        """规则基础推荐（作为备选策略）"""
        try:
            # 获取用户的类型偏好
            genre_preferences = self._get_user_genre_preferences(user_id)
            
            # 计算推荐分数
            movie_scores = []
            for movie in candidate_movies:
                try:
                    # 基础分数
                    base_score = movie.vote_average if movie.vote_average else 0
                    
                    # 计算类型匹配度
                    genre_score = 0
                    if movie.genres:
                        matching_genres = set(movie.genres) & set(genre_preferences)
                        if matching_genres:
                            genre_score = sum(genre_preferences[genre] for genre in matching_genres) / len(matching_genres)
                    
                    # 时效性权重
                    recency_score = 0
                    if movie.release_date:
                        days_old = (timezone.now().date() - movie.release_date).days
                        if days_old <= 90:
                            recency_score = 1.2
                        elif days_old <= 180:
                            recency_score = 1.1
                        else:
                            recency_score = 1.0
                    
                    # 热度权重
                    popularity_score = 1.0
                    if movie.vote_count:
                        if movie.vote_count > 1000:
                            popularity_score = 1.2
                        elif movie.vote_count > 500:
                            popularity_score = 1.1
                    
                    # 综合评分
                    final_score = (
                        base_score * 0.3 +
                        genre_score * 0.3 +
                        recency_score * 0.2 +
                        popularity_score * 0.2
                    )
                    
                    movie_scores.append((movie.tmdb_id, final_score))
                except Exception as e:
                    logger.warning(f"计算电影 {movie.tmdb_id} 的规则推荐分数时出错: {str(e)}")
                    continue
            
            # 排序并返回推荐结果
            movie_scores.sort(key=lambda x: x[1], reverse=True)
            return [mid for mid, _ in movie_scores[:top_n]]
            
        except Exception as e:
            logger.error(f"规则推荐失败: {str(e)}")
            return self._get_popular_movies(top_n)

    def _get_popular_movies(self, top_n):
        """获取热门电影"""
        try:
            return list(
                Movie.objects.filter(
                    poster_path__isnull=False
                ).exclude(
                    poster_path=''
                ).order_by(
                    '-vote_average',
                    '-vote_count'
                )[:top_n].values_list('tmdb_id', flat=True)
            )
        except Exception as e:
            logger.error(f"获取热门电影失败: {str(e)}")
            return []

    def _diversify_recommendations(self, movie_ids, scores, top_n, n_clusters=5):
        # 生成特征矩阵
        features = np.array([self._get_genre_vector(self.movie_features[mid][2:7]) for mid in movie_ids])

        # 聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features)

        # 按分数排序
        sorted_indices = np.argsort(scores)[::-1]

        # 从每个簇中选择
        selected = set()
        cluster_counts = defaultdict(int)
        max_per_cluster = max(1, top_n // n_clusters)

        for idx in sorted_indices:
            if len(selected) >= top_n:
                break
            cluster = clusters[idx]
            if cluster_counts[cluster] < max_per_cluster:
                selected.add(idx)
                cluster_counts[cluster] += 1

        # 补足剩余名额
        if len(selected) < top_n:
            remaining = top_n - len(selected)
            for idx in sorted_indices:
                if idx not in selected:
                    selected.add(idx)
                    remaining -= 1
                    if remaining == 0:
                        break

        return [movie_ids[i] for i in sorted(selected, key=lambda i: -scores[i])]

    @transaction.atomic
    def train_model(self, epochs=10, batch_size=256):
        """训练推荐模型"""
        try:
            # 准备训练数据
            reviews = Review.objects.all().select_related('user', 'movie')
            
            # 收集所有用户和电影ID
            user_ids = list(self.user_features.keys())
            movie_ids = list(self.movie_features.keys())
            
            # 创建ID到索引的映射
            self.user_mapping = {uid: i for i, uid in enumerate(user_ids)}
            self.movie_mapping = {mid: i for i, mid in enumerate(movie_ids)}
            
            # 准备训练数据
            user_indices = []
            movie_indices = []
            ratings = []
            user_feats = []
            movie_feats = []
            
            for review in reviews:
                if review.user_id in self.user_mapping and review.movie.tmdb_id in self.movie_mapping:
                    user_idx = self.user_mapping[review.user_id]
                    movie_idx = self.movie_mapping[review.movie.tmdb_id]
                    
                    user_indices.append(user_idx)
                    movie_indices.append(movie_idx)
                    ratings.append(review.rating)
                    
                    user_feats.append(self.user_features[review.user_id])
                    movie_feats.append(self.movie_features[review.movie.tmdb_id])
            
            # 转换为numpy数组
            user_indices = np.array(user_indices)
            movie_indices = np.array(movie_indices)
            ratings = np.array(ratings)
            user_feats = np.array(user_feats, dtype=np.float32)
            movie_feats = np.array(movie_feats, dtype=np.float32)
            
            # 构建和训练模型
            self.model = self.build_model(
                num_users=len(user_ids),
                num_movies=len(movie_ids)
            )
            
            history = self.model.fit(
                [user_indices, movie_indices, user_feats, movie_feats],
                ratings,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,
                verbose=1
            )
            
            # 保存模型
            self.save_model()
            
            return history
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            raise

    def _create_new_mappings(self):
        """创建新的用户和电影ID映射关系"""
        logger.info("正在创建新的用户和电影映射...")

        # 创建用户映射 (user_id -> index)
        users = CustomUser.objects.all().order_by('id')
        self.user_mapping = {user.id: idx for idx, user in enumerate(users)}

        # 创建电影映射 (tmdb_id -> index)
        movies = Movie.objects.all().order_by('tmdb_id')
        self.movie_mapping = {movie.tmdb_id: idx for idx, movie in enumerate(movies)}

        logger.info(f"映射创建完成：{len(self.user_mapping)} 用户，{len(self.movie_mapping)} 电影")

    def build_fallback_model(self):
        """构建应急模型"""
        logger.warning("使用规则基础推荐作为应急方案")
        self.model = None  # 清除模型引用
        self._init_fallback_features()

    def _init_fallback_features(self):
        """初始化应急特征"""
        try:
            # 初始化基本特征
            for user in CustomUser.objects.all():
                self.user_features[user.id] = self.default_user_feature()
            
            for movie in Movie.objects.all():
                self.movie_features[movie.tmdb_id] = self.default_movie_feature()
            
            logger.info("应急特征初始化完成")
        except Exception as e:
            logger.error(f"应急特征初始化失败: {str(e)}")
            # 使用空特征
            self.user_features.clear()
            self.movie_features.clear()

    def save_model(self):
        """保存模型和相关数据"""
        try:
            # 确保保存目录存在
            model_dir = os.path.join(settings.BASE_DIR, 'models')
            mapping_dir = os.path.join(settings.BASE_DIR, 'data', 'mappings')
            os.makedirs(model_dir, exist_ok=True)
            os.makedirs(mapping_dir, exist_ok=True)
            
            # 保存Keras模型 - 使用.h5格式
            h5_path = os.path.abspath(os.path.join(model_dir, 'recommendation_model.h5'))
            
            # 先删除旧文件（如果存在）
            if os.path.exists(h5_path):
                os.remove(h5_path)
            
            # 保存为.h5格式
            self.model.save(h5_path)
            logger.info(f"模型保存到: {h5_path}")
            
            # 保存特征缩放器
            joblib.dump(self.user_scaler, os.path.join(model_dir, 'user_scaler.pkl'))
            joblib.dump(self.movie_scaler, os.path.join(model_dir, 'movie_scaler.pkl'))
            logger.info("特征缩放器保存成功")
            
            # 保存映射关系
            joblib.dump(self.user_mapping, os.path.join(mapping_dir, 'user_mapping.pkl'))
            joblib.dump(self.movie_mapping, os.path.join(mapping_dir, 'movie_mapping.pkl'))
            
            # 保存特征数据
            joblib.dump(self.user_features, os.path.join(mapping_dir, 'user_features.pkl'))
            joblib.dump(self.movie_features, os.path.join(mapping_dir, 'movie_features.pkl'))
            logger.info("映射关系和特征数据保存成功")
            
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            raise

    def load_model_and_data(self):
        """加载模型和相关数据"""
        try:
            model_dir = os.path.join(settings.BASE_DIR, 'models')
            mapping_dir = os.path.join(settings.BASE_DIR, 'data', 'mappings')
            
            # 加载模型 - 使用.h5格式
            h5_path = os.path.abspath(os.path.join(model_dir, 'recommendation_model.h5'))
            
            if os.path.exists(h5_path):
                self.model = tf.keras.models.load_model(h5_path)
                logger.info("模型加载成功 (.h5格式)")
            
            # 加载特征缩放器
            user_scaler_path = os.path.join(model_dir, 'user_scaler.pkl')
            movie_scaler_path = os.path.join(model_dir, 'movie_scaler.pkl')
            if os.path.exists(user_scaler_path) and os.path.exists(movie_scaler_path):
                self.user_scaler = joblib.load(user_scaler_path)
                self.movie_scaler = joblib.load(movie_scaler_path)
                logger.info("特征缩放器加载成功")
            
            # 加载映射关系
            user_mapping_path = os.path.join(mapping_dir, 'user_mapping.pkl')
            movie_mapping_path = os.path.join(mapping_dir, 'movie_mapping.pkl')
            if os.path.exists(user_mapping_path) and os.path.exists(movie_mapping_path):
                self.user_mapping = joblib.load(user_mapping_path)
                self.movie_mapping = joblib.load(movie_mapping_path)
                logger.info("映射关系加载成功")
            
            # 加载特征数据
            user_features_path = os.path.join(mapping_dir, 'user_features.pkl')
            movie_features_path = os.path.join(mapping_dir, 'movie_features.pkl')
            if os.path.exists(user_features_path) and os.path.exists(movie_features_path):
                self.user_features = joblib.load(user_features_path)
                self.movie_features = joblib.load(movie_features_path)
                logger.info("特征数据加载成功")
            
            return True
            
        except Exception as e:
            logger.error(f"加载模型和数据失败: {str(e)}")
            return False
