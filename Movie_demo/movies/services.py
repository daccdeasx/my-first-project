# 3. 创建电影服务模块（movies/services.py）
from sqlite3 import IntegrityError

import tmdbsimple as tmdb
from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers
from .models import Review, Movie
from users.serializers import UserBriefSerializer

class TMDBService:
    def __init__(self):
        tmdb.API_KEY = settings.TMDB_API_KEY
        self.cache = cache

    def _get_cache_key(self, method, **kwargs):
        return f'tmdb_{method}_{hash(frozenset(kwargs.items()))}'

    def _call_api(self, method, **kwargs):
        cache_key = self._get_cache_key(method, **kwargs)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # 根据方法名动态调用API
            resource, action = method.split('/')
            obj = getattr(tmdb, resource.title())()
            result = getattr(obj, action)(**kwargs)

            # 标准化响应格式
            response = {
                'results': result.get('results', []),
                'page': result.get('page', 1),
                'total_pages': result.get('total_pages', 1)
            }

            self.cache.set(cache_key, response, settings.CACHE_TTL)
            return response
        except Exception as e:
            return {'error': str(e)}


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['tmdb_id', 'title', 'poster_path']  # 确保包含poster_path


class ReviewSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_featured = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'content', 'rating', 'created_at', 'user', 'movie', 'like_count', 'is_featured', 'is_liked']
        extra_kwargs = {
            'rating': {
                'min_value': 1,
                'max_value': 10
            }
        }

    def get_like_count(self, obj):
        return obj.like_count if hasattr(obj, 'like_count') else obj.review_likes.count()

    def get_is_featured(self, obj):
        like_count = obj.like_count if hasattr(obj, 'like_count') else obj.review_likes.count()
        return like_count >= 5

    def get_is_liked(self, obj):
        return getattr(obj, 'is_liked', False)

    def create(self, validated_data):
        movie = self.context['movie']
        user = self.context['request'].user

        try:
            return Review.objects.create(
                movie=movie,
                user=user,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError("您已经评价过该电影")
