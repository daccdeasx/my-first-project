from datetime import timezone
from multiprocessing import Value

import psutil
from annotated_types.test_cases import Case
from click.core import F
from django.forms import FloatField
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from Movie_demo import settings
from movies.recommendations import logger
from movies.services import ReviewSerializer, MovieSerializer
from .serializers import AdminUserSerializer, HotPostSerializer, UserSearchSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404
from .serializers import UserSettingsSerializer
from .permissions import IsSuperAdmin
from .permissions import IsAdmin
from .permissions import IsMovieAdmin, IsForumAdmin, IsOrderAdmin
from django.db.models.functions import TruncDay, Coalesce, ExtractHour, Cast
from django.utils import timezone
from django.utils.timesince import timesince
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from datetime import timedelta
from movies.models import Movie, Review
from django.core.cache import cache
from django.core import serializers
from django.http import HttpResponse
from django.conf import settings
import os
import json
import logging
from datetime import datetime
from .models import PostImage, ReplyImage
from .permissions import IsPostAuthorOrReadOnly
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, ExpressionWrapper, FloatField, Q, Case, When
from .models import Post, Reply, Notification, PostLike, PostFavorite, CustomUser, PointLog
from .serializers import (
    PostSerializer, ReplySerializer, NotificationSerializer,
    UserSerializer, CustomAuthTokenSerializer, UserDetailSerializer,
    PostAdminSerializer, PointLogSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.contenttypes.models import ContentType
from django.db.models import Value as V  # 重命名为 V 避免冲突


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def check_auth(request):
    return Response({
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else ''
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_token(request):
    return Response({
        'valid': True,
        'expires_at': request.auth.created + timedelta(seconds=settings.REST_FRAMEWORK_TOKEN_EXPIRE_SECONDS)
    })


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        if 'avatar' in self.request.FILES:
            if self.request.user.avatar:
                self.request.user.avatar.delete(save=False)
            serializer.save(avatar=self.request.FILES['avatar'])
        else:
            serializer.save()


class UserReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        return {
            'request': self.request,
            'movie': self._get_movie()
        }

    def _get_movie(self):
        movie_id = self.request.query_params.get('movie_id')
        if movie_id:
            return get_object_or_404(Movie, tmdb_id=movie_id)
        return None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserSettingsView(RetrieveUpdateAPIView):
    serializer_class = UserSettingsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        if 'new_password' in self.request.data:
            if 'old_password' not in self.request.data:
                raise ValidationError({"old_password": "需要提供旧密码"})

        serializer.save()


class UserCollectionView(generics.ListAPIView):
    serializer_class = MovieSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movie.objects.filter(
            movie_favorites__user=self.request.user
        ).order_by('-movie_favorites__created_at')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"收藏列表获取失败: {str(e)}", exc_info=True)
            return Response(
                {"error": "服务器内部错误"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminUserPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def admin_user_list(request):
    paginator = AdminUserPagination()
    queryset = CustomUser.objects.all().order_by('-date_joined')
    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer = AdminUserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = AdminUserSerializer(page, many=True, context={'request': request})
    return Response(serializer.data)


# 切换用户状态
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])  # 超级管理员专用
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return Response({'status': 'success', 'is_active': user.is_active})


# 提取仪表盘数据获取逻辑到独立函数
def get_admin_dashboard_data():
    # 基础统计
    total_users = CustomUser.objects.count()
    total_movies = Movie.objects.count()
    today_reviews = Review.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    # 用户增长数据（最近 30 天）
    user_growth = CustomUser.objects.annotate(
        date=TruncDay('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:30]

    # 格式转换：将 count 重命名为 value（前端图表要求）
    formatted_user_growth = [
        {'date': entry['date'].strftime('%Y-%m-%d'), 'value': entry['count']}
        for entry in user_growth
    ]

    # 电影类型分布
    genre_distribution = Movie.objects.values('genres').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # 最近活动（从数据库获取真实数据）
    recent_activities = []

    # 相对时间计算函数
    def get_time_ago(created_at):
        return timesince(created_at, timezone.now()) + '前'

    # 1. 最近注册用户（取最近 7 天，按注册时间倒序）
    recent_users = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).order_by('-date_joined')[:5]

    for user in recent_users:
        recent_activities.append({
            'timestamp': user.date_joined.strftime('%Y-%m-%d %H:%M'),
            'type': 'user',
            'action': '注册',
            'user': user.username or user.email,  # 使用 username，若为空则使用 email
            'time_ago': get_time_ago(user.date_joined),
            'extra': ''
        })

    # 2. 最近发布的评论（取最近 7 天，关联电影和用户）
    recent_reviews = Review.objects.select_related('user', 'movie').filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:5]

    for review in recent_reviews:
        recent_activities.append({
            'timestamp': review.created_at.strftime('%Y-%m-%d %H:%M'),
            'type': 'review',
            'action': '发布评论',
            'user': review.user.username or review.user.email,  # 使用 username，若为空则使用 email
            'movie': review.movie.title,
            'review_id': review.id,
            'time_ago': get_time_ago(review.created_at)
        })

    # 按时间倒序排列所有活动
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)

    # 获取系统状态数据
    cpu_percent = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().used / (1024.0 ** 3)
    disk_usage = psutil.disk_usage('/').used / (1024.0 ** 3)

    return {
        'total_users': total_users,
        'total_movies': total_movies,
        'today_reviews': today_reviews,
        'user_growth': formatted_user_growth,
        'genre_distribution': [
            {'name': entry['genres'], 'value': entry['count']}
            for entry in genre_distribution
        ],
        'recent_activities': recent_activities,
        'health': {
            'cpu': cpu_percent,
            'memory': memory_usage,
            'disk': disk_usage
        }
    }


# 修改 admin_dashboard 视图
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    dashboard_data = get_admin_dashboard_data()
    return Response(dashboard_data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user == request.user:
        return Response({'error': '不能删除当前登录用户'}, status=400)
    user.delete()
    return Response(status=204)


# 修改 data_analytics 视图
@api_view(['GET'])
@permission_classes([IsAdminUser])
def data_analytics(request):
    """数据分析核心接口"""
    # 用户行为分析
    active_users = CustomUser.objects.annotate(
        review_count=Count('reviews'),
        favorite_count=Count('user_favorites')
    ).order_by('-login_count', '-review_count')[:10]

    # 电影评分分布
    rating_distribution = Review.objects.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')

    # 系统性能数据（示例）
    performance_data = {
        'response_time': {'min': 120, 'avg': 250, 'max': 800},
        'server_load': {'cpu': 35, 'memory': 60},
        'database': {'queries': 420, 'connections': 15}
    }

    # 获取基础统计数据
    total_users = CustomUser.objects.count()

    # 获取仪表盘数据
    dashboard_data = get_admin_dashboard_data()

    # 构建响应数据
    response_data = {
        # 基础统计
        'total_users': total_users,
        'active_users': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'login_count': u.login_count,
                'review_count': u.review_count,
                'favorite_count': u.favorite_count,
                'last_login': u.last_login.strftime('%Y-%m-%d %H:%M:%S') if u.last_login else None,
                'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M:%S') if u.date_joined else None
            } for u in active_users
        ],
        # 电影相关
        'rating_distribution': [
            {'rating': r['rating'], 'count': r['count']}
            for r in rating_distribution
        ],
        # 系统性能
        'performance': performance_data,
        # 合并管理员仪表盘数据
        **dashboard_data
    }

    return Response(response_data)


@api_view(['GET', 'PUT'])
@permission_classes([IsSuperAdmin])
def system_config(request):
    config_path = os.path.join(settings.BASE_DIR, 'config.json')
    version_dir = os.path.join(settings.BASE_DIR, 'config_versions')
    if not os.path.exists(version_dir):
        os.makedirs(version_dir, exist_ok=True)

    try:
        if request.method == 'GET':
            if not os.path.exists(config_path):
                default_config = {"site_title": "默认网站标题", "cache_duration": 60, "auto_backup": "off"}
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return Response(default_config)

            with open(config_path, 'r') as f:
                config = json.load(f)
                return Response(config)

        elif request.method == 'PUT':
            # 保存旧配置为版本
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    old_config = json.load(f)
                version_file = os.path.join(version_dir, f"config_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
                with open(version_file, 'w') as f:
                    json.dump(old_config, f, indent=2)
            with open(config_path, 'w') as f:
                json.dump(request.data, f, indent=2)
                return Response({'status': '配置更新成功'})

    except FileNotFoundError:
        default_config = {"site_title": "默认网站标题", "cache_duration": 60, "auto_backup": "off"}
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        return Response(default_config)

    except json.JSONDecodeError as e:
        return Response({'error': '配置文件格式错误'}, status=500)

    except Exception as e:
        return Response({'error': f'服务器错误: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def get_config_versions(request):
    version_dir = os.path.join(settings.BASE_DIR, 'config_versions')
    if not os.path.exists(version_dir):
        return Response([])

    versions = []
    for file in os.listdir(version_dir):
        if file.startswith('config_') and file.endswith('.json'):
            version_time = file.split('_')[1].split('.')[0]
            version_time = datetime.strptime(version_time, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
            versions.append({'id': file, 'time': version_time})

    return Response(versions)


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def get_config_by_version(request, version_file):
    version_dir = os.path.join(settings.BASE_DIR, 'config_versions')
    version_path = os.path.join(version_dir, version_file)
    if not os.path.exists(version_path):
        return Response({'error': '配置版本不存在'}, status=404)
    try:
        with open(version_path, 'r') as f:
            config = json.load(f)
        return Response(config)
    except json.JSONDecodeError as e:
        return Response({'error': '配置版本文件格式错误'}, status=500)
    except Exception as e:
        return Response({'error': f'服务器错误: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def system_backup(request):
    """创建系统备份"""
    try:
        # 示例：数据库备份
        backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = f'backup_{backup_time}.json'

        data = serializers.serialize("json", Movie.objects.all())
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{backup_file}"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def system_logs(request):
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    log_file = os.path.join(log_dir, 'system.log')

    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))

    try:
        if not os.path.exists(log_file):
            logger.warning(f"系统日志文件 {log_file} 不存在")
            return Response({'logs': [], 'page': page, 'page_size': page_size, 'total': 0})

        with open(log_file, 'r') as f:
            logs = f.readlines()
            if not logs:
                logger.warning(f"系统日志文件 {log_file} 为空")
                return Response({'logs': [], 'page': page, 'page_size': page_size, 'total': 0})

            total = len(logs)
            start = (page - 1) * page_size
            end = start + page_size
            return Response({
                'logs': logs[start:end],
                'page': page,
                'page_size': page_size,
                'total': total
            })

    except Exception as e:
        logger.error(f'读取日志失败: {str(e)}')
        return Response({'error': f'读取日志失败: {str(e)}'}, status=500)


@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def clear_system_logs(request):
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    log_file = os.path.join(log_dir, 'system.log')

    try:
        if os.path.exists(log_file):
            os.remove(log_file)
            return Response({'status': '系统日志已清除'})
        else:
            return Response({'status': '系统日志文件不存在'})
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"清除系统日志失败: {str(e)}")
        return Response({'error': '清除系统日志失败'}, status=500)


@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def system_clear_cache(request):
    cache.clear()
    return Response({'status': '缓存已清除'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_health(request):
    cpu_percent = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().used / (1024.0 ** 3)
    disk_usage = psutil.disk_usage('/').used / (1024.0 ** 3)
    health_data = {
        'cpu': cpu_percent,
        'memory': memory_usage,
        'disk': disk_usage
    }
    return Response(health_data)


# ==============================
# 论坛帖子相关视图（整合后）
# ==============================

class PostListCreateView(generics.ListCreateAPIView):
    """
    帖子列表（支持主题筛选）和创建视图
    - 认证用户可创建帖子（支持多图上传）
    - 公开接口返回已发布的帖子列表
    """
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]  # 支持 multipart/form-data 格式（文件上传）
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 仅认证用户可创建帖子

    def get_queryset(self):
        """
        获取已发布的帖子列表（支持主题筛选）
        """
        # 基础查询：过滤已发布状态，并按创建时间倒序
        queryset = Post.objects.filter(status='approved').order_by('-created_at')

        # 主题筛选（可选参数）
        theme = self.request.query_params.get('theme')
        if theme:
            # 校验主题是否存在
            valid_themes = [choice[0] for choice in Post.THEME_CHOICES]
            if theme in valid_themes:
                queryset = queryset.filter(theme=theme)

        # 排序方式（可选参数）
        sort = self.request.query_params.get('sort')
        if sort == 'hot':
            queryset = queryset.annotate(
                hot_score=ExpressionWrapper(F('like_count') * 2 + F('reply_count') + F('view_count') * 0.5,
                                            output_field=FloatField())
            ).order_by('-hot_score')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'old':
            queryset = queryset.order_by('created_at')

        return queryset

    def perform_create(self, serializer):
        """
        创建帖子时自动关联用户，并处理图片上传
        """
        # 关联当前用户
        post = serializer.save(user=self.request.user)

        # 处理多图片上传
        uploaded_images = self.request.FILES.getlist('images')
        if uploaded_images:
            post_images = [PostImage(post=post, image=img) for img in uploaded_images]
            PostImage.objects.bulk_create(post_images)  # 批量创建提升性能


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """普通用户：查看/更新/删除自己的帖子（管理员可操作所有帖子）"""
    queryset = Post.objects.all().prefetch_related('replies__children')  # 优化查询
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          permissions.IsAdminUser | IsPostAuthorOrReadOnly]  # 作者或管理员可编辑

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加浏览量
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()


class ReplyCreateView(generics.CreateAPIView):
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        parent_id = self.request.data.get('parent_id')
        parent = None

        if parent_id:
            # 验证父评论是否存在且属于当前帖子
            parent = get_object_or_404(Reply, id=parent_id, post=post)

        # 保存回复时关联帖子和父评论
        reply = serializer.save(user=self.request.user, post=post, parent=parent)

        # 处理图片上传
        images = self.request.FILES.getlist('images')
        for image in images:
            ReplyImage.objects.create(reply=reply, image=image)

        # 更新帖子回复数
        post.reply_count = post.replies.count()
        post.save()

        return Response(
            ReplySerializer(reply, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED
        )


class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = PostLike.objects.get_or_create(
            user=request.user,
            post=post
        )
        if not created:
            like.delete()
            post.like_count -= 1
            message = '取消点赞成功'
        else:
            post.like_count += 1
            message = '点赞成功'

        post.save()
        return Response({
            'message': message,
            'liked': created,
            'like_count': post.like_count
        })


class PostFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id)
            favorite, created = PostFavorite.objects.get_or_create(
                user=request.user,
                post=post
            )
            
            if not created:
                favorite.delete()
                post.favorite_count = max(0, post.favorite_count - 1)  # 确保不会小于0
                message = '取消收藏成功'
                is_favorited = False
            else:
                post.favorite_count += 1
                message = '收藏成功'
                is_favorited = True
            
            post.save()
            return Response({
                'message': message,
                'favorited': is_favorited,
                'favorite_count': post.favorite_count
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=500)


class HotPostListView(generics.ListAPIView):
    serializer_class = HotPostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        try:
            # 获取已审核的帖子
            approved_posts = Post.objects.filter(status='approved')

            # 构建查询，计算热度得分
            queryset = approved_posts.annotate(
                total_likes=Coalesce(Count('likes'), V(0)),
                total_replies=Coalesce(Count('replies'), V(0)),
                calculated_score=ExpressionWrapper(
                    Coalesce(Count('likes'), V(0)) * 2.0 +
                    Coalesce(Count('replies'), V(0)) * 1.5 +
                    Coalesce('view_count', V(0)) * 0.5 +
                    Case(
                        When(is_pinned=True, then=V(100.0)),
                        default=V(0.0),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField()
                )
            ).order_by('-calculated_score', '-created_at')[:10]

            return queryset

        except Exception as e:
            return Post.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "获取热门帖子失败"}, status=500)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # 新增这行

    def get_queryset(self):
        # 确保返回当前用户的通知列表
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationAsReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 只有通知的接收者可以标记为已读
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        instance.is_read = True
        instance.save()
        return Response(self.get_serializer(instance).data)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username,
            'is_admin': user.is_admin
        })


class UserPointLogView(generics.ListAPIView):
    serializer_class = PointLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PointLog.objects.filter(user=self.request.user).order_by('-created_at')


class UserPostCollectionView(generics.ListAPIView):
    """用户收藏的帖子列表视图"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer  # 使用帖子序列化器

    def get_queryset(self):
        # 通过 PostFavorite 模型关联用户和帖子
        return Post.objects.filter(
            favorites__user=self.request.user
        ).order_by('-favorites__created_at')  # 按收藏时间倒序


class UserSearchView(generics.ListAPIView):
    """用户搜索接口（支持用户名/邮箱模糊查询）"""
    serializer_class = UserSearchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 按需设置权限
    pagination_class = None

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', '').strip()
        if len(keyword) < 2:
            return CustomUser.objects.none()  # 至少输入2个字符才搜索

        # 同时搜索用户名和邮箱（不区分大小写）
        return CustomUser.objects.filter(
            Q(username__icontains=keyword) | Q(email__icontains=keyword)
        ).order_by('username')[:10]  # 最多返回10条结果


# 新增视图
class UserPostListView(generics.ListAPIView):
    """用户创建的帖子列表"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-created_at')


# ==============================
# 管理员审核相关视图
# ==============================

class TogglePostPinView(generics.UpdateAPIView):
    """切换帖子置顶状态"""
    queryset = Post.objects.all()
    serializer_class = PostAdminSerializer
    permission_classes = [IsForumAdmin]

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.is_pinned = not post.is_pinned
        post.save()
        return Response({'status': '置顶状态已更新', 'post_id': post.id, 'is_pinned': post.is_pinned})


class AdminPostListView(generics.ListAPIView):
    """管理员帖子列表（带分页和状态筛选）"""
    serializer_class = PostAdminSerializer
    permission_classes = [IsForumAdmin]
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-is_pinned', '-created_at')
        status = self.request.query_params.get('status')

        # 筛选逻辑（修复版）
        if status in ['pending', 'approved', 'rejected']:
            queryset = queryset.filter(status=status)

        return queryset


class ApprovePostView(generics.UpdateAPIView):
    """审核通过帖子"""
    queryset = Post.objects.all()
    serializer_class = PostAdminSerializer
    permission_classes = [IsForumAdmin]

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.status = 'approved'
        post.save()
        return Response({'status': '审核通过', 'post_id': post.id})


class RejectPostView(generics.UpdateAPIView):
    """审核拒绝帖子"""
    queryset = Post.objects.all()
    serializer_class = PostAdminSerializer
    permission_classes = [IsForumAdmin]

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post.status = 'rejected'
        post.rejection_reason = request.data.get('reason', '未提供理由')
        post.save()
        return Response({'status': '已拒绝', 'post_id': post.id, 'reason': post.rejection_reason})


class AllPostListView(generics.ListAPIView):
    """管理员全部帖子接口 /users/admin/posts/all/"""
    serializer_class = PostAdminSerializer
    permission_classes = [IsForumAdmin]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            # 基础查询
            queryset = Post.objects.all().select_related("user").order_by("-created_at")

            # ✅ 筛选状态（修复这里）
            status = self.request.query_params.get('status')
            if status in ['pending', 'approved', 'rejected']:
                queryset = queryset.filter(status=status)

            return queryset
        except Exception as e:
            logger.error(f"AllPostListView 查询异常: {e}", exc_info=True)
            return Post.objects.none()


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def update_user_role(request, user_id):
    """
    超级管理员修改用户角色：
    - admin_role: user|movie_admin|forum_admin|order_admin
    同时自动同步 is_staff：
    - admin_role != user -> is_staff=True
    - admin_role == user -> is_staff=False（不影响 is_superuser）
    """
    user = get_object_or_404(CustomUser, id=user_id)
    role = request.data.get('admin_role')
    valid_roles = {c[0] for c in CustomUser.ADMIN_ROLE_CHOICES}
    if role not in valid_roles:
        return Response({"error": "无效的admin_role"}, status=400)

    user.admin_role = role
    if not user.is_superuser:
        user.is_staff = role != 'user'
        user.is_admin = role != 'user'
    user.save()
    return Response({"status": "success", "admin_role": user.admin_role, "is_staff": user.is_staff})

    def get_queryset(self):
        status = self.request.query_params.get('status')

        # 定义有效状态列表
        valid_statuses = ['pending', 'approved', 'rejected']

        # 处理无效状态参数
        if status not in valid_statuses:
            return Post.objects.all().order_by('-created_at')

        # 按状态筛选
        return Post.objects.filter(status=status).order_by('-created_at')


class PostAdminListView(generics.ListAPIView):
    serializer_class = PostAdminSerializer
    permission_classes = [IsAdminUser]
    queryset = Post.objects.all().order_by('-is_pinned', '-created_at')

    # ✅ 正确：在视图中设置分页器
    pagination_class = PageNumberPagination  # 与 settings.py 中的配置一致
    page_size = 10  # 可省略，使用 settings.py 中的 PAGE_SIZE


# ==============================
# 图片相关视图
# ==============================

class PostImageUploadView(generics.CreateAPIView):
    """上传帖子图片（单独接口，可按需使用）"""
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        image = self.request.FILES['image']
        PostImage.objects.create(post=post, image=image)
        return Response({'status': '图片上传成功'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_yearly_report(request):
    """获取用户年度报告数据"""
    user = request.user
    current_year = timezone.now().year
    
    try:
        # 获取用户观影数据
        watched_movies = Movie.objects.filter(
            movie_favorites__user=user,
            movie_favorites__created_at__year=current_year
        ).count()
        
        # 获取用户评论数据
        reviews = Review.objects.filter(
            user=user,
            created_at__year=current_year
        ).count()
        
        # 获取用户发帖数据
        posts = Post.objects.filter(
            user=user,  # 修改 author 为 user
            created_at__year=current_year
        ).count()
        
        # 获取用户获得的点赞数
        likes_received = PostLike.objects.filter(
            post__user=user,  # 修改 post__author 为 post__user
            created_at__year=current_year
        ).count()
        
        # 获取用户最常访问的时间段
        from django.db.models.functions import ExtractHour
        favorite_hours = Post.objects.filter(
            user=user,  # 修改 author 为 user
            created_at__year=current_year
        ).annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        # 获取用户最活跃的月份
        from django.db.models.functions import ExtractMonth
        active_months = Post.objects.filter(
            user=user,  # 修改 author 为 user
            created_at__year=current_year
        ).annotate(
            month=ExtractMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        return Response({
            'year': current_year,
            'watched_movies': watched_movies,
            'reviews': reviews,
            'posts': posts,
            'likes_received': likes_received,
            'favorite_hours': list(favorite_hours),
            'active_months': list(active_months),
            'total_points': user.points,
            'join_days': (timezone.now() - user.date_joined).days
        })
    except Exception as e:
        logger.error(f"获取年度报告失败: {str(e)}", exc_info=True)
        return Response(
            {"error": "获取年度报告失败，请稍后重试"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )