from rest_framework import permissions, serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import Post, PostImage, Reply, ReplyImage, CustomUser, Notification, PointLog
from rest_framework.authtoken.models import Token


# ==============
# 权限类
# ==============

class IsSuperAdmin(permissions.BasePermission):
    """仅超级管理员可访问"""

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsContentAdmin(permissions.BasePermission):
    """内容管理员权限"""

    def has_permission(self, request, view):
        return request.user and request.user.has_perm('movies.manage_content')


class IsAdmin(permissions.BasePermission):
    """管理员权限"""

    def has_permission(self, request, view):
        return request.user and getattr(request.user, 'is_admin', False)


class IsPostAuthorOrReadOnly(permissions.BasePermission):
    """文章作者可编辑，其他用户只读"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可编辑，其他用户只读"""

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS or
                (request.user.is_authenticated and getattr(request.user, 'is_admin', False))
        )


# ==============
# 序列化器
# ==============
class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']  # 按需返回字段


class HotPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.IntegerField(source='total_likes', default=0)
    reply_count = serializers.IntegerField(source='total_replies', default=0)
    view_count = serializers.IntegerField(default=0)
    hot_score = serializers.FloatField(source='calculated_score', default=0.0)
    theme = serializers.CharField(default='other')
    is_pinned = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'username', 'created_at',
            'like_count', 'reply_count', 'view_count', 'hot_score',
            'theme', 'is_pinned'
        ]

    def to_representation(self, instance):
        try:
            data = super().to_representation(instance)

            # 确保数值字段不为空
            data['like_count'] = int(getattr(instance, 'total_likes', 0) or 0)
            data['reply_count'] = int(getattr(instance, 'total_replies', 0) or 0)
            data['view_count'] = int(getattr(instance, 'view_count', 0) or 0)
            data['hot_score'] = float(getattr(instance, 'calculated_score', 0) or 0)

            return data
        except Exception as e:
            # 返回基本数据
            return {
                'id': instance.id,
                'title': instance.title,
                'username': instance.user.username,
                'created_at': instance.created_at,
                'like_count': 0,
                'reply_count': 0,
                'view_count': 0,
                'hot_score': 0.0,
                'theme': instance.theme,
                'is_pinned': instance.is_pinned
            }


class PointLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PointLog
        fields = ['id', 'username', 'amount', 'reason', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    reply_content = serializers.CharField(source='reply.content', read_only=True)
    reply_post_id = serializers.IntegerField(source='reply.post.id', read_only=True)  # 新增字段，直接获取帖子ID
    type = serializers.CharField(source='get_type_display', read_only=True)  # 新增通知类型（可选，方便前端逻辑）
    post_pk = serializers.IntegerField(source='post.pk', read_only=True)
    reply_post_pk = serializers.IntegerField(source='reply.post.pk', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'content', 'post', 'post_title', 'reply', 'reply_content', 'reply_post_id', 'type',  # 包含新增字段
            'is_read', 'created_at', 'post_pk', 'reply_post_pk'
        ]


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'image', 'uploaded_at')


class ReplyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyImage
        fields = ('id', 'image', 'uploaded_at')


class ReplySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    content = serializers.CharField(required=False)  # 允许内容为空（配合图片）
    images = ReplyImageSerializer(many=True, read_only=True)  # 序列化图片
    children = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(source='parent.id', allow_null=True, read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'username', 'content', 'post', 'created_at', 'children', 'images', 'parent_id']
        read_only_fields = ['username', 'post', 'created_at', 'children', 'images', 'parent_id']

    def get_children(self, obj):
        return ReplySerializer(obj.children.all(), many=True, context=self.context).data


class PostSerializer(serializers.ModelSerializer):
    # 基础信息
    images = PostImageSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status = serializers.CharField(read_only=True)

    # 新增置顶字段
    is_pinned = serializers.BooleanField(read_only=True)  # 普通用户只读

    # 统计信息
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    favorite_count = serializers.IntegerField(source='favorites.count', read_only=True)
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)

    # 用户交互状态
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(read_only=True)

    # 关联对象
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'images', 'status', 'theme', 'is_pinned',  # 包含 is_pinned 和 theme
            'username', 'created_at', 'replies', 'reply_count',
            'like_count', 'favorite_count', 'is_liked', 'is_favorited',
        ]
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': True},
            'images': {'required': False},
        }

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False


class PostAdminSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username', read_only=True)  # 作者用户名
    is_pinned = serializers.BooleanField(required=False)  # 管理员可编辑

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'author', 'content', 'status', 'theme', 'is_pinned',  # 支持主题和置顶修改
            'created_at', 'rejection_reason'
        ]
        read_only_fields = ['id', 'author', 'created_at']

    def update(self, instance, validated_data):
        # 允许管理员修改主题和置顶状态
        if 'theme' in validated_data:
            instance.theme = validated_data['theme']
        if 'is_pinned' in validated_data:
            instance.is_pinned = validated_data['is_pinned']
        if 'status' in validated_data:
            instance.status = validated_data['status']
        if 'rejection_reason' in validated_data:
            instance.rejection_reason = validated_data['rejection_reason']
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=20
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'birthday', 'age', 'phone', 'bio')
        extra_kwargs = {
            'birthday': {'required': True},
            'age': {'required': True},
            'phone': {'required': True},
            'bio': {'required': False}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            request = self.context.get('request')
            user = authenticate(request=request, email=email, password=password)
            if not user:
                raise serializers.ValidationError('无法使用提供的凭证登录', code='authorization')
        else:
            raise serializers.ValidationError('必须包含"email"和"password"', code='authorization')

        attrs['user'] = user
        return attrs


class UserBriefSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar']

    def get_avatar(self, obj):
        if not obj.avatar:
            return '/static/default_avatar.png'
        request = self.context.get('request')
        return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url


class UserDetailSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    is_admin = serializers.BooleanField(source='is_staff')
    admin_role = serializers.CharField()
    is_superuser = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'phone', 'bio', 'is_admin', 'admin_role', 'is_superuser', 'date_joined']

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url


class UserSettingsSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        min_length=8,
        max_length=20,
        required=False
    )
    email = serializers.EmailField(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'old_password', 'new_password', 'avatar', 'phone', 'bio', 'is_admin']
        extra_kwargs = {
            'avatar': {'required': False},
            'phone': {'required': False},
            'bio': {'required': False}
        }

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def update(self, instance, validated_data):
        if 'new_password' in validated_data:
            instance.set_password(validated_data['new_password'])
        if 'email' in validated_data:
            instance.email = self.validate_email(validated_data['email'])
        instance.phone = validated_data.get('phone', instance.phone)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance

    def validate_email(self, value):
        if CustomUser.objects.exclude(id=self.instance.id).filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value


class AdminUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'is_active',
            'is_staff', 'is_superuser', 'admin_role', 'date_joined', 'last_login', 'avatar'
        ]
        read_only_fields = ['date_joined', 'last_login']

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url