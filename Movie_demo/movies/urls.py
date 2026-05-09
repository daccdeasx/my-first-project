from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    tmdb_proxy, movie_detail, movie_reviews, sync_movie, movie_interaction,
    RecommendationView, LLMRecommendView, UserFavoriteView, AIChatView,
    admin_movie_management, admin_movie_export,
    admin_review_management, toggle_review_status, batch_delete_reviews,
    CinemaViewSet, MovieScheduleViewSet, OrderViewSet, toggle_review_like,
    thirdparty_proxy
)

router = DefaultRouter()
router.register(r'cinemas', CinemaViewSet)
router.register(r'schedules', MovieScheduleViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    # TMDB代理接口
    path('movies/tmdb/', tmdb_proxy, name='tmdb-proxy'),
    path('movies/<int:movie_id>/', movie_detail, name='movie-detail'),
    path('movies/<int:movie_id>/reviews/', movie_reviews, name='movie-reviews'),
    path('movies/<int:movie_id>/reviews/<int:review_id>/', movie_reviews, name='movie-review-detail'),
    path('movies/reviews/<int:review_id>/like/', toggle_review_like, name='review-like'),

    # 新增同步接口
    path('sync/', sync_movie, name='sync-movie'),
    path('movies/<int:movie_id>/interaction/', movie_interaction),

    # 推荐和AI接口
    path('recommend/', RecommendationView.as_view(), name='movie-recommend'),
    path('llm/recommend/', LLMRecommendView.as_view(), name='llm-recommend'),
    path('llm/chat/', AIChatView.as_view(), name='ai-chat'),

    # 用户收藏接口
    path('movies/<int:tmdb_id>/favorite/', UserFavoriteView.as_view(), name='user-favorite'),

    # 管理员电影管理接口
    path('admin/movies/', admin_movie_management, name='admin-movie-list', kwargs={'tmdb_id': None}),
    path('admin/movies/<int:tmdb_id>/', admin_movie_management, name='admin-movie-detail'),
    path('admin/movies/export/', admin_movie_export, name='admin-movie-export'),

    # 管理员评论管理接口
    path('admin/reviews/', admin_review_management),
    path('admin/reviews/<int:review_id>/', admin_review_management),
    path('admin/reviews/<int:review_id>/toggle-status/', toggle_review_status),
    path('admin/reviews/batch/', batch_delete_reviews),

    path('thirdparty-proxy/', thirdparty_proxy, name='thirdparty_proxy'),
]