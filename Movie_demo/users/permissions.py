from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """仅超级管理员可访问"""
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class HasAdminRole(permissions.BasePermission):
    """
    角色管理员权限（超级管理员自动放行）。
    使用方式：在视图上设置 `required_roles = {...}` 或在子类里覆写 `required_roles`。
    """
    required_roles = set()

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_superuser', False):
            return True
        required = getattr(view, 'required_roles', None) or self.required_roles
        if not required:
            return False
        return getattr(user, 'admin_role', 'user') in set(required)

class IsMovieAdmin(HasAdminRole):
    required_roles = {'movie_admin'}

class IsForumAdmin(HasAdminRole):
    required_roles = {'forum_admin'}

class IsOrderAdmin(HasAdminRole):
    required_roles = {'order_admin'}

class IsContentAdmin(permissions.BasePermission):
    """内容管理员权限"""
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('movies.manage_content')

class IsAdmin(permissions.BasePermission):
    """管理员权限（检查 is_admin 字段）"""
    def has_permission(self, request, view):
        return request.user and request.user.is_admin  # 直接检查模型中的 is_admin 字段

class IsPostAuthorOrReadOnly(permissions.BasePermission):
    """文章作者可编辑，其他用户只读"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可编辑，其他用户只读（检查 is_admin 字段）"""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or
            (request.user.is_authenticated and request.user.is_admin)  # 检查 is_admin
        )