# users/admin_apis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminUserList.as_view(), name='admin-user-list')
]