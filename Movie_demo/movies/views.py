# movies/models
from MySQLdb import IntegrityError
from django.core.cache import cache
from django.db import IntegrityError as DjangoIntegrityError
from django.db import transaction
from django.db.models import Avg, Count
import tmdbsimple as tmdb
from django.conf import settings
import logging
import hashlib
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from . import services
from .ai_chat import AIChatRecommender
from .models import UserFavorite, Review, Movie, Cinema, MovieSchedule, Order, ReviewLike
from datetime import timedelta, time, datetime
from django.utils import timezone

from .recommendations import RecommendationService
from .serializers import MovieAdminSerializer, AdminReviewSerializer, CinemaSerializer, MovieScheduleSerializer, \
    OrderSerializer
from .services import ReviewSerializer
from circuitbreaker import circuit

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from users.permissions import IsMovieAdmin, IsSuperAdmin
from rest_framework import status
from django.db.models import Q
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseBadRequest
import csv

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
import uuid
import requests

logger = logging.getLogger(__name__)


class MovieService:
    @staticmethod
    def validate_api_key():
        if not getattr(settings, 'TMDB_API_KEY', None):
            raise ValueError("TMDB API密钥未配置")

    @staticmethod
    def generate_cache_key(endpoint, params):
        param_str = str(sorted(params.items())).encode('utf-8')
        return f"tmdb_{endpoint}_{hashlib.md5(param_str).hexdigest()}"

    @staticmethod
    def get_batch_info(titles):
        """批量获取电影信息"""
        from .models import Movie
        return [
            Movie.objects.filter(title__icontains=title).first()
            for title in titles
            if title
        ]


@api_view(['GET'])
def tmdb_proxy(request):
    """通用TMDB代理接口"""
    try:
        # 基础验证
        MovieService.validate_api_key()
        tmdb.API_KEY = settings.TMDB_API_KEY

        # 缓存时间配置
        endpoint_config = {
            'now_playing': {
                'cache_time': 3600 * 6  # 6小时缓存
            },
            'top_rated': {
                'cache_time': 3600 * 24  # 24小时缓存
            },
            'popular': {
                'cache_time': 3600 * 6  # 6小时缓存
            },
            'featured': {
                'cache_time': 3600 * 6  # 6小时缓存
            },
            'discover': {
                'cache_time': 3600 * 24 * 7  # 一周缓存
            },
            'search': {
                'cache_time': 600  # 搜索缓存10分钟
            },
            'genre': {
                'cache_time': 3600 * 24 * 7  # 一周缓存
            }
        }

        # 获取请求类型
        endpoint_type = request.GET.get('type', 'now_playing')
        valid_endpoints = {
            'now_playing': tmdb.Movies().now_playing,
            'top_rated': tmdb.Movies().top_rated,
            'popular': tmdb.Movies().popular,
            'featured': tmdb.Movies().upcoming,
            'discover': tmdb.Discover().movie,
            'search': tmdb.Search().movie,
            'genre': tmdb.Genres().movie_list
        }

        if endpoint_type not in valid_endpoints:
            return Response({"error": "无效的请求类型"}, status=400)

        # 参数基础处理
        base_params = {
            'language': request.GET.get('language', 'zh-CN'),
            'page': int(request.GET.get('page', 1)),
            'region': request.GET.get('region', '').upper()
        }

        # 端点特定参数处理
        if endpoint_type == 'search':
            params = {
                'query': request.GET.get('query'),
                'page': base_params['page'],
                'language': base_params['language']
            }
        elif endpoint_type == 'discover':
            params = {
                **base_params,
                'with_genres': request.GET.get('with_genres'),
                'primary_release_year': request.GET.get('primary_release_year'),
                'sort_by': request.GET.get('sort_by', 'popularity.desc'),
                # 新增参数支持
                'vote_count.gte': request.GET.get('vote_count.gte'),
                'primary_release_date.gte': request.GET.get('primary_release_date.gte'),
                'primary_release_date.lte': request.GET.get('primary_release_date.lte')
            }
        else:
            params = base_params

        # 参数清理
        params = {k: v for k, v in params.items() if v not in [None, '']}

        # 参数验证
        if 'page' in params:
            try:
                params['page'] = int(params['page'])
                if params['page'] < 1:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({"error": "无效的分页参数"}, status=400)

        # 生成缓存键（包含端点类型）
        cache_key = f"tmdb_{endpoint_type}_{hash(frozenset(params.items()))}"
        if cached_data := cache.get(cache_key):
            logger.info(f"缓存命中：{cache_key}")
            return Response(cached_data)

        # 动态调用API
        api_method = valid_endpoints[endpoint_type]

        if endpoint_type == 'genre':
            result = api_method()
            response_data = {'genres': result.get('genres', [])}
        else:
            result = api_method(**params)
            response_data = {
                'results': result.get('results', []),
                'page': result.get('page', 1),
                'total_pages': min(result.get('total_pages', 1), 500)
            }

        logger.debug(f"API调用参数：{params} 响应状态：{result.get('status_code', 200)}")

        # 写入缓存（不同类型设置不同缓存时间）
        cache_time = endpoint_config[endpoint_type]['cache_time']
        cache.set(cache_key, response_data, cache_time)

        return Response(response_data)

    except ValueError as e:
        logger.warning(f"参数验证失败：{str(e)}")
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        # TMDB 接口不可用时，回退到本地 Movie 表，保证首页可用
        logger.error(f"TMDB API 或外部服务错误：{str(e)}，使用本地电影数据回退", exc_info=True)

        # 简单的本地数据回退逻辑：根据不同 type 做排序，返回前 N 条
        queryset = Movie.objects.all()
        endpoint_type = request.GET.get('type', 'now_playing')

        if endpoint_type == 'top_rated':
            queryset = queryset.order_by('-vote_average', '-vote_count')
        elif endpoint_type == 'popular':
            queryset = queryset.order_by('-vote_count', '-vote_average')
        else:
            # now_playing / featured 等，按更新时间或上映日期倒序
            queryset = queryset.order_by('-release_date', '-updated_at')

        # 简单分页
        page = int(request.GET.get('page', 1))
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size
        total = queryset.count()

        movies = queryset[start:end]
        results = [
            {
                "id": m.tmdb_id,
                "tmdb_id": m.tmdb_id,
                "title": m.title,
                "overview": m.overview,
                "poster_path": m.poster_path,
                "release_date": m.release_date.isoformat() if m.release_date else None,
                "vote_average": m.vote_average,
            }
            for m in movies
        ]

        fallback_response = {
            "results": results,
            "page": page,
            "total_pages": (total + page_size - 1) // page_size if total else 1,
        }

        return Response(fallback_response, status=200)


# 收藏功能
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, movie_id):
    user = request.user
    movie = get_object_or_404(Movie, tmdb_id=movie_id)

    favorite, created = UserFavorite.objects.get_or_create(
        user=user,
        movie=movie
    )

    if not created:
        favorite.delete()
        return Response({'status': 'removed', 'is_favorite': False})

    return Response({'status': 'added', 'is_favorite': True})


class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


def update_movie_rating_cache(movie):
    """更新电影评分缓存"""
    cache_key = f"movie_{movie.tmdb_id}_ratings"

    # 计算最新评分
    avg_rating = Review.objects.filter(movie=movie).aggregate(
        Avg('rating')
    )['rating__avg'] or 0.0

    # 设置缓存（1小时有效期）
    cache.set(cache_key, round(avg_rating, 1), 3600)
    return avg_rating


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def movie_reviews(request, movie_id, review_id=None):
    # 获取电影对象
    try:
        movie = get_or_create_movie(movie_id)
    except Movie.DoesNotExist:
        return Response({"error": "电影不存在"}, status=404)
    except Exception as e:
        logger.error(f"获取电影失败: {str(e)}")
        return Response({"error": "电影数据不可用"}, status=503)

    # 处理DELETE请求
    if request.method == 'DELETE':
        if not review_id:
            return Response({"error": "缺少评论ID"}, status=400)
        review = get_object_or_404(Review, id=review_id, movie=movie)
        review.delete()
        return Response(status=204)

    # 处理PUT请求
    if request.method == 'PUT':
        if not review_id:
            return Response({"error": "缺少评论ID"}, status=400)
        review = get_object_or_404(Review, id=review_id, movie=movie)
        serializer = ReviewSerializer(
            review,
            data=request.data,
            context={
                'request': request,
                'movie': movie
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 处理 POST 请求
    if request.method == 'POST':
        try:
            with transaction.atomic():
                serializer = ReviewSerializer(
                    data=request.data,
                    context={
                        'request': request,
                        'movie': movie
                    }
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

                # 更新评分缓存
                update_movie_rating_cache(movie)

                return Response(serializer.data, status=201)

        except IntegrityError:
            logger.warning(f"重复评论提交: {request.user.id} -> {movie_id}")
            return Response({"error": "请勿重复提交评论"}, status=409)
        except services.ValidationError as e:
            return Response(e.detail, status=400)

    # 处理 GET 请求
    reviews = Review.objects.filter(
        movie__tmdb_id=movie_id
    ).select_related('user').annotate(
        like_count=Count('review_likes')
    ).order_by('-like_count', '-created_at')

    # 标记精品评论（点赞数超过5的评论）
    for review in reviews:
        review.is_featured = review.like_count >= 5
        # 检查当前用户是否点赞
        if request.user.is_authenticated:
            review.is_liked = ReviewLike.objects.filter(
                user=request.user,
                review=review
            ).exists()
        else:
            review.is_liked = False

    paginator = ReviewPagination()
    result_page = paginator.paginate_queryset(reviews, request)
    serializer = ReviewSerializer(
        result_page,
        many=True,
        context={'request': request}
    )
    return paginator.get_paginated_response(serializer.data)


def needs_update(movie):
    """判断电影是否需要更新"""
    # 新创建未同步的临时记录
    if movie.title == '临时标题':
        return True

    # 超过7天未更新
    update_threshold = timezone.now() - timedelta(days=7)
    return movie.updated_at < update_threshold


# movies/views.py
def get_or_create_movie(tmdb_id):
    """实时同步电影数据"""
    max_retries = 3
    retry_delay = 1  # 秒

    for attempt in range(max_retries):
        try:
            # 检查TMDB ID有效性
            if not str(tmdb_id).isdigit():
                raise ValueError(f"无效的TMDB ID: {tmdb_id}")

            # 使用update_or_create避免重复
            movie, created = Movie.objects.update_or_create(
                tmdb_id=tmdb_id,
                defaults={'title': '临时标题'}
            )

            # 强制同步新数据
            if created or needs_update(movie):
                logger.info(f"开始同步TMDB数据 ID={tmdb_id}")
                return update_movie_from_tmdb(movie)

            return movie
        except Movie.DoesNotExist:
            try:
                # 立即同步创建
                return update_movie_from_tmdb(Movie(tmdb_id=tmdb_id))
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay * (attempt + 1))
        except Exception as e:
            logger.error(f"获取电影失败: {str(e)}")
            if attempt == max_retries - 1:
                logger.error(f"电影同步严重失败 ID={tmdb_id}: {str(e)}")
                return None  # 返回None而非抛出异常
            else:
                raise


def get_interaction_data(request, movie):
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = UserFavorite.objects.filter(
            user=request.user,
            movie=movie
        ).exists()

    reviews = Review.objects.filter(movie=movie)
    review_count = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    return {
        "is_favorite": is_favorite,
        "review_count": review_count,
        "average_rating": round(avg_rating, 1)
    }


def get_credits_data(movie):
    try:
        credits = tmdb.Movies(movie.tmdb_id).credits(language='zh-CN')
        return {
            "cast": credits.get("cast", [])[:10],
            "crew": [
                {"name": c["name"], "job": c["job"]}
                for c in credits.get("crew", [])
                if c["job"] in ["Director", "Screenplay"]
            ]
        }
    except tmdb.APIError as e:
        logger.error(f"TMDB 演职员信息请求失败: {str(e)}")
        return {"cast": [], "crew": []}


def get_similar_movies_data(movie):
    try:
        similar = tmdb.Movies(movie.tmdb_id).similar_movies(language='zh-CN')
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "poster_path": m.get("poster_path")
            }
            for m in similar.get("results", [])[:5]
        ]
    except tmdb.APIError as e:
        logger.error(f"TMDB 相似电影信息请求失败: {str(e)}")
        return []


@api_view(['GET'])
def movie_detail(request, movie_id):
    """获取电影详情"""
    try:
        movie = get_or_create_movie(movie_id)

        # 添加数据库存在性验证
        if not movie or not movie.title:
            raise Movie.DoesNotExist

        # 获取互动数据
        interaction_data = get_interaction_data(request, movie)

        # 获取演职员信息
        credits_data = get_credits_data(movie)

        # 获取相似电影信息
        similar_movies_data = get_similar_movies_data(movie)

        response_data = {
            "detail": {
                "id": movie.tmdb_id,
                "title": movie.title,
                "overview": movie.overview,
                "poster_path": movie.poster_path,
                "release_date": movie.release_date,
                "runtime": movie.runtime,
                "genres": movie.genres,
                "budget": movie.budget,
                "revenue": movie.revenue,
                "production_countries": movie.production_countries,
                "spoken_languages": movie.spoken_languages,
                "vote_average": movie.vote_average,
                "vote_count": movie.vote_count
            },
            "credits": credits_data,
            "similar": similar_movies_data,
            "interaction": interaction_data
        }

        return Response(response_data)
    except Movie.DoesNotExist:
        logger.error(f"电影不存在: {movie_id}")
        return Response({"error": "电影不存在"}, status=404)
    except tmdb.APIError as e:
        logger.error(f"TMDB API请求失败: {str(e)}")
        return Response({
            "error": "暂时无法获取电影数据",
            "code": "TMDB_UNAVAILABLE"
        }, status=503)
    except Exception as e:
        logger.error(f"获取电影详情失败: {str(e)}", exc_info=True)
        return Response({
            "error": "服务器内部错误",
            "code": "INTERNAL_ERROR"
        }, status=500)


# movies/views.py
def update_movie_from_tmdb(movie):
    """实时同步TMDB数据"""
    try:
        # 获取完整数据
        tmdb_movie = tmdb.Movies(movie.tmdb_id)
        details = tmdb_movie.info(language='zh-CN')

        # 数据校验
        if not details.get('title'):
            raise ValueError("无效的TMDB数据")

        # 更新字段
        movie.title = details['title']
        movie.overview = details.get('overview', '')
        movie.poster_path = details.get('poster_path', '')
        movie.release_date = details.get('release_date') or None
        movie.runtime = details.get('runtime', 0)
        movie.budget = details.get('budget', 0)
        movie.revenue = details.get('revenue', 0)
        movie.genres = [g['name'] for g in details.get('genres', [])]
        movie.production_countries = [c['name'] for c in details.get('production_countries', [])]
        movie.spoken_languages = [l['name'] for l in details.get('spoken_languages', [])]
        movie.vote_average = details.get('vote_average', 0.0)
        movie.vote_count = details.get('vote_count', 0)

        # 立即保存
        movie.save()
        return movie

    except Exception as e:
        logger.error(f"电影同步失败: {str(e)}")
        # 清理无效数据
        if movie.pk:
            movie.delete()
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_movie(request):
    tmdb_id = request.data.get('tmdb_id')
    if not tmdb_id:
        return Response({"error": "缺少tmdb_id参数"}, status=400)

    try:
        movie = get_or_create_movie(tmdb_id)
        return Response({"status": "synced", "movie_id": movie.id})
    except Exception as e:
        logger.error(f"电影同步失败: {str(e)}")
        return Response({"error": "无法同步电影数据"}, status=500)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def movie_interaction(request, movie_id):
    movie = get_object_or_404(Movie, tmdb_id=movie_id)

    # 计算全局平均评分
    avg_rating = Review.objects.filter(movie=movie).aggregate(
        Avg('rating')
    )['rating__avg'] or 0.0

    interaction_data = {
        "is_favorite": UserFavorite.objects.filter(
            user=request.user,
            movie=movie
        ).exists(),
        "user_rating": Review.objects.filter(
            user=request.user,
            movie=movie
        ).values('rating').first() or 0,
        "average_rating": round(avg_rating, 1)  # 确保返回数值类型
    }

    return Response(interaction_data)


class ReviewUpdateView(UpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        # 添加请求上下文
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class RecommendationView(APIView):
    def get(self, request):
        try:
            # 创建推荐服务实例
            service = RecommendationService()

            # 获取推荐电影ID列表 - 返回5个推荐
            recommended_ids = service.recommend_for_user(request.user.id, top_n=5)

            if not recommended_ids:
                logger.warning(f"用户 {request.user.id} 没有获取到推荐")
                return Response({
                    'status': 'success',
                    'count': 0,
                    'recommendations': []
                })

            # 获取电影详情
            movies = Movie.objects.filter(
                tmdb_id__in=recommended_ids
            ).values(
                'tmdb_id',
                'title',
                'poster_path',
                'vote_average'
            )

            # 保持推荐顺序
            movie_dict = {m['tmdb_id']: m for m in movies}
            sorted_movies = [
                movie_dict[mid] for mid in recommended_ids
                if mid in movie_dict
            ]

            return Response({
                'status': 'success',
                'count': len(sorted_movies),
                'recommendations': [
                    {
                        'tmdb_id': m['tmdb_id'],
                        'title': m['title'],
                        'poster_path': m['poster_path'],
                        'vote_average': float(m['vote_average']) if m['vote_average'] else 0.0
                    }
                    for m in sorted_movies
                ]
            })

        except Exception as e:
            logger.error(f"推荐服务失败: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': '推荐服务暂时不可用',
                'recommendations': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 新增视图 (movies/views.py)
from rest_framework.views import APIView
from .llm import LLMRecommendation


class LLMRecommendView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        movie_ids = request.data.get('movie_ids', [])
        try:
            reasons = LLMRecommendation.generate_recommend_reasons(
                request.user,
                movie_ids
            )
            return Response({'reasons': reasons})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class AIChatView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @circuit(failure_threshold=5, recovery_timeout=60)
    def post(self, request):
        try:
            # 参数验证
            if not request.data.get('message'):
                return Response({"error": "消息内容不能为空"}, status=400)

            message = request.data['message'].strip()
            if len(message) > 500:
                return Response({"error": "消息过长（最大500字符）"}, status=400)

            # 获取推荐结果
            recommender = AIChatRecommender()
            result = recommender.generate_recommendation(
                user=request.user,
                message=message,
                history=request.data.get('history', []),
                selected_movie_ids=[]
            )

            # 修改后的电影数据处理逻辑
            movie_details = []
            for title in result['recommended_movies']:
                try:
                    # 优先使用TMDB ID匹配
                    movie = Movie.objects.filter(
                        Q(title__icontains=title) |
                        Q(tmdb_id=title)
                    ).first()

                    # 本地不存在则搜索TMDB
                    if not movie:
                        search = tmdb.Search().movie(
                            query=title,
                            language='zh-CN',
                            include_adult=False
                        )
                        if search.get('results'):
                            # 取匹配度最高的结果
                            best_match = search['results'][0]
                            movie = get_or_create_movie(best_match['id'])

                    if movie:
                        movie_details.append({
                            "tmdb_id": movie.tmdb_id,  # 确保返回tmdb_id
                            "title": movie.title,
                            "poster_path": movie.poster_path,
                            "vote_average": movie.vote_average,
                            "release_date": movie.release_date,
                            "overview": (movie.overview[:100] + "...") if movie.overview else "暂无简介"
                        })
                except tmdb.base.APIKeyError:
                    logger.error("TMDB API密钥配置错误")
                    continue
                except Exception as e:
                    logger.warning(f"电影处理失败: {title} - {str(e)}")
                    continue

            return Response({
                'response': result['response'],
                'movies': movie_details[:3],  # 最多返回3部
                'updated_history': result['history']
            })

        except Exception as e:
            logger.error(f"AI对话失败: {str(e)}", exc_info=True)
            return Response({
                'error': '推荐服务暂时不可用',
                'code': 'AI_SERVICE_UNAVAILABLE'
            }, status=503)


class UserFavoriteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, tmdb_id):
        """添加收藏"""
        movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
        try:
            UserFavorite.objects.create(user=request.user, movie=movie)
            return Response(
                {"detail": "已添加到收藏", "is_favorite": True},
                status=status.HTTP_201_CREATED
            )
        except IntegrityError:
            return Response(
                {"error": "已存在收藏记录"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, tmdb_id):
        try:
            movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
            deleted_count, _ = UserFavorite.objects.filter(
                user=request.user,
                movie=movie
            ).delete()

            response_data = {
                "status": "success",
                "code": "FAVORITE_REMOVED",
                "detail": "已取消收藏",
                "data": {
                    "tmdb_id": tmdb_id,
                    "removed": bool(deleted_count)
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"取消收藏失败 | 用户:{request.user.id} | 电影:{tmdb_id} | 错误:{str(e)}")
            return Response(
                {
                    "status": "error",
                    "code": "SERVER_ERROR",
                    "detail": "服务暂时不可用"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, tmdb_id):
        """检查收藏状态"""
        movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
        exists = UserFavorite.objects.filter(
            user=request.user,
            movie=movie
        ).exists()
        return Response({"is_favorite": exists})


class MovieAdminPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    max_page_size = 100


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsMovieAdmin])
def admin_movie_management(request, tmdb_id=None):
    """电影管理核心API"""
    # 处理GET请求（列表查询和分页）
    if request.method == 'GET':
        # 查询集预处理
        queryset = Movie.objects.all().order_by('-updated_at')

        # 搜索过滤
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(overview__icontains=search)
            )

        # 分页处理
        paginator = MovieAdminPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = MovieAdminSerializer(
            page if page is not None else queryset,
            many=True,
            context={'request': request}
        )

        # 返回分页响应（包含count、next、previous等字段）
        if page is not None:
            return paginator.get_paginated_response(serializer.data)
        return Response(serializer.data)

    # 处理POST请求（创建电影）
    elif request.method == 'POST':
        serializer = MovieAdminSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except (DjangoIntegrityError, IntegrityError):
            logger.exception("管理员创建电影失败：数据约束冲突")
            return Response(
                {"detail": "创建失败：tmdb_id 可能已存在或字段不合法"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            logger.exception("管理员创建电影失败：未知错误")
            return Response(
                {"detail": "服务暂时不可用"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 处理单个电影的操作（PUT和DELETE需要tmdb_id）
    if tmdb_id is None:
        return Response({"error": "缺少tmdb_id参数"}, status=status.HTTP_400_BAD_REQUEST)

    # 获取电影对象
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    # 处理PUT请求（更新电影）
    if request.method == 'PUT':
        serializer = MovieAdminSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 处理DELETE请求（删除电影）
    elif request.method == 'DELETE':
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsMovieAdmin])
def admin_movie_export(request):
    """导出电影数据为CSV"""
    queryset = Movie.objects.all()
    response = StreamingHttpResponse(
        streaming_content=generate_csv_stream(queryset),
        content_type='text/csv'
    )
    response['Content-Disposition'] = 'attachment; filename="movies.csv"'
    return response


def generate_csv_stream(queryset):
    """生成CSV流"""
    fieldnames = [
        'tmdb_id', 'title', 'release_date', 'runtime',
        'vote_average', 'is_featured', 'genres', 'overview'
    ]
    writer = csv.DictWriter(None, fieldnames=fieldnames)
    yield writer.writerow(dict(zip(fieldnames, fieldnames)))  # 写入表头

    for movie in queryset:
        yield writer.writerow({
            'tmdb_id': movie.tmdb_id,
            'title': movie.title,
            'release_date': movie.release_date.strftime('%Y-%m-%d') if movie.release_date else '',
            'runtime': movie.runtime,
            'vote_average': movie.vote_average,
            'is_featured': movie.is_featured,
            'genres': ','.join(movie.genres) if movie.genres else '',
            'overview': movie.overview[:200]  # 截断过长内容
        })


# movies/views.py
class ReviewAdminPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    max_page_size = 100


@api_view(['GET', 'DELETE'])
@permission_classes([IsMovieAdmin])
def admin_review_management(request, review_id=None):
    """评论管理核心API"""
    # 查询集预处理（包含用户和电影信息）
    queryset = Review.objects.select_related('user', 'movie').order_by('-created_at')

    # GET 列表查询
    if request.method == 'GET':
        # 过滤条件
        search = request.GET.get('search')
        status_filter = request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(user__username__icontains=search) |
                Q(movie__title__icontains=search)
            )

        # 修改这里：使用 is_approved 而非 status
        if status_filter and status_filter.lower() in ['true', 'false']:
            is_approved = status_filter.lower() == 'true'
            queryset = queryset.filter(is_approved=is_approved)

        # 分页处理
        paginator = ReviewAdminPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = AdminReviewSerializer(
            page if page is not None else queryset,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    # DELETE 删除评论
    elif request.method == 'DELETE':
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsMovieAdmin])
def toggle_review_status(request, review_id):
    """切换评论审核状态"""
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = not review.is_approved
    review.save()
    return Response({'status': 'success', 'is_approved': review.is_approved})


@api_view(['POST'])  # 批量删除通常使用POST或DELETE，这里按URL设计使用POST
@permission_classes([IsMovieAdmin])
def batch_delete_reviews(request):
    """批量删除评论"""
    review_ids = request.data.get('review_ids', [])
    if not review_ids:
        return Response({"error": "缺少需要删除的评论ID列表"}, status=status.HTTP_400_BAD_REQUEST)

    # 批量删除评论
    deleted_count, _ = Review.objects.filter(id__in=review_ids).delete()
    return Response({
        "status": "success",
        "deleted_count": deleted_count
    }, status=status.HTTP_200_OK)


class CinemaViewSet(viewsets.ModelViewSet):
    queryset = Cinema.objects.all().order_by('id')
    serializer_class = CinemaSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        lat = float(request.query_params.get('lat', 0))
        lng = float(request.query_params.get('lng', 0))
        # 简单的距离计算,实际项目中可以使用更复杂的地理位置查询
        cinemas = Cinema.objects.all()
        return Response(CinemaSerializer(cinemas, many=True).data)


class MovieScheduleViewSet(viewsets.ModelViewSet):
    queryset = MovieSchedule.objects.all().order_by('start_time')
    serializer_class = MovieScheduleSerializer

    def get_queryset(self):
        queryset = MovieSchedule.objects.all().order_by('start_time')
        movie_id = self.request.query_params.get('movie', None)
        cinema_id = self.request.query_params.get('cinema', None)
        date = self.request.query_params.get('date', None)

        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        if cinema_id:
            queryset = queryset.filter(cinema_id=cinema_id)
        if date:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            queryset = queryset.filter(
                start_time__date=date_obj
            )
        return queryset.order_by('start_time')


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and (getattr(user, 'is_superuser', False) or getattr(user, 'admin_role', 'user') == 'order_admin'):
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        schedule_id = request.data.get('schedule')
        seats = request.data.get('seats', [])
        movie_id = request.data.get('movie_id')
        cinema_id = request.data.get('cinema_id')
        total_price = request.data.get('total_price')
        order_data = request.data.get('order_data', {})

        try:
            # 如果是模拟场次（schedule为None或模拟ID），创建特殊订单
            if not schedule_id or str(schedule_id).startswith(('mock_', 'fallback_')):
                # 获取订单数据中的真实信息
                order_data = request.data.get('order_data', {})

                # 创建包含真实信息的座位数据
                enhanced_seats = {
                    'seats': seats,
                    'cinema_name': order_data.get('cinema_name', '演示影院'),
                    'movie_title': order_data.get('movie_title', '演示电影'),
                    'show_time': order_data.get('show_time'),
                    'movie_poster': order_data.get('movie_poster'),
                    'movie_id': order_data.get('movie_id'),
                    'cinema_id': order_data.get('cinema_id')
                }

                # 创建模拟订单
                order = Order.objects.create(
                    user=request.user,
                    schedule=None,  # 模拟场次没有真实的schedule对象
                    seats=enhanced_seats,  # 存储增强的座位信息
                    total_price=total_price or 50,  # 默认价格
                    order_number=str(uuid.uuid4()).replace('-', ''),
                    status='paid'  # 模拟订单直接设为已支付
                )

                return Response(
                    OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED
                )

            # 真实场次订单处理
            schedule = MovieSchedule.objects.get(id=schedule_id)
            # 检查座位是否可用
            existing_orders = Order.objects.filter(
                schedule=schedule,
                status__in=['pending', 'paid']
            )
            occupied_seats = []
            for order in existing_orders:
                occupied_seats.extend(order.seats)

            for seat in seats:
                if seat in occupied_seats:
                    return Response(
                        {'error': f'座位 {seat} 已被占用'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 创建订单
            total_price = schedule.price * len(seats)
            order = Order.objects.create(
                user=request.user,
                schedule=schedule,
                seats=seats,
                total_price=total_price,
                order_number=str(uuid.uuid4()).replace('-', '')
            )

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )

        except MovieSchedule.DoesNotExist:
            return Response(
                {'error': '场次不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"创建订单失败: {str(e)}")
            return Response(
                {'error': '创建订单失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != 'paid':
            return Response(
                {'error': '只有已支付的订单可以取消'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['POST'])
    def change(self, request, pk=None):
        order = self.get_object()
        new_schedule_id = request.data.get('new_schedule')
        new_seats = request.data.get('new_seats', [])

        if order.status != 'paid':
            return Response(
                {'error': '只有已支付的订单可以改签'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_schedule = MovieSchedule.objects.get(id=new_schedule_id)
            # 检查新座位是否可用
            existing_orders = Order.objects.filter(
                schedule=new_schedule,
                status__in=['pending', 'paid']
            )
            occupied_seats = []
            for existing_order in existing_orders:
                occupied_seats.extend(existing_order.seats)

            for seat in new_seats:
                if seat in occupied_seats:
                    return Response(
                        {'error': f'座位 {seat} 已被占用'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 更新订单
            order.schedule = new_schedule
            order.seats = new_seats
            order.total_price = new_schedule.price * len(new_seats)
            order.status = 'changed'
            order.save()

            return Response(OrderSerializer(order).data)

        except MovieSchedule.DoesNotExist:
            return Response(
                {'error': '场次不存在'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggle_review_like(request, review_id):
    """切换评论点赞状态"""
    review = get_object_or_404(Review, id=review_id)

    try:
        like = ReviewLike.objects.get(user=request.user, review=review)
        like.delete()
        return Response({'status': 'unliked', 'is_liked': False})
    except ReviewLike.DoesNotExist:
        ReviewLike.objects.create(user=request.user, review=review)
        return Response({'status': 'liked', 'is_liked': True})


def thirdparty_proxy(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponseBadRequest('Missing url')
    try:
        resp = requests.get(url, timeout=10)
        return JsonResponse(resp.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
