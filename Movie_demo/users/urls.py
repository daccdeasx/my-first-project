from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    # 认证与用户
    RegisterViewSet, CustomAuthToken, UserProfileView, UserSettingsView,
    UserLoginView, UserRegistrationView, UserPointLogView,

    # 用户内容
    UserReviewsViewSet, UserCollectionView,

    # 论坛核心功能
    PostListCreateView, PostDetailView, ReplyCreateView,
    PostLikeView, PostFavoriteView, HotPostListView,

    # 管理员功能
    admin_user_list, toggle_user_status, admin_dashboard, delete_user,
    update_user_role,
    data_analytics, system_config, system_backup, system_logs,
    system_clear_cache, get_config_versions, get_config_by_version,
    clear_system_logs, get_system_health,

    # 审核功能
    AdminPostListView, ApprovePostView, RejectPostView, AllPostListView,

    # 通知与积分
    NotificationListView, MarkNotificationAsReadView, UserPostCollectionView, UserSearchView,
    TogglePostPinView, UserPostListView,

    # 年度报告
    get_yearly_report,
)

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'reviews', UserReviewsViewSet, basename='user-reviews')  # 用户评论视图集
router.register(r'register', RegisterViewSet, basename='register')  # 用户注册（仅 POST）

urlpatterns = [
                  # =====================
                  # 基础认证路由
                  # =====================
                  path('login/', CustomAuthToken.as_view(), name='login'),  # 登录获取 Token
                  path('register/', UserRegistrationView.as_view(), name='user-register'),  # 公开注册接口
                  path('profile/', UserProfileView.as_view(), name='user-profile'),  # 用户资料
                  path('settings/', UserSettingsView.as_view(), name='user-settings'),  # 用户设置
                  path('point-log/', UserPointLogView.as_view(), name='user-point-log'),  # 用户积分日志

                  # =====================
                  # 论坛核心路由
                  # =====================
                  # 帖子列表与创建
                  path('posts/', PostListCreateView.as_view(), name='post-list-create'),
                  # 帖子详情（含点赞/收藏/浏览量）
                  path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
                  # 点赞接口
                  path('posts/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
                  # 收藏接口
                  path('posts/<int:post_id>/favorite/', PostFavoriteView.as_view(), name='post-favorite'),
                  # 热门帖子列表
                  path('posts/hot/', HotPostListView.as_view(), name='hot-post-list'),
                  # 用户搜索
                  path('search/', UserSearchView.as_view(), name='user-search'),

                  # =====================
                  # 回复路由
                  # =====================
                  path('posts/<int:post_id>/replies/', ReplyCreateView.as_view(), name='reply-create'),

                  # =====================
                  # 用户个人内容路由
                  # =====================
                  path('', include(router.urls)),  # 包含视图集生成的路由
                  path('collection/', UserCollectionView.as_view(), name='user-collection'),  # 用户收藏列表
                  path('notifications/', NotificationListView.as_view(), name='notification-list'),  # 通知列表
                  path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(),
                       name='mark-notification-read'),  # 标记通知已读
                  path('post-collections/', UserPostCollectionView.as_view(), name='user-post-collections'),  # 帖子收藏
                  path('posts/', UserPostListView.as_view(), name='user-post-list'),
                  path('posts/<int:pk>/', PostDetailView.as_view(), name='user-post-detail'),

                  # =====================
                  # 管理员路由（需权限控制）
                  # =====================
                  path('admin/users/', admin_user_list, name='admin-user-list'),  # 用户管理列表
                  path('admin/users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle-user-status'),
                  # 切换用户状态
                  path('admin/users/<int:user_id>/role/', update_user_role, name='update-user-role'),
                  path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),  # 仪表盘数据
                  path('admin/users/delete/<int:user_id>/', delete_user, name='delete-user'),  # 删除用户
                  path('admin/analytics/', data_analytics, name='admin-data-analytics'),  # 数据分析
                  path('admin/system/config/', system_config, name='system-config'),  # 系统配置
                  path('admin/system/backup/', system_backup, name='system-backup'),  # 系统备份
                  path('admin/system/logs/', system_logs, name='system-logs'),  # 系统日志
                  path('admin/system/cache/clear/', system_clear_cache, name='system-cache-clear'),  # 清除缓存
                  path('admin/config-versions/', get_config_versions, name='get-config-versions'),  # 配置版本列表
                  path('admin/config-versions/<str:version_file>/', get_config_by_version,name='get-config-by-version'),  # 查看配置版本
                  path('admin/posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

                  # =====================
                  # 审核路由（管理员专用）
                  # =====================
                  path('admin/posts/pending/', AdminPostListView.as_view(), name='admin-post-pending-list'),  # 待审核帖子
                  path('admin/posts/<int:pk>/approve/', ApprovePostView.as_view(), name='approve-post'),  # 审核通过
                  path('admin/posts/<int:pk>/reject/', RejectPostView.as_view(), name='reject-post'),  # 审核拒绝
                  path('admin/posts/all/', AllPostListView.as_view(), name='admin-post-all-list'),  # 所有状态帖子列表
                  path('admin/posts/<int:pk>/pin/', TogglePostPinView.as_view(), name='toggle-post-pin'),  # 置顶帖子

                  # =====================
                  # 系统监控路由
                  # =====================
                  path('admin/system/health/', get_system_health, name='system-health'),  # 系统健康状态

                  # =====================
                  # 静态资源路由（开发环境）
                  # =====================
                  path('user-post-collection/', UserPostCollectionView.as_view(), name='user-post-collection'),
                  path('user-search/', UserSearchView.as_view(), name='user-search'),
                  path('user-posts/', UserPostListView.as_view(), name='user-posts'),
                  path('yearly-report/', get_yearly_report, name='yearly-report'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
