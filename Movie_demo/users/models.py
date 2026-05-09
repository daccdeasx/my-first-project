from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from django.utils.html import strip_tags
import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class CustomUser(AbstractUser):
    """自定义用户模型，扩展自AbstractUser"""
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=False,
        help_text='可选字段，系统会自动生成唯一用户名',
    )
    birthday = models.DateField(verbose_name='生日', null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name='年龄', null=True, blank=True, editable=False)
    phone = models.CharField(max_length=20, verbose_name='手机号', blank=True)
    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        verbose_name='头像'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    is_admin = models.BooleanField(default=False, verbose_name='管理员')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='最后登录IP')
    login_count = models.PositiveIntegerField(default=0, verbose_name='登录次数')
    points = models.PositiveIntegerField(default=0, verbose_name='积分')

    ADMIN_ROLE_CHOICES = [
        ('user', '普通用户'),
        ('movie_admin', '电影管理员'),
        ('forum_admin', '论坛管理员'),
        ('order_admin', '订单管理员'),
    ]
    admin_role = models.CharField(
        max_length=20,
        choices=ADMIN_ROLE_CHOICES,
        default='user',
        verbose_name='管理员角色'
    )

    # 设置邮箱为认证字段
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        permissions = [
            ("manage_user", "Can manage users"),
            ("manage_content", "Can manage content"),
            ("view_analytics", "Can view analytics"),
        ]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.email or self.username or f"用户#{self.id}"

    def clean(self):
        # 验证手机号格式
        if self.phone and not self.phone.isdigit():
            raise ValidationError({'phone': '手机号只能包含数字'})

    def save(self, *args, **kwargs):
        # 自动计算年龄
        if self.birthday:
            today = timezone.now().date()
            self.age = today.year - self.birthday.year - (
                    (today.month, today.day) < (self.birthday.month, self.birthday.day))

        # 自动生成唯一用户名
        if not self.username:
            self.username = self.generate_unique_username()

        super().save(*args, **kwargs)

    def generate_unique_username(self):
        """生成基于UUID的唯一用户名"""
        return f"user_{uuid.uuid4().hex[:8]}"

    def add_points(self, amount, reason):
        """添加积分并记录日志"""
        self.points += amount
        self.save()
        PointLog.objects.create(user=self, amount=amount, reason=reason)


class PointLog(models.Model):
    """积分变动日志"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='point_logs')
    amount = models.IntegerField(verbose_name='变动积分')
    reason = models.CharField(max_length=200, verbose_name='原因')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Post(models.Model):
    """论坛帖子模型"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已发布'),
        ('rejected', '已拒绝'),
    ]

    THEME_CHOICES = [
        ('tech', '技术'),
        ('life', '生活'),
        ('entertainment', '娱乐'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='reviewed_posts')
    rejection_reason = models.TextField(blank=True, verbose_name='拒绝原因')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    reply_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    favorite_count = models.PositiveIntegerField(default=0, verbose_name='收藏数')

    # 新增置顶字段
    is_pinned = models.BooleanField(default=False, verbose_name='是否置顶')

    class Meta:
        ordering = ['-is_pinned', '-created_at']  # 置顶帖子优先显示
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'is_pinned']),
            models.Index(fields=['theme']),
        ]

    @property
    def hot_score(self):
        """计算帖子热度（包含置顶权重）"""
        return self.like_count * 2 + self.reply_count + self.view_count * 0.5 + (self.is_pinned * 100)  # 置顶加100分


class PostImage(models.Model):
    """帖子图片模型"""
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='forum/post_images/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']


class Reply(models.Model):
    """帖子回复模型"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(max_length=500, blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父回复'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['parent']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.handle_mentions()
        # 回复成功后增加用户积分
        self.user.add_points(5, '发表评论')

    def handle_mentions(self):
        """处理@提及功能"""
        mentions = re.findall(r'@(\w+)', self.content)
        for username in mentions:
            try:
                mentioned_user = CustomUser.objects.get(username=username)
                Notification.objects.create(
                    user=mentioned_user,
                    content=f'你被提及在回复中：{strip_tags(self.content)[:50]}...',
                    reply=self,
                    post=self.post
                )
            except CustomUser.DoesNotExist:
                pass


class ReplyImage(models.Model):
    """回复图片模型"""
    reply = models.ForeignKey(Reply, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='forum/reply_images/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    """通知模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    content = models.TextField(verbose_name='通知内容')
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联帖子')
    reply = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='关联回复')
    is_read = models.BooleanField(default=False, verbose_name='已读状态')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PostLike(models.Model):
    """帖子点赞模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class PostFavorite(models.Model):
    """帖子收藏模型"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


@receiver(post_save, sender=Notification)
def send_notification_signal(sender, instance, created, **kwargs):
    """发送实时通知信号"""
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.user.id}',
            {
                'type': 'send_notification',
                'content': {
                    'id': instance.id,
                    'content': instance.content,
                    'is_read': instance.is_read,
                    'created_at': instance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f'/forum/post/{instance.reply.post.id}#reply-{instance.reply.id}' if instance.reply else f'/forum/post/{instance.post.id}',
                }
            }
        )


@receiver(post_save, sender=Post)
def award_points_for_post(sender, instance, created, **kwargs):
    """发布帖子奖励积分"""
    if created:
        instance.user.add_points(10, '发布帖子')