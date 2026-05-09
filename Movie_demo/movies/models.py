# movies/models.py
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import JSONField

from Movie_demo import settings
from users.models import CustomUser

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True)
    runtime = models.PositiveIntegerField(null=True)
    budget = models.BigIntegerField(null=True)
    revenue = models.BigIntegerField(null=True)
    genres = JSONField(default=list)
    production_countries = JSONField(default=list)
    spoken_languages = JSONField(default=list)
    vote_average = models.FloatField(null=True)
    vote_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['release_date']),
        ]

    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='reviews')
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='reviews')
    content = models.TextField()
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # 添加这个字段，表示评论是否已审核

    class Meta:
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='unique_user_movie_review'
            )
        ]

class ReviewLike(models.Model):
    """评论点赞模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review_likes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')
        indexes = [
            models.Index(fields=['user', 'review']),
            models.Index(fields=['created_at']),
        ]

class UserFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_favorites'  # 添加这行
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='movie_favorites'  # 添加这行
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

class Cinema(models.Model):
    name = models.CharField(max_length=255, default='未知影院')
    address = models.TextField(default='地址待更新')
    city = models.CharField(max_length=100, default='未知城市')
    phone = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return self.name

class MovieSchedule(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='schedules')
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='schedules')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available_seats = models.PositiveIntegerField(default=100)
    total_seats = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['movie', 'cinema']),
            models.Index(fields=['start_time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'cinema', 'start_time'],
                name='unique_movie_cinema_schedule'
            )
        ]

    def __str__(self):
        return f"{self.movie.title} - {self.cinema.name} - {self.start_time}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    schedule = models.ForeignKey(MovieSchedule, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    seats = JSONField(default=list)  # 存储座位信息
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"订单 {self.order_number} - {self.user.username}"