# core/admin_router.py
from django.urls import path, include

# 关键：变量名必须为 urlpatterns
urlpatterns = [
    path('admin/users/', include('users.admin_apis.urls')),
    path('admin/movies/', include('movies.admin_apis.urls'))
]