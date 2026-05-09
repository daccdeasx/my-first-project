from rest_framework import serializers
from .models import Movie, Review, Cinema, MovieSchedule, Order
from django.contrib.auth import get_user_model
from django.utils import timezone

class MovieAdminSerializer(serializers.ModelSerializer):
    # 管理员专用字段（不落库，仅用于表单/审计等场景；这里选择忽略保存）
    internal_notes = serializers.CharField(write_only=True, required=False, allow_blank=True)
    revenue = serializers.IntegerField(required=False)

    class Meta:
        model = Movie
        fields = [
            'tmdb_id', 'title', 'overview', 'poster_path',
            'release_date', 'runtime', 'budget', 'revenue',
            'genres', 'production_countries', 'spoken_languages',
            'internal_notes'  # 新增管理员专用字段
        ]

    def validate_release_date(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("上映日期不能晚于当前日期")
        return value

    def create(self, validated_data):
        validated_data.pop('internal_notes', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('internal_notes', None)
        return super().update(instance, validated_data)

User = get_user_model()

class AdminReviewSerializer(serializers.ModelSerializer):
    # 自定义用户序列化，只包含必要字段
    user = serializers.SerializerMethodField()
    movie_title = serializers.CharField(source='movie.title')
    movie_poster = serializers.CharField(source='movie.poster_path')

    class Meta:
        model = Review
        fields = [
            'id', 'content', 'rating', 'created_at',
            'user', 'movie_title', 'movie_poster',
            'is_approved'
        ]
        read_only_fields = ['created_at']

    def get_user(self, obj):
        # 返回包含用户名的用户信息
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            # 可以根据需要添加更多用户字段
        }

class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = '__all__'

class MovieScheduleSerializer(serializers.ModelSerializer):
    cinema_name = serializers.CharField(source='cinema.name', read_only=True)
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    
    class Meta:
        model = MovieSchedule
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    cinema_name = serializers.SerializerMethodField()
    movie_title = serializers.SerializerMethodField()
    schedule_time = serializers.SerializerMethodField()
    movie_poster = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('order_number', 'user', 'total_price')
    
    def get_cinema_name(self, obj):
        # 优先从关联的schedule获取
        if obj.schedule and obj.schedule.cinema:
            return obj.schedule.cinema.name
        
        # 从订单的seats字段中获取影院信息（如果存储了的话）
        if hasattr(obj, 'seats') and isinstance(obj.seats, dict) and 'cinema_name' in obj.seats:
            return obj.seats['cinema_name']
        
        return '演示影院'
    
    def get_movie_title(self, obj):
        # 优先从关联的schedule获取
        if obj.schedule and obj.schedule.movie:
            return obj.schedule.movie.title
        
        # 从订单的seats字段中获取电影信息（如果存储了的话）
        if hasattr(obj, 'seats') and isinstance(obj.seats, dict) and 'movie_title' in obj.seats:
            return obj.seats['movie_title']
        
        return '演示电影'
    
    def get_schedule_time(self, obj):
        if obj.schedule:
            return obj.schedule.start_time
        
        # 从订单的seats字段中获取时间信息（如果存储了的话）
        if hasattr(obj, 'seats') and isinstance(obj.seats, dict) and 'show_time' in obj.seats:
            return obj.seats['show_time']
        
        return obj.created_at
    
    def get_movie_poster(self, obj):
        # 优先从关联的schedule获取
        if obj.schedule and obj.schedule.movie and hasattr(obj.schedule.movie, 'poster_path'):
            return obj.schedule.movie.poster_path
        
        # 从订单的seats字段中获取海报信息（如果存储了的话）
        if hasattr(obj, 'seats') and isinstance(obj.seats, dict) and 'movie_poster' in obj.seats:
            return obj.seats['movie_poster']
        
        return None