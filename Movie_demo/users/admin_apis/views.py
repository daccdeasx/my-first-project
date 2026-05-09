from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import CustomUser
from movies.models import Movie, Review
from users.serializers import AdminUserSerializer
from datetime import  timezone
from django.db.models.functions import TruncDay
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from movies.models import Movie, Review

class AdminUserList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    # 基础统计数据
    total_users = CustomUser.objects.count()
    total_movies = Movie.objects.count()
    today_reviews = Review.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    # 用户增长数据（最近30天，格式：{date: "MM-DD", value: number}）
    user_growth = CustomUser.objects.annotate(
        date=TruncDay('date_joined')  # 按天分组
    ).values('date').annotate(
        value=Count('id')  # 字段名改为前端需要的`value`
    ).order_by('date')[:30]  # 取最近30天

    # 处理日期格式为 MM-DD（如 "09-01"）
    user_growth_formatted = [
        {
            'date': entry['date'].strftime('%m-%d'),  # 格式化为月-日
            'value': entry['value']
        }
        for entry in user_growth
    ]

    # 电影类型分布（格式：{name: "类型名", value: number}）
    genre_distribution = Movie.objects.values('genres').annotate(
        value=Count('id')  # 字段名改为前端需要的`value`
    ).order_by('-value')[:10]  # 取前10大类型

    # 最近活动（格式：{timestamp: "YYYY-MM-DD HH:MM", title: "标题", content: "内容"}）
    recent_activities = []

    # 添加用户注册活动示例
    recent_activities.append({
        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M'),
        'title': '新用户注册',
        'content': f"用户 {request.user.username} 注册了账号"  # 可替换为实际用户名
    })

    # 添加新评论活动示例
    recent_reviews = Review.objects.order_by('-created_at')[:3]
    for review in recent_reviews:
        recent_activities.append({
            'timestamp': review.created_at.strftime('%Y-%m-%d %H:%M'),
            'title': f"新评论 - {review.movie.title}",
            'content': f"用户 {review.user.username} 评论了《{review.movie.title}》"
        })

    return Response({
        'total_users': total_users,
        'total_movies': total_movies,
        'today_reviews': today_reviews,
        'user_growth': user_growth_formatted,
        'genre_distribution': genre_distribution,
        'recent_activities': recent_activities
    })